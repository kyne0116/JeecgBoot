@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ========================================
REM Git 仓库同步管理工具 - Windows版本
REM 用途：保持fork与官方仓库同步，并提供回退功能
REM 使用方法：
REM   sync-with-upstream.bat          - 执行同步操作
REM   sync-with-upstream.bat rollback - 回退到同步前状态
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
set "STATE_FILE=.sync-state.txt"

REM 初始化总结变量
set "master_sync_status=Not Started"
set "master_changes_count=0"
set "master_files_changed="
set "commits_behind=0"
set "personal_branch_status=Not Started"
set "backup_branch_name="
set "rebase_method="
set "conflicts_occurred=No"
set "commits_before=0"
set "commits_after=0"

REM 颜色定义（Windows CMD不支持ANSI颜色，使用文本标记）
set "INFO_PREFIX=[INFO]"
set "SUCCESS_PREFIX=[SUCCESS]"
set "WARNING_PREFIX=[WARNING]"
set "ERROR_PREFIX=[ERROR]"

echo ========================================
echo        Git Repository Sync Tool
echo ========================================
echo.
echo Configuration:
echo   Upstream repo: %UPSTREAM_REPO_URL%
echo   Origin repo: %ORIGIN_REPO_URL%
echo   Main branch: %MAIN_BRANCH%
echo   Personal branch: %PERSONAL_BRANCH%
echo ========================================
echo.

REM 检查参数
if "%1"=="rollback" goto :rollback_operation
if "%1"=="" goto :sync_operation
echo %ERROR_PREFIX% Invalid parameter. Use 'rollback' or no parameter.
echo Usage:
echo   %0          - Execute sync operation
echo   %0 rollback - Rollback to pre-sync state
pause
exit /b 1

:sync_operation
echo %INFO_PREFIX% Starting sync operation...
echo.

REM 保存同步前的Git状态
echo %INFO_PREFIX% Saving current Git state...
call :save_git_state
if errorlevel 1 (
    echo %ERROR_PREFIX% Failed to save Git state!
    pause
    exit /b 1
)

REM 记录当前分支，脚本结束时切换回来
echo %INFO_PREFIX% Recording current branch...
for /f %%i in ('git branch --show-current 2^>nul') do set "ORIGINAL_BRANCH=%%i"
if "!ORIGINAL_BRANCH!"=="" (
    echo %WARNING_PREFIX% Could not determine current branch, will stay on final branch
    set "ORIGINAL_BRANCH="
) else (
    echo %INFO_PREFIX% Current branch: !ORIGINAL_BRANCH!
)

REM Check if in git repository
echo %INFO_PREFIX% Checking Git repository status...
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo %ERROR_PREFIX% Current directory is not a Git repository!
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM Check for uncommitted changes
echo %INFO_PREFIX% Checking for uncommitted changes...
git diff-index --quiet HEAD -- >nul 2>&1
if errorlevel 1 (
    echo %WARNING_PREFIX% Detected uncommitted changes!
    echo Please commit or stash your changes first:
    git status --porcelain
    set /p "continue=Continue anyway? (y/N): "
    if /i not "!continue!"=="y" (
        echo %INFO_PREFIX% Operation cancelled
        echo Press any key to exit...
        pause >nul
        exit /b 0
    )
)

REM Check and add upstream repository
echo %INFO_PREFIX% Checking upstream repository configuration...
git remote get-url !UPSTREAM_REMOTE_NAME! >nul 2>&1
if errorlevel 1 (
    echo %INFO_PREFIX% Adding upstream repository...
    git remote add !UPSTREAM_REMOTE_NAME! !UPSTREAM_REPO_URL!
    if errorlevel 1 (
        echo %ERROR_PREFIX% Failed to add upstream repository!
        echo Press any key to exit...
        pause >nul
        exit /b 1
    )
    echo !SUCCESS_PREFIX! Upstream repository added
) else (
    echo !INFO_PREFIX! Upstream repository already exists
)

echo Current remote repository configuration:
git remote -v

echo.
echo !INFO_PREFIX! Starting sync for !MAIN_BRANCH! branch...

REM Switch to main branch
echo !INFO_PREFIX! Switching to !MAIN_BRANCH! branch...
git checkout !MAIN_BRANCH!
if errorlevel 1 (
    echo !ERROR_PREFIX! Failed to switch to !MAIN_BRANCH! branch!
    set "master_sync_status=Failed"
    goto :restore_branch_and_exit
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
    goto :restore_branch_and_exit
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
    goto :restore_branch_and_exit
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
echo !INFO_PREFIX! Starting update for personal branch !PERSONAL_BRANCH!...

REM 检查分支是否存在
git show-ref --verify --quiet refs/heads/!PERSONAL_BRANCH! >nul 2>&1
if errorlevel 1 (
    echo !WARNING_PREFIX! Branch !PERSONAL_BRANCH! does not exist, skipping personal branch update
    set "personal_branch_status=Skipped (branch not found)"
    goto :show_summary
)

REM 切换到个人分支
echo !INFO_PREFIX! Switching to personal branch !PERSONAL_BRANCH!...
git checkout !PERSONAL_BRANCH!
if errorlevel 1 (
    echo !ERROR_PREFIX! Failed to switch to personal branch!
    set "personal_branch_status=Failed"
    goto :restore_branch_and_exit
)

REM 获取更新前的提交数量
for /f %%i in ('git rev-list --count HEAD') do set "commits_before=%%i"

REM Create backup branch
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set "backup_date=%%c%%a%%b"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "backup_time=%%a%%b"
set "backup_branch_name=!PERSONAL_BRANCH!-backup-!backup_date!-!backup_time!"
echo !INFO_PREFIX! Creating backup branch !backup_branch_name!...
git checkout -b !backup_branch_name! >nul 2>&1
git checkout !PERSONAL_BRANCH! >nul 2>&1

REM Choose update method
echo Choose update method:
echo 1) Rebase (recommended, keeps clean history)
echo 2) Merge (safe, preserves complete history)
set /p "choice=Please choose (1/2): "

if "!choice!"=="1" (
    echo !INFO_PREFIX! Using rebase method...
    set "rebase_method=Rebase"
    git rebase !MAIN_BRANCH!
    if errorlevel 1 (
        echo !ERROR_PREFIX! Rebase encountered conflicts, please resolve manually:
        echo   git add ^<conflict-files^>
        echo   git rebase --continue
        echo Or abort rebase:
        echo   git rebase --abort
        set "personal_branch_status=Failed (conflicts)"
        set "conflicts_occurred=Yes"
        goto :restore_branch_and_exit
    ) else (
        echo !SUCCESS_PREFIX! Rebase completed!
        set "personal_branch_status=Success"
    )
) else if "!choice!"=="2" (
    echo !INFO_PREFIX! Using merge method...
    set "rebase_method=Merge"
    git merge !MAIN_BRANCH!
    if errorlevel 1 (
        echo !ERROR_PREFIX! Merge encountered conflicts, please resolve manually:
        echo   git add ^<conflict-files^>
        echo   git commit
        set "personal_branch_status=Failed (conflicts)"
        set "conflicts_occurred=Yes"
        goto :restore_branch_and_exit
    ) else (
        echo !SUCCESS_PREFIX! Merge completed!
        set "personal_branch_status=Success"
    )
) else (
    echo !WARNING_PREFIX! Invalid choice, skipping personal branch update
    set "personal_branch_status=Skipped (user cancelled)"
    goto :show_summary
)

REM 获取更新后的提交数量
for /f %%i in ('git rev-list --count HEAD') do set "commits_after=%%i"

echo !SUCCESS_PREFIX! Personal branch !PERSONAL_BRANCH! update completed!
echo !INFO_PREFIX! Backup branch created: !backup_branch_name!

:show_summary
echo.
echo ========================================
echo            Sync Operation Summary
echo ========================================
echo.
echo 📊 !MAIN_BRANCH! branch sync result:
echo    Status: !master_sync_status!
if !commits_behind! gtr 0 (
    echo    Updates: Synced !commits_behind! commits
) else (
    echo    Updates: Already up to date
)
if not "!master_files_changed!"=="" (
    echo    Changes: !master_files_changed!
)
echo.
echo 🔧 Personal branch processing result:
echo    Branch name: !PERSONAL_BRANCH!
echo    Processing status: !personal_branch_status!
if not "!rebase_method!"=="" (
    echo    Update method: !rebase_method!
)
if not "!backup_branch_name!"=="" (
    echo    Backup branch: !backup_branch_name!
)
if !commits_before! gtr 0 if !commits_after! gtr 0 (
    echo    Commit count: !commits_before! → !commits_after!
)
echo.
echo 🚨 Conflict status:
echo    Any conflicts: !conflicts_occurred!
echo.
echo ========================================
echo.
if "!master_sync_status!"=="Success" if "!personal_branch_status!"=="Success" (
    echo ✅ Sync operation completed successfully! Your code is updated to the latest version.
) else (
    echo ⚠️  Sync operation partially completed, please check the status information above.
)
echo.
echo %INFO_PREFIX% Sync operation completed, returning to %PERSONAL_BRANCH% branch
git checkout !PERSONAL_BRANCH! >nul 2>&1
echo Current branch:
git branch --show-current
echo.
echo Press any key to exit...
pause >nul
exit /b 0

:restore_branch_and_exit
echo.
echo %WARNING_PREFIX% Sync operation encountered error, trying to restore to %PERSONAL_BRANCH% branch...
git checkout !PERSONAL_BRANCH! >nul 2>&1
if errorlevel 1 (
    echo %WARNING_PREFIX% Cannot switch to %PERSONAL_BRANCH% branch, staying on current branch
) else (
    echo %SUCCESS_PREFIX% Restored to %PERSONAL_BRANCH% branch
)
echo Current branch:
git branch --show-current
echo.
echo Press any key to exit...
pause >nul
exit /b 1

:rollback_operation
echo %INFO_PREFIX% Starting rollback operation...
echo.
echo ========================================
echo        Rollback to Pre-sync State
echo ========================================
echo.

REM 检查状态文件是否存在
if not exist "!STATE_FILE!" (
    echo %ERROR_PREFIX% State file !STATE_FILE! not found!
    echo No previous sync operation found, or state file was deleted.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo %INFO_PREFIX% Loading saved Git state...
call :load_git_state
if errorlevel 1 (
    echo %ERROR_PREFIX% Failed to load Git state!
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo.
echo %WARNING_PREFIX% About to execute the following rollback operations:
echo   - Rollback %MAIN_BRANCH% branch to: !SAVED_MASTER_COMMIT!
echo   - Rollback %PERSONAL_BRANCH% branch to: !SAVED_PERSONAL_COMMIT!
echo   - Force push to remote repository (this will overwrite remote history)
echo.
echo %WARNING_PREFIX% This operation is irreversible, please confirm!
echo.
set /p "confirm=Confirm rollback operation? (y/N): "
if /i not "!confirm!"=="y" (
    echo %INFO_PREFIX% Rollback operation cancelled
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 0
)

echo.
echo %INFO_PREFIX% Starting rollback execution...

REM 回退master分支
echo %INFO_PREFIX% Rolling back %MAIN_BRANCH% branch...
git checkout !MAIN_BRANCH! >nul 2>&1
if errorlevel 1 (
    echo %ERROR_PREFIX% Cannot switch to %MAIN_BRANCH% branch!
    goto :rollback_failed
)

git reset --hard !SAVED_MASTER_COMMIT! >nul 2>&1
if errorlevel 1 (
    echo %ERROR_PREFIX% Failed to rollback %MAIN_BRANCH% branch!
    goto :rollback_failed
)
echo %SUCCESS_PREFIX% %MAIN_BRANCH% branch rolled back to !SAVED_MASTER_COMMIT!

REM 强制推送master分支
echo %INFO_PREFIX% Force pushing %MAIN_BRANCH% branch to remote repository...
git push !ORIGIN_REMOTE_NAME! !MAIN_BRANCH! --force >nul 2>&1
if errorlevel 1 (
    echo %WARNING_PREFIX% Failed to push %MAIN_BRANCH% branch to remote, may need manual push
) else (
    echo %SUCCESS_PREFIX% %MAIN_BRANCH% branch force pushed to remote repository
)

REM 回退个人分支
echo %INFO_PREFIX% Rolling back %PERSONAL_BRANCH% branch...
git checkout !PERSONAL_BRANCH! >nul 2>&1
if errorlevel 1 (
    echo %ERROR_PREFIX% Cannot switch to %PERSONAL_BRANCH% branch!
    goto :rollback_failed
)

git reset --hard !SAVED_PERSONAL_COMMIT! >nul 2>&1
if errorlevel 1 (
    echo %ERROR_PREFIX% Failed to rollback %PERSONAL_BRANCH% branch!
    goto :rollback_failed
)
echo %SUCCESS_PREFIX% %PERSONAL_BRANCH% branch rolled back to !SAVED_PERSONAL_COMMIT!

REM 强制推送个人分支
echo %INFO_PREFIX% Force pushing %PERSONAL_BRANCH% branch to remote repository...
git push !ORIGIN_REMOTE_NAME! !PERSONAL_BRANCH! --force >nul 2>&1
if errorlevel 1 (
    echo %WARNING_PREFIX% Failed to push %PERSONAL_BRANCH% branch to remote, may need manual push
) else (
    echo %SUCCESS_PREFIX% %PERSONAL_BRANCH% branch force pushed to remote repository
)

echo.
echo %SUCCESS_PREFIX% Rollback operation completed!
echo Current branch: %PERSONAL_BRANCH%
echo Git state has been restored to pre-sync state.
echo.
echo Press any key to exit...
pause >nul
exit /b 0

:rollback_failed
echo.
echo %ERROR_PREFIX% Rollback operation failed!
echo Please check Git status and handle manually.
echo.
echo Press any key to exit...
pause >nul
exit /b 1

REM ========================================
REM 子程序：保存Git状态
REM ========================================
:save_git_state
echo %INFO_PREFIX% Saving current Git state to %STATE_FILE%...

REM 检查Git仓库状态
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo %ERROR_PREFIX% Current directory is not a Git repository!
    exit /b 1
)

REM 获取当前分支
for /f %%i in ('git branch --show-current 2^>nul') do set "CURRENT_BRANCH=%%i"
if "!CURRENT_BRANCH!"=="" (
    echo %ERROR_PREFIX% Cannot determine current branch!
    exit /b 1
)

REM 获取master分支的commit hash
git show-ref --verify --quiet refs/heads/!MAIN_BRANCH! >nul 2>&1
if errorlevel 1 (
    echo %ERROR_PREFIX% %MAIN_BRANCH% branch does not exist!
    exit /b 1
)
for /f %%i in ('git rev-parse !MAIN_BRANCH! 2^>nul') do set "MASTER_COMMIT=%%i"

REM 获取个人分支的commit hash
git show-ref --verify --quiet refs/heads/!PERSONAL_BRANCH! >nul 2>&1
if errorlevel 1 (
    echo %WARNING_PREFIX% %PERSONAL_BRANCH% branch does not exist, will record as empty
    set "PERSONAL_COMMIT="
) else (
    for /f %%i in ('git rev-parse !PERSONAL_BRANCH! 2^>nul') do set "PERSONAL_COMMIT=%%i"
)

REM 获取当前时间戳
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set "SAVE_DATE=%%c-%%a-%%b"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "SAVE_TIME=%%a:%%b"

REM 保存状态到文件
echo # Git Sync State File > "!STATE_FILE!"
echo # Save Time: !SAVE_DATE! !SAVE_TIME! >> "!STATE_FILE!"
echo CURRENT_BRANCH=!CURRENT_BRANCH! >> "!STATE_FILE!"
echo MASTER_COMMIT=!MASTER_COMMIT! >> "!STATE_FILE!"
echo PERSONAL_COMMIT=!PERSONAL_COMMIT! >> "!STATE_FILE!"
echo SAVE_TIMESTAMP=!SAVE_DATE!_!SAVE_TIME! >> "!STATE_FILE!"

echo %SUCCESS_PREFIX% Git state saved
echo   Current branch: !CURRENT_BRANCH!
echo   %MAIN_BRANCH% branch: !MASTER_COMMIT!
if not "!PERSONAL_COMMIT!"=="" (
    echo   %PERSONAL_BRANCH% branch: !PERSONAL_COMMIT!
)
exit /b 0

REM ========================================
REM 子程序：加载Git状态
REM ========================================
:load_git_state
echo %INFO_PREFIX% Loading Git state from %STATE_FILE%...

REM 读取状态文件
for /f "usebackq tokens=1,2 delims==" %%a in ("!STATE_FILE!") do (
    if "%%a"=="CURRENT_BRANCH" set "SAVED_CURRENT_BRANCH=%%b"
    if "%%a"=="MASTER_COMMIT" set "SAVED_MASTER_COMMIT=%%b"
    if "%%a"=="PERSONAL_COMMIT" set "SAVED_PERSONAL_COMMIT=%%b"
    if "%%a"=="SAVE_TIMESTAMP" set "SAVED_TIMESTAMP=%%b"
)

REM 验证必要的变量
if "!SAVED_MASTER_COMMIT!"=="" (
    echo %ERROR_PREFIX% Missing %MAIN_BRANCH% branch info in state file!
    exit /b 1
)

echo %SUCCESS_PREFIX% Git state loaded successfully
echo   Save time: !SAVED_TIMESTAMP!
echo   Original branch: !SAVED_CURRENT_BRANCH!
echo   %MAIN_BRANCH% branch: !SAVED_MASTER_COMMIT!
if not "!SAVED_PERSONAL_COMMIT!"=="" (
    echo   %PERSONAL_BRANCH% branch: !SAVED_PERSONAL_COMMIT!
)
exit /b 0
