# Kubernetes / k3s Dry-run Runbook

```powershell
aiwfctl iac kubernetes assess --work-id <work-id>
aiwfctl iac kubernetes gap-report --work-id <work-id>
aiwfctl iac kubernetes generate --work-id <work-id>
aiwfctl iac kubernetes dry-run --work-id <work-id>
aiwfctl iac kubernetes e2e-plan --work-id <work-id>
aiwfctl iac kubernetes evidence --work-id <work-id>
```

実際に kubectl の dry-run を実行する場合:

```powershell
aiwfctl iac kubernetes dry-run --work-id <work-id> --execute --human-check approved
```
