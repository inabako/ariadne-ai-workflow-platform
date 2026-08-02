# test_github_knowledge_maintenance.py

このファイルは `runtime/tests/test_github_knowledge_maintenance.py` のpytest node id単位UT仕様です。

| 項目 | 値 |
| --- | ---: |
| cases | 50 |

## ケース一覧

#### RT-UT-CASE-130

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_build_parser_parses_every_subcommand
```

- 確認内容: pytest case `build parser parses every subcommand` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:163`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `publish_args`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-131

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_repository_name_and_default_work_id_variants
```

- 確認内容: pytest case `repository name and default work id variants` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:213`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-131A

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_status_reports_package_execution_and_next_action
```

- 確認内容: message repair package が存在するstatusで、package実行情報と次アクションが正しく提示されることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:231`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `github-knowledge-analysis.json` と `message-repair-package.json`
- 期待結果: latest package の `allow_push` と `expected_remote_sha` が読み込まれ、未解決candidate数と `verify-remote-then-rebase-apply` のnext actionが返る。
#### RT-UT-CASE-131B

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_next_action_prefers_reuse_worktree_when_replay_worktree_exists
```

- 確認内容: replay用worktreeが既に存在する場合、next-action が再利用前提のresume commandを優先することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:275`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: approved history rewrite candidate、`rebase-replay-package.json`、既存 `git-worktree`
- 期待結果: next action が `resume-rebase-apply-with-reuse-worktree` となり、commandに `--reuse-worktree`、cleanup commandに `cleanup-worktree` が含まれる。
#### RT-UT-CASE-131B-1

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_resume_blocks_when_analysis_json_is_corrupt
```

- 確認内容: corrupt analysis JSON がある場合、resume が通常復帰せず encoding gate block を返すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:315`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: `encoding_gate.status` が `block` となり、next action が artifact integrity 修復確認に切り替わる。

#### RT-UT-CASE-131B-2

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_resume_blocks_push_package_without_expected_remote_sha
```

- 確認内容: push 許可 package に `expected_remote_sha` が無い場合、next-action が push/rebase command を返さず block することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:335`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: `encoding_gate.status` が `block` となり、finding に expected remote SHA 欠落が記録される。

#### RT-UT-CASE-131C

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_verify_remote_compares_expected_sha_from_package
```

- 確認内容: verify-remote が package内の `expected_remote_sha` とremote branch SHAを比較し、push可能判定を返すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:371`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: `rebase-replay-package.json` の `expected_remote_sha = abc123` とmockした `git ls-remote` 結果
- 期待結果: `matches = True` となり、next action が `safe-to-push` になる。
#### RT-UT-CASE-131D

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_cleanup_worktree_requires_force_before_removal
```

- 確認内容: cleanup-worktree がforceなしでは削除せず、force指定時のみGit worktreeを削除することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:414`
  - fixture/arg: `tmp_path` (temporary filesystem), `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: 既存 `git-worktree/feature-issue-2-v0.0.2` とmockした `git worktree remove --force`
- 期待結果: forceなしでは `force_required = True` かつworktreeが残り、forceありでは `removed = True` かつworktreeが削除される。
#### RT-UT-CASE-132

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_init_work_rejects_existing_without_reuse_and_script_load
```

- 確認内容: pytest case `init work rejects existing without reuse and script load` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:462`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-133

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_gate_and_tool_selection_proposal_mode_do_not_require_human_check
```

- 確認内容: pytest case `gate and tool selection proposal mode do not require human check` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:503`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-134

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_tool_selection_apply_mode_splits_local_and_remote_git_auth
```

- 確認内容: pytest case `tool selection apply mode splits local and remote git auth` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:523`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-135

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_register_github_knowledge_contexts_skips_missing_files_and_registers_existing
```

- 確認内容: pytest case `register github knowledge contexts skips missing files and registers existing` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:532`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-136

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_markdown_helpers_render_empty_values_booleans_lists_and_titles
```

- 確認内容: pytest case `markdown helpers render empty values booleans lists and titles` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:552`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-137

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_load_analysis_reports_missing_work_missing_file_and_non_object
```

- 確認内容: pytest case `load analysis reports missing work missing file and non object` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:568`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-138

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_default_analysis_ignores_non_string_assumptions_and_analysis_template_missing_work
```

- 確認内容: pytest case `default analysis ignores non string assumptions and analysis template missing work` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:583`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-139

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_require_github_operation_gate_reports_missing_contexts
```

- 確認内容: pytest case `require github operation gate reports missing contexts` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:605`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-140

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_require_github_operation_gate_rejects_unapproved_mutation_and_rag
```

- 確認内容: pytest case `require github operation gate rejects unapproved mutation and rag` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:613`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-141

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_build_repair_sync_and_rag_markdown_include_dynamic_sections
```

- 確認内容: repair / sync / RAG Markdownの動的sectionに加え、rebase planのOK / NG入力欄が候補別チェックリストだけにあり、詳細事項には候補IDごとの判断材料だけが出ることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:624`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: rebase planは表にだけOK / NGチェック欄を出し、詳細事項には expected commit、判断理由、証跡refs、verification commands などの判断材料を出す。

#### RT-UT-CASE-142

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_build_sync_plan_renders_empty_action_placeholder
```

- 確認内容: pytest case `build sync plan renders empty action placeholder` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:663`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-143

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_history_rewrite_candidate_validation_edges
```

- 確認内容: pytest case `history rewrite candidate validation edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:670`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-144

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_detect_history_rewrite_candidates_from_commit_log
```

- 確認内容: pytest case `detect history rewrite candidates from commit log` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:710`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-145

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_detect_history_rewrite_candidates_requires_manual_review_when_subjects_are_thin
```

- 確認内容: pytest case `detect history rewrite candidates requires manual review when subjects are thin` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:752`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-146

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_detect_rebase_candidates_writes_analysis
```

- 確認内容: pytest case `create detect rebase candidates writes analysis` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:785`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `detected`, `updated`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-147

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_repair_plan_writes_output_and_registers_artifact
```

- 確認内容: pytest case `create repair plan writes output and registers artifact` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:845`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-148

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_rebase_plan_writes_output_and_registers_artifact
```

- 確認内容: pytest case `create rebase plan writes output and registers artifact` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:868`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `rebase_plan`, `artifact_index`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-148-INTEGRITY-001

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_artifact_integrity_report_passes_for_valid_analysis_and_rebase_plan
```

- 確認内容: GitHub knowledge maintenance の analysis JSON と rebase plan Markdown が UTF-8 / JSON / Markdown 契約を満たすとき、artifact integrity gate が pass することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:895`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: artifact integrity report が findings なしで生成され、後続 workflow が表示文字化けに惑わされず本線へ戻れる。

#### RT-UT-CASE-148-INTEGRITY-002

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_artifact_integrity_report_fails_for_invalid_analysis_json
```

- 確認内容: analysis JSON が壊れている場合に、artifact integrity gate が fail として検出することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:923`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: JSON破損は握りつぶされず findings に記録され、AI が手作業更新を続けない判断材料になる。

#### RT-UT-CASE-148A

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_rebase_review_intake_reads_ok_ng_checklist
```

- 確認内容: rebase review checklistのOK/NGを読み取り、analysis JSONの `approval_status` と具体的な `repair_goal` に反映することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:957`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `updated`
- 期待結果: OK候補は `approved` + `absorb-into-existing-commit`、NG候補は `rejected` + `no-rewrite` として記録される。

#### RT-UT-CASE-149

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_rebase_apply_requires_human_and_candidate_approval
```

- 確認内容: pytest case `create rebase apply requires human and candidate approval` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1034`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `updated`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-149A

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_apply_commit_patch_auto_3way_falls_back
```

- 確認内容: direct patch適用に失敗した場合、`auto-3way` がGit 3-way applyへフォールバックすることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1111`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `calls`
- 期待結果: direct失敗後にgit-3wayが呼ばれ、選択modeが `git-3way` になる。

#### RT-UT-CASE-149B

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_rebase_replay_package_generates_from_approved_candidate
```

- 確認内容: 承認済みhistory rewrite candidateから `rebase-replay-package.json` を生成できることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1132`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `package`, `updated`, `artifact_index`
- 期待結果: packageにtarget branch、apply mode、candidate id、absorb action、verification commandが記録される。

#### RT-UT-CASE-149C

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_rebase_replay_package_rejects_unapproved_candidate
```

- 確認内容: 未承認candidateからrebase replay packageを生成できないことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1189`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 未承認candidate選択時にエラーとなる。

#### RT-UT-CASE-149D

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_rebase_replay_package_requires_split_message
```

- 確認内容: split repair candidateでは具体的なcommit message overrideが必須であることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1214`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: message未指定のsplit candidateはpackage生成でエラーとなる。

#### RT-UT-CASE-149E

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_rebase_replay_apply_uses_worktree_and_builtin_runtime
```

- 確認内容: rebase replay applyがmain checkoutではなくworktree配下で組み込みruntimeを使うことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1251`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `mapping`, `updated`
- 期待結果: worktree path、SHA mapping、execution reportが生成され、candidateがverifiedになる。

#### RT-UT-CASE-149E-1

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_rebase_replay_apply_preserves_final_tree_when_absorbed_patch_context_moved
```

- 確認内容: rebase replay applyがsource patchの文脈移動で通常のpatch適用に失敗し得る場合でも、承認済み吸収候補を却下せず、tree-preserving replayで最終tree一致とDROPPED mappingを成立させることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1337`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `mapping`
- 期待結果: replay後の最終treeがsource refと一致し、source commitは `DROPPED`、中間commitは保持され、candidateがverifiedになる。

#### RT-UT-CASE-149E-2

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_rebase_replay_apply_resolves_absorb_cycle_to_earliest_anchor
```

- 確認内容: rebase replay applyが短縮SHAを40桁SHAへ解決した後、相互absorb cycleを本来の履歴位置にあるearliest responsibility anchorへ自動解決することを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1411`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `mapping`, `report`
- 期待結果: replay後の最終treeがsource refと一致し、anchor commitは保持され、吸収対象commitは `DROPPED` になり、実行レポートに `Semantic Anchor Resolution` が記録される。

#### RT-UT-CASE-149E-3

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_message_repair_plan_intake_package_and_replay_apply
```

- 確認内容: message repair plan、OK/NG intake、message repair package、replay apply が、treeを維持する高risk履歴書き換えflowとして接続されることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1488`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `text`, `package_data`, `updated`
- 期待結果: final tree が source ref と一致し、弱いsubjectがlatest logから消え、candidateが `verified` になり、before/after SHA mappingが記録される。
#### RT-UT-CASE-149F

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_publish_verified_replay_pushes_existing_verified_tip
```

- 確認内容: verified済みで未publishのreplay executionを、package再生成なしで専用のforce-with-lease runtime entrypointからpublishできることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1582`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `updated`
- 期待結果: remote branch がverified済みの `new_tip` へ移動し、analysisに `rebase_replay_publications` が記録され、対応するmessage repair candidateが `pushed` になる。
#### RT-UT-CASE-149G

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_rebase_replay_apply_dry_run_does_not_create_worktree
```

- 確認内容: rebase replay applyのdry-runがworktreeを作成せず、実行予定だけを返すことを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1673`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: dry-runではworktree未作成のまま計画が返り、analysis JSONが破壊されない。

#### RT-UT-CASE-150

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_rebase_apply_rejects_interactive_rebase_even_when_allowed
```

- 確認内容: pytest case `rebase apply rejects interactive rebase even when allowed` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1707`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-151

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_github_sync_command_validation_edges
```

- 確認内容: pytest case `github sync command validation edges` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1733`
  - fixture/arg: なし
  - parameter: names=なし, case=なし
  - inline input: `action`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-151A

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_sync_review_plan_and_intake_reads_ok_ng_checklist
```

- 確認内容: GitHub Issue / PR / comment repair actionが1つのOK/NG checklistでreviewされ、`github_sync_actions` へ取り込まれることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1760`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `text`, `updated`
- 期待結果: one action becomes `approved`, one action becomes `rejected`, and human review source metadata is recorded.
#### RT-UT-CASE-152

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_sync_apply_requires_approval_and_records_result
```

- 確認内容: pytest case `create sync apply requires approval and records result` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1823`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: `updated`
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-153

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_sync_apply_blocks_unresolved_rebase_candidates
```

- 確認内容: pytest case `create sync apply blocks unresolved rebase candidates` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1894`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-153A

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_sync_apply_blocks_unresolved_message_repair_candidates
```

- 確認内容: approvedまたはpendingのcommit message repair candidateが未verifiedの間、GitHub sync applyがblockされることを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1915`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: `github-sync-apply` raises a runtime block that names `MESSAGE-REPAIR-001`.
#### RT-UT-CASE-154

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_rag_candidate_requires_human_approval_for_publish
```

- 確認内容: pytest case `create rag candidate requires human approval for publish` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1950`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-155

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_rag_candidate_writes_explicit_output_with_ready_gate
```

- 確認内容: pytest case `create rag candidate writes explicit output with ready gate` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1969`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-156

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_create_rag_candidate_default_and_publish_outputs
```

- 確認内容: pytest case `create rag candidate default and publish outputs` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:1994`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-157

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_run_dispatches_commands_and_rejects_unknown
```

- 確認内容: pytest case `run dispatches commands and rejects unknown` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:2052`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。

#### RT-UT-CASE-158

- pytest node id:

```text
runtime/tests/test_github_knowledge_maintenance.py::test_main_prints_json
```

- 確認内容: pytest case `main prints json` に対応するruntimeの単体振る舞い、境界条件、error boundaryを確認します。
- 入力値:
  - pytest node: 上記コードブロックのnode id
  - source: `runtime/tests/test_github_knowledge_maintenance.py:2151`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `capsys` (captured stdout/stderr)
  - parameter: names=なし, case=なし
  - inline input: test関数内で生成される固定入力、mock入力、または一時ファイル
- 期待結果: 該当caseがpassし、対象runtimeの正常系または境界条件が仕様どおりに確認される。
