# REUSE Lint Local Rehearsal

## Summary

- date: 2026-07-30
- command: `.\runtime\windows-script\uv.cmd tool run "reuse[charset-normalizer]" lint`
- tool: `reuse 6.2.0`
- result: `pass`
- purpose: OSS公開前に、REUSE Specification 3.3に対するSPDX metadata整備状況を予行確認する。

## GitHub Actions Workflow

- workflow: `.github/workflows/reuse-lint.yml`
- trigger: `workflow_dispatch`
- permissions: `contents: read`
- artifact: `ariadne-reuse-lint-results`
- output directory: `reuse-lint-output/`
- local artifact path: `.act-artifacts/reuse-lint-passed-20260730/`
- local rehearsal runner: `act`

このworkflowはGitHub Actions本番用です。ローカル予行でも同じworkflowと同じjobを `act` で実行します。
REUSE lintがfailした場合でも、結果artifactを保存してからjobをfailさせます。今回のローカル予行では、artifact保存を含めてjobはpassしました。

```powershell
act workflow_dispatch `
  -W .github/workflows/reuse-lint.yml `
  -j reuse-lint `
  -P ubuntu-latest=catthehacker/ubuntu:act-22.04 `
  --artifact-server-path .act-artifacts
```

## Result

REUSE lintはpassしました。
`LICENSES/AGPL-3.0-or-later.txt` と `REUSE.toml` を追加し、repository内fileのcopyright / license metadataを機械可読にしました。

## Key Findings

- missing license text: `0`
- invalid SPDX license expression: `0`
- copyright / licensing information missing: `0`
- files with copyright information: `1577 / 1577`
- files with license information: `1577 / 1577`
- read errors: `0`
- bad licenses: `0`
- deprecated licenses: `0`

## Interpretation

ScanCodeのローカル予行では明らかなlicense / copyright上の懸念は確認されませんでしたが、REUSE lintは別観点です。
REUSE lintのpassは、repository全体のSPDX metadataがREUSE Specification 3.3に対して機械可読になったことを示します。
初期対応では、大量fileに個別headerを追加せず、`REUSE.toml` でpath pattern単位に `AGPL-3.0-or-later` と `2026 ARIADNE contributors` を付与しました。

## Remaining Actions

- release前にGitHub Actions本番の `workflow_dispatch` で `.github/workflows/reuse-lint.yml` を実行し、artifactを確認する。

## Resolved Items

- `LICENSES/AGPL-3.0-or-later.txt` を追加した。
- `REUSE.toml` を追加し、repository全体の初期SPDX metadataをpath pattern単位で付与した。
- root `README.md` のSPDX tag風の説明表記を通常文へ変更し、REUSE lintのinvalid SPDX license expression 1件を解消した。

このファイルはreview evidenceであり、法的助言ではありません。
