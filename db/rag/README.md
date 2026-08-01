# db/rag

`db/rag/` は、Ariadne の file-based RAG 知識を検索しやすくするための、ローカル生成 read model と検証 evidence の置き場です。

このディレクトリは RAG 知識の source of truth ではありません。

## 役割

Ariadne では、RAG の元データと生成済みDBを分けて扱います。

| 種別 | 主な場所 | Git管理 | 役割 |
| --- | --- | --- | --- |
| RAG source / JSON / JSONL | `work/db/ariadne-knowledge-platform/rag/` | 原則 workflow 方針に従う | Human Review 済み知識、normalized document、chunk、index、embedding、retrieval artifact |
| DuckDB read model | `db/rag/ariadne-knowledge.duckdb` | しない | RAG source から再生成できる検索用DB |
| migration / reference check evidence | `db/rag/evidence/` | しない | DuckDB rebuild、ingestion、reference check のローカル検証結果 |
| この README | `db/rag/README.md` | する | ディレクトリ責務の説明 |

## 置いてよいもの

- `ariadne-knowledge.duckdb`
- `migration-errors.jsonl`
- `evidence/migration-summary.json`
- `evidence/reference-check.json`
- `evidence/ingestion/`
- `evidence/context/`

これらは runtime が生成するローカル成果物です。再生成可能なため、通常は commit しません。

## 置かないもの

- Human Review 前の作業メモ
- RAG source Markdown
- normalized document JSON
- chunks / indexes / embeddings / retrieval JSON
- 外部Web本文や、機密情報を含む可能性がある raw data

長期保存する RAG 知識は、`work/db/ariadne-knowledge-platform/rag/` 側に保存します。

## 再生成

標準 RAG source から DuckDB read model を再構築する場合は、次を使います。

```powershell
.\runtime\windows-script\aiwfctl.cmd knowledge rebuild --reset
```

参照検索の疎通確認は、次を使います。

```powershell
.\runtime\windows-script\aiwfctl.cmd knowledge verify
```

`ARIADNE_KNOWLEDGE_REPOSITORY` が指定されている場合、runtime は `work/db/<repository-name>/rag/` を知識ソースとして扱います。未指定時の既定は `work/db/ariadne-knowledge-platform/rag/` です。

## Git 管理方針

`.gitignore` では `db/rag/**` を除外し、`db/rag/README.md` だけを commit できるようにしています。

この方針により、fresh checkout では README によって責務を確認でき、実行時には runtime が必要な DuckDB / evidence をローカルに生成できます。
