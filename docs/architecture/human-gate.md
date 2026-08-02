# Human Gate

Human Gateは、project ownerの判断が必要な操作を明示的に止めるdecision pointです。

## 典型的なGate発火条件

- license、trademark、publication policyの判断。
- 不可逆なGit、GitHub、release、deployment操作。
- security-sensitiveな変更。
- evidenceの削除または不可視化。
- repository history、release note、artifactの公開。
- constrainedまたは未検証の設計判断の受容。

## Gate出力

Human Gateでは次を記録します。

- decision status。
- 判明している場合はdecision makerまたはreview owner。
- reviewしたevidence。
- 選択したoptionと却下したalternative。
- follow-up action。

## 現在のOSS Gate

現在のrepository license方針は `AGPL-3.0-or-later` です。release時に必要な著作権者、公開URL、release日、GitHub Security Advisories方針、third-party dependency license reviewは [legal-review-items.md](../legal/evidence/legal-review-items.md) で追跡します。
