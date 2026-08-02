# OSS Release Audit Map

この文書は、OSS releaseや継続運用時に行うlicense / security / dependency auditと、その証跡がどこへ集約されるかを図で示します。

詳細は `docs/legal/README.md`、`docs/release/release-checklist.md`、`docs/security/scancode-github-actions.md`、`.github/workflows/` を優先します。

## 全体像

```mermaid
flowchart TD
  Source[Repository source] --> ReleaseValidate[aiwfctl release validate]
  Source --> Reuse[REUSE lint]
  Source --> ScanCode[ScanCode Toolkit]
  Source --> DependencyReview[Dependency Review]
  Source --> WorkflowAudit[actionlint / yamllint / local rehearsal]
  Source --> SecretReview[Secret / private info review]

  ReleaseValidate --> ReleaseEvidence[docs/legal/evidence/release-license-check.json]
  Reuse --> ReuseEvidence[docs/legal/evidence/reuse-lint-local-rehearsal.md]
  ScanCode --> ScanCodeArtifact[GitHub Actions artifact scancode-output]
  ScanCodeArtifact --> LegalReport[docs/legal/evidence/dependency-license-report.json]
  DependencyReview --> DependencyEvidence[docs/legal/evidence/dependency-review-github-actions.md]
  WorkflowAudit --> WorkflowEvidence[docs/legal/evidence/workflows-public-readiness-local-rehearsal.md]
  SecretReview --> LegalItems[docs/legal/evidence/legal-review-items.md]

  ReleaseEvidence --> HumanReleaseGate{Release Human Gate}
  ReuseEvidence --> HumanReleaseGate
  LegalReport --> HumanReleaseGate
  DependencyEvidence --> HumanReleaseGate
  WorkflowEvidence --> HumanReleaseGate
  LegalItems --> HumanReleaseGate

  HumanReleaseGate -- blocked --> Fix[Fix docs / metadata / config]
  Fix --> Source
  HumanReleaseGate -- approved --> Release[GitHub Release / tag]
```

## Audit sources

| Audit | 主な入口 | 主な確認内容 | 主な証跡 |
| --- | --- | --- | --- |
| Release validation | `aiwfctl release validate --json` | license方針、release readiness、metadata整合 | `release-license-check.json`、release manifest |
| REUSE lint | local rehearsal / `.github/workflows/reuse-lint.yml` | SPDX metadata、license file、copyright |
| ScanCode | `.github/workflows/scancode.yml` | repository内license / copyright検出 |
| Dependency Review | `.github/workflows/dependency-review.yml` | PR差分dependencyのlicense policy / vulnerability |
| Workflow audit | `actionlint`, `yamllint`, local rehearsal | GitHub Actions構文、workflow_dispatch、設定整合 |
| Human legal review | `docs/legal/evidence/legal-review-items.md` | GitHub Security Advisories、連絡先、公開URL、copyright holder |
| Secret review | release checklist / manual review | token、private URL、顧客固有情報、非公開project情報 |

## GitHub Actions audit

```mermaid
flowchart TD
  PR[Pull Request] --> DependencyReview[dependency-review.yml]
  DependencyReview --> DepResult{license / vulnerability ok?}
  DepResult -- no --> PRBlocked[PR blocked / exception review]
  DepResult -- yes --> PRContinue[PR can proceed]

  Manual[workflow_dispatch] --> Reuse[reuse-lint.yml]
  Manual --> ScanCode[scancode.yml]
  Reuse --> ReuseResult[REUSE result]
  ScanCode --> ScanCodeResult[scancode-results.json/html]
  ScanCodeResult --> HumanReview[Human license review]
  HumanReview --> EvidenceUpdate[Update docs/legal/evidence]
```

Dependency ReviewはPR差分の監査です。
ScanCodeとREUSE lintはrelease前または継続監査として手動実行し、結果を人間が確認してevidenceへ反映します。

## Legal evidence flow

```mermaid
flowchart TD
  Policy[docs/legal policy docs] --> Evidence[docs/legal/evidence]
  Evidence --> ReleaseChecklist[docs/release/release-checklist.md]
  ReleaseChecklist --> ReleaseValidate[aiwfctl release validate]
  ReleaseValidate --> Decision{Release ready?}
  Decision -- no --> Remediation[Fix metadata / docs / config]
  Decision -- yes --> ReleaseNote[Release note / tag / GitHub Release]

  Evidence --> SecurityContact[GitHub Security Advisories]
  Evidence --> Discussions[Discussions for bugs / questions / proposals]
```

Policy documentは方針を説明する文書です。
`docs/legal/evidence/` は、あるrelease candidateや継続監査時点の確認状態を残す場所です。

## Contact and vulnerability handling

```mermaid
flowchart TD
  UserReport[Bug / question / proposal] --> Discussions[GitHub Discussions]
  SecurityReport[Security / vulnerability] --> SecurityAdvisory[GitHub Security Advisories]
  SecurityAdvisory --> Triage[Private triage]
  Triage --> Fix[Fix / coordinated disclosure]
  Fix --> Release[Security release / advisory publication]
```

一般のバグ報告・質問・提案は Discussions で受けます。
セキュリティ・脆弱性連絡は GitHub Security Advisories で受け、公開Issueで詳細を扱いません。

## Release gate

```mermaid
flowchart TD
  Candidate[Release candidate] --> SourceChecks[Source / tests / docs checks]
  SourceChecks --> AuditChecks[License / security / dependency checks]
  AuditChecks --> EvidenceReady{Evidence complete?}
  EvidenceReady -- no --> Block[Block release]
  Block --> Fix[Fix and rerun]
  Fix --> Candidate
  EvidenceReady -- yes --> HumanDecision[Human release decision]
  HumanDecision --> Tag[Git tag]
  Tag --> GitHubRelease[GitHub Release]
  GitHubRelease --> PostRelease[Post-release verification]
```

Release Gateは、CIが通ったことだけではなく、release checklist、legal evidence、security contact、dependency/license audit、documentationが揃っていることを確認します。
