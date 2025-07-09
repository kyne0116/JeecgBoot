#!/bin/bash

# Save the full path of this script to avoid issues when switching branches
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

# ========================================
# Git Repository Sync Tool - Linux/macOS Version
# Purpose: Keep fork synchronized with official repository and update personal branch
# ========================================

# ========================================
# Configuration Variables - Modify these variables for your project
# ========================================
UPSTREAM_REPO_URL="https://github.com/jeecgboot/JeecgBoot.git"
ORIGIN_REPO_URL="https://github.com/kyne0116/JeecgBoot.git"
MAIN_BRANCH="master"
PERSONAL_BRANCH="my-custom"
UPSTREAM_REMOTE_NAME="upstream"
ORIGIN_REMOTE_NAME="origin"

# ========================================
# Smart Sync Configuration
# ========================================
# Enable selective sync mode (avoids conflicts with sync scripts)
SELECTIVE_SYNC_MODE="true"
# Skip commits that modify sync scripts to avoid conflicts
SKIP_SYNC_SCRIPT_COMMITS="true"

# Initialize summary variables
master_sync_status="Not Started"
master_changes_count=0
master_files_changed=""
commits_behind=0
personal_branch_status="Not Started"
backup_branch_name=""
rebase_method=""
conflicts_occurred="No"
commits_before=0
commits_after=0

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Prefix definitions
INFO_PREFIX="[INFO]"
SUCCESS_PREFIX="[SUCCESS]"
WARNING_PREFIX="[WARNING]"
ERROR_PREFIX="[ERROR]"

# Logging functions
log_info() {
    echo -e "${BLUE}${INFO_PREFIX}${NC} $1"
}

log_success() {
    echo -e "${GREEN}${SUCCESS_PREFIX}${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}${WARNING_PREFIX}${NC} $1"
}

log_error() {
    echo -e "${RED}${ERROR_PREFIX}${NC} $1"
}

echo "========================================"
echo "        Git Repository Sync Tool"
echo "========================================"
echo
echo "Configuration:"
echo "  Upstream repo: ${UPSTREAM_REPO_URL}"
echo "  Origin repo: ${ORIGIN_REPO_URL}"
echo "  Main branch: ${MAIN_BRANCH}"
echo "  Personal branch: ${PERSONAL_BRANCH}"
echo "========================================"
echo

log_info "Starting sync operation..."
echo

# Record current branch for information
log_info "Recording current branch..."
CURRENT_BRANCH_INFO=$(git branch --show-current 2>/dev/null || echo "")
if [ -z "$CURRENT_BRANCH_INFO" ]; then
    log_warning "Could not determine current branch"
else
    log_info "Current branch: $CURRENT_BRANCH_INFO"
fi

# Check if in git repository
check_git_repo() {
    log_info "Checking Git repository status..."
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Current directory is not a Git repository!"
        read -p "Press any key to exit..."
        exit 1
    fi
}

# Check and configure safe directory if needed (for Git 2.35.2+)
check_safe_directory() {
    log_info "Checking Git safe directory configuration..."
    current_dir=$(pwd)
    if ! git config --global --get-all safe.directory | grep -q "^${current_dir}$" 2>/dev/null; then
        log_info "Adding current directory to Git safe directories..."
        if git config --global --add safe.directory "$current_dir" 2>/dev/null; then
            log_success "Directory added to Git safe directories"
        else
            log_warning "Could not add directory to safe.directory config"
            log_warning "You may need to run: git config --global --add safe.directory \"$current_dir\""
        fi
    else
        log_info "Directory is already in Git safe directories"
    fi
}

# Check for uncommitted changes
check_uncommitted_changes() {
    log_info "Checking for uncommitted changes..."
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        log_warning "Detected uncommitted changes!"
        echo "Please commit or stash your changes first:"
        git status --porcelain
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Operation cancelled"
            read -p "Press any key to exit..."
            exit 0
        fi
    fi
}

# Check and add upstream repository
setup_upstream() {
    log_info "Checking upstream repository configuration..."
    if ! git remote get-url ${UPSTREAM_REMOTE_NAME} > /dev/null 2>&1; then
        log_info "Adding upstream repository..."
        if git remote add ${UPSTREAM_REMOTE_NAME} ${UPSTREAM_REPO_URL}; then
            log_success "Upstream repository added"
        else
            log_error "Failed to add upstream repository!"
            read -p "Press any key to exit..."
            exit 1
        fi
    else
        log_info "Upstream repository already exists"
    fi

    echo "Current remote repository configuration:"
    git remote -v
}

echo
log_info "Starting sync for ${MAIN_BRANCH} branch..."

# Record current branch to restore later
ORIGINAL_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [ -z "$ORIGINAL_BRANCH" ]; then
    ORIGINAL_BRANCH="$PERSONAL_BRANCH"
fi

# Use a safer approach: update master branch without switching to it
sync_master() {
    log_info "Updating local ${MAIN_BRANCH} branch from upstream (without switching)..."

    # Change back to the directory where the script is located
    cd "$(dirname "$SCRIPT_PATH")"

    # Get commits behind count for master branch
    log_info "Getting initial commits behind count..."
    commits_behind=$(git rev-list --count ${MAIN_BRANCH}..${UPSTREAM_REMOTE_NAME}/${MAIN_BRANCH} 2>/dev/null || echo "0")
    log_info "Initial commits behind: $commits_behind"

    # Fetch upstream updates
    log_info "Fetching upstream repository updates..."
    log_info "Running: git fetch ${UPSTREAM_REMOTE_NAME}"
    if ! git fetch ${UPSTREAM_REMOTE_NAME} 2>&1; then
        log_error "Failed to fetch upstream updates!"
        log_error "Git fetch command returned error"
        master_sync_status="Failed"
        restore_branch_and_exit
        return 1
    fi
    log_success "Fetch completed successfully"

    # Recalculate commits behind count
    log_info "Calculating commits behind count..."
    commits_behind=$(git rev-list --count ${MAIN_BRANCH}..${UPSTREAM_REMOTE_NAME}/${MAIN_BRANCH} 2>/dev/null || echo "0")
    log_info "Commits behind: $commits_behind"

    log_info "Checking if updates are needed..."

    if [ "$commits_behind" -gt 0 ]; then
        update_master_branch
    else
        master_already_updated
    fi
}

update_master_branch() {
    log_info "Found $commits_behind new commits, updating local ${MAIN_BRANCH} branch..."

    # Update master branch using git update-ref (safer than checkout + merge)
    if ! git update-ref refs/heads/${MAIN_BRANCH} ${UPSTREAM_REMOTE_NAME}/${MAIN_BRANCH}; then
        log_error "Failed to update local ${MAIN_BRANCH} branch!"
        master_sync_status="Failed"
        restore_branch_and_exit
        return 1
    fi

    # Check if origin has commits not in upstream before force push
    log_info "Checking if your fork has unique commits on master branch..."
    origin_ahead=$(git rev-list --count ${UPSTREAM_REMOTE_NAME}/${MAIN_BRANCH}..${ORIGIN_REMOTE_NAME}/${MAIN_BRANCH} 2>/dev/null || echo "0")

    if [ "$origin_ahead" -gt 0 ]; then
        log_warning "Your fork has $origin_ahead commits on master that are not in upstream!"
        log_warning "This indicates you may have made commits directly to master branch."
        echo
        echo "These commits will be lost if you continue with force push:"
        git log --oneline ${UPSTREAM_REMOTE_NAME}/${MAIN_BRANCH}..${ORIGIN_REMOTE_NAME}/${MAIN_BRANCH}
        echo
        echo "Recommendations:"
        echo "  1) Create a backup branch for these commits first"
        echo "  2) Cherry-pick important commits to your personal branch"
        echo "  3) Only continue if you're sure these commits are not needed"
        echo
        read -p "Do you want to force push anyway and lose these commits? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Force push cancelled to preserve your commits"
            log_info "Consider backing up these commits before running sync again"
            master_sync_status="Cancelled (preserving fork commits)"
            personal_branch_update
            return 0
        fi
        log_warning "Proceeding with force push - your fork commits will be lost!"
    else
        log_info "Your fork master is clean (no unique commits), safe to force push"
    fi

    # Push to fork (force push to ensure sync)
    log_info "Pushing updates to your fork..."
    log_warning "This will force-push to ensure master branch sync with upstream"
    if git push ${ORIGIN_REMOTE_NAME} ${MAIN_BRANCH} --force; then
        master_sync_status="Success"
    else
        log_warning "Failed to push to fork, may need manual push"
        master_sync_status="Partial Success"
    fi
    master_files_changed="Updated $commits_behind commits"
    master_sync_completed
}

master_already_updated() {
    log_info "Local ${MAIN_BRANCH} branch is already up to date"
    master_sync_status="Already up to date"
    master_files_changed="No changes needed"
    master_sync_completed
}

master_sync_completed() {
    log_success "${MAIN_BRANCH} branch sync completed!"
    personal_branch_update
}

personal_branch_update() {
    echo
    log_info "Starting update for personal branch ${PERSONAL_BRANCH}..."

    # Check if branch exists
    log_info "Checking if branch ${PERSONAL_BRANCH} exists..."
    if ! git show-ref --verify --quiet refs/heads/${PERSONAL_BRANCH} 2>/dev/null; then
        log_warning "Branch ${PERSONAL_BRANCH} does not exist, skipping personal branch update"
        personal_branch_status="Skipped (branch not found)"
        show_summary
        return 0
    fi
    log_info "Branch ${PERSONAL_BRANCH} exists, proceeding..."

    # Switch to personal branch
    log_info "Switching to personal branch ${PERSONAL_BRANCH}..."
    if ! git checkout ${PERSONAL_BRANCH}; then
        log_error "Failed to switch to personal branch!"
        personal_branch_status="Failed"
        restore_branch_and_exit
        return 1
    fi

    # Get commit count before update
    commits_before=$(git rev-list --count HEAD 2>/dev/null || echo "0")

    # Create backup branch with numeric timestamp (YYYYMMDD-HHMMSS format)
    timestamp=$(date +%Y%m%d-%H%M%S)
    backup_branch_name="${PERSONAL_BRANCH}-backup-${timestamp}"
    log_info "Creating backup branch ${backup_branch_name}..."
    git checkout -b ${backup_branch_name} > /dev/null 2>&1
    git checkout ${PERSONAL_BRANCH} > /dev/null 2>&1

    # Choose update method
    echo "Choose update method:"
    echo "1) Rebase (recommended, keeps clean history)"
    echo "2) Merge (safe, preserves complete history)"
    read -p "Please choose (1/2): " -n 1 -r
    echo

    case $REPLY in
        1)
            log_info "Using rebase method..."
            rebase_method="Rebase"

            # Smart sync: Check for potential conflicts with sync scripts
            if [ "$SELECTIVE_SYNC_MODE" = "true" ]; then
                log_info "Smart sync mode enabled - checking for potential conflicts..."
                if git log --oneline ${MAIN_BRANCH}..HEAD | grep -i "sync" > /dev/null 2>&1; then
                    log_warning "Detected sync-related commits that may conflict"
                    log_info "Recommendation: Use selective cherry-pick instead of full rebase"
                    echo
                    echo "Choose sync strategy:"
                    echo "1) Continue with full rebase (may have conflicts)"
                    echo "2) Use selective cherry-pick (recommended)"
                    echo "3) Skip sync and keep current state"
                    read -p "Please choose (1/2/3): " -n 1 -r
                    echo

                    case $REPLY in
                        2)
                            log_info "Using selective cherry-pick strategy..."
                            selective_cherry_pick
                            show_summary
                            return 0
                            ;;
                        3)
                            log_info "Skipping sync, keeping current state"
                            personal_branch_status="Skipped (user choice)"
                            show_summary
                            return 0
                            ;;
                        *)
                            log_info "Continuing with full rebase..."
                            ;;
                    esac
                fi
            fi

            if git rebase ${MAIN_BRANCH}; then
                log_success "Rebase completed!"
                personal_branch_status="Success"
            else
                handle_rebase_conflicts
                return 1
            fi
            ;;
        2)
            log_info "Using merge method..."
            rebase_method="Merge"
            if git merge ${MAIN_BRANCH}; then
                log_success "Merge completed!"
                personal_branch_status="Success"
            else
                handle_merge_conflicts
                return 1
            fi
            ;;
        *)
            log_warning "Invalid choice, skipping personal branch update"
            personal_branch_status="Skipped (user cancelled)"
            show_summary
            return 0
            ;;
    esac

    # Get commit count after update
    commits_after=$(git rev-list --count HEAD 2>/dev/null || echo "0")

    log_success "Personal branch ${PERSONAL_BRANCH} update completed!"
    log_info "Backup branch created: ${backup_branch_name}"

    show_summary
}

handle_rebase_conflicts() {
    log_error "Rebase encountered conflicts!"
    echo
    echo "Choose how to handle the conflicts:"
    echo "1) Abort rebase and return to original state (recommended)"
    echo "2) Leave in conflict state for manual resolution"
    read -p "Please choose (1/2): " -n 1 -r
    echo

    case $REPLY in
        1)
            log_info "Aborting rebase and returning to original state..."
            if git rebase --abort; then
                log_success "Rebase aborted, returned to original state"
                personal_branch_status="Aborted (conflicts)"
            else
                log_warning "Failed to abort rebase, manual intervention required"
                personal_branch_status="Failed (rebase abort failed)"
            fi
            ;;
        2)
            log_info "Leaving in conflict state for manual resolution"
            echo "Please resolve conflicts manually:"
            echo "  git add <conflict-files>"
            echo "  git rebase --continue"
            echo "Or abort rebase later:"
            echo "  git rebase --abort"
            personal_branch_status="Manual resolution required"
            conflicts_occurred="Yes"
            show_summary
            return 0
            ;;
    esac
    conflicts_occurred="Yes"
}

handle_merge_conflicts() {
    log_error "Merge encountered conflicts!"
    echo
    echo "Choose how to handle the conflicts:"
    echo "1) Abort merge and return to original state (recommended)"
    echo "2) Leave in conflict state for manual resolution"
    read -p "Please choose (1/2): " -n 1 -r
    echo

    case $REPLY in
        1)
            log_info "Aborting merge and returning to original state..."
            if git merge --abort; then
                log_success "Merge aborted, returned to original state"
                personal_branch_status="Aborted (conflicts)"
            else
                log_warning "Failed to abort merge, manual intervention required"
                personal_branch_status="Failed (merge abort failed)"
            fi
            ;;
        2)
            log_info "Leaving in conflict state for manual resolution"
            echo "Please resolve conflicts manually:"
            echo "  git add <conflict-files>"
            echo "  git commit"
            echo "Or abort merge later:"
            echo "  git merge --abort"
            personal_branch_status="Manual resolution required"
            conflicts_occurred="Yes"
            show_summary
            return 0
            ;;
    esac
    conflicts_occurred="Yes"
}

selective_cherry_pick() {
    log_info "Starting selective cherry-pick process..."
    log_info "Analyzing commits from ${MAIN_BRANCH} that are safe to apply..."

    # Get list of commits from master that are not in current branch
    git log --oneline ${MAIN_BRANCH}..HEAD > current_commits.tmp 2>/dev/null || true
    git log --oneline HEAD..${MAIN_BRANCH} > available_commits.tmp 2>/dev/null || true

    if [ ! -f available_commits.tmp ] || [ ! -s available_commits.tmp ]; then
        log_info "No new commits to cherry-pick"
        personal_branch_status="Already up to date"
        cleanup_cherry_pick
        return 0
    fi

    # Filter out sync-related commits if enabled
    if [ "$SKIP_SYNC_SCRIPT_COMMITS" = "true" ]; then
        log_info "Filtering out sync script related commits..."
        grep -v -i "sync" available_commits.tmp > safe_commits.tmp || touch safe_commits.tmp
    else
        cp available_commits.tmp safe_commits.tmp
    fi

    # Check if there are safe commits to apply
    safe_commit_count=$(wc -l < safe_commits.tmp 2>/dev/null || echo "0")

    if [ "$safe_commit_count" -eq 0 ]; then
        log_info "No safe commits found to cherry-pick"
        personal_branch_status="No safe updates available"
        cleanup_cherry_pick
        return 0
    fi

    log_info "Found $safe_commit_count safe commits to apply:"
    cat safe_commits.tmp
    echo
    read -p "Apply these commits? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Applying safe commits..."
        applied_count=0
        failed_count=0

        while IFS= read -r line; do
            commit_hash=$(echo "$line" | awk '{print $1}')
            log_info "Cherry-picking commit $commit_hash..."
            if git cherry-pick "$commit_hash" > /dev/null 2>&1; then
                log_success "Successfully applied commit $commit_hash"
                applied_count=$((applied_count + 1))
            else
                log_warning "Failed to apply commit $commit_hash, skipping..."
                git cherry-pick --abort > /dev/null 2>&1
                failed_count=$((failed_count + 1))
            fi
        done < safe_commits.tmp

        log_info "Cherry-pick completed: $applied_count applied, $failed_count failed"
        if [ "$applied_count" -gt 0 ]; then
            personal_branch_status="Partial sync ($applied_count commits applied)"
        else
            personal_branch_status="No commits applied"
        fi
    else
        log_info "Cherry-pick cancelled by user"
        personal_branch_status="Cancelled by user"
    fi

    cleanup_cherry_pick
}

cleanup_cherry_pick() {
    rm -f current_commits.tmp available_commits.tmp safe_commits.tmp 2>/dev/null || true
}
show_summary() {
    echo
    echo "========================================"
    echo "            Sync Operation Summary"
    echo "========================================"
    echo
    echo "${MAIN_BRANCH} branch sync result:"
    echo "    Status: ${master_sync_status}"
    if [ "$commits_behind" -gt 0 ]; then
        echo "    Updates: Synced $commits_behind commits"
    else
        echo "    Updates: Already up to date"
    fi
    if [ -n "$master_files_changed" ]; then
        echo "    Changes: ${master_files_changed}"
    fi
    echo
    echo "Personal branch processing result:"
    echo "    Branch name: ${PERSONAL_BRANCH}"
    echo "    Processing status: ${personal_branch_status}"
    if [ -n "$rebase_method" ]; then
        echo "    Update method: ${rebase_method}"
    fi
    if [ -n "$backup_branch_name" ]; then
        echo "    Backup branch: ${backup_branch_name}"
    fi
    if [ "$commits_before" -gt 0 ] && [ "$commits_after" -gt 0 ]; then
        echo "    Commit count: ${commits_before} to ${commits_after}"
    fi
    echo
    echo "Conflict status:"
    echo "    Any conflicts: ${conflicts_occurred}"
    echo
    echo "========================================"
    echo
    if [ "$master_sync_status" = "Success" ] && [ "$personal_branch_status" = "Success" ]; then
        echo "Sync operation completed successfully! Your code is updated to the latest version."
    else
        echo "Sync operation partially completed, please check the status information above."
    fi
    echo
    if [ -n "$backup_branch_name" ]; then
        log_info "Backup branch created: ${backup_branch_name}"
        echo "If you need to rollback, use:"
        echo "  git reset --hard ${backup_branch_name}"
        echo "  git push origin ${PERSONAL_BRANCH} --force"
        echo
    fi
    log_info "Sync operation completed"
    echo "Current branch:"
    git branch --show-current
    echo
    read -p "Press any key to exit..."
}

restore_branch_and_exit() {
    echo
    log_warning "Sync operation encountered error, trying to restore to original branch..."
    if [ -n "$ORIGINAL_BRANCH" ]; then
        log_info "Attempting to restore to $ORIGINAL_BRANCH branch..."
        if git checkout "$ORIGINAL_BRANCH" > /dev/null 2>&1; then
            log_success "Restored to $ORIGINAL_BRANCH branch"
        else
            log_warning "Cannot switch to $ORIGINAL_BRANCH branch, trying $PERSONAL_BRANCH..."
            if git checkout "$PERSONAL_BRANCH" > /dev/null 2>&1; then
                log_success "Restored to $PERSONAL_BRANCH branch"
            else
                log_warning "Cannot switch to $PERSONAL_BRANCH branch, staying on current branch"
            fi
        fi
    else
        log_info "Attempting to restore to $PERSONAL_BRANCH branch..."
        if git checkout "$PERSONAL_BRANCH" > /dev/null 2>&1; then
            log_success "Restored to $PERSONAL_BRANCH branch"
        else
            log_warning "Cannot switch to $PERSONAL_BRANCH branch, staying on current branch"
        fi
    fi
    echo "Current branch:"
    git branch --show-current
    echo
    read -p "Press any key to exit..."
    exit 1
}

# Main function
main() {
    check_git_repo
    check_safe_directory
    check_uncommitted_changes
    setup_upstream

    echo
    sync_master
}

# Execute main function
main "$@"
