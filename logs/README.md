# Logs

`logs/` は、Ariadne runtime がローカル実行中に生成するログの出力先です。

生成された log file は machine-local な観測データであり、原則として Git 管理しません。継続的に残すべき証跡は、目的に応じて `work/<work-id>/test-evidence/`、`work/<work-id>/process-report/`、`docs/legal/evidence/` などの evidence directory へ転記してください。

## 管理方針

- `logs/README.md` と `logs/runtime/README.md` だけを Git 管理します。
- `logs/runtime/runtime-events.log` などの実ログは Git 管理しません。
- runtime trace id を使って調査する場合は、必要な範囲だけを report や Feedback に要約します。
- secret、token、個人環境固有の値を含む可能性があるため、log file をそのまま commit しないでください。
