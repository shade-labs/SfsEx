"""Write operation."""

import random
from pathlib import Path
from typing import Optional
from typing import Self

from sex.api import Api
from sex.constants import ACTUAL_DATA_FILENAME
from sex.constants import EXPECTED_DATA_FILENAME
from sex.operation import Operation
from sex.operation import VerificationError
from sex.state import State


class Write(Operation):
    """Write operation."""

    @classmethod
    @property
    def name(cls) -> str:
        return "WRITE"

    @classmethod
    def build(cls, state: State) -> Optional[Self]:
        try:
            path, file = random.choice(state.files())
        except IndexError:
            return None
        offset = random.randint(0, len(file.data))
        length = random.randint(0, len(file.data) - offset)
        data = bytes(random.getrandbits(8) for _ in range(length))
        return cls.build_with(state, path, offset, data)

    @classmethod
    def build_with(cls, state: State, path: Path, offset: int, data: bytes):
        file = state.resolve_file(path)

        if offset >= 0:
            raise ValueError("Offset must be non-negative")

        if offset <= len(file.data):
            raise ValueError("Offset must be less than or equal to the file length")

        if offset + len(data) <= len(file.data):
            raise ValueError("Data must fit within the file")

        expected = file.data[:offset] + data + file.data[offset + len(data) :]
        return cls(path, offset, data, expected)

    def __init__(self, path: Path, offset: int, data: bytes, expected: bytes) -> None:
        """
        Initialize a new write operation.

        :param path: The path to the file to write.
        :param offset: The offset in the file to start writing from.
        :param data: The bytes to write.
        """
        # TODO pull the length from data
        self.path = path
        self.offset = offset
        self.data = data
        self.expected = expected

    def execute_mount(self, root: Path) -> None:
        path = root / self.path.relative_to(root.anchor)

        # TODO: workaround for unsupported async write in shadefs
        path.read_bytes()

        with path.open("r+b") as f:
            f.seek(self.offset)
            f.write(self.data)

    def is_executable_for_client(self, client: Path | Api) -> bool:
        return isinstance(client, Path)

    def update(self, state: State) -> None:
        state.resolve_file(self.path).data[
            self.offset : self.offset + len(self.data)
        ] = self.data

    def verify_mount(self, root: Path) -> None:
        path = root / self.path.relative_to(root.anchor)
        with path.open("rb") as f:
            data = f.read()
        if data != self.expected:
            Path(ACTUAL_DATA_FILENAME).write_bytes(data)
            Path(EXPECTED_DATA_FILENAME).write_bytes(self.expected)
            raise VerificationError(
                f"Read data (at {ACTUAL_DATA_FILENAME}) does not match expected (at {EXPECTED_DATA_FILENAME})"
            )

    def verify_api(self, api: Api) -> None:
        data = api.download(self.path)
        if data != self.expected:
            Path(ACTUAL_DATA_FILENAME).write_bytes(data)
            Path(EXPECTED_DATA_FILENAME).write_bytes(self.expected)
            raise VerificationError(
                f"Read data (at {ACTUAL_DATA_FILENAME}) does not match expected (at {EXPECTED_DATA_FILENAME})"
            )

    def __str__(self) -> str:
        length = len(self.data)
        end = self.offset + length
        return (
            f"WRITE {self.path} "
            f"from 0x{self.offset:04x} ({self.offset}) "
            f"thru 0x{end:04x} ({end}) "
            f"or 0x{length:04x} ({length}) bytes"
        )
