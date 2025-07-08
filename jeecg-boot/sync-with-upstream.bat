@echo off
setlocal enabledelayedexpansion

REM ========================================
REM 通用仓库同步脚本 - Windows版本
REM 用途：保持fork与官方仓库同步，并更新个人分支
REM ========================================

REM ========================================
REM 配置变量 - 根据您的项目修改以下变量
REM ========================================
set "UPSTREAM_REPO_URL=https://github.com/jeecgboot/JeecgBoot.git"
set "ORIGIN_REPO_URL=https://github.com/kyne0116/JeecgBoot.git"
set "MAIN_BRANCH=master"
set "PERSONAL_BRANCH=my-custom"
set "UPSTREAM_REMOTE_NAME=upstream"
set "ORIGIN_REMOTE_NAME=origin"

REM 初始化总结变量
set "master_sync_status=未开始"
set "master_changes_count=0"
set "master_files_changed="
set "commits_behind=0"
set "personal_branch_status=未开始"
set "backup_branch_name="
set "rebase_method="
set "conflicts_occurred=否"
set "commits_before=0"
set "commits_after=0"

REM 颜色定义（Windows CMD不支持ANSI颜色，使用文本标记）
set "INFO_PREFIX=[信息]"
set "SUCCESS_PREFIX=[成功]"
set "WARNING_PREFIX=[警告]"
set "ERROR_PREFIX=[错误]"

echo ========================================
echo     通用仓库同步脚本 - Windows版本
echo ========================================
echo.
echo 配置信息：
echo   上游仓库: !UPSTREAM_REPO_URL!
echo   源仓库: !ORIGIN_REPO_URL!
echo   主分支: !MAIN_BRANCH!
echo   个人分支: !PERSONAL_BRANCH!
echo ========================================
echo.

REM 检查是否在git仓库中
echo !INFO_PREFIX! 检查Git仓库状态...
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo !ERROR_PREFIX! 当前目录不是Git仓库！
    pause
    exit /b 1
)

REM 检查是否有未提交的变更
echo !INFO_PREFIX! 检查未提交的变更...
git diff-index --quiet HEAD -- >nul 2>&1
if errorlevel 1 (
    echo !WARNING_PREFIX! 检测到未提交的变更！
    echo 请先提交或暂存您的变更：
    git status --porcelain
    set /p "continue=是否继续？(y/N): "
    if /i not "!continue!"=="y" (
        echo !INFO_PREFIX! 操作已取消
        pause
        exit /b 0
    )
)

REM 检查并添加上游仓库
echo !INFO_PREFIX! 检查上游仓库配置...
git remote get-url !UPSTREAM_REMOTE_NAME! >nul 2>&1
if errorlevel 1 (
    echo !INFO_PREFIX! 添加上游仓库...
    git remote add !UPSTREAM_REMOTE_NAME! !UPSTREAM_REPO_URL!
    if errorlevel 1 (
        echo !ERROR_PREFIX! 添加上游仓库失败！
        pause
        exit /b 1
    )
    echo !SUCCESS_PREFIX! 上游仓库已添加
) else (
    echo !INFO_PREFIX! 上游仓库已存在
)

echo 当前远程仓库配置：
git remote -v

echo.
echo !INFO_PREFIX! Starting sync for !MAIN_BRANCH! branch...

REM Switch to main branch
echo !INFO_PREFIX! Switching to !MAIN_BRANCH! branch...
git checkout !MAIN_BRANCH!
if errorlevel 1 (
    echo !ERROR_PREFIX! Failed to switch to !MAIN_BRANCH! branch!
    set "master_sync_status=Failed"
    pause
    exit /b 1
)

REM Get commits behind count
for /f %%i in ('git rev-list --count HEAD..!UPSTREAM_REMOTE_NAME!/!MAIN_BRANCH! 2^>nul') do set "commits_behind=%%i"
if "!commits_behind!"=="" set "commits_behind=0"

REM Fetch upstream updates
echo !INFO_PREFIX! Fetching upstream repository updates...
git fetch !UPSTREAM_REMOTE_NAME!
if errorlevel 1 (
    echo !ERROR_PREFIX! Failed to fetch upstream updates!
    set "master_sync_status=Failed"
    pause
    exit /b 1
)

REM Recalculate commits behind count
for /f %%i in ('git rev-list --count HEAD..!UPSTREAM_REMOTE_NAME!/!MAIN_BRANCH! 2^>nul') do set "commits_behind=%%i"
if "!commits_behind!"=="" set "commits_behind=0"

REM Merge upstream updates
echo !INFO_PREFIX! Merging upstream updates to local !MAIN_BRANCH!...
git merge !UPSTREAM_REMOTE_NAME!/!MAIN_BRANCH! --stat > temp_merge_output.txt 2>&1
if errorlevel 1 (
    echo !ERROR_PREFIX! Failed to merge upstream updates! Conflicts may need manual resolution
    set "master_sync_status=Failed"
    set "conflicts_occurred=Yes"
    type temp_merge_output.txt
    del temp_merge_output.txt
    pause
    exit /b 1
) else (
    REM Parse merge statistics
    for /f "delims=" %%i in (temp_merge_output.txt) do (
        echo %%i | findstr "files changed" >nul
        if not errorlevel 1 set "master_files_changed=%%i"
    )
    if "!master_files_changed!"=="" set "master_files_changed=No file changes"
    set "master_sync_status=Success"
    del temp_merge_output.txt
)

REM Push to fork
echo !INFO_PREFIX! Pushing updates to your fork...
git push !ORIGIN_REMOTE_NAME! !MAIN_BRANCH!
if errorlevel 1 (
    echo !WARNING_PREFIX! Failed to push to fork, may need manual push
    set "master_sync_status=Partial Success"
)

echo !SUCCESS_PREFIX! !MAIN_BRANCH! branch sync completed!

echo.
echo %INFO_PREFIX% 开始更新个人分支 %PERSONAL_BRANCH%...

REM 检查分支是否存在
git show-ref --verify --quiet refs/heads/%PERSONAL_BRANCH% >nul 2>&1
if errorlevel 1 (
    echo %WARNING_PREFIX% 分支 %PERSONAL_BRANCH% 不存在，跳过个人分支更新
    set "personal_branch_status=跳过（分支不存在）"
    goto :show_summary
)

REM 切换到个人分支
echo %INFO_PREFIX% 切换到个人分支 %PERSONAL_BRANCH%...
git checkout %PERSONAL_BRANCH%
if errorlevel 1 (
    echo %ERROR_PREFIX% 切换到个人分支失败！
    set "personal_branch_status=失败"
    pause
    exit /b 1
)

REM 获取更新前的提交数量
for /f %%i in ('git rev-list --count HEAD') do set "commits_before=%%i"

REM 创建备份分支
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set "backup_date=%%c%%a%%b"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "backup_time=%%a%%b"
set "backup_branch_name=%PERSONAL_BRANCH%-backup-%backup_date%-%backup_time%"
echo %INFO_PREFIX% 创建备份分支 %backup_branch_name%...
git checkout -b %backup_branch_name% >nul 2>&1
git checkout %PERSONAL_BRANCH% >nul 2>&1

REM 选择更新方式
echo 选择更新方式：
echo 1) Rebase (推荐，保持历史清洁)
echo 2) Merge (安全，保留完整历史)
set /p "choice=请选择 (1/2): "

if "%choice%"=="1" (
    echo %INFO_PREFIX% 使用rebase方式更新...
    set "rebase_method=Rebase"
    git rebase %MAIN_BRANCH%
    if errorlevel 1 (
        echo %ERROR_PREFIX% Rebase遇到冲突，请手动解决后运行：
        echo   git add ^<冲突文件^>
        echo   git rebase --continue
        echo 或者放弃rebase：
        echo   git rebase --abort
        set "personal_branch_status=失败（冲突）"
        set "conflicts_occurred=是"
        pause
        exit /b 1
    ) else (
        echo %SUCCESS_PREFIX% Rebase完成！
        set "personal_branch_status=成功"
    )
) else if "%choice%"=="2" (
    echo %INFO_PREFIX% 使用merge方式更新...
    set "rebase_method=Merge"
    git merge %MAIN_BRANCH%
    if errorlevel 1 (
        echo %ERROR_PREFIX% Merge遇到冲突，请手动解决后运行：
        echo   git add ^<冲突文件^>
        echo   git commit
        set "personal_branch_status=失败（冲突）"
        set "conflicts_occurred=是"
        pause
        exit /b 1
    ) else (
        echo %SUCCESS_PREFIX% Merge完成！
        set "personal_branch_status=成功"
    )
) else (
    echo %WARNING_PREFIX% 无效选择，跳过个人分支更新
    set "personal_branch_status=跳过（用户取消）"
    goto :show_summary
)

REM 获取更新后的提交数量
for /f %%i in ('git rev-list --count HEAD') do set "commits_after=%%i"

echo %SUCCESS_PREFIX% 个人分支 %PERSONAL_BRANCH% 更新完成！
echo %INFO_PREFIX% 备份分支已创建：%backup_branch_name%

:show_summary
echo.
echo ========================================
echo            同步操作总结报告
echo ========================================
echo.
echo 📊 %MAIN_BRANCH%分支同步结果：
echo    状态: %master_sync_status%
if %commits_behind% gtr 0 (
    echo    更新: 同步了 %commits_behind% 个提交
) else (
    echo    更新: 已是最新版本
)
if not "%master_files_changed%"=="" (
    echo    变更: %master_files_changed%
)
echo.
echo 🔧 个人分支处理结果：
echo    分支名称: %PERSONAL_BRANCH%
echo    处理状态: %personal_branch_status%
if not "%rebase_method%"=="" (
    echo    更新方式: %rebase_method%
)
if not "%backup_branch_name%"=="" (
    echo    备份分支: %backup_branch_name%
)
if %commits_before% gtr 0 if %commits_after% gtr 0 (
    echo    提交数量: %commits_before% → %commits_after%
)
echo.
echo 🚨 冲突情况：
echo    是否有冲突: %conflicts_occurred%
echo.
echo ========================================
echo.
if "%master_sync_status%"=="成功" if "%personal_branch_status%"=="成功" (
    echo ✅ 同步操作全部完成！您的代码已更新到最新版本。
) else (
    echo ⚠️  同步操作部分完成，请检查上述状态信息。
)
echo.

echo 按任意键退出...
pause >nul
