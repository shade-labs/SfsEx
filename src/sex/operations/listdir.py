"""List directory operation."""

import random
from pathlib import Path
from typing import Optional
from typing import Self

from sex.api import Api
from sex.operation import Operation
from sex.operation import VerificationError
from sex.state import State


class Listdir(Operation):
    """List directory operation."""

    @classmethod
    @property
    def name(cls) -> str:
        return "LISTDIR"

    @classmethod
    def build(cls, state: State) -> Optional[Self]:
        try:
            path, directory = random.choice(state.directories())
        except IndexError:
            return None
        return cls(path, set(directory.children.keys()))

    def __init__(self, path: Path, expected: set[str]) -> None:
        """
        Initialize a new listdir operation.

        :param path: The path to the directory to list.
        :param expected: The expected names of files and folders in the directory.
        """
        self.path = path
        self.expected = expected

    def execute_mount(self, root: Path) -> None:
        path = root / self.path.relative_to(root.anchor)
        names = {
            child.name for child in path.iterdir() if not child.name.startswith(".")
        }
        if names != self.expected:
            raise VerificationError(
                f"Listed names {names!r} do not match expected {self.expected!r}"
            )

    def execute_api(self, api: Api) -> None:
        names = {Path(obj["path"]).name for obj in api.listdir(self.path)}
        names = {name for name in names if not name.startswith(".")}
        if names != self.expected:
            raise VerificationError(
                f"Listed names {names!r} do not match expected {self.expected!r}"
            )

    def update(self, state: State) -> None:
        pass  # there is no change to the state

    def verify_mount(self, root: Path) -> None:
        pass  # there is no change to verify

    def verify_api(self, api: Api) -> None:
        pass  # there is no change to verify

    def __str__(self) -> str:
        return f"LISTDIR {self.path}"
