# Ariadne Test Strategy

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.ariadne/shared/output-language-policy.md` に従って日本語で作成してください。

## Purpose

対象システムの test strategy を定義します。

Ariadne では、unit test だけでは安全を保証できません。simulation、mock、bench、limited field test を段階的に組み合わせます。

## Test Pyramid For Ariadne

```text
field test
bench test
hardware mock / HIL-like test
simulation / integration test
unit test
static checks
```

上に行くほど現実に近く、cost と risk が上がります。下位 test で潰せる問題を field test に持ち込まないことを重視します。

## Test Types

### Static Checks

目的:

- obvious bug
- type / lint / formatting
- unsafe dependency / config

対象:

- source code
- config
- scripts
- docs links

### Unit Test

目的:

- pure logic
- parser
- command validation
- safety state transition
- timeout calculation

確認:

- command age
- invalid input
- boundary values
- STOP priority
- state machine transition

### Integration Test

目的:

- component 間の接続確認
- protocol compatibility
- process interaction

確認:

- GUI -> control command
- telemetry -> UI state
- video state -> operator warning
- reconnect behavior
- config loading

### Simulation Test

目的:

- 実機なしで scenario を検証する
- dangerous condition を安全に再現する

確認:

- communication loss
- sensor stale / invalid
- obstacle-like input
- delayed telemetry
- command burst
- process crash

### Hardware Mock / HIL-like Test

目的:

- hardware dependency を限定的に再現する
- driver / device interface を確認する

確認:

- motor command output boundary
- sensor value mapping
- camera unavailable
- GPS / IMU unavailable
- power warning input

### Bench Test

目的:

- 実機または実デバイスを、制御された環境で確認する

確認:

- startup safe state
- STOP
- low-speed movement
- left-right direction
- video stream
- telemetry freshness
- network disconnect
- restart / recovery

### Limited Field Test

目的:

- 現場条件で限定的に確認する

確認:

- operator workflow
- visibility
- connectivity
- degraded state
- emergency stop role
- logs / telemetry usefulness
- incident capture

## Required Regression Areas

変更内容に関係なく、対象システムでは次を regression 候補にします。

- STOP / emergency stop
- startup safe state
- shutdown safe state
- communication timeout
- stale command handling
- video loss handling
- telemetry freshness
- sensor abnormality
- process restart
- operator degraded state
- logs / telemetry output

## Change-Based Test Viewpoints

テスト実行前に、修正点ごとのテスト観点を作成します。

入力として以下を使います。

- corrective action report
- Issue scope
- implementation plan
- changed files / planned diff
- RAGで取得した過去の類似不具合や疎通ノウハウ

各修正点について、最低1つのテストケースを割り当てます。直接テストできない場合は、理由、残リスク、代替証跡を明記します。

観点:

- normal behavior
- boundary / error behavior
- regression risk
- safety impact
- observability: logs, metrics, telemetry, UI display
- integration / communication path

```markdown
| Change ID | Planned Change / Fix Point | Affected File / Component | Behavior To Prove | Risk | Test Viewpoint | Test Case IDs | Untestable Reason / Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CHG-001 |  |  | normal / boundary / error / regression / safety / observability | low / medium / high / critical |  | TC-001 |  |
```

## Test Matrix Template

```markdown
| ID | Area | Test Type | Scenario | Expected Result | Required For |
| --- | --- | --- | --- | --- | --- |
| T-001 | Safety | unit | STOP command has highest priority | robot enters safe stop | all releases |
| T-002 | Network | integration | heartbeat timeout | command output stops | control changes |
| T-003 | Video | integration | video stream loss | UI shows degraded state | remote operation |
| T-004 | Runtime | bench | control process restart | startup safe state | runtime changes |
```

## Evidence Rule

Test result は、未来の調査で使える形で残します。

残すもの:

- command
- environment
- robot / device identifier where available
- version / commit
- result
- logs / screenshots / telemetry
- unresolved issue

## Quality Gate

次の場合、release または field trial に進みません。

- STOP test がない
- communication loss test がない
- high / critical finding が未解決
- field test の中止条件がない
- rollback rehearsal がない
- operator が degraded state を認識できない
