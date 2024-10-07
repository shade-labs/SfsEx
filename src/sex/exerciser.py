"""SEx main command."""

import random
import time
from pathlib import Path
from typing import Optional

import click

from sex.api import Api
from sex.api import ApiAddrType
from sex.operation import Operation
from sex.operations.create import Create
from sex.operations.delete import Delete
from sex.operations.listdir import Listdir
from sex.operations.read import Read
from sex.operations.truncate import Truncate
from sex.operations.write import Write
from sex.state import State


operations = [Read, Write, Create, Delete, Truncate, Listdir]


@click.command()
@click.version_option()
@click.option("-v", "--verbose", is_flag=True, help="Debug output for all operations.")
@click.option("-s", "--seed", type=int, help="Seed for the random number generator.")
@click.option(
    "-p",
    "--position",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, resolve_path=True, path_type=Path
    ),
    help="Path to a position file to run.",
)
@click.option(
    "-i",
    "--interactive",
    type=int,
    help="Enter interactive mode after running N operations.",
)
@click.option("--progress", is_flag=True, help="Show timeout progress while verifying.")
@click.option(
    "-n",
    "--num-operations",
    type=int,
    help="Number of operations to generate.",
    default=-1,
)
@click.option(
    "-t", "--timeout", type=float, help="Verification timeout in seconds.", default=60
)
@click.option(
    "-c",
    "--cleanup",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, resolve_path=True, path_type=Path
    ),
    help="Path to a mount directory to cleanup after running.",
)
@click.option(
    "-m",
    "--mountpoint",
    "mountpoints",
    multiple=True,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, resolve_path=True, path_type=Path
    ),
)
@click.option(
    "-a",
    "--api-url",
    "apis",
    multiple=True,
    type=ApiAddrType(),
)
def exercise(
    verbose: bool,
    position: Optional[Path],
    seed: Optional[int],
    interactive: Optional[int],
    progress: bool,
    num_operations: Optional[int],
    timeout: float,
    cleanup: Optional[Path],
    mountpoints: list[Path],
    apis: list[Api],
) -> None:
    """Run the exerciser."""
    if not mountpoints and not apis:
        raise click.ClickException(
            "At least one mountpoint or API URL must be provided."
        )

    if cleanup and cleanup not in mountpoints:
        raise click.ClickException("Path to clean up must be a mountpoint.")

    # ensure mountpoints are empty
    for mountpoint in mountpoints:
        existing_paths = [
            path for path in mountpoint.iterdir() if not path.name.startswith(".")
        ]
        if existing_paths:
            raise click.ClickException(
                f"Mountpoint {mountpoint} is not empty: {", ".join(str(p) for p in existing_paths)} exist.\n"
            )

    # ensure apis are empty
    for api_url in apis:
        existing_paths = [Path(obj["path"]) for obj in api_url.listdir("/")]
        existing_paths = [
            path for path in existing_paths if not path.name.startswith(".")
        ]
        if existing_paths:
            raise click.ClickException(
                f"API {api_url.url} is not empty: {", ".join(str(p) for p in existing_paths)} exist.\n"
            )

    with State(cleanup) as state:
        if position:
            click.echo(f"Using position file: {position}")
            exercise_position(
                state,
                verbose,
                position,
                timeout,
                mountpoints,
                apis,
                interactive,
                progress,
            )
        else:
            if seed is None:
                seed = random.randint(0, 2**8)

            click.echo(f"Using seed: {seed}")
            random.seed(seed)

            exercise_random(
                state,
                verbose,
                num_operations,
                timeout,
                mountpoints,
                apis,
                interactive,
                progress,
            )


def exercise_position(
    state: State,
    verbose: bool,
    position_file: Path,
    timeout: float,
    mountpoints: list[Path],
    apis: list[Api],
    interactive: Optional[int],
    progress: bool,
) -> None:
    """
    Run the exerciser using a position file.

    :param position_file: Path to position file describing the operations to run.
    """
    for n, step in enumerate(eval(position_file.read_text())):  # noqa: S307
        mountpoint_idx, operation = step(state)
        try:
            mountpoint = mountpoints[mountpoint_idx]
        except IndexError:
            raise click.ClickException(
                f"Invalid mountpoint index: {mountpoint_idx} in position file {position_file}"
            ) from None

        if verbose:
            click.echo(f"{n}: {operation} on {mountpoint}")

        if interactive is not None and interactive <= n:
            print("Press Enter to execute the operation...", end="")
            input()

        # apply it
        operation.execute(mountpoint)
        operation.update(state)

        # verify it
        verify_operation(mountpoints + apis, operation, timeout, progress)


def exercise_random(
    state: State,
    verbose: bool,
    num_operations: int,
    timeout: float,
    mountpoints: list[Path],
    apis: list[Api],
    interactive: Optional[int],
    progress: bool,
) -> None:
    """
    Run the exerciser with random operations.

    :param num_operations: The number of operations to generate.
    """
    n = 0
    while num_operations == -1 or n < num_operations:
        # pick a new operation at random
        op_cls = random.choice(operations)
        operation = op_cls.build(state)
        if operation is None:
            # skip operation
            continue

        # pick a mountpoint for the operation
        main_client = random.choice(mountpoints + apis)
        if not operation.is_executable_for_client(main_client):
            continue

        if verbose:
            click.echo(f"{n}: {operation} on {main_client}")

        if interactive is not None and interactive <= n:
            print("Press Enter to execute the operation...", end="")
            input()

        # apply it
        operation.execute(main_client)
        operation.update(state)

        # verify it
        verify_operation(mountpoints + apis, operation, timeout, progress)

        n += 1


def verify_operation(
    clients: list[Path | Api], operation: Operation, timeout: float, show_progress: bool
) -> None:
    """
    Verify that an operation was successfully applied to all mountpoints.

    :param clients: list of clients to verify the operation on.
    :param operation: The operation to verify.
    :param timeout: The **total** timeout in seconds for verification across **all** mountpoints.
    :param show_progress: If true, print remaining timeout to stdout while verifying.
    """

    def print_progress(msg: str = ""):
        if show_progress:
            print(msg.ljust(80), end="\r")

    start = time.perf_counter()
    for client in clients:
        while True:
            try:
                operation.verify(client)
            except Exception as e:
                remaining = timeout - (time.perf_counter() - start)
                if remaining <= 0:
                    raise e from None

                print_progress(
                    f"Verifying {operation.name} on {client}... ({remaining:.2f}s)",
                )
                time.sleep(0.1)
            else:
                break
            finally:
                print_progress()
