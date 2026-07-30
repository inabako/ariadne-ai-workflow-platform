# 変更履歴

ARIADNE の主な変更はこのファイルに記録します。

このprojectはreview可能なrelease noteを重視します。日付は `YYYY-MM-DD` 形式で記載します。

英語版は [CHANGELOG.en.md](CHANGELOG.en.md) を参照してください。

## [Unreleased]

### 追加

- OSS公開基盤のdocs、citation metadata、release checklist、release validation toolingを追加。
- `aiwfctl`、runtime、workflow dispatch、state、artifact、evidence、Human Gate、recoveryのarchitecture docsを追加。
- `AGPL-3.0-or-later` license policy、legal boundary docs、release validation supportを追加。

### 変更

- ルートREADMEからOSS公開、release、citation、contribution、security、license関連docsへ辿れるように更新。
- Ariadne workflow資産を `.github/` から `.ariadne/` へ移動し、`.github/` をGitHub platform設定中心に整理。

### Security

- 公開前に必須ファイルとprivate data候補を確認するrelease validationを追加。
