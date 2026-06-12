from __future__ import annotations

import argparse
import json
import re
import secrets
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo, slugify, utc_now_iso, write_json  # noqa: E402


DEFAULT_DRAFT_DIR = "work/devlop-edit-draft"
DEFAULT_RAG_SOURCE_DIR = "rag/workspace-environment"
CROCKFORD_BASE32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare VSCode environment workflow artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create the VSCode environment workflow work area.")
    init.add_argument("--work-id", default="vscode-environment")
    init.add_argument("--target-dir", default="")
    init.add_argument("--repo-root", default="")
    init.add_argument("--reuse-existing", action="store_true")

    req = subparsers.add_parser("requirements-template", help="Create workspace-requirements.md scaffold.")
    req.add_argument("--work-id", default="vscode-environment")
    req.add_argument("--repo-root", default="")

    validation = subparsers.add_parser("validation-template", help="Create shared artifact validation scaffold.")
    validation.add_argument("--work-id", default="vscode-environment")
    validation.add_argument("--repo-root", default="")
    validation.add_argument("--status", choices=["pass", "conditional-pass", "fail"], default="fail")

    draft = subparsers.add_parser("draft-template", help="Create a txt draft scaffold for the VSCode environment workflow.")
    draft.add_argument("--draft-dir", default=DEFAULT_DRAFT_DIR)
    draft.add_argument("--repo-root", default="")

    questions = subparsers.add_parser("open-questions", help="Create open-questions.md from txt draft intake.")
    questions.add_argument("--work-id", default="vscode-environment")
    questions.add_argument("--draft-dir", default=DEFAULT_DRAFT_DIR)
    questions.add_argument("--repo-root", default="")

    rag = subparsers.add_parser("rag-template", help="Create a VSCode environment RAG source Markdown file.")
    rag.add_argument("--work-id", default="vscode-environment")
    rag.add_argument("--source-dir", default=DEFAULT_RAG_SOURCE_DIR)
    rag.add_argument("--topic", default="localty-vscode-environment")
    rag.add_argument("--repository", default="localty")
    rag.add_argument("--target-workspace", default="")
    rag.add_argument("--status", default="draft")
    rag.add_argument("--repo-root", default="")

    return parser


def repo_root_from(args: argparse.Namespace) -> Path:
    return Path(args.repo_root).resolve() if args.repo_root else find_repo_root()


def work_dir(repo_root: Path, work_id: str) -> Path:
    return repo_root / "work" / work_id


def ensure_work_dirs(base: Path) -> None:
    for name in ["context", "design-document", "process-report", "test-evidence", "test-evidence/evidence"]:
        (base / name).mkdir(parents=True, exist_ok=True)


def init_work(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from(args)
    base = work_dir(repo_root, args.work_id)
    if base.exists() and not args.reuse_existing:
        raise FileExistsError(f"Work directory already exists: {base}. Re-run with --reuse-existing after confirming reuse.")
    ensure_work_dirs(base)
    target_dir = Path(args.target_dir).resolve() if args.target_dir else None
    state = {
        "schema_version": "1.0",
        "artifact_type": "vscode-environment-state",
        "workflow": "vscode-environment",
        "work_id": args.work_id,
        "target_dir": str(target_dir) if target_dir else "",
        "draft_dir": DEFAULT_DRAFT_DIR,
        "created_at": utc_now_iso(),
        "status": "initialized",
        "required_artifacts": [
            "workspace-requirements.md",
            "workspace-shared-artifact-validation.json",
            "vscode-design.md",
            "terminal-design.md",
            "workspace-test.md",
        ],
    }
    state_path = base / "context" / "vscode-environment-state.json"
    write_json(state_path, state)
    return {"work_dir": relative_to_repo(repo_root, base), "state_path": relative_to_repo(repo_root, state_path), **state}


def draft_template_text() -> str:
    return """VSCode Environment Draft

目的:
- TODO: このworkspaceで何を再現可能にしたいか

対象workspace:
- TODO: 例 C:\\github\\localty-system-gui

起動したいAI workflow:
- TODO: 例 /corrective-action-fix, /realtime-iac, /vscode-environment

必要tool / runtime:
- Git:
- Docker Desktop:
- Python / uv:
- Node.js:
- Java:
- MSYS2:
- その他:

必要VSCode拡張:
- TODO: extension ID または拡張名

Terminal構成:
- Dispatcher:
- Software Workflow:
- IaC Workflow:
- Docker Test:
- Evidence:

VSCode task案:
- TODO: task label と実行コマンド

Debug / launch案:
- TODO: launch name と対象program

試走したい内容:
- TODO: task実行、terminal起動、Docker連携、Python実行、AI workflow起動など

Evidence:
- TODO: 保存したいログ、スクリーンショット、human check

未確定:
- TODO
"""


def write_draft_template(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from(args)
    draft_dir = (repo_root / args.draft_dir).resolve()
    draft_dir.mkdir(parents=True, exist_ok=True)
    path = draft_dir / "vscode-environment-draft.txt"
    created = False
    if not path.exists():
        path.write_text(draft_template_text(), encoding="utf-8")
        created = True
    return {"draft_path": relative_to_repo(repo_root, path), "created": created}


def discover_txt_drafts(draft_dir: Path) -> list[Path]:
    if not draft_dir.exists():
        return []
    return sorted(path for path in draft_dir.iterdir() if path.is_file() and path.suffix.lower() == ".txt")


def open_questions_text(work_id: str, draft_dir: str, draft_paths: list[str]) -> str:
    draft_list = "\n".join(f"- `{path}`" for path in draft_paths) if draft_paths else "- none"
    return f"""# Open Questions: VSCode Environment

- workflow: `vscode-environment`
- work_id: `{work_id}`
- status: `blocked`
- draft_dir: `{draft_dir}`
- created_at: `{utc_now_iso()}`
- owner_agent: `workspace-requirements-analyst`

## Stop Reason

The VSCode Environment workflow starts from a txt draft. Required information must be confirmed by a human before `.vscode` files are created or changed.

## Draft Files

{draft_list}

## Required Confirmation Flow

```text
txt draft
  -> open-questions.md
  -> human review / answers
  -> approval
  -> .vscode environment implementation
  -> trial run / evidence
```

## Missing Required Inputs

| ID | Missing Item | Why Required | Required Answer |
| --- | --- | --- | --- |
| VSCODE-Q001 | target workspace path | `.vscode` files need a concrete target directory. | Absolute path to target repository / workspace |
| VSCODE-Q002 | workflow entrypoints | `tasks.json` needs explicit AI workflow commands. | Slash commands or task names to expose |
| VSCODE-Q003 | required tools / runtimes | preflight and task commands depend on these tools. | Git, Docker, Python, uv, Node.js, Java, MSYS2, etc. |
| VSCODE-Q004 | required VSCode extensions | `extensions.json` must list extension IDs. | Extension ID list |
| VSCODE-Q005 | terminal roles | terminal profiles and default shell must be explicit. | Dispatcher / Software / IaC / Docker / Evidence terminal settings |
| VSCODE-Q006 | trial run checks | completion needs concrete evidence. | Tasks, launch configs, Docker/runtime checks, human checks |

## Questions For Human

### VSCODE-Q001

Which workspace / repository should receive the VSCode environment files?

Answer:

```text

```

### VSCODE-Q002

Which AI workflow commands should be runnable from VSCode tasks?

Answer:

```text

```

### VSCODE-Q003

Which tools and runtimes are required for this workspace?

Answer:

```text

```

### VSCODE-Q004

Which VSCode extensions are required or recommended?

Answer:

```text

```

### VSCODE-Q005

What terminal profiles and roles should be created?

Answer:

```text

```

### VSCODE-Q006

What trial run should prove the VSCode environment works?

Answer:

```text

```

## Resume Instructions

After human answers are added and approved, initialize the work area with the confirmed target:

```powershell
uv run python runtime/workflow/vscode_environment.py init `
  --work-id "{work_id}" `
  --target-dir "<answered-target-workspace>" `
  --reuse-existing
```
"""


def write_open_questions(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from(args)
    base = work_dir(repo_root, args.work_id)
    ensure_work_dirs(base)
    draft_dir = (repo_root / args.draft_dir).resolve()
    draft_paths = [relative_to_repo(repo_root, path) for path in discover_txt_drafts(draft_dir)]
    path = base / "design-document" / "open-questions.md"
    path.write_text(open_questions_text(args.work_id, args.draft_dir, draft_paths), encoding="utf-8")
    state = {
        "schema_version": "1.0",
        "artifact_type": "vscode-environment-draft-state",
        "workflow": "vscode-environment",
        "work_id": args.work_id,
        "draft_dir": args.draft_dir,
        "draft_files": draft_paths,
        "open_questions_path": relative_to_repo(repo_root, path),
        "status": "blocked",
        "created_at": utc_now_iso(),
    }
    state_path = base / "context" / "vscode-environment-draft-state.json"
    write_json(state_path, state)
    return {"open_questions_path": relative_to_repo(repo_root, path), "state_path": relative_to_repo(repo_root, state_path), "draft_files": draft_paths}


def random_token(length: int = 6) -> str:
    return "".join(secrets.choice(CROCKFORD_BASE32) for _ in range(length))


def rag_filename(topic: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    topic_slug = slugify(topic).lower()
    topic_slug = re.sub(r"-+", "-", topic_slug).strip("-._") or "vscode-environment"
    return f"{timestamp}_{random_token()}_{topic_slug}.md"


def rag_template_text(args: argparse.Namespace, source_path: str) -> str:
    target_workspace = args.target_workspace or "TBD"
    return f"""---
title: Localty VSCode Environment Pattern
type: workspace-environment-pattern
project: localty
repository: {args.repository}
branch: TBD
commit: unknown
workflow: vscode-environment
phase: knowledge-capture
status: {args.status}
created_at: {utc_now_iso()}
source: {source_path}
tags:
  - localty
  - vscode-environment
  - workspace-as-code
  - ai-workflow
areas:
  - VSCode
  - terminal
  - tasks
  - launch
  - extensions
  - environment-preflight
  - evidence
---

# Localty VSCode Environment Pattern

## Summary

Localty repositories should treat VSCode configuration as Workspace as Code. The environment starts from a human-readable txt draft, turns unknowns into `open-questions.md`, waits for human approval, then creates `.vscode` artifacts and trial-run evidence.

## Scope

- target_workspace: `{target_workspace}`
- work_id: `{args.work_id}`
- source_rag_path: `{source_path}`
- source_type: internal project RAG

## Intake Pattern

1. Save a human draft under `work/devlop-edit-draft/*.txt`.
2. When `/vscode-environment` has no target argument or the draft is incomplete, create `work/<work-id>/design-document/open-questions.md`.
3. Wait for human answers and approval.
4. Initialize `work/<work-id>` with the confirmed target workspace.
5. Implement target `.vscode` files only after requirements and validation pass.

## Required Workspace Artifacts

- `.vscode/settings.json`
- `.vscode/tasks.json`
- `.vscode/launch.json`
- `.vscode/extensions.json`
- optional `<name>.code-workspace`
- `work/<work-id>/design-document/workspace-requirements.md`
- `work/<work-id>/design-document/vscode-design.md`
- `work/<work-id>/design-document/terminal-design.md`
- `work/<work-id>/context/workspace-shared-artifact-validation.json`
- `work/<work-id>/test-evidence/workspace-test.md`

## Localty Runtime Policy

- Prefer published Python packages for shared protocol dependencies, such as `localty-system-protocol>=0.1.0`.
- If package install or import verification fails, use the direct support repository fallback only after recording the reason.
- Keep MSYS2, uv, Python, Docker, and VSCode checks explicit in preflight evidence.
- Do not store tokens, secrets, or personal-only absolute paths in committed workspace files.

## Terminal Role Pattern

Recommended terminal roles:

| Role | Purpose |
| --- | --- |
| Dispatcher | Run AI workflow commands and coordinate artifacts. |
| Software Workflow | Run Python, test, lint, and application commands. |
| IaC Workflow | Run Docker, compose, gateway, network, and deployment checks. |
| Docker Test | Isolate Docker Desktop and compose validation commands. |
| Evidence | Capture logs, screenshots, manual checks, and skipped-test notes. |

## Task Pattern

VSCode tasks should expose stable workflow commands instead of personal shell history. Prefer labels that map to workflow intent, such as:

- `workflow:vscode-open-questions`
- `workflow:vscode-preflight`
- `workflow:vscode-test`
- `workflow:corrective-action-fix`
- `workflow:rag-load`
- `workflow:rag-build`

## Evidence Pattern

Record trial-run evidence under:

```text
work/<work-id>/test-evidence/
```

Evidence should include JSON validity, task labels, terminal profile startup, launch configuration checks, runtime version checks, Docker checks when applicable, and human-check items when UI observation is required.

## RAG Capture Rule

When a Localty VSCode environment pattern becomes reusable, store the Markdown source under:

```text
rag/workspace-environment/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

Then build it with:

```powershell
uv run python runtime/rag/standardize_corrective_report_names.py `
  --source-dir rag/workspace-environment `
  --replace-references

uv run python runtime/rag/normalize_documents.py `
  --source-dir rag/workspace-environment `
  --output-dir rag/normalized `
  --document-type workspace-environment-pattern
```

## Open Questions

- Which Localty repository is the first target: GUI, robot, simulator, protocol, or a multi-root workspace?
- Which terminal profile should be the default for each repository?
- Which tasks should be required and which should be recommended only?
- Which checks require human observation because VSCode UI state cannot be proven from CLI output alone?
"""


def write_rag_template(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from(args)
    source_dir = (repo_root / args.source_dir).resolve()
    try:
        source_dir.relative_to(repo_root.resolve())
    except ValueError:
        raise ValueError(f"RAG source directory must be inside repo root: {source_dir}")
    source_dir.mkdir(parents=True, exist_ok=True)
    path = source_dir / rag_filename(args.topic)
    source_path = relative_to_repo(repo_root, path)
    path.write_text(rag_template_text(args, source_path), encoding="utf-8")
    return {"path": source_path, "document_type": "workspace-environment-pattern"}


def requirements_text(work_id: str) -> str:
    return f"""# Workspace Requirements

- workflow: `vscode-environment`
- work_id: `{work_id}`
- status: `draft`

## Intent

TODO: Describe why this VSCode workspace is needed and which AI/human workflows it must support.

## Target Workspace

- path: TODO
- repository: TODO
- branch: TODO

## Required Tools

| Tool | Required | Version Policy | Install / Check Command | Notes |
| --- | --- | --- | --- | --- |
| Git | yes | TODO | `git --version` | TODO |
| Docker Desktop | TODO | TODO | `docker version` | TODO |
| Python | TODO | TODO | `python --version` or `uv run python --version` | TODO |
| Node.js | TODO | TODO | `node --version` | TODO |
| Java | TODO | TODO | `java --version` | TODO |

## Required VSCode Extensions

| Extension ID | Required | Reason |
| --- | --- | --- |
| TODO | yes | TODO |

## Terminal Profiles

| Role | Profile Name | Shell | Working Directory | Startup Command |
| --- | --- | --- | --- | --- |
| Dispatcher | TODO | TODO | TODO | TODO |
| Software Workflow | TODO | TODO | TODO | TODO |
| IaC Workflow | TODO | TODO | TODO | TODO |
| Docker Test | TODO | TODO | TODO | TODO |
| Evidence | TODO | TODO | TODO | TODO |

## Tasks

| Label | Command | Depends On | Evidence |
| --- | --- | --- | --- |
| TODO | TODO | TODO | TODO |

## Debug / Launch Targets

| Name | Runtime | Program | Preconditions |
| --- | --- | --- | --- |
| TODO | TODO | TODO | TODO |

## AI Workflow Entrypoints

| Task Label | Workflow | Command | Evidence |
| --- | --- | --- | --- |
| TODO | TODO | TODO | TODO |

## Docker / Runtime Integration

TODO: Describe Docker Desktop, compose files, exposed ports, health checks, and logs.

## Evidence Workflow

TODO: Describe where test evidence, screenshots, logs, and human checks are stored.

## Personal Values And Placeholders

TODO: List paths, secrets, tokens, machine names, or devices that must stay placeholders.

## Open Questions

- TODO
"""


def write_requirements_template(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from(args)
    base = work_dir(repo_root, args.work_id)
    ensure_work_dirs(base)
    path = base / "design-document" / "workspace-requirements.md"
    if not path.exists():
        path.write_text(requirements_text(args.work_id), encoding="utf-8")
    return {"path": relative_to_repo(repo_root, path), "created": True}


def validation_markdown(data: dict[str, Any]) -> str:
    missing = data.get("missing_required_items", [])
    questions = data.get("open_questions", [])
    lines = [
        "# Workspace Shared Artifact Validation",
        "",
        f"- status: `{data['status']}`",
        f"- created_at: `{data['created_at']}`",
        "",
        "## Missing Required Items",
        "",
    ]
    lines.extend([f"- {item}" for item in missing] or ["- none"])
    lines.extend(["", "## Open Questions", ""])
    lines.extend([f"- {item}" for item in questions] or ["- none"])
    return "\n".join(lines) + "\n"


def write_validation_template(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from(args)
    base = work_dir(repo_root, args.work_id)
    ensure_work_dirs(base)
    data: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "workspace-shared-artifact-validation",
        "workflow": "vscode-environment",
        "work_id": args.work_id,
        "created_at": utc_now_iso(),
        "status": args.status,
        "missing_required_items": [
            "required tool list",
            "required VSCode extension list",
            "terminal profile structure",
            "AI workflow entry task list",
        ],
        "conditions": [],
        "open_questions": [
            "Which target workspace should receive .vscode files?",
            "Which tasks must be available from VSCode?",
        ],
        "evidence": [],
    }
    json_path = base / "context" / "workspace-shared-artifact-validation.json"
    md_path = base / "process-report" / "workspace-shared-artifact-validation.md"
    write_json(json_path, data)
    md_path.write_text(validation_markdown(data), encoding="utf-8")
    return {"json_path": relative_to_repo(repo_root, json_path), "markdown_path": relative_to_repo(repo_root, md_path)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = init_work(args)
        elif args.command == "requirements-template":
            result = write_requirements_template(args)
        elif args.command == "validation-template":
            result = write_validation_template(args)
        elif args.command == "draft-template":
            result = write_draft_template(args)
        elif args.command == "open-questions":
            result = write_open_questions(args)
        elif args.command == "rag-template":
            result = write_rag_template(args)
        else:  # pragma: no cover
            parser.error(f"Unknown command: {args.command}")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
