# Legal Documents

このdirectoryは、ARIADNEのOSS公開に向けたlicense方針、生成artifact方針、第三者license確認、公開前review項目をまとめる入口です。

## 方針文書

人間が読むためのpolicy / guideです。

| Document | Purpose |
| --- | --- |
| [license-policy.md](license-policy.md) | `AGPL-3.0-or-later` 方針、`or-later` の意味、生成artifactへの非波及方針 |
| [generated-artifacts.md](generated-artifacts.md) | ARIADNEをtoolとして使った生成artifactのlicense boundary |
| [component-license-boundaries.md](component-license-boundaries.md) | ARIADNE本体、外部入力、生成物、組み込みmaterialの境界 |
| [network-source-offer.md](network-source-offer.md) | AGPLでnetwork提供する場合のsource提供確認項目 |
| [third-party-licenses.md](third-party-licenses.md) | dependency license reviewの入口 |
| [faq.md](faq.md) | 公開前後に利用者へ説明するlicense FAQ |

## Release Evidence

公開前確認の結果や、未完了review項目を構造化して残すevidenceです。方針そのものではなく、release candidateの確認状態を表します。

| Evidence | Purpose |
| --- | --- |
| [evidence/legal-review-items.md](evidence/legal-review-items.md) | 公開前に人間確認が必要な著作権者、公開URL、security contactなど |
| [evidence/dependency-license-report.json](evidence/dependency-license-report.json) | third-party dependency license review状況 |
| [evidence/license-boundary-report.json](evidence/license-boundary-report.json) | ARIADNE本体、生成物、外部入力のlicense boundary確認 |
| [evidence/release-license-check.json](evidence/release-license-check.json) | AGPL方針へのrelease license整合性確認 |
