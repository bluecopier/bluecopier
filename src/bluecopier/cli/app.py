import logging
from typing import Annotated

import typer

app = typer.Typer(pretty_exceptions_enable=False, rich_markup_mode="rich")


@app.callback(invoke_without_command=False)
def bootstrap(
    debug: Annotated[bool, typer.Option("--debug", help="Enable debug logging")] = False,
) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(levelname).1s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
