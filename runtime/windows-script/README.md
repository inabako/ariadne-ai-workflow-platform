# Windows Script Runtime

Windows 11 で Ariadne AI Workflow を動かす場合は、まずこの PS1 runtime を入口にします。

```powershell
.\runtime\windows-script\aiwf.cmd help
.\runtime\windows-script\aiwf.cmd ctl help search github knowledge
.\runtime\windows-script\aiwf.cmd pytest -q
.\runtime\windows-script\aiwf.cmd spec-check
```

Use `runtime/windows-script/aiwf.cmd` as the normal PATH-friendly Windows entrypoint. It delegates to `runtime/windows-script/aiwf.cmd`, which invokes this PS1 runtime with process-scoped `-ExecutionPolicy Bypass`, so the repository does not require changing the user's PowerShell policy.

## 役割

- PowerShell の入出力を UTF-8 no BOM に固定する。
- repository root と `runtime/` の位置を script から解決する。
- `python` / `py` の Windows Store alias を避け、`uv run ... python ...` に統一する。
- 通常 workflow は必ず `runtime/ctl/ctl.py`、つまり `aiwfctl` 正式入口へ委譲する。
- BOM scan / strip、pytest、UT 仕様同期 check も PowerShell ネイティブ入口から実行できるようにする。

## コマンド

| Command | Delegation |
| --- | --- |
| `ctl` | `uv run --project runtime python runtime/ctl/ctl.py --repo-root <repo-root> ...` |
| `doctor` | `aiwfctl doctor ...` |
| `pytest` | `runtime/` を working directory にして `uv run pytest ...` |
| `spec-check` | `aiwfctl tools spec-check` |
| `bom-scan` | `aiwfctl tools bom-scan` |
| `bom-strip` | `aiwfctl tools bom-strip` |

## 運用ルール

Windows 11 上で AI workflow を実行する場合、この PS1 runtime を先に使います。

PS1 は workflow の判断や承認を持ちません。Context First、Human Check、GitHub knowledge maintenance、self-improvement などの正式判断は `aiwfctl` / `runtime/ctl/ctl.py` 側に集約します。

不足している操作がある場合は、PS1 へ直接 workflow ロジックを増やさず、まず self-improvement Feedback に流します。Accepted Feedback になった後でのみ、`runtime/ctl/ctl.py` の正式入口改修候補にします。
