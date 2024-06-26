"""Command-line interface."""

import click


@click.command()
@click.version_option()
def main() -> None:
    """SEx."""


if __name__ == "__main__":
    main(prog_name="SEx")  # pragma: no cover
