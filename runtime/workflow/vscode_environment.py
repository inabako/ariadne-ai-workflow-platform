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
from runtime.constants.paths import (  # noqa: E402
    GENERATED_NORMALIZED,
    KNOWLEDGE_SOURCE_LOCAL_BACKUP_DIRS,
    KNOWLEDGE_SOURCE_REPO,
    SOURCE_WORKSPACE_ENVIRONMENT,
)
from runtime.constants.schemas import RUNTIME_CONTEXT_SCHEMA, VSCODE_ENVIRONMENT_STATE_SCHEMA  # noqa: E402
from runtime.constants.workspace import (
    CONTEXT_DIR_NAME,
    DESIGN_DOCUMENT_DIR_NAME,
    PROCESS_REPORT_DIR_NAME,
    TEST_EVIDENCE_DIR_NAME,
    context_file,
    design_document_dir_for_work_dir,
    process_report_dir_for_work_dir,
    work_dir_for_id,
)  # noqa: E402
from runtime.workflow.context_first import register_context  # noqa: E402
from runtime.workflow import work_cleanup_hint  # noqa: E402


DEFAULT_DRAFT_DIR = "work/requirements/devlop-edit-draft"
DEFAULT_DRAFT_SCAFFOLD = "README.md"
DEFAULT_RAG_SOURCE_DIR = SOURCE_WORKSPACE_ENVIRONMENT.as_posix()
CROCKFORD_BASE32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
UTF8_POWERSHELL_STARTUP = (
    "[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false); "
    "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false); "
    "$OutputEncoding = [System.Text.UTF8Encoding]::new($false); "
    "chcp 65001 > $null"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare VSCode environment workflow artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create the VSCode environment workflow work area.")
    init.add_argument("--work-id", default="vscode-environment")
    init.add_argument("--target-dir", default="")
    init.add_argument("--mode", choices=["self-provision", "target-workspace", "custom-design"], default="self-provision")
    init.add_argument("--repo-root", default="")
    init.add_argument("--reuse-existing", action="store_true")

    req = subparsers.add_parser("requirements-template", help="Create workspace-requirements.md scaffold.")
    req.add_argument("--work-id", default="vscode-environment")
    req.add_argument("--mode", choices=["self-provision", "target-workspace", "custom-design"], default="self-provision")
    req.add_argument("--repo-root", default="")

    validation = subparsers.add_parser("validation-template", help="Create shared artifact validation scaffold.")
    validation.add_argument("--work-id", default="vscode-environment")
    validation.add_argument("--mode", choices=["self-provision", "target-workspace", "custom-design"], default="self-provision")
    validation.add_argument("--repo-root", default="")
    validation.add_argument("--status", choices=["pass", "conditional-pass", "fail"], default="fail")

    draft = subparsers.add_parser("draft-template", help="Create a human-editable draft README scaffold for the VSCode environment workflow.")
    draft.add_argument("--draft-dir", default=DEFAULT_DRAFT_DIR)
    draft.add_argument("--repo-root", default="")

    questions = subparsers.add_parser("open-questions", help="Create open-questions.md for unresolved custom-design intake.")
    questions.add_argument("--work-id", default="vscode-environment")
    questions.add_argument("--draft-dir", default=DEFAULT_DRAFT_DIR)
    questions.add_argument("--repo-root", default="")

    rag = subparsers.add_parser("rag-template", help="Create a VSCode environment RAG source Markdown file.")
    rag.add_argument("--work-id", default="vscode-environment")
    rag.add_argument("--source-dir", default=DEFAULT_RAG_SOURCE_DIR)
    rag.add_argument("--topic", default="localty-vscode-environment")
    rag.add_argument("--repository", default="localty")
    rag.add_argument("--target-workspace", default="")
    rag.add_argument("--mode", choices=["self-provision", "target-workspace", "custom-design"], default="self-provision")
    rag.add_argument("--status", default="draft")
    rag.add_argument("--repo-root", default="")

    return parser


def repo_root_from(args: argparse.Namespace) -> Path:
    return Path(args.repo_root).resolve() if args.repo_root else find_repo_root()


def work_dir(repo_root: Path, work_id: str) -> Path:
    return work_dir_for_id(repo_root, work_id)


def ensure_work_dirs(base: Path) -> None:
    for name in [
        CONTEXT_DIR_NAME,
        DESIGN_DOCUMENT_DIR_NAME,
        PROCESS_REPORT_DIR_NAME,
        TEST_EVIDENCE_DIR_NAME,
        f"{TEST_EVIDENCE_DIR_NAME}/evidence",
    ]:
        (base / name).mkdir(parents=True, exist_ok=True)


def ensure_knowledge_source_local_backup(repo_root: Path) -> list[str]:
    created: list[str] = []
    for relative_dir in KNOWLEDGE_SOURCE_LOCAL_BACKUP_DIRS:
        target = repo_root / relative_dir
        existed = target.exists()
        target.mkdir(parents=True, exist_ok=True)
        if not existed:
            created.append(relative_to_repo(repo_root, target))
    return created


def utf8_first_contract() -> dict[str, Any]:
    return {
        "policy": "utf-8-first",
        "required": True,
        "vscode_settings": {
            "files.encoding": "utf8",
            "files.autoGuessEncoding": False,
            "files.eol": "\n",
            "terminal.integrated.env.windows": {
                "PYTHONUTF8": "1",
                "PYTHONIOENCODING": "utf-8",
                "AIWF_TEXT_ENCODING": "utf-8",
            },
        },
        "powershell_startup": UTF8_POWERSHELL_STARTUP,
        "editorconfig_required": {
            "[*]": {
                "charset": "utf-8",
                "end_of_line": "lf",
            },
            "[*.{bat,cmd}]": {
                "charset": "unset",
                "end_of_line": "crlf",
            },
        },
        "codex_config_note": {
            "scope": "~/.codex/config.toml or <repo>/.codex/config.toml",
            "standard_encoding_key_supported": False,
            "do_not_add_encoding_table_as_enforcement": True,
            "note": "Codex config.toml is for documented Codex settings such as model, provider, approvals, sandbox, MCP, hooks, and features. Do not rely on an invented [encoding] table for mojibake prevention.",
            "recommended_policy_location": "AGENTS.md or workflow docs for human/agent guidance; .vscode/settings.json, .editorconfig, PowerShell profile, and aiwfctl doctor for enforcement.",
        },
        "doctor_check": "aiwfctl doctor --fail-on-warning",
    }


def init_work(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from(args)
    base = work_dir(repo_root, args.work_id)
    if base.exists() and not args.reuse_existing:
        raise FileExistsError(f"Work directory already exists: {base}. Re-run with --reuse-existing after confirming reuse.")
    ensure_work_dirs(base)
    created_backup_dirs = ensure_knowledge_source_local_backup(repo_root)
    target_dir = Path(args.target_dir).resolve() if args.target_dir else None
    state = {
        "schema_version": "1.0",
        "artifact_type": "vscode-environment-state",
        "workflow": "vscode-environment",
        "work_id": args.work_id,
        "mode": args.mode,
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
    state_path = context_file(base, "vscode-environment-state.json")
    write_json(state_path, state)
    runtime_context = {
        "schema_version": "1.0",
        "artifact_type": "runtime-context",
        "architecture": "context-first",
        "workflow": "vscode-environment",
        "work_id": args.work_id,
        "mode": args.mode,
        "target_dir": str(target_dir) if target_dir else "",
        "created_at": utc_now_iso(),
        "runtime": {
            "host_os": "Windows",
            "default_shell": "PowerShell",
            "terminal_scope": "VSCode integrated terminal",
        },
        "encoding_contract": utf8_first_contract(),
        "tool_paths": [
            "runtime/windows-script",
        ],
        "knowledge_source_backup": {
            "mode": "local-backup",
            "push_to_git": False,
            "source_repo": KNOWLEDGE_SOURCE_REPO.as_posix(),
            "created_dirs": created_backup_dirs,
        },
        "verification_commands": [
            "aiwfctl path check",
            "aiwfctl help list",
            "uv run --project runtime python runtime/ctl/ctl.py --repo-root . workflow validate-vscode-workspace check --workspace .",
            "uv run --project runtime python runtime/ctl/ctl.py --repo-root . doctor --fail-on-warning",
        ],
        "human_check_required_when": [
            "User Path, default terminal, extensions, Docker Desktop, or local tool installation changes affect the human environment.",
            "A target workspace has existing .vscode files that would be overwritten.",
            "custom-design mode requests personal paths, special terminals, or non-standard toolchains.",
        ],
    }
    runtime_context_path = context_file(base, "runtime-context.json")
    write_json(runtime_context_path, runtime_context)
    register_context(
        repo_root,
        base,
        work_id=args.work_id,
        context_type="vscode-environment-state",
        path=state_path,
        required=True,
        generated_by="vscode-environment",
        owner="workflow",
        schema=VSCODE_ENVIRONMENT_STATE_SCHEMA,
    )
    register_context(
        repo_root,
        base,
        work_id=args.work_id,
        context_type="runtime-context",
        path=runtime_context_path,
        required=True,
        generated_by="vscode-environment",
        owner="workflow",
        schema=RUNTIME_CONTEXT_SCHEMA,
    )
    return {
        "work_dir": relative_to_repo(repo_root, base),
        "state_path": relative_to_repo(repo_root, state_path),
        "runtime_context_path": relative_to_repo(repo_root, runtime_context_path),
        "knowledge_source_backup": runtime_context["knowledge_source_backup"],
        **state,
    }


def draft_template_text() -> str:
    return """# VSCode Environment Custom Design Draft

この draft は `/vscode-environment` の custom-design mode 向けの任意入力です。引数なしの self-provision mode では current repository の repo evidence を読むため、記入済み draft は必須ではありません。

## 目的
- TODO: この workspace で何を再現可能にしたいか

## Mode

- TODO: self-provision / target-workspace / custom-design

## 対象 Workspace

- TODO: self-provision なら current repository。target-workspace / custom-design なら例 `C:\\github\\localty-system-gui`

## 起動したい AI Workflow

- TODO: 例 `/corrective-action-fix`, `/realtime-iac`, `/vscode-environment`

## 必要 Tool / Runtime

- Git:
- Docker Desktop:
- Python / uv:
- Node.js:
- Java:
- MSYS2:
- Repo-local command tools:
  - TODO: 例 `${workspaceFolder}\\runtime\\windows-script` を `terminal.integrated.env.windows.Path` に追加するか
- その他:

## 必要 VSCode 拡張

- TODO: extension ID または拡張名

## Terminal 構成

- Dispatcher:
- Software Workflow:
- IaC Workflow:
- Docker Test:
- Evidence:

## VSCode Task 案
- TODO: task label と実行コマンド

## Debug / Launch 案
- TODO: launch name と対象 program

## 試走したい内容

- TODO: task実行、terminal起動、Docker連携、Python実行、AI workflow起動など

## Evidence

- TODO: 保存したいログ、スクリーンショット、human check

## 未確定
- TODO
"""


def write_draft_template(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from(args)
    draft_dir = (repo_root / args.draft_dir).resolve()
    draft_dir.mkdir(parents=True, exist_ok=True)
    path = draft_dir / DEFAULT_DRAFT_SCAFFOLD
    created = False
    if not path.exists():
        path.write_text(draft_template_text(), encoding="utf-8")
        created = True
    return {"draft_path": relative_to_repo(repo_root, path), "created": created}


def discover_drafts(draft_dir: Path) -> list[Path]:
    if not draft_dir.exists():
        return []
    return sorted(
        path
        for path in draft_dir.iterdir()
        if path.is_file()
        and (
            (path.name.lower().startswith("readme_") and path.suffix.lower() in {".md", ".markdown"})
            or path.suffix.lower() == ".txt"
        )
    )


def open_questions_text(work_id: str, draft_dir: str, draft_paths: list[str]) -> str:
    draft_list = "\n".join(f"- `{path}`" for path in draft_paths) if draft_paths else "- なし"
    scaffold_path = f"{draft_dir}/{DEFAULT_DRAFT_SCAFFOLD}".replace("\\", "/")
    return f"""# 未解決事項: VSCode Environment

- workflow: `vscode-environment`
- work_id: `{work_id}`
- status: `blocked`
- language: `ja-JP`
- draft_dir: `{draft_dir}`
- created_at: `{utc_now_iso()}`
- owner_agent: `workspace-requirements-analyst`

## 停止理由

VSCode Environment workflow は、通常は repo evidence から開始できます。引数なしの `/vscode-environment` は self-provision mode として current repository を対象にするため、記入済み draft は必須ではありません。

ただし custom-design mode で terminal、Docker、extension、launch、multi-root、personal/local-only path などの設計選択が repo evidence から安全に判断できない場合は、人間確認が必要です。`{scaffold_path}` は任意の custom-design scaffold です。記入済み draft は `README_*.md` を使います。legacy `.txt` draft がある場合も確認対象に含めます。

## Scaffold File

- `{scaffold_path}`

## 任意 Custom Design Draft File

{draft_list}

## 確認 Flow

```text
self-provision / target-workspace
  -> repo evidence inspection
  -> implement safe workspace-as-code updates
  -> validation / evidence

custom-design
  -> optional README.md scaffold
  -> optional README_*.md filled draft
  -> open-questions.md when unresolved choices remain
  -> human review / answers
  -> approval
  -> .vscode environment implementation
  -> trial run / evidence
```

## 不足している必須入力

| ID | 不足項目 | 必要な理由 | 必須回答 |
| --- | --- | --- | --- |
| VSCODE-Q001 | target workspace path | target-workspace / custom-design mode では具体的な target directory が必要です。self-provision mode なら current repository でよいです。 | target repository / workspace の absolute path、または self-provision 承認 |
| VSCODE-Q002 | workflow entrypoints | `tasks.json` には明示的な AI workflow command が必要です。 | 公開する slash command または task name |
| VSCODE-Q003 | required tools / runtimes | preflight と task command はこれらの tool に依存します。 | Git、Docker、Python、uv、Node.js、Java、MSYS2 など |
| VSCODE-Q004 | required VSCode extensions | `extensions.json` には extension ID 一覧が必要です。 | Extension ID list |
| VSCODE-Q005 | terminal roles | terminal profile と default shell を明示する必要があります。 | Dispatcher / Software / IaC / Docker / Evidence terminal settings |
| VSCODE-Q006 | trial run checks | 完了判断には具体的な evidence が必要です。 | Tasks、launch configs、Docker/runtime checks、human checks |

## 人間への確認事項

### VSCODE-Q001

VSCode environment files を配置する workspace / repository はどれですか。
回答:

```text

```

### VSCODE-Q002

VSCode tasks から実行可能にする AI workflow commands はどれですか。
回答:

```text

```

### VSCODE-Q003

この workspace に必要な tool と runtime はどれですか。
回答:

```text

```

### VSCODE-Q004

必須または推奨する VSCode extensions はどれですか。
回答:

```text

```

### VSCODE-Q005

作成する terminal profile と役割は何ですか。
回答:

```text

```

### VSCODE-Q006

VSCode environment が機能することを証明する trial run は何ですか。
回答:

```text

```

## 再開手順

人間の回答を追記し、承認後、確定した target で work area を初期化します。

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . workflow vscode-environment init `
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
    draft_paths = [relative_to_repo(repo_root, path) for path in discover_drafts(draft_dir)]
    path = design_document_dir_for_work_dir(base) / "open-questions.md"
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
    state_path = context_file(base, "vscode-environment-draft-state.json")
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
title: Localty VSCode 環境パターン
type: workspace-environment-pattern
project: localty
repository: {args.repository}
branch: TBD
commit: unknown
workflow: vscode-environment
phase: knowledge-capture
status: {args.status}
language: ja-JP
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

# Localty VSCode 環境パターン

## 要約

Localty repository では、VSCode 設定を Workspace as Code として扱います。通常は repo evidence から開始し、特殊な設計選択が必要な場合のみ任意 draft や `open-questions.md` で人間確認を行います。

## 範囲

- target_workspace: `{target_workspace}`
- mode: `{args.mode}`
- work_id: `{args.work_id}`
- source_rag_path: `{source_path}`
- source_type: internal project RAG

## 参照パターン

1. `/vscode-environment` に target argument がない場合は、self-provision mode として current repository を対象にする。
2. `/vscode-environment <target-workspace>` の場合は、target-workspace mode として対象 repo evidence を読む。
3. 特殊な terminal、Docker、extension、launch、multi-root、local-only path などが必要な場合は custom-design mode として扱う。
4. custom-design mode では、任意で `work/requirements/devlop-edit-draft/README.md` scaffold と `README_*.md` draft を使う。
5. repo evidence または draft から安全に判断できない事項は `work/<work-id>/design-document/open-questions.md` に整理する。
6. 人間の回答と承認を待つ。
7. 確定した target workspace で `work/<work-id>` を初期化する。
8. requirements と validation が通った後にのみ、target `.vscode` files を実装する。

## 必須 Workspace 成果物

- `.vscode/settings.json`
- `.vscode/tasks.json`
- `.vscode/launch.json`
- `.vscode/extensions.json`
- optional `.vscode/<name>.code-workspace`
- `work/<work-id>/design-document/workspace-requirements.md`
- `work/<work-id>/design-document/vscode-design.md`
- `work/<work-id>/design-document/terminal-design.md`
- `work/<work-id>/context/workspace-shared-artifact-validation.json`
- `work/<work-id>/test-evidence/workspace-test.md`

## Localty Runtime 方針

- shared protocol dependency は、`localty-system-protocol>=0.1.0` のような公開済み Python package を優先する。
- package install または import verification に失敗した場合のみ、理由を記録して support repository fallback を使う。
- MSYS2、uv、Python、Docker、VSCode の確認は preflight evidence に明示する。
- token、secret、個人専用 absolute path を commit 対象 workspace file に保存しない。

## Terminal 役割パターン

推奨する terminal role:

| Role | 目的 |
| --- | --- |
| Dispatcher | AI workflow command を実行し、artifact を調整する。 |
| Software Workflow | Python、test、lint、application command を実行する。 |
| IaC Workflow | Docker、compose、gateway、network、deployment check を実行する。 |
| Docker Test | Docker Desktop と compose validation command を分離して実行する。 |
| Evidence | log、screenshot、manual check、skipped-test note を記録する。 |

## Task パターン

VSCode task は、個人の shell 履歴ではなく、安定した workflow command を公開します。Workflow intent に対応する label を優先します。

- `workflow:vscode-open-questions`
- `workflow:vscode-preflight`
- `workflow:aiwfctl-path-shell`
- `workflow:vscode-test`
- `workflow:corrective-action-fix`
- `workflow:rag-load`
- `workflow:rag-build`

## Evidence パターン

試行証跡は次の場所へ記録します。

```text
work/<work-id>/test-evidence/
```

Evidence には、JSON 妥当性、task label、terminal profile 起動、launch configuration 確認、runtime version 確認、必要に応じた Docker 確認、AI 観察が必要な human-check 項目を含めます。

## RAG 保存ルール

Localty VSCode 環境パターンが再利用可能になった場合、Markdown source を次の場所へ保存します。

```text
{DEFAULT_RAG_SOURCE_DIR}/YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

その後、次の順序で RAG artifact を生成します。

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . rag standardize `
  --source-dir {DEFAULT_RAG_SOURCE_DIR} `
  --replace-references

uv run --project runtime python runtime/ctl/ctl.py --repo-root . rag normalize `
  --source-dir {DEFAULT_RAG_SOURCE_DIR} `
  --output-dir {GENERATED_NORMALIZED.as_posix()} `
  --document-type workspace-environment-pattern
```

## 未解決事項

- 最初の target は Localty GUI、robot、simulator、protocol、multi-root workspace のどれか。
- 各 repository の default terminal profile はどれか。
- 必須 task と推奨 task をどう分けるか。
- VSCode UI 状態を CLI だけで証明できず、人間観察が必要な check はどれか。
"""


def write_rag_template(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from(args)
    base = work_dir(repo_root, args.work_id)
    ensure_work_dirs(base)
    source_dir = (repo_root / args.source_dir).resolve()
    try:
        source_dir.relative_to(repo_root.resolve())
    except ValueError:
        raise ValueError(f"RAG source directory must be inside repo root: {source_dir}")
    source_dir.mkdir(parents=True, exist_ok=True)
    path = source_dir / rag_filename(args.topic)
    source_path = relative_to_repo(repo_root, path)
    path.write_text(rag_template_text(args, source_path), encoding="utf-8")
    work_cleanup_hint.register_long_lived_artifact(
        repo_root,
        base,
        work_id=args.work_id,
        workflow_name="vscode-environment",
        artifact_id="VSCODE-ENVIRONMENT-RAG-SOURCE",
        title="VSCode Environment RAG Source",
        path=path,
        artifact_type="rag-source",
        status=args.status,
        owner_agent="vscode-environment",
        summary="Reusable VSCode workspace environment knowledge source.",
    )
    work_cleanup = work_cleanup_hint.record(repo_root, base, args.work_id)
    return {
        "path": source_path,
        "document_type": "workspace-environment-pattern",
        "work_id": args.work_id,
        "work_cleanup": work_cleanup,
        "next_action": work_cleanup_hint.next_action(
            work_cleanup,
            reason="Approved VSCode environment Knowledge output is available in the long-lived knowledge area.",
        ),
    }


def requirements_text(work_id: str, mode: str) -> str:
    return f"""# Workspace 要件

- workflow: `vscode-environment`
- work_id: `{work_id}`
- mode: `{mode}`
- status: `draft`
- language: `ja-JP`

## 意図

TODO: この VSCode workspace が必要な理由と、支援する AI / human workflow を記載する。

## 対象 Workspace

- path: TODO
- repository: TODO
- branch: TODO

## Mode 別方針

- self-provision: 引数なし。current repository を対象にし、記入済み草案は不要。
- target-workspace: 指定 path の repository を対象にし、repo evidence から安全な既定値を推定する。
- custom-design: 特殊な terminal、Docker、extension、launch、multi-root、local-only path などを任意 draft または human question で補う。

## 必要 Tool

| Tool | 必須 | Version 方針 | Install / Check Command | Notes |
| --- | --- | --- | --- | --- |
| Git | yes | TODO | `git --version` | TODO |
| Docker Desktop | TODO | TODO | `docker version` | TODO |
| Python | TODO | TODO | `python --version` or `uv run --project runtime python --version` | TODO |
| Node.js | TODO | TODO | `node --version` | TODO |
| Java | TODO | TODO | `java --version` | TODO |

## 必要 VSCode Extension

| Extension ID | 必須 | 理由 |
| --- | --- | --- |
| TODO | yes | TODO |

## Terminal Profile

| Role | Profile 名 | Shell | Working Directory | Startup Command |
| --- | --- | --- | --- | --- |
| Dispatcher | TODO | TODO | TODO | TODO |
| Software Workflow | TODO | TODO | TODO | TODO |
| IaC Workflow | TODO | TODO | TODO | TODO |
| Docker Test | TODO | TODO | TODO | TODO |
| Evidence | TODO | TODO | TODO | TODO |

## Terminal Environment

Repo-local command tools がある場合、VSCode integrated terminal の PATH へ追加する。

```json
{{
  "terminal.integrated.env.windows": {{
    "Path": "${{workspaceFolder}}\\runtime\\windows-script;${{env:Path}}",
    "PYTHONUTF8": "1",
    "PYTHONIOENCODING": "utf-8",
    "AIWF_TEXT_ENCODING": "utf-8"
  }}
}}
```

## UTF-8 First / Mojibake Prevention

VSCode 初期構築時点で、この workspace を UTF-8 として扱う前提を明示する。日本語 Markdown、prompt、JSON、workflow docs を含む場合、文字コードの自動推測に頼らない。

`.vscode/settings.json` に必ず含める:

```json
{{
  "files.encoding": "utf8",
  "files.autoGuessEncoding": false,
  "files.eol": "\\n",
  "terminal.integrated.env.windows": {{
    "PYTHONUTF8": "1",
    "PYTHONIOENCODING": "utf-8",
    "AIWF_TEXT_ENCODING": "utf-8"
  }}
}}
```

PowerShell terminal profile の起動時に必ず含める:

```powershell
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
chcp 65001 > $null
```

`.editorconfig` に必ず含める:

```ini
[*]
charset = utf-8
end_of_line = lf

[*.{{bat,cmd}}]
charset = unset
end_of_line = crlf
```

Codex の `config.toml` は Codex が読む設定だけに使う。UTF-8 を強制するために独自の `[encoding]` table を追加しても、Codex 標準設定として解釈される前提にはしない。

Codex 向けに UTF-8 方針を永続化したい場合は、`AGENTS.md` や workflow docs へ「この repository は UTF-8 First で扱う」と書き、機械チェックは `.vscode/settings.json`、`.editorconfig`、PowerShell profile、`aiwfctl doctor --fail-on-warning` で行う。

## Tasks

| Label | Command | Depends On | Evidence |
| --- | --- | --- | --- |
| workflow:aiwfctl-path-shell | `runtime/windows-script/register-aiwfctl-path.cmd --shell` | repo-local tools | `Get-Command aiwfctl`, `aiwfctl help list` |
| TODO | TODO | TODO | TODO |

## Debug / Launch Target

| Name | Runtime | Program | 前提条件 |
| --- | --- | --- | --- |
| TODO | TODO | TODO | TODO |

## AI Workflow 入口

| Task Label | Workflow | Command | Evidence |
| --- | --- | --- | --- |
| TODO | TODO | TODO | TODO |

## Docker / Runtime 連携

TODO: Docker Desktop、compose file、公開 port、health check、log を記載する。

## Evidence Workflow

TODO: test evidence、screenshot、log、human check の保存先を記載する。

## 個人値と Placeholder

TODO: placeholder のまま残すべき path、secret、token、machine 名、device を列挙する。

## 未解決事項
- TODO
"""


def write_requirements_template(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from(args)
    base = work_dir(repo_root, args.work_id)
    ensure_work_dirs(base)
    path = design_document_dir_for_work_dir(base) / "workspace-requirements.md"
    if not path.exists():
        path.write_text(requirements_text(args.work_id, args.mode), encoding="utf-8")
    return {"path": relative_to_repo(repo_root, path), "created": True}


def validation_markdown(data: dict[str, Any]) -> str:
    missing = data.get("missing_required_items", [])
    questions = data.get("open_questions", [])
    lines = [
        "# Workspace共有Artifact検証",
        "",
        f"- status: `{data['status']}`",
        f"- created_at: `{data['created_at']}`",
        "- language: `ja-JP`",
        "",
        "## 不足している必須項目",
        "",
    ]
    lines.extend([f"- {item}" for item in missing] or ["- なし"])
    lines.extend(["", "## 未解決事項", ""])
    lines.extend([f"- {item}" for item in questions] or ["- なし"])
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
        "mode": args.mode,
        "created_at": utc_now_iso(),
        "status": args.status,
        "missing_required_items": [
            "必須tool一覧",
            "必須VSCode extension一覧",
            "terminal profile 構成",
            "UTF-8 First 設定 (.vscode/settings.json、.editorconfig、PowerShell profile、Codex 向け方針の AGENTS.md/docs 記載)",
            "AI workflow 入口 task 一覧",
        ],
        "conditions": [],
        "open_questions": [
            "どの target workspace へ .vscode files を配置するか。",
            "VSCode から利用可能にする必須 task はどれか。",
            "Shift_JIS / CP932 を保持する必要があるファイル種別はあるか。",
        ],
        "evidence": [],
    }
    json_path = context_file(base, "workspace-shared-artifact-validation.json")
    md_path = process_report_dir_for_work_dir(base) / "workspace-shared-artifact-validation.md"
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
