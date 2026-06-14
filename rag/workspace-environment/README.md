# Workspace Environment RAG

このdirectoryは、Localtyおよび関連robotics AI workflowで再利用できるVSCode Workspace-as-Code knowledgeを保存します。

利用対象:

- VSCode settings、tasks、launch、extension pattern
- terminal role pattern
- runtimeとpreflightの期待値
- trial-run evidence pattern
- 再利用可能なLocalty environment decision

保存しないもの:

- secret、token、個人credential
- local-only evidenceとして明示していないprivate machine-only path
- 外部記事や外部documentationの本文そのもの
- target repository requirementsに関する未承認の推測

## Naming

RAG source area共通のMarkdown report naming styleを使います。

```text
YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md
```

例:

```text
20260612182244_K8M2Q7_localty-vscode-environment.md
```

このdirectoryには次だけを置きます。

- `README.md`
- `YYYYMMDDHHMMSS_<random-5-to-8>_<topic>.md` 形式のapproved / draft source Markdown file

sidecar JSON、normalized JSON、chunk JSON、indexes、embeddings、retrieval resultsはこのdirectoryに置きません。

## Build

このdirectoryのMarkdown fileは、人間がreviewするsource noteです。最終的なmachine-readable RAG knowledge artifactではありません。

Human approval後、approved notesをUUID名JSONへnormalizeします。

```powershell
uv run python runtime/rag/standardize_corrective_report_names.py `
  --source-dir rag/workspace-environment `
  --replace-references

uv run python runtime/rag/normalize_documents.py `
  --source-dir rag/workspace-environment `
  --output-dir rag/normalized `
  --document-type workspace-environment-pattern
```

最終着地:

```text
rag/normalized/<uuid>.json
```

normalized UUID JSONを耐久的なknowledge recordとして扱います。Chunk JSON、indexes、embeddings、retrieval results、context packsは派生artifactです。既存の非UUID Markdown / JSON / JSONL / text artifactにUUID wrapperが必要な場合のみ `rag/jsonized/<uuid>.json` を使いますが、normalized RAG documentの代替にはしません。

## Current Normalized Outputs

現在、このdirectoryのsource Markdownは次へnormalize済みです。

```text
rag/normalized/4b8bf5b6-cad2-5bbd-9721-1ac0eb8994b2.json
rag/normalized/5f5fb26e-a2c6-50a0-bafd-6b45ddaa9b44.json
```
