---
name: corrective-action-fix
description: GitHub repository / branch と任意の corrective action report を受け取り、work/<branch> に原本を取得し、report作成または読込、RAG build/load、GitHub Issue、work/issue-XXX + feature/issue-XXX、修正、単体テスト、起動/結合確認、人間チェック、push まで進めます。
argument-hint: "<target-repository> <target-branch> [report]"
agent: agent
---

# Corrective Action Fix Skill Entrypoint

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成してください。

Readable workflow additions:

- Before push, generate PR material with `runtime/workflow/knowledge_capture.py`: `pull-request-title.md`, `pull-request-description.md`, `merge-comment.md`, and `knowledge-capture-report.md`.
- Before push, confirm test specifications and evidence are stored under `work/issue-XXX/source/repository/docs/evidence/issue-XXX/test_specifications/`, `ut/`, `integration/`, and `human_check/` when required. Split test case tables into `unit-test-cases.md`, `integration-test-cases.md`, and `human-check-list.md`. `knowledge_capture.py` creates missing scaffold directories, but scaffold `README.md` files alone are not evidence.
- After docs evidence is present and human approval is recorded, push only `feature/issue-XXX`.
- For final knowledge recovery, extract RAG candidates from `work/issue-XXX/process-report`, `work/issue-XXX/test-specifications`, and `work/issue-XXX/test-evidence`.
- Before deleting `work/<base-branch>`, summarize and link `work/<base-branch>/process-report` into the report-only close archive under `work/close/improvement/issue-XXX/`.
- Do not run RAG registration/rebuild, prepare/prune the close archive, or delete source/cache under `work/close/improvement/issue-XXX` without explicit human approval.
- Do not delete `work/<base-branch>` until base process reports are summarized / linked and human approval is recorded.

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

`/corrective-action-report` で作成済みのレポートを使う場合:

```text
/corrective-action-fix localty-system-gui develop rag/corrective-action-report/260704120000_ABC12345_localty-system-gui.md
```

Flow:

1. 改善対象の repository / branch を取得する。
2. `work/<branch>/source/repository` に原本branchを格納する。
3. corrective action report が指定されていれば読み込み、未指定なら `/corrective-action-report` 相当のread-only調査で作成する。
4. `/rag-build` を実行する。
5. `/rag-load` を実行する。
6. 不明な実装領域や標準仕様確認が必要な場合は、外部Web RAGをsupporting referenceとしてdispatchする。
7. Issue scope、実装方針、test specificationが専門知識に依存する場合はSpecialist Agent reviewを実行する。
8. 修正内容、supporting reference、specialist review referenceを GitHub Issue に載せる。
9. `work/issue-XXX/source/repository` を作り、Git branch `feature/issue-XXX` を作成する。
10. `work/requirements/svg-input/FIX_*.svg`がある場合、Issue作業領域へ取り込み、GaC / UaC GUI ModeをFIX modeで実行する。
11. Next.js画面機能を含む場合、Next.js Webapp Implementation Prepを実行し、画面/API/auth/env/testを確定する。
12. `work/requirements/svg-input/WEB_FIX_*.svg`がある場合、Web SVG Layout Modeを実行し、layout / React / Playwright候補をreviewする。
13. 改善レポートと RAG context に従って修正する。
14. テスト仕様書のテストケース表に従ってユニットテストを作成・実施する。
15. PyQt / Qt GUIの場合、QTest化できる結合疎通試験をソース化して実行する。
16. 起動確認 / 結合試験を実施する。
17. 起動確認 / 結合試験について人間チェックを受ける。
18. 人間チェック承認後、`feature/issue-XXX` を push する。

GaC / UaC GUI Mode:

```powershell
python runtime/workflow/gui_mode.py run `
  --issue-id "FIX-XXX" `
  --work-dir "work/issue-XXX" `
  --mode corrective-improvement
```

SVGが無ければ`skipped`で通常flowへ戻ります。SVGがある場合、生成候補を既存GUIとの差分としてreviewし、最小変更、既存挙動維持、固定座標排除、QTest回帰防止を優先します。

Next.js Webapp Implementation Prep:

```text
.github/prompts/nextjs-webapp-implementation-prep.prompt.md
templates/process-report/nextjs-webapp-implementation-prep-template.md
```

既存Next.js appでは `nextjs-webapp-template` はreference-onlyです。画面route、user action、API contract、auth/session、env/secret境界、typecheck、lint、unit、e2e、health、UI smoke、API connectivityが未整理なら実装へ進みません。

Web SVG Layout Mode:

```text
.github/prompts/web-svg-layout-mode.prompt.md
runtime/workflow/web_svg_layout_mode.py
```

`work/requirements/svg-input/WEB_FIX_*.svg` がある場合、`work/issue-<number>/web-ui/` を生成します。React / Playwright候補は既存画面への最小修正としてreviewし、無条件コピーしません。

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
- Next.js画面機能の場合は、`nextjs-webapp-implementation-prep.md` の `Implementation may start: yes` を確認してからsourceを変更する。
- `WEB_FIX_*.svg` がある場合は、`web-ui/` のreviewとvalidateを確認してからsourceへ統合する。
