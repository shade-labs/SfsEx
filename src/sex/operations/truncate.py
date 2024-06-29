"""Truncate operation."""

import random
from pathlib import Path
from typing import Optional
from typing import Self

from sex.operation import Operation
from sex.operation import VerificationError
from sex.state import State


class Truncate(Operation):
    """Truncate operation."""

    MAX_SIZE = 0xFFFF

    @classmethod
    @property
    def name(cls):
        return "TRUNCATE"

    @classmethod
    def build(cls, state: State) -> Optional[Self]:
        try:
            path, file = random.choice(state.files())
        except IndexError:
            return None
        size = random.randint(0, cls.MAX_SIZE)
        return cls(path, size)

    def __init__(self, path: Path, size: int) -> None:
        """
        Initialize a new truncate operation.

        :param path: The path to the file to truncate.
        :param size: The size of the file to truncate.
        """
        self.path = path
        self.size = size

    def update(self, state: State) -> None:
        data: bytearray = state.resolve_file(self.path).data
        if len(data) < self.size:
            data.extend(b"\0" * (self.size - len(data)))
        else:
            del data[self.size :]

    def execute(self, fs: Path) -> None:
        path = fs / self.path
        with path.open("r+b") as f:
            f.truncate(self.size)

    def verify(self, fs: Path) -> None:
        path = fs / self.path
        if not path.exists():
            raise VerificationError(f"File {path} does not exist")
        if path.is_dir():
            raise VerificationError(f"Path {path} is a directory")
        if path.stat().st_size != self.size:
            raise VerificationError(
                f"File {path} has size {path.stat().st_size}, expected {self.size}"
            )

    def __str__(self) -> str:
        return f"TRUNCATE {self.path} " f"to size 0x{self.size:04x} ({self.size}) bytes"
