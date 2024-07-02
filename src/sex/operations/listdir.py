"""List directory operation."""

import random
from pathlib import Path
from typing import Optional
from typing import Self

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

    def execute(self, fs: Path) -> None:
        path = fs / self.path
        names = {child.name for child in path.iterdir()}
        if names != self.expected:
            raise VerificationError(
                f"Listed names {names!r} do not match expected {self.expected!r}"
            )

    def update(self, state: State) -> None:
        pass  # there is no change to the state

    def verify(self, fs: Path) -> None:
        pass  # there is no change to verify

    def __str__(self) -> str:
        return f"LISTDIR {self.path}"
