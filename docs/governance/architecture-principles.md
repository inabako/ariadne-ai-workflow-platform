---
language: ja-JP
---

# Architecture Principles

この文書は、Ariadne AI Workflow Platform で守る設計原則を定義します。

設計原則は、実装を縛るためではなく、改善時の判断を安定させるためにあります。新しいworkflow、runtime helper、schema、RAG pipeline、docsを追加するときは、この原則に照らして構造を決めます。

## Responsibility Separation

目的: Human、AI Agent、Workflow、Dispatcher、Runtime、Repositoryの責務を分けます。

メリット: 失敗時にどこを直すべきか分かりやすくなり、AI Agentに過剰な判断を押し付けずに済みます。

採用理由: Ariadneは複数のworkflowとAgentが協調するplatformです。責務が混ざると、改善が局所的に成功しても全体の一貫性が壊れます。

運用上の注意: 便利だからという理由で、一つのscriptやpromptへ判断、実行、承認、記録を詰め込まないでください。

## Context First

目的: WorkflowやAgentが作業前に標準Contextを読み、前提を推論しない状態を作ります。

メリット: repository、branch、tool、環境、成果物の読み違いを減らし、後続workflowの再現性を高めます。

採用理由: AI Agentは不足した前提を補おうとします。Context Firstは、その推論負荷をplatform側で下げるための設計です。

運用上の注意: Contextが不足する場合は、推測で進めず、Context生成またはHuman Checkへ戻します。

## Dispatcher First

目的: Workflow実行前に、環境、tool、workflow選択、実行計画などをDispatcherが整理します。

メリット: 各workflowが独自に環境判断を実装せず、選択理由とHuman Check条件を共有できます。

採用理由: 同じ判断を複数箇所へ散らすと、改善時に矛盾が発生します。Dispatcherを先に置くことで判断を集約します。

運用上の注意: Dispatcher Contextをworkflow側で上書きしてはいけません。必要な変更は、新しいContextとして記録します。

## Human Check

目的: 人間の承認や判断が必要な操作を明示します。

メリット: GitHub mutation、push、RAG登録、install、実機操作などの副作用を安全に扱えます。

採用理由: AriadneはAI Agentを信頼しますが、人間の責任をAIへ移譲しません。

運用上の注意: Human Checkは形式的な確認ではありません。判断材料、選択肢、Evidenceを揃えてから人間へ渡します。

## Runtime Observability

目的: Runtimeの状態、error、retry、token、cost、Human Check、Evidence生成状況を後続workflowが読める形で残します。

メリット: 失敗や摩擦を個別の会話に閉じ込めず、改善候補として扱えます。

採用理由: Ariadne自身を改善するには、runtimeがどのように動いたかを観測可能にする必要があります。

運用上の注意: ログを増やすだけでは不十分です。machine-readableなmetrics、process report、artifact indexへ接続します。

## UTF-8を共通認識とする

目的: 日本語docs、prompt、schema、reportを安定して読み書きできる状態を作ります。

メリット: mojibakeによる誤読、diff汚染、Agent判断ミスを防ぎます。

採用理由: Ariadneは日本語を既定言語とする成果物を多く扱います。文字コードは品質と再現性の前提です。

運用上の注意: `.bat` / `.cmd` など意図的にShift_JIS / CP932を使う例外は境界を明示し、MarkdownやJSONはUTF-8を前提にします。

## Workflowは再利用可能であること

目的: 一度の作業だけでなく、別repository、別issue、別workflowから再利用できる構造にします。

メリット: 成果物、template、schema、helperを次の作業へ戻せます。

採用理由: Ariadneは継続改善platformです。再利用できないworkflowは、知識が蓄積されません。

運用上の注意: 特定案件の事情はContextやwork artifactへ置き、workflow本体へ埋め込みすぎないでください。

## Platformはローカルファーストを基本とする

目的: 主要な判断、検証、artifact生成をrepository-localに残します。

メリット: 外部サービスの状態に依存しすぎず、source of truthを追跡しやすくなります。

採用理由: Ariadneは、人間とAI Agentが同じworkspaceで成果物を確認できることを重視します。

運用上の注意: GitHubや外部toolを使う場合も、入力、判断、Evidence、出力の最小記録をlocal artifactとして残します。

## Knowledgeは構造化管理する

目的: docs、RAG source、schema、process report、archiveを後続workflowが使える知識として整理します。

メリット: 会話依存を減らし、改善判断を再利用できます。

採用理由: Knowledgeが散在すると、AI Agentは古い情報や曖昧な記憶を使い始めます。

運用上の注意: Knowledgeは現在の実装を上書きするものではありません。current repository evidenceを優先し、RAGは補助情報として扱います。

## Self-Improvement Workflow との関係

Self-Improvement Workflow は、改善案がこれらの設計原則を強めるか確認します。

Repository Curation Workflow は、責務分離、UTF-8、Knowledge構造、再利用性がrepository内で保たれているか確認します。

Runtime Maintenance Workflow は、Dispatcher First、Context First、Runtime Observabilityがruntime変更で壊れないか確認します。

## Summary

- Ariadneの設計は、責務分離、Context First、Dispatcher First、Human Checkを前提にする。
- UTF-8、Observability、Knowledge構造化は、日本語運用と継続改善の品質を支える。
- Workflowとruntimeは、一回限りではなく再利用可能なplatform資産として設計する。
- RAGや過去知識は補助であり、現在のrepository evidenceを優先する。
