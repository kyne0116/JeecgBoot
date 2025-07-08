@echo off
setlocal enabledelayedexpansion

REM Universal Repository Sync Script (Windows Version)
REM Purpose: Keep fork synced with official repository and update personal branch

REM ========================================
REM Configuration Variables - Modify these for your project
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
set "personal_branch_status=Not Started"
set "backup_branch_name="
set "rebase_method="
set "conflicts_occurred=No"

echo ========================================
echo     Universal Repository Sync Script
echo ========================================
echo.
echo Configuration:
echo   Upstream: %UPSTREAM_REPO_URL%
echo   Origin: %ORIGIN_REPO_URL%
echo   Main Branch: %MAIN_BRANCH%
echo   Personal Branch: %PERSONAL_BRANCH%
echo ========================================
echo.

REM Check if in git repository
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Current directory is not a Git repository!
    pause
    exit /b 1
)

REM Check for uncommitted changes
git diff-index --quiet HEAD -- >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Uncommitted changes detected!
    echo Please commit or stash your changes first:
    git status --porcelain
    echo.
    set /p continue="Continue anyway? (y/N): "
    if /i "!continue!" NEQ "y" (
        echo [INFO] Operation cancelled
        pause
        exit /b 0
    )
    echo [INFO] Continuing with uncommitted changes...
)

REM Check and add upstream repository
echo [INFO] Checking upstream repository configuration...
git remote get-url %UPSTREAM_REMOTE_NAME% >nul 2>&1
if errorlevel 1 (
    echo [INFO] Adding upstream repository...
    git remote add %UPSTREAM_REMOTE_NAME% %UPSTREAM_REPO_URL%
    if errorlevel 1 (
        echo [ERROR] Failed to add upstream repository!
        pause
        exit /b 1
    )
    echo [SUCCESS] Upstream repository added
) else (
    echo [INFO] Upstream repository already exists
)

echo.
echo Current remote repository configuration:
git remote -v
echo.

REM Sync main branch
echo [INFO] Starting %MAIN_BRANCH% branch sync...
echo.

echo [INFO] Switching to %MAIN_BRANCH% branch...
git checkout %MAIN_BRANCH%
if errorlevel 1 (
    echo [ERROR] Failed to switch to %MAIN_BRANCH% branch!
    set "master_sync_status=Failed"
    pause
    exit /b 1
)

echo [INFO] Fetching upstream updates...
git fetch %UPSTREAM_REMOTE_NAME%
if errorlevel 1 (
    echo [ERROR] Failed to fetch upstream updates!
    set "master_sync_status=Failed"
    pause
    exit /b 1
)

REM Get merge statistics before merge
for /f "tokens=*" %%i in ('git rev-list --count HEAD..%UPSTREAM_REMOTE_NAME%/%MAIN_BRANCH%') do set "commits_behind=%%i"

echo [INFO] Merging upstream updates to local %MAIN_BRANCH%...
git merge %UPSTREAM_REMOTE_NAME%/%MAIN_BRANCH% --stat > merge_output.tmp 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to merge upstream updates! Conflicts may need manual resolution
    set "master_sync_status=Failed"
    set "conflicts_occurred=Yes"
    pause
    exit /b 1
) else (
    REM Parse merge statistics
    for /f "tokens=*" %%i in ('findstr /C:"files changed" merge_output.tmp') do set "master_files_changed=%%i"
    if "!master_files_changed!"=="" set "master_files_changed=No file changes"
    set "master_sync_status=Success"
)

echo [INFO] Pushing updates to your fork...
git push %ORIGIN_REMOTE_NAME% %MAIN_BRANCH%
if errorlevel 1 (
    echo [WARNING] Failed to push to fork, may need manual push
    set "master_sync_status=Partial Success"
)

del merge_output.tmp >nul 2>&1
echo [SUCCESS] %MAIN_BRANCH% branch sync completed!
echo.

REM Update personal branch
set branch_name=%PERSONAL_BRANCH%
echo [INFO] Starting personal branch %branch_name% update...

REM Check if branch exists
git show-ref --verify --quiet refs/heads/%branch_name% >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Branch %branch_name% does not exist, skipping personal branch update
    set "personal_branch_status=Skipped (Branch not found)"
    goto :summary
)

echo [INFO] Switching to personal branch %branch_name%...
git checkout %branch_name%
if errorlevel 1 (
    echo [ERROR] Failed to switch to personal branch!
    set "personal_branch_status=Failed"
    pause
    exit /b 1
)

REM Get commit count before update
for /f "tokens=*" %%i in ('git rev-list --count HEAD') do set "commits_before=%%i"

REM Create backup branch
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set mydate=%%c%%a%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set mytime=%%a%%b
set mytime=!mytime: =0!
set backup_branch=%branch_name%-backup-!mydate!-!mytime!
set "backup_branch_name=!backup_branch!"

echo [INFO] Creating backup branch !backup_branch!...
git checkout -b !backup_branch! >nul 2>&1
git checkout %branch_name% >nul 2>&1

echo.
echo Choose update method:
echo 1) Rebase (recommended, keeps clean history)
echo 2) Merge (safe, preserves complete history)
set /p choice="Please choose (1/2): "

if "!choice!"=="1" (
    echo [INFO] Using rebase method...
    set "rebase_method=Rebase"
    git rebase %MAIN_BRANCH%
    if errorlevel 1 (
        echo [ERROR] Rebase encountered conflicts, please resolve manually then run:
        echo   git add ^<conflict-files^>
        echo   git rebase --continue
        echo Or abort rebase:
        echo   git rebase --abort
        set "personal_branch_status=Failed (Conflicts)"
        set "conflicts_occurred=Yes"
        pause
        exit /b 1
    )
    echo [SUCCESS] Rebase completed!
    set "personal_branch_status=Success"
) else if "!choice!"=="2" (
    echo [INFO] Using merge method...
    set "rebase_method=Merge"
    git merge %MAIN_BRANCH%
    if errorlevel 1 (
        echo [ERROR] Merge encountered conflicts, please resolve manually then run:
        echo   git add ^<conflict-files^>
        echo   git commit
        set "personal_branch_status=Failed (Conflicts)"
        set "conflicts_occurred=Yes"
        pause
        exit /b 1
    )
    echo [SUCCESS] Merge completed!
    set "personal_branch_status=Success"
) else (
    echo [WARNING] Invalid choice, skipping personal branch update
    set "personal_branch_status=Skipped (User cancelled)"
    goto :summary
)

REM Get commit count after update
for /f "tokens=*" %%i in ('git rev-list --count HEAD') do set "commits_after=%%i"

echo [SUCCESS] Personal branch %branch_name% update completed!
echo [INFO] Backup branch created: !backup_branch!

:summary
echo.
echo ========================================
echo           Sync Operation Summary
echo ========================================
echo.
echo %MAIN_BRANCH% Branch Sync Result:
echo    Status: %master_sync_status%
if not "%commits_behind%"=="" (
    if %commits_behind% GTR 0 (
        echo    Updates: Synced %commits_behind% commits
    ) else (
        echo    Updates: Already up to date
    )
)
if not "%master_files_changed%"=="" (
    echo    Changes: %master_files_changed%
)
echo.
echo Personal Branch Processing Result:
echo    Branch Name: %branch_name%
echo    Status: %personal_branch_status%
if not "%rebase_method%"=="" (
    echo    Update Method: %rebase_method%
)
if not "%backup_branch_name%"=="" (
    echo    Backup Branch: %backup_branch_name%
)
if not "%commits_before%"=="" if not "%commits_after%"=="" (
    echo    Commit Count: %commits_before% -^> %commits_after%
)
echo.
echo Conflict Status:
echo    Conflicts Occurred: %conflicts_occurred%
echo.
echo ========================================
echo.
if "%master_sync_status%"=="Success" if "%personal_branch_status%"=="Success" (
    echo [SUCCESS] All sync operations completed! Your code is up to date.
) else (
    echo [WARNING] Sync operations partially completed, please check status above.
)
echo.
echo Press any key to exit...
pause >nul
