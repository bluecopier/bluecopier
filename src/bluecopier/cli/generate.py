from pathlib import Path
from typing import Annotated

import typer

from bluecopier.cli.app import app
from bluecopier.enums import CodeHosting, License
from bluecopier.project import Project
from bluecopier.user_options import UserOptions


@app.command()
def generate(
    output_dir: Annotated[Path, typer.Argument(file_okay=False)],
    blueprint_names: Annotated[list[str], typer.Option("-b", metavar="BLUEPRINT", help="Blueprint name")],
    features: Annotated[
        list[str],
        typer.Option("-f", metavar="FEATURE", help="Feature name", default_factory=list),
    ],
    # | None = None,
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
    hooks: Annotated[
        bool,
        typer.Option(
            "--hooks/--no-hooks",
            help="If pre-commit hooks should run",
            rich_help_panel="Project",
        ),
    ] = True,
    version: Annotated[
        str,
        typer.Option(help="Project version", rich_help_panel="Project"),
    ] = "0.1.0",
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
    # Build
    build: Annotated[
        bool,
        typer.Option("--build/--no-build", help="Build after generating", rich_help_panel="Build"),
    ] = False,
) -> None:
    if name is None:
        name = output_dir.name
    user_options = UserOptions(
        blueprint_names=blueprint_names,
        code_hosting=code_hosting,
        raw_features=features,
        license_=license,
        output_dir=output_dir,
        project_homepage=homepage,
        project_name=name,
        publish=bool(publish),
        project_private=not public,
        project_description=description,
        project_version=version,
        github_org=github_org,
    )
    project = Project(user_options=user_options)
    for blueprint_name in user_options.blueprint_names:
        project.load_blueprint(blueprint_name, directly_included=True)
    if user_options.editor == "vscode":
        project.load_blueprint("devcontainer", directly_included=False)

    vcs = project.get_vcs()
    vcs.load_blueprints()

    project.resolve_links()

    project.generate()

    # TODO: requires venv to be activated
    # Run formatter
    # if project.blueprint_loaded('black'):

    project.write_state()

    project.install_dependencies()

    vcs.init()

    if hooks:
        project.run_formatters()

    if build:
        project.build()

    if user_options.publish:
        vcs.publish()

    # Open in editor
    # if edit:
    #     if entrypoint:
