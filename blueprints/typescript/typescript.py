from typing import Any

from bluecopier.blueprint.blueprint import Blueprint

# https://github.com/microsoft/TypeScript/wiki/Node-Target-Mapping
NODE_VERSION_TO_TARGET_MAPPING = {
    "20": "es2022",
    "18": "es2021",
    "16": "es2020",
    "14": "es2020",
    "12": "es2019",
}


class TypescriptBlueprint(Blueprint):
    def context(self) -> dict[str, Any]:
        runtime = self.project.get_runtime()
        return {
            "node_target": NODE_VERSION_TO_TARGET_MAPPING[runtime.version],
        }
