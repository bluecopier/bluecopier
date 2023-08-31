import collections
import dataclasses
import logging
import shutil
import subprocess
from collections.abc import Iterable
from pathlib import Path

import yaml

from bluecopier.blueprint.blueprint import Blueprint, BlueprintName
from bluecopier.blueprint.loader import BlueprintLoader
from bluecopier.blueprint.operation import merge_operations
from bluecopier.user_options import UserOptions
from bluecopier.vcs.githubvcs import VCS

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Project:
    user_options: UserOptions

    loader: BlueprintLoader = dataclasses.field(init=False)

    master_blueprint: Blueprint = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.loader = BlueprintLoader(project=self)
        blueprint_name = self.user_options.blueprint_name
        self.master_blueprint = self.loader.load(name=blueprint_name)

    @property
    def name(self) -> str:
        return self.user_options.project_name

    @property
    def output_path(self) -> Path:
        return self.user_options.output_dir

    def blueprint_loaded(self, name: str) -> bool:
        return name in self.loader.blueprints_by_name

    @property
    def entrypoint(self) -> str | None:
        return self.master_blueprint.config.entrypoint

    @property
    def vcs(self) -> str | None:
        if self.user_options.code_hosting in ["github", "gitlab"]:
            return "git"
        return None

    @property
    def blueprints(self) -> Iterable[Blueprint]:
        return list(self.loader.blueprints_by_name.values())

    def run(self, *args: str, capture_output: bool = False) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            args,
            cwd=str(self.output_path),
            capture_output=capture_output,
            check=False,
        )

    def write_state(self) -> None:
        bluecopier_dir = self.output_path / ".bluecopier"
        bluecopier_dir.mkdir(exist_ok=True)
        with (bluecopier_dir / "state.yml").open("w") as f:
            yaml.dump(
                {
                    "blueprints": {
                        "master": self.master_blueprint.name,
                        "includes": [
                            {"name": b.name} for b in self.blueprints if b.name != self.master_blueprint.name
                        ],
                    },
                },
                f,
            )

    def generate(self) -> None:
        operations = collections.defaultdict(list)
        for blueprint in self.blueprints:
            for op in blueprint.get_operations():
                operations[op.destination].append(op)
        merged_operations = merge_operations(operations)

        # TODO: support update/incremental without deleting existing directory
        destination_dir = self.output_path
        shutil.rmtree(destination_dir, ignore_errors=True)
        destination_dir.mkdir(exist_ok=True)
        for _path, exop in merged_operations.items():
            exop.execute(destination_dir)

    def load_blueprint(self, blueprint: BlueprintName) -> None:
        self.loader.load(name=blueprint)

    def get_vcs(self) -> VCS:
        logger.info("Loading GitHub VCS")
        from bluecopier.vcs.githubvcs import GitHubVCS

        return GitHubVCS(project=self)

    def install_dependencies(self) -> None:
        logger.info("Installing and pinning dependencies")
        # TODO: configure package manager in blueprint
        #       this should be PackageManager().install_dev_dependencies()
        if self.master_blueprint.name == "typescript":
            self.run("npm", "install")
        elif self.master_blueprint.name == "python":
            # TODO: cache venvs to speed up subsequent runs
            self.run("python", "-mvenv", "venv", "--upgrade-deps")
            self.run("venv/bin/pip", "install", "-e", ".[dev]", "-q")
            output = self.run("venv/bin/pip", "freeze", capture_output=True)
            deps = {}
            for line in output.stdout.decode("utf-8").splitlines():
                if line.startswith(("#", "-")):
                    continue
                pkg, version = line.split("==")
                deps[pkg] = version

    def run_formatters(self) -> None:
        content = self.output_path / ".pre-commit-config.yaml"
        with content.open("rb") as stream:
            repos = yaml.safe_load(stream)
        if repos:
            hooks = []
            for repo in repos["repos"]:
                for hook in repo["hooks"]:
                    hooks.append(hook["id"])
            logger.info(f'Running pre-commit hooks: {", ".join(sorted(hooks))}')
            output = self.run("pre-commit", "run", "--all-files", capture_output=True)
            if output.returncode != 0:
                logger.warning("pre-commit failed, check out logs")
                logger.info(output.stderr.decode("utf-8"))
                logger.info(output.stdout.decode("utf-8"))
