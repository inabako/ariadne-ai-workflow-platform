# Security Guide

## 原則

- public ports は最小化する
- internal service は直接公開しない
- SSH / admin access は CIDR 制限する
- health / metrics は原則 internal に閉じる
- secret は IaC repository に保存しない
- `.env` は生成しない

## Review Checklist

| Check | Status | Evidence |
| --- | --- | --- |
| port definition と IaC が一致している |  |  |
| public exposure に理由がある |  |  |
| admin CIDR が制限されている |  |  |
| health / metrics の公開範囲が妥当 |  |  |
| secret が placeholder または外部参照だけ |  |  |
| rollback 手順がある |  |  |

## 禁止事項

- real token / password / private key の commit
- `0.0.0.0/0` の安易な admin access
- application protocol 実装の IaC 混入
- target service 固有値を common module へ直書き
