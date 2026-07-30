# コントリビューションガイド

ARIADNEへの貢献を検討いただきありがとうございます。

ARIADNEは、intent capture、context-first execution、review可能なartifact、Human Gate、recovery、再現可能なevidenceを重視するAI workflow platformです。貢献時も、この責務境界を保つことを大切にしてください。

英語版は [CONTRIBUTING.en.md](CONTRIBUTING.en.md) を参照してください。

## 始める前に

- documentation mapとして [docs/README.md](docs/README.md) を確認してください。
- platform構造は [docs/architecture/overview.md](docs/architecture/overview.md) を確認してください。
- releaseに影響する変更では [docs/release/release-policy.md](docs/release/release-policy.md) を確認してください。
- 明示的にtracked artifactとして定義されていない生成物は、`work/`、`logs/`、`db/rag/` などのignored workspaceに保存してください。

## Contribution Flow

1. intent、期待するimpact、影響範囲が分かるIssueを作成または参照してください。
2. runtime behavior、tests、documentation、release metadataのscopeが独立している場合は、reviewしやすい粒度に分けてください。
3. behavior変更には必要なtestを追加または更新してください。
4. command、schema、artifact location、実装挙動が変わる場合はdocsも更新してください。
5. review依頼前に関連checkを実行してください。

## Pull Request Expectations

- Intent、Scope、Decision、Impactを記載してください。
- 関連Issue、design note、evidenceをリンクしてください。
- test commandと結果を記載してください。
- Human Gate decision、security-sensitive behavior、release impactがある場合は明記してください。

## ライセンス

貢献することで、その貢献がARIADNEのrepository licenseである `AGPL-3.0-or-later` のもとで配布されることに同意したものとします。

project ownerが承認したlicense decisionでない限り、通常の貢献でlicense identifier、package license metadata、root `LICENSE` を変更しないでください。

ARIADNEをtoolとして使用して生成されたoutputは、ARIADNEを使用したという理由だけで自動的にARIADNE repository licenseへ割り当てられるものではありません。詳細は [docs/legal/generated-artifacts.md](docs/legal/generated-artifacts.md) を参照してください。

## Code and Documentation Standards

- 新しい抽象化より、既存のruntime / workflow patternを優先してください。
- UTF-8 text encodingを維持してください。
- secret、顧客情報、private URL、local absolute path、非公開project detailsをtracked filesに追加しないでください。
- 人間向けreport、review artifact、docsは、別途指定がない限り日本語で記載してください。
- 未実装機能を完了済みとして説明しないでください。

## Release Checks

releaseに影響する変更では、次を実行してください。

```powershell
aiwfctl release validate
```
