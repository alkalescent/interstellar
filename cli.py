import typer
import logging
import json
from typing import Annotated
from tools import BIP39, SLIP39
logging.getLogger("slip39").setLevel(logging.ERROR)


class CLI:
    """Command Line Interface for BIP39 mnemonic generation and validation."""

    def __init__(self):
        self.bip39 = BIP39()
        self.slip39 = SLIP39()

    def get_mnemos(self, filename: str) -> list[list[str]]:
        """Get the mnemos from a file."""
        with open(filename, "r") as f:
            return [[
                subline.strip() for subline in line.strip().split(',')
            ] for line in f.readlines()]

    def enforce_standard(self, standard: str):
        if standard.upper() not in ["SLIP39", "BIP39"]:
            raise ValueError("Standard must be either 'SLIP39' or 'BIP39'")

    def parse_2D_list(self, value: str) -> list[list[str]]:
        """Parse a string representation of a 2D list into an actual 2D list."""
        value = value.strip()
        if not value:
            return []
        lines = value.split(';')
        result = [line.strip().split(',') for line in lines]
        return result


app = typer.Typer()
cli = CLI()


@app.command()
def deconstruct(
    mnemonic: Annotated[str, typer.Option(
        help="BIP39 mnemonic to deconstruct")] = "",
    filename: Annotated[str, typer.Option(
        help="File containing the BIP39 mnemonic"
    )] = "",
    standard: Annotated[str, typer.Option(
        help="Output format: 'BIP39' or 'SLIP39'")] = "SLIP39",
    required: Annotated[int, typer.Option(
        help="Number of required shares for SLIP39 reconstruction (e.g. 2 of 3)")] = 2,
    total: Annotated[int, typer.Option(
        help="Number of total shares for SLIP39 reconstruction (e.g. 3 of 3)")] = 3,
    digits: Annotated[bool, typer.Option(
        help="Output format: use digits instead of words"
    )] = False
):
    cli.enforce_standard(standard)
    if not mnemonic:
        mnemonic = cli.get_mnemos(filename)[0][0]
    if not mnemonic:
        raise ValueError("Mnemonic is required")

    # Auto-detect split based on mnemonic length
    word_count = len(mnemonic.split())
    split = 2 if word_count == 24 else 1

    bip_parts = cli.bip39.deconstruct(mnemonic, split)
    if standard.upper() == "BIP39":
        output = [{
            "standard": "BIP39",
            "mnemonic": bip_part,
            "eth_addr": cli.bip39.eth(bip_part),
            "digits": digits
        } for bip_part in bip_parts]
        typer.echo(json.dumps(output))
        raise typer.Exit(code=0)
    else:
        total_shares: list[list[str]] = []
        for part in bip_parts:
            shares = cli.slip39.deconstruct(part, required, total)
            if digits:
                shares = [" ".join(str(cli.slip39.map[word])
                                   for word in share.split()) for share in shares]
            total_shares.append(shares)

        output = {
            "standard": "SLIP39",
            "shares": total_shares,
            "split": split,
            "digits": digits
        }
        typer.echo(json.dumps(output))
        raise typer.Exit(code=0)


@app.command()
def reconstruct(
    shares: Annotated[str, typer.Option(
        help="SLIP39 shares to reconstruct",
        parser=cli.parse_2D_list
    )] = "",
    filename: Annotated[str, typer.Option(
        help="File containing the SLIP39 shares (newline separated)"
    )] = "",
    standard: Annotated[str, typer.Option(
        help="Input format: 'BIP39' or 'SLIP39'")] = "SLIP39",
    digits: Annotated[bool, typer.Option(
        help="Input format: use digits instead of words"
    )] = False,
):
    cli.enforce_standard(standard)
    if not shares:
        shares = cli.get_mnemos(filename)
    if not shares:
        raise ValueError("Shares are required")

    required = 0

    if standard.upper() == "SLIP39":
        groups = shares
        shares = []
        for gidx, group in enumerate(groups):
            if digits:
                group = [" ".join(cli.slip39.words[int(idx)-1]
                                  for idx in member.split()) for member in group]

            required = cli.slip39.get_required(group[gidx])
            shares.append(cli.slip39.reconstruct(group))
    else:  # BIP39
        shares = [part for group in shares for part in group]
        if digits:
            shares = [" ".join(cli.bip39.words[int(idx)-1]
                               for idx in share.split()) for share in shares[0]]
    reconstructed = cli.bip39.reconstruct(shares)
    output = {
        "standard": "BIP39",
        "mnemonic": reconstructed,
        "eth_addr": cli.bip39.eth(reconstructed),
        "required": required,
        "digits": digits
    }
    typer.echo(json.dumps(output))
    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
# TODO: move to new repo
# TODO: add github release action and checksum
# TODO: release on PyPI w name kintsugi alt
# TODO: message PyPi user
