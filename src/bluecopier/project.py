import collections
import dataclasses
import logging
import os
import shutil
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast

import tomlkit
import yaml

from bluecopier.blueprint.blueprint import Blueprint, BlueprintName
from bluecopier.blueprint.configuration import RequireItem
from bluecopier.blueprint.loader import BlueprintLoader
from bluecopier.blueprint.operation import merge_operations
from bluecopier.user_options import UserOptions
from bluecopier.vcs.githubvcs import VCS

logger = logging.getLogger("prj")


@dataclasses.dataclass
class Project:
    user_options: UserOptions

    loader: BlueprintLoader = dataclasses.field(init=False)

    extra_context: dict[str, Any] = dataclasses.field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self.loader = BlueprintLoader(project=self)

    def load_blueprint(self, name: BlueprintName, *, directly_included: bool) -> Blueprint:
        return self.loader.load(name=name, directly_included=directly_included)

    @property
    def name(self) -> str:
        return self.user_options.project_name

    @property
    def output_path(self) -> Path:
        return self.user_options.output_dir

    def blueprint_loaded(self, name: str) -> bool:
        return name in self.loader.blueprints_by_name

    # @property
    # def entrypoint(self) -> str | None:

    @property
    def vcs(self) -> str | None:
        if self.user_options.code_hosting in ["github", "gitlab"]:
            return "git"
        return None

    @property
    def blueprints(self) -> Iterable[Blueprint]:
        return list(self.loader.blueprints_by_name.values())

    def run(
        self,
        *args: str,
        capture_output: bool = False,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        if env is None:
            env = {}
        cwd = str(self.output_path.absolute())
        return subprocess.run(
            args,
            cwd=cwd,
            capture_output=capture_output,
            check=False,
            env=os.environ | env,
        )

    def get_template_context(self) -> dict[str, Any]:
        user_options = self.user_options
        context = {
            "author_name": user_options.author_name,
            "author_email": user_options.author_email,
            "license": user_options.license_,
            "project": self,
            "python_version": user_options.python_version,
        } | self.extra_context
        return context

    @classmethod
    def from_path(cls, project_path: Path) -> "Project":
        logger.info("Loading project state")
        state_path = project_path / ".bluecopier" / "state.yml"
        with state_path.open("rt") as f:
            state = yaml.load(f, Loader=yaml.Loader)  # noqa: S506
        user_options = state.pop("user_options")
        self = cls(user_options=UserOptions.from_dict(user_options), **state)
        for name in self.user_options.blueprint_names:
            self.load_blueprint(name=name, directly_included=True)
        return self

    def asdict(self) -> dict[str, Any]:
        user_options = self.user_options.asdict()
        del user_options["features"]
        del user_options["secrets"]
        return {"user_options": user_options}

    def write_state(self) -> None:
        bluecopier_path = self.output_path / ".bluecopier"
        bluecopier_path.mkdir(exist_ok=True)
        with (bluecopier_path / "state.yml").open("w") as f:
            yaml.dump(self.asdict(), f)

    def generate(self, *, clear: bool = False) -> None:
        operations = collections.defaultdict(list)
        for blueprint in self.blueprints:
            for op in blueprint.get_operations():
                operations[op.destination].append(op)
        merged_operations = merge_operations(operations)

        # TODO: support update/incremental without deleting existing directory
        destination_dir = self.output_path
        if clear:
            shutil.rmtree(destination_dir, ignore_errors=True)
        destination_dir.mkdir(exist_ok=True)
        for _path, exop in merged_operations.items():
            exop.execute(destination_dir)

    def get_vcs(self) -> VCS:
        logger.info("Loading GitHub VCS")
        from bluecopier.vcs.githubvcs import GitHubVCS

        return GitHubVCS(project=self)

    def install_dependencies(self) -> None:
        logger.info("Installing and pinning dependencies")
        for blueprint in self.loader.blueprints_by_name.values():
            if not blueprint.directly_included:
                continue
            # TODO: configure package manager in blueprint
            #       this should be PackageManager().install_dev_dependencies()
            if blueprint.name == "typescript":
                self.run("npm", "install")
            elif blueprint.name == "python":
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

    def _set_pre_commit_mypy_additional_dependencies(self) -> list[dict[str, Any]]:
        pyproject_path = self.output_path / "pyproject.toml"
        with pyproject_path.open() as f:
            pyproject = tomlkit.parse(f.read())

        content = self.output_path / ".pre-commit-config.yaml"
        with content.open("rb") as stream:
            repos = yaml.safe_load(stream)
            # This is all a big fat hack, but need to fix two things before it can be removed
            # 1. pre-commit-config.yaml needs to be able to reference dependencies loaded from pyproject.toml
            # 2. Needs to be able to have a better understanding of the contents of pyproject.toml
            #    a) fetching all dependencies
            #    b) pinning dependencies like npm does
            for repo in repos["repos"]:
                if repo["repo"] != "https://github.com/pre-commit/mirrors-mypy":
                    continue
                for hook in repo["hooks"]:
                    if hook["id"] != "mypy":
                        continue
                    optional_dependencies = pyproject.get("project", {}).get("optional-dependencies")
                    if not optional_dependencies:
                        continue
                    hook["additional_dependencies"] = [str(s) for s in optional_dependencies["types"].value]

        with content.open("wt") as stream:
            yaml.dump(repos, stream)

        return cast(list[dict[str, Any]], repos["repos"])

    def run_formatters(self) -> None:
        repos = self._set_pre_commit_mypy_additional_dependencies()
        if not repos:
            return

        # Note: perhaps avoid using pre-commit here and ask each formatter
        #       to run, but then we need to understand the dependencies better
        hooks = []
        for repo in repos:
            for hook in repo["hooks"]:
                hooks.append(hook["id"])
        logger.info(f'Running pre-commit hooks: {", ".join(sorted(hooks))}')
        output = self.run(
            "pre-commit",
            "run",
            "-c",
            ".pre-commit-config.yaml",
            capture_output=True,
        )
        if output.returncode != 0:
            logger.warning("pre-commit failed, check out logs")
            logger.info(output.stderr.decode("utf-8"))
            logger.info(output.stdout.decode("utf-8"))

    def parse_providers(self, direct: list[Blueprint]) -> dict[str, list[str | bool]]:
        providers: dict[str, list[str | bool]] = collections.defaultdict(list)
        for blueprint in direct:
            if blueprint.config.provides is None:
                continue
            for provide in blueprint.config.provides:
                match provide:
                    case str(provide):
                        providers[provide].append(True)
                    case dict():
                        for key, value in provide.items():
                            providers[key].append(cast(str, value))
                    case _:
                        raise NotImplementedError(provide)

        return providers

    def validate_require(
        self,
        require_blueprint: Blueprint,
        providers: dict[str, list[str | bool]],
        require: RequireItem | str,
    ) -> None:
        match require:
            case {"name": str(name), "optional": optional}:
                pass
            case str(name):
                optional = False
            case _:
                raise NotImplementedError

        values = providers.get(name, [])
        if not values:
            if not optional:
                raise Exception(f"Missing provider for {name}")
        elif len(values) == 1:
            require_blueprint.link(name, values[0])
        else:
            raise NotImplementedError(f"Multiple providers for {name}")

    def resolve_links(self) -> None:
        direct = []
        for b in self.loader.blueprints_by_name.values():
            if b.directly_included:
                direct.append(b)
        providers = self.parse_providers(direct)

        for require_blueprint in direct[:]:
            if require_blueprint.config.requires is None:
                continue
            for require in require_blueprint.config.requires:
                self.validate_require(require_blueprint, providers, require)

    def build(self) -> None:
        logger.info("Building project")
        for blueprint in self.blueprints:
            blueprint.build()

    def deploy(self) -> None:
        logger.info("Deploying blueprints")
        for blueprint in self.blueprints:
            blueprint.deploy()
