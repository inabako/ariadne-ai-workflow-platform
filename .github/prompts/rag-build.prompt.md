# /rag-build

## Official Runtime Entrypoint

通常実行では `aiwfctl rag build` を使用してください。
個別moduleの直接実行は、runtime module開発または単体試験でそのmodule自体を検証する場合に限定します。

```powershell
.\runtime\windows-script\aiwf.cmd ctl rag build `
  --work-id "<work-id>" `
  --source-dir work/db/ariadne-knowledge-platform/rag/corrective-action-report `
  --document-type corrective-action-report `
  --clean-output
```

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成してください。

RAG Build Skill を使って、Ariadne AI Workflow の Markdown report を file-based RAG artifact に変換してください。

既定では日本語で応答してください。

実行する既定 pipeline:

1. `aiwfctl rag normalize`
2. `aiwfctl rag chunk`
3. `aiwfctl rag optimize`
4. `aiwfctl rag index`
5. `aiwfctl rag embed`
6. 必要に応じて `aiwfctl rag jsonize`

`ingestion_optimizer.py` は、RAG吸収前のchunk候補を `ACCEPT / REWRITE / HUMAN_CHECK / REJECT` に分類し、`db/rag/evidence/ingestion` にEvidenceを保存します。通常は `ACCEPT` 済みの `work/db/ariadne-knowledge-platform/rag/optimized-chunks/*.json` だけをindex / embedding対象にしてください。

`work/db/ariadne-knowledge-platform/rag/corrective-action-report` 配下の Markdown report は、build前に `aiwfctl rag standardize --source-dir work/db/ariadne-knowledge-platform/rag/corrective-action-report --replace-references` で `YYYYMMDDHHmmSS_<random-5-to-8>_<repository-name>.md` に統一してください。標準は8桁です。

RAG artifact のファイル名は UUID にしてください。検索はファイル名ではなく JSON の `content` と metadata を対象にします。

`aiwfctl rag normalize`、`aiwfctl rag chunk`、`aiwfctl rag jsonize` は標準で `--clean-output` を使い、旧ファイル名artifactを混在させないでください。

既存 artifact は、ユーザーが明示しない限り削除しないでください。
