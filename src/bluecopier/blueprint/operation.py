import dataclasses
import json
from pathlib import Path

import commentjson
import tomlkit
import yaml

from bluecopier.utils.jsonutils import merge_json_documents
from bluecopier.utils.tomlutils import merge_toml_documents, parse_toml


@dataclasses.dataclass
class Operation:
    destination: Path

    def execute(self, output_dir: Path) -> None:
        raise NotImplementedError


@dataclasses.dataclass
class CreateDirectoryOp(Operation):
    def execute(self, output_dir: Path) -> None:
        directory = output_dir / self.destination
        directory.mkdir(exist_ok=True)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.destination!r})"


MAX_CONTENT_LENGTH = 50


@dataclasses.dataclass
class WriteFileOp(Operation):
    content: bytes | str
    source: Path | None = None

    def execute(self, output_dir: Path) -> None:
        path = output_dir / self.destination
        content = self.content
        if isinstance(content, str):
            path.write_text(content)
        else:
            path.write_bytes(content)
        source = self.source
        if source:
            path.chmod(source.stat().st_mode)

    def __repr__(self) -> str:
        content = self.content
        if len(content) > MAX_CONTENT_LENGTH:
            content = self.content[:MAX_CONTENT_LENGTH]
        return f"{type(self).__name__}({self.destination!r}, content={content!r})"


PathOperation = dict[Path, Operation]
PathOperations = dict[Path, list[Operation]]


def merge_operations(operations: PathOperations) -> PathOperation:
    d = {}
    for path, item in operations.items():
        # First, reverse the list of operations to get the last blueprint first
        ops = list(item[::-1])
        first_op = ops[0]
        if len(ops) == 1:
            d[path] = first_op
            continue
        elif all(isinstance(op, CreateDirectoryOp) for op in ops) or ops.count(first_op) == len(ops):
            value = first_op
        elif path.suffix == ".toml":
            value = merge_toml_operations(ops)
        elif path.suffix in [".yaml", ".yml"]:
            value = merge_yaml_operations(ops)
        elif path.suffix in [".json"]:
            value = merge_json_operations(ops)
        elif ops.count(first_op) == len(ops):
            value = first_op
        elif path.name == ".gitignore":
            value = merge_gitignore_operations(ops)
        else:
            raise SystemExit(f"Multiple operations for {path}: {ops}")
        d[path] = value

    return d


def merge_toml_operations(ops: list[Operation]) -> WriteFileOp:
    first = ops[0]
    assert isinstance(first, WriteFileOp)
    assert isinstance(first.content, str)
    a = parse_toml(first.content)
    for op in ops[1:]:
        assert isinstance(op, WriteFileOp)
        if isinstance(op.content, str):
            merge_toml_documents(a, b=parse_toml(op.content))
    write_op = WriteFileOp(destination=first.destination, content=tomlkit.dumps(a))
    return write_op


def merge_json_operations(ops: list[Operation]) -> WriteFileOp:
    first = ops[0]
    assert isinstance(first, WriteFileOp)
    a = commentjson.loads(first.content)
    for op in ops[1:]:
        assert isinstance(op, WriteFileOp)
        merge_json_documents(a, b=json.loads(op.content))
    write_op = WriteFileOp(destination=first.destination, content=json.dumps(a, indent=4))
    return write_op


def merge_yaml_operations(ops: list[Operation]) -> WriteFileOp:
    first = ops[0]
    match first:
        case WriteFileOp(content=str(first_content)):
            pass
        case _:
            raise NotImplementedError(first)
    a = yaml.safe_load(first_content)
    for op in ops[1:]:
        match op:
            case WriteFileOp(content=content):
                pass
            case _:
                raise NotImplementedError(op)
        merge_json_documents(a, b=yaml.safe_load(content))
    write_op = WriteFileOp(destination=first.destination, content=yaml.dump(a))
    return write_op


def merge_gitignore_operations(ops: list[Operation]) -> WriteFileOp:
    first = ops[0]
    match first:
        case WriteFileOp(content=str(content)):
            pass
        case _:
            raise NotImplementedError(first)
    lines = content.splitlines()
    lines_set = set(lines)
    for op in ops[1:]:
        match op:
            case WriteFileOp(content=str(content)):
                pass
            case _:
                raise NotImplementedError(op)
        for line in content.splitlines():
            if line not in lines_set:
                lines_set.add(line)
                lines.append(line)

    write_op = WriteFileOp(destination=first.destination, content="\n".join(lines) + "\n")
    return write_op


# def test_merge_yaml_documents():
#     merge_yaml_operations(
#         ops=[WritePathOp(path=Path("a.toml"), content=)],
#
#     merge_toml_documents(
