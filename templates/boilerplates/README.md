# Boilerplate Templates

新システム開発で、既存の共通土台からservice / appを生成するためのboilerplate置き場です。

このディレクトリは、成果物ひな形ではなく、実装の出発点になるsource templateを置きます。

## Supported Template Names

| Template | Target | Instruction | Status |
| --- | --- | --- | --- |
| `gateway-template/` | Go gateway service | `gateway-template_組み込み指示書.md` | available |
| `pyqt-template/` | PyQt / Qt GUI app | `pyqt-template_組み込み指示書.md` | available |
| `realtime-gateway-infra-template/` | Realtime gateway IaC / infrastructure | `realtime-gateway-infra-template_実装指示書.md` | available |

## Workflow Rule

- 新システム開発では、Implementation前にこのディレクトリを確認します。
- 対応するtemplate directoryが存在する場合、templateをコピーして新しいservice / app / IaC directoryを作ります。
- template本体は直接編集しません。
- 対応するtemplate directoryが存在しない場合、`decision: traditional-coding` と理由をprocess reportに残し、従来どおりcodingします。
- template採用時も、architecture、protocol、port、safety behavior、test case table、evidence planを省略しません。
- IaC template採用時も、shared artifacts、software inventory、public exposure、secret source、firewall policy、rollbackを省略しません。

## Expected Selection Report

```text
work/<receipt-id>/process-report/boilerplate-template-selection.md
```

Report template:

```text
templates/process-report/boilerplate-template-selection-report-template.md
```
