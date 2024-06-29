"""Read operation."""

import random
from pathlib import Path
from typing import Optional
from typing import Self

from sex.operation import Operation
from sex.operation import VerificationError
from sex.state import State


class Read(Operation):
    """Read operation."""

    @classmethod
    @property
    def name(cls) -> str:
        return "READ"

    @classmethod
    def build(cls, state: State) -> Optional[Self]:
        try:
            path, file = random.choice(state.files())
        except IndexError:
            return None
        offset = random.randint(0, len(file.data))
        length = random.randint(0, len(file.data) - offset)
        return cls(path, offset, length, file.data[offset : offset + length])

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

    def execute(self, fs: Path) -> None:
        path = fs / self.path
        with path.open("rb") as f:
            f.seek(self.offset)
            data = f.read(self.length)
        if data != self.expected:
            raise VerificationError(
                f"Read data {data!r} does not match expected {self.expected!r}"
            )

    def update(self, state: State) -> None:
        pass  # there is no change to the state

    def verify(self, fs: Path) -> None:
        pass  # there is no change to verify

    def __str__(self) -> str:
        end = self.offset + self.length
        return (
            f"READ {self.path} "
            f"from 0x{self.offset:04x} ({self.offset}) "
            f"thru 0x{end:04x} ({end}) "
            f"or 0x{self.length:04x} ({self.length}) bytes"
        )
