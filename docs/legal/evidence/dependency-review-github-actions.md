# Dependency Review GitHub Actions運用Evidence

## 概要

- date: 2026-07-30
- workflow: `.github/workflows/dependency-review.yml`
- configuration: `.github/config/dependency-review.yml`
- artifact: `ariadne-dependency-review-results`
- output directory: `dependency-review-output/`
- purpose: OSS公開前後のpull requestで、dependency license policy違反とvulnerability混入を確認する。

## 起動条件

- `pull_request`: dependency changesをmerge前に確認する。
- `workflow_dispatch`: release前に任意のbase ref / head refを指定して手動確認する。

## ポリシー

Dependency Reviewは `deny-licenses` ではなく `allow-licenses` を使います。
許可list外のdependency licenseが追加された場合は、merge前に人間がlicense compatibilityと公開方針への影響を確認します。

AGPL公開においても、dependency licenseの適合性はdependencyの配布形態、利用形態、同梱有無によって変わります。
このworkflowのpassは法的判断の完了を意味せず、ScanCode / REUSE lint / human reviewと組み合わせてrelease gateの判断材料にします。

## 出力

- `dependencyChanges.json`
- `vulnerableChanges.json`
- `invalidLicenseChanges.json`
- `deniedChanges.json`
- `commentContent.md`
- `dependency-review-summary.md`
- `execution-metadata.json`

## 残作業

- GitHub Actions上でPR作成時に `.github/workflows/dependency-review.yml` が実行されることを確認する。
- 公開前に `workflow_dispatch` でbase ref / head refを指定し、artifactを確認する。
- 許可license listは、実際のdependency review結果と公開方針に応じて継続的に見直す。

このファイルはreview evidenceであり、法的助言ではありません。
