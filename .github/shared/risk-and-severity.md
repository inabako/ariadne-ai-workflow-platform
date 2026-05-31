# Risk And Severity

## Purpose

Agent 間で risk level と severity の意味を揃えます。

## Risk Level

Risk level は、変更や作業単位の危険度です。

| Level | Meaning | Default Requirement |
| --- | --- | --- |
| low | docs、ログ追加、非制御領域の軽微修正 | targeted test |
| medium | telemetry表示、operator UI、network設定、runtime restart | regression + integration |
| high | control logic、timeout、STOP、sensor handling、deployment topology | safety review + bench test |
| critical | emergency stop、motor output、remote command authority、人や設備への直接危険 | formal safety gate + limited field test |
| unknown | 判断材料が足りない | QA before implementation |

## Finding Severity

Severity は、review finding 単体の重大度です。

| Severity | Meaning | Default Action |
| --- | --- | --- |
| critical | 人、設備、機体に即時危険がある | stop / redesign |
| high | 暴走、安全停止不全、重大な operator error risk | block release |
| medium | safety低下、recovery困難、観測不足 | conditional pass with action |
| low | 改善提案 | track |
| info | clarification / traceability note | record |

## Blocking Rule

以下は原則として blocking です。

- STOP behavior が未定義
- communication loss behavior が未定義
- startup / shutdown safe state が未定義
- safety-critical QA が未回答
- rollback plan がない high / critical change
- field trial stop condition がない

