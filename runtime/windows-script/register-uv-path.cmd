@echo off
setlocal
chcp 65001 >nul
set "ARIADNE_SCRIPT_DIR=%~dp0"
set "ARIADNE_UV_PATH_MODE=%~1"

powershell -NoProfile -Command ^
  "$tools = [System.IO.Path]::GetFullPath($env:ARIADNE_SCRIPT_DIR).TrimEnd('\');" ^
  "$mode = [Environment]::GetEnvironmentVariable('ARIADNE_UV_PATH_MODE', 'Process');" ^
  "$candidateDirs = @($tools, (Join-Path $env:USERPROFILE '.local\bin'), (Join-Path $env:USERPROFILE '.cargo\bin'), (Join-Path $env:LOCALAPPDATA 'Programs\uv'));" ^
  "$candidateDirs = @($candidateDirs | Where-Object { $_ -and (Test-Path $_) } | ForEach-Object { [System.IO.Path]::GetFullPath($_).TrimEnd('\') } | Select-Object -Unique);" ^
  "$current = [Environment]::GetEnvironmentVariable('Path', 'User');" ^
  "$parts = @($current -split ';' | Where-Object { $_ -and $_.Trim() } | ForEach-Object { $_.Trim() });" ^
  "$missing = @();" ^
  "foreach ($dir in $candidateDirs) { $exists = $false; foreach ($part in $parts) { if ([string]::Equals($part.TrimEnd('\'), $dir, [System.StringComparison]::OrdinalIgnoreCase)) { $exists = $true } }; if (-not $exists) { $missing += $dir } }" ^
  "if ($mode -eq '--check') { Write-Output 'Candidate PATH entries:'; $candidateDirs | ForEach-Object { Write-Output ('  ' + $_) }; if ($missing.Count -eq 0) { Write-Output 'uv path entries are registered.' } else { Write-Output 'missing from User Path:'; $missing | ForEach-Object { Write-Output ('  ' + $_) } }; exit 0 }" ^
  "if ($missing.Count -gt 0) { [Environment]::SetEnvironmentVariable('Path', (($missing + $parts) -join ';'), 'User'); Write-Output 'added to User Path:'; $missing | ForEach-Object { Write-Output ('  ' + $_) } } else { Write-Output 'uv path entries are already registered.' }" ^
  "Write-Output 'Open a new terminal, then run: uv --version'"

if "%ARIADNE_UV_PATH_MODE%"=="--check" exit /b %ERRORLEVEL%
if "%ARIADNE_UV_PATH_MODE%"=="--shell" (
  set "Path=%ARIADNE_SCRIPT_DIR%;%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%LOCALAPPDATA%\Programs\uv;%Path%"
  echo.
  echo Starting a refreshed PowerShell session with Ariadne runtime tools on Path...
  powershell -NoLogo -NoExit -Command "Write-Host 'Ariadne uv session ready'; Get-Command uv -ErrorAction SilentlyContinue; Write-Host 'Try: uv --version'"
  exit /b %ERRORLEVEL%
)

echo.
echo Existing PowerShell sessions do not inherit User Path changes.
echo If uv is still not found in this session, run:
echo   $env:Path="%ARIADNE_SCRIPT_DIR%;$env:USERPROFILE\.local\bin;$env:USERPROFILE\.cargo\bin;$env:LOCALAPPDATA\Programs\uv;$env:Path"
