from __future__ import annotations

from pathlib import Path


WORK_ROOT = Path("work")
WORK_ID_PLACEHOLDER = "<work-id>"
WORK_REQUIREMENTS_DIR = WORK_ROOT / "requirements"
SVG_INPUT_DIR = WORK_REQUIREMENTS_DIR / "svg-input"

CONTEXT_DIR_NAME = "context"
CONTEXT_MANIFEST_FILE_NAME = "context-manifest.json"
PROCESS_REPORT_DIR_NAME = "process-report"
REPORTS_DIR_NAME = "reports"
DESIGN_DOCUMENT_DIR_NAME = "design-document"
REQUIREMENTS_DIR_NAME = "requirements"
SOURCE_DIR_NAME = "source"
TARGET_REPOSITORY_RELATIVE = Path(SOURCE_DIR_NAME) / "repository"
TEST_EVIDENCE_DIR_NAME = "test-evidence"
TEST_ENVIRONMENT_DIR_NAME = "test-environment"
IMPLEMENTATION_DIR_NAME = "implementation"
GIT_WORKTREE_DIR_NAME = "git-worktree"

WORK_DIR_PATTERN = f"{WORK_ROOT.as_posix()}/{WORK_ID_PLACEHOLDER}"
TARGET_REPOSITORY_PATTERN = f"{WORK_DIR_PATTERN}/{TARGET_REPOSITORY_RELATIVE.as_posix()}"

DEFAULT_WORK_DIR_HELP = f"Explicit work directory. Default: {WORK_DIR_PATTERN}"
DEFAULT_TARGET_REPO_HELP = f"Target repository. Default: {TARGET_REPOSITORY_PATTERN}"


def work_path_pattern(*parts: str, work_id: str = WORK_ID_PLACEHOLDER) -> str:
    base = f"{WORK_ROOT.as_posix()}/{work_id}"
    suffix = Path(*parts).as_posix() if parts else ""
    return f"{base}/{suffix}" if suffix else base


def context_path_pattern(filename: str = "*") -> str:
    return work_path_pattern(CONTEXT_DIR_NAME, filename)


def process_report_path_pattern(filename: str = "*") -> str:
    return work_path_pattern(PROCESS_REPORT_DIR_NAME, filename)


def reports_path_pattern(filename: str = "*") -> str:
    return work_path_pattern(REPORTS_DIR_NAME, filename)


def requirements_path_pattern(filename: str = "*") -> str:
    return work_path_pattern(REQUIREMENTS_DIR_NAME, filename)


def test_evidence_path_pattern(filename: str = "*") -> str:
    return work_path_pattern(TEST_EVIDENCE_DIR_NAME, filename)


def implementation_path_pattern(*parts: str) -> str:
    return work_path_pattern(IMPLEMENTATION_DIR_NAME, *parts)


def git_worktree_path_pattern(branch: str = "<target-branch>") -> str:
    return work_path_pattern(GIT_WORKTREE_DIR_NAME, branch)


def work_dir_for_id(repo_root: Path, work_id: str) -> Path:
    return repo_root / WORK_ROOT / work_id


def svg_input_dir(repo_root: Path) -> Path:
    return repo_root / SVG_INPUT_DIR


def work_requirements_dir(repo_root: Path) -> Path:
    return repo_root / WORK_REQUIREMENTS_DIR


def resolve_work_dir(repo_root: Path, work_id: str, work_dir: str | Path = "") -> Path:
    if work_dir:
        raw = Path(work_dir)
        return raw if raw.is_absolute() else repo_root / raw
    return work_dir_for_id(repo_root, work_id)


def context_dir_for_work_dir(work_dir: Path) -> Path:
    return work_dir / CONTEXT_DIR_NAME


def context_file(work_dir: Path, filename: str) -> Path:
    return context_dir_for_work_dir(work_dir) / filename


def manifest_path_for_work_dir(work_dir: Path) -> Path:
    return context_file(work_dir, CONTEXT_MANIFEST_FILE_NAME)


def process_report_dir_for_work_dir(work_dir: Path) -> Path:
    return work_dir / PROCESS_REPORT_DIR_NAME


def reports_dir_for_work_dir(work_dir: Path) -> Path:
    return work_dir / REPORTS_DIR_NAME


def design_document_dir_for_work_dir(work_dir: Path) -> Path:
    return work_dir / DESIGN_DOCUMENT_DIR_NAME


def requirements_dir_for_work_dir(work_dir: Path) -> Path:
    return work_dir / REQUIREMENTS_DIR_NAME


def source_dir_for_work_dir(work_dir: Path) -> Path:
    return work_dir / SOURCE_DIR_NAME


def target_repository_dir_for_work_dir(work_dir: Path) -> Path:
    return work_dir / TARGET_REPOSITORY_RELATIVE


def test_evidence_dir_for_work_dir(work_dir: Path) -> Path:
    return work_dir / TEST_EVIDENCE_DIR_NAME


def test_environment_dir_for_work_dir(work_dir: Path) -> Path:
    return work_dir / TEST_ENVIRONMENT_DIR_NAME


def implementation_dir_for_work_dir(work_dir: Path) -> Path:
    return work_dir / IMPLEMENTATION_DIR_NAME


def git_worktree_dir_for_work_dir(work_dir: Path) -> Path:
    return work_dir / GIT_WORKTREE_DIR_NAME
