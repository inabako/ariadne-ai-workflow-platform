param(
    [ValidateSet("local", "dev", "stg", "prod")]
    [string]$Env = "local",
    [switch]$SkipTerraform
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

$required = @(
    "README.md",
    "main.tf",
    "variables.tf",
    "outputs.tf",
    "modules/database_catalog/main.tf",
    "modules/docker_compose_manifest/main.tf",
    "environments/$Env/main.tf",
    "postgresql/docker-compose/compose.yaml",
    "postgresql/docker-compose/env.example",
    "postgresql/init/03-create-schema.sql",
    "mysql/docker-compose/compose.yaml",
    "mysql/docker-compose/env.example",
    "mysql/init/03-grant-privileges.sql",
    "integrated/single-instance/compose.yaml",
    "integrated/multi-database/compose.yaml",
    "integrated/application-stack-example/compose.yaml",
    "docs/completion-criteria.md"
)

foreach ($relative in $required) {
    $path = Join-Path $root $relative
    if (-not (Test-Path -LiteralPath $path)) {
        throw "missing required template file: $relative"
    }
}

if ($SkipTerraform) {
    Write-Output "DATABASE_INFRA_TEMPLATE_STATIC_OK"
    return
}

$terraformCommand = Get-Command terraform -ErrorAction SilentlyContinue
$terraform = if ($terraformCommand) {
    $terraformCommand.Source
}
elseif (Test-Path -LiteralPath "C:\terraform\terraform.exe") {
    "C:\terraform\terraform.exe"
}
else {
    throw "terraform command was not found. Install Terraform, place terraform.exe at C:\terraform\terraform.exe, or run with -SkipTerraform for static template validation."
}

Push-Location $root
try {
    & $terraform fmt -recursive -check
    if ($LASTEXITCODE -ne 0) {
        throw "terraform fmt -recursive -check failed."
    }

    $envDir = Join-Path $root "environments/$Env"
    & $terraform "-chdir=$envDir" init -backend=false
    if ($LASTEXITCODE -ne 0) {
        throw "terraform init failed."
    }

    & $terraform "-chdir=$envDir" validate
    if ($LASTEXITCODE -ne 0) {
        throw "terraform validate failed."
    }
}
finally {
    Pop-Location
}

Write-Output "DATABASE_INFRA_TEMPLATE_TERRAFORM_OK"

