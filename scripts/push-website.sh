#!/bin/bash
# push-website.sh — Deploy the seminar website to the server via rsync.

set -euo pipefail

REMOTE="gittea@linux.cs.rpi.edu:/cs/gittea/public.html/old-site/teaching/mltheoryseminar/"

die() { echo "ERROR: $*" >&2; exit 1; }
usage() {
  cat >&2 <<'EOF'
Usage: ./push-website.sh [--dry-run]

  --dry-run    Show what would be transferred without actually doing it.

Deploys the website/ directory to the seminar web server.
EOF
  exit 1
}
require() { command -v "$1" >/dev/null 2>&1 || die "'$1' not found on PATH."; }

DRY_RUN=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN="--dry-run" ;;
    -h|--help) usage ;;
    *) die "Unknown argument: $arg" ;;
  esac
done

require rsync

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEBSITE_DIR="$REPO_ROOT/website"

[ -d "$WEBSITE_DIR" ] || die "website/ directory not found at $REPO_ROOT"

echo "Deploying website to $REMOTE"
[ -n "$DRY_RUN" ] && echo "(dry run — no changes will be made)"
echo ""

rsync -av --delete $DRY_RUN \
  "$WEBSITE_DIR/" "$REMOTE"

echo ""
echo "Done."
