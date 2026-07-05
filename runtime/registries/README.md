# Runtime Registries

`tool_candidates.json` は、Context First Tool Dispatcher が参照するtool候補、mode、Human Check条件のregistryです。

このディレクトリは、runtime全体から参照される機械可読なregistry実体を置きます。

## 責任範囲

- workflow、intake、doctor、将来のruntime補助CLIから共通参照される承認ゲート、分類表、許可リストなどを置きます。
- JSON Schemaは置きません。schema定義は `.github/schemas/` に置きます。
- RAG蓄積物は置きません。RAGは `rag/` 配下で扱います。
- 作業中/close済み成果物は置きません。作業成果物は `work/` 配下で扱います。

## 現在のregistry

| File | 用途 |
| --- | --- |
| `human_gates.json` | 人間承認が必要なruntime操作のregistry |
| `workflow_help.json` | `aiwfctl help` で表示・検索するAI workflow prompt commandのregistry |
| `workflow_environment_profiles.json` | `aiwfctl env` で参照する利用者向けEnvironmentと内部Backend profileのregistry |
