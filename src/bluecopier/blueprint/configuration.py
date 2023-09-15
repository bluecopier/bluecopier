import dataclasses
import logging
from pathlib import Path
from typing import TYPE_CHECKING, NotRequired, TypedDict, cast

import yaml

if TYPE_CHECKING:
    from bluecopier.blueprint.loader import BlueprintLoader

logger = logging.getLogger(__name__)


class ProvideItem(TypedDict):
    name: str
    target: str


class RequireItem(TypedDict):
    name: str
    optional: NotRequired[bool]


class BlueprintNode(TypedDict):
    name: str
    uses: NotRequired[list[str]]
    source_root: NotRequired[str]
    provides: NotRequired[list[ProvideItem]]
    requires: NotRequired[list[RequireItem] | list[str]]
    entrypoint: NotRequired[str]
    ignore: NotRequired[list[str]]
    deploy: NotRequired[dict[str, str]]


class FeatureNode(TypedDict):
    name: str
    default: bool
    include_if_true: NotRequired[list[str]]
    uses: NotRequired[list[str]]


class RootNode(TypedDict):
    blueprint: BlueprintNode
    features: NotRequired[dict[str, FeatureNode]]


@dataclasses.dataclass
class UserOptions:
    features: dict[str, bool]


@dataclasses.dataclass
class BlueprintConfiguration:
    # TODO: document the above
    loader: "BlueprintLoader"
    uses: list[str] = dataclasses.field(default_factory=list, init=False)
    features: dict[str, FeatureNode] = dataclasses.field(default_factory=dict, init=False)
    excluded_files: list[str] = dataclasses.field(default_factory=list, init=False)
    source_root: str = "src"
    entrypoint: str | None = None
    ignore: set[str] = dataclasses.field(default_factory=set)
    provides: list[ProvideItem] | None = None
    requires: list[RequireItem] | list[str] | None = None

    def load_from_path(self, *, path: Path) -> None:
        self.parse(path)

    def evaluate_root_node(self, root: RootNode) -> None:
        self.evaluate_blueprint_node(root["blueprint"])
        for feature, feature_node in root.get("features", {}).items():
            self.evaluate_feature_node(feature, feature_node)

    def evaluate_blueprint_node(self, blueprint_node: BlueprintNode) -> None:
        for use in blueprint_node.get("uses", []):
            self.load_use(use)
        self.evaluate_uses_node(blueprint_node.get("uses", []))
        source_root = blueprint_node.get("source_root")
        if source_root:
            self.source_root = source_root
        entrypoint = blueprint_node.get("entrypoint")
        if entrypoint:
            self.entrypoint = entrypoint
        ignore = blueprint_node.get("ignore")
        if ignore:
            self.ignore = set(ignore)
        self.provides = blueprint_node.get("provides", [])
        self.requires = blueprint_node.get("requires", cast(list[str], []))

    def evaluate_feature_node(self, feature: str, feature_node: FeatureNode) -> None:
        self.evaluate_uses_node(feature_node.get("uses", []))
        self.features[feature] = feature_node

    def evaluate_uses_node(self, uses: list[str]) -> None:
        for use in uses:
            self.load_use(use)

    def load_use(self, use: str) -> None:
        self.loader.load(name=use, directly_included=False)

    def parse(self, path: Path) -> RootNode:
        with path.open("r") as f:
            root = cast(RootNode, yaml.safe_load(f))
        self.evaluate_root_node(root)
        return root

    def asdict(self) -> dict[str, str]:
        return {
            "source_root": self.source_root,
        }
