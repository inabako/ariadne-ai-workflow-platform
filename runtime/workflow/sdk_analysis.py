from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import quote

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

try:  # pragma: no cover - Python 3.11+ standard path, fallback is defensive.
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

from runtime.constants.runtime_values import FILE_HASH_CHUNK_BYTES, SCHEMA_VERSION  # noqa: E402
from runtime.common import find_repo_root, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.constants.cli_defaults import SDK_ANALYSIS_MAX_BYTES_DEFAULT, SDK_ANALYSIS_MAX_FILES_DEFAULT  # noqa: E402
from runtime.constants.workflow_limits import (  # noqa: E402
    SDK_KEYWORD_PREVIEW_LIMIT,
    SDK_README_EXCERPT_MAX_CHARS,
    SDK_README_SAMPLE_MAX_BYTES,
)
from runtime.constants.schemas import SDK_ANALYSIS_CONTEXT_SCHEMA, SDK_EXTERNAL_DISCOVERY_SCHEMA  # noqa: E402
from runtime.constants.workspace import (  # noqa: E402
    context_dir_for_work_dir,
    context_file,
    manifest_path_for_work_dir,
    reports_dir_for_work_dir,
    requirements_dir_for_work_dir,
    resolve_work_dir as workspace_resolve_work_dir,
)
from runtime.rag import duckdb_store  # noqa: E402
from runtime.workflow.context_first import register_context  # noqa: E402
from runtime.workflow import work_cleanup_hint  # noqa: E402



ARTIFACT_TYPE = "sdk-analysis-context"
DISCOVERY_ARTIFACT_TYPE = "sdk-external-discovery"
KNOWLEDGE_ARTIFACT_TYPE = "sdk-analysis-knowledge"
DEFAULT_SOURCE_DIR = Path("work/requirements/sdk")
DEFAULT_CONTEXT_SCHEMA = SDK_ANALYSIS_CONTEXT_SCHEMA
DEFAULT_DISCOVERY_SCHEMA = SDK_EXTERNAL_DISCOVERY_SCHEMA
DEFAULT_KNOWLEDGE_DIR = duckdb_store.DEFAULT_SOURCE_REPO_PATH / "rag" / "jsonized"
ANALYZABLE_EXTENSIONS = {
    ".bat",
    ".cfg",
    ".cmd",
    ".conf",
    ".cs",
    ".csproj",
    ".dart",
    ".go",
    ".gradle",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".kt",
    ".lock",
    ".md",
    ".mod",
    ".php",
    ".properties",
    ".ps1",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sum",
    ".swift",
    ".toml",
    ".ts",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
IMPORTANT_FILE_NAMES = {
    "readme",
    "license",
    "licence",
    "changelog",
    "openapi",
    "swagger",
    "package",
    "pyproject",
    "requirements",
    "pom",
    "build.gradle",
    "go.mod",
    "cargo",
    "pubspec",
    "auth",
    "authentication",
    "authorization",
}
EXCLUDED_DIRS = {
    ".git",
    ".gradle",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "pods",
    "target",
    "vendor",
}
SECRET_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"api[_-]?key\s*[:=]\s*['\"][^'\"]{8,}",
        r"access[_-]?token\s*[:=]\s*['\"][^'\"]{8,}",
        r"secret[_-]?key\s*[:=]\s*['\"][^'\"]{8,}",
        r"password\s*[:=]\s*['\"][^'\"]{8,}",
        r"-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----",
    ]
]
URL_PATTERN = re.compile(r"https?://[^\s\]\)\"'<>]+")
CLOUD_SERVICE_HINTS = {
    "s3": ["s3", "object-storage", "storage"],
    "dynamodb": ["dynamodb", "state-management", "nosql"],
    "sqs": ["sqs", "queue", "messaging"],
    "sns": ["sns", "notification"],
    "lambda": ["lambda", "function"],
    "kinesis": ["kinesis", "stream"],
    "cloudwatch": ["cloudwatch", "metrics", "logs"],
    "secretsmanager": ["secretsmanager", "secret-manager"],
    "storage": ["storage", "bucket", "object-storage"],
    "pubsub": ["pubsub", "pub/sub", "messaging"],
    "bigquery": ["bigquery", "analytics"],
    "firestore": ["firestore", "document-db"],
    "spanner": ["spanner", "database"],
    "cloudtasks": ["cloudtasks", "tasks"],
    "secretmanager": ["secretmanager", "secret-manager"],
    "logging": ["logging", "logs"],
    "monitoring": ["monitoring", "metrics"],
}
CLOUD_SDK_PATTERNS = [
    {
        "provider": "aws",
        "language": "java",
        "package_manager": "maven/gradle",
        "generation": "v2",
        "pattern": re.compile(r"software\.amazon\.awssdk(?::|\.)([A-Za-z0-9_.-]+)?", re.IGNORECASE),
    },
    {
        "provider": "aws",
        "language": "java",
        "package_manager": "maven/gradle",
        "generation": "v1",
        "pattern": re.compile(r"com\.amazonaws(?::|\.)([A-Za-z0-9_.-]+)?", re.IGNORECASE),
    },
    {
        "provider": "aws",
        "language": "python",
        "package_manager": "pip/poetry/uv",
        "generation": "current",
        "pattern": re.compile(r"\b(boto3|botocore|aioboto3|aiobotocore)\b", re.IGNORECASE),
    },
    {
        "provider": "aws",
        "language": "javascript/typescript",
        "package_manager": "npm/pnpm/yarn",
        "generation": "v3",
        "pattern": re.compile(r"@aws-sdk/(client|credential|lib)-([A-Za-z0-9_-]+)", re.IGNORECASE),
    },
    {
        "provider": "aws",
        "language": "javascript/typescript",
        "package_manager": "npm/pnpm/yarn",
        "generation": "v2",
        "pattern": re.compile(r'"aws-sdk"|\'aws-sdk\'|\baws-sdk\b', re.IGNORECASE),
    },
    {
        "provider": "aws",
        "language": "go",
        "package_manager": "go-modules",
        "generation": "v2",
        "pattern": re.compile(r"github\.com/aws/aws-sdk-go-v2(?:/([A-Za-z0-9_./-]+))?", re.IGNORECASE),
    },
    {
        "provider": "aws",
        "language": "go",
        "package_manager": "go-modules",
        "generation": "v1",
        "pattern": re.compile(r"github\.com/aws/aws-sdk-go(?:/([A-Za-z0-9_./-]+))?", re.IGNORECASE),
    },
    {
        "provider": "gcp",
        "language": "java",
        "package_manager": "maven/gradle",
        "generation": "current",
        "pattern": re.compile(r"com\.google\.(cloud|api-client|auth)(?::|\.)([A-Za-z0-9_.-]+)?", re.IGNORECASE),
    },
    {
        "provider": "gcp",
        "language": "python",
        "package_manager": "pip/poetry/uv",
        "generation": "current",
        "pattern": re.compile(r"\b(google-cloud-[A-Za-z0-9_-]+|google-auth|google-api-core|grpcio)\b", re.IGNORECASE),
    },
    {
        "provider": "gcp",
        "language": "javascript/typescript",
        "package_manager": "npm/pnpm/yarn",
        "generation": "current",
        "pattern": re.compile(r"@google-cloud/([A-Za-z0-9_-]+)|\b(google-auth-library|google-gax)\b", re.IGNORECASE),
    },
    {
        "provider": "gcp",
        "language": "go",
        "package_manager": "go-modules",
        "generation": "current",
        "pattern": re.compile(r"(cloud\.google\.com/go(?:/([A-Za-z0-9_./-]+))?|google\.golang\.org/api(?:/([A-Za-z0-9_./-]+))?)", re.IGNORECASE),
    },
]
PAYMENT_SERVICE_HINTS = {
    "checkout": ["checkout", "checkout session"],
    "payment_intents": ["paymentintent", "payment_intent", "payment intents", "payment_intents"],
    "customers": ["customer", "customers"],
    "subscriptions": ["subscription", "subscriptions"],
    "invoices": ["invoice", "invoices"],
    "webhooks": ["webhook", "webhooks", "signing secret"],
    "refunds": ["refund", "refunds"],
    "connect": ["connect", "oauth"],
    "terminal": ["terminal"],
    "tax": ["tax"],
    "billing_portal": ["billing portal", "billing_portal"],
}
PAYMENT_SDK_PATTERNS = [
    {
        "vendor": "stripe",
        "language": "java",
        "package_manager": "maven/gradle",
        "generation": "current",
        "pattern": re.compile(r"\bcom\.stripe(?::|\.)(stripe-java|net|model|param)?\b", re.IGNORECASE),
    },
    {
        "vendor": "stripe",
        "language": "python",
        "package_manager": "pip/poetry/uv",
        "generation": "current",
        "pattern": re.compile(r"\bstripe\b", re.IGNORECASE),
    },
    {
        "vendor": "stripe",
        "language": "javascript/typescript",
        "package_manager": "npm/pnpm/yarn",
        "generation": "current",
        "pattern": re.compile(r"@stripe/(stripe-js|react-stripe-js)|(?<![@\w-])stripe(?![\w-])", re.IGNORECASE),
    },
    {
        "vendor": "stripe",
        "language": "go",
        "package_manager": "go-modules",
        "generation": "current",
        "pattern": re.compile(r"github\.com/stripe/stripe-go(?:/v[0-9]+)?", re.IGNORECASE),
    },
    {
        "vendor": "stripe",
        "language": "php",
        "package_manager": "composer",
        "generation": "current",
        "pattern": re.compile(r"stripe/stripe-php|\bStripe\\\\StripeClient\b", re.IGNORECASE),
    },
    {
        "vendor": "stripe",
        "language": "ruby",
        "package_manager": "bundler",
        "generation": "current",
        "pattern": re.compile(r"\bstripe-ruby\b|\bStripe::", re.IGNORECASE),
    },
    {
        "vendor": "stripe",
        "language": ".net",
        "package_manager": "nuget",
        "generation": "current",
        "pattern": re.compile(r"\bStripe\.net\b|\bStripeClient\b", re.IGNORECASE),
    },
]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def resolve_repo_path(repo_root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def resolve_work_dir(repo_root: Path, work_id: str, work_dir: str = "") -> Path:
    if not work_id:
        raise ValueError("--work-id is required when --work-dir is not specified.")
    return workspace_resolve_work_dir(repo_root, work_id, work_dir)


def default_source_dir(repo_root: Path) -> Path:
    return repo_root / DEFAULT_SOURCE_DIR


def should_exclude(path: Path) -> bool:
    return any(part.lower() in EXCLUDED_DIRS for part in path.parts)


def is_analyzable_file(path: Path) -> bool:
    if should_exclude(path):
        return False
    if path.name.lower() in IMPORTANT_FILE_NAMES:
        return True
    if path.suffix.lower() in ANALYZABLE_EXTENSIONS:
        return True
    return any(path.name.lower().startswith(name) for name in IMPORTANT_FILE_NAMES)


def collect_files(source_dir: Path, *, max_files: int = SDK_ANALYSIS_MAX_FILES_DEFAULT) -> list[Path]:
    if not source_dir.exists() or not source_dir.is_dir():
        return []
    files = [path for path in source_dir.rglob("*") if path.is_file() and is_analyzable_file(path)]
    return sorted(files, key=lambda item: item.relative_to(source_dir).as_posix().lower())[:max_files]


def read_text_sample(path: Path, *, max_bytes: int = SDK_ANALYSIS_MAX_BYTES_DEFAULT) -> str:
    data = path.read_bytes()[:max_bytes]
    return data.decode("utf-8-sig", errors="replace")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def load_toml(path: Path) -> dict[str, Any]:
    if tomllib is None:
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = value.strip()
        key = normalized.lower()
        if normalized and key not in seen:
            result.append(normalized)
            seen.add(key)
    return result


def find_readme(files: list[Path]) -> Path | None:
    for path in files:
        if path.name.lower().startswith("readme"):
            return path
    return None


def detect_package_metadata(source_dir: Path, files: list[Path]) -> dict[str, Any]:
    by_name = {path.relative_to(source_dir).as_posix().lower(): path for path in files}
    packages: list[dict[str, Any]] = []
    names: list[str] = []
    versions: list[str] = []
    license_values: list[str] = []

    package_json = by_name.get("package.json")
    if package_json:
        data = load_json(package_json)
        if data:
            names.append(str(data.get("name", "")))
            versions.append(str(data.get("version", "")))
            license_values.append(str(data.get("license", "")))
            packages.append(
                {
                    "manager": "npm",
                    "file": package_json.relative_to(source_dir).as_posix(),
                    "name": data.get("name", ""),
                    "version": data.get("version", ""),
                    "homepage": data.get("homepage", ""),
                    "repository": data.get("repository", ""),
                    "bugs": data.get("bugs", ""),
                }
            )

    pyproject = by_name.get("pyproject.toml")
    if pyproject:
        data = load_toml(pyproject)
        project = data.get("project", {}) if isinstance(data.get("project"), dict) else {}
        poetry = data.get("tool", {}).get("poetry", {}) if isinstance(data.get("tool"), dict) else {}
        names.append(str(project.get("name", "") or poetry.get("name", "")))
        versions.append(str(project.get("version", "") or poetry.get("version", "")))
        license_value = project.get("license", "")
        if isinstance(license_value, dict):
            license_value = license_value.get("text", "")
        license_values.append(str(license_value))
        packages.append(
            {
                "manager": "python",
                "file": pyproject.relative_to(source_dir).as_posix(),
                "name": project.get("name", "") or poetry.get("name", ""),
                "version": project.get("version", "") or poetry.get("version", ""),
                "homepage": (project.get("urls", {}) or {}).get("Homepage", "") if isinstance(project.get("urls", {}), dict) else "",
                "repository": (project.get("urls", {}) or {}).get("Repository", "") if isinstance(project.get("urls", {}), dict) else "",
            }
        )

    for rel_name, requirements_path in by_name.items():
        if Path(rel_name).name.startswith("requirements") and requirements_path.suffix.lower() == ".txt":
            text = read_text_sample(requirements_path)
            for raw_line in text.splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                package_name = re.split(r"[<>=!~\[]", line, maxsplit=1)[0].strip()
                version_match = re.search(r"==\s*([A-Za-z0-9_.+-]+)", line)
                if package_name:
                    names.append(package_name)
                    versions.append(version_match.group(1) if version_match else "")
                    packages.append(
                        {
                            "manager": "python",
                            "file": requirements_path.relative_to(source_dir).as_posix(),
                            "name": package_name,
                            "version": version_match.group(1) if version_match else "",
                        }
                    )

    go_mod = by_name.get("go.mod")
    if go_mod:
        text = read_text_sample(go_mod)
        match = re.search(r"^module\s+(.+)$", text, re.MULTILINE)
        names.append(match.group(1).strip() if match else "")
        packages.append({"manager": "go", "file": go_mod.relative_to(source_dir).as_posix(), "name": names[-1] if names else ""})

    cargo = by_name.get("cargo.toml")
    if cargo:
        data = load_toml(cargo)
        package = data.get("package", {}) if isinstance(data.get("package"), dict) else {}
        names.append(str(package.get("name", "")))
        versions.append(str(package.get("version", "")))
        license_values.append(str(package.get("license", "")))
        packages.append(
            {
                "manager": "cargo",
                "file": cargo.relative_to(source_dir).as_posix(),
                "name": package.get("name", ""),
                "version": package.get("version", ""),
            }
        )

    pubspec = by_name.get("pubspec.yaml")
    if pubspec:
        text = read_text_sample(pubspec)
        name_match = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
        version_match = re.search(r"^version:\s*(.+)$", text, re.MULTILINE)
        names.append(name_match.group(1).strip() if name_match else "")
        versions.append(version_match.group(1).strip() if version_match else "")
        packages.append({"manager": "dart-pub", "file": pubspec.relative_to(source_dir).as_posix(), "name": names[-1] if names else ""})

    return {
        "names": unique(names),
        "versions": unique(versions),
        "licenses": unique(license_values),
        "packages": packages,
    }


def detect_languages(files: list[Path]) -> list[dict[str, Any]]:
    mapping = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".kt": "Kotlin",
        ".go": "Go",
        ".cs": ".NET",
        ".rs": "Rust",
        ".dart": "Dart",
        ".swift": "Swift",
        ".php": "PHP",
        ".rb": "Ruby",
    }
    counts = Counter(mapping[path.suffix.lower()] for path in files if path.suffix.lower() in mapping)
    return [{"language": name, "file_count": count} for name, count in counts.most_common()]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(FILE_HASH_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_file_language(path: Path) -> str:
    suffix = path.suffix.lower()
    if path.name.lower() in {"pom.xml", "build.gradle", "build.gradle.kts", "gradle.lockfile"}:
        return "java"
    if path.name.lower() in {"requirements.txt", "pyproject.toml", "poetry.lock", "uv.lock", "pipfile", "pipfile.lock"}:
        return "python"
    if path.name.lower() in {"package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "tsconfig.json"}:
        return "javascript/typescript"
    if path.name.lower() in {"go.mod", "go.sum"}:
        return "go"
    return {
        ".py": "python",
        ".java": "java",
        ".js": "javascript",
        ".ts": "typescript",
        ".go": "go",
    }.get(suffix, "unknown")


def detect_package_manager(path: Path) -> str:
    name = path.name.lower()
    if name == "pom.xml":
        return "maven"
    if name in {"build.gradle", "build.gradle.kts", "gradle.lockfile", "settings.gradle", "settings.gradle.kts"}:
        return "gradle"
    if name.startswith("requirements") or name in {"pipfile", "pipfile.lock"}:
        return "pip"
    if name == "pyproject.toml":
        return "python-project"
    if name == "poetry.lock":
        return "poetry"
    if name == "uv.lock":
        return "uv"
    if name == "package.json" or name == "package-lock.json":
        return "npm"
    if name == "pnpm-lock.yaml":
        return "pnpm"
    if name == "yarn.lock":
        return "yarn"
    if name in {"go.mod", "go.sum"}:
        return "go-modules"
    if path.suffix.lower() in {".jar", ".whl", ".tgz", ".zip", ".tar.gz"}:
        return "binary-package"
    return "unknown"


def service_from_text(value: str) -> str:
    lowered = value.lower()
    for service, hints in CLOUD_SERVICE_HINTS.items():
        if any(hint.lower() in lowered for hint in hints):
            return service
    return ""


def file_inventory(source_dir: Path, files: list[Path], samples: dict[Path, str]) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for path in files:
        rel_path = path.relative_to(source_dir).as_posix()
        text = samples.get(path, "")
        cloud = detect_cloud_provider_from_text(text)
        inventory.append(
            {
                "relative_path": rel_path,
                "file_name": path.name,
                "file_type": path.suffix.lower() or path.name.lower(),
                "file_size": path.stat().st_size,
                "sha256": sha256_file(path),
                "detected_language": detect_file_language(path),
                "detected_package_manager": detect_package_manager(path),
                "detected_provider": cloud,
                "analysis_status": "analyzed",
                "skip_reason": "",
            }
        )
    return inventory


def detect_cloud_provider_from_text(text: str) -> str:
    providers = set()
    for item in CLOUD_SDK_PATTERNS:
        if item["pattern"].search(text):
            providers.add(str(item["provider"]))
    if len(providers) > 1:
        return "multiple"
    if providers:
        return sorted(providers)[0]
    return "unknown"


def cloud_service_hints(text: str) -> list[str]:
    lowered = text.lower()
    services = [
        service
        for service, hints in CLOUD_SERVICE_HINTS.items()
        if any(hint.lower() in lowered for hint in hints)
    ]
    return unique(services)


def detect_cloud_sdks(source_dir: Path, samples: dict[Path, str]) -> dict[str, Any]:
    sdks: list[dict[str, Any]] = []
    services: list[str] = []
    providers: list[str] = []
    languages: list[str] = []
    managers: list[str] = []
    generations: list[str] = []
    for path, text in samples.items():
        rel_path = path.relative_to(source_dir).as_posix()
        for item in CLOUD_SDK_PATTERNS:
            for match in item["pattern"].finditer(text):
                match_text = match.group(0)
                service = service_from_text(match_text) or service_from_text(text)
                provider = str(item["provider"])
                language = str(item["language"])
                manager = str(item["package_manager"])
                generation = str(item["generation"])
                providers.append(provider)
                languages.append(language)
                managers.append(manager)
                generations.append(generation)
                if service:
                    services.append(service)
                sdks.append(
                    {
                        "provider": provider,
                        "language": language,
                        "package_manager": manager,
                        "generation": generation,
                        "matched_text": match_text,
                        "service": service,
                        "source_file": rel_path,
                    }
                )
    unique_providers = unique(providers)
    provider_status = "multiple" if len(unique_providers) > 1 else unique_providers[0] if unique_providers else "unknown"
    auth = []
    all_text = "\n".join(samples.values()).lower()
    if provider_status in {"aws", "multiple"}:
        auth.extend(["AWS Credential Provider Chain", "IAM Role", "Access Key", "Web Identity"])
    if provider_status in {"gcp", "multiple"}:
        auth.extend(["GCP Application Default Credentials", "Service Account", "Workload Identity"])
    if "localstack" in all_text:
        services.append("localstack")
    if "emulator" in all_text:
        services.append("emulator")
    cloud = {
        "provider": provider_status,
        "providers": unique_providers,
        "languages": unique(languages),
        "package_managers": unique(managers),
        "sdk_generations": unique(generations),
        "sdks": sdks,
        "services": unique(services),
        "authentication_candidates": unique(auth),
        "region_project_requirements": region_project_requirements(provider_status),
        "local_testing": local_testing_guidance(provider_status, unique(services), all_text),
        "human_checks": cloud_human_checks(provider_status, unique(services)),
        "adoption_status": "needs_human_check" if unique_providers else "unknown",
    }
    return cloud


def region_project_requirements(provider: str) -> list[str]:
    requirements: list[str] = []
    if provider in {"aws", "multiple"}:
        requirements.extend(["AWS Region", "IAM permissions", "API endpoint / private endpoint requirement"])
    if provider in {"gcp", "multiple"}:
        requirements.extend(["GCP Project", "GCP Region / Zone", "API enablement", "Service Account roles"])
    if not requirements:
        requirements.append("Cloud provider is unknown; human confirmation is required.")
    return requirements


def local_testing_guidance(provider: str, services: list[str], all_text: str) -> dict[str, Any]:
    candidates: list[str] = []
    if provider in {"aws", "multiple"}:
        candidates.extend(["LocalStack", "botocore Stubber", "SDK mock / fake client"])
    if provider in {"gcp", "multiple"}:
        candidates.extend(["Google Cloud Emulator when available", "fake client", "sandbox project"])
    if "sandbox" in all_text:
        candidates.append("SDK-provided sandbox")
    if "mock" in all_text:
        candidates.append("SDK-provided mock")
    return {
        "required": True if provider in {"aws", "gcp", "multiple"} else False,
        "candidates": unique(candidates),
        "services": services,
    }


def cloud_human_checks(provider: str, services: list[str]) -> list[str]:
    checks = [
        "SDK採用可否とvendor lock-inを確認する。",
        "本番credentialを保存せず、credential管理方式を確認する。",
        "利用料金、quota、rate limit、production network利用条件を確認する。",
        "timeout、retry、logging、metrics、tracing、paginationを確認する。",
        "local test、mock、emulator、sandboxの可否を確認する。",
    ]
    if provider in {"aws", "multiple"}:
        checks.extend(["AWS IAM最小権限を確認する。", "AWS Regionと利用サービス提供状況を確認する。"])
    if provider in {"gcp", "multiple"}:
        checks.extend(["GCP Service Account最小権限を確認する。", "GCP Project、API有効化、Region / Zoneを確認する。"])
    if not services:
        checks.append("利用予定サービスが自動特定できないため、人間確認が必要。")
    return unique(checks)


def payment_service_from_text(value: str) -> str:
    lowered = value.lower()
    for service, hints in PAYMENT_SERVICE_HINTS.items():
        if any(hint.lower() in lowered for hint in hints):
            return service
    return ""


def detect_payment_sdks(source_dir: Path, samples: dict[Path, str]) -> dict[str, Any]:
    sdks: list[dict[str, Any]] = []
    services: list[str] = []
    vendors: list[str] = []
    languages: list[str] = []
    managers: list[str] = []
    generations: list[str] = []
    for path, text in samples.items():
        rel_path = path.relative_to(source_dir).as_posix()
        for item in PAYMENT_SDK_PATTERNS:
            for match in item["pattern"].finditer(text):
                match_text = match.group(0)
                service = payment_service_from_text(match_text) or payment_service_from_text(text)
                vendor = str(item["vendor"])
                language = str(item["language"])
                manager = str(item["package_manager"])
                generation = str(item["generation"])
                vendors.append(vendor)
                languages.append(language)
                managers.append(manager)
                generations.append(generation)
                if service:
                    services.append(service)
                sdks.append(
                    {
                        "vendor": vendor,
                        "category": "payment",
                        "language": language,
                        "package_manager": manager,
                        "generation": generation,
                        "matched_text": match_text,
                        "service": service,
                        "source_file": rel_path,
                    }
                )
    unique_vendors = unique(vendors)
    all_text = "\n".join(samples.values()).lower()
    if "webhook" in all_text:
        services.append("webhooks")
    if "checkout" in all_text:
        services.append("checkout")
    if "paymentintent" in all_text or "payment_intent" in all_text:
        services.append("payment_intents")
    detected = bool(unique_vendors)
    return {
        "category": "payment",
        "vendor": "multiple" if len(unique_vendors) > 1 else unique_vendors[0] if unique_vendors else "unknown",
        "vendors": unique_vendors,
        "languages": unique(languages),
        "package_managers": unique(managers),
        "sdk_generations": unique(generations),
        "sdks": sdks,
        "services": unique(services),
        "authentication_candidates": (
            ["Stripe secret key", "Stripe publishable key", "Restricted API key", "Webhook signing secret", "Stripe Connect OAuth"]
            if "stripe" in unique_vendors
            else []
        ),
        "operational_requirements": payment_operational_requirements(unique_vendors),
        "local_testing": payment_local_testing_guidance(unique_vendors, unique(services), all_text),
        "human_checks": payment_human_checks(unique_vendors, unique(services)),
        "adoption_status": "needs_human_check" if detected else "unknown",
    }


def payment_operational_requirements(vendors: list[str]) -> list[str]:
    requirements: list[str] = []
    if "stripe" in vendors:
        requirements.extend(
            [
                "Stripe test mode / live mode separation",
                "Webhook endpoint and signing secret handling",
                "Idempotency key policy for write operations",
                "Currency, amount rounding, tax, refund, and chargeback policy",
                "PCI scope and card data handling boundary",
            ]
        )
    if not requirements:
        requirements.append("Payment SDK vendor is unknown; human confirmation is required.")
    return requirements


def payment_local_testing_guidance(vendors: list[str], services: list[str], all_text: str) -> dict[str, Any]:
    candidates: list[str] = []
    if "stripe" in vendors:
        candidates.extend(["Stripe test mode", "Stripe CLI webhook forwarding", "SDK mock / fake client"])
    if "sandbox" in all_text:
        candidates.append("Vendor sandbox")
    if "mock" in all_text:
        candidates.append("SDK-provided mock")
    return {
        "required": bool(vendors),
        "candidates": unique(candidates),
        "services": services,
    }


def payment_human_checks(vendors: list[str], services: list[str]) -> list[str]:
    checks = []
    if "stripe" in vendors:
        checks.extend(
            [
                "Stripeの採用可否、手数料、利用国、利用規約、production利用条件を確認する。",
                "secret key / publishable key / webhook signing secretを保存しない運用を確認する。",
                "test modeとlive modeの分離、誤課金防止、idempotency key運用を確認する。",
                "Webhook再送、署名検証、イベント順序、重複処理、失敗時の再試行方針を確認する。",
                "返金、キャンセル、チャージバック、税、通貨、少数丸め、請求書の業務ルールを確認する。",
                "PCI scopeとカード情報を自システムで保持しない境界を確認する。",
            ]
        )
    if vendors and not services:
        checks.append("Payment SDKの利用機能が自動特定できないため、人間確認が必要。")
    return unique(checks)


def specialized_search_queries(payment: dict[str, Any]) -> list[dict[str, str]]:
    queries: list[dict[str, str]] = []
    if "stripe" in payment.get("vendors", []):
        for purpose, query in [
            ("official-docs", "Stripe official SDK documentation"),
            ("webhook", "Stripe webhook signature verification retry idempotency documentation"),
            ("testing", "Stripe test mode Stripe CLI webhook forwarding documentation"),
            ("security", "Stripe API keys restricted keys webhook signing secret security"),
            ("changelog", "Stripe SDK changelog migration guide"),
        ]:
            queries.append({"purpose": purpose, "query": query})
    return queries


def detect_keyword_hits(source_dir: Path, samples: dict[Path, str]) -> dict[str, list[dict[str, str]]]:
    keyword_sets = {
        "auth": ["api key", "apikey", "oauth", "bearer", "token", "service account", "certificate", "iam", "認証", "認可"],
        "network": ["endpoint", "base url", "proxy", "timeout", "retry", "rate limit", "websocket", "grpc", "http"],
        "constraints": ["deprecated", "unsupported", "beta", "preview", "thread safe", "license", "offline", "quota"],
        "tests": ["mock", "stub", "sandbox", "emulator", "test endpoint", "fixture", "pytest", "jest"],
        "errors": ["exception", "error code", "timeout", "429", "401", "403", "500", "rate limit"],
    }
    hits: dict[str, list[dict[str, str]]] = {key: [] for key in keyword_sets}
    for path, text in samples.items():
        lowered = text.lower()
        for category, keywords in keyword_sets.items():
            found = [keyword for keyword in keywords if keyword.lower() in lowered]
            if found:
                hits[category].append(
                    {
                        "file": path.relative_to(source_dir).as_posix(),
                        "keywords": ", ".join(unique(found)[:SDK_KEYWORD_PREVIEW_LIMIT]),
                    }
                )
    return hits


def detect_secret_findings(source_dir: Path, samples: dict[Path, str]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path, text in samples.items():
        matched = [pattern.pattern for pattern in SECRET_PATTERNS if pattern.search(text)]
        if matched:
            findings.append(
                {
                    "file": path.relative_to(source_dir).as_posix(),
                    "finding": "secret-like literal was detected; value is intentionally not copied.",
                }
            )
    return findings


def redact_secret_like_literals(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED_SECRET_LITERAL]", redacted)
    return redacted


def metadata_url(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ["url", "web", "homepage"]:
            if value.get(key):
                return str(value.get(key))
    return ""


def extract_urls(source_dir: Path, samples: dict[Path, str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for path, text in samples.items():
        for raw_url in URL_PATTERN.findall(text):
            url = raw_url.rstrip(".,;")
            if url.lower() in seen:
                continue
            seen.add(url.lower())
            rows.append(
                {
                    "url": url,
                    "file": path.relative_to(source_dir).as_posix(),
                    "source": "sdk-program-inline-url",
                }
            )
    return rows


def package_external_sources(package: dict[str, Any]) -> list[dict[str, str]]:
    manager = str(package.get("manager", ""))
    name = str(package.get("name", "")).strip()
    if not name:
        return []
    quoted_name = quote(name, safe="@/")
    encoded_name = quote(name, safe="")
    sources: list[dict[str, str]] = []
    if manager == "npm":
        sources.extend(
            [
                {"type": "package-registry", "priority": "high", "url": f"https://www.npmjs.com/package/{quoted_name}"},
                {"type": "package-registry-api", "priority": "medium", "url": f"https://registry.npmjs.org/{quoted_name}"},
            ]
        )
    elif manager == "python":
        sources.append({"type": "package-registry", "priority": "high", "url": f"https://pypi.org/project/{encoded_name}/"})
    elif manager == "cargo":
        sources.append({"type": "package-registry", "priority": "high", "url": f"https://crates.io/crates/{encoded_name}"})
    elif manager == "go":
        sources.append({"type": "package-registry", "priority": "high", "url": f"https://pkg.go.dev/{name}"})
    elif manager == "dart-pub":
        sources.append({"type": "package-registry", "priority": "high", "url": f"https://pub.dev/packages/{encoded_name}"})

    for field, source_type in [("homepage", "official-docs"), ("repository", "source-repository"), ("bugs", "issue-tracker")]:
        url = metadata_url(package.get(field, ""))
        if url:
            sources.append({"type": source_type, "priority": "high", "url": url})

    sources.extend(
        [
            {"type": "security-advisory", "priority": "medium", "url": f"https://osv.dev/list?q={encoded_name}"},
            {"type": "security-advisory", "priority": "medium", "url": f"https://github.com/advisories?query={encoded_name}"},
        ]
    )
    return sources


def external_source_candidates(metadata: dict[str, Any], inline_urls: list[dict[str, str]]) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    seen: set[str] = set()
    for package in metadata.get("packages", []):
        if isinstance(package, dict):
            for item in package_external_sources(package):
                key = item["url"].lower()
                if key not in seen:
                    candidates.append(item)
                    seen.add(key)
    for row in inline_urls:
        url = row.get("url", "")
        if url and url.lower() not in seen:
            candidates.append(
                {
                    "type": "sdk-inline-reference",
                    "priority": "medium",
                    "url": url,
                    "file": row.get("file", ""),
                }
            )
            seen.add(url.lower())
    return candidates


def external_search_queries(metadata: dict[str, Any]) -> list[dict[str, str]]:
    queries: list[dict[str, str]] = []
    for name in metadata.get("names", []):
        for purpose, template in [
            ("official-docs", "{name} official SDK documentation"),
            ("package-registry", "{name} package registry version license"),
            ("changelog", "{name} changelog release notes migration guide"),
            ("security", "{name} security advisory vulnerability"),
            ("deprecation", "{name} deprecated unsupported end of life"),
            ("license", "{name} license terms production use"),
        ]:
            queries.append({"purpose": purpose, "query": template.format(name=name)})
    return queries


def render_discovery_report(context: dict[str, Any]) -> str:
    sources = context.get("external_source_candidates", [])
    queries = context.get("search_queries", [])
    artifacts = context.get("artifacts", {})
    lines = [
        "# SDK外部関連資料 discovery report",
        "",
        f"- status: `{context.get('status', '')}`",
        f"- work_id: `{context.get('work_id', '')}`",
        f"- sdk_program: `{context.get('source', {}).get('path', '')}`",
        "",
        "## 外部確認候補URL",
        "",
    ]
    if sources:
        lines.extend(
            f"- [{item.get('type', '')}] {item.get('priority', '')}: {item.get('url', '')}"
            for item in sources
        )
    else:
        lines.append("- 未検出")
    lines.extend(["", "## 検索query", ""])
    if queries:
        lines.extend(f"- [{item.get('purpose', '')}] {item.get('query', '')}" for item in queries)
    else:
        lines.append("- 未生成")
    lines.extend(
        [
            "",
            "## 確認方針",
            "",
            "- 公式docs、package registry、公式repository、release notes、security advisoryを優先する。",
            "- 外部ページ本文を丸ごと保存しない。",
            "- 保存する場合は、claim、根拠URL、version、制約、Human Checkだけをcompactに残す。",
            "",
            "## 出力",
            "",
        ]
    )
    lines.extend(f"- {key}: `{value}`" for key, value in artifacts.items())
    return "\n".join(lines).rstrip() + "\n"


def render_external_requirements(context: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# SDK外部関連資料 要件追記候補",
            "",
            "この文書はSDKプログラムから抽出したpackage名、URL、metadataをもとに、外部確認すべき事項を要件定義へ引き継ぐための候補です。",
            "",
            "## 要件定義へ残す参照",
            "",
            f"- SDKプログラム格納場所: `{context.get('source', {}).get('path', '')}`",
            f"- 外部discovery context: `{context.get('artifacts', {}).get('context', '')}`",
            "",
            "## Human Check候補",
            "",
            "- 公式docsでproduction利用条件を確認する。",
            "- package registryでversion、license、deprecated / unsupported表示を確認する。",
            "- release notes / changelogでbreaking changeとmigration guideを確認する。",
            "- security advisoryで既知脆弱性を確認する。",
            "- 外部確認結果がローカルSDKプログラムと矛盾する場合は人間へ戻す。",
            "",
        ]
    )


def write_discovery_outputs(repo_root: Path, work_dir: Path, context: dict[str, Any]) -> dict[str, str]:
    report_path = reports_dir_for_work_dir(work_dir) / "sdk-external-discovery-report.md"
    context_path = context_dir_for_work_dir(work_dir) / "sdk-external-discovery.json"
    requirements_path = requirements_dir_for_work_dir(work_dir) / "sdk-external-requirements.md"
    artifacts = {
        "report": relative_to_repo(repo_root, report_path),
        "context": relative_to_repo(repo_root, context_path),
        "requirements": relative_to_repo(repo_root, requirements_path),
    }
    context["artifacts"] = artifacts
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_discovery_report(context), encoding="utf-8")
    requirements_path.parent.mkdir(parents=True, exist_ok=True)
    requirements_path.write_text(render_external_requirements(context), encoding="utf-8")
    write_json(context_path, context)
    return artifacts


def run_discovery(
    repo_root: Path,
    *,
    work_id: str,
    source: str = "",
    work_dir: str = "",
    max_files: int = SDK_ANALYSIS_MAX_FILES_DEFAULT,
    max_bytes: int = SDK_ANALYSIS_MAX_BYTES_DEFAULT,
) -> dict[str, Any]:
    work_path = resolve_work_dir(repo_root, work_id, work_dir)
    source_dir = resolve_repo_path(repo_root, source) if source else default_source_dir(repo_root)
    files = collect_files(source_dir, max_files=max_files)
    if not source_dir.exists() or not files:
        context = {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": DISCOVERY_ARTIFACT_TYPE,
            "status": "skipped",
            "skip_reason": "missing-or-empty-sdk-input",
            "work_id": work_id,
            "generated_at": utc_now_iso(),
            "source": {
                "path": relative_to_repo(repo_root, source_dir),
                "exists": source_dir.exists(),
                "analyzed_file_count": 0,
                "files": [],
            },
            "external_source_candidates": [],
            "search_queries": [],
            "message": "SDK program input was not found or had no analyzable files. SDK external discovery was skipped.",
        }
        artifacts = write_discovery_outputs(repo_root, work_path, context)
        context["artifacts"] = artifacts
        write_json(context_file(work_path, "sdk-external-discovery.json"), context)
        return context

    samples = {path: read_text_sample(path, max_bytes=max_bytes) for path in files}
    metadata = detect_package_metadata(source_dir, files)
    cloud = detect_cloud_sdks(source_dir, samples)
    payment = detect_payment_sdks(source_dir, samples)
    inline_urls = extract_urls(source_dir, samples)
    candidates = external_source_candidates(metadata, inline_urls)
    queries = external_search_queries(metadata) + specialized_search_queries(payment)
    status = "available" if candidates or queries else "human-check-required"
    context = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": DISCOVERY_ARTIFACT_TYPE,
        "status": status,
        "work_id": work_id,
        "generated_at": utc_now_iso(),
        "workflow": "requirement-discovery",
        "execution_mode": "search-plan",
        "source": {
            "path": relative_to_repo(repo_root, source_dir),
            "exists": source_dir.exists(),
            "analyzed_file_count": len(files),
            "files": [path.relative_to(source_dir).as_posix() for path in files],
        },
        "sdk": metadata,
        "cloud": cloud,
        "payment": payment,
        "inline_urls": inline_urls,
        "external_source_candidates": candidates,
        "search_queries": queries,
        "human_checks": [
            "外部確認は公式docs、package registry、公式repository、release notes、security advisoryを優先する。",
            "外部ページ本文を丸ごと保存せず、compact claimと根拠URLだけを残す。",
            "外部確認結果がローカルSDKプログラムと矛盾する場合は人間確認へ戻す。",
        ],
        "rules": {
            "network_fetch_is_not_performed_by_default": True,
            "external_web_rag_may_review_candidates": True,
            "do_not_store_full_external_page_bodies": True,
        },
    }
    artifacts = write_discovery_outputs(repo_root, work_path, context)
    manifest = register_context(
        repo_root,
        work_path,
        work_id=work_id,
        context_type="sdk-external-discovery",
        path=context_file(work_path, "sdk-external-discovery.json"),
        required=False,
        generated_by="sdk-discovery",
        owner="requirement-discovery",
        schema=DEFAULT_DISCOVERY_SCHEMA,
        status=status,
    )
    context["artifacts"] = artifacts
    context["manifest_path"] = relative_to_repo(repo_root, manifest_path_for_work_dir(work_path))
    context["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(context_file(work_path, "sdk-external-discovery.json"), context)
    return context


def human_checks(metadata: dict[str, Any], hits: dict[str, list[dict[str, str]]], secrets: list[dict[str, str]]) -> list[str]:
    checks = [
        "SDK採用可否、代替手段、vendor lock-inを人間が確認する。",
        "production network接続、外部送信、cost / quota / rate limitを人間が確認する。",
    ]
    if not metadata.get("licenses"):
        checks.append("LICENSEまたはpackage metadataから利用条件を確認できないため、人間確認が必要。")
    if hits.get("auth"):
        checks.append("認証方式、credential保管、token rotation、権限境界を人間が確認する。")
    else:
        checks.append("認証方式が資料から明確でないため、人間確認が必要。")
    if hits.get("constraints"):
        checks.append("deprecated / unsupported / beta / quotaなどの制約を人間が確認する。")
    if secrets:
        checks.append("secret-like literalが検出されたため、値を記録せず、漏えい有無を人間が確認する。")
    return unique(checks)


def status_from_analysis(files: list[Path], secrets: list[dict[str, str]]) -> str:
    if not files:
        return "skipped"
    if secrets:
        return "human-check-required"
    return "available"


def render_markdown_report(context: dict[str, Any]) -> str:
    sdk = context.get("sdk", {})
    cloud = context.get("cloud", {})
    payment = context.get("payment", {})
    source = context.get("source", {})
    hits = context.get("findings", {})
    human = context.get("human_checks", [])
    artifacts = context.get("artifacts", {})

    def bullet(values: list[str]) -> str:
        return "\n".join(f"- {value}" for value in values) if values else "- 未検出"

    lines = [
        "# SDK事前解析レポート",
        "",
        f"- status: `{context.get('status', '')}`",
        f"- work_id: `{context.get('work_id', '')}`",
        f"- source: `{source.get('path', '')}`",
        f"- analyzed_files: `{source.get('analyzed_file_count', 0)}`",
        "",
        "## SDK概要",
        "",
        f"- name: `{', '.join(sdk.get('names', [])) or '未検出'}`",
        f"- version: `{', '.join(sdk.get('versions', [])) or '未検出'}`",
        f"- license: `{', '.join(sdk.get('licenses', [])) or '未検出'}`",
        "",
        "## package / runtime",
        "",
    ]
    packages = sdk.get("packages", [])
    if packages:
        lines.extend(f"- {item.get('manager', '')}: `{item.get('file', '')}` {item.get('name', '')} {item.get('version', '')}".rstrip() for item in packages)
    else:
        lines.append("- 未検出")
    lines.extend(["", "## 認証・通信・制約の検出", ""])
    for category in ["auth", "network", "constraints", "tests", "errors"]:
        lines.extend([f"### {category}", ""])
        rows = hits.get(category, [])
        if not rows:
            lines.append("- 未検出")
        else:
            lines.extend(f"- `{row.get('file', '')}`: {row.get('keywords', '')}" for row in rows)
        lines.append("")
    lines.extend(
        [
            "## Cloud SDK",
            "",
            f"- provider: `{cloud.get('provider', 'unknown')}`",
            f"- providers: `{', '.join(cloud.get('providers', [])) or '未検出'}`",
            f"- languages: `{', '.join(cloud.get('languages', [])) or '未検出'}`",
            f"- package managers: `{', '.join(cloud.get('package_managers', [])) or '未検出'}`",
            f"- sdk generations: `{', '.join(cloud.get('sdk_generations', [])) or '未検出'}`",
            f"- services: `{', '.join(cloud.get('services', [])) or '未検出'}`",
            f"- adoption status: `{cloud.get('adoption_status', 'unknown')}`",
            "",
            "### Cloud Human Check",
            "",
        ]
    )
    cloud_checks = cloud.get("human_checks", [])
    lines.extend(f"- {item}" for item in cloud_checks) if cloud_checks else lines.append("- 未検出")
    lines.append("")
    lines.extend(
        [
            "## Payment SDK",
            "",
            f"- vendor: `{payment.get('vendor', 'unknown')}`",
            f"- vendors: `{', '.join(payment.get('vendors', [])) or '未検出'}`",
            f"- languages: `{', '.join(payment.get('languages', [])) or '未検出'}`",
            f"- package managers: `{', '.join(payment.get('package_managers', [])) or '未検出'}`",
            f"- services: `{', '.join(payment.get('services', [])) or '未検出'}`",
            f"- adoption status: `{payment.get('adoption_status', 'unknown')}`",
            "",
            "### Payment Human Check",
            "",
        ]
    )
    payment_checks = payment.get("human_checks", [])
    lines.extend(f"- {item}" for item in payment_checks) if payment_checks else lines.append("- 未検出")
    lines.append("")
    lines.extend(["## Human Check", "", bullet(human), "", "## 出力", ""])
    for key, value in artifacts.items():
        lines.append(f"- {key}: `{value}`")
    return "\n".join(lines).rstrip() + "\n"


def render_requirement_addendum(context: dict[str, Any]) -> str:
    sdk = context.get("sdk", {})
    cloud = context.get("cloud", {})
    payment = context.get("payment", {})
    human = context.get("human_checks", [])
    hits = context.get("findings", {})
    return "\n".join(
        [
            "# SDK連携 要件追記候補",
            "",
            "この文書はSDKプログラムの事前解析から作成した、要件定義review draftへ取り込むための候補です。",
            "",
            "## 候補SDK",
            "",
            f"- name: `{', '.join(sdk.get('names', [])) or '未検出'}`",
            f"- version: `{', '.join(sdk.get('versions', [])) or '未検出'}`",
            f"- license: `{', '.join(sdk.get('licenses', [])) or '未検出'}`",
            "",
            "## 要件へ反映すべき観点",
            "",
            "- SDK採用理由、代替手段、採用しない場合の影響を明記する。",
            "- 認証情報の保管、rotation、権限境界、ログ出力禁止条件を明記する。",
            "- timeout、retry、rate limit、通信失敗時のfallbackを明記する。",
            "- test double、sandbox、mock可否を明記する。",
            "- license、deprecated、unsupported、cost、production利用条件をHuman Checkで確定する。",
            "- AWS/GCP SDKを使う場合は、provider、service、IAM / Service Account、region / project、API有効化、local test可否を明記する。",
            "",
            "## 検出された入力材料",
            "",
            f"- auth evidence files: `{len(hits.get('auth', []))}`",
            f"- network evidence files: `{len(hits.get('network', []))}`",
            f"- constraint evidence files: `{len(hits.get('constraints', []))}`",
            f"- test evidence files: `{len(hits.get('tests', []))}`",
            f"- cloud provider: `{cloud.get('provider', 'unknown')}`",
            f"- cloud services: `{', '.join(cloud.get('services', [])) or '未検出'}`",
            f"- payment vendor: `{payment.get('vendor', 'unknown')}`",
            f"- payment services: `{', '.join(payment.get('services', [])) or '未検出'}`",
            "",
            "## 未確定質問",
            "",
            *[f"- {item}" for item in human],
            "",
        ]
    )


def knowledge_content(context: dict[str, Any]) -> str:
    sdk = context.get("sdk", {})
    cloud = context.get("cloud", {})
    payment = context.get("payment", {})
    findings = context.get("findings", {})
    checks = context.get("human_checks", [])
    return "\n".join(
        [
            f"SDK事前解析: {', '.join(sdk.get('names', [])) or context.get('work_id', '')}",
            f"versions: {', '.join(sdk.get('versions', [])) or '未検出'}",
            f"licenses: {', '.join(sdk.get('licenses', [])) or '未検出'}",
            f"auth evidence count: {len(findings.get('auth', []))}",
            f"network evidence count: {len(findings.get('network', []))}",
            f"constraint evidence count: {len(findings.get('constraints', []))}",
            f"cloud provider: {cloud.get('provider', 'unknown')}",
            f"cloud services: {', '.join(cloud.get('services', [])) or '未検出'}",
            f"payment vendor: {payment.get('vendor', 'unknown')}",
            f"payment services: {', '.join(payment.get('services', [])) or '未検出'}",
            "human checks:",
            *[f"- {item}" for item in checks],
        ]
    )


def knowledge_record(context: dict[str, Any]) -> dict[str, Any]:
    content = knowledge_content(context)
    knowledge_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"sdk-analysis:{context.get('work_id')}:{sha256_text(content)}"))
    sdk = context.get("sdk", {})
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": KNOWLEDGE_ARTIFACT_TYPE,
        "knowledge_id": knowledge_id,
        "title": f"SDK事前解析: {', '.join(sdk.get('names', [])) or context.get('work_id', '')}",
        "content": content,
        "summary": "要件定義工程でSDKプログラムを事前解析し、採用判断、認証、制約、テスト観点を抽出したKnowledge候補。",
        "semantic_hint": "SDK pre-analysis requirement discovery authentication license constraint testing",
        "category": "requirements",
        "document_type": "sdk-analysis",
        "source": "ariadne-ai-workflow-platform",
        "source_path": context.get("artifacts", {}).get("context", ""),
        "environment": "runtime",
        "workflow": "requirement-discovery",
        "metadata": {
            "status": context.get("status", ""),
            "trust_level": "medium",
            "tags": ["sdk", "requirement-discovery", "context-first"],
            "work_id": context.get("work_id", ""),
            "human_checks": context.get("human_checks", []),
            "secret_findings": context.get("secret_findings", []),
        },
    }


def write_outputs(
    repo_root: Path,
    work_dir: Path,
    context: dict[str, Any],
    *,
    knowledge_dir: Path,
    write_knowledge: bool,
) -> dict[str, str]:
    report_path = reports_dir_for_work_dir(work_dir) / "sdk-analysis-report.md"
    context_path = context_dir_for_work_dir(work_dir) / "sdk-analysis-context.json"
    inventory_path = context_dir_for_work_dir(work_dir) / "sdk-files.json"
    requirements_path = requirements_dir_for_work_dir(work_dir) / "sdk-integration-requirements.md"

    artifacts = {
        "report": relative_to_repo(repo_root, report_path),
        "context": relative_to_repo(repo_root, context_path),
        "inventory": relative_to_repo(repo_root, inventory_path),
        "requirements": relative_to_repo(repo_root, requirements_path),
    }
    context["artifacts"] = artifacts

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_markdown_report(context), encoding="utf-8")
    requirements_path.parent.mkdir(parents=True, exist_ok=True)
    requirements_path.write_text(render_requirement_addendum(context), encoding="utf-8")
    write_json(
        inventory_path,
        {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": "sdk-file-inventory",
            "work_id": context.get("work_id", ""),
            "source": context.get("source", {}),
            "files": context.get("inventory", []),
        },
    )
    write_json(context_path, context)

    if write_knowledge and context.get("status") != "skipped":
        record = knowledge_record(context)
        knowledge_path = knowledge_dir / f"{record['knowledge_id']}.json"
        write_json(knowledge_path, record)
        artifacts["knowledge_json"] = relative_to_repo(repo_root, knowledge_path)
        artifacts["duckdb_rebuild_command"] = (
            f"aiwfctl knowledge rebuild --source-repo {duckdb_store.DEFAULT_SOURCE_REPO_PATH.as_posix()} --reset"
        )
        context["artifacts"] = artifacts
        work_cleanup_hint.register_long_lived_artifact(
            repo_root,
            work_dir,
            work_id=str(context.get("work_id", "")),
            workflow_name="sdk-analysis",
            artifact_id="SDK-ANALYSIS-KNOWLEDGE",
            title=str(record.get("title", "SDK Analysis Knowledge")),
            path=knowledge_path,
            artifact_type="knowledge-json",
            status="verified" if context.get("status") == "available" else str(context.get("status", "draft")),
            owner_agent="sdk-analysis",
            summary=str(record.get("summary", "SDK analysis Knowledge JSON.")),
        )
        work_cleanup = work_cleanup_hint.record(repo_root, work_dir, str(context.get("work_id", "")))
        context["work_cleanup"] = work_cleanup
        context["next_action"] = work_cleanup_hint.next_action(
            work_cleanup,
            reason="SDK analysis Knowledge JSON is available in the long-lived knowledge area.",
        )
        artifacts["work_cleanup_check"] = work_cleanup.get("check_command", "")
        context["artifacts"] = artifacts
        write_json(context_path, context)
    return artifacts


def run_analysis(
    repo_root: Path,
    *,
    work_id: str,
    source: str = "",
    work_dir: str = "",
    knowledge_dir: str = "",
    write_knowledge: bool = True,
    skip: bool = False,
    max_files: int = SDK_ANALYSIS_MAX_FILES_DEFAULT,
    max_bytes: int = SDK_ANALYSIS_MAX_BYTES_DEFAULT,
) -> dict[str, Any]:
    work_path = resolve_work_dir(repo_root, work_id, work_dir)
    source_dir = resolve_repo_path(repo_root, source) if source else default_source_dir(repo_root)
    knowledge_path = resolve_repo_path(repo_root, knowledge_dir) if knowledge_dir else repo_root / DEFAULT_KNOWLEDGE_DIR

    files = [] if skip else collect_files(source_dir, max_files=max_files)
    if skip or not source_dir.exists() or not files:
        reason = "explicit-skip" if skip else "missing-or-empty-sdk-input"
        return {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": ARTIFACT_TYPE,
            "status": "skipped",
            "skip_reason": reason,
            "work_id": work_id,
            "source": {
                "path": relative_to_repo(repo_root, source_dir),
                "exists": source_dir.exists(),
                "analyzed_file_count": 0,
                "files": [],
            },
            "message": "SDK input was not found or had no analyzable files. SDK analysis was skipped.",
        }

    samples = {path: read_text_sample(path, max_bytes=max_bytes) for path in files}
    package_metadata = detect_package_metadata(source_dir, files)
    inventory = file_inventory(source_dir, files, samples)
    cloud = detect_cloud_sdks(source_dir, samples)
    payment = detect_payment_sdks(source_dir, samples)
    readme_path = find_readme(files)
    readme_excerpt = (
        redact_secret_like_literals(read_text_sample(readme_path, max_bytes=SDK_README_SAMPLE_MAX_BYTES)[:SDK_README_EXCERPT_MAX_CHARS])
        if readme_path
        else ""
    )
    hits = detect_keyword_hits(source_dir, samples)
    secrets = detect_secret_findings(source_dir, samples)
    checks = human_checks(package_metadata, hits, secrets)
    checks = unique(checks + payment.get("human_checks", []))
    status = status_from_analysis(files, secrets)

    context = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "status": status,
        "work_id": work_id,
        "generated_at": utc_now_iso(),
        "workflow": "requirement-discovery",
        "source": {
            "path": relative_to_repo(repo_root, source_dir),
            "exists": source_dir.exists(),
            "analyzed_file_count": len(files),
            "files": [path.relative_to(source_dir).as_posix() for path in files],
        },
        "sdk": {
            **package_metadata,
            "languages": detect_languages(files),
            "readme": readme_path.relative_to(source_dir).as_posix() if readme_path else "",
            "readme_excerpt": readme_excerpt,
        },
        "cloud": cloud,
        "payment": payment,
        "inventory": inventory,
        "findings": hits,
        "secret_findings": secrets,
        "human_checks": checks,
        "rules": {
            "do_not_copy_secret_values": True,
            "human_confirmation_required_for_license_auth_cost_and_production_network": True,
            "requirement_review_draft_must_carry_open_questions": True,
        },
    }
    artifacts = write_outputs(repo_root, work_path, context, knowledge_dir=knowledge_path, write_knowledge=write_knowledge)
    manifest = register_context(
        repo_root,
        work_path,
        work_id=work_id,
        context_type="sdk-analysis",
        path=context_file(work_path, "sdk-analysis-context.json"),
        required=False,
        generated_by="sdk-analysis",
        owner="requirement-discovery",
        schema=DEFAULT_CONTEXT_SCHEMA,
        status=status,
    )
    context["artifacts"] = artifacts
    context["manifest_path"] = relative_to_repo(repo_root, manifest_path_for_work_dir(work_path))
    context["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(context_file(work_path, "sdk-analysis-context.json"), context)
    return context


def format_result(result: dict[str, Any]) -> str:
    if result.get("artifact_type") == DISCOVERY_ARTIFACT_TYPE:
        if result.get("status") == "skipped":
            return "\n".join(
                [
                    "SDK External Discovery: skipped",
                    f"Reason : {result.get('skip_reason', '')}",
                    f"Source : {result.get('source', {}).get('path', '')}",
                    result.get("message", ""),
                ]
            )
        artifacts = result.get("artifacts", {})
        return "\n".join(
            [
                "SDK External Discovery",
                f"Status : {result.get('status', '')}",
                f"Work ID: {result.get('work_id', '')}",
                f"Source : {result.get('source', {}).get('path', '')}",
                f"Candidates: {len(result.get('external_source_candidates', []))}",
                f"Queries   : {len(result.get('search_queries', []))}",
                "",
                "Artifacts:",
                *[f"- {key}: {value}" for key, value in artifacts.items()],
            ]
        )
    if result.get("status") == "skipped":
        return "\n".join(
            [
                "SDK Analysis: skipped",
                f"Reason : {result.get('skip_reason', '')}",
                f"Source : {result.get('source', {}).get('path', '')}",
                result.get("message", ""),
            ]
        )
    artifacts = result.get("artifacts", {})
    return "\n".join(
        [
            "SDK Analysis",
            f"Status : {result.get('status', '')}",
            f"Work ID: {result.get('work_id', '')}",
            f"Source : {result.get('source', {}).get('path', '')}",
            f"Files  : {result.get('source', {}).get('analyzed_file_count', 0)}",
            "",
            "Artifacts:",
            *[f"- {key}: {value}" for key, value in artifacts.items()],
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze SDK program files before requirement discovery review drafting.")
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="Analyze work/requirements/sdk and create requirement-discovery context.")
    analyze.add_argument("--work-id", required=True)
    analyze.add_argument("--source", default="", help="SDK program directory. Default: work/requirements/sdk")
    analyze.add_argument("--work-dir", default="", help="Explicit work directory. Default: work/<work-id>")
    analyze.add_argument("--knowledge-dir", default="", help=f"Knowledge JSON output directory. Default: {DEFAULT_KNOWLEDGE_DIR.as_posix()}")
    analyze.add_argument("--no-knowledge", action="store_true", help="Do not write Knowledge JSON.")
    analyze.add_argument("--skip-sdk-analysis", action="store_true")
    analyze.add_argument("--max-files", type=int, default=SDK_ANALYSIS_MAX_FILES_DEFAULT)
    analyze.add_argument("--max-bytes", type=int, default=SDK_ANALYSIS_MAX_BYTES_DEFAULT)
    analyze.add_argument("--json", action="store_true")

    discover = sub.add_parser("discover", help="Create external source discovery plan from work/requirements/sdk.")
    discover.add_argument("--work-id", required=True)
    discover.add_argument("--source", default="", help="SDK program directory. Default: work/requirements/sdk")
    discover.add_argument("--work-dir", default="", help="Explicit work directory. Default: work/<work-id>")
    discover.add_argument("--max-files", type=int, default=SDK_ANALYSIS_MAX_FILES_DEFAULT)
    discover.add_argument("--max-bytes", type=int, default=SDK_ANALYSIS_MAX_BYTES_DEFAULT)
    discover.add_argument("--json", action="store_true")
    return parser


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = resolve_repo_path(Path.cwd(), args.repo_root).resolve() if getattr(args, "repo_root", "") else find_repo_root()
    if args.command == "analyze":
        return run_analysis(
            repo_root,
            work_id=args.work_id,
            source=args.source,
            work_dir=args.work_dir,
            knowledge_dir=args.knowledge_dir,
            write_knowledge=not args.no_knowledge,
            skip=args.skip_sdk_analysis,
            max_files=args.max_files,
            max_bytes=args.max_bytes,
        )
    if args.command == "discover":
        return run_discovery(
            repo_root,
            work_id=args.work_id,
            source=args.source,
            work_dir=args.work_dir,
            max_files=args.max_files,
            max_bytes=args.max_bytes,
        )
    raise ValueError(f"Unknown sdk-analysis command: {args.command}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = run(args)
    if getattr(args, "json", False):
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
