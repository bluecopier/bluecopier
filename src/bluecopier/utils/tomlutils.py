import tomlkit
from tomlkit import TOMLDocument, document, table
from tomlkit.container import Container
from tomlkit.items import Table

from bluecopier.utils.jsonutils import JSONObject


def parse_toml(content: str) -> TOMLDocument:
    return tomlkit.parse(content)


TOMLThing = TOMLDocument | Table | Container
ContainerTable = Container, Table


def merge_toml_documents(a: TOMLThing, b: TOMLThing) -> None:
    for key, b_value in b.items():
        if isinstance(a, ContainerTable) and key in a:
            a_value = a.get(key)
            if isinstance(a_value, ContainerTable) and isinstance(b_value, ContainerTable):
                merge_toml_documents(a_value, b_value)
            elif isinstance(a_value, list) and isinstance(b_value, list):
                a_value = a_value + b_value
            a[key] = a_value
        else:
            a.add(key, b_value)


def test_merge_toml_documents() -> None:
    a = tomlkit.parse("[a.b]\nc = 1")
    merge_toml_documents(
        a=a,
        b=tomlkit.parse("[c.d]\nd = 2"),
    )
    assert tomlkit.dumps(a) == """[a.b]\nc = 1\n[c.d]\nd = 2"""

    merge_toml_documents(
        a=tomlkit.parse("[a.b]\ndeps = [1]"),
        b=tomlkit.parse("[a.b]\ndeps = [2]"),
    )
    assert tomlkit.dumps(a) == """[a.b]\ndeps = [1, 2]"""


def json_as_toml(data: JSONObject) -> TOMLDocument:
    doc = document()
    if isinstance(data, dict):
        for name, attrs in data.items():
            t = table()
            if isinstance(attrs, dict):
                for key, value in attrs.items():
                    t.add(key, value)
                doc.add(name, t)
    else:
        raise NotImplementedError(type(data))
    return doc
