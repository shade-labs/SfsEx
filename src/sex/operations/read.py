"""Read operation."""

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
        return cls(path, file.data)

    def __init__(self, path: Path, expected: bytes) -> None:
        """
        Initialize a new read operation.

        :param path: The path to the file to read.
        :param offset: The offset in the file to start reading from.
        :param length: The number of bytes to read.
        :param expected: The expected bytes that should be read.
        """
        self.path = path
        self.expected = expected

    def execute_mount(self, root: Path) -> None:
        path = root / self.path.relative_to(root.anchor)
        with path.open("rb") as f:
            data = f.read()
        if data != self.expected:
            Path(ACTUAL_DATA_FILENAME).write_bytes(data)
            Path(EXPECTED_DATA_FILENAME).write_bytes(self.expected)
            raise VerificationError(
                f"Read data (at {ACTUAL_DATA_FILENAME}) does not match expected (at {EXPECTED_DATA_FILENAME})"
            )

    def execute_api(self, api: Api) -> None:
        data = api.download(self.path)
        if data != self.expected:
            Path(ACTUAL_DATA_FILENAME).write_bytes(data)
            Path(EXPECTED_DATA_FILENAME).write_bytes(self.expected)
            raise VerificationError(
                f"Read data (at {ACTUAL_DATA_FILENAME}) does not match expected (at {EXPECTED_DATA_FILENAME})"
            )

    def update(self, state: State) -> None:
        pass  # there is no change to the state

    def verify_mount(self, root: Path) -> None:
        pass  # there is no change to verify

    def verify_api(self, api: Api) -> None:
        pass  # there is no change to verify

    def __str__(self) -> str:
        return f"READ {self.path}"
