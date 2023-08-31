# This file is part of the Bluecopier toolset
# .gitignore support https://git-scm.com/docs/gitignore
from collections.abc import Iterable
from pathlib import Path

import requests

from bluecopier.blueprint.blueprint import Blueprint
from bluecopier.blueprint.operation import WriteFileOp

# We're reusing GitHubs collection of .gitignore templates
GITIGNORE_URL = "https://raw.githubusercontent.com/github/gitignore/main/{name}.gitignore"


class GitIgnore(Blueprint):
    name = "gitignore"

    def generate(self) -> Iterable[WriteFileOp]:
        r = requests.get(GITIGNORE_URL.format(name="Python"), timeout=10)
        r.raise_for_status()
        yield WriteFileOp(
            destination=Path(".gitignore"),
            content=r.text,
        )
