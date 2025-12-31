# interstellar

A command-line tool for managing cryptocurrency mnemonics using BIP39 and SLIP39 standards. This tool allows you to split, combine, and convert mnemonic phrases for secure key management.

## Features

- **BIP39 Support**: Generate, validate, and split BIP39 mnemonic phrases
- **SLIP39 Support**: Create Shamir Secret Sharing (SLIP39) shares from mnemonics
- **Flexible Splitting**: Deconstruct 24-word mnemonics into multiple 12-word parts
- **Share Reconstruction**: Reconstruct mnemonics from SLIP39 shares with threshold requirements
- **Digit Mode**: Convert mnemonics to/from numeric format for easier backup

## Installation

### Development Setup

From the CLI directory:
```bash
cd cli
uv sync
```

### Build Binary

From the repository root:
```bash
./scripts/cli.sh
```

This creates a standalone executable at `dist/cli`.

## Usage

The CLI provides two main commands: `deconstruct` and `reconstruct`.

### Deconstruct Command

Split a BIP39 mnemonic into multiple parts or SLIP39 shares.

**From command line:**
```bash
./dist/cli deconstruct --mnemonic "your 24 word mnemonic phrase here..."
```

**From file:**
```bash
./dist/cli deconstruct --filename seed.txt
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
./dist/cli deconstruct \
  --mnemonic "word1 word2 ... word24" \
  --standard SLIP39 \
  --required 2 \
  --total 3
```

**Example: Split into BIP39 parts**
```bash
./dist/cli deconstruct \
  --mnemonic "word1 word2 ... word24" \
  --standard BIP39 \
  --split 2
```

### Reconstruct Command

Reconstruct a BIP39 mnemonic from shares or parts.

**From command line (semicolon and comma delimited):**
```bash
./dist/cli reconstruct --shares "group1_share1,group1_share2;group2_share1,group2_share2"
```

**From file:**
```bash
./dist/cli reconstruct --filename shares.txt
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
./dist/cli reconstruct \
  --shares "group1_share1,group1_share2;group2_share1,group2_share2" \
  --standard SLIP39
```

**Example: Reconstruct from file**
```bash
./dist/cli reconstruct --filename shares.txt --standard SLIP39
```

## File Format

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
./dist/cli deconstruct --filename seed.txt | jq -r '.shares'

# Extract the reconstructed mnemonic
./dist/cli reconstruct --filename shares.txt | jq -r '.mnemonic'

# Save output to file
./dist/cli deconstruct --mnemonic "word1 ..." > output.json
```

## Testing

Run the test suite:
```bash
cd cli
uv run pytest -v
```

Run with coverage reporting (requires 90% coverage):
```bash
uv run pytest --cov --cov-report=term-missing --cov-fail-under=90
```

## Security Notes

⚠️ **Important Security Considerations:**

- Never share your seed phrase or private keys
- Store mnemonic backups securely in multiple physical locations
- SLIP39 shares should be distributed to different secure locations
- Use the digit format for metal plate backups or other durable storage
- Always verify reconstructed mnemonics match the original
- This tool is for educational and personal use only

## Architecture

The CLI consists of three main modules:

- **`tools.py`**: Core BIP39 and SLIP39 implementation
  - `BIP39` class: Mnemonic generation, validation, splitting
  - `SLIP39` class: Shamir Secret Sharing implementation
  
- **`cli.py`**: Command-line interface using Typer
  - `deconstruct`: Split mnemonics into parts/shares
  - `reconstruct`: Rebuild mnemonics from parts/shares

- **`test_tools.py`**: Comprehensive test suite
  - BIP39 generation and roundtrip tests
  - SLIP39 share creation and reconstruction
  - Integration tests for full workflows

## Examples

### Secure Backup Strategy

1. Generate a 24-word BIP39 mnemonic
2. Split it into 2 parts (two 12-word mnemonics)
3. Convert each part to SLIP39 shares (2-of-3)
4. Distribute 6 total shares across secure locations
5. To recover, need 2 shares from each group (4 shares total)

```bash
# Deconstruct (outputs JSON)
./dist/cli deconstruct \
  --mnemonic "abandon abandon ... art" \
  --standard SLIP39 \
  --required 2 \
  --total 3 > shares.json

# Extract shares with jq
cat shares.json | jq -r '.shares'

# Reconstruct from file
./dist/cli reconstruct --filename backup_shares.txt --standard SLIP39

# Or from command line
./dist/cli reconstruct \
  --shares "share1,share2;share3,share4" \
  --standard SLIP39
```

## Dependencies

- `hdwallet`: HD wallet generation and derivation
- `mnemonic`: BIP39 mnemonic implementation
- `slip39`: SLIP39 Shamir Secret Sharing
- `typer`: Modern CLI framework
- `pytest`: Testing framework

## License

For personal and educational use.