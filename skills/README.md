# Workflow Skills

このディレクトリは、Ariadne workflow を開始するための Skill entrypoint を格納します。

## Skills

| Slash Command | Skill | Delegated Prompt | Purpose |
| --- | --- | --- | --- |
| `/requirement-discovery` | `requirement-discovery/` | `/requirement-discovery` | `work/requirements/draft/` の箇条書き草案を精査し、質問と人間レビューを経て完成版要件定義書を `work/requirements/` に保存する |
| `/docs-sync` | `docs-sync/` | `/docs-sync` | 実装と `docs/` の差分をJSON化し、Issue branchでdocsのみ修正してRAG/archive準備まで行う |
| `/github-knowledge-maintenance` | `github-knowledge-maintenance/` | `/github-knowledge-maintenance` | GitHub Issue / PR / docs / CARを知識資産として保守し、承認済み同期とRAG候補生成を行う |
| `/vscode-environment` | `vscode-environment/` | `/vscode-environment` | VSCode workspace as code、tasks、launch、extensions、terminal、AI workflow entrypoints、evidenceを整備する |
| `/ariadne-new-system` | `ariadne-new-system/` | `/ariadne-new-system-development` | 新しい対象システムを立ち上げる |
| `/ariadne-new-system-iac` | `ariadne-new-system-iac/` | `/ariadne-new-system-iac` | 新システム設計、Shared Artifacts生成・検証、realtime IaC連携を一気通貫で行う |
| `/ariadne-feature-maintenance` | `ariadne-feature-maintenance/` | `/ariadne-feature-maintenance-development` | 既存対象システムの新機能追加または保守開発を行う |
| `/realtime-iac` | `realtime-iac/` | `/realtime-iac` | リアルタイムシステム向けIaCを設計、生成、レビュー、検証、文書化する |
| `/corrective-action-report` | `corrective-action-report/` | `/corrective-action-report` | 指定repository / branchの改善点をreport化する |
| `/rag-build` | `rag-build/` | `/rag-build` | Markdown report を file-based RAG 用に normalize / chunk / index / embedding 化する |
| `/rag-load` | `rag-load/` | `/rag-load` | 開発前に file-based RAG を並列検索し、圧縮済み context を読み込む |

Additional skill:

Additional knowledge-capture skill:

| Slash Command | Skill | Delegated Prompt | Purpose |
| --- | --- | --- | --- |
| `/knowledge-capture` | `knowledge-capture/` | `/knowledge-capture` | completed issue workflow のPR資料、証跡整理、RAG/docs候補、archive準備 |

| Slash Command | Skill | Delegated Prompt | Purpose |
| --- | --- | --- | --- |
| `/corrective-action-fix` | `corrective-action-fix/` | `/corrective-action-fix` | GitHub repository / branchをwork/<branch>へ取得し、work/issue-XXXで修正/pushする |

## Intake Rule

開発系 Skill は、開発本体に入る前に `runtime/intake/intake_requirements.py` と `/pre-development-preparation` を通します。

`work/requirements/` に完成版の要件定義書が1件だけある状態が必要です。

以下の場合は harness で受領拒否します。

- 要件定義書が無い
- 要件定義書が2件以上ある
- 要件定義書から `Repository Control` が読み取れない

会話ログだけを根拠に intake 済みとして扱ってはいけません。

## Codex Discovery

この `skills/` ディレクトリは workflow repository 側の source of truth です。

Codex の Skill 候補として表示するには、`C:\Users\User\.codex\skills` から参照できる必要があります。

現在は以下の junction を使います。

```text
C:\Users\User\.codex\skills\requirement-discovery
  -> C:\github\ariadne-ai-workflow-platform\skills\requirement-discovery

C:\Users\User\.codex\skills\docs-sync
  -> C:\github\ariadne-ai-workflow-platform\skills\docs-sync

C:\Users\User\.codex\skills\github-knowledge-maintenance
  -> C:\github\ariadne-ai-workflow-platform\skills\github-knowledge-maintenance

C:\Users\User\.codex\skills\vscode-environment
  -> C:\github\ariadne-ai-workflow-platform\skills\vscode-environment

C:\Users\User\.codex\skills\ariadne-new-system
  -> C:\github\ariadne-ai-workflow-platform\skills\ariadne-new-system

C:\Users\User\.codex\skills\ariadne-new-system-iac
  -> C:\github\ariadne-ai-workflow-platform\skills\ariadne-new-system-iac

C:\Users\User\.codex\skills\ariadne-feature-maintenance
  -> C:\github\ariadne-ai-workflow-platform\skills\ariadne-feature-maintenance

C:\Users\User\.codex\skills\realtime-iac
  -> C:\github\ariadne-ai-workflow-platform\skills\realtime-iac

C:\Users\User\.codex\skills\corrective-action-report
  -> C:\github\ariadne-ai-workflow-platform\skills\corrective-action-report

C:\Users\User\.codex\skills\corrective-action-fix
  -> C:\github\ariadne-ai-workflow-platform\skills\corrective-action-fix

C:\Users\User\.codex\skills\rag-build
  -> C:\github\ariadne-ai-workflow-platform\skills\rag-build

C:\Users\User\.codex\skills\rag-load
  -> C:\github\ariadne-ai-workflow-platform\skills\rag-load

C:\Users\User\.codex\skills\knowledge-capture
  -> C:\github\ariadne-ai-workflow-platform\skills\knowledge-capture
```

`.ariadne/` は Ariadne AI workflow assets の source of truth です。
Codex の repository guidance は `AGENTS.md` を入口にし、Codex Skill 候補は `C:\Users\User\.codex\skills` を主に見ます。
VS Code Copilot Chat の常時参照は `.github/copilot-instructions.md`、`/` prompt候補は `.github/prompts/*.prompt.md` の薄いbridgeから `.ariadne/prompts/` を参照します。

## Corrective Action Report Rule

`/corrective-action-report` は、開発開始ではなく read-only review と report 作成の Skill です。

開始前に、必ず対象repositoryと対象branchを user に確認します。未指定の場合は作業前に入力を求めます。

Report は以下へ保存します。

```text
C:\github\ariadne-ai-workflow-platform\work\db\ariadne-knowledge-platform\rag\corrective-action-report
```
