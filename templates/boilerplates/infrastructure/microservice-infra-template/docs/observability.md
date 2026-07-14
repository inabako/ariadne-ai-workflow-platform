# Observability Guide

## Required Signals

- service / container status
- connection count
- error count
- restart count
- last communication time

## Health

health check は runtime の restart policy と連動できる形にします。
公開が必要な場合は、公開範囲と認証方式を security design に記録します。

## Metrics

metrics は internal network からの取得を基本にします。
外部公開が必要な場合は、reverse proxy、auth、CIDR 制限、TLS を設計します。

## Alerts

prod では alert hook を必須扱いにします。
webhook URL は secret source から注入し、Terraform file へ実値を書きません。
