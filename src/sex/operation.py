"""Interface for filesystem operations."""

import abc
from pathlib import Path
from typing import Optional
from typing import Self

from sex.api import Api
from sex.state import State


class Operation(abc.ABC):
    """Interface for filesystem operations."""

    @classmethod
    @abc.abstractmethod
    def build(cls, state: State) -> Optional[Self]:
        """
        Randomly generate a new operation that is valid for the given state.

        This method should return None if no valid operation can be generated for the given state.

        This method should not modify the state of the system.

        The standard library `random` module should be used to generate random values.
        It will be seeded with a fixed value by the caller, so the operation should be deterministic for a given state.

        :param state: The current state of the system.
        """
        pass

    def is_executable_for_client(self, client: Path | Api) -> bool:
        """
        Check if the operation can be executed on the client.

        :param client: The client to check, either a Path to a mountpoint or an Api.
        :return: True if the operation can be executed on the client, False otherwise.
        """
        return True

    def execute(self, client: Path | Api) -> None:
        """
        Execute the operation on the client.

        This method should raise an exception if the operation fails or if the system was found to be in an
        unexpected state.

        :param client: The client to operate on, either a Path to a mountpoint or an Api.
        :return: None
        """
        if isinstance(client, Path):
            self.execute_mount(client)
        elif isinstance(client, Api):
            self.execute_api(client)
        else:
            raise ValueError(f"Invalid client: {client}")

    def execute_mount(self, root: Path) -> None:
        """
        Execute the operation on the filesystem.

        This method should raise an exception if the operation fails or if the filesystem was found to be in an
        unexpected state.

        :param fs: The filesystem to operate on.
        :return: None
        """
        raise NotImplementedError()

    def execute_api(self, api: Api) -> None:
        """
        Execute the operation on the API.

        This method should raise an exception if the operation fails or if the API was found to be in an
        unexpected state.

        :param api: The API to operate on.
        :return: None
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def update(self, state: State) -> None:
        """
        Update the state of the virtual system to reflect the operation.

        This method should raise an exception if the operation fails or if the filesystem was found to be in an
        unexpected state.

        :param state: The current state of the system.
        :return: None
        """

    def verify(self, client: Path | Api) -> None:
        """
        Verify that the operation was successful.

        This method should be idempotent and should not change the state of the system.

        This method should raise an exception if the operation was not successful or if the system was found to be
        in an unexpected state.

        If it fails (by raising an exception), the call will be retried, and the system should be left in the same
        state as it was before the method was called.

        :param client: The client to verify the operation on, either a Path to a mountpoint or an Api.
        :return: None
        """
        if isinstance(client, Path):
            self.verify_mount(client)
        elif isinstance(client, Api):
            self.verify_api(client)
        else:
            raise ValueError(f"Invalid client: {client}")

    def verify_mount(self, root: Path) -> None:
        """
        Verify that the operation was successful on the filesystem.

        This method should be idempotent and should not change the state of the system.

        This method should raise an exception if the operation was not successful or if the filesystem was found to be
        in an unexpected state.

        If it fails (by raising an exception), the call will be retried, and the system should be left in the same
        state as it was before the method was called.

        :param fs: The filesystem to verify the operation on.
        :return: None
        """
        raise NotImplementedError()

    def verify_api(self, api: Api) -> None:
        """
        Verify that the operation was successful on the API.

        This method should be idempotent and should not change the state of the system.

        This method should raise an exception if the operation was not successful or if the API was found to be
        in an unexpected state.

        If it fails (by raising an exception), the call will be retried, and the system should be left in the same
        state as it was before the method was called.

        :param api: The API to verify the operation on.
        :return: None
        """
        raise NotImplementedError()

    @classmethod
    @property
    @abc.abstractmethod
    def name(cls) -> str:
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        """:return: human-readable string representation of the operation."""
        pass


class VerificationError(Exception):
    """
    Verification error.

    The state of the system is not as expected.
    """
