# アーキテクチャ概要

ARIADNEは、Context Firstを基本にしたAI workflow platformです。文書化されたworkflow入口、runtime helper、state artifact、evidence、Human Gate、復帰経路を組み合わせて作業を進めます。

## システム構成

- `.ariadne/prompts/` はworkflow入口promptを定義します。
- `.ariadne/agents/` は専門agentの責務を定義します。
- `.ariadne/schemas/` はworkflow artifactのJSON contractを定義します。
- `runtime/` は再現可能な実行のために `aiwfctl` とhelper moduleを提供します。
- `docs/` はworkflow、governance、runtime、release、運用方針を説明します。
- `templates/` は再利用可能なartifact templateを保存します。
- `work/` はlocal workflow出力を保存します。多くはGit管理対象外です。

## 運用原則

実行前に判断を検査可能にすることを重視します。workflowは不可逆な変更を行う前に、intent、必要context、安全確認、期待artifact、evidence、handoff条件を明確にします。

## アーキテクチャ文書

- [aiwfctlアーキテクチャ](aiwfctl-architecture.md)
- [Runtimeアーキテクチャ](runtime-architecture.md)
- [Workflow Dispatch](workflow-dispatch.md)
- [StateとArtifact管理](state-and-artifact-management.md)
- [Evidenceと完了条件](evidence-and-completion.md)
- [Human Gate](human-gate.md)
- [RetryとResume](retry-and-resume.md)
