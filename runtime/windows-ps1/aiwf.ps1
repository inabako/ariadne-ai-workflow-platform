[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("help", "ctl", "doctor", "pytest", "spec-check", "bom-scan", "bom-strip")]
    [string]$Command = "help",

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding = $Utf8NoBom
[Console]::OutputEncoding = $Utf8NoBom
$OutputEncoding = $Utf8NoBom

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir "../..")).Path
$RuntimeRoot = Join-Path $RepoRoot "runtime"
$CtlPath = Join-Path $RuntimeRoot "common/ctl.py"
$BomToolPath = Join-Path $RuntimeRoot "tools/utf8_bom.py"
$SpecSyncPath = Join-Path $RuntimeRoot "tools/pytest_ut_spec_sync.py"
$SpecPath = Join-Path $RepoRoot "docs/reference/runtime-pytest-ut/case-specification.md"

function Test-AiwfWindowsHost {
    $isWindowsVariable = Get-Variable -Name IsWindows -ErrorAction SilentlyContinue
    if ($null -ne $isWindowsVariable) {
        return [bool]$isWindowsVariable.Value
    }
    return [System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT
}

function Test-AiwfWindows11 {
    if (-not (Test-AiwfWindowsHost)) {
        return $false
    }
    $version = [System.Environment]::OSVersion.Version
    return $version.Major -ge 10 -and $version.Build -ge 22000
}

function Assert-AiwfRepoRoot {
    if (-not (Test-Path -LiteralPath $CtlPath -PathType Leaf)) {
        throw "runtime/common/ctl.py was not found. Run this script from the Ariadne repository checkout."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot ".git"))) {
        throw ".git was not found under the resolved repository root: $RepoRoot"
    }
}

function Get-AiwfUvPath {
    $uvCommand = Get-Command uv -ErrorAction SilentlyContinue
    if ($null -eq $uvCommand) {
        $localUv = Join-Path $RuntimeRoot "tools/uv.cmd"
        if (Test-Path -LiteralPath $localUv -PathType Leaf) {
            return $localUv
        }
        throw "uv was not found on PATH. Run runtime/tools/register-uv-path.cmd --shell, then open a new terminal."
    }
    return $uvCommand.Source
}

function Invoke-AiwfNative {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [Parameter(Mandatory = $true)]
        [string[]]$ArgumentList,

        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory
    )

    Push-Location $WorkingDirectory
    try {
        & $FilePath @ArgumentList
        $exitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }

    if ($null -eq $exitCode) {
        $exitCode = 0
    }
    if ($exitCode -ne 0) {
        exit $exitCode
    }
}

function Invoke-AiwfUv {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$ArgumentList,

        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory
    )

    $uvPath = Get-AiwfUvPath
    Invoke-AiwfNative -FilePath $uvPath -ArgumentList $ArgumentList -WorkingDirectory $WorkingDirectory
}

function Show-AiwfHelp {
    Write-Output @"
Ariadne Windows PowerShell runtime

Usage:
  .\runtime\windows-ps1\aiwf.ps1 ctl <aiwfctl-args>
  .\runtime\windows-ps1\aiwf.ps1 doctor [aiwfctl-doctor-args]
  .\runtime\windows-ps1\aiwf.ps1 pytest [pytest-args]
  .\runtime\windows-ps1\aiwf.ps1 spec-check
  .\runtime\windows-ps1\aiwf.ps1 bom-scan [utf8_bom scan args]
  .\runtime\windows-ps1\aiwf.ps1 bom-strip [utf8_bom strip args]

Resolved paths:
  Repo root    : $RepoRoot
  Runtime root : $RuntimeRoot

Windows 11:
  AI workflows on Windows 11 should start here first, then delegate through aiwfctl.
"@
}

Assert-AiwfRepoRoot

if ((Test-AiwfWindowsHost) -and -not (Test-AiwfWindows11)) {
    Write-Warning "This runtime is supported for Windows PowerShell hosts, but the AI workflow default target is Windows 11."
}

switch ($Command) {
    "help" {
        Show-AiwfHelp
    }
    "ctl" {
        $arguments = @("run", "--project", $RuntimeRoot, "python", $CtlPath, "--repo-root", $RepoRoot)
        $arguments += $RemainingArgs
        Invoke-AiwfUv -ArgumentList $arguments -WorkingDirectory $RepoRoot
    }
    "doctor" {
        $arguments = @("run", "--project", $RuntimeRoot, "python", $CtlPath, "--repo-root", $RepoRoot, "doctor")
        $arguments += $RemainingArgs
        Invoke-AiwfUv -ArgumentList $arguments -WorkingDirectory $RepoRoot
    }
    "pytest" {
        $arguments = @("run", "pytest")
        $arguments += $RemainingArgs
        Invoke-AiwfUv -ArgumentList $arguments -WorkingDirectory $RuntimeRoot
    }
    "spec-check" {
        $arguments = @(
            "run",
            "--project",
            $RuntimeRoot,
            "python",
            $SpecSyncPath,
            "--spec",
            $SpecPath,
            "--runtime-root",
            $RuntimeRoot,
            "check"
        )
        $arguments += $RemainingArgs
        Invoke-AiwfUv -ArgumentList $arguments -WorkingDirectory $RepoRoot
    }
    "bom-scan" {
        $arguments = @("run", "--project", $RuntimeRoot, "python", $BomToolPath, "--repo-root", $RepoRoot, "scan")
        $arguments += $RemainingArgs
        Invoke-AiwfUv -ArgumentList $arguments -WorkingDirectory $RepoRoot
    }
    "bom-strip" {
        $arguments = @("run", "--project", $RuntimeRoot, "python", $BomToolPath, "--repo-root", $RepoRoot, "strip")
        $arguments += $RemainingArgs
        Invoke-AiwfUv -ArgumentList $arguments -WorkingDirectory $RepoRoot
    }
}
