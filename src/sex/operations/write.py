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
        return cls(path, offset, length, data)

    def __init__(self, path: Path, offset: int, length: int, data: bytes) -> None:
        """
        Initialize a new write operation.

        :param path: The path to the file to write.
        :param offset: The offset in the file to start writeing from.
        :param length: The number of bytes to write.
        :param expected: The expected bytes that should be write.
        """
        self.path = path
        self.offset = offset
        self.length = length
        self.data = data

    def execute_mount(self, root: Path) -> None:
        path = root / self.path.relative_to(root.anchor)
        with path.open("r+b") as f:
            f.seek(self.offset)
            f.write(self.data)

    def is_executable_for_client(self, client: Path | Api) -> bool:
        return isinstance(client, Path)

    def update(self, state: State) -> None:
        state.resolve_file(self.path).data[
            self.offset : self.offset + self.length
        ] = self.data

    def verify_mount(self, root: Path) -> None:
        path = root / self.path.relative_to(root.anchor)
        with path.open("rb") as f:
            f.seek(self.offset)
            data = f.read(self.length)
        if data != self.data:
            Path(ACTUAL_DATA_FILENAME).write_bytes(data)
            Path(EXPECTED_DATA_FILENAME).write_bytes(self.data)
            raise VerificationError(
                f"Read data (at {ACTUAL_DATA_FILENAME}) does not match expected (at {EXPECTED_DATA_FILENAME})"
            )

    def verify_api(self, api: Api) -> None:
        data = api.download(self.path)
        data = data[self.offset : self.offset + self.length]
        if data != self.data:
            Path(ACTUAL_DATA_FILENAME).write_bytes(data)
            Path(EXPECTED_DATA_FILENAME).write_bytes(self.data)
            raise VerificationError(
                f"Read data (at {ACTUAL_DATA_FILENAME}) does not match expected (at {EXPECTED_DATA_FILENAME})"
            )

    def __str__(self) -> str:
        end = self.offset + self.length
        return (
            f"WRITE {self.path} "
            f"from 0x{self.offset:04x} ({self.offset}) "
            f"thru 0x{end:04x} ({end}) "
            f"or 0x{self.length:04x} ({self.length}) bytes"
        )
