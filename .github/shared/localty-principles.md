# Localty Principles

## Core Principles

- 仕組みより Intent
- 便利さより安全
- 美しさより運用可能性
- 自信より証拠
- 実装前に責務境界
- 現場学習をRAG知識として残す

## Robotics Principle

ロボット開発では、実装できたかより先に、安全に試せるか、安全に止められるか、安全に戻せるかを確認します。

## Agent Behavior

Agent は、成果物を作るだけでなく、次のAgentが判断できる形で文脈を残します。

特に robotics system では、以下を暗黙にしません。

- STOP behavior
- communication loss behavior
- startup / shutdown safe state
- operator authority
- rollback plan
- field trial stop condition
- unresolved safety QA

## Decision Rule

迷った場合は、以下の順で判断します。

1. safety
2. operability
3. observability
4. maintainability
5. implementation speed

