# test_oss_release_foundation.py

このファイルは `runtime/tests/test_oss_release_foundation.py` の pytest node id 単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 14 |

## ケース一覧

#### RT-UT-CASE-018H

- pytest node id:

```text
runtime/tests/test_oss_release_foundation.py::test_oss_release_foundation_files_exist
```

- Confirm: OSS公開に必要な release foundation file が揃っていることを確認します。
- Input:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_oss_release_foundation.py:24`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: `required`
- Expected: OSS release、legal、documentation、GitHub、runtime release に関する必須fileの不足がありません。

#### RT-UT-CASE-AUTO-001

- pytest node id:

```text
runtime/tests/test_oss_release_foundation.py::test_gitattributes_documents_line_ending_policy
```

- Confirm: `.gitattributes` が改行コード方針を明示し、text / Windows command / binary artifact の扱いを固定していることを確認します。
- Input:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_oss_release_foundation.py:76`
  - fixture/arg: none
  - parameter: names=none case=none
  - inline input: `text`
- Expected: LF正規化、Windows commandのCRLF維持、binary artifactの非text化、改行正規化を別review単位にする説明が `.gitattributes` に含まれます。

#### RT-UT-CASE-AUTO-002

- pytest node id:

```text
runtime/tests/test_oss_release_foundation.py::test_github_copilot_bridge_files_point_to_ariadne_source_of_truth
```

- Confirm: `.github` 配下の Copilot bridge が `.ariadne` を source of truth として案内し、workflow本体と誤認されないことを確認します。
- Input:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_oss_release_foundation.py:86`
  - fixture/arg: none
  - parameter: names=none case=none
  - inline input: `copilot`, `prompt`
- Expected: `.github/copilot-instructions.md` と `.github/prompts/ariadne-workflows.prompt.md` が薄いbridgeであること、`.ariadne/prompts/` と `.ariadne/agents/` を参照することを明示します。

#### RT-UT-CASE-018I

- pytest node id:

```text
runtime/tests/test_oss_release_foundation.py::test_ariadne_assets_do_not_point_to_legacy_github_ai_asset_paths
```

- Confirm: `.ariadne` asset が legacy `.github` AI asset path を参照していないことを確認します。
- Input:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_oss_release_foundation.py:75`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: `forbidden`, `offenders`, `text`
- Expected: `.ariadne` 配下の Markdown / JSON asset に禁止された legacy path reference が含まれません。

#### RT-UT-CASE-018J

- pytest node id:

```text
runtime/tests/test_oss_release_foundation.py::test_validate_release_reports_current_repo_as_pass_with_warnings
```

- Confirm: Release validation が current repository に error を出さず、obsolete license-policy human review warning を要求しないことを確認します。
- Input:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_oss_release_foundation.py:98`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: test-local fixtures and assertions
- Expected: release validation error は空で、license policy human review warning は含まれません。

#### RT-UT-CASE-018K

- pytest node id:

```text
runtime/tests/test_oss_release_foundation.py::test_scancode_workflow_is_manual_only_and_read_only
```

- Confirm: ScanCode GitHub Actions workflow が manual-only、read-only、version pinned、artifact upload 付きであることを確認します。
- Input:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_oss_release_foundation.py:107`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: `text`
- Expected: workflow metadata、permission、ScanCode version、report output、artifact retention が release-audit contract と一致します。

#### RT-UT-CASE-018L

- pytest node id:

```text
runtime/tests/test_oss_release_foundation.py::test_reuse_lint_workflow_is_manual_only_read_only_and_uploads_evidence
```

- Confirm: REUSE lint workflow が manual-only、read-only、version pinned、evidence upload 付きであることを確認します。
- Input:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_oss_release_foundation.py:138`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: `text`
- Expected: workflow command、summary、artifact upload、retention、failure step が release-audit contract と一致します。

#### RT-UT-CASE-018M

- pytest node id:

```text
runtime/tests/test_oss_release_foundation.py::test_reuse_metadata_scaffold_covers_repository_files
```

- Confirm: REUSE metadata scaffold が AGPL-3.0-or-later policy のもとで repository file を対象にしていることを確認します。
- Input:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_oss_release_foundation.py:165`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: `reuse_toml`, `license_text`
- Expected: `REUSE.toml` に copyright と license metadata があり、AGPL license text が存在します。

#### RT-UT-CASE-018N

- pytest node id:

```text
runtime/tests/test_oss_release_foundation.py::test_license_audit_local_outputs_are_ignored
```

- Confirm: local license-audit output directory が Git 管理対象外になっていることを確認します。
- Input:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_oss_release_foundation.py:180`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: `gitignore`
- Expected: ScanCode、REUSE lint、act artifact output directory が `.gitignore` に含まれます。

#### RT-UT-CASE-018O

- pytest node id:

```text
runtime/tests/test_oss_release_foundation.py::test_vscode_tasks_include_license_audit_act_rehearsals
```

- Confirm: VS Code task に ScanCode と REUSE lint の local act rehearsal が含まれることを確認します。
- Input:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_oss_release_foundation.py:189`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: `tasks`
- Expected: list / rehearsal task が期待する workflow file、platform image、job name、artifact path、workspace cwd で `act` を呼び出します。

#### RT-UT-CASE-018P

- pytest node id:

```text
runtime/tests/test_oss_release_foundation.py::test_validate_release_cli_json_output
```

- Confirm: `aiwfctl release validate --json` が pass の machine-readable release validation result を返すことを確認します。
- Input:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_oss_release_foundation.py:258`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: `payload`
- Expected: CLI が成功終了し、JSON status は `pass` で、obsolete license-policy warning は含まれません。

#### RT-UT-CASE-018Q

- pytest node id:

```text
runtime/tests/test_oss_release_foundation.py::test_release_manifest_contains_stable_required_fields
```

- Confirm: Release manifest generation が安定した必須fieldとdocumentation referenceを含むことを確認します。
- Input:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_oss_release_foundation.py:283`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: test-local fixtures and assertions
- Expected: manifest に project name、version、tag、AGPL license、fixed timestamp、artifact hash、documentation list が含まれます。

#### RT-UT-CASE-018R

- pytest node id:

```text
runtime/tests/test_oss_release_foundation.py::test_release_manifest_is_reproducible_with_fixed_timestamp
```

- Confirm: timestamp と input が固定されている場合、Release manifest generation が再現可能であることを確認します。
- Input:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_oss_release_foundation.py:298`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: test-local fixtures and assertions
- Expected: 同一inputから生成された2つの manifest が一致します。

#### RT-UT-CASE-018S

- pytest node id:

```text
runtime/tests/test_oss_release_foundation.py::test_release_runtime_modules_are_executable
```

- Confirm: Release validation / manifest module が script loading で実行可能であることを確認します。
- Input:
  - pytest node: 上記 node id
  - source: `runtime/tests/test_oss_release_foundation.py:307`
  - fixture/arg: なし
  - parameter: names=なし case=なし
  - inline input: test-local fixtures and assertions
- Expected: runtime release module が `runpy` 実行時に parser entrypoint を公開します。
