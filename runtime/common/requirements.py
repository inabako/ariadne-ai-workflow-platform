from __future__ import annotations

from pathlib import Path

from .common import read_json


REPOSITORY_KEYS = {
    "target repository",
    "repository",
    "repository url",
    "git repository url",
    "github repository url",
}
GITHUB_OWNER_KEYS = {"github owner", "owner"}
GITHUB_REPO_KEYS = {"github repository", "github repo", "repo"}
TARGET_BRANCH_KEYS = {"target branch", "base branch", "branch"}
REMOTE_KEYS = {"git remote", "remote"}


def normalize_key(value: str) -> str:
    return value.strip().lower().replace("`", "")


def split_markdown_table_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    if len(cells) < 2:
        return None
    if all(set(cell) <= {"-", ":", " "} for cell in cells):
        return None
    return cells


def extract_repository_config_from_text(text: str) -> dict[str, str]:
    config: dict[str, str] = {}
    table_values: dict[str, str] = {}

    for line in text.splitlines():
        cells = split_markdown_table_row(line)
        if cells and len(cells) >= 2:
            key = normalize_key(cells[0])
            value = cells[1].strip()
            if key not in {"item", "key", "field"} and value:
                table_values[key] = value
            continue

        if ":" in line and not line.lstrip().startswith("#"):
            key, value = line.split(":", 1)
            key = normalize_key(key)
            value = value.strip()
            if value:
                table_values[key] = value

    github_owner = ""
    github_repo = ""
    for key, value in table_values.items():
        if key in REPOSITORY_KEYS:
            config["repository"] = value
        elif key in GITHUB_OWNER_KEYS:
            github_owner = value
        elif key in GITHUB_REPO_KEYS:
            github_repo = value
        elif key in TARGET_BRANCH_KEYS:
            config["target_branch"] = value
        elif key in REMOTE_KEYS:
            config["remote"] = value

    if "repository" not in config and github_owner and github_repo:
        if "/" in github_repo:
            config["repository"] = github_repo
        else:
            config["repository"] = f"{github_owner}/{github_repo}"
    return config


def extract_repository_config_from_files(paths: list[Path]) -> dict[str, str]:
    config: dict[str, str] = {}
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        file_config = extract_repository_config_from_text(text)
        config.update({key: value for key, value in file_config.items() if value})
    return config


def requirement_files_from_artifact_index(repo_root: Path, work_dir: Path) -> list[Path]:
    index = read_json(work_dir / "context" / "artifact-index.json", default={}) or {}
    paths = []
    for artifact in index.get("artifacts", []):
        if artifact.get("type") != "requirement":
            continue
        raw_path = artifact.get("path")
        if not raw_path:
            continue
        path = Path(raw_path)
        paths.append(path if path.is_absolute() else repo_root / path)
    return paths

