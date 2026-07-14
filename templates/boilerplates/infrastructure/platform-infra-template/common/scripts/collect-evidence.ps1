$ErrorActionPreference = "Stop"
param(
    [string]$OutputDir = "test-evidence/platform-infra"
)

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
Write-Output "Collect platform evidence into $OutputDir."

