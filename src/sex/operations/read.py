"""Read operation."""

from pathlib import Path
from typing import Optional
from typing import Self

from sex.operation import Operation
from sex.state import State


class Read(Operation):
    """Read operation."""

    def __init__(self, path: Path, offset: int, length: int, expected: bytes) -> None:
        """
        Initialize a new read operation.

        :param path: The path to the file to read.
        :param offset: The offset in the file to start reading from.
        :param length: The number of bytes to read.
        :param expected: The expected bytes that should be read.
        """
        self.path = path
        self.offset = offset
        self.length = length
        self.expected = expected

    @classmethod
    def build(cls, state: State) -> Optional[Self]:
        raise NotImplementedError

    def execute(self, fs: Path) -> None:
        raise NotImplementedError

    def verify(self, fs: Path) -> None:
        raise NotImplementedError

    def __str__(self) -> str:
        end = self.offset + self.length
        return (
            f"READ {self.path} "
            f"from 0x{self.offset:08x} ({self.offset}) "
            f"thru 0x{end:08x} ({end}) "
            f"or 0x{self.length:08x} ({self.length}) bytes"
        )
