#!/bin/bash

set -eu

# Extract project name from README.md
NAME="$(grep '^#' README.md | head -n 1 | sed -e 's/^# *//' -e 's/ *$//')"

# If CI is true, then use basename of $GITHUB_REPOSITORY as name
if [ "${CI:-false}" = "true" ]; then
  NAME=$(basename "$GITHUB_REPOSITORY")
fi

MODE="${MODE:-standalone}"

SITE_PACKAGES=$(uv run python -c "import sysconfig; print(sysconfig.get_path('purelib'))")
uv run python -m nuitka \
  --mode="${MODE}" \
  --output-filename="${NAME}" \
  --include-data-files="$SITE_PACKAGES/shamir_mnemonic/wordlist.txt=./shamir_mnemonic/wordlist.txt" \
  --remove-output \
  --assume-yes-for-downloads \
  cli.py