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

REM ========================================
REM Smart Sync Configuration
REM ========================================
REM Enable selective sync mode (avoids conflicts with sync scripts)
set "SELECTIVE_SYNC_MODE=true"
REM Skip commits that modify sync scripts to avoid conflicts
set "SKIP_SYNC_SCRIPT_COMMITS=true"

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
for /f "delims=" %%i in ('git branch --show-current 2^>nul') do set "CURRENT_BRANCH_INFO=%%i"
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

REM Check and configure safe directory if needed (for Git 2.35.2+)
echo %INFO_PREFIX% Checking Git safe directory configuration...
git config --global --get-all safe.directory | findstr /C:"%CD%" >nul 2>&1
if errorlevel 1 (
    echo %INFO_PREFIX% Adding current directory to Git safe directories...
    git config --global --add safe.directory "%CD%"
    if errorlevel 1 (
        echo %WARNING_PREFIX% Could not add directory to safe.directory config
        echo %WARNING_PREFIX% You may need to run: git config --global --add safe.directory "%CD%"
    ) else (
        echo %SUCCESS_PREFIX% Directory added to Git safe directories
    )
) else (
    echo %INFO_PREFIX% Directory is already in Git safe directories
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
for /f "delims=" %%i in ('git branch --show-current 2^>nul') do set "ORIGINAL_BRANCH=%%i"
if "!ORIGINAL_BRANCH!"=="" set "ORIGINAL_BRANCH=%PERSONAL_BRANCH%"

REM Use a safer approach: update master branch without switching to it
echo %INFO_PREFIX% Updating local %MAIN_BRANCH% branch from upstream (without switching)...

REM Change back to the directory where the script is located
cd /d "%~dp0"

REM Get commits behind count for master branch
echo %INFO_PREFIX% Getting initial commits behind count...
for /f "delims=" %%i in ('git rev-list --count %MAIN_BRANCH%..%UPSTREAM_REMOTE_NAME%/%MAIN_BRANCH% 2^>nul') do set "commits_behind=%%i"
if "!commits_behind!"=="" set "commits_behind=0"
echo %INFO_PREFIX% Initial commits behind: !commits_behind!

REM Fetch upstream updates
echo %INFO_PREFIX% Fetching upstream repository updates...
echo %INFO_PREFIX% Running: git fetch %UPSTREAM_REMOTE_NAME%
git fetch %UPSTREAM_REMOTE_NAME% 2>&1
if errorlevel 1 (
    echo %ERROR_PREFIX% Failed to fetch upstream updates!
    echo %ERROR_PREFIX% Git fetch command returned error code: %errorlevel%
    set "master_sync_status=Failed"
    goto :restore_branch_and_exit
)
echo %SUCCESS_PREFIX% Fetch completed successfully

REM Recalculate commits behind count
echo %INFO_PREFIX% Calculating commits behind count...
for /f "delims=" %%i in ('git rev-list --count %MAIN_BRANCH%..%UPSTREAM_REMOTE_NAME%/%MAIN_BRANCH% 2^>nul') do set "commits_behind=%%i"
if "!commits_behind!"=="" set "commits_behind=0"
echo %INFO_PREFIX% Commits behind: !commits_behind!

echo %INFO_PREFIX% Checking if updates are needed...
set /a "commits_check=!commits_behind!"

REM Use goto instead of if-else to avoid parsing issues
if !commits_check! gtr 0 goto :update_master_branch
goto :master_already_updated

:update_master_branch
echo %INFO_PREFIX% Found !commits_behind! new commits, updating local %MAIN_BRANCH% branch...

REM Update master branch using git update-ref (safer than checkout + merge)
git update-ref refs/heads/%MAIN_BRANCH% %UPSTREAM_REMOTE_NAME%/%MAIN_BRANCH%
if errorlevel 1 (
    echo %ERROR_PREFIX% Failed to update local %MAIN_BRANCH% branch!
    set "master_sync_status=Failed"
    goto :restore_branch_and_exit
)

REM Check if origin has commits not in upstream before force push
echo %INFO_PREFIX% Checking if your fork has unique commits on master branch...
for /f "delims=" %%i in ('git rev-list --count %UPSTREAM_REMOTE_NAME%/%MAIN_BRANCH%..%ORIGIN_REMOTE_NAME%/%MAIN_BRANCH% 2^>nul') do set "origin_ahead=%%i"
if "!origin_ahead!"=="" set "origin_ahead=0"

if !origin_ahead! gtr 0 (
    echo %WARNING_PREFIX% Your fork has !origin_ahead! commits on master that are not in upstream!
    echo %WARNING_PREFIX% This indicates you may have made commits directly to master branch.
    echo.
    echo These commits will be lost if you continue with force push:
    git log --oneline %UPSTREAM_REMOTE_NAME%/%MAIN_BRANCH%..%ORIGIN_REMOTE_NAME%/%MAIN_BRANCH%
    echo.
    echo Recommendations:
    echo   1^) Create a backup branch for these commits first
    echo   2^) Cherry-pick important commits to your personal branch
    echo   3^) Only continue if you're sure these commits are not needed
    echo.
    set /p "force_confirm=Do you want to force push anyway and lose these commits? (y/N): "
    if /i not "!force_confirm!"=="y" (
        echo %INFO_PREFIX% Force push cancelled to preserve your commits
        echo %INFO_PREFIX% Consider backing up these commits before running sync again
        set "master_sync_status=Cancelled (preserving fork commits)"
        goto :personal_branch_update
    )
    echo %WARNING_PREFIX% Proceeding with force push - your fork commits will be lost!
) else (
    echo %INFO_PREFIX% Your fork master is clean (no unique commits), safe to force push
)

REM Push to fork (force push to ensure sync)
echo %INFO_PREFIX% Pushing updates to your fork...
echo %WARNING_PREFIX% This will force-push to ensure master branch sync with upstream
git push %ORIGIN_REMOTE_NAME% %MAIN_BRANCH% --force
if errorlevel 1 (
    echo %WARNING_PREFIX% Failed to push to fork, may need manual push
    set "master_sync_status=Partial Success"
) else (
    set "master_sync_status=Success"
)
set "master_files_changed=Updated !commits_behind! commits"
goto :master_sync_completed

:master_already_updated
echo %INFO_PREFIX% Local %MAIN_BRANCH% branch is already up to date
set "master_sync_status=Already up to date"
set "master_files_changed=No changes needed"
goto :master_sync_completed

:master_sync_completed

echo %SUCCESS_PREFIX% %MAIN_BRANCH% branch sync completed!

:personal_branch_update
echo.
echo %INFO_PREFIX% Starting update for personal branch %PERSONAL_BRANCH%...

REM Check if branch exists
echo %INFO_PREFIX% Checking if branch %PERSONAL_BRANCH% exists...
git show-ref --verify --quiet refs/heads/%PERSONAL_BRANCH% >nul 2>&1
if errorlevel 1 (
    echo %WARNING_PREFIX% Branch %PERSONAL_BRANCH% does not exist, skipping personal branch update
    set "personal_branch_status=Skipped (branch not found)"
    goto :show_summary
)
echo %INFO_PREFIX% Branch %PERSONAL_BRANCH% exists, proceeding...

REM Switch to personal branch
echo %INFO_PREFIX% Switching to personal branch %PERSONAL_BRANCH%...
git checkout %PERSONAL_BRANCH%
if errorlevel 1 (
    echo %ERROR_PREFIX% Failed to switch to personal branch!
    set "personal_branch_status=Failed"
    goto :restore_branch_and_exit
)

REM Get commit count before update
for /f "delims=" %%i in ('git rev-list --count HEAD 2^>nul') do set "commits_before=%%i"

REM Create backup branch with numeric timestamp (YYYYMMDD-HHMMSS format)
for /f "delims=" %%i in ('powershell -command "Get-Date -Format 'yyyyMMdd-HHmmss'"') do set "timestamp=%%i"
set "backup_branch_name=!PERSONAL_BRANCH!-backup-!timestamp!"
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

    REM Smart sync: Check for potential conflicts with sync scripts
    if "%SELECTIVE_SYNC_MODE%"=="true" (
        echo %INFO_PREFIX% Smart sync mode enabled - checking for potential conflicts...
        git log --oneline %MAIN_BRANCH%..HEAD | findstr /i "sync" >nul 2>&1
        if not errorlevel 1 (
            echo %WARNING_PREFIX% Detected sync-related commits that may conflict
            echo %INFO_PREFIX% Recommendation: Use selective cherry-pick instead of full rebase
            echo.
            echo Choose sync strategy:
            echo 1^) Continue with full rebase ^(may have conflicts^)
            echo 2^) Use selective cherry-pick ^(recommended^)
            echo 3^) Skip sync and keep current state
            set /p "sync_strategy=Please choose (1/2/3): "

            if "!sync_strategy!"=="2" (
                echo %INFO_PREFIX% Using selective cherry-pick strategy...
                call :selective_cherry_pick
                goto :show_summary
            ) else if "!sync_strategy!"=="3" (
                echo %INFO_PREFIX% Skipping sync, keeping current state
                set "personal_branch_status=Skipped (user choice)"
                goto :show_summary
            )
            echo %INFO_PREFIX% Continuing with full rebase...
        )
    )

    git rebase %MAIN_BRANCH%
    if errorlevel 1 (
        echo %ERROR_PREFIX% Rebase encountered conflicts!
        echo.
        echo Choose how to handle the conflicts:
        echo 1^) Abort rebase and return to original state ^(recommended^)
        echo 2^) Leave in conflict state for manual resolution
        set /p "conflict_choice=Please choose (1/2): "

        if "!conflict_choice!"=="1" (
            echo %INFO_PREFIX% Aborting rebase and returning to original state...
            git rebase --abort
            if errorlevel 1 (
                echo %WARNING_PREFIX% Failed to abort rebase, manual intervention required
                set "personal_branch_status=Failed (rebase abort failed)"
            ) else (
                echo %SUCCESS_PREFIX% Rebase aborted, returned to original state
                set "personal_branch_status=Aborted (conflicts)"
            )
        ) else (
            echo %INFO_PREFIX% Leaving in conflict state for manual resolution
            echo Please resolve conflicts manually:
            echo   git add ^<conflict-files^>
            echo   git rebase --continue
            echo Or abort rebase later:
            echo   git rebase --abort
            set "personal_branch_status=Manual resolution required"
            set "conflicts_occurred=Yes"
            goto :show_summary
        )
        set "conflicts_occurred=Yes"
    ) else (
        echo %SUCCESS_PREFIX% Rebase completed!
        set "personal_branch_status=Success"
    )
) else if "!choice!"=="2" (
    echo %INFO_PREFIX% Using merge method...
    set "rebase_method=Merge"
    git merge %MAIN_BRANCH%
    if errorlevel 1 (
        echo %ERROR_PREFIX% Merge encountered conflicts!
        echo.
        echo Choose how to handle the conflicts:
        echo 1^) Abort merge and return to original state ^(recommended^)
        echo 2^) Leave in conflict state for manual resolution
        set /p "conflict_choice=Please choose (1/2): "

        if "!conflict_choice!"=="1" (
            echo %INFO_PREFIX% Aborting merge and returning to original state...
            git merge --abort
            if errorlevel 1 (
                echo %WARNING_PREFIX% Failed to abort merge, manual intervention required
                set "personal_branch_status=Failed (merge abort failed)"
            ) else (
                echo %SUCCESS_PREFIX% Merge aborted, returned to original state
                set "personal_branch_status=Aborted (conflicts)"
            )
        ) else (
            echo %INFO_PREFIX% Leaving in conflict state for manual resolution
            echo Please resolve conflicts manually:
            echo   git add ^<conflict-files^>
            echo   git commit
            echo Or abort merge later:
            echo   git merge --abort
            set "personal_branch_status=Manual resolution required"
            set "conflicts_occurred=Yes"
            goto :show_summary
        )
        set "conflicts_occurred=Yes"
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
for /f "delims=" %%i in ('git rev-list --count HEAD 2^>nul') do set "commits_after=%%i"

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

:selective_cherry_pick
echo %INFO_PREFIX% Starting selective cherry-pick process...
echo %INFO_PREFIX% Analyzing commits from %MAIN_BRANCH% that are safe to apply...

REM Get list of commits from master that are not in current branch
git log --oneline %MAIN_BRANCH%..HEAD >current_commits.tmp 2>nul
git log --oneline HEAD..%MAIN_BRANCH% >available_commits.tmp 2>nul

if not exist available_commits.tmp (
    echo %INFO_PREFIX% No new commits to cherry-pick
    set "personal_branch_status=Already up to date"
    goto :cleanup_cherry_pick
)

REM Filter out sync-related commits if enabled
if "%SKIP_SYNC_SCRIPT_COMMITS%"=="true" (
    echo %INFO_PREFIX% Filtering out sync script related commits...
    findstr /v /i "sync" available_commits.tmp > safe_commits.tmp
) else (
    copy available_commits.tmp safe_commits.tmp >nul
)

REM Check if there are safe commits to apply
for /f %%i in ('type safe_commits.tmp ^| find /c /v ""') do set "safe_commit_count=%%i"

if %safe_commit_count% EQU 0 (
    echo %INFO_PREFIX% No safe commits found to cherry-pick
    set "personal_branch_status=No safe updates available"
    goto :cleanup_cherry_pick
)

echo %INFO_PREFIX% Found %safe_commit_count% safe commits to apply:
type safe_commits.tmp
echo.
set /p "apply_commits=Apply these commits? (y/N): "

if /i "!apply_commits!"=="y" (
    echo %INFO_PREFIX% Applying safe commits...
    set "applied_count=0"
    set "failed_count=0"

    for /f "tokens=1" %%i in (safe_commits.tmp) do (
        echo %INFO_PREFIX% Cherry-picking commit %%i...
        git cherry-pick %%i >nul 2>&1
        if errorlevel 1 (
            echo %WARNING_PREFIX% Failed to apply commit %%i, skipping...
            git cherry-pick --abort >nul 2>&1
            set /a "failed_count+=1"
        ) else (
            echo %SUCCESS_PREFIX% Successfully applied commit %%i
            set /a "applied_count+=1"
        )
    )

    echo %INFO_PREFIX% Cherry-pick completed: !applied_count! applied, !failed_count! failed
    if !applied_count! GTR 0 (
        set "personal_branch_status=Partial sync (!applied_count! commits applied)"
    ) else (
        set "personal_branch_status=No commits applied"
    )
) else (
    echo %INFO_PREFIX% Cherry-pick cancelled by user
    set "personal_branch_status=Cancelled by user"
)

:cleanup_cherry_pick
if exist current_commits.tmp del current_commits.tmp >nul 2>&1
if exist available_commits.tmp del available_commits.tmp >nul 2>&1
if exist safe_commits.tmp del safe_commits.tmp >nul 2>&1
goto :eof

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