# POSIX Bash Runtime

Linux / WSL / macOS で Ariadne AI Workflow を動かす場合は、まずこの bash runtime を入口にします。

```bash
./runtime/posix-bash/aiwf.sh help
./runtime/posix-bash/aiwf.sh ctl help search github knowledge
./runtime/posix-bash/aiwf.sh pytest -q
./runtime/posix-bash/aiwf.sh spec-check
```

## 役割

- Bash の `set -Eeuo pipefail` で失敗を握りつぶさない。
- repository root と `runtime/` の位置を script から解決する。
- `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8` を設定する。
- 通常 workflow は必ず `runtime/ctl/ctl.py`、つまり `aiwfctl` 正式入口へ委譲する。
- BOM scan / strip、pytest、UT 仕様同期 check も bash 入口から実行できるようにする。

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

Linux / WSL / macOS 上で AI workflow を実行する場合、この bash runtime を先に使います。

Bash runtime は workflow の判断や承認を持ちません。Context First、Human Check、GitHub knowledge maintenance、self-improvement などの正式判断は `aiwfctl` / `runtime/ctl/ctl.py` 側に集約します。

不足している操作がある場合は、bash へ直接 workflow ロジックを増やさず、まず self-improvement Feedback に流します。Accepted Feedback になった後でのみ、`runtime/ctl/ctl.py` の正式入口改修候補にします。
