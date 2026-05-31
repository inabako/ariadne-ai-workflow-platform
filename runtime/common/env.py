from __future__ import annotations

import os
import re
from pathlib import Path


def parse_env_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None
    key, value = stripped.split("=", 1)
    key = key.strip()
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    if not key:
        return None
    return key, value


def load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    settings: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        parsed = parse_env_line(line)
        if parsed:
            key, value = parsed
            settings[key] = value
    return settings


def load_env(repo_root: Path, include_process: bool = True) -> dict[str, str]:
    settings: dict[str, str] = {}
    if include_process:
        settings.update({key: value for key, value in os.environ.items() if isinstance(value, str)})
    settings.update(load_env_file(repo_root / ".env"))
    return settings


def env_csv(settings: dict[str, str], key: str) -> list[str]:
    value = settings.get(key, "")
    return [item.strip() for item in value.split(",") if item.strip()]


def env_value(settings: dict[str, str], *keys: str, default: str = "") -> str:
    for key in keys:
        value = settings.get(key, "")
        if value:
            return value
    return default


def resolve_github_repo(settings: dict[str, str], explicit: str | None = None) -> str:
    if explicit:
        return explicit
    raise ValueError("GitHub repository is required. Set --github-repo or prepare scm-state.json from requirements.")


def repository_to_github_slug(repository: str) -> str | None:
    value = repository.strip()
    if not value:
        return None
    if re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", value):
        return value
    patterns = [
        r"github\.com[:/](?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$",
        r"https?://[^/]*github[^/]*/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    return None


def repository_to_clone_source(repository: str) -> str:
    value = repository.strip()
    if re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", value):
        return f"https://github.com/{value}.git"
    return value
