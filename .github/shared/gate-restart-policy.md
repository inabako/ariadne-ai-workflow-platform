# Gate Restart Policy

この文書は、workflow gate で異常を検出したときの共通復帰ルールを定義します。

## Core Rule

workflow gate が `fail` または継続不能な `warning` を返した場合、workflow は次の工程へ進まず、失敗した同じ gate に留まります。

修復 runtime が存在する場合でも、修復は workflow 本線の代替工程ではありません。修復 runtime は失敗 gate の内側で実行される subroutine として扱い、修復後は必ず同じ gate を再実行します。

## Contract

gate restart を返す runtime は、結果 JSON に `gate_restart` を含めます。

```json
{
  "gate_restart": {
    "gate": "<failed-gate-name>",
    "restart_from": "<same-gate>",
    "restart_reason": "<why-restart-is-needed>",
    "repair_available": true,
    "repair_command": "<runtime command>",
    "status_after_restart": "<pass|warning|fail|unknown>",
    "next_on_pass": "return-to-calling-workflow-after-gate",
    "next_on_fail": "stay-at-gate"
  }
}
```

## Agent Rule

Agent は gate failure を検出したあと、下流工程へ飛ばしてはいけません。`repair_available` が `true` の場合は `repair_command` を使い、再実行後に同じ gate の `pass` を確認してから呼び出し元 workflow に戻ります。

足りない操作があれば直叩きを増やさず、Feedback に流し、runtime の正式入口を先に拡張します。
