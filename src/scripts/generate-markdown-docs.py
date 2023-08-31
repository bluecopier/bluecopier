from pathlib import Path

import mkdocs_gen_files

src_root = Path(__file__).parent.parent / "bluecopier"
for path in sorted(src_root.glob("**/*.py")):
    doc_path = path.relative_to(src_root).with_suffix(".md")
    if doc_path.stem == "__init__":
        continue
    with mkdocs_gen_files.open(doc_path, "w") as f:
        ident = "bluecopier." + ".".join(doc_path.with_suffix("").parts)
        print("::: " + ident, file=f)
