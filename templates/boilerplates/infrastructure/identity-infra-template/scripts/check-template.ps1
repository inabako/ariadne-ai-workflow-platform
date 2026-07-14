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
    "modules/identity_catalog/main.tf",
    "modules/docker_compose_manifest/main.tf",
    "environments/$Env/main.tf",
    "openldap/docker-compose/compose.yaml",
    "openldap/docker-compose/env.example",
    "openldap/ldif/00-base.ldif",
    "openldap/ldif/10-organizational-units.ldif",
    "openldap/ldif/20-groups.ldif",
    "openldap/ldif/30-users.ldif",
    "openldap/scripts/validate-bind.sh",
    "openldap/scripts/validate-user-search.sh",
    "openldap/scripts/validate-group-search.sh",
    "integrated/web-application-example/compose.yaml",
    "docs/dn-design-guidelines.md",
    "docs/completion-criteria.md"
)

foreach ($relative in $required) {
    $path = Join-Path $root $relative
    if (-not (Test-Path -LiteralPath $path)) {
        throw "missing required template file: $relative"
    }
}

if ($SkipTerraform) {
    Write-Output "IDENTITY_INFRA_TEMPLATE_STATIC_OK"
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

Write-Output "IDENTITY_INFRA_TEMPLATE_TERRAFORM_OK"

