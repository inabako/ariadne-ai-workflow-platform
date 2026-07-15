from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.rag.cleanup_guard import assert_safe_clean_output_target  # noqa: E402


DEFAULT_POLICY_PATH = Path("runtime/rag/policies/knowledge-ingestion-policy.json")
DECISIONS = {"ACCEPT", "REWRITE", "HUMAN_CHECK", "REJECT"}
MARKDOWN_DECORATION_RE = re.compile(r"^[\s#*\-`|:]+$")
HEADING_ONLY_RE = re.compile(r"^\s*#{1,6}\s+.+?\s*$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate RAG chunk candidates before indexing and embedding.")
    parser.add_argument("--chunks-dir", default="rag/chunks")
    parser.add_argument("--output-dir", default="rag/optimized-chunks")
    parser.add_argument("--evidence-dir", default="db/rag/evidence/ingestion")
    parser.add_argument("--policy", default=str(DEFAULT_POLICY_PATH))
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--clean-output", action="store_true")
    return parser


def resolve_repo_path(repo_root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalized_text(value: str) -> str:
    lines = [line.strip() for line in value.replace("\r\n", "\n").replace("\r", "\n").splitlines()]
    return "\n".join(line for line in lines if line)


def content_hash(value: str) -> str:
    return sha256_text(normalized_text(value))


def load_policy(repo_root: Path, policy_path: str | Path) -> dict[str, Any]:
    path = resolve_repo_path(repo_root, policy_path)
    if not path.exists() and Path(policy_path).as_posix() == DEFAULT_POLICY_PATH.as_posix():
        path = Path(__file__).resolve().parent / "policies" / "knowledge-ingestion-policy.json"
    policy = read_json(path, default=None)
    if not isinstance(policy, dict):
        raise ValueError(f"Invalid RAG ingestion policy: {path}")
    weights = policy.get("weights", {})
    if not isinstance(weights, dict):
        raise ValueError("RAG ingestion policy weights must be an object.")
    weight_total = sum(float(value) for value in weights.values())
    if weight_total <= 0:
        raise ValueError("RAG ingestion policy weights total must be positive.")
    return policy


def discover_chunks(chunks_dir: Path) -> list[Path]:
    if not chunks_dir.exists():
        raise FileNotFoundError(f"RAG chunks directory not found: {chunks_dir}")
    return sorted(path for path in chunks_dir.rglob("*.json") if path.is_file())


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def line_repetition_ratio(text: str) -> float:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return 0.0
    counts = Counter(lines)
    repeated = sum(count - 1 for count in counts.values() if count > 1)
    return repeated / len(lines)


def pattern_hits(patterns: Sequence[str], text: str) -> list[str]:
    hits: list[str] = []
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            hits.append(pattern)
    return hits


def term_hits(terms: Sequence[str], text: str) -> list[str]:
    lowered = text.lower()
    return [term for term in terms if term.lower() in lowered or term in text]


def metadata_value(chunk: dict[str, Any], key: str) -> Any:
    metadata = chunk.get("metadata", {})
    if isinstance(metadata, dict) and key in metadata:
        return metadata.get(key)
    return chunk.get(key)


def is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(is_present(item) for item in value)
    return True


def score_semantic_completeness(text: str) -> float:
    clean = normalized_text(text)
    if not clean:
        return 0.0
    if HEADING_ONLY_RE.match(clean):
        return 0.25
    if len(clean) < 40:
        return 0.45
    sentence_markers = sum(clean.count(marker) for marker in ["。", ".", "です", "ます", ":", "："])
    return clamp(0.62 + min(0.28, len(clean) / 1200) + min(0.10, sentence_markers * 0.02))


def score_retrieval_usefulness(chunk: dict[str, Any], text: str) -> float:
    heading_path = chunk.get("heading_path", [])
    tags = metadata_value(chunk, "tags") or []
    unique_terms = len(set(re.findall(r"[A-Za-z0-9_.:-]+|[\u3040-\u30ff\u3400-\u9fff]+", text)))
    if not text.strip():
        return 0.0
    if MARKDOWN_DECORATION_RE.match(text.strip()):
        return 0.1
    return clamp(0.35 + min(0.30, unique_terms / 80) + (0.15 if heading_path else 0.0) + (0.15 if tags else 0.0))


def score_source_reliability(chunk: dict[str, Any]) -> float:
    status = str(metadata_value(chunk, "status") or "").lower()
    trust_level = str(metadata_value(chunk, "trust_level") or "").lower()
    sources = metadata_value(chunk, "sources")
    commit = str(metadata_value(chunk, "commit") or "")
    score = 0.50
    if trust_level in {"high", "official", "verified"}:
        score += 0.30
    elif trust_level in {"medium", "internal"}:
        score += 0.15
    elif trust_level in {"low", "unknown"}:
        score -= 0.15
    if status in {"approved", "merged", "reviewed", "published"}:
        score += 0.20
    elif status in {"draft", "proposed"}:
        score += 0.15
    if is_present(sources):
        score += 0.10
    if commit and commit != "unknown":
        score += 0.10
    return clamp(score)


def score_metadata_completeness(chunk: dict[str, Any], hash_value: str) -> float:
    required = {
        "chunk_id": chunk.get("chunk_id"),
        "document_id": chunk.get("document_id"),
        "source_path": chunk.get("source_path"),
        "chunk_index": chunk.get("chunk_index"),
        "content_hash": hash_value,
        "document_type": metadata_value(chunk, "document_type"),
        "title": metadata_value(chunk, "title"),
    }
    return sum(1 for value in required.values() if is_present(value)) / len(required)


def score_context_independence(text: str, ambiguous_terms: Sequence[str]) -> float:
    hits = term_hits(ambiguous_terms, text)
    if not hits:
        return 1.0
    return clamp(1.0 - min(0.75, len(hits) * 0.18))


def score_traceability(chunk: dict[str, Any]) -> float:
    fields = [
        chunk.get("source_path"),
        chunk.get("normalized_path"),
        chunk.get("document_id"),
        metadata_value(chunk, "source"),
        metadata_value(chunk, "title"),
        metadata_value(chunk, "status"),
        metadata_value(chunk, "commit"),
        metadata_value(chunk, "repository"),
        metadata_value(chunk, "branch"),
        metadata_value(chunk, "sources"),
    ]
    present = sum(1 for value in fields if is_present(value) and value != "unknown")
    return clamp(present / 6)


def noise_penalty(text: str, noise_patterns: Sequence[str]) -> float:
    clean = normalized_text(text)
    if not clean:
        return 1.0
    penalty = 0.0
    penalty += min(0.35, len(pattern_hits(noise_patterns, clean)) * 0.12)
    penalty += min(0.35, line_repetition_ratio(clean) * 0.8)
    if MARKDOWN_DECORATION_RE.match(clean):
        penalty += 0.45
    return clamp(penalty)


def duplication_penalty(hash_value: str, seen_hashes: set[str]) -> float:
    return 1.0 if hash_value in seen_hashes else 0.0


def ambiguity_penalty(text: str, ambiguous_terms: Sequence[str]) -> float:
    hits = term_hits(ambiguous_terms, text)
    return clamp(min(0.8, len(hits) * 0.18))


def oversize_penalty(text: str) -> float:
    length = len(text)
    if length <= 2400:
        return 0.0
    return clamp((length - 2400) / 2400)


def fragmentation_penalty(text: str) -> float:
    clean = normalized_text(text)
    if not clean:
        return 1.0
    if HEADING_ONLY_RE.match(clean):
        return 0.9
    if clean.startswith("```") and clean.endswith("```"):
        return 0.65
    if len(clean) < 25:
        return 0.75
    if clean.endswith(("、", ",", ":", "：", "and", "or")):
        return 0.45
    return 0.0


def conflict_penalty(text: str) -> float:
    conflict_terms = ["矛盾", "conflict", "deprecated", "廃止", "旧版", "新版", "不一致", "互換性"]
    return clamp(min(0.8, len(term_hits(conflict_terms, text)) * 0.20))


def detect_human_check_reasons(chunk: dict[str, Any], text: str, policy: dict[str, Any], conflict: float) -> list[str]:
    reasons: list[str] = []
    for topic in policy.get("human_check_topics", []):
        if str(topic).lower() in text.lower() or str(topic) in text:
            reasons.append(f"high-risk-topic:{topic}")
    if conflict > 0:
        reasons.append("conflict-candidate")
    if not is_present(chunk.get("source_path")):
        reasons.append("missing-source-traceability")
    return sorted(set(reasons))


def detect_reject_reasons(text: str, policy: dict[str, Any], duplicate: float, fragment: float) -> list[str]:
    reasons: list[str] = []
    if not normalized_text(text):
        reasons.append("empty-content")
    for pattern in pattern_hits(policy.get("reject_patterns", []), text):
        reasons.append(f"reject-pattern:{pattern}")
    if duplicate >= 1.0:
        reasons.append("duplicate-content-hash")
    if fragment >= 1.0:
        reasons.append("unrecoverable-fragment")
    return reasons


def compute_weighted_score(scores: dict[str, float], weights: dict[str, Any]) -> float:
    positive_score = 0.0
    positive_weight = 0.0
    penalty_score = 0.0
    for name, raw_weight in weights.items():
        weight = float(raw_weight)
        value = float(scores.get(name, 0.0))
        if name.endswith("_penalty"):
            penalty_score += weight * value
        else:
            positive_score += weight * value
            positive_weight += weight
    score = (positive_score / positive_weight if positive_weight else 0.0) - penalty_score
    return round(clamp(score), 4)


def decide(score: float, reject_reasons: list[str], human_check_reasons: list[str], policy: dict[str, Any]) -> str:
    if reject_reasons:
        return "REJECT"
    if human_check_reasons:
        return "HUMAN_CHECK"
    thresholds = policy.get("thresholds", {})
    accept_threshold = float(thresholds.get("accept", 0.80))
    rewrite_threshold = float(thresholds.get("rewrite", 0.55))
    if score >= accept_threshold:
        return "ACCEPT"
    if score >= rewrite_threshold:
        return "REWRITE"
    return "REJECT"


def rewrite_content(text: str, policy: dict[str, Any]) -> tuple[str, list[str]]:
    changes: list[str] = []
    seen_lines: set[str] = set()
    rewritten_lines: list[str] = []
    noise_patterns = policy.get("noise_patterns", [])
    for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines():
        stripped = line.strip()
        if stripped and stripped in seen_lines:
            changes.append("removed-duplicate-line")
            continue
        if stripped and pattern_hits(noise_patterns, stripped):
            changes.append("removed-noise-line")
            continue
        if stripped:
            seen_lines.add(stripped)
        rewritten_lines.append(line.rstrip())
    rewritten = "\n".join(rewritten_lines).strip() + ("\n" if rewritten_lines else "")
    if rewritten != text:
        changes.append("normalized-whitespace")
    return rewritten, sorted(set(changes))


def evaluate_chunk(
    chunk: dict[str, Any],
    policy: dict[str, Any],
    seen_hashes: set[str],
    *,
    after_rewrite: bool = False,
) -> dict[str, Any]:
    text = str(chunk.get("content", ""))
    hash_value = content_hash(text)
    duplicate = duplication_penalty(hash_value, seen_hashes)
    conflict = conflict_penalty(text)
    scores = {
        "semantic_completeness": score_semantic_completeness(text),
        "retrieval_usefulness": score_retrieval_usefulness(chunk, text),
        "source_reliability": score_source_reliability(chunk),
        "metadata_completeness": score_metadata_completeness(chunk, hash_value),
        "context_independence": score_context_independence(text, policy.get("ambiguous_terms", [])),
        "traceability": score_traceability(chunk),
        "noise_penalty": noise_penalty(text, policy.get("noise_patterns", [])),
        "duplication_penalty": duplicate,
        "ambiguity_penalty": ambiguity_penalty(text, policy.get("ambiguous_terms", [])),
        "oversize_penalty": oversize_penalty(text),
        "fragmentation_penalty": fragmentation_penalty(text),
        "conflict_penalty": conflict,
    }
    score = compute_weighted_score(scores, policy.get("weights", {}))
    reject_reasons = detect_reject_reasons(text, policy, duplicate, scores["fragmentation_penalty"])
    human_check_reasons = detect_human_check_reasons(chunk, text, policy, conflict)
    decision = decide(score, reject_reasons, human_check_reasons, policy)
    if not after_rewrite and decision == "ACCEPT" and scores["noise_penalty"] >= 0.12:
        decision = "REWRITE"
    if after_rewrite and decision == "REWRITE":
        decision = "HUMAN_CHECK"
        human_check_reasons.append("rewrite-retry-limit-reached")
    return {
        "score": score,
        "scores": scores,
        "decision": decision,
        "content_hash": hash_value,
        "reject_reasons": sorted(set(reject_reasons)),
        "human_check_reasons": sorted(set(human_check_reasons)),
    }


def build_candidate_record(repo_root: Path, chunk_path: Path, chunk: dict[str, Any], hash_value: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "candidate_chunk_id": chunk.get("chunk_id", ""),
        "document_id": chunk.get("document_id", ""),
        "source_path": chunk.get("source_path", ""),
        "chunk_path": relative_to_repo(repo_root, chunk_path),
        "content_hash": hash_value,
        "metadata": chunk.get("metadata", {}),
    }


def enriched_chunk(chunk: dict[str, Any], evaluation: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(chunk.get("metadata", {})) if isinstance(chunk.get("metadata"), dict) else {}
    metadata.update(
        {
            "content_hash": evaluation["content_hash"],
            "optimization_score": evaluation["score"],
            "optimization_decision": evaluation["decision"],
        }
    )
    return {
        **chunk,
        "content_hash": evaluation["content_hash"],
        "optimization_score": evaluation["score"],
        "optimization_decision": evaluation["decision"],
        "optimization_scores": evaluation["scores"],
        "metadata": metadata,
    }


def optimize_chunk(
    repo_root: Path,
    chunk_path: Path,
    policy: dict[str, Any],
    seen_hashes: set[str],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    chunk = read_json(chunk_path)
    if not isinstance(chunk, dict):
        raise ValueError(f"Invalid RAG chunk document: {chunk_path}")

    initial = evaluate_chunk(chunk, policy, seen_hashes)
    rewritten_content = str(chunk.get("content", ""))
    rewrite_changes: list[str] = []
    final = initial
    if initial["decision"] == "REWRITE":
        rewritten_content, rewrite_changes = rewrite_content(str(chunk.get("content", "")), policy)
        rewritten_chunk = {**chunk, "content": rewritten_content}
        final = evaluate_chunk(rewritten_chunk, policy, seen_hashes, after_rewrite=True)
        chunk = rewritten_chunk

    optimized = enriched_chunk(chunk, final) if final["decision"] == "ACCEPT" else None
    evaluation = {
        "schema_version": "1.0",
        "artifact_type": "rag-ingestion-evaluation",
        "evaluated_at": utc_now_iso(),
        "candidate_chunk_id": chunk.get("chunk_id", ""),
        "document_id": chunk.get("document_id", ""),
        "source_path": chunk.get("source_path", ""),
        "chunk_path": relative_to_repo(repo_root, chunk_path),
        "decision": final["decision"],
        "score": final["score"],
        "scores": final["scores"],
        "reasons": {
            "reject": final["reject_reasons"],
            "human_check": final["human_check_reasons"],
            "rewrite": rewrite_changes,
        },
        "original_content_hash": initial["content_hash"],
        "optimized_content_hash": final["content_hash"],
        "metadata": chunk.get("metadata", {}),
    }
    if initial["decision"] == "REWRITE":
        evaluation["initial_decision"] = initial["decision"]
        evaluation["initial_score"] = initial["score"]
    return evaluation, optimized


def clean_outputs(repo_root: Path, output_dir: Path, evidence_dir: Path) -> None:
    assert_safe_clean_output_target(repo_root, output_dir)
    assert_safe_clean_output_target(repo_root, evidence_dir)
    if output_dir.exists():
        for path in output_dir.glob("*.json"):
            path.unlink()
    for name in [
        "source-manifest.json",
        "chunk-candidates.jsonl",
        "optimization-evaluations.jsonl",
        "accepted-chunks.jsonl",
        "rewritten-chunks.jsonl",
        "human-check-required.jsonl",
        "rejected-chunks.jsonl",
        "ingestion-summary.json",
    ]:
        path = evidence_dir / name
        if path.exists():
            path.unlink()


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    chunks_dir = resolve_repo_path(repo_root, args.chunks_dir).resolve()
    output_dir = resolve_repo_path(repo_root, args.output_dir).resolve()
    evidence_dir = resolve_repo_path(repo_root, args.evidence_dir).resolve()
    policy = load_policy(repo_root, args.policy)
    if args.clean_output:
        clean_outputs(repo_root, output_dir, evidence_dir)

    chunk_paths = discover_chunks(chunks_dir)
    source_manifest = {
        "schema_version": "1.0",
        "artifact_type": "rag-ingestion-source-manifest",
        "created_at": utc_now_iso(),
        "chunks_dir": relative_to_repo(repo_root, chunks_dir),
        "chunk_count": len(chunk_paths),
        "policy": relative_to_repo(repo_root, resolve_repo_path(repo_root, args.policy)),
        "sources": [relative_to_repo(repo_root, path) for path in chunk_paths],
    }

    candidates: list[dict[str, Any]] = []
    evaluations: list[dict[str, Any]] = []
    accepted_rows: list[dict[str, Any]] = []
    rewritten_rows: list[dict[str, Any]] = []
    human_rows: list[dict[str, Any]] = []
    rejected_rows: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()

    for chunk_path in chunk_paths:
        raw_chunk = read_json(chunk_path)
        if not isinstance(raw_chunk, dict):
            raise ValueError(f"Invalid RAG chunk document: {chunk_path}")
        raw_hash = content_hash(str(raw_chunk.get("content", "")))
        candidates.append(build_candidate_record(repo_root, chunk_path, raw_chunk, raw_hash))
        evaluation, optimized = optimize_chunk(repo_root, chunk_path, policy, seen_hashes)
        evaluations.append(evaluation)
        decision = evaluation["decision"]
        if decision == "ACCEPT" and optimized is not None:
            seen_hashes.add(evaluation["optimized_content_hash"])
            output_path = output_dir / f"{optimized['chunk_id']}.json"
            write_json(output_path, optimized)
            accepted_rows.append({**evaluation, "optimized_chunk_path": relative_to_repo(repo_root, output_path)})
        elif decision == "REJECT":
            rejected_rows.append(evaluation)
        elif decision == "HUMAN_CHECK":
            human_rows.append(evaluation)
        if evaluation.get("initial_decision") == "REWRITE":
            rewritten_rows.append(evaluation)

    summary = {
        "schema_version": "1.0",
        "artifact_type": "rag-ingestion-summary",
        "created_at": utc_now_iso(),
        "policy": source_manifest["policy"],
        "chunks_dir": relative_to_repo(repo_root, chunks_dir),
        "optimized_chunks_dir": relative_to_repo(repo_root, output_dir),
        "evidence_dir": relative_to_repo(repo_root, evidence_dir),
        "candidate_chunk_count": len(candidates),
        "accepted_chunk_count": len(accepted_rows),
        "rewritten_chunk_count": len(rewritten_rows),
        "human_check_required_count": len(human_rows),
        "rejected_chunk_count": len(rejected_rows),
        "average_optimization_score": round(
            sum(float(item["score"]) for item in evaluations) / len(evaluations), 4
        )
        if evaluations
        else 0.0,
        "embedding_allowed_chunk_count": len(accepted_rows),
        "human_check_required": bool(human_rows),
    }

    write_json(evidence_dir / "source-manifest.json", source_manifest)
    write_jsonl(evidence_dir / "chunk-candidates.jsonl", candidates)
    write_jsonl(evidence_dir / "optimization-evaluations.jsonl", evaluations)
    write_jsonl(evidence_dir / "accepted-chunks.jsonl", accepted_rows)
    write_jsonl(evidence_dir / "rewritten-chunks.jsonl", rewritten_rows)
    write_jsonl(evidence_dir / "human-check-required.jsonl", human_rows)
    write_jsonl(evidence_dir / "rejected-chunks.jsonl", rejected_rows)
    write_json(evidence_dir / "ingestion-summary.json", summary)

    return {
        "status": "completed",
        "chunks_dir": relative_to_repo(repo_root, chunks_dir),
        "optimized_chunks_dir": relative_to_repo(repo_root, output_dir),
        "evidence_dir": relative_to_repo(repo_root, evidence_dir),
        "ingestion_summary": relative_to_repo(repo_root, evidence_dir / "ingestion-summary.json"),
        **summary,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
