@echo off
setlocal
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
set "REPO_ROOT=%~dp0..\..\"
where uv >nul 2>nul
if %ERRORLEVEL%==0 (
  uv run python "%REPO_ROOT%runtime\ctl.py" %*
) else (
  python "%REPO_ROOT%runtime\ctl.py" %*
)
exit /b %ERRORLEVEL%
