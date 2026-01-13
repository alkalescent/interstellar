# interstellar

[![CI](https://github.com/alkalescent/interstellar/actions/workflows/release.yml/badge.svg)](https://github.com/alkalescent/interstellar/actions/workflows/release.yml)
[![PyPI version](https://badge.fury.io/py/interstellar.svg)](https://pypi.org/project/interstellar/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A command-line tool for managing cryptocurrency mnemonics using BIP39 and SLIP39 standards. This tool allows you to split, combine, and convert mnemonic phrases for secure key management.

## ✨ Features

- **BIP39 Support**: Generate, validate, and split BIP39 mnemonic phrases
- **SLIP39 Support**: Create Shamir Secret Sharing (SLIP39) shares from mnemonics
- **Flexible Splitting**: Deconstruct 24-word mnemonics into multiple 12-word parts
- **Share Reconstruction**: Reconstruct mnemonics from SLIP39 shares with threshold requirements
- **Digit Mode**: Convert mnemonics to/from numeric format for easier backup

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
brew install interstellar
```

### PyPI (Recommended)

```bash
pip install interstellar
```

After installation, use either the command directly or as a Python module:

```bash
# Direct command
interstellar --help

# As Python module
python -m interstellar --help
```

### From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/alkalescent/interstellar.git
cd interstellar
pip install -e .
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
MODE=onefile ./scripts/build.sh

# Build fast (directory, faster startup)
MODE=standalone ./scripts/build.sh
```

## 🚀 Usage

The CLI provides two main commands: `deconstruct` and `reconstruct`.

### Deconstruct Command

Split a BIP39 mnemonic into multiple parts or SLIP39 shares.

**From command line:**
```bash
interstellar deconstruct --mnemonic "your 24 word mnemonic phrase here..."
```

**From file:**
```bash
interstellar deconstruct --filename seed.txt
```

**Options:**
- `--mnemonic`: BIP39 mnemonic to deconstruct (default: empty, reads from file)
- `--filename`: File containing the BIP39 mnemonic (default: empty)
- `--standard`: Output format: `BIP39` or `SLIP39` (default: `SLIP39`)
- `--split`: Number of BIP39 parts to create (default: `2`)
- `--required`: Required shares for SLIP39 reconstruction (default: `2`)
- `--total`: Total SLIP39 shares to generate (default: `3`)
- `--digits`: Output numeric format instead of words (default: `false`)

**Output Format (JSON):**

For BIP39:
```json
[
  {"standard": "BIP39", "mnemonic": "first part words..."},
  {"standard": "BIP39", "mnemonic": "second part words..."}
]
```

For SLIP39:
```json
{
  "standard": "SLIP39",
  "shares": [
    ["share1 group1", "share2 group1", "share3 group1"],
    ["share1 group2", "share2 group2", "share3 group2"]
  ]
}
```

**Example: Create SLIP39 shares**
```bash
interstellar deconstruct \
  --mnemonic "word1 word2 ... word24" \
  --standard SLIP39 \
  --required 2 \
  --total 3
```

**Example: Split into BIP39 parts**
```bash
interstellar deconstruct \
  --mnemonic "word1 word2 ... word24" \
  --standard BIP39 \
  --split 2
```

### Reconstruct Command

Reconstruct a BIP39 mnemonic from shares or parts.

**From command line (semicolon and comma delimited):**
```bash
interstellar reconstruct --shares "group1_share1,group1_share2;group2_share1,group2_share2"
```

**From file:**
```bash
interstellar reconstruct --filename shares.txt
```

**Options:**
- `--shares`: Shares to reconstruct, formatted as semicolon-separated groups with comma-separated shares (default: empty, reads from file)
- `--filename`: File containing shares (default: empty)
- `--standard`: Input format: `BIP39` or `SLIP39` (default: `SLIP39`)
- `--digits`: Input is in numeric format (default: `false`)

**Output Format (JSON):**
```json
{
  "standard": "BIP39",
  "mnemonic": "reconstructed 24 word mnemonic phrase..."
}
```

**Example: Reconstruct from SLIP39 shares (CLI)**
```bash
interstellar reconstruct \
  --shares "group1_share1,group1_share2;group2_share1,group2_share2" \
  --standard SLIP39
```

**Example: Reconstruct from file**
```bash
interstellar reconstruct --filename shares.txt --standard SLIP39
```

## 📁 Files

### Input Files

**For deconstruct command:**
The file should contain the mnemonic phrase:
```
word1 word2 word3 ... word24
```

**For reconstruct command:**
Shares should be grouped by line, with comma-separated shares within each group:
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

When using `--shares` on the command line:
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

# Save output to file
interstellar deconstruct --mnemonic "word1 ..." > output.json
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
- Always verify reconstructed mnemonics match the original
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
4. Distribute 6 total shares across secure locations
5. To recover, need 2 shares from each group (4 shares total)

```bash
# Deconstruct (outputs JSON)
interstellar deconstruct \
  --mnemonic "abandon abandon ... art" \
  --standard SLIP39 \
  --required 2 \
  --total 3 > shares.json

# Extract shares with jq
cat shares.json | jq -r '.shares'

# Reconstruct from file
interstellar reconstruct --filename backup_shares.txt --standard SLIP39

# Or from command line
interstellar reconstruct \
  --shares "share1,share2;share3,share4" \
  --standard SLIP39
```

## 📚 Dependencies

- `hdwallet`: HD wallet generation and derivation (subdependency of slip39)
- `mnemonic`: BIP39 mnemonic implementation
- `slip39`: SLIP39 Shamir Secret Sharing
- `typer`: Modern CLI framework

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.