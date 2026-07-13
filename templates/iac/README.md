# IaC Templates

`templates/iac/` は、リアルタイムシステム向け Infrastructure as Code workflow の成果物ひな形です。

## Templates

| Template | Purpose |
| --- | --- |
| `software-inventory-template.md` | 基盤に入れるsoftware、version、runtime unit、ports、env、health check、責務境界の確認 |
| `communication-specification-template.md` | IaCに影響する通信flow、port、network boundary、security、failure behavior、evidenceの確認 |
| `realtime-iac-design-template.md` | network / security / runtime / observability / IaC generation の設計記録 |
| `realtime-iac-test-specification-template.md` | Docker Desktop、Linux runtime、integration、human check の試験仕様 |

## Rules

- `.env` は生成しない。`.env.example` のみ生成する。
- secret、token、certificate private key、production password は placeholder にする。
- software inventory、port、protocol、public exposure、network boundary は共有成果物から参照する。
- 共有成果物が不足する場合は `open-questions.md` を作成し、IaC生成を停止する。
- Docker Desktopで検証できないLinux依存項目は Linux runtime validation へ移す。
- Host設定変更やinstallが必要な検証は、人間承認前に実行しない。
- 開発・CI/CD・監視platformを構築する場合は `templates/boilerplates/platform-infra-template/` を候補にし、Terraform component selection、Docker Compose profile、admin CIDR、secret source、backup / restore、product別validation evidenceを確認する。
