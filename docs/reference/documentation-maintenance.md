# Documentation Maintenance

この文書は、Ariadne の実装、runtime、workflow、schema、template、GitHub運用、RAG運用を変更したときに、どのdocsを一緒に確認するかをまとめる運用ガイドです。

docs更新は「手順を追記する作業」だけではありません。後続Agentと人間が、なぜその変更が必要で、どの入口から使い、どのevidenceで確認したかを再開できるようにするためのartifact更新です。

## 基本ルール

- 変更した機能の入口docsを更新する。
- 実行手順、責務境界、artifact配置、Human Gate、検証方法のどれが変わったかを確認する。
- Runtime behaviorが変わる場合は、Runtime docsとpytest UT仕様書を同期する。
- workflowや運用判断が変わる場合は、Development Notesへ意図と検証を残す。
- docsだけを変える場合も、古いversion固定表現、公開前だけの表現、local absolute path、英語主体の本文が残っていないか確認する。

## 変更種別ごとの確認先

| 変更内容 | 一緒に確認するdocs / artifact |
| --- | --- |
| `aiwfctl` command、runtime CLI、wrapperを変更した | `docs/reference/runtime.md`、`docs/runtime/runtime-observability.md`、`docs/reference/runtime-pytest-ut/` |
| Runtime event log、trace、metrics、Feedback連携を変更した | `docs/runtime/runtime-observability.md`、`docs/reference/workflow-feedback.md`、`logs/README.md`、`logs/test/README.md` |
| workflow prompt、Skill、Agent promptを変更した | `docs/workflows/README.md`、該当 `docs/workflows/*.md`、`docs/reference/agent-inventory.md`、`.agents/skills/skill-index.json` |
| `.ariadne/` のschema、agent、prompt、shared ruleを変更した | `docs/reference/data-model.md`、`docs/reference/repository-structure.md`、該当workflow docs |
| `templates/registries`、`db/registries`、help registryを変更した | `docs/reference/workflow-help.md`、`docs/reference/repository-structure.md`、`runtime/tests/test_ctl_help.py`、UT仕様書 |
| RAG source、RAG build/load、DuckDB read modelを変更した | `docs/reference/rag.md`、`docs/workflows/rag-build-load.md`、`docs/rag/README.md`、`docs/rag/duckdb-read-model.md`、`docs/rag/knowledge-quality-metrics.md` |
| Review Council Runtimeを変更した | `docs/reference/review-council-runtime.md`、`docs/reference/agent-inventory.md`、`docs/reference/runtime-pytest-ut/cases/test_review_council_runtime.md` |
| Expectation-Driven Design Flowを変更した | design runtime docs、Expectation関連UT仕様書、Development Notes |
| GitHub Issue / PR template、Actions、security、license運用を変更した | `docs/README.md`、`docs/legal/README.md`、`docs/release/`、`docs/security/`、`.github/` 配下の該当ファイル |
| governance、責務境界、Human Gateを変更した | `docs/governance/`、`docs/architecture/human-gate.md`、`docs/reference/human-gates.md` |
| test caseを追加、削除、renameした | `docs/reference/runtime-pytest-ut/`、`docs/reference/runtime-pytest-ut/test-items.md`、`tools spec-check` 結果 |
| release note、version plan、長めの運用改善を行った | `docs/development-notes/<version>.md`、`docs/development-notes/README.md` |

## Runtime pytest UT仕様書

Runtime pytestを変更した場合、pytest node id とUT仕様書の同期を確認します。

```powershell
.\runtime\windows-script\uv.cmd run --project runtime --group dev python runtime\ctl\ctl.py --repo-root . tools spec-check
```

期待する状態:

```text
status = ok
pytest_count = spec_count
missing_in_spec = []
stale_in_spec = []
order_matches = true
```

新しいcase scaffoldを自動生成した場合でも、生成直後の定型文をそのまま残さず、`確認内容`、`入力値`、`期待結果` が人間に伝わる粒度になっているか確認します。

## 表現チェック

docs更新後は、必要に応じて次を検索します。

```powershell
rg -n "TODO|TBD|FIXME|\?\?\?|C:\\\\github\\\\v0\\.0\\.|公開前|v0\\.0\\.2 では" docs -g "*.md"
```

検索結果の扱い:

- `TODO` は、理由、対応条件、関連Issueがある場合だけ残す。
- `公開前` は、過去のローカル予行evidenceなど履歴として必要な場合だけ残す。現在のpolicy / guideでは `release前`、`release時`、`継続運用` を使う。
- local absolute pathは、例示として必要な場合を除き、repo-relative pathまたは `<repo-root>` 表現へ寄せる。
- version固定表現は、Development Notesやrelease note以外では避ける。

## Development Notes

次のどれかに当てはまる変更は、Development Notesへ残します。

- workflowの進め方が変わった。
- Runtimeの復帰、観測、ログ、evidenceの読み方が変わった。
- GitHub / release / legal / security の運用判断が変わった。
- RAG、registry、templateなど、fresh checkoutや後続Agentの起動性に影響する変更をした。
- 将来のIssueやPR説明に再利用したい判断理由がある。

Development Notesはrelease noteではなく、後続Agentと人間が判断を再開するための運用記録です。

## 完了確認

docs maintenanceの完了条件は、変更規模に応じて次を確認します。

- 変更した機能の入口docsが更新されている。
- 参照先リンクが切れていない。
- Runtime pytest変更がある場合、`tools spec-check` がpassしている。
- 運用判断が変わる場合、Development Notesに意図と検証が残っている。
- Evidence、log、RAG、registryなどの生成物とsource of truthの境界が説明されている。
