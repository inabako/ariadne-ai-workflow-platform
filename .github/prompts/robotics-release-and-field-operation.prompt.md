# Robotics Release And Field Operation

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成してください。

## Purpose

Robotics system を現場へ出す前後の release、rollback、operation handover、incident capture を定義します。

Release は software deployment だけではありません。operator、robot、network、field condition、recovery procedure を含む運用切り替えです。

## Release Readiness

確認:

- release target が明確
- affected robot / environment が明確
- required tests が完了
- safety review の blocking finding がない
- rollback plan がある
- operation guide が更新済み
- operator notice がある
- monitoring / telemetry 確認方法がある

## Release Plan Template

```markdown
# Release Plan


## Release Intent

## Target

- robot / device:
- environment:
- version / commit:
- operator:

## Changes

## Risk Level

low / medium / high / critical

## Required Tests

## Deployment Steps

## Rollback Steps

## Monitoring Plan

## Stop Conditions

## Owner
```

## Rollback Principle

Rollback は「失敗したら考える」ものではなく、release 前に確認するものです。

確認:

- 何を戻すのか
- どの version に戻すのか
- config / model / dependency も戻す必要があるか
- robot 側と GUI 側の互換性はあるか
- rollback 後に最低限どの test をするか

## Field Operation Checklist

開始前:

- emergency stop 手段を確認した
- operator / observer / recorder の役割を確認した
- field boundary を確認した
- network state を確認した
- battery / power を確認した
- logs / telemetry capture を開始した
- trial stop condition を確認した

実行中:

- operator が robot state を認識できている
- degraded state が表示されている
- video / telemetry delay が許容範囲
- unexpected movement がない
- warning / error を記録している

終了後:

- robot が safe state
- logs / telemetry を保存
- operator feedback を記録
- incident / near-miss を記録
- next action を決める

## Incident Capture

Incident または near-miss は、責めるためではなく system を育てるために記録します。

保存先候補:

```text
knowledge-inbox/
  field-notes/
  investigations/
  improvement-reports/
```

Incident note に含める内容:

- date / time
- environment
- robot / version
- operator action
- observed behavior
- expected behavior
- safety state
- logs / telemetry reference
- suspected cause
- immediate action
- follow-up action
- RAG candidate tags

## Post-release Observation

Release 後に確認すること:

- error / warning frequency
- reconnect frequency
- process restart
- communication latency
- video loss
- command timeout
- operator confusion
- field feedback

## Operation Handover

運用者へ渡すもの:

- operation guide
- startup / shutdown procedure
- emergency stop procedure
- degraded state explanation
- troubleshooting
- contact / escalation path
- known limitations
- rollback / maintenance request procedure

## Exit Conditions

- release plan が完了
- rollback plan が確認済み
- post-release observation が記録済み
- incident / near-miss があれば knowledge-inbox に保存済み
- next improvement が必要なら issue / field note 化済み

