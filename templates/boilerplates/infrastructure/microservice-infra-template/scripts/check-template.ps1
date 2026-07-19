param(
    [ValidateSet("local", "dev", "stg", "prod")]
    [string]$Env = "local"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$envDir = Join-Path $root "environments\$Env"

$terraformCommand = Get-Command terraform -ErrorAction SilentlyContinue
$terraform = if ($terraformCommand) {
    $terraformCommand.Source
}
elseif (Test-Path -LiteralPath "C:\terraform\terraform.exe") {
    "C:\terraform\terraform.exe"
}
else {
    throw "terraform command was not found. Install Terraform or place terraform.exe at C:\terraform\terraform.exe."
}

function Invoke-Terraform {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & $terraform @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "terraform $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
    }
}

Push-Location $root
try {
    Invoke-Terraform -Arguments @("fmt", "-recursive", "-check")
    Invoke-Terraform -Arguments @("-chdir=$envDir", "init", "-backend=false")
    Invoke-Terraform -Arguments @("-chdir=$envDir", "validate")
}
finally {
    Pop-Location
}
