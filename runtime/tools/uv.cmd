@echo off
setlocal
chcp 65001 >nul
set "UV_WRAPPER=%~f0"
set "UV_EXE="

for %%P in (
  "%USERPROFILE%\.local\bin\uv.exe"
  "%USERPROFILE%\.cargo\bin\uv.exe"
  "%LOCALAPPDATA%\Programs\uv\uv.exe"
) do (
  if exist "%%~P" (
    set "UV_EXE=%%~P"
    goto :run_uv
  )
)

for /f "usebackq delims=" %%P in (`where uv.exe 2^>nul`) do (
  if exist "%%~fP" (
    set "UV_EXE=%%~fP"
    goto :run_uv
  )
)

echo ERROR: uv.exe was not found.
echo.
echo Install uv, then open a new terminal:
echo   winget install --id astral-sh.uv -e
echo.
echo Ariadne runtime project commands:
echo   cd runtime
echo   uv run --group dev pytest -q
echo   uv run --group dev coverage run --branch -m pytest
echo.
echo If uv is installed but not found, run:
echo   runtime\tools\register-uv-path.cmd --shell
exit /b 9009

:run_uv
"%UV_EXE%" %*
exit /b %ERRORLEVEL%
