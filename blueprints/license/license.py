# This file is part of the Bluecopier toolset
# license support, https://spdx.org/licenses/
import datetime
import shutil
import subprocess
from collections.abc import Iterable
from pathlib import Path

import requests

from bluecopier.blueprint.blueprint import Blueprint
from bluecopier.blueprint.operation import WriteFileOp
from bluecopier.enums import License

SPDX_LICENSE_URL = "https://spdx.org/licenses/{license}.json"


class LicenseBlueprint(Blueprint):
    name = "license"

    def _generate_license(self, *, author_name: str, license_: License) -> str:
        r = requests.get(SPDX_LICENSE_URL.format(license=license_.value), timeout=10)
        r.raise_for_status()
        text = r.json()["licenseText"]
        text = text.replace("<year>", str(datetime.datetime.now(tz=datetime.UTC).year))
        text = text.replace("<copyright holders>", author_name)
        # TODO: rewrite fold in Python, textwrap() is weird
        fold = shutil.which("fold")
        assert fold is not None
        text = subprocess.check_output([fold, "-s"], input=text, encoding="utf-8")
        return text

    def generate(self) -> Iterable[WriteFileOp]:
        # 1. global project singleton
        # 2. loader -> configuration -> blueprint needs to know its project
        # 3. Another option?
        user_options = self.project.user_options
        license_ = user_options.license_
        author_name = user_options.author_name
        content = self._generate_license(license_=license_, author_name=author_name)
        yield WriteFileOp(Path("LICENSE"), content)
