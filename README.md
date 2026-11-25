# interstellar

[![CI](https://github.com/alkalescent/interstellar/actions/workflows/release.yml/badge.svg)](https://github.com/alkalescent/interstellar/actions/workflows/release.yml)
[![PyPI version](https://badge.fury.io/py/interstellar.svg)](https://pypi.org/project/interstellar/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A command-line tool for managing cryptocurrency mnemonics using BIP39 and SLIP39 standards. This tool allows you to split, combine, and convert mnemonic phrases for secure key management.

## ✨ Features

- **BIP39 Support**: Validate and split BIP39 mnemonic phrases
- **SLIP39 Support**: Create Shamir Secret Sharing (SLIP39) shares from mnemonics
- **Flexible Splitting**: Deconstruct 24-word mnemonics into multiple 12-word parts
- **Share Reconstruction**: Reconstruct mnemonics from SLIP39 shares with threshold requirements
- **Digit Mode**: Convert mnemonics to/from numeric format for easier backup (1-indexed: BIP39 uses 1-2048, SLIP39 uses 1-1024)
- **Address Check**: Confirm a reconstructed mnemonic against the Ethereum address recorded when it was deconstructed

## 💖 Support

Love this tool? Your support means the world! ❤️

<table align="center">
  <tr>
    <th>Currency</th>
    <th>Address</th>
    <th>QR</th>
  </tr>
  <tr>
    <td><strong>₿ BTC</strong></td>
    <td><code>bc1qwn7ea6s8wqx66hl5rr2supk4kv7qtcxnlqcqfk</code></td>
    <td><img src="assets/qr_btc.png" width="80" /></td>
  </tr>
  <tr>
    <td><strong>Ξ ETH</strong></td>
    <td><code>0x7cdB1861AC1B4385521a6e16dF198e7bc43fDE5f</code></td>
    <td><img src="assets/qr_eth.png" width="80" /></td>
  </tr>
  <tr>
    <td><strong>ɱ XMR</strong></td>
    <td><code>463fMSWyDrk9DVQ8QCiAir8TQd4h3aRAiDGA8CKKjknGaip7cnHGmS7bQmxSiS2aYtE9tT31Zf7dSbK1wyVARNgA9pkzVxX</code></td>
    <td><img src="assets/qr_xmr.png" width="80" /></td>
  </tr>
  <tr>
    <td><strong>◈ BNB</strong></td>
    <td><code>0x7cdB1861AC1B4385521a6e16dF198e7bc43fDE5f</code></td>
    <td><img src="assets/qr_bnb.png" width="80" /></td>
  </tr>
</table>

## 📦 Installation

### Homebrew (macOS/Linux)

```bash
brew tap alkalescent/tap
brew trust alkalescent/tap
brew install interstellar
```

### PyPI (Recommended)

```bash
uv pip install interstellar
```

After installation, use either the command directly or as a Python module:

```bash
# Direct command
interstellar --help

# As Python module (if direct command not in PATH)
uv run python -m interstellar --help
```

### From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/alkalescent/interstellar.git
cd interstellar
make install DEV=1  # Install with dev dependencies
```

### Pre-built Binaries

Download from [GitHub Releases](https://github.com/alkalescent/interstellar/releases):

| Variant | Description | Startup | Format |
|---------|-------------|---------|--------|
| **Portable** | Single file, no installation needed | ~10 sec | `interstellar-{os}-portable` |
| **Fast** | Optimized for speed | ~1 sec | `interstellar-{os}-fast.tar.gz` |

> **Note**: In the filenames and commands, replace `{os}` with your operating system (e.g., `linux`, `macos`). The examples below use `linux`. For Windows, you may need to use a tool like 7-Zip to extract `.tar.gz` archives.

For **Portable**, download and run directly:
```bash
chmod +x interstellar-linux-portable
./interstellar-linux-portable --help
```

For **Fast**, extract the archive and run from within:
```bash
tar -xzf interstellar-linux-fast.tar.gz
./cli.dist/interstellar --help
```

### Build from Source

Build your own binaries using [Nuitka](https://nuitka.net/):

```bash
git clone https://github.com/alkalescent/interstellar.git
cd interstellar

# Build portable (single file, slower startup)
MODE=onefile make build

# Build fast (directory, faster startup)
MODE=standalone make build
```

## 🚀 Usage

The CLI provides two main commands: `deconstruct` and `reconstruct`.

### Deconstruct Command

Split a BIP39 mnemonic into multiple parts or SLIP39 shares.

**From a hidden prompt:**
```bash
interstellar deconstruct
```

With neither `--mnemonic` nor `--filename`, the command prompts for the mnemonic and hides what you type. The prompt reads from the terminal, so pass a file with `--filename` instead of piping it in.

**From file:**
```bash
interstellar deconstruct --filename seed.txt
```

**From command line:**
```bash
interstellar deconstruct --mnemonic "your 24 word mnemonic phrase here..."
```

> **Warning**: A mnemonic passed with `--mnemonic`, or shares passed with `--shares`, are saved in your shell's history file and show in the process list while the command runs. Use the prompt or `--filename` instead.

**Options:**
- `--mnemonic`: BIP39 mnemonic to deconstruct, saved in shell history (default: empty, prompts unless `--filename` is given)
- `--filename`: File containing the BIP39 mnemonic (default: empty)
- `--standard`: Output format: `BIP39` or `SLIP39` (default: `SLIP39`)
- `--required`: Required shares for SLIP39 reconstruction (default: `2`)
- `--total`: Total SLIP39 shares to generate (default: `3`)
- `--digits`: Output numeric format instead of words (default: `false`)

For SLIP39, `--required` and `--total` take 1 of 1, or M of N with 2 <= M <= N <= 16.

**Output Format (JSON):**

For BIP39:
```json
[
  {"standard": "BIP39", "mnemonic": "first part words...", "eth_addr": "0x...", "digits": false},
  {"standard": "BIP39", "mnemonic": "second part words...", "eth_addr": "0x...", "digits": false}
]
```

For SLIP39:
```json
{
  "standard": "SLIP39",
  "shares": [
    ["share1 group1", "share2 group1", "share3 group1"],
    ["share1 group2", "share2 group2", "share3 group2"]
  ],
  "eth_addr": "0x...",
  "split": 2,
  "digits": false
}
```

`eth_addr` is the first Ethereum address (`m/44'/60'/0'/0/0`, without a passphrase) derived from a mnemonic. In BIP39 output, each part's `eth_addr` belongs to that part. In SLIP39 output, it belongs to the full mnemonic: record it with the shares and pass it to `reconstruct --address`. BIP39 output has no address for the full mnemonic, and deconstructing it with `--standard SLIP39` prints one. `split` is 2 when a 24-word mnemonic is split into two 12-word halves, each with its own group of shares, and 1 otherwise.

**Example: Create SLIP39 shares**
```bash
interstellar deconstruct \
  --standard SLIP39 \
  --required 2 \
  --total 3
```

**Example: Split into BIP39 parts**
```bash
interstellar deconstruct --standard BIP39
```

### Reconstruct Command

Reconstruct a BIP39 mnemonic from shares or parts.

**From a hidden prompt:**
```bash
interstellar reconstruct --address 0x...
```

With neither `--shares` nor `--filename`, the command prompts for the shares and hides what you type. Separate shares with commas and groups with semicolons.

**From file:**
```bash
interstellar reconstruct --filename shares.txt --address 0x...
```

**From command line (semicolon and comma delimited):**
```bash
interstellar reconstruct --shares "group1_share1,group1_share2;group2_share1,group2_share2"
```

**Options:**
- `--shares`: Shares to reconstruct, formatted as semicolon-separated groups with comma-separated shares, saved in shell history (default: empty, prompts unless `--filename` is given)
- `--filename`: File containing shares, one group per line with commas between shares (default: empty)
- `--standard`: Input format: `BIP39` or `SLIP39` (default: `SLIP39`)
- `--digits`: Input is in numeric format (default: `false`)
- `--address`: The `eth_addr` that `deconstruct` printed (default: empty, no check)

Groups and parts must stay in their original order. Swapped ones still form a valid mnemonic of a different wallet. Pass `--address` to make the command fail when the recovered mnemonic derives a different address.

**Output Format (JSON):**
```json
{
  "standard": "BIP39",
  "mnemonic": "reconstructed 24 word mnemonic phrase...",
  "eth_addr": "0x...",
  "required": 2,
  "digits": false
}
```

`required` is the SLIP39 threshold read from the shares, and 0 for BIP39 parts.

**Example: Reconstruct from SLIP39 shares at the prompt**
```bash
interstellar reconstruct --standard SLIP39 --address 0x...
```

**Example: Reconstruct from file**
```bash
interstellar reconstruct --filename shares.txt --standard SLIP39 --address 0x...
```

## 📁 Files

### Input Files

**For deconstruct command:**
The file should contain the mnemonic phrase:
```
word1 word2 word3 ... word24
```

**For reconstruct command:**
Shares should be grouped by line, in their original order, with comma-separated shares within each group (blank lines are skipped):
```
group1_share1,group1_share2
group2_share1,group2_share2
```

For example, with a 2-of-3 SLIP39 scheme split into 2 BIP39 parts:
```
academic acid ... (20 words),academic always ... (20 words)
academic arcade ... (20 words),academic axes ... (20 words)
```

### Command-Line Format

When using `--shares` or the prompt:
- Use commas (`,`) to separate shares within a group
- Use semicolons (`;`) to separate groups
- Example: `"group1_share1,group1_share2;group2_share1,group2_share2"`

### JSON Output

All commands output JSON for easy parsing and piping:

```bash
# Extract just the shares
interstellar deconstruct --filename seed.txt | jq -r '.shares'

# Extract the reconstructed mnemonic
interstellar reconstruct --filename shares.txt | jq -r '.mnemonic'

# Save output to file (the prompt still shows in the terminal)
interstellar deconstruct > output.json
```

## 🧪 Testing

Run the test suite:
```bash
uv run python -m pytest -v
```

Run with coverage reporting (requires 90% coverage):
```bash
uv run python -m pytest --cov --cov-report=term-missing --cov-fail-under=90
```

## 🔐 Security

⚠️ **Important Security Considerations:**

- **Run on an airgapped machine or a fresh [Tails](https://tails.net) installation via USB with networking disabled**
- Never share your seed phrase or private keys
- Store mnemonic backups securely in multiple physical locations
- SLIP39 shares should be distributed to different secure locations
- Use the digit format for metal plate backups or other durable storage
- Always verify reconstructed mnemonics match the original, for example with `reconstruct --address`
- Give mnemonics and shares at the prompt or with `--filename`: `--mnemonic` and `--shares` save them in shell history and show them in the process list
- Passphrases are unsupported. SLIP39 shares made with a passphrase in another tool, such as a hardware wallet, recover to a different mnemonic here with no error, and `eth_addr` is always derived without a BIP39 passphrase
- This tool is for educational and personal use only

## 🏗️ Architecture

The CLI consists of the following modules:

- **`tools.py`**: Core BIP39 and SLIP39 implementation
  - `BIP39` class: Mnemonic generation, validation, splitting
  - `SLIP39` class: Shamir Secret Sharing implementation
  
- **`cli.py`**: Command-line interface using Typer
  - `deconstruct`: Split mnemonics into parts/shares
  - `reconstruct`: Rebuild mnemonics from parts/shares

- **`test_tools.py`** / **`test_cli.py`**: Comprehensive test suites
  - BIP39 generation and roundtrip tests
  - SLIP39 share creation and reconstruction
  - CLI integration tests

## 📖 Examples

### Secure Backup Strategy

1. Generate a 24-word BIP39 mnemonic
2. Split it into 2 parts (two 12-word mnemonics)
3. Convert each part to SLIP39 shares (2-of-3)
4. Distribute 6 total shares across secure locations, with a record of the full mnemonic's `eth_addr`
5. To recover, need 2 shares from each group (4 shares total), in their original order

```bash
# Deconstruct (outputs JSON)
interstellar deconstruct \
  --standard SLIP39 \
  --required 2 \
  --total 3 > shares.json

# Extract the shares and the address to record
jq -r '.shares, .eth_addr' shares.json

# Reconstruct from file and check the address
interstellar reconstruct --filename backup_shares.txt --standard SLIP39 --address 0x...

# Or at the hidden prompt
interstellar reconstruct --standard SLIP39 --address 0x...
```

## 🔒 Cryptotag Odin 7 Backup Guide

The [Cryptotag Odin 7](https://cryptotag.io/products/odin/) is a titanium hexagonal prism system designed for SLIP39 backups. This guide explains how to use interstellar with Odin 7 for secure 24-word BIP39 seed storage.

### Overview

A 24-word BIP39 seed is split into **2 wallet parts** (12 words each), and each part is converted to **3 SLIP39 shares** (20 words each). This creates **6 total shares** that fit perfectly on 6 Odin hexagons, with 1 test hexagon for verification.

| Wallet Part | Shares | Hexagons |
|-------------|--------|----------|
| Wallet 1 (words 1-12) | Share 1, 2, 3 | Hexagons 1-3 |
| Wallet 2 (words 13-24) | Share 1, 2, 3 | Hexagons 4-6 |
| Test | For verification | Hexagon 7 |

### Store: Creating Shares with --digits

```bash
# Generate SLIP39 shares in digit format for metal engraving
interstellar deconstruct \
  --required 2 \
  --total 3 \
  --digits
```

Output structure:
```json
{
  "shares": [
    ["wallet1_share1 (20 digits)", "wallet1_share2", "wallet1_share3"],
    ["wallet2_share1 (20 digits)", "wallet2_share2", "wallet2_share3"]
  ],
  "eth_addr": "0x..."
}
```

Record `eth_addr` for the restore step.

### Hexagon Face Layout

Each Odin hexagon has 6 faces. Here's how to engrave them:

```
┌───────────────────────────────────────────────────┐
│                 FACE 1: METADATA                  │
├─────────────────────────┬─────────────────────────┤
│  Total:  3                             Share:  1  │
│  Thresh: 2                             Wallet: 1  │
└─────────────────────────┴─────────────────────────┘

┌───────────────────────────────────────────────────┐
│                 FACE 2: WORDS 1-4                 │
├────────────┬────────────┬────────────┬────────────┤
│                                                   │
│  1: [----]    2: [----]    3: [----]    4: [----] │
└────────────┴────────────┴────────────┴────────────┘

┌───────────────────────────────────────────────────┐
│                 FACE 3: WORDS 5-8                 │
├────────────┬────────────┬────────────┬────────────┤
│                                                   │
│  5: [----]    6: [----]    7: [----]    8: [----] │
└────────────┴────────────┴────────────┴────────────┘

... (Faces 4-6 continue pattern through word 20)
```

### Restore: Reconstructing from Shares

To recover your seed, you need **2 shares from each wallet part** (4 shares total).

1. Create a file `shares.txt` with your digit shares (comma-separated within each wallet group, one group per line):

```
123 456 789 ... 20 digits, 234 567 890 ... 20 digits
345 678 901 ... 20 digits, 456 789 012 ... 20 digits
```

Line 1 contains 2 shares from wallet 1, line 2 contains 2 shares from wallet 2. Swapped lines recover a different valid mnemonic, which `--address` rejects.

2. Reconstruct:

```bash
interstellar reconstruct --filename shares.txt --digits --address 0x...
```

### Security Notes

- Store each hexagon in a **different physical location**
- With 2-of-3 threshold, losing 1 hexagon per wallet part is recoverable
- The test hexagon can verify your engraving is correct before distributing

## 📚 Dependencies

- `mnemonic`: BIP39 mnemonic implementation
- `shamir-mnemonic`: SLIP39 Shamir Secret Sharing
- `typer`: Modern CLI framework

Ethereum address derivation is pure Python, in `wallet.py` and `keccak.py`.

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
