#!/usr/bin/env bash
set -euo pipefail

# Foydalanish:
# ./scripts/git_push_template.sh YOUR_GITHUB_USERNAME

USERNAME=${1:-}
REPO="yordamchi-ai-namdtu-transport"

if [ -z "$USERNAME" ]; then
  echo "GitHub username kiriting: ./scripts/git_push_template.sh USERNAME"
  exit 1
fi

git init
git add .
git commit -m "Initial MVP for Yordamchi AI NamDTU Transport"
git branch -M main
git remote add origin "https://github.com/${USERNAME}/${REPO}.git"
git push -u origin main
