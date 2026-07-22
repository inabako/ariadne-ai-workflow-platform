@echo off
setlocal
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
set "REPO_ROOT=%~dp0..\..\"
set "AIWFCTL_SCRIPT_DIR=%~dp0"
if /I "%~1"=="path" goto :path_command
if exist "%AIWFCTL_SCRIPT_DIR%uv.cmd" (
  call "%AIWFCTL_SCRIPT_DIR%uv.cmd" run --project "%REPO_ROOT%runtime" python "%REPO_ROOT%runtime\ctl\ctl.py" %*
) else (
  python "%REPO_ROOT%runtime\ctl\ctl.py" %*
)
exit /b %ERRORLEVEL%

:path_command
set "AIWFCTL_PATH_ACTION=%~2"
if "%AIWFCTL_PATH_ACTION%"=="" goto :path_usage
if /I "%AIWFCTL_PATH_ACTION%"=="check" (
  call "%AIWFCTL_SCRIPT_DIR%register-aiwfctl-path.cmd" --check
  exit /b %ERRORLEVEL%
)
if /I "%AIWFCTL_PATH_ACTION%"=="register" (
  call "%AIWFCTL_SCRIPT_DIR%register-aiwfctl-path.cmd"
  exit /b %ERRORLEVEL%
)
if /I "%AIWFCTL_PATH_ACTION%"=="shell" (
  call "%AIWFCTL_SCRIPT_DIR%register-aiwfctl-path.cmd" --shell
  exit /b %ERRORLEVEL%
)
if /I "%AIWFCTL_PATH_ACTION%"=="refresh" (
  call "%AIWFCTL_SCRIPT_DIR%register-aiwfctl-path.cmd" --shell
  exit /b %ERRORLEVEL%
)
goto :path_usage

:path_usage
echo Usage:
echo   aiwfctl path check
echo   aiwfctl path register
echo   aiwfctl path shell
echo.
echo Notes:
echo   path check    checks whether runtime\windows-script is registered in User Path.
echo   path register registers runtime\windows-script in User Path.
echo   path shell    registers User Path and opens a refreshed PowerShell session.
exit /b 1
