# aiwfctlアーキテクチャ

`aiwfctl` は、ARIADNE runtime操作のためのlocal CLI entrypointです。

## 責務

- workflowとruntime subcommandを1つのcommand surfaceから呼び出せるようにする。
- shell wrapperを薄く保ち、Python runtime moduleへdispatchする。
- workflow state、artifact、evidence、completion markerを読み書きする。
- Human Gateが必要な状態を明示的なstatusとして返す。
- recovery、resume、validation、inspection commandを支援する。

## Entry Point

Windowsでは次のように呼び出します。

```powershell
.\runtime\windows-script\aiwfctl.cmd help list
```

`runtime/windows-script` が `PATH` にある場合は、短い形式を使えます。

```powershell
aiwfctl help list
```

POSIX環境では次のように呼び出します。

```bash
./runtime/posix-bash/aiwf.sh help list
```

## Runtime境界

Shell scriptはrepository rootの解決、環境差分の吸収、Python runtimeの呼び出しに限定します。workflow判断はshell wrapperではなく、Python moduleまたは文書化されたpromptに置きます。
