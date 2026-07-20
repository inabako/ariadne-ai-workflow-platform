@echo off
setlocal
chcp 65001 >nul
set "AIWFCTL_SCRIPT_DIR=%~dp0"
set "AIWFCTL_PATH_MODE=%~1"
powershell -NoProfile -Command ^
  "$tool = [System.IO.Path]::GetFullPath($env:AIWFCTL_SCRIPT_DIR).TrimEnd('\');" ^
  "$mode = [Environment]::GetEnvironmentVariable('AIWFCTL_PATH_MODE', 'Process');" ^
  "$current = [Environment]::GetEnvironmentVariable('Path', 'User');" ^
  "$parts = @($current -split ';' | Where-Object { $_ -and $_.Trim() });" ^
  "$exists = $false;" ^
  "foreach ($part in $parts) { if ([string]::Equals($part.TrimEnd('\'), $tool, [System.StringComparison]::OrdinalIgnoreCase)) { $exists = $true } }" ^
  "if ($mode -eq '--check') { if ($exists) { Write-Output ('registered in User Path: ' + $tool) } else { Write-Output ('not registered in User Path: ' + $tool) }; exit 0 }" ^
  "if (-not $exists) { [Environment]::SetEnvironmentVariable('Path', (($tool, $parts) -join ';'), 'User'); Write-Output ('added to User Path: ' + $tool) } else { Write-Output ('already in User Path: ' + $tool) }" ^
  "Write-Output 'Open a new PowerShell session, then run: aiwfctl help list'"
if "%AIWFCTL_PATH_MODE%"=="--check" exit /b %ERRORLEVEL%
if "%AIWFCTL_PATH_MODE%"=="--shell" (
  set "Path=%AIWFCTL_SCRIPT_DIR%;%Path%"
  echo.
  echo Starting a refreshed PowerShell session with aiwfctl on Path...
  powershell -NoLogo -NoExit -Command "Write-Host 'aiwfctl session ready'; Get-Command aiwfctl; Write-Host 'Try: aiwfctl help list'"
  exit /b %ERRORLEVEL%
)
echo.
echo Existing PowerShell sessions do not inherit User Path changes.
echo If aiwfctl is still not found in this session, run:
echo   $env:Path="%AIWFCTL_SCRIPT_DIR%;$env:Path"
