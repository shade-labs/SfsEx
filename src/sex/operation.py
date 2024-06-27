"""Interface for filesystem operations."""

import abc
from pathlib import Path
from typing import Optional
from typing import Self

from sex.state import State


class Operation(abc.ABC):
    """Interface for filesystem operations."""

    @classmethod
    @abc.abstractmethod
    def build(cls, state: State) -> Optional[Self]:
        """
        Randomly generate a new operation that is valid for the given state.

        The standard library `random` module should be used to generate random values.
        It will be seeded with a fixed value by the caller, so the operation should be deterministic for a given state.

        :param state: The current state of the system.
        """
        pass

    @abc.abstractmethod
    def execute(self, fs: Path) -> None:
        """
        Execute the operation on the filesystem.

        This method should raise an exception if the operation fails or if the filesystem was found to be in an
        unexpected state.

        :param fs: The path to the root of the filesystem to operate on.
        :return: None
        """
        pass

    @abc.abstractmethod
    def verify(self, fs: Path) -> None:
        """
        Verify that the operation was successful.

        This method should be idempotent and should not modify the filesystem.

        This method should raise an exception if the operation was not successful or if the filesystem was found to be
        in an unexpected state.

        If it fails (by raising an exception), the call will be retried, and the filesystem should be left in the same
        state as it was before the method was called.

        :param fs: The path to the root of the filesystem to operate on.
        :return: None
        """
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        """:return: human-readable string representation of the operation."""
        pass
