@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Save the full path of this script to avoid issues when switching branches
set "SCRIPT_PATH=%~dp0%~nx0"

REM ========================================
REM Git Repository Sync Tool - Windows Version
REM Purpose: Keep fork synchronized with official repository and update personal branch
REM ========================================

REM ========================================
REM Configuration Variables - Modify these variables for your project
REM ========================================
set "UPSTREAM_REPO_URL=https://github.com/jeecgboot/JeecgBoot.git"
set "ORIGIN_REPO_URL=https://github.com/kyne0116/JeecgBoot.git"
set "MAIN_BRANCH=master"
set "PERSONAL_BRANCH=my-custom"
set "UPSTREAM_REMOTE_NAME=upstream"
set "ORIGIN_REMOTE_NAME=origin"

REM Initialize summary variables
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

REM Color definitions (Windows CMD doesn't support ANSI colors, use text markers)
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

echo %INFO_PREFIX% Starting sync operation...
echo.

REM Record current branch for information
echo %INFO_PREFIX% Recording current branch...
for /f %%i in ('git branch --show-current 2^^^>nul') do set "CURRENT_BRANCH_INFO=%%i"
if "!CURRENT_BRANCH_INFO!"=="" (
    echo %WARNING_PREFIX% Could not determine current branch
) else (
    echo %INFO_PREFIX% Current branch: !CURRENT_BRANCH_INFO!
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
git remote get-url %UPSTREAM_REMOTE_NAME% >nul 2>&1
if errorlevel 1 (
    echo %INFO_PREFIX% Adding upstream repository...
    git remote add %UPSTREAM_REMOTE_NAME% %UPSTREAM_REPO_URL%
    if errorlevel 1 (
        echo %ERROR_PREFIX% Failed to add upstream repository!
        echo Press any key to exit...
        pause >nul
        exit /b 1
    )
    echo %SUCCESS_PREFIX% Upstream repository added
) else (
    echo %INFO_PREFIX% Upstream repository already exists
)

echo Current remote repository configuration:
git remote -v

echo.
echo %INFO_PREFIX% Starting sync for %MAIN_BRANCH% branch...

REM Record current branch to restore later
for /f %%i in ('git branch --show-current 2^^^>nul') do set "ORIGINAL_BRANCH=%%i"
if "!ORIGINAL_BRANCH!"=="" set "ORIGINAL_BRANCH=%PERSONAL_BRANCH%"

REM Check if we need to switch to main branch
if not "!ORIGINAL_BRANCH!"=="%MAIN_BRANCH%" (
    echo %INFO_PREFIX% Switching to %MAIN_BRANCH% branch...
    git checkout %MAIN_BRANCH%
    if errorlevel 1 (
        echo %ERROR_PREFIX% Failed to switch to %MAIN_BRANCH% branch!
        set "master_sync_status=Failed"
        goto :restore_branch_and_exit
    )
) else (
    echo %INFO_PREFIX% Already on %MAIN_BRANCH% branch
)

REM Change back to the directory where the script is located
cd /d "%~dp0"

REM Get commits behind count
for /f %%i in ('git rev-list --count HEAD..%UPSTREAM_REMOTE_NAME%/%MAIN_BRANCH% 2^^^>nul') do set "commits_behind=%%i"
if "!commits_behind!"=="" set "commits_behind=0"

REM Fetch upstream updates
echo %INFO_PREFIX% Fetching upstream repository updates...
git fetch %UPSTREAM_REMOTE_NAME%
if errorlevel 1 (
    echo %ERROR_PREFIX% Failed to fetch upstream updates!
    set "master_sync_status=Failed"
    goto :restore_branch_and_exit
)

REM Recalculate commits behind count
for /f %%i in ('git rev-list --count HEAD..%UPSTREAM_REMOTE_NAME%/%MAIN_BRANCH% 2^^^>nul') do set "commits_behind=%%i"
if "!commits_behind!"=="" set "commits_behind=0"

REM Merge upstream updates
echo %INFO_PREFIX% Merging upstream updates to local %MAIN_BRANCH%...
git merge %UPSTREAM_REMOTE_NAME%/%MAIN_BRANCH% --stat > temp_merge_output.txt 2>&1
if errorlevel 1 (
    echo %ERROR_PREFIX% Failed to merge upstream updates! Conflicts may need manual resolution
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
echo %INFO_PREFIX% Pushing updates to your fork...
git push %ORIGIN_REMOTE_NAME% %MAIN_BRANCH%
if errorlevel 1 (
    echo %WARNING_PREFIX% Failed to push to fork, may need manual push
    set "master_sync_status=Partial Success"
)

echo %SUCCESS_PREFIX% %MAIN_BRANCH% branch sync completed!

REM Switch back to original branch immediately after master sync
if not "!ORIGINAL_BRANCH!"=="%MAIN_BRANCH%" (
    echo %INFO_PREFIX% Switching back to !ORIGINAL_BRANCH! branch...
    git checkout !ORIGINAL_BRANCH!
    if errorlevel 1 (
        echo %WARNING_PREFIX% Failed to switch back to !ORIGINAL_BRANCH! branch
        set "personal_branch_status=Failed (cannot switch back)"
        goto :show_summary
    )
)

echo.
echo %INFO_PREFIX% Starting update for personal branch %PERSONAL_BRANCH%...

REM Check if branch exists
git show-ref --verify --quiet refs/heads/%PERSONAL_BRANCH% >nul 2>&1
if errorlevel 1 (
    echo %WARNING_PREFIX% Branch %PERSONAL_BRANCH% does not exist, skipping personal branch update
    set "personal_branch_status=Skipped (branch not found)"
    goto :show_summary
)

REM Switch to personal branch
echo %INFO_PREFIX% Switching to personal branch %PERSONAL_BRANCH%...
git checkout %PERSONAL_BRANCH%
if errorlevel 1 (
    echo %ERROR_PREFIX% Failed to switch to personal branch!
    set "personal_branch_status=Failed"
    goto :restore_branch_and_exit
)

REM Get commit count before update
for /f %%i in ('git rev-list --count HEAD') do set "commits_before=%%i"

REM Create backup branch
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set "backup_date=%%c%%a%%b"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "backup_time=%%a%%b"
set "backup_branch_name=!PERSONAL_BRANCH!-backup-!backup_date!-!backup_time!"
echo %INFO_PREFIX% Creating backup branch !backup_branch_name!...
git checkout -b !backup_branch_name! >nul 2>&1
git checkout %PERSONAL_BRANCH% >nul 2>&1

REM Choose update method
echo Choose update method:
echo 1^) Rebase ^(recommended, keeps clean history^)
echo 2^) Merge ^(safe, preserves complete history^)
set /p "choice=Please choose (1/2): "

if "!choice!"=="1" (
    echo %INFO_PREFIX% Using rebase method...
    set "rebase_method=Rebase"
    git rebase %MAIN_BRANCH%
    if errorlevel 1 (
        echo %ERROR_PREFIX% Rebase encountered conflicts, please resolve manually:
        echo   git add ^<conflict-files^>
        echo   git rebase --continue
        echo Or abort rebase:
        echo   git rebase --abort
        set "personal_branch_status=Failed (conflicts)"
        set "conflicts_occurred=Yes"
        goto :restore_branch_and_exit
    ) else (
        echo %SUCCESS_PREFIX% Rebase completed!
        set "personal_branch_status=Success"
    )
) else if "!choice!"=="2" (
    echo %INFO_PREFIX% Using merge method...
    set "rebase_method=Merge"
    git merge %MAIN_BRANCH%
    if errorlevel 1 (
        echo %ERROR_PREFIX% Merge encountered conflicts, please resolve manually:
        echo   git add ^<conflict-files^>
        echo   git commit
        set "personal_branch_status=Failed (conflicts)"
        set "conflicts_occurred=Yes"
        goto :restore_branch_and_exit
    ) else (
        echo %SUCCESS_PREFIX% Merge completed!
        set "personal_branch_status=Success"
    )
) else (
    echo %WARNING_PREFIX% Invalid choice, skipping personal branch update
    set "personal_branch_status=Skipped (user cancelled)"
    goto :show_summary
)

REM Get commit count after update
for /f %%i in ('git rev-list --count HEAD') do set "commits_after=%%i"

echo %SUCCESS_PREFIX% Personal branch %PERSONAL_BRANCH% update completed!
echo %INFO_PREFIX% Backup branch created: !backup_branch_name!

:show_summary
echo.
echo ========================================
echo            Sync Operation Summary
echo ========================================
echo.
echo %MAIN_BRANCH% branch sync result:
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
echo Personal branch processing result:
echo    Branch name: %PERSONAL_BRANCH%
echo    Processing status: !personal_branch_status!
if not "!rebase_method!"=="" (
    echo    Update method: !rebase_method!
)
if not "!backup_branch_name!"=="" (
    echo    Backup branch: !backup_branch_name!
)
if !commits_before! gtr 0 if !commits_after! gtr 0 (
    echo    Commit count: !commits_before! to !commits_after!
)
echo.
echo Conflict status:
echo    Any conflicts: !conflicts_occurred!
echo.
echo ========================================
echo.
if "!master_sync_status!"=="Success" if "!personal_branch_status!"=="Success" (
    echo Sync operation completed successfully! Your code is updated to the latest version.
) else (
    echo Sync operation partially completed, please check the status information above.
)
echo.
if not "!backup_branch_name!"=="" (
    echo %INFO_PREFIX% Backup branch created: !backup_branch_name!
    echo If you need to rollback, use:
    echo   git reset --hard !backup_branch_name!
    echo   git push origin %PERSONAL_BRANCH% --force
    echo.
)
echo %INFO_PREFIX% Sync operation completed
echo Current branch:
git branch --show-current
echo.
echo Press any key to exit...
pause >nul
exit /b 0

:restore_branch_and_exit
echo.
echo %WARNING_PREFIX% Sync operation encountered error, trying to restore to original branch...
if not "!ORIGINAL_BRANCH!"=="" (
    echo %INFO_PREFIX% Attempting to restore to !ORIGINAL_BRANCH! branch...
    git checkout !ORIGINAL_BRANCH! >nul 2>&1
    if errorlevel 1 (
        echo %WARNING_PREFIX% Cannot switch to !ORIGINAL_BRANCH! branch, trying %PERSONAL_BRANCH%...
        git checkout %PERSONAL_BRANCH% >nul 2>&1
        if errorlevel 1 (
            echo %WARNING_PREFIX% Cannot switch to %PERSONAL_BRANCH% branch, staying on current branch
        ) else (
            echo %SUCCESS_PREFIX% Restored to %PERSONAL_BRANCH% branch
        )
    ) else (
        echo %SUCCESS_PREFIX% Restored to !ORIGINAL_BRANCH! branch
    )
) else (
    echo %INFO_PREFIX% Attempting to restore to %PERSONAL_BRANCH% branch...
    git checkout %PERSONAL_BRANCH% >nul 2>&1
    if errorlevel 1 (
        echo %WARNING_PREFIX% Cannot switch to %PERSONAL_BRANCH% branch, staying on current branch
    ) else (
        echo %SUCCESS_PREFIX% Restored to %PERSONAL_BRANCH% branch
    )
)
echo Current branch:
git branch --show-current
echo.
echo Press any key to exit...
pause >nul
exit /b 1