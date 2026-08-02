# Knowledge Capture

完了したIssue作業から、PR材料、docs evidence確認、RAG候補、docs候補、report-only close archive準備を作るworkflowです。

## Command

```text
/knowledge-capture --issue issue-11 --repository target-system --branch feature/issue-11
```

最小指定:

```text
/knowledge-capture issue-11
```

## Input

```text
work/<issue-id>/
```

必要なsource artifacts:

```text
work/<issue-id>/process-report/
work/<issue-id>/test-specifications/
work/<issue-id>/test-evidence/
```

target repository docs側の永続証跡:

```text
work/<issue-id>/source/repository/docs/evidence/<issue-id>/test_specifications/
work/<issue-id>/source/repository/docs/evidence/<issue-id>/test_specifications/unit-test-cases.md
work/<issue-id>/source/repository/docs/evidence/<issue-id>/test_specifications/integration-test-cases.md
work/<issue-id>/source/repository/docs/evidence/<issue-id>/test_specifications/human-check-list.md
work/<issue-id>/source/repository/docs/evidence/<issue-id>/ut/
work/<issue-id>/source/repository/docs/evidence/<issue-id>/integration/
work/<issue-id>/source/repository/docs/evidence/<issue-id>/human_check/
```

`aiwfctl workflow knowledge-capture` は、存在しない証跡フォルダとscaffold用 `README.md` を自動生成します。ただし、`README.md` だけでは実エビデンスとはみなしません。

## Flow

1. knowledge capture packageを生成する。
2. target repository docs配下にtest evidenceが置かれているか確認する。
3. push gateを確認する。
4. Issue branch push後、`develop` へのPull Request gateを確認する。
5. RAG candidateを抽出する。
6. docs candidateを抽出する。
7. report-only close archive readinessを確認する。
8. base work resetの準備をする。

## Output

```text
work/<issue-id>/process-report/pull-request-title.md
work/<issue-id>/process-report/pull-request-description.md
work/<issue-id>/process-report/merge-comment.md
work/<issue-id>/process-report/knowledge-capture-report.md
work/<issue-id>/process-report/knowledge-capture-*.json
```

`pull-request-title.md` は、利用可能なGitHub Issue recordのtitleを使います。
`pull-request-description.md` には、Issueからbranch、test evidence、push、Pull Request、`develop` までのMermaid式sequence diagramを含めます。

## Context First

`/knowledge-capture` は、作業完了時の回収処理として `context-manifest.json` を優先して読みます。

- `scm-state`: manifestに存在する場合はmanifest経由で読みます。古い作業領域では `context/scm-state.json` へfallbackします。
- `knowledge-capture`: 生成した回収結果をmanifestへ登録し、後続のclose archive / RAG候補抽出が参照できるようにします。
- `context_resolution`: `scm-state` をmanifestで読んだかfallbackで読んだかを出力JSONへ記録します。

これにより、Context First導入前の既存workも壊さず、導入後のworkではmanifestを第一入力として扱えます。

active workでは、manifest上の `scm-state` を必須にします。
`work/close/...` のclose archiveは、古い成果物を読めるようにfallbackを継続します。
旧workを明示的に読む場合は `--allow-legacy-scm-fallback` を付けます。

## Pull Request

Issue branch push後に、`develop` へPull Requestを送信します。

```powershell
.\runtime\windows-script\aiwf.cmd ctl github pr `
  --work-id "<issue-id>" `
  --base develop `
  --create `
  --human-check approved
```

## Report-only Close Archive

承認後、次を実行します。

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . close-archive prepare --issue "<issue-id>" --require-rag
uv run --project runtime python runtime/ctl/ctl.py --repo-root . close-archive audit --issue "<issue-id>"
```

`prepare` はRAG sourceを自動検出し、吸収済みの具体内容をclose reportへ反映します。RAG sourceが自動検出できない、または重要なRAG sourceを必ず含めたい場合は、次のように明示します。

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . close-archive prepare `
  --issue "<issue-id>" `
  --source-rag "work/db/ariadne-knowledge-platform/rag/normalized/<rag-source>.json" `
  --require-rag
```

不要なsource checkoutやcacheを削除する場合は、dry-runを確認してから承認付きで実行します。

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . close-archive prune --issue "<issue-id>"
uv run --project runtime python runtime/ctl/ctl.py --repo-root . close-archive prune `
  --issue "<issue-id>" `
  --execute `
  --human-check approved
```

`work/close` はsource checkoutではなく、次のreport-only構成を目標にします。

```text
work/close/improvement/<issue-id>/
  00-summary.md
  01-work-report.md
  02-test-report.md
  03-review-report.md
  04-human-check.md
  05-retrospective.md
  links.md
  metadata.json
```

## Guardrails

- 実装codeを変更しません。
- designを変更しません。
- push、Pull Request作成、RAG登録、close archive作成、archive pruning、base work削除は人間承認後に行います。
- `work/close` はsource checkoutではなく、report-only archiveとして扱います。
- evidenceを削除しません。
- テスト成果物の保存先は [Test Artifact Storage](../reference/test-artifact-storage.md) に従います。

## Source Skill

```text
skills/knowledge-capture/SKILL.md
```
