# db/rag

`db/rag/` は、Ariadne の RAG knowledge を検索・検証しやすくするための、ローカル生成 read model と evidence の置き場です。

このディレクトリは RAG knowledge の source of truth ではありません。

長期保存する knowledge source は、標準では `work/db/ariadne-knowledge-platform/rag/` 側に置きます。`db/rag/` は、その source から再生成できる DuckDB、migration log、reference check、ingestion evidence を置くための runtime local area です。

## 役割

| 種別 | 主な場所 | Git管理 | 役割 |
| --- | --- | --- | --- |
| RAG source / JSON / JSONL | `work/db/ariadne-knowledge-platform/rag/` | knowledge repository側の方針に従う | Human Review済みknowledge、normalized document、chunk、index、embedding、retrieval artifact |
| DuckDB read model | `db/rag/ariadne-knowledge.duckdb` | しない | RAG sourceから再生成できる検索用DB |
| migration / reference check evidence | `db/rag/evidence/` | しない | DuckDB rebuild、ingestion、reference checkのローカル検証結果 |
| このREADME | `db/rag/README.md` | する | `db/rag/` の責務境界を説明する |

## 置いてよいもの

`db/rag/` に置いてよいものは、Ariadne本体で再生成できるローカル成果物だけです。

- `ariadne-knowledge.duckdb`
- `migration-errors.jsonl`
- `evidence/migration-summary.json`
- `evidence/reference-check.json`
- `evidence/ingestion/`
- `evidence/context/`

これらは runtime が生成する read model / evidence です。削除されても、knowledge source が残っていれば再生成できます。

## 置かないもの

`db/rag/` には、knowledge の正本や長期保存したい資料を置きません。

- Human Review前の作業メモ
- Human Review済みの RAG source Markdown
- semantic hints の source / backup
- normalized document JSON
- chunks / optimized-chunks / indexes / embeddings / retrieval JSON
- 外部Web本文、機密情報、secret、token、credential
- 削除すると再生成できない判断材料

これらは `work/db/ariadne-knowledge-platform/rag/`、または各workflowの `work/<work-id>/` 配下に置きます。

## work/db との違い

`work/db/ariadne-knowledge-platform/` は、knowledge source repository のローカル作業場所です。

```text
work/db/ariadne-knowledge-platform/
  rag/              knowledge source and file-based RAG artifacts
  registries/       registry backup / mirror when needed
  semantic-hints/   project-specific semantic hint backup
```

一方で、`db/rag/` は Ariadne本体側の生成物置き場です。

```text
db/rag/
  ariadne-knowledge.duckdb
  evidence/
```

つまり、`work/db/...` は「knowledgeを残す場所」、`db/rag/` は「knowledgeを検索しやすく投影した生成物を置く場所」です。

## Fresh Checkout

fresh checkout では、`db/rag/README.md` だけが存在していれば十分です。

`db/rag/ariadne-knowledge.duckdb` や `db/rag/evidence/` は、runtime実行時に必要に応じて自動生成されます。事前に空ディレクトリや空DBをcommitする必要はありません。

`work/` しか存在しない状態でも、RAG / semantic hints / VSCode environment などの runtime を実行すると、必要な `work/db/ariadne-knowledge-platform/rag/` 配下のディレクトリは順次作成されます。

## 再生成

標準RAG sourceから DuckDB read model を再構築する場合は、次を使います。

```powershell
.\runtime\windows-script\aiwfctl.cmd rag duckdb rebuild --reset
```

参照検索の疎通確認は、次を使います。

```powershell
.\runtime\windows-script\aiwfctl.cmd rag duckdb verify
```

`ARIADNE_KNOWLEDGE_REPOSITORY` が指定されている場合、runtime は `work/db/<repository-name>/rag/` を knowledge source として扱います。未指定時の既定は `work/db/ariadne-knowledge-platform/rag/` です。

## Git管理方針

`.gitignore` では `db/rag/**` を除外し、`db/rag/README.md` だけをcommitできるようにしています。

この方針により、fresh checkout ではREADMEで責務を確認でき、実行時にはruntimeが必要な DuckDB / evidence をローカルに生成できます。
