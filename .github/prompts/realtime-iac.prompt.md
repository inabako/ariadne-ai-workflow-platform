# Realtime IaC Workflow

## Output Language

既定では日本語で応答し、人間向けreport、document、review、evidence、RAG source Markdownは `.github/shared/output-language-policy.md` に従って日本語で作成してください。

## Purpose

リアルタイムシステム向けの Infrastructure as Code を、要件整理、設計、生成、レビュー、Docker Desktop検証、Linux検証、統合試験、ドキュメント化まで一貫して進めるための flow です。

対象:

- ariadne
- IoT system
- edge AI
- video streaming system
- realtime gateway
- remote operation system
- distributed control system

この flow は、アプリケーションとインフラの責務を分け、共有成果物を single source of truth として扱います。

## Entry Conditions

- 完成版要件定義書が `work/requirements/` に1件だけ存在する
- 要件定義書に `Repository Control` が含まれる
- IaC対象のrepository mode、repository名、branchが明確である
- IaC対象基盤に入れるsoftware inventoryが明確である
- IaC対象が Docker Compose、systemd、firewall、reverse proxy、TURN/STUN、logrotate、monitoring、runtime environment のいずれかを含む

## Phase 0: Pre-development Preparation

開発本体に入る前に `/pre-development-preparation` を実行します。

確認:

- repository mode を判定した
- software inventoryを確認した
- existing repository modeの場合、GitHubから対象repository / target branch を取得した
- precreated-new repository modeの場合、GitHubサイト側で作成済みの `owner/repository`、initial branch、visibility、push承認gateを確認した
- 要件定義書とrepository stateまたはnew repository planを比較した
- existing repository modeの場合、IaC scope、acceptance criteria、test evidence planをGitHub Issueへ記載し、Issue番号から `feature/issue-<issue-number>` branch を作成した
- precreated-new repository modeの場合、この時点ではIssue branchを作らない。IaC生成、初回push、GitHub Issue作成、Issue branch作成の順で進める
- `work/<receipt-id>/context/scm-state.json` にbranch情報が記録されている
- `/rag-load` を実行し、過去の corrective action report から関連する deployment / startup / network / security / observability / evidence gap を読み込んだ
- 必要な場合、Specialist Agent reviewを実行し、専門前提と採用した外部知識を `work/<receipt-id>/process-report/` に記録した

この準備が未完了の場合、IaC設計や生成へ進みません。

### Repository Mode

Existing repository mode:

```text
prepare existing repository
  -> compare requirements
  -> create [IaC] GitHub Issue
  -> create feature/issue-<issue-number>
  -> implement and validate
  -> push issue branch
  -> Pull Request
```

Precreated new repository mode:

```text
confirm precreated owner/repository and initial branch
  -> confirm repository exists on GitHub
  -> generate IaC under work/<receipt-id>/source/repository/
  -> initial commit and initial branch push
  -> create [IaC] GitHub Issue in the new repository
  -> create feature/issue-<issue-number>
  -> continue validation and issue-branch work
  -> push issue branch
  -> Pull Request
```

For precreated-new repository mode, the workflow must not create `feature/issue-<issue-number>` before the initial branch has been pushed. The GitHub repository itself is created by the human before the workflow starts.

## Phase 1: Shared Artifact Gate

設計前に共有成果物とsoftware inventoryを確認します。

必須:

- communication specification
- port definition list
- network boundary definition
- software inventory

推奨:

- protocol definition
- public / private network policy
- system architecture diagram
- architecture decision records

Quality Gate:

- 必須成果物が不足している場合は workflow を停止する
- software inventoryが不足している場合は workflow を停止する
- `work/<receipt-id>/design-document/open-questions.md` を作成する
- 不足項目、必要な追加成果物、人間レビュー依頼を記録する
- AIは software component、port番号、通信経路、公開範囲、責務境界を推測で補完しない

software inventoryで確認すること:

- software name
- purpose
- owner / responsibility boundary
- version or version policy
- runtime unit, such as container, systemd service, host package, proxy, sidecar, or monitoring job
- required ports / protocols
- required environment variables and secret placeholders
- persistence / volume needs
- health check method
- license or distribution constraint when relevant

要件定義書に同等の構造が無い場合は、次のテンプレートを使って不足項目を洗い出す。

```text
templates/iac/software-inventory-template.md
templates/iac/communication-specification-template.md
```

## Phase 2: Requirements Organization

インフラ要件を整理します。

出力:

- `requirements.md`
- `open-questions.md`

確認すること:

- runtime target
- host OS / container runtime
- required services
- software inventory
- inbound / outbound communication
- port and protocol list
- public / private exposure
- dependency and startup order
- secrets and configuration source
- validation environments

## Phase 3: Network / Security Design

network と security を設計します。

出力:

- `network-design.md`
- `security-design.md`
- `firewall-policy.md`

確認すること:

- UDP / TCP port ownership
- firewall rules
- route and NAT assumptions
- TLS certificate handling
- authentication / authorization boundary
- TURN / STUN / reverse proxy use
- secret storage and rotation
- public exposure justification

Quality Gate:

- public exposure is justified and minimized
- secrets are placeholders only
- `.env` is not generated
- `.env.example` contains placeholders and comments only
- firewall policy matches the shared port definition list

## Phase 4: Runtime Design

runtime を設計します。

出力:

- `runtime-design.md`
- `docker-compose-design.md`

確認すること:

- Docker Compose service model
- systemd units
- environment variables
- startup order
- restart policy
- graceful shutdown
- health checks
- host volume and permission policy
- rollback unit

## Phase 5: Observability Design

可観測性を設計します。

出力:

- `observability-design.md`
- `monitoring-policy.md`

確認すること:

- logs
- log rotation
- metrics
- health endpoint or command
- alert triggers
- incident evidence location
- operator-visible degradation state

## Phase 5.5: Boilerplate Template Selection

IaC実装前に、承認済みdesignとshared artifactsに対して利用可能なboilerplate templateを確認します。

候補:

| 対象 | Template | 組み込み指示書 |
| --- | --- | --- |
| Realtime gateway IaC / infrastructure | `templates/boilerplates/realtime-gateway-infra-template/` | `realtime-gateway-infra-template_実装指示書.md` |
| Development / CI/CD / observability platform infrastructure | `templates/boilerplates/platform-infra-template/` | `Platform_Infrastructure_Boilerplate_追加実装指示書.md` |
| PostgreSQL / MySQL shared database infrastructure | `templates/boilerplates/database-infra-template/` | `Database_Infrastructure_Boilerplate_追加実装指示書.md` |
| Redis shared middleware infrastructure | `templates/boilerplates/middleware-infra-template/` | `Redis _OpenLDAP_Infrastructure_Boilerplate_追加実装指示書.md` |
| OpenLDAP identity / directory infrastructure | `templates/boilerplates/identity-infra-template/` | `Redis _OpenLDAP_Infrastructure_Boilerplate_追加実装指示書.md` |

出力:

- `work/<receipt-id>/process-report/boilerplate-template-selection.md`

判定:

- realtime gateway infrastructure が対象に含まれ、`realtime-gateway-infra-template/` が存在する場合は、templateをコピーしてコピー先だけを編集する。
- 開発・CI/CD・監視platformが対象に含まれ、`platform-infra-template/` が存在する場合は、templateをコピーしてコピー先だけを編集する。
- PostgreSQL / MySQL shared database infrastructure が対象に含まれ、`database-infra-template/` が存在する場合は、templateをコピーしてコピー先だけを編集する。
- Redis shared middleware infrastructure が対象に含まれ、`middleware-infra-template/` が存在する場合は、templateをコピーしてコピー先だけを編集する。
- OpenLDAP identity / directory infrastructure が対象に含まれ、`identity-infra-template/` が存在する場合は、templateをコピーしてコピー先だけを編集する。
- templateが対象に合わない場合は、`decision: traditional-coding` と理由を記録し、従来どおりIaCを生成する。
- template本体は直接編集しない。
- `.env`、real secret、production password、private keyは生成しない。
- shared artifacts、software inventory、public exposure、secret source、firewall policy、rollback、test case table、evidence planを省略しない。

Quality Gate:

- boilerplate template selection resultが記録されていない場合、IaC Implementationへ進まない。

## Phase 6: IaC Implementation

承認された設計をもとに IaC artifacts を生成します。

対象:

- `docker-compose.yml`
- `.env.example`
- systemd unit
- reverse proxy configuration
- TURN / STUN configuration
- logrotate configuration
- monitoring configuration
- README / setup docs

原則:

- unrelated refactor を混ぜない
- application logic を変更しない
- secret を生成しない
- `.env` を生成しない
- 本番値は placeholder にする
- design decision を process report に記録する

Precreated-new repository modeでは、このphaseの出力を `work/<receipt-id>/source/repository/` に配置し、初回push可能なrepository rootとして整えます。

## Phase 6.5: Precreated New Repository Bootstrap

precreated-new repository modeの場合だけ実行します。

出力:

- `bootstrap-repository-<timestamp>.json`
- initial branch on GitHub
- `[IaC]` GitHub Issue
- `feature/issue-<issue-number>` branch

順序:

1. Human approval を得る。
2. GitHubサイト側で作成済みのrepositoryが指定先と一致することを確認する。
3. `runtime/scm/bootstrap_repository.py --push --human-check approved` で初回commitとinitial branch pushを行う。
4. `runtime/github/issue_manager.py --flow-label iac --create` で新repositoryにIssueを作成する。
5. `runtime/scm/create_issue_branch.py --link-to-issue` でIssue branchを作成する。

Stop conditions:

- planned repository name is missing
- repository does not exist on GitHub
- software inventory is missing
- human approval is missing
- initial branch push failed
- Issue creation failed

## Phase 7: Security Review

生成された IaC をレビューします。

出力:

- `security-review.md`

確認すること:

- unnecessary public ports
- secret leakage
- excessive privileges
- TLS configuration
- firewall consistency
- environment variable management
- container privilege / volume exposure
- authentication / authorization boundary

High / critical finding がある場合、Phase 3 または Phase 6 へ戻します。

## Phase 8: Docker Desktop Validation

Desktop Docker 上で IaC を検証します。

出力:

- `docker-test-plan.md`
- `docker-test-result.md`
- `evidence/`

確認すること:

- `docker compose config`
- container startup
- health check
- environment variable loading
- port binding
- log output
- restart policy
- network isolation
- UDP communication when applicable

Docker Desktopで検証できない項目は、Linux runtime validation または human check に明示的に残します。

## Phase 9: Linux Runtime Validation

Linux実行環境で OS 依存機能を検証します。

出力:

- `runtime-validation.md`

確認すること:

- systemd unit validation
- firewall validation
- logrotate validation
- service restart
- health check
- host permissions

Hostへのinstallや設定変更が必要な場合は、人間承認を得るまで実行しません。

## Phase 10: Integration Validation

システム全体の疎通試験を行います。

出力:

- `integration-test.md`
- `evidence/`

確認すること:

- control communication
- video communication
- telemetry communication
- gateway communication
- degraded / recovery behavior
- restart / reconnect behavior

## Phase 11: Documentation

運用に必要なdocsを作成または更新します。

出力:

- README
- setup guide
- operation guide
- troubleshooting guide
- architecture notes
- network overview

## Test Case And Evidence Storage

Before validation, create:

```text
docs/evidence/issue-<issue-number>/test_specifications/iac-test-cases.md
```

Evidence:

```text
docs/evidence/issue-<issue-number>/integration/docker-desktop/
docs/evidence/issue-<issue-number>/integration/linux-runtime/
docs/evidence/issue-<issue-number>/integration/iac-integration/
docs/evidence/issue-<issue-number>/human_check/
```

Push is blocked until required test cases and evidence exist, or skip reasons and residual risks are recorded.

## Exit Conditions

- AI workflow is defined
- agent responsibilities are separated
- precreated-new repository modeの場合、initial branch and issue branch are pushed or explicit block reason exists
- Docker Desktop validation is possible or explicit skip reasons exist
- Linux runtime validation is possible or explicit skip reasons exist
- integration test is executable or blocked with named missing artifacts
- documentation is prepared
- evidence capture method is defined
- generated artifacts are reviewable by humans
- `work/<receipt-id>/context/artifact-index.json` can point to all major artifacts
