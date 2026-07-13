# Ariadne Feature / Maintenance Requirements

## Intent

既存対象システムに対する新機能追加、bug fix、保守変更、field feedback対応で達成したいことを記載します。

## Decision

この要件定義書では、対象repository、target branch、Issue化する変更内容、影響範囲、risk、test、rollbackを定義します。

## Reason

保守開発では、既存の安全挙動、operator workflow、runtime、network、external dependency を壊さないことが重要です。

## Repository Control

この欄は `runtime/intake/intake_requirements.py` と `runtime/scm/prepare_repository.py` が読み取ります。

repository が空の場合、この要件定義書は受領されません。

| Item | Value |
| --- | --- |
| Target Repository | required |
| GitHub Owner |  |
| GitHub Repository |  |
| GitHub Repository URL |  |
| Target Branch | main |
| Git Remote | origin |

## Noise Reduction Reference

要件review draft作成前に実行したNoise Reduction Phaseの結果を記録します。

| Item | Value |
| --- | --- |
| Noise Reduction Directory | work/requirements/draft/<draft-stem>-noise-reduction/ |
| Readiness | PASS / WARNING / BLOCK |
| Human Interview Sheet |  |
| Project Glossary |  |
| Remaining WARNING Items |  |

## Change Identity

| Item | Value |
| --- | --- |
| Change Title |  |
| Change Type | feature / bugfix / safety-improvement / reliability / observability / device-replacement / docs |
| Target System / Component |  |
| Related Incident / Field Note |  |
| Expected GitHub Issue Title |  |

## Current Behavior

現在の挙動、既存仕様、既知の制約を記載します。

## Target Behavior

変更後に期待する挙動を記載します。

## Scope

| Area | In Scope | Out of Scope |
| --- | --- | --- |
| Control |  |  |
| Video |  |  |
| Telemetry |  |  |
| Safety |  |  |
| Network |  |  |
| Runtime |  |  |
| UI / Operator |  |  |
| Deployment |  |  |

## Risk Classification

| Level | Selected | Reason |
| --- | --- | --- |
| low | yes/no | docs、ログ追加、非制御領域の軽微修正 |
| medium | yes/no | telemetry表示、operator UI、network設定、runtime restart |
| high | yes/no | control logic、timeout、STOP、sensor handling、deployment topology |
| critical | yes/no | emergency stop、motor output、remote command authority、人や設備への直接危険 |

## Functional Requirements

| ID | Requirement | Reason | Acceptance Criteria |
| --- | --- | --- | --- |
| FR-001 |  |  |  |

## Compatibility / Regression Concerns

| Existing Behavior | Concern | Required Test |
| --- | --- | --- |
|  |  |  |

## Safety Impact

| Item | Impact | Required Action |
| --- | --- | --- |
| STOP / emergency stop | none / changed / unknown |  |
| Communication loss | none / changed / unknown |  |
| Startup safe state | none / changed / unknown |  |
| Shutdown safe state | none / changed / unknown |  |
| Sensor failure | none / changed / unknown |  |

## Test Requirements

| ID | Test Type | Scenario | Required Evidence |
| --- | --- | --- | --- |
| TEST-001 | unit / integration / simulation / bench / limited-field / rollback-rehearsal |  |  |

## Deployment / Rollback

| Item | Requirement |
| --- | --- |
| Deployment Target |  |
| Maintenance Window |  |
| Rollback Plan |  |
| Post-change Observation |  |

## GitHub Issue Notes

この内容は `runtime/github/issue_manager.py` が作成するIssue bodyの材料になります。

| Item | Value |
| --- | --- |
| Labels |  |
| Assignees |  |
| Acceptance Criteria Summary |  |

## Open Questions

| ID | Question | Impact | Owner | Blocking |
| --- | --- | --- | --- | --- |
| QA-001 |  |  |  | yes/no |
