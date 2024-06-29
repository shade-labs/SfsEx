"""Create operation."""

import random
from pathlib import Path
from typing import Optional
from typing import Self

from sex.name import gen_name
from sex.operation import Operation
from sex.operation import VerificationError
from sex.state import State


class Create(Operation):
    """Create operation."""

    MAX_SIZE = 0xFFFF

    @classmethod
    @property
    def name(cls):
        return "CREATE"

    @classmethod
    def build(cls, state: State) -> Optional[Self]:
        try:
            path, dir = random.choice(state.directories())
        except IndexError:
            return None
        size = random.randint(0, cls.MAX_SIZE)
        return cls(path / f"{gen_name()}.bin", size)

    def __init__(self, path: Path, size: int) -> None:
        """
        Initialize a new create operation.

        :param path: The path to the file to create.
        :param size: The size of the file to create.
        """
        self.path = path
        self.size = size

    def update(self, state: State) -> None:
        state.create_file(self.path, bytearray(b"\0" * self.size))

    def execute(self, fs: Path) -> None:
        path = fs / self.path
        path.write_bytes(b"\0" * self.size)

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
        return f"CREATE {self.path} " f"of size 0x{self.size:04x} ({self.size}) bytes"
