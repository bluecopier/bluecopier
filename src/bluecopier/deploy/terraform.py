import dataclasses
import json
import logging
import subprocess
from pathlib import Path
from typing import TypedDict

logger = logging.getLogger(__name__)


class TerraformVariable(TypedDict):
    description: str
    type: str
    default: str


@dataclasses.dataclass
class Terraform:
    root_path: Path

    def parse_variable_definitions(self) -> dict[str, TerraformVariable]:
        # TODO: Parse HCL which is nicer to write
        variables_path = self.root_path / "variables.tf.json"
        defs: dict[str, TerraformVariable] = {}
        if variables_path.exists():
            with variables_path.open() as f:
                defs = json.load(f)["variable"]
        return defs

    def write_auto_tfvars(self, variables: dict[str, str]) -> None:
        auto_tfvars = self.root_path / "auto.tfvars.json"
        with auto_tfvars.open("w") as f:
            json.dump(variables, f)

    def init(self) -> None:
        logger.info("Initializing terraform")
        result = self.run(
            "terraform",
            "init",
            "-plugin-dir=../tf-plugins/",
            "-backend=false",
            capture_output=True,
        )
        if result.returncode:
            logger.error("Deploy failed: %s", result.stdout.decode("utf-8"))
            raise SystemExit

    def run(self, *args: str, capture_output: bool = False) -> subprocess.CompletedProcess[bytes]:
        cwd = str(self.root_path.absolute())
        return subprocess.run(
            args,
            cwd=cwd,
            capture_output=capture_output,
            check=False,
        )

    def validate(self) -> None:
        logger.info("Validating terraform")
        result = self.run("terraform", "validate", "-json", capture_output=True)
        validation = json.loads(result.stdout.decode("utf-8"))
        if not validation["valid"]:
            logger.error("Validation failed: %s", result.stdout.decode("utf-8"))
            raise SystemExit

    def apply(self, *, auto_approve: bool = False) -> None:
        args = ["terraform", "apply"]
        if auto_approve:
            args.append("-auto-approve")

        logger.info("Deploying")
        result = self.run(*args, capture_output=True)
        if result.returncode:
            logger.error("Deploy failed")
            logger.info(result.stdout.decode("utf-8"))
            raise SystemExit
        else:
            logger.info("Deployed")
            logger.info(result.stdout.decode("utf-8"))
