# ScanCode GitHub Actions

この文書は、ARIADNEのrelease前および継続運用で実行するScanCode Toolkit license auditの運用手順を記録します。

ScanCodeの検出結果は、release時のlicense review evidenceです。検出結果だけで法的判断を自動確定しません。Unknown license、複数license候補、出所不明file、ARIADNEと無関係なcopyright holder、package metadataの不足は、人間reviewerが確認します。

## 目的

`.github/workflows/scancode.yml` は、ARIADNE自身のrepositoryを対象に、次を検出します。

- license
- copyright
- package metadata
- system package database

このworkflowはGitHub Actions本番用です。ローカル予行も同じworkflowと同じjobを `act` で実行します。ローカル専用workflow、簡易scan、代替scriptは作成しません。

## 固定バージョン

| Item | Version |
| --- | --- |
| ScanCode Toolkit | `32.5.0` |
| Python | `3.12` |
| Checkout action | `actions/checkout@v4` |
| Setup Python action | `actions/setup-python@v5` |
| Upload Artifact action | `actions/upload-artifact@v4` |
| act runner image | `catthehacker/ubuntu:act-22.04` |

ScanCode CLI optionは、固定したScanCode Toolkit versionの公式CLI仕様に基づいて運用します。

## 起動条件

初期導入時点では、意図しない長時間実行を避けるため、起動条件は手動実行だけです。

```yaml
on:
  workflow_dispatch:
```

Pull Requestや`main` pushでの自動実行は、GitHub-hosted runnerでの初回確認と実行時間の評価後に追加します。

## 権限

workflow権限は読み取りに限定します。

```yaml
permissions:
  contents: read
```

ScanCode実行とartifact保存だけを行うため、`contents: write`、`issues: write`、`pull-requests: write`、`packages: write`、`actions: write` は付与しません。

## スキャン対象

対象はARIADNE repositoryの公開対象です。

```text
.
```

次は公開対象外、生成物、一時領域、local cache、巨大なread modelとして除外します。

| Pattern | Reason |
| --- | --- |
| `.git/**` | Git履歴全体は公開source treeのscan対象ではない |
| `work/**` | local workflow workspaceであり公開対象外 |
| `tmp/**`, `temp/**` | 一時領域 |
| `logs/**`, `reports/**`, `artifacts/**` | local/generated evidence置き場 |
| `coverage/**`, `dist/**`, `build/**` | generated output |
| `__pycache__/**`, `.pytest_cache/**` | local cache |
| `.venv/**`, `venv/**`, `runtime/.venv/**` | local virtual environment |
| `node_modules/**` | vendored dependency cache |
| `db/**/*.duckdb` | generated DuckDB read model |
| `scancode-output/**` | ScanCode自身の出力先 |

除外設定は「速くするため」だけではなく、OSS公開対象ではないことを理由にします。公開対象外情報は、workflow除外だけに頼らず、repositoryへ混入させないことを優先します。

## 実行コマンド

workflowは次の検出optionと出力形式を使用します。

```bash
scancode \
  --license \
  --copyright \
  --package \
  --system-package \
  --strip-root \
  --json-pp scancode-output/scancode-results.json \
  --html scancode-output/scancode-results.html \
  .
```

実際のworkflowでは、上記に除外patternを加えて実行します。

JSONを正式な監査成果物とし、HTMLは人間確認用の補助成果物とします。

## 出力

workflowは次を生成します。

```text
scancode-output/
├─ scancode-results.json
├─ scancode-results.html
├─ scancode-summary.md
└─ execution-metadata.json
```

`execution-metadata.json` には、repository、scanner、scanner version、workflow path、job、target、local simulationかどうかを記録します。

`scancode-summary.md` には、scan対象resource数、license detection数、copyright detection数、package detection数を記録します。

## Artifact

GitHub Actionsでは、scan結果をartifactとして保存します。

```yaml
uses: actions/upload-artifact@v4
with:
  name: ariadne-scancode-results
  path: scancode-output/
  if-no-files-found: error
  retention-days: 30
```

ScanCodeが失敗した場合でも、`if: always()` により生成済みoutputの保存を試みます。ただし、artifactにsecret、private URL、customer data、公開対象外情報が含まれないことを確認してください。

## ローカル予行

ローカル予行では、GitHub Actions本番用workflowをそのまま `act` で実行します。

## Provisioning / Preflight

ローカル予行に必要な `act` と Docker daemon は、Ariadne runtimeのpreflightにoptional capabilityとして組み込みます。
未導入または未起動の場合は `Missing Optional` として警告し、GitHub Actions本番での手動実行はブロックしません。

```powershell
.\runtime\windows-script\aiwf.cmd preflight --profile scancode-audit
```

`vscode-environment` profileでも、VS Code taskからScanCode workflowを予行できるように、`act` と Docker daemonをoptional checkします。

事前確認:

```powershell
act --version
docker info
act workflow_dispatch --list `
  -W .github/workflows/scancode.yml `
  -P ubuntu-latest=catthehacker/ubuntu:act-22.04
```

job実行:

```powershell
act workflow_dispatch `
  -W .github/workflows/scancode.yml `
  -j scancode `
  -P ubuntu-latest=catthehacker/ubuntu:act-22.04 `
  --artifact-server-path .act-artifacts
```

詳細ログ:

```powershell
act workflow_dispatch `
  -W .github/workflows/scancode.yml `
  -j scancode `
  -P ubuntu-latest=catthehacker/ubuntu:act-22.04 `
  --artifact-server-path .act-artifacts `
  --verbose
```

`--artifact-server-path` は、`actions/upload-artifact@v4` を `act` で検証するために指定します。生成される `.act-artifacts/` はlocal rehearsal artifactであり、git管理対象外です。

VS Codeから実行する場合は、次のtaskを使用します。

| Task | Purpose |
| --- | --- |
| `ARIADNE: List ScanCode GitHub Actions Jobs` | `act` がScanCode workflowとjobを認識するか確認する |
| `ARIADNE: Rehearse ScanCode Workflow` | `workflow_dispatch` で `scancode` jobをローカル予行する |

`act` はGitHub-hosted runnerの完全な複製ではありません。ローカル成功だけで導入完了と判断せず、GitHub Actions本番で `workflow_dispatch` を実行して確認します。

## GitHub Actions本番確認

初回本番確認では、GitHub repositoryのActions tabから `ScanCode License Audit` を手動実行します。

確認項目:

- `ubuntu-latest` runnerで起動する。
- ScanCode Toolkit versionが `32.5.0` である。
- JSONとHTMLが生成される。
- `ariadne-scancode-results` artifactをdownloadできる。
- 実行時間とresource使用量が許容範囲である。
- 追加secretやwrite permissionを必要としない。

## 人間review

ScanCode結果は、次の観点で人間が確認します。

- Unknown license。
- 複数license候補。
- license表記なしの公開対象file。
- ARIADNEと無関係なcopyright holder。
- 外部由来と思われるsource。
- AGPL方針と互換性を確認すべきlicense。
- binaryまたはgenerated output。
- 出所不明file。

確認結果は、必要に応じて [Third-Party Licenses](../legal/third-party-licenses.md) と [Legal Evidence Index](../legal/README.md#release-evidence) に反映します。

## Legal Evidenceへの反映

ScanCode artifactそのものは、実行ごとの監査成果物としてGitHub Actions artifactに保存します。repositoryには直接commitしません。

人間review後、確認済みのdependency license、未解決項目、追加NOTICEが必要な項目だけを次へ反映します。

- [Dependency License Report](../legal/evidence/dependency-license-report.json)
- [Legal Review Items](../legal/evidence/legal-review-items.md)
- [Third-Party Licenses](../legal/third-party-licenses.md)
