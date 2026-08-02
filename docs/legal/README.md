# Legal Documents

このdirectoryは、ARIADNEのOSS公開と継続release運用に必要なlicense方針、生成artifact方針、第三者license確認、release review項目をまとめる入口です。

## 方針文書

人間が読むためのpolicy / guideです。

| Document | Purpose |
| --- | --- |
| [license-policy.md](license-policy.md) | `AGPL-3.0-or-later` 方針、`or-later` の意味、生成artifactへの非波及方針 |
| [generated-artifacts.md](generated-artifacts.md) | ARIADNEをtoolとして使った生成artifactのlicense boundary |
| [component-license-boundaries.md](component-license-boundaries.md) | ARIADNE本体、外部入力、生成物、組み込みmaterialの境界 |
| [network-source-offer.md](network-source-offer.md) | AGPLでnetwork提供する場合のsource提供確認項目 |
| [third-party-licenses.md](third-party-licenses.md) | dependency license reviewの入口 |
| [../security/scancode-github-actions.md](../security/scancode-github-actions.md) | ScanCode Toolkitによるrelease前 / 継続license auditの実行手順 |
| [faq.md](faq.md) | 利用者へ説明するlicense FAQ |

## Release Evidence

release確認の結果や、未完了review項目を構造化して残すevidenceです。方針そのものではなく、release candidateや継続監査の確認状態を表します。

| Evidence | Purpose |
| --- | --- |
| [evidence/legal-review-items.md](evidence/legal-review-items.md) | release時に人間確認が必要な著作権者、公開URL、GitHub Security Advisories方針など |
| [evidence/dependency-license-report.json](evidence/dependency-license-report.json) | third-party dependency license review状況 |
| [evidence/license-boundary-report.json](evidence/license-boundary-report.json) | ARIADNE本体、生成物、外部入力のlicense boundary確認 |
| [evidence/release-license-check.json](evidence/release-license-check.json) | AGPL方針へのrelease license整合性確認 |
| [evidence/reuse-lint-local-rehearsal.md](evidence/reuse-lint-local-rehearsal.md) | REUSE lintローカル予行結果とSPDX metadata整備の残課題 |
| [evidence/dependency-review-github-actions.md](evidence/dependency-review-github-actions.md) | Dependency ReviewによるPR依存license / vulnerability確認の運用記録 |
| [evidence/workflows-public-readiness-local-rehearsal.md](evidence/workflows-public-readiness-local-rehearsal.md) | GitHub Actions workflowの公開準備ローカル予行結果 |

## ScanCode Evidence

ScanCode Toolkitの実行結果はGitHub Actions artifactとして保存し、`scancode-output/scancode-results.json` を正式な監査成果物、`scancode-output/scancode-results.html` を人間確認用の補助成果物として扱います。

ScanCode artifactはrepositoryへ直接commitせず、review結果だけを必要に応じて [evidence/dependency-license-report.json](evidence/dependency-license-report.json) と [evidence/legal-review-items.md](evidence/legal-review-items.md) に反映します。

## REUSE Lint Evidence

REUSE lintは、repository内fileのSPDX copyright / license metadataが機械可読に整備されているかを確認するために使います。
ローカル予行結果は [evidence/reuse-lint-local-rehearsal.md](evidence/reuse-lint-local-rehearsal.md) に記録します。

## Dependency Review Evidence

Dependency Reviewは、pull requestで追加・変更されるdependencyのlicense policy違反とvulnerabilityを確認するために使います。
GitHub Actionsの実行結果はartifactとして保存し、release時およびpull request時の依存関係review evidenceとして扱います。
