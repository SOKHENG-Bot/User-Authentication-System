# ===============================
# GIT CHEAT SHEET
# ===============================

# --- Initialize / Clone ---
git init                     # Initialize a new Git repository
git clone <url>              # Clone a remote repository

# --- Check Status ---
git status                   # Show current changes
git diff                     # Show unstaged changes
git diff --staged            # Show staged changes

# --- Stage & Commit ---
git add <file_or_dir>        # Stage specific file(s)
git add .                    # Stage all changes
git commit -m "message"      # Commit staged changes
git commit -am "message"     # Stage & commit modified files in one step

# --- Branching ---
git branch                   # List branches
git branch <name>            # Create a new branch
git checkout <name>          # Switch to branch
git checkout -b <name>       # Create & switch to branch

# --- Merging ---
git merge <branch>           # Merge branch into current branch
git rebase <branch>          # Rebase current branch onto another branch

# --- Remote Repositories ---
git remote -v                # Show remote URLs
git remote add <name> <url>  # Add new remote
git push origin <branch>     # Push branch to remote
git pull origin <branch>     # Pull changes from remote
git fetch                    # Fetch changes without merging
git fetch --all              # Fetch all remotes

# --- Undo / Reset ---
git reset --soft HEAD~1      # Undo last commit, keep changes staged
git reset --hard HEAD~1      # Undo last commit, discard changes
git checkout -- <file>       # Discard changes in file
git revert <commit>          # Create a new commit that undoes a previous commit

# --- Stash Changes ---
git stash                    # Stash uncommitted changes
git stash list               # List stashes
git stash apply              # Apply last stash
git stash pop                # Apply & remove last stash

# --- Logs / History ---
git log                      # Show commit history
git log --oneline --graph    # Compact history with branch graph
git show <commit>            # Show changes in a specific commit

# --- Tags ---
git tag                      # List tags
git tag <name>               # Create tag
git push origin <tag>        # Push tag to remote
