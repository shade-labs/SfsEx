"""Delete operation."""

import random
from pathlib import Path
from typing import Optional
from typing import Self

from sex.operation import Operation
from sex.operation import VerificationError
from sex.state import State


class Delete(Operation):
    """Delete operation."""

    @classmethod
    @property
    def name(cls):
        return "DELETE"

    @classmethod
    def build(cls, state: State) -> Optional[Self]:
        try:
            path, file = random.choice(state.files())
        except IndexError:
            return None
        return cls(path)

    def __init__(self, path: Path) -> None:
        """
        Initialize a new delete operation.

        :param path: The path to the file to delete.
        """
        self.path = path

    def execute(self, fs: Path) -> None:
        path = fs / self.path
        path.unlink()

    def update(self, state: State) -> None:
        state.delete_file(self.path)

    def verify(self, fs: Path) -> None:
        path = fs / self.path
        if path.exists():
            raise VerificationError(f"File {path} still exists")

    def __str__(self) -> str:
        return f"DELETE {self.path}"
