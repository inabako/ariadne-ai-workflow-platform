# IaC Deployment Runtime

IaC を生成する前に、アプリが最終的にどう動くかを確認する共通 runtime です。

Kubernetes / k3s、Terraform、Docker Compose などの具体的な IaC は、要件定義や設計書だけを直接読んで確定しません。まず `Deployment Contract` を作り、実行単位、image、port、health、env / Secret、外部依存、storage、resource、起動停止、観測、E2E 対象を確認します。

## Flow

```text
Requirement / Design
  -> App Runtime Assessment
  -> Deployment Contract
  -> IaC Deployment Gap Report
  -> Provider-specific IaC
```

## Commands

迷わない入口として、通常は `iac prepare` から始めます。

```powershell
.\runtime\windows-script\aiwfctl.cmd iac prepare --work-id <work-id>
```

この command は、Deployment Contract を作成したうえで provider-specific IaC を検出し、Kubernetes / k3s 指定がある場合は manifest scaffold、dry-run evidence、integration E2E plan まで進めます。

```powershell
.\runtime\windows-script\aiwfctl.cmd iac deployment assess --work-id <work-id>
.\runtime\windows-script\aiwfctl.cmd iac deployment contract --work-id <work-id>
.\runtime\windows-script\aiwfctl.cmd iac deployment gap-report --work-id <work-id>
```

明示的に読み取り source を指定する場合:

```powershell
.\runtime\windows-script\aiwfctl.cmd iac deployment assess `
  --work-id <work-id> `
  --source work/<work-id>/requirements/requirement.md `
  --source work/<work-id>/design-document/design.md
```

## Artifacts

| Artifact | Location |
| --- | --- |
| App Runtime Assessment | `work/<work-id>/context/iac-app-runtime-assessment.json` |
| Deployment Contract | `work/<work-id>/context/iac-deployment-contract.json`, `.md` |
| Deployment Gap Report | `work/<work-id>/process-report/iac-deployment-gap-report.json`, `.md` |
| IaC Prepare Report | `work/<work-id>/process-report/iac-prepare-report.json`, `.md` |

## Rules

- IaC の最終化は Deployment Contract を入力にします。
- 要件や設計に不足がある場合は、値を推測せず gap report に残します。
- 秘密値は contract や manifest に直書きしません。Secret 名、参照名、責務境界だけを扱います。
- Kubernetes / k3s runtime は `iac-deployment-contract.json` があればそれを参照します。
