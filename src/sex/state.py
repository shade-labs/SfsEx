"""Code to track filesystem state."""

import abc
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Iterator
from typing import Optional
from typing import Tuple


class StateError(Exception):
    """Exception raised for errors in the filesystem state."""


@dataclass
class Node(abc.ABC):
    """Representation of a filesystem node."""


@dataclass
class File(Node):
    """Representation of a file."""

    data: bytearray = field(default_factory=bytearray)


@dataclass
class Directory(Node):
    """Representation of a directory."""

    children: dict[str, Node] = field(default_factory=dict)


class State:
    """Representation of the filesystem state."""

    root: Directory
    cleanup_mount_path: Optional[Path]

    def __init__(self, cleanup_mount_path: Optional[Path]) -> None:
        """Initialize an empty virtual filesystem."""
        self.root = Directory()
        self.cleanup_mount_path = cleanup_mount_path

    def __enter__(self):
        """Enter the filesystem state context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the filesystem state context."""
        if not self.cleanup_mount_path:
            return

        for path, _ in self.files():
            (self.cleanup_mount_path / path.relative_to("/")).unlink()

        for path, _ in self.directories():
            # don't try to remove the mountpoint
            if path == Path("/"):
                continue

            (self.cleanup_mount_path / path.relative_to("/")).rmdir()

    def _iter_nodes(self) -> Iterator[Tuple[Path, Node]]:
        """Iterate over all nodes in the filesystem."""
        q = [(Path("/"), self.root)]
        while q:
            path, node = q.pop()
            yield path, node
            if isinstance(node, Directory):
                for name, child in node.children.items():
                    q.append((path / name, child))

    def files(self) -> list[Tuple[Path, File]]:
        """Iterate over all files in the filesystem."""
        return [
            (path, node) for path, node in self._iter_nodes() if isinstance(node, File)
        ]

    def directories(self) -> list[Tuple[Path, Directory]]:
        """Iterate over all directories in the filesystem."""
        return [
            (path, node)
            for path, node in self._iter_nodes()
            if isinstance(node, Directory)
        ]

    def _resolve(self, path: Path) -> Node:
        """Resolve a path to a node in the filesystem."""
        node = self.root
        for name in path.parts[1:]:
            if isinstance(node, File):
                raise StateError(f"Path {path} does not exist")
            if name not in node.children:
                raise StateError(f"Path {path} does not exist")
            node = node.children[name]
        return node

    def resolve_file(self, path: Path) -> File:
        """Resolve a path to a file in the filesystem."""
        node = self._resolve(path)
        if not isinstance(node, File):
            raise StateError(f"Path {path} is not a file")
        return node

    def resolve_directory(self, path: Path) -> Directory:
        node = self._resolve(path)
        if not isinstance(node, Directory):
            raise StateError(f"Path {path} is not a directory")
        return node

    def create_file(self, path: Path, data: bytearray) -> None:
        """Create a file at the given path with the given data."""
        directory = self.resolve_directory(path.parent)
        if path.name in directory.children:
            raise StateError(f"File {path} already exists")
        directory.children[path.name] = File(data=data)

    def delete_file(self, path: Path) -> None:
        """Delete a file at the given path."""
        directory = self.resolve_directory(path.parent)
        if path.name not in directory.children:
            raise StateError(f"File {path} does not exist")
        del directory.children[path.name]

    def create_directory(self, path: Path) -> None:
        """Create a directory at the given path."""
        directory = self.resolve_directory(path.parent)
        if path.name in directory.children:
            raise StateError(f"Directory {path} already exists")
        directory.children[path.name] = Directory()
