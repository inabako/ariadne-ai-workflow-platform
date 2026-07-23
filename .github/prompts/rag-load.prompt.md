# /rag-load

## Official Runtime Entrypoint

通常実行では `aiwfctl rag load` を使用してください。
単発debug検索だけが必要な場合は `aiwfctl rag retrieve` を使用します。
個別moduleの直接実行は、runtime module開発または単体試験でそのmodule自体を検証する場合に限定します。

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag load `
  --task "<development task>" `
  --repository "<target-repository>" `
  --branch "<target-branch>" `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000 `
  --jobs 4
```

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成してください。

RAG Load Skill を使って、開発フローに入る前に file-based RAG から関連知識を読み込んでください。

既定では日本語で応答してください。

方針:

1. task context、対象 repository、branch、要件、Issue、比較レポートから 3〜5 個の検索クエリを作る。
2. `aiwfctl rag load` を実行する。
3. dispatcher が `aiwfctl rag retrieve` をクエリごとに並列実行する。
4. RAG 圧縮は `aiwfctl rag retrieve` の既存 context pack 生成を使う。
5. 生成された `artifact_type: rag-load-dispatch` の `work/db/ariadne-knowledge-platform/rag/retrieval/<uuid>.json` と、参照先の `artifact_type: rag-context-pack` の `work/db/ariadne-knowledge-platform/rag/retrieval/<uuid>.json` を読み、開発前の前提知識として要約する。

検索はファイル名ではなく JSON の `content` と metadata を対象にしてください。RAG artifact のファイル名は UUID です。

RAG index または embedding が存在しない場合は、先に `/rag-build` を実行してください。
