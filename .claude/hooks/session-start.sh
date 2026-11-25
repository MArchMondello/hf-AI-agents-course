#!/bin/bash
# SessionStart hook: if the session starts on main, bring main up to date with GitHub.
# Fast-forward only: it never creates a merge commit and never touches local work.
# It must never block the session: every failure is reported and the script exits 0.

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

# Only when a session starts (not on resume, /clear or compaction)
source=$(sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([a-z]*\)".*/\1/p')
[ "${source:-startup}" = "startup" ] || exit 0

branch=$(git branch --show-current 2>/dev/null)
[ "$branch" = "main" ] || exit 0

before=$(git rev-parse --short HEAD)
if out=$(timeout 20 git pull --ff-only --quiet origin main 2>&1); then
  after=$(git rev-parse --short HEAD)
  if [ "$before" = "$after" ]; then
    echo "git pull on main: already up to date ($after)."
  else
    echo "git pull on main: updated $before -> $after."
  fi
else
  reason=$(printf '%s\n' "$out" | grep -m1 '^fatal:' || printf '%s\n' "$out" | tail -n1)
  echo "git pull on main failed, main left as it was. ${reason:-timeout or no network}"
fi
exit 0
