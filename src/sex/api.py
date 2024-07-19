"""ShadeFS HTTP API client."""

from pathlib import Path

import click
import requests


class ApiAddrType(click.ParamType):
    """Click ShadeFS API address type."""

    name = "api_url"

    def convert(self, value, param, ctx):
        try:
            return Api(value)
        except Exception:
            self.fail(
                f"{value!r} is not a valid API URL. Please use the format host:port/drive",
                param,
                ctx,
            )


class Api:
    """ShadeFS HTTP API client."""

    def __init__(self, addr: str):
        """
        Initialize a new API client.

        :param addr: The address of the API server, in the format `host:port/drive`.
        """
        addr, self.drive = addr.split("/")
        host, port = addr.split(":")
        self.url = f"http://{host}:{port}"

    def listdir(self, path: Path) -> list[dict]:
        res = requests.get(
            self.url + "/admin/fs/listdir",
            timeout=5,
            params={
                "path": str(path),
                "drive": self.drive,
            },
        )
        res.raise_for_status()
        return res.json()

    def getattr(self, path: Path) -> dict:
        res = requests.get(
            self.url + "/admin/fs/attr",
            timeout=5,
            params={
                "path": str(path),
                "drive": self.drive,
            },
        )
        res.raise_for_status()
        return res.json()

    def download(self, path: Path) -> bytes:
        res = requests.get(
            self.url + "/admin/fs/download",
            timeout=5,
            params={
                "path": str(path),
                "drive": self.drive,
            },
        )
        res.raise_for_status()
        return res.content

    def mkdir(self, path: Path) -> None:
        res = requests.post(
            self.url + "/admin/fs/mkdir",
            timeout=5,
            params={"path": str(path), "drive": self.drive, "email": "sex@shade.inc"},
        )
        res.raise_for_status()

    def copyfile(self, src: Path, dst: Path) -> None:
        res = requests.post(
            self.url + "/admin/fs/copyfile",
            timeout=5,
            params={
                "src": str(src),
                "dst": str(dst),
                "drive": self.drive,
                "email": "sex@shade.inc",
            },
        )
        res.raise_for_status()

    def delete(self, path: Path) -> None:
        res = requests.post(
            self.url + "/admin/fs/delete",
            timeout=5,
            params={"path": str(path), "drive": self.drive, "email": "sex@shade.inc"},
        )
        res.raise_for_status()

    def move(self, src: Path, dst: Path) -> None:
        res = requests.post(
            self.url + "/admin/fs/move",
            timeout=5,
            params={
                "src": str(src),
                "dst": str(dst),
                "drive": self.drive,
                "email": "sex@shade.inc",
            },
        )
        res.raise_for_status()

    def __str__(self):
        return f"{self.url}/{self.drive}"
