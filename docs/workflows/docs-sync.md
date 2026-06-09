# Docs Sync

実装と `docs/` のズレを検出し、Issue化して、docsだけを修正するworkflowです。

## Command

```text
/docs-sync <target-repository> <target-branch>
```

例:

```text
/docs-sync localty-system-gui develop
```

## Directory Model

```text
work/<target-branch>/source/repository
work/issue-<issue-number>/source/repository
```

Git branch は次の形式にします。

```text
feature/issue-<issue-number>
```

## Flow

1. `work/<target-branch>` を初期化する。
2. target branchをfetch / checkoutする。
3. implementation と docs を比較する。
4. `work/<target-branch>/context/docs-drift-analysis.json` を保存する。
5. JSONからIssue bodyを作る。
6. 人間承認後にGitHub Issueを作成する。
7. Issue branchを作成し、`work/issue-<issue-number>` にcloneする。
8. docsだけを修正する。
9. docs-only差分を確認してcommit / pushする。
10. Issue titleをPR titleとして `develop` へPull Requestを作成する。
11. RAG候補とarchive準備を確認する。

## Issue Title

docs同期は改善扱いとして、Issue titleに次のprefixを付けます。

```text
[改善フロー] <issue-title>
```

## Guardrails

- 実装codeを変更しません。
- test、script、configを変更しません。
- docs driftの根拠はcurrent implementationとcurrent docsを優先します。
- RAGは補助contextであり、current codeを上書きする根拠にはしません。
- Issue bodyはfree-form summaryではなく、`docs-drift-analysis.json` から作ります。
- Pull Request titleは対応するIssue titleを使用します。

## Source Skill

```text
skills/docs-sync/SKILL.md
```
