# 第三者ライセンス

third-party dependency reviewは次で追跡します。

- [evidence/dependency-license-report.json](evidence/dependency-license-report.json)
- [runtime/pyproject.toml](../../runtime/pyproject.toml) のruntime package metadata
- [ScanCode GitHub Actions](../security/scancode-github-actions.md) のartifact

## 現在のRuntime Dependency

runtime packageは現在、次を宣言しています。

- `duckdb>=1.1`
- `langgraph>=1.2.9`

各release前に、dependency licenseを `AGPL-3.0-or-later` およびrelease distribution modelと照合してreviewする必要があります。

## Review Status

現在のreportはscaffoldです。完全なdependency license auditの代替ではありません。

ScanCode Toolkitの結果はlicense auditの入力です。検出結果だけでcompatibilityや配布可否を自動確定せず、release前またはdependency変更時に人間reviewで確認します。
