---
name: corrective-action-fix
description: GitHub repository / branch を受け取り、work/<branch> に原本を取得し、corrective action report、RAG build/load、GitHub Issue、work/issue-XXX + feature/issue-XXX、修正、単体テスト、起動/結合確認、人間チェック、push まで進めます。
argument-hint: "<target-repository> <target-branch>"
agent: agent
---

# Corrective Action Fix Skill Entrypoint

Readable workflow additions:

- Before push, generate PR material with `runtime/workflow/knowledge_capture.py`: `pull-request-title.md`, `pull-request-description.md`, `merge-comment.md`, and `knowledge-capture-report.md`.
- Before push, confirm test specifications and evidence are stored under `work/issue-XXX/source/repository/docs/evidence/issue-XXX/test_specifications/`, `ut/`, `integration/`, and `human_check/` when required. Split test case tables into `unit-test-cases.md`, `integration-test-cases.md`, and `human-check-list.md`. `knowledge_capture.py` creates missing scaffold directories, but scaffold `README.md` files alone are not evidence.
- After docs evidence is present and human approval is recorded, push only `feature/issue-XXX`.
- For final knowledge recovery, extract RAG candidates from `work/issue-XXX/process-report`, `work/issue-XXX/test-specifications`, and `work/issue-XXX/test-evidence`.
- Before deleting `work/<base-branch>`, preserve `work/<base-branch>/process-report` under `work/close/issue-XXX/process-report/base-work-<base-branch>` and verify the copy.
- Do not run RAG registration/rebuild or move `work/issue-XXX` to `work/close/issue-XXX` without explicit human approval.
- Do not delete `work/<base-branch>` until base process reports are preserved and human approval is recorded.

Use:

```text
skills/corrective-action-fix/SKILL.md
```

想定例:

```text
/corrective-action-fix [inabako/localty-system-gui.git](https://github.com/inabako/localty-system-gui.git) develop
```

`.env` に `GITHUB_OWNER=inabako` がある場合:

```text
/corrective-action-fix localty-system-gui develop
```

Flow:

1. 改善対象の repository / branch を取得する。
2. `work/<branch>/source/repository` に原本branchを格納する。
3. corrective action report を作成する。
4. `/rag-build` を実行する。
5. `/rag-load` を実行する。
6. 不明な実装領域や標準仕様確認が必要な場合は、外部Web RAGをsupporting referenceとしてdispatchする。
7. Issue scope、実装方針、test specificationが専門知識に依存する場合はSpecialist Agent reviewを実行する。
8. 修正内容、supporting reference、specialist review referenceを GitHub Issue に載せる。
9. `work/issue-XXX/source/repository` を作り、Git branch `feature/issue-XXX` を作成する。
10. 改善レポートと RAG context に従って修正する。
11. テスト仕様書のテストケース表に従ってユニットテストを作成・実施する。
12. PyQt / Qt GUIの場合、QTest化できる結合疎通試験をソース化して実行する。
13. 起動確認 / 結合試験を実施する。
14. 起動確認 / 結合試験について人間チェックを受ける。
15. 人間チェック承認後、`feature/issue-XXX` を push する。

Guardrail:

- `work/issue-XXX` はフォルダ名、`feature/issue-XXX` は Git branch 名として扱う。
- `work/<branch>` または `work/issue-XXX` が既に存在する場合は止めて、既存フォルダを確認するよう user に伝える。
- 既存フォルダを再利用する場合は、確認後に `--reuse-existing` を指定する。
- 人間チェックが承認されるまで push しない。
- `intent-driven-robotics-ai-workflow` はworkflow/RAG/report置き場であり、このflowのpush対象にしない。
- push対象は、step 1で指定されたrepositoryの `work/issue-XXX/source/repository` と `feature/issue-XXX` のみ。
- target branch へ直接実装しない。
- RAG build/load を省略しない。
- 外部Web RAGはsupporting referenceであり、current source code、test evidence、human-approved findingを上書きしない。
- Specialist Agent reviewを使った場合は、採用した外部Web RAG、採用しなかったclaim、repository evidence、required tests、human-check itemを `work/<branch>/process-report/` または `work/issue-XXX/process-report/` に残す。
- PyQt / Qt GUIの場合は、承認済みテストケース表からQTest化できる結合疎通試験を選別し、`src/tests/qt/test_<feature>_integration.py` などにソース化する。
- QTestで実UDP、GStreamer、RobotController、hardware serviceを起動する場合は、テストケース表に明示し、通常はstub / disable方針を優先する。
