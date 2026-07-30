@echo off
setlocal
chcp 65001 >nul
set "FLUTTER_PATH_MODE=%~1"
set "FLUTTER_SDK_ROOT=%~2"
if "%FLUTTER_SDK_ROOT%"=="" set "FLUTTER_SDK_ROOT=C:\flutter"
powershell -NoProfile -Command ^
  "$mode = [Environment]::GetEnvironmentVariable('FLUTTER_PATH_MODE', 'Process');" ^
  "$sdkRoot = [Environment]::GetEnvironmentVariable('FLUTTER_SDK_ROOT', 'Process');" ^
  "$flutterBin = [System.IO.Path]::GetFullPath((Join-Path $sdkRoot 'bin')).TrimEnd('\');" ^
  "$flutterBat = Join-Path $flutterBin 'flutter.bat';" ^
  "if (-not (Test-Path -LiteralPath $flutterBat)) { Write-Error ('flutter.bat was not found: ' + $flutterBat); exit 1 }" ^
  "$current = [Environment]::GetEnvironmentVariable('Path', 'User');" ^
  "$parts = @($current -split ';' | Where-Object { $_ -and $_.Trim() });" ^
  "$exists = $false;" ^
  "foreach ($part in $parts) { if ([string]::Equals($part.TrimEnd('\'), $flutterBin, [System.StringComparison]::OrdinalIgnoreCase)) { $exists = $true } }" ^
  "if ($mode -eq '--check') { if ($exists) { Write-Output ('registered in User Path: ' + $flutterBin) } else { Write-Output ('not registered in User Path: ' + $flutterBin) }; exit 0 }" ^
  "if (-not $exists) { [Environment]::SetEnvironmentVariable('Path', (($flutterBin, $parts) -join ';'), 'User'); Write-Output ('added to User Path: ' + $flutterBin) } else { Write-Output ('already in User Path: ' + $flutterBin) }" ^
  "Write-Output 'Open a new PowerShell session, then run: flutter --version'"
if "%FLUTTER_PATH_MODE%"=="--check" exit /b %ERRORLEVEL%
if "%FLUTTER_PATH_MODE%"=="--shell" (
  set "Path=%FLUTTER_SDK_ROOT%\bin;%Path%"
  echo.
  echo Starting a refreshed PowerShell session with Flutter on Path...
  powershell -NoLogo -NoExit -Command "Write-Host 'Flutter session ready'; Get-Command flutter; flutter --version; Write-Host 'Try: flutter doctor -v'"
  exit /b %ERRORLEVEL%
)
echo.
echo Existing PowerShell sessions do not inherit User Path changes.
echo If flutter is still not found in this session, run:
echo   $env:Path="%FLUTTER_SDK_ROOT%\bin;$env:Path"
