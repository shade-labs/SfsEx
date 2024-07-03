"""Command-line interface."""

import random
import time
from pathlib import Path
from typing import Optional

import click

from sex.operation import Operation
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
    "-i",
    "--interactive",
    type=int,
    help="Enter interactive mode after running N operations.",
)
@click.option(
    "-p", "--progress", is_flag=True, help="Show timeout progress while verifying."
)
@click.option(
    "-n",
    "--num-operations",
    type=int,
    help="Number of operations to generate.",
    default=-1,
)
@click.option(
    "-t", "--timeout", type=float, help="Verification timeout in seconds.", default=10
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
    seed: Optional[int],
    interactive: Optional[int],
    progress: bool,
    num_operations: Optional[int],
    timeout: float,
    mountpoints: list[Path],
) -> None:
    """SEx."""
    # ensure mountpoints are empty
    for mountpoint in mountpoints:
        existing_paths = list(
            path for path in mountpoint.iterdir() if not path.name.startswith(".")
        )
        if existing_paths:
            raise click.ClickException(
                f"Mountpoint {mountpoint} is not empty: {", ".join(str(p) for p in existing_paths)} exist.\n"
                "Use -r to remove all files before running."
            )

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
            continue

        # pick a mountpoint for the operation
        main_mountpoint = random.choice(mountpoints)

        if verbose:
            click.echo(f"{n}: {operation} on {main_mountpoint}")

        if interactive is not None and interactive <= n:
            print("Press Enter to execute the operation...", end="")
            input()

        # apply it
        operation.execute(main_mountpoint)
        operation.update(state)

        # verify it
        verify_operation(mountpoints, operation, timeout, progress)

        n += 1


def verify_operation(
    mountpoints: list[Path], operation: Operation, timeout: float, show_progress: bool
) -> None:
    """
    Verify that an operation was successfully applied to all mountpoints.

    :param mountpoints: The list of mountpoints to verify the operation on.
    :param operation: The operation to verify.
    :param timeout: The **total** timeout in seconds for verification across **all** mountpoints.
    :param show_progress: If true, print remaining timeout to stdout while verifying.
    """

    def print_progress(msg: str = ""):
        if show_progress:
            print(msg.ljust(80), end="\r")

    start = time.perf_counter()
    for other_mountpoint in mountpoints:
        while True:
            try:
                operation.verify(other_mountpoint)
            except Exception as e:
                remaining = timeout - (time.perf_counter() - start)
                if remaining <= 0:
                    raise e from None

                print_progress(
                    f"Verifying {operation.name} on {other_mountpoint}... ({remaining:.2f}s)",
                )
                time.sleep(0.1)
            else:
                break
            finally:
                print_progress()


if __name__ == "__main__":
    main(prog_name="SEx")
