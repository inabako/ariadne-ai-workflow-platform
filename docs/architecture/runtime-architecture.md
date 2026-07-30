# Runtimeアーキテクチャ

`runtime/` 配下のruntimeは、workflow実行、review、validation、artifact管理を再現可能にするlocal helper群です。

## 主な領域

- `runtime/ctl/`: `aiwfctl` のcommand parsingとdispatch。
- `runtime/workflow/`: workflow別helper module。
- `runtime/design/`: expectation-driven design flow helper。
- `runtime/review/`: review永続化とReview Council支援。
- `runtime/rag/`: local RAGの保存、ingestion、retrieval、dispatch helper。
- `runtime/tools/`: repository品質とencoding utility。
- `runtime/tests/`: runtime contractを確認するpytest。

## Contract

Runtime commandは、構造化された出力、決定的なpath、明示的なstatus、人間または後続workflowが復帰できるだけのdiagnostic dataを返します。

## 失敗時の扱い

復帰可能な失敗では、next actionと、利用できる場合はresume commandを示します。releaseに関わるcommandは、security failureやvalidation failureを隠してはいけません。
