from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path


def detect_license(repo_root: Path) -> str:
    license_path = repo_root / "LICENSE"
    if not license_path.exists():
        return "UNKNOWN"
    text = license_path.read_text(encoding="utf-8")
    if "GNU AFFERO GENERAL PUBLIC LICENSE" in text:
        return "AGPL-3.0-or-later"
    return "UNKNOWN"


def run_git(repo_root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        return "unknown"
    return completed.stdout.strip() or "unknown"


def read_project_version(repo_root: Path) -> str:
    pyproject = repo_root / "runtime" / "pyproject.toml"
    if not pyproject.exists():
        return "unknown"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    return str(data.get("project", {}).get("version", "unknown"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def list_docs(repo_root: Path) -> list[str]:
    docs_root = repo_root / "docs"
    if not docs_root.exists():
        return []
    return sorted(path.relative_to(repo_root).as_posix() for path in docs_root.rglob("*.md"))


def build_manifest(
    repo_root: Path,
    version: str | None,
    tag: str | None,
    artifacts: list[str],
    generated_at_utc: str | None = None,
) -> dict[str, object]:
    artifact_entries: list[dict[str, object]] = []
    for artifact in sorted(artifacts):
        path = (repo_root / artifact).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Artifact does not exist: {artifact}")
        artifact_entries.append(
            {
                "path": Path(artifact).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    resolved_version = version or read_project_version(repo_root)
    generated_at = generated_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "artifact_list": artifact_entries,
        "branch": run_git(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"]),
        "commit_hash": run_git(repo_root, ["rev-parse", "HEAD"]),
        "documentation_list": list_docs(repo_root),
        "generated_at_utc": generated_at,
        "license": detect_license(repo_root),
        "os": platform.platform(),
        "project_name": "ARIADNE",
        "python_version": platform.python_version(),
        "tag": tag or f"v{resolved_version}",
        "test_result": "not-recorded",
        "version": resolved_version,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a deterministic ARIADNE release manifest.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--version", default=None, help="Release version. Defaults to runtime/pyproject.toml.")
    parser.add_argument("--tag", default=None, help="Git tag. Defaults to v<version>.")
    parser.add_argument("--artifact", action="append", default=[], help="Release artifact path. Can be repeated.")
    parser.add_argument("--output", default=None, help="Optional output JSON path.")
    parser.add_argument(
        "--generated-at-utc",
        default=None,
        help="Fixed ISO-8601 UTC timestamp for reproducible manifest generation.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    try:
        manifest = build_manifest(repo_root, args.version, args.tag, args.artifact, args.generated_at_utc)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    text = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
