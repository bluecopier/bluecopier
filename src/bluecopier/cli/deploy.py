import logging
import secrets
from pathlib import Path
from typing import Annotated

import typer

from bluecopier.cli.app import app
from bluecopier.deploy.terraform import Terraform
from bluecopier.project import Project

logger = logging.getLogger("dpl")


@app.command()
def deploy(
    project_path: Annotated[Path, typer.Argument(file_okay=False)],
) -> None:
    # TODO: Where do we decide if it should be using zip or docker?

    # TODO: Design ECS+docker+gunicorn
    # TODO: Design local development environment with docker-compose
    # TODO: Will be much more interesting with an RDS database

    # 1. Generate Pulumi/TF Deployment Code/YML/JSON based on input
    project = Project.from_path(project_path.absolute())

    # TODO: Should this be a separate build step?
    # 2. Install vendor dependencies (e.g. Flask and requests) and build zip file/docker image
    project.build()
    project.deploy()
    terraform = Terraform(root_path=project.output_path)
    project_context = {
        "project_name": project.name,
        "function_name": project.name + "-" + secrets.token_urlsafe(6).lower(),
        "region_name": "eu-north-1",
        "source_root": str(project.output_path),
    }
    variables = {}
    for name in terraform.parse_variable_definitions():
        if name in project_context:
            variables[name] = project_context[name]

    if variables:
        terraform.write_auto_tfvars(variables)
    terraform.init()
    terraform.validate()

    terraform.apply(auto_approve=True)
