#!/bin/bash

set -eu
SITE_PACKAGES=$(uv run python3 -c "import sysconfig; print(sysconfig.get_path('purelib'))")
uv run python3 -m nuitka \
  --onefile \
  --output-filename=cli \
  --output-dir=./dist \
  --include-data-files="$SITE_PACKAGES/shamir_mnemonic/wordlist.txt=./shamir_mnemonic/wordlist.txt" \
  --remove-output \
  --assume-yes-for-downloads \
  cli.py