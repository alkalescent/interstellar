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
# Nuitka's self-execution guard intercepts a leading -m as Python's module
# flag, which breaks `interstellar deconstruct -m <mnemonic>`, the documented
# short form of --mnemonic. The guard protects against a compiled binary
# re-invoking itself as an interpreter, which this CLI never does.
uv run python -m nuitka \
  --mode="${MODE}" \
  --output-filename="${NAME}" \
  --no-deployment-flag=self-execution \
  --include-data-files="$SITE_PACKAGES/shamir_mnemonic/wordlist.txt=./shamir_mnemonic/wordlist.txt" \
  --include-data-dir="$SITE_PACKAGES/mnemonic/wordlist=./mnemonic/wordlist" \
  --remove-output \
  --assume-yes-for-downloads \
  src/${NAME}/cli.py