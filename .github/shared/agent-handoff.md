# Agent Handoff

## Purpose

Agent が次のAgentへ作業を渡すときの共通ルールです。

Handoff は単なる要約ではありません。次のAgentが同じ文脈を再探索せず、判断の続きから始められるようにするための context package です。

## Required Handoff Contents

Agent は作業終了時に、必要に応じて `handoff-package.schema.json` に沿って以下を残します。

- from agent
- to agent
- workflow / phase
- intent
- summary
- decisions
- artifacts
- open questions
- risks
- required next actions
- stop conditions

## Handoff Quality Gate

以下が不足している handoff は不十分です。

- なぜその判断になったかが書かれていない
- 未解決QAが隠れている
- blocking risk が severity なしで書かれている
- artifact path がない
- 次に誰が何を確認すべきか不明

## Do Not

- 次Agentに必要な前提を会話ログだけに残さない
- safety-critical QA を summary に埋めない
- finding を「注意」だけで終わらせない
- evidence なしに pass と判断しない
