@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo 正在同步 AI 视频提示词数据库...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\prepare_viewer_data.ps1"

if errorlevel 1 (
  echo.
  echo 启动失败，请检查 AI视频提示词数据库.json 是否存在。
  pause
  exit /b 1
)

echo 正在打开提示词浏览器...
start "" "%~dp0index.html"
exit /b 0
