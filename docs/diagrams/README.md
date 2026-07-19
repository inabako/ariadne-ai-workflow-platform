# Mermaid Diagrams

このディレクトリは、Ariadne AI Workflow の視覚理解を速くするためのMermaid図を置きます。

## Documents

| Document | Purpose |
| --- | --- |
| [Workflow Flowcharts](workflow-flowcharts.md) | 各AI workflowのMermaid式flowchart |
| [Workflow Flowchart Process Tables](workflow-flowchart-process-tables.md) | flowchartを業務工程ごとの表で解説する横断資料 |
| [Dispatcher / Workflow Map](dispatcher-workflow-map.md) | Dispatcher群と各Workflowの関係、Context First gate、RAG dispatchの位置づけ |

## Rule

- Mermaid図は、詳細手順そのものではなく、動作イメージを掴むための入口として使います。
- 表ベースの解説は、flowchartを業務工程、入力、出力、gateへ読み替えるために使います。
- 詳細な実行手順は `docs/workflows/` と `skills/<skill-name>/SKILL.md` をsource of truthにします。
