import dataclasses
import os
import pwd
import shutil
import subprocess
from pathlib import Path
from typing import Any

import appdirs
import tomlkit

from bluecopier.enums import CodeHosting, License


def get_username() -> str:
    git = shutil.which("git")
    assert git is not None
    try:
        username = subprocess.check_output([git, "config", "user.name"], encoding="utf-8")
    except subprocess.CalledProcessError:
        username = None
    else:
        assert username is not None
        username = username.strip()
    if not username:
        username = pwd.getpwuid(os.getuid())[4]
    return username


def get_email() -> str | None:
    git = shutil.which("git")
    assert git is not None
    email: str | None
    try:
        email = subprocess.check_output([git, "config", "user.email"], encoding="utf-8")
    except subprocess.CalledProcessError:
        email = None
    else:
        assert email is not None
        email = email.strip()
    return email


@dataclasses.dataclass
class UserOptions:
    """
    Options specified by the user, either via command line or via a wizard
    """

    features: dict[str, bool]
    blueprint_name: str
    project_name: str
    output_dir: Path
    code_hosting: CodeHosting
    project_description: str
    project_homepage: str
    python_version: str = "3.11"
    editor: str = "vscode"
    license_: License = License.MIT
    author_name: str = dataclasses.field(default_factory=get_username)
    author_email: str | None = dataclasses.field(default_factory=get_email)
    project_private: bool = False
    secrets: dict[str, dict[str, str]] = dataclasses.field(default_factory=dict)
    publish: bool = False
    github_org: str | None = None

    def __post_init__(self) -> None:
        config_dir = appdirs.user_config_dir("bluecopier")

        user_config = Path(config_dir) / "user.config.toml"
        self._load_user_config(user_config)

        secrets = Path(config_dir) / "secrets.toml"
        self._load_secrets(secrets)

    def _load_user_config(self, path: Path) -> None:
        try:
            with path.open("r") as f:
                user_data = tomlkit.parse(f.read())
        except FileNotFoundError:
            pass
        else:
            self.author_name = self._get_author_name(user_data)

    def _load_secrets(self, path: Path) -> None:
        try:
            with path.open("r") as f:
                secrets = tomlkit.parse(f.read())
        except FileNotFoundError:
            pass
        else:
            self.secrets = secrets

    def _get_author_name(self, data: dict[str, Any]) -> str:
        author_name = data.get("author_name")
        if author_name is None:
            author_name = get_username()
        return author_name
