import collections
import dataclasses
import os
import pwd
import shutil
import subprocess
from pathlib import Path
from typing import Any, Self

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


BlueprintName = str
FeatureName = str
FeatureValue = str | bool | None

Features = dict[BlueprintName, dict[FeatureName, FeatureValue]]


@dataclasses.dataclass
class UserOptions:
    """
    Options specified by the user, either via command line or via a wizard
    """

    # Raw unparsed key=value options
    raw_features: list[str] | None = dataclasses.field()
    blueprint_names: list[str]
    project_name: str
    output_dir: Path
    code_hosting: CodeHosting
    project_description: str
    project_homepage: str
    project_version: str = "0.1.0"
    python_version: str = "3.11"
    editor: str = "vscode"
    license_: License = License.MIT
    features: Features = dataclasses.field(default_factory=dict, init=False)
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

        self.features = self._parse_raw_features()

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
            self.secrets = secrets.unwrap()

    def _get_author_name(self, data: dict[str, Any]) -> str:
        author_name = data.get("author_name")
        if author_name is None:
            author_name = get_username()
        return author_name

    def asdict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, param: dict[str, Any]) -> Self:
        return cls(**param)

    def _parse_raw_features(self) -> Features:
        features: Features = collections.defaultdict(dict)
        if self.raw_features is not None:
            value: FeatureValue
            for feature in self.raw_features:
                if "=" in feature:
                    name, value = feature.split("=", 1)
                else:
                    name, value = feature, True
                if value == "true":
                    value = True
                elif value == "false":
                    value = False
                elif value == "null":
                    value = None
                blueprint, feature_name = name.split(".")
                features[blueprint][feature_name] = value
        return dict(features)
