from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REQUIRED_FILES = [
    "CITATION.cff",
    "AGENTS.md",
    "LICENSE",
    "LICENSES/AGPL-3.0-or-later.txt",
    "REUSE.toml",
    "README.md",
    "CHANGELOG.md",
    "CHANGELOG.en.md",
    "SECURITY.md",
    "SECURITY.en.md",
    "CONTRIBUTING.md",
    "CONTRIBUTING.en.md",
    "NOTICE",
    "NOTICE.ja",
    "docs/release/release-policy.md",
    "docs/release/release-checklist.md",
    "docs/release/versioning-policy.md",
    "docs/citation/citation-guide.md",
    "docs/security/scancode-github-actions.md",
    "docs/legal/evidence/reuse-lint-local-rehearsal.md",
    ".github/copilot-instructions.md",
    ".github/instructions/ariadne.instructions.md",
    ".github/prompts/ariadne-workflows.prompt.md",
    ".github/workflows/reuse-lint.yml",
]

REQUIRED_ARCHITECTURE_DOCS = [
    "docs/architecture/overview.md",
    "docs/architecture/aiwfctl-architecture.md",
    "docs/architecture/runtime-architecture.md",
    "docs/architecture/workflow-dispatch.md",
    "docs/architecture/state-and-artifact-management.md",
    "docs/architecture/evidence-and-completion.md",
    "docs/architecture/human-gate.md",
    "docs/architecture/retry-and-resume.md",
]

FORBIDDEN_PATTERNS = {
    "windows-user-directory": re.compile(r"C:\\Users\\(?!User\\b)[^\\\s]+", re.IGNORECASE),
    "private-url": re.compile(r"https?://(?:localhost|127\.0\.0\.1|10\.|172\.(?:1[6-9]|2\d|3[0-1])\.|192\.168\.)", re.IGNORECASE),
    "secret-like-assignment": re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
}


@dataclass(frozen=True)
class Finding:
    id: str
    severity: str
    message: str
    path: str | None = None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def project_version(repo_root: Path) -> str | None:
    pyproject = repo_root / "runtime" / "pyproject.toml"
    if not pyproject.exists():
        return None
    data = tomllib.loads(read_text(pyproject))
    value = data.get("project", {}).get("version")
    return str(value) if value else None


def package_license(repo_root: Path) -> str | None:
    pyproject = repo_root / "runtime" / "pyproject.toml"
    if not pyproject.exists():
        return None
    data = tomllib.loads(read_text(pyproject))
    value = data.get("project", {}).get("license")
    return str(value) if value else None


def project_license(repo_root: Path) -> str:
    license_text = read_text(repo_root / "LICENSE") if (repo_root / "LICENSE").exists() else ""
    if "GNU AFFERO GENERAL PUBLIC LICENSE" in license_text:
        return "AGPL-3.0-or-later"
    return "UNKNOWN"


def parse_simple_citation(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line or line.startswith(" ") or line.startswith("-"):
            continue
        key, raw = line.split(":", 1)
        values[key.strip()] = raw.strip().strip('"')
    return values


def iter_public_text_files(repo_root: Path) -> Iterable[Path]:
    ignored_parts = {".git", ".venv", "__pycache__", ".pytest_cache", "logs"}
    allowed_suffixes = {".md", ".py", ".toml", ".json", ".yml", ".yaml", ".cff", ".txt", ""}
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_parts for part in path.parts):
            continue
        if path.suffix.lower() in allowed_suffixes:
            yield path


def validate(repo_root: Path, expected_license: str | None = None) -> tuple[list[Finding], list[Finding]]:
    errors: list[Finding] = []
    warnings: list[Finding] = []

    for rel_path in [*REQUIRED_FILES, *REQUIRED_ARCHITECTURE_DOCS]:
        if not (repo_root / rel_path).exists():
            errors.append(Finding("required-file-missing", "error", f"Required file is missing: {rel_path}", rel_path))

    citation_path = repo_root / "CITATION.cff"
    if citation_path.exists():
        citation = parse_simple_citation(read_text(citation_path))
        for key in ("cff-version", "message", "title", "type", "version", "license"):
            if not citation.get(key):
                errors.append(Finding("citation-field-missing", "error", f"CITATION.cff is missing {key}", "CITATION.cff"))
        version = project_version(repo_root)
        if version and citation.get("version") != version:
            errors.append(
                Finding(
                    "citation-version-mismatch",
                    "error",
                    f"CITATION.cff version {citation.get('version')} does not match runtime version {version}",
                    "CITATION.cff",
                )
            )
        expected = expected_license or "AGPL-3.0-or-later"
        if citation.get("license") and citation.get("license") != expected:
            errors.append(
                Finding(
                    "citation-license-mismatch",
                    "error",
                    f"CITATION.cff license {citation.get('license')} does not match expected license {expected}",
                    "CITATION.cff",
                )
            )

    detected_license = project_license(repo_root)
    expected = expected_license or "AGPL-3.0-or-later"
    if detected_license != expected:
        errors.append(
            Finding(
                "root-license-mismatch",
                "error",
                f"Detected root license {detected_license}, expected {expected}",
                "LICENSE",
            )
        )
    detected_package_license = package_license(repo_root)
    if detected_package_license != expected:
        errors.append(
            Finding(
                "package-license-mismatch",
                "error",
                f"Detected package license {detected_package_license}, expected {expected}",
                "runtime/pyproject.toml",
            )
        )

    for path in iter_public_text_files(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            errors.append(Finding("utf8-decode-failed", "error", f"File is not valid UTF-8: {rel}", rel))
            continue
        for finding_id, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(text):
                warnings.append(Finding(finding_id, "warning", f"Potential private or secret value in {rel}", rel))

    legal_check = repo_root / "docs" / "legal" / "evidence" / "release-license-check.json"
    if legal_check.exists():
        try:
            json.loads(read_text(legal_check))
        except json.JSONDecodeError as exc:
            errors.append(Finding("legal-check-invalid-json", "error", str(exc), str(legal_check.relative_to(repo_root))))

    return errors, warnings


def validation_result(repo_root: Path, expected_license: str | None = None, *, fail_on_warning: bool = False) -> dict[str, object]:
    errors, warnings = validate(repo_root, expected_license)
    return {
        "status": "pass" if not errors and not (fail_on_warning and warnings) else "fail",
        "errors": [finding.__dict__ for finding in errors],
        "warnings": [finding.__dict__ for finding in warnings],
    }


def format_validation_result(result: dict[str, object]) -> str:
    lines = [f"release validation: {result['status']}"]
    findings = [*result.get("errors", []), *result.get("warnings", [])]
    for item in findings:
        if not isinstance(item, dict):
            continue
        location = f" ({item.get('path', '')})" if item.get("path") else ""
        lines.append(f"{item.get('severity', '')}: {item.get('id', '')}: {item.get('message', '')}{location}")
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate ARIADNE release readiness.")
    parser.add_argument("--repo-root", default=".", help="Repository root to validate.")
    parser.add_argument("--expected-license", default=None, help="Expected license identifier, for example AGPL-3.0-or-later.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--fail-on-warning", action="store_true", help="Return failure when warnings are present.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        print(f"Repository root does not exist: {repo_root}", file=sys.stderr)
        return 2

    result = validation_result(repo_root, args.expected_license, fail_on_warning=args.fail_on_warning)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_validation_result(result), end="")
    if result["status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
