"""Delete operation."""

import random
from pathlib import Path
from typing import Optional
from typing import Self

from requests.exceptions import HTTPError

from sex.api import Api
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

    def execute_mount(self, root: Path) -> None:
        path = root / self.path.relative_to(root.anchor)
        path.unlink()

    def execute_api(self, api: Api) -> None:
        api.delete(self.path)

    def update(self, state: State) -> None:
        state.delete_file(self.path)

    def verify_mount(self, root: Path) -> None:
        path = root / self.path.relative_to(root.anchor)
        if path.exists():
            raise VerificationError(f"File {path} still exists")

    def verify_api(self, api: Api) -> None:
        try:
            api.getattr(self.path)
        except HTTPError as e:
            if e.response.status_code == 404:
                return
            raise
        raise VerificationError(f"File {self.path} still exists")

    def __str__(self) -> str:
        return f"DELETE {self.path}"
