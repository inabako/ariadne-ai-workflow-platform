# Legal Review Items

## Summary

ARIADNEの公開license方針は `AGPL-3.0-or-later` です。公開前に、著作権者、公開URL、初回release日、GitHub Security Advisories方針、third-party dependency licenseを確認します。

## License Status

- `LICENSE`: GNU Affero General Public License Version 3本文。
- `runtime/pyproject.toml`: `AGPL-3.0-or-later`。
- `CITATION.cff`: `AGPL-3.0-or-later`。
- READMEとlegal docs: `AGPL-3.0-or-later` 方針。

## Required Review

- `CITATION.cff` のproject author nameを確認する。
- public repository URLを確認する。
- first public release dateを確認する。
- security contactとしてGitHub Security Advisoriesを使用する方針を確認する。
- third-party dependency license reviewを完了する。
- GitHub Actions本番でREUSE lint workflowを実行し、artifactを確認する。
- trademarkとlogo usage policyを確認する。

## ScanCode Local Rehearsal Review

- ScanCodeのローカル予行は完了。
- 人間レビューの結果、明らかなlicense / copyright上の懸念は確認されなかった。
- 公開前に、GitHub Actions本番の `workflow_dispatch` 実行結果で最終確認する。

## REUSE Lint Local Rehearsal Review

- REUSE lintのローカル予行は完了。
- 結果はpass。
- `LICENSES/AGPL-3.0-or-later.txt` と `REUSE.toml` により、repository内fileのSPDX metadataを機械可読にした。
- `bad licenses`、`deprecated licenses`、`missing licenses`、`read errors`、`invalid SPDX license expressions` は `0`。
- copyright / license informationは `1577 / 1577`。
- 詳細は [reuse-lint-local-rehearsal.md](reuse-lint-local-rehearsal.md) に記録する。

このファイルはreview scaffoldであり、法的助言ではありません。
