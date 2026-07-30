$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $ProjectRoot
try {
  python -m pytest -o "cache_dir=$(Join-Path $ProjectRoot '.pytest_cache')"
} finally {
  Pop-Location
}
