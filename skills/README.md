# Workflow Skills

このディレクトリは、Localty robotics workflow を開始するための Skill entrypoint を格納します。

## Skills

| Slash Command | Skill | Delegated Prompt | Purpose |
| --- | --- | --- | --- |
| `/robotics-new-system` | `robotics-new-system/` | `/new-robotics-system-development` | 新しい robotics system を立ち上げる |
| `/robotics-feature-maintenance` | `robotics-feature-maintenance/` | `/robotics-maintenance-development` | 既存 robotics system の新機能追加または保守開発を行う |
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

どちらの Skill も、開発本体に入る前に `runtime/intake/intake_requirements.py` と `/pre-development-preparation` を通します。

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
C:\Users\User\.codex\skills\robotics-new-system
  -> C:\github\intent-driven-robotics-ai-workflow\skills\robotics-new-system

C:\Users\User\.codex\skills\robotics-feature-maintenance
  -> C:\github\intent-driven-robotics-ai-workflow\skills\robotics-feature-maintenance

C:\Users\User\.codex\skills\corrective-action-report
  -> C:\github\intent-driven-robotics-ai-workflow\skills\corrective-action-report

C:\Users\User\.codex\skills\corrective-action-fix
  -> C:\github\intent-driven-robotics-ai-workflow\skills\corrective-action-fix

C:\Users\User\.codex\skills\rag-build
  -> C:\github\intent-driven-robotics-ai-workflow\skills\rag-build

C:\Users\User\.codex\skills\rag-load
  -> C:\github\intent-driven-robotics-ai-workflow\skills\rag-load

C:\Users\User\.codex\skills\knowledge-capture
  -> C:\github\intent-driven-robotics-ai-workflow\skills\knowledge-capture
```

VS Code Copilot Chat の `/` 候補は `.github/prompts/*.prompt.md`、Codex Skill 候補は `C:\Users\User\.codex\skills` を主に見ます。

## Corrective Action Report Rule

`/corrective-action-report` は、開発開始ではなく read-only review と report 作成の Skill です。

開始前に、必ず対象repositoryと対象branchを user に確認します。未指定の場合は作業前に入力を求めます。

Report は以下へ保存します。

```text
C:\github\intent-driven-robotics-ai-workflow\rag\corrective-action-report
```
