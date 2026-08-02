# test_runtime_status.py

This file records pytest node ids for `runtime/tests/test_runtime_status.py`.

| Item | Value |
| --- | ---: |
| cases | 12 |

## Cases

#### RT-UT-CASE-AUTO-001

- pytest node id:

```text
runtime/tests/test_runtime_status.py::test_runtime_status_collects_trace_log_work_and_knowledge_state
```

- Confirm: `test_runtime_status_collects_trace_log_work_and_knowledge_state` runtime contract is covered by pytest assertions.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_status.py:12`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: active trace, runtime event log, workflow-state, knowledge source and DuckDB fixtures
- Expected: pytest assertion defines the expected result.

#### RT-UT-CASE-AUTO-002

- pytest node id:

```text
runtime/tests/test_runtime_status.py::test_ctl_status_outputs_json_and_human_summary
```

- Confirm: `test_ctl_status_outputs_json_and_human_summary` runtime contract is covered by pytest assertions.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_status.py:56`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: repository-local aiwfctl fixture and CTL parser arguments
- Expected: pytest assertion defines the expected result.

#### RT-UT-CASE-AUTO-003

- pytest node id:

```text
runtime/tests/test_runtime_status.py::test_runtime_status_uses_doctor_guidance_for_duckdb_rebuild_next_action
```

- Confirm: `aiwfctl status` next action uses the same DuckDB rebuild guidance as workflow doctor.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_status.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: knowledge source JSON exists and generated DuckDB read model is missing
- Expected: next actions include `aiwfctl rag duckdb rebuild --source-repo work/db/ariadne-knowledge-platform --reset` and do not include the shortened rebuild command.

#### RT-UT-CASE-AUTO-004

- pytest node id:

```text
runtime/tests/test_runtime_status.py::test_runtime_status_suggests_log_maintenance_when_event_log_is_large
```

- Confirm: `aiwfctl status` suggests runtime log maintenance when the event log exceeds the configured keep-last threshold.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_status.py`
  - fixture/arg: `monkeypatch`, `tmp_path` (temporary filesystem)
  - parameter: `RUNTIME_LOG_DEFAULT_KEEP_LAST=1`
  - inline input: two runtime event log lines
- Expected: next actions include `aiwfctl log summary` and `aiwfctl log archive --keep-last 1 --dry-run`.

#### RT-UT-CASE-AUTO-005

- pytest node id:

```text
runtime/tests/test_runtime_status.py::test_runtime_status_exposes_last_problem_event_without_status_noise
```

- Confirm: `aiwfctl status` keeps raw last event while exposing the latest non-noise and problem events.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_status.py`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: a blocked preflight event followed by successful `help markdown` and `status` events
- Expected: raw `last_event` remains `status`, but `last_relevant_event` and `last_problem_event` skip help/status noise and point to the blocked preflight event.

#### RT-UT-CASE-AUTO-006

- pytest node id:

```text
runtime/tests/test_runtime_status.py::test_runtime_status_work_id_links_related_traces
```

- Confirm: `aiwfctl status --work-id` links the selected work id to related runtime traces and exposes the latest trace as a next action.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_status.py:169`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: workflow-state for `issue-1` and two runtime events with `input.work_id=issue-1`
- Expected: related traces include `trace-work`, problem count is preserved, formatted status shows `Related Traces`, and next actions include `aiwfctl trace show trace-work`.

#### RT-UT-CASE-AUTO-001

- pytest node id:

```text
runtime/tests/test_runtime_status.py::test_runtime_status_acknowledgement_candidates_list_multiple_problems
```

- Confirm: `aiwfctl status` lists multiple runtime problem events as acknowledgement candidates.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_status.py:252`
  - fixture/arg: `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: two blocked runtime command events for `env select` and `rag build`
- Expected: acknowledgement candidates are returned newest-first, each candidate has an acknowledgement command, and next actions include `aiwfctl log tail --problems -n 20`.

#### RT-UT-CASE-AUTO-007

- pytest node id:

```text
runtime/tests/test_runtime_status.py::test_runtime_status_integrates_doctor_warning_count_and_next_action
```

- Confirm: `aiwfctl status` includes doctor warning count and adds a doctor JSON next action when warnings exist.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_status.py:234`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: mocked doctor warning summary and ready dependency readiness
- Expected: runtime status becomes `attention`, doctor warning count is preserved, formatted output shows warning count, and next actions include `aiwfctl doctor --json`.

#### RT-UT-CASE-AUTO-001

- pytest node id:

```text
runtime/tests/test_runtime_status.py::test_runtime_status_attention_reasons_explain_dirty_repo
```

- Confirm: `aiwfctl status` explains why attention is required through `attention_reasons`.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_status.py:271`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: mocked dirty git status with ready dependency readiness and pass doctor status
- Expected: runtime status becomes `attention`, `git-dirty` appears in `attention_reasons`, and the summary JSON view preserves that reason.

#### RT-UT-CASE-AUTO-008

- pytest node id:

```text
runtime/tests/test_runtime_status.py::test_runtime_status_dependency_readiness_summarizes_required_and_optional_missing
```

- Confirm: dependency readiness summarizes required and optional missing runtime capabilities.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_status.py:268`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: mocked preflight checks for Git, uv, Docker, GitHub CLI, REUSE, act, ScanCode workflow, and DuckDB read model
- Expected: required missing and optional missing counts are separated, with required uv missing reported as `missing-required` and Docker daemon as `missing-optional`.

#### RT-UT-CASE-AUTO-009

- pytest node id:

```text
runtime/tests/test_runtime_status.py::test_runtime_status_json_views_filter_summary_and_problems
```

- Confirm: status JSON views can be reduced to summary or problem-focused payloads while verbose keeps full detail.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_status.py:316`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: mocked doctor warnings, dependency readiness with one failed optional check, and a runtime problem event
- Expected: summary view omits full doctor warnings, problems view includes last problem event and failed checks, and verbose view keeps doctor warning details.

#### RT-UT-CASE-AUTO-002

- pytest node id:

```text
runtime/tests/test_runtime_status.py::test_runtime_status_problems_view_omits_pass_and_empty_sections
```

- Confirm: `status --problems --json` omits pass/empty diagnostic sections.
- Input:
  - pytest node: above node id
  - source: `runtime/tests/test_runtime_status.py:419`
  - fixture/arg: `monkeypatch` (environment / function monkeypatch), `tmp_path` (temporary filesystem)
  - parameter: names=none case=none
  - inline input: mocked pass doctor status, ready dependency readiness, and no runtime problem event
- Expected: problems view stays `ok`, keeps an empty `attention_reasons` list, and omits empty `doctor`, `environment`, `runtime`, and `related_traces` sections.
