#!/usr/bin/env bash
# Check the ECC toolbox for news (default) or update it (--pull). Review the diff first: ECC ships hooks and
# scripts that run on your machine.
#   scripts/toolbox-update.sh [--pull]       (TOOLBOX_REPO=<path> to use a local clone elsewhere)
set -euo pipefail
# shellcheck source=common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

REPO="${TOOLBOX_REPO:-$MASTER/../toolbox-src/repo}"
UPSTREAM="$(sed -n 's/^upstream=//p' "$MASTER/toolbox.lock")"
TESTED_VERSION="$(sed -n 's/^version=//p' "$MASTER/toolbox.lock")"
TESTED_COMMIT="$(sed -n 's/^commit=//p' "$MASTER/toolbox.lock" | cut -c1-7)"

if [[ ! -d "$REPO/.git" ]]; then
  cat <<EOF
No local ECC clone at $REPO, so the toolbox comes straight from the marketplace. To update it:
  claude plugin marketplace update ecc && claude plugin update ecc@ecc
CWCDT was tested with ECC $TESTED_VERSION (commit $TESTED_COMMIT).
To track a local clone instead:  git clone $UPSTREAM $REPO
EOF
  exit 0
fi

git -C "$REPO" fetch --quiet origin
LOCAL="$(git -C "$REPO" rev-parse HEAD)"
REMOTE="$(git -C "$REPO" rev-parse '@{u}')"

if [[ "$LOCAL" == "$REMOTE" ]]; then
  echo "ECC is up to date: ${LOCAL:0:7} (v$(cat "$REPO/VERSION"))"
  exit 0
fi

echo "ECC has news: ${LOCAL:0:7} -> ${REMOTE:0:7}"
git -C "$REPO" log --oneline "$LOCAL..$REMOTE" | head -30
echo
echo "Review before accepting:"
echo "  git -C $REPO diff --stat $LOCAL..$REMOTE | tail -5"
echo "  git -C $REPO diff $LOCAL..$REMOTE -- hooks scripts .claude-plugin"

if [[ "${1:-}" != "--pull" ]]; then
  echo "If it looks fine: $0 --pull"
  exit 0
fi

git -C "$REPO" merge --ff-only '@{u}'
claude plugin update ecc@ecc
printf 'upstream=%s\ncommit=%s\ncommit_date=%s\nversion=%s\nreviewed=%s\n' \
  "$UPSTREAM" "$(git -C "$REPO" rev-parse HEAD)" "$(git -C "$REPO" log -1 --format=%cs)" \
  "$(cat "$REPO/VERSION")" "$(date +%F)" >"$MASTER/toolbox.lock"
echo "toolbox.lock updated. Restart Claude Code and measure the effect: scripts/measure.sh post-update"
