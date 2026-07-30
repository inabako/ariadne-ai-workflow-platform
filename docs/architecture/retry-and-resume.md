# RetryとResume

ARIADNE workflowは、中断後に復帰できることを前提にします。

## Retry

Retryは、tool、environment、validationなどの一時的な問題で失敗し、再実行しても危険な重複副作用を生まない場合に適しています。

## Resume

Resumeは、永続化されたstateまたはartifactから、最後に完了したstepと次の安全なactionを特定できる場合に適しています。

## 要件

- 完了済み作業と未完了作業を特定できるstateを残す。
- 不可逆な副作用を自動で繰り返さない。
- 失敗したvalidation outputを見える状態に残す。
- runtimeが提供できる場合は、文書化されたresume commandを優先する。

## Release作業

Release validationとmanifest generationは、同じsource stateから同じreview可能な結果を生成できるよう、決定的にします。
