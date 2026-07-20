---
language: ja-JP
---

# Docker Template

この文書は、Docker を利用する application、service、development environmentの boilerplate に適用する規範を定義します。

対象には次を含みます。

* Dockerfile。
* Compose。
* development container。
* build image。
* runtime image。
* local integration environment。
* container test。

## 目的

* 再現可能な container build を提供する。
* build環境と runtime環境を分離する。
* secret を image へ含めない。
* 最小権限で process を実行する。
* health、shutdown、resource を扱えるようにする。
* local、CI、deployment で共通利用できる土台を作る。

## Dockerfile

### MUST

* base image version を固定する。
* 信頼できる official または approved image を使用する。
* unnecessary package を install しない。
* build cache と secret を適切に扱う。
* multi-stage build を必要に応じて利用する。
* runtime image へ build tool を不要に残さない。
* container 内 process を原則 non-root で実行する。
* application entrypoint を明確にする。
* `.dockerignore` を用意する。
* secret を `ARG`、`ENV`、layer へ埋め込まない。

### SHOULD

* image size を必要以上に増やさない。
* package cache を削除する。
* layer順序を build cache効率に合わせる。
* immutableな artifact を copy する。
* shell form より exec formの ENTRYPOINT を優先する。

## Base Image

### MUST

* lifecycle と security support を確認する。
* floating tagだけに依存しない。
* architecture compatibility を確認する。
* license と distribution条件を確認する。
* vulnerability scan を必要に応じて行う。

例:

```text
language-runtime:major.minor-patch
```

digest固定を採用する場合は更新方法を用意します。

## User and Permission

### MUST

* root権限が不要な application を root で実行しない。
* writable directory を限定する。
* file ownership を明示する。
* host socket を不用意に mount しない。
* privileged mode を default にしない。
* Linux capability を必要最小限にする。

## Configuration

### MUST

* environment 固有値を image へ build-in しない。
* configuration を runtime で注入する。
* secret を Compose file へ平文記載しない。
* required configuration を startup 時に validation する。
* local、test、productionの設定を区別する。

## Ports and Network

### MUST

* 必要な portだけを公開する。
* internal port と host port を区別する。
* public binding を default にしない。
* `0.0.0.0` への公開が必要か確認する。
* service間 network を明示する。
* container 名や IP を永続 contract にしない。

### SHOULD

* Compose network を用途別に分ける。
* internal service を external network へ公開しない。
* hostname は service discovery を利用する。

## Volumes

### MUST

* persistent data と temporary data を区別する。
* host path mount を最小化する。
* production data を development container へ mount しない。
* source mount と generated artifact mount を区別する。
* permission問題を考慮する。
* volume 削除が data deletion になることを明示する。

## Health Check

### MUST

* service として利用する container には、必要に応じて health check を用意する。
* process存在だけでなく ready状態を確認する。
* health check へ重大な side effect を持たせない。
* timeout、interval、retries を定義する。
* dependency の一時停止で不必要な restart loop を作らない。

## Shutdown

### MUST

* signal を application process へ伝播する。
* PID 1問題を考慮する。
* graceful shutdown を検証する。
* in-flight operation と resource cleanup を扱う。
* stop timeout を無制限にしない。

## Docker Compose

### MUST

* Compose fileの目的を明確にする。
* development、test、production を一つの file へ無理に統合しない。
* dependency startup順序だけに ready 判定を依存しない。
* secret を commit しない。
* destructive volume operation を明示する。
* external network や volumeの前提を README へ記載する。

### SHOULD

```text
compose.yml
compose.override.yml
compose.test.yml
```

など、用途に応じて分離します。

## Build Reproducibility

### MUST

* dependency version を固定する。
* build input を repository から追跡可能にする。
* network取得物を無検証で使用しない。
* build日時だけで artifact 内容が変わらないようにする。
* generated artifactの source revision を記録する。

## Security

### MUST

* secret を image history へ残さない。
* Docker socket を mount しないことを基本とする。
* privileged container を利用しない。
* read-only filesystem を可能な範囲で検討する。
* unnecessary capability を drop する。
* remote image を無条件に信頼しない。
* vulnerability scan failure を無断で無視しない。

## Testing

### MUST

template では次を検証します。

* image build。
* container startup。
* health check。
* non-root execution。
* required configuration failure。
* graceful shutdown。
* exposed port。
* secret absence。
* Compose startup。
* cleanup。

## Generated Files

Docker template は必要に応じて次を生成します。

```text
Dockerfile
.dockerignore
compose.yml
compose.test.yml
docker/
 entrypoint.sh
docs/
 docker.md
```

entrypoint script には、文字コード、改行コード、実行権限を考慮します。

## AI Agent 向け規範

AI Agent は Docker構成変更時に次を確認します。

1. base image。
2. version。
3. user。
4. secret。
5. port。
6. volume。
7. signal。
8. health。
9. resource。
10. scan。
11. multi-platform。
12. development と productionの差異。

## まとめ

* Docker template は再現可能な build と安全な runtime を提供する。
* root、secret、public port、privileged mode を安全でない default にしない。
* build image と runtime image を分離する。
* health、signal、shutdown を検証する。
* Compose は用途と environmentごとに責務を明確にする。
