# Robotics Safety Gates

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成してください。

## Purpose

Robotics workflow の各段階で、安全に次へ進めるかを判断するための gate です。

Safety Gate は作業を止めるためではなく、危険な曖昧さを早い段階で見つけるためにあります。

## Gate 0: Intent Safety

適用タイミング:

- 新システム開発の開始時
- 大きな保守変更の開始時

確認:

- robot の mission が明確
- robot がしてはいけないことが明確
- target environment が明確
- human / equipment risk が初期認識されている
- emergency stop の必要性が検討されている

Fail 条件:

- 何を安全に守るべきか不明
- operator / environment が未定義
- physical risk を扱わずに implementation へ進もうとしている

## Gate 1: Architecture Safety

確認:

- control / video / telemetry / safety / network の責務が分かれている
- STOP path が最短かつ最高優先
- startup safe state が定義済み
- shutdown safe state が定義済み
- communication loss の behavior が定義済み
- process failure の recovery path がある

Fail 条件:

- STOP より他 command が優先される可能性がある
- stale command で走り続ける可能性がある
- safety responsibility がどこにも明示されていない
- failure domain が理由なく一体化している

## Gate 2: Implementation Safety

確認:

- safety-critical behavior が test されている
- timeout / command age / sensor freshness が扱われている
- invalid sensor value を正常値として扱わない
- process restart 後に safe state へ戻る
- logs / telemetry が safety event を記録する

Fail 条件:

- emergency stop test がない
- communication loss test がない
- sensor abnormality handling がない
- safety-critical constants が undocumented

## Gate 3: Bench Safety

確認:

- motor / actuator の意図しない動作がない
- left-right inversion / wiring mismatch を確認した
- video loss / telemetry loss が operator に見える
- watchdog / supervisor が期待通り動く
- rollback 手順が机上または限定環境で確認済み

Fail 条件:

- 実機投入前に STOP を確認していない
- 異常時に operator が状態を認識できない
- rollback が手順として存在しない

## Gate 4: Field Trial Safety

確認:

- test scenario が定義済み
- operator / observer / emergency stop role が明確
- field boundary が明確
- trial 中止条件が明確
- incident / near-miss の保存先が決まっている

Fail 条件:

- 誰が止めるか不明
- どの条件で中止するか不明
- field trial の範囲が曖昧
- high / critical finding が未解決

## Gate 5: Release Safety

確認:

- operation guide がある
- troubleshooting がある
- rollback plan がある
- monitoring checklist がある
- operator が degraded state を理解できる
- post-release observation plan がある

Fail 条件:

- 運用者が異常状態を判断できない
- rollback できない
- logs / telemetry から incident を追えない
- known critical risk が未解決

## Severity Rule

| Severity | Meaning | Default Action |
| --- | --- | --- |
| critical | 人、設備、機体に即時危険 | stop / redesign |
| high | 暴走、安全停止不全、重大な operator error risk | block release |
| medium | safety低下、recovery困難、観測不足 | conditional pass with action |
| low | 改善提案 | track |
| info | clarify / traceability | record |

## Safety Gate Record Template

```markdown
# Safety Gate Record


## Gate

## Decision

pass / conditional-pass / fail

## Evidence

## Findings

| ID | Severity | Finding | Required Action | Owner |
| --- | --- | --- | --- | --- |

## Required Tests

## Open QA

## Final Judgment
```

