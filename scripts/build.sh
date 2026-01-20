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
  --include-data-dir="$SITE_PACKAGES/mnemonic/wordlist=./mnemonic/wordlist" \
  --include-data-dir="$SITE_PACKAGES/hdwallet/mnemonics/bip39/wordlist=./hdwallet/mnemonics/bip39/wordlist" \
  --include-data-dir="$SITE_PACKAGES/hdwallet/mnemonics/slip39/wordlist=./hdwallet/mnemonics/slip39/wordlist" \
  --remove-output \
  --assume-yes-for-downloads \
  src/${NAME}/cli.py