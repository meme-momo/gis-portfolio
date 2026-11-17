@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   同步到 Gitee + GitHub
echo ========================================
echo.
git add -A
git commit -m "update"
if errorlevel 1 echo [提示] 没有新的改动需要提交
echo.
echo [同步] 先拉取 Gitee，避免冲突...
git pull --rebase --autostash
echo.
echo [1/2] 推送 Gitee ...
git push
if errorlevel 1 goto fail
echo.
echo [2/2] 推送 GitHub ...
git push github
if errorlevel 1 goto fail
git push github --tags
echo.
echo ========================================
echo 完成：Gitee 与 GitHub 均已同步
git log --oneline -3
echo ========================================
pause
exit /b 0

:fail
echo.
echo [失败] 上面有错误提示，两个平台可能不一致
echo 解决后重新双击本文件即可
pause
exit /b 1
