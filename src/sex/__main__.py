"""Command-line interface."""

import random
import time
from pathlib import Path

import click

from sex.operations.create import Create
from sex.operations.delete import Delete
from sex.operations.read import Read
from sex.operations.truncate import Truncate
from sex.operations.write import Write
from sex.state import State


operations = [Read, Write, Create, Delete, Truncate]


@click.command()
@click.version_option()
@click.option("-v", "--verbose", is_flag=True, help="Debug output for all operations.")
@click.option("-s", "--seed", type=int, help="Seed for the random number generator.")
@click.option(
    "-n",
    "--num-operations",
    type=int,
    help="Number of operations to generate.",
    default=-1,
)
@click.option(
    "-t", "--timeout", type=float, help="Verification timeout in seconds.", default=5
)
@click.argument(
    "mountpoints",
    nargs=-1,
    required=True,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, resolve_path=True, path_type=Path
    ),
)
def main(
    verbose: bool,
    seed: int,
    num_operations: int,
    timeout: float,
    mountpoints: list[str],
) -> None:
    """SEx."""
    state = State()

    if seed is None:
        seed = random.randint(0, 2**8)

    click.echo(f"Using seed: {seed}")
    random.seed(seed)

    n = 0
    while num_operations == -1 or n < num_operations:
        # pick a new operation at random
        op_cls = random.choice(operations)
        operation = op_cls.build(state)
        if operation is None:
            # skip operation
            if verbose:
                click.echo(f"Skip {op_cls.name}")
            continue

        # pick a mountpoint for the operation
        main_mountpoint = random.choice(mountpoints)

        if verbose:
            click.echo(f"{n}: {operation} on {main_mountpoint}")

        # apply it
        operation.execute(main_mountpoint)
        operation.update(state)

        # verify on all mountpoints
        start = time.perf_counter()
        for other_mountpoint in mountpoints:
            while True:
                try:
                    operation.verify(other_mountpoint)
                except Exception as e:
                    if time.perf_counter() - start > timeout:
                        raise e from None
                    time.sleep(0.1)
                else:
                    break

        n += 1


if __name__ == "__main__":
    main(prog_name="SEx")
