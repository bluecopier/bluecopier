#!/usr/bin/env python
import logging
from pathlib import Path
from typing import Annotated

import typer

from bluecopier.enums import CodeHosting, License
from bluecopier.project import Project
from bluecopier.user_options import UserOptions

app = typer.Typer(pretty_exceptions_enable=False, rich_markup_mode="rich")
logger = logging.getLogger(__name__)


@app.command()
def test() -> None:
    pass


@app.command()
def deploy() -> None:
    pass


@app.command()
def generate(
    output_dir: Annotated[Path, typer.Argument(file_okay=False)],
    blueprint_name: Annotated[str, typer.Option("-b", metavar="BLUEPRINT", help="Blueprint name")],
    edit: Annotated[bool, typer.Option("-e", "--editor", help="Launch in editor after generating")]
    | None = None,
    # Project
    description: Annotated[
        str,
        typer.Option(metavar="URL", help="Project description", rich_help_panel="Project"),
    ] = "",
    homepage: Annotated[
        str,
        typer.Option(metavar="URL", help="Project homepage", rich_help_panel="Project"),
    ] = "",
    license: Annotated[  # noqa: A002
        License,
        typer.Option(help="License for new project", rich_help_panel="Project"),
    ] = License.MIT,
    name: Annotated[str, typer.Option(metavar="NAME", help="Project name", rich_help_panel="Project")]
    | None = None,
    public: Annotated[
        bool,
        typer.Option(
            "--public/--private",
            help="If the published repo should be public",
            rich_help_panel="Project",
        ),
    ] = True,
    # Code Hosting
    code_hosting: Annotated[
        CodeHosting,
        typer.Option(help="Code hosting provider", rich_help_panel="Code Hosting"),
    ] = CodeHosting.GITHUB,
    publish: Annotated[
        bool,
        typer.Option(
            "--publish/--no-publish",
            help="Publish to code hosting provider after generating",
            rich_help_panel="Code Hosting",
            prompt="Publish to code hosting provider after generating?",
        ),
    ]
    | None = None,
    github_org: Annotated[
        str,
        typer.Option(help="GitHub organization", rich_help_panel="Code Hosting"),
    ]
    | None = None,
) -> None:
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    if name is None:
        name = output_dir.name
    user_options = UserOptions(
        blueprint_name=blueprint_name,
        code_hosting=code_hosting,
        features={},
        license_=license,
        output_dir=output_dir,
        project_homepage=homepage,
        project_name=name,
        publish=bool(publish),
        project_private=not public,
        project_description=description,
        github_org=github_org,
    )
    project = Project(user_options=user_options)
    if user_options.editor == "vscode":
        project.load_blueprint("devcontainer")

    vcs = project.get_vcs()
    vcs.load_blueprints()

    project.generate()

    # Post generation
    #################

    # TODO: requires venv to be activated
    # Run formatter
    # if project.blueprint_loaded('black'):

    project.write_state()

    project.install_dependencies()

    vcs.init()

    project.run_formatters()

    if user_options.publish:
        vcs.publish()

    # Open in editor
    if edit:
        args = ["/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code", "."]
        entrypoint = project.entrypoint
        if entrypoint:
            args += ["-g", f"{entrypoint}:1:1"]
        project.run(*args)
