# Workflow Dispatch

Workflow dispatchは、要求されたgoalを、実行に必要な最小限のcontextとruntime支援へ接続します。

## Dispatch入力

- user intentまたはslash-style command。
- repositoryとbranch context。
- 既存work artifact。
- 関連するschema、template、prompt、agent定義。
- Human Gate要件。

## Dispatch出力

- 選択されたworkflowまたはruntime command。
- workflowが永続contextを必要とする場合の `work/<work-id>/context/` 配下のcontext directory。
- artifact pathとcompletion criteria。
- reviewまたはhandoff指示。

## Review境界

Dispatchは、reviewerまたはspecialist agentに必要なcontextだけを渡します。review結果はartifactとして戻し、comparison report、Human Gate判断、follow-up issueの材料にできるようにします。
