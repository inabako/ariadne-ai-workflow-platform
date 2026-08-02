# Shared Agent Instructions

このディレクトリには、すべてのAgentが共通で読むべき運用ルールを格納します。

`schemas/` は構造化された受け渡し契約、`shared/` はAgentの振る舞いと判断基準を定義します。

## Shared Files

| File | Purpose |
| --- | --- |
| `agent-handoff.md` | Agent間の引き継ぎルール |
| `ariadne-principles.md` | Ariadne workflow の共通判断原則 |
| `artifact-management.md` | artifact index と保存先の扱い |
| `gate-restart-policy.md` | workflow gate failure 後に同じ gate へ戻り、修復後も同じ gate から再開する共通ルール |
| `output-language-policy.md` | report / document / evidence / RAG source の既定言語ルール |
| `risk-and-severity.md` | risk level と severity の共通定義 |
| `runtime-entrypoint-policy.md` | `aiwfctl` / `runtime/ctl/ctl.py` を正式runtime入口にする共通ルール |

## Rule

Agent は、自分の成果物だけで完結しません。

次のAgentが判断を継続できるように、decision、reason、evidence、open QA、risk、artifact path を残します。
