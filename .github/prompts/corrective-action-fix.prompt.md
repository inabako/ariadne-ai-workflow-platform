---
name: corrective-action-fix
description: GitHub repository / branch を受け取り、work/<branch> に原本を取得し、corrective action report、RAG build/load、GitHub Issue、work/issue-XXX + feature/issue-XXX、修正、単体テスト、起動/結合確認、人間チェック、push まで進めます。
argument-hint: "<target-repository> <target-branch>"
agent: agent
---

# Corrective Action Fix Skill Entrypoint

Use:

```text
skills/corrective-action-fix/SKILL.md
```

想定例:

```text
/corrective-action-fix [inabako/localty-system-gui.git](https://github.com/inabako/localty-system-gui.git) develop
```

Flow:

1. 改善対象の repository / branch を取得する。
2. `work/<branch>/source/repository` に原本branchを格納する。
3. corrective action report を作成する。
4. `/rag-build` を実行する。
5. `/rag-load` を実行する。
6. 修正内容を GitHub Issue に載せる。
7. `work/issue-XXX/source/repository` を作り、Git branch `feature/issue-XXX` を作成する。
8. 改善レポートと RAG context に従って修正する。
9. ユニットテストを作成・実施する。
10. 起動確認 / 結合試験を実施する。
11. 起動確認 / 結合試験について人間チェックを受ける。
12. 人間チェック承認後、`feature/issue-XXX` を push する。

Guardrail:

- `work/issue-XXX` はフォルダ名、`feature/issue-XXX` は Git branch 名として扱う。
- 人間チェックが承認されるまで push しない。
- `intent-driven-robotics-ai-workflow` はworkflow/RAG/report置き場であり、このflowのpush対象にしない。
- push対象は、step 1で指定されたrepositoryの `work/issue-XXX/source/repository` と `feature/issue-XXX` のみ。
- target branch へ直接実装しない。
- RAG build/load を省略しない。
