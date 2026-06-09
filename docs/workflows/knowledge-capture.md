# Knowledge Capture

完了したIssue作業から、PR材料、docs evidence確認、RAG候補、docs候補、archive準備を作るworkflowです。

## Command

```text
/knowledge-capture --issue issue-11 --repository localty-system-gui --branch feature/issue-11
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

`runtime/workflow/knowledge_capture.py` は、存在しない証跡フォルダとscaffold用 `README.md` を自動生成します。
ただし、`README.md` だけでは実エビデンスとはみなしません。

## Flow

1. knowledge capture packageを生成する。
2. target repository docs配下にtest evidenceが置かれているか確認する。
3. push gateを確認する。
4. Issue branch push後、`develop` へのPull Request gateを確認する。
5. RAG candidateを抽出する。
6. docs candidateを抽出する。
7. archive readinessを確認する。
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

## Pull Request

Issue branch push後に、`develop` へPull Requestを送信します。

```powershell
python runtime/github/pull_request_manager.py `
  --work-id "<issue-id>" `
  --base develop `
  --create `
  --human-check approved
```

## Guardrails

- 実装codeを変更しません。
- designを変更しません。
- push、Pull Request作成、RAG登録、archive移動、base work削除は人間承認後に行います。
- evidenceを削除しません。
- テスト成果物の保存先は [Test Artifact Storage](../reference/test-artifact-storage.md) に従います。

## Source Skill

```text
skills/knowledge-capture/SKILL.md
```
