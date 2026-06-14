#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

REMOTE_NAME="${REMOTE_NAME:-origin}"
BRANCH_NAME="${BRANCH_NAME:-$(git branch --show-current)}"

if [[ -z "$BRANCH_NAME" ]]; then
  echo "Cannot detect current git branch. Set BRANCH_NAME=master and retry." >&2
  exit 1
fi

bash script/update_edgetunnel_bestip.sh

git add bestip.txt
if git diff --cached --quiet; then
  echo "bestip.txt is unchanged; nothing to commit."
  exit 0
fi

git commit -m "chore: update local edgetunnel bestip"
git push "$REMOTE_NAME" "$BRANCH_NAME"

echo "Updated bestip.txt from this machine and pushed to $REMOTE_NAME/$BRANCH_NAME."
