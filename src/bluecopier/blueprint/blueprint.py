import dataclasses
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from bluecopier.blueprint.configuration import BlueprintConfiguration
from bluecopier.blueprint.operation import CreateDirectoryOp, Operation, WriteFileOp
from bluecopier.template_rendering import maybe_render_jinja_template
from bluecopier.utils.fileutils import decode_text_or_bytes

if TYPE_CHECKING:
    from bluecopier.project import Project

BlueprintName = str


def ignore_path(*, path: Path, root: Path, ignore: set[str]) -> bool:
    if path.name in {"blueprint.py", "blueprint.yml"}:
        return True
    if path.stem == root.stem and path.suffix == ".py":
        return True
    topmost_folder_or_name = path.relative_to(root).parts[0]
    if topmost_folder_or_name in ignore:
        return True
    # TODO: use .gitignore?
    if topmost_folder_or_name in {"__pycache__", ".git"}:
        return True
    return False


@dataclasses.dataclass
class Blueprint:
    name: BlueprintName
    root_path: Path
    config: BlueprintConfiguration
    project: "Project"

    @property
    def source_root(self) -> str:
        return self.config.source_root

    def find_paths(self) -> Iterable[Path]:
        paths: list[Path] = []
        directories = set(paths)
        for path in self.root_path.rglob("*"):
            if ignore_path(path=path, root=self.root_path, ignore=self.config.ignore):
                continue
            if path not in directories:
                paths.append(path)
            if not path.is_dir():
                continue
            for subpath in path.parents:
                if subpath == self.root_path:
                    break
                if subpath in directories:
                    continue
                directories.add(subpath)
                paths.append(subpath)
        return sorted(paths)

    def decode_content(self, source_path: Path) -> str | bytes:
        content = decode_text_or_bytes(source_path)
        rendered = None
        if isinstance(content, str):
            rendered = maybe_render_jinja_template(
                source_path=source_path,
                content=content,
                blueprint=self,
            )
        return rendered or content

    def get_operations(self) -> Iterable[Operation]:
        yield from self.generate()
        for source_path in self.find_paths():
            destination = source_path.relative_to(self.root_path)
            if source_path.is_dir():
                yield CreateDirectoryOp(destination=destination)
            else:
                yield WriteFileOp(
                    destination=destination,
                    content=self.decode_content(source_path),
                    source=source_path,
                )

    def generate(self) -> Iterable[Operation]:
        return []
