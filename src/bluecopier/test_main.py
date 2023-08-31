import dataclasses
import os
import subprocess
import venv
from pathlib import Path

from bluecopier.main import generate as main
from bluecopier.template_rendering import ROOT_DIR


@dataclasses.dataclass
class PackageManager:
    output_dir: Path
    python: Path = dataclasses.field(init=False)

    def init_venv(self) -> None:
        venv_dir = self.output_dir / "venv"
        venv.create(venv_dir, with_pip=True)
        self.python = venv_dir / "bin" / "python"

    def _pip(self, *args: str) -> None:
        subprocess.check_call(
            [str(self.python), "-m", "pip", "--disable-pip-version-check", *list(args)],
        )

    def install_from_pyproject(self) -> None:
        self._pip("install", "-e", ".")

    def install_packages(self, *packages: str) -> None:
        self._pip("install", *packages)


def test_main() -> None:
    output_dir = ROOT_DIR / "output"
    main(output_dir=output_dir, blueprint_name="python-flask", name="my_project")
    os.chdir(output_dir)
