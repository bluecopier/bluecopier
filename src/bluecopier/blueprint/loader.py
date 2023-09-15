import dataclasses
import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING

from bluecopier.blueprint.blueprint import Blueprint, BlueprintName
from bluecopier.blueprint.configuration import BlueprintConfiguration
from bluecopier.blueprint.errors import BlueprintNotFoundError

if TYPE_CHECKING:
    from bluecopier.project import Project

ROOT_DIR = Path(__file__).parent.parent.parent.parent
BLUEPRINT_DIR = ROOT_DIR / "blueprints"
logger = logging.getLogger("ldr")


def load_module(module_path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, str(module_path))
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    logger.debug("Loaded module %s", module_name)
    return module


def get_blueprint_class_from_module(module: ModuleType) -> type[Blueprint] | None:
    for _key, value in module.__dict__.items():
        if not inspect.isclass(value):
            continue
        if value is Blueprint:
            continue
        if not issubclass(value, Blueprint):
            continue
        logger.debug("Using Blueprint subclass %s.%s", value.__module__, value.__name__)
        return value

    logger.error("No blueprint class found in %s", module)
    return None


@dataclasses.dataclass
class BlueprintLoader:
    directory_path = BLUEPRINT_DIR
    project: "Project"
    blueprints_by_name: dict[BlueprintName, Blueprint] = dataclasses.field(default_factory=dict)

    def load(self, name: BlueprintName, *, directly_included: bool) -> Blueprint:
        blueprint = self.blueprints_by_name.get(name)
        if blueprint is None:
            # TODO: Support for multiple blueprint directories:
            # - ~/.local/share/bluecopier/blueprints
            # - /usr/share/bluecopier/blueprints
            # - etc
            source_path = self.directory_path / name
            try:
                blueprint = self.load_from_path(
                    name=name,
                    source_path=source_path,
                    directly_included=directly_included,
                )
            except FileNotFoundError as exc:
                raise BlueprintNotFoundError(f"Blueprint {name} not found.") from exc
            self.blueprints_by_name[name] = blueprint
        return blueprint

    def load_from_path(self, *, name: str, source_path: Path, directly_included: bool) -> Blueprint:
        if not source_path.exists():
            raise FileNotFoundError(f"Blueprint {name} not found.")

        config = BlueprintConfiguration(loader=self)
        config_path = source_path / "blueprint.yml"
        if config_path.exists():
            config.load_from_path(path=config_path)

        module_name = source_path.name
        module_path = source_path / f"{module_name}.py"
        blueprint_class = None
        if module_path.exists():
            full_module_name = f"blueprints.{module_name}.{module_name}"
            module = load_module(module_path, full_module_name)
            blueprint_class = get_blueprint_class_from_module(module)
        if not blueprint_class:
            blueprint_class = Blueprint
        blueprint = blueprint_class(
            name=BlueprintName(name),
            root_path=source_path,
            config=config,
            project=self.project,
            directly_included=directly_included,
        )
        logger.debug("Loaded blueprint %s", name)
        return blueprint

    # TODO: load_from_github("user/repo")

    def blueprint_names(self) -> set[str]:
        return set(self.blueprints_by_name.keys())
