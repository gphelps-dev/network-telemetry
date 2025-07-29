#!/bin/bash

# Force push script to keep all changes in one commit
# This script will amend all changes to the existing commit and force push

echo "Force pushing changes to main..."

# Check if there are any changes to commit
if [[ -n $(git status --porcelain) ]]; then
    echo "Changes detected, amending to existing commit..."
    
    # Add all changes
    git add .
    
    # Amend the existing commit (keeping the same message)
    git commit --amend --no-edit
    
    echo "Changes amended to existing commit"
else
    echo "No changes detected"
fi

# Force push to main
echo "Force pushing to main..."
git push --force-with-lease origin main

echo "Successfully force pushed to main!"
echo "Current commit: $(git log --oneline -1)"