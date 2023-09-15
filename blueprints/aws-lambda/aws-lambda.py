# This file is part of the Bluecopier toolset
import logging
import zipfile

from bluecopier.blueprint.blueprint import Blueprint

logger = logging.getLogger(__name__)

VENDOR_PATH = "vendor"


class AwsLambdaUrlDockerBlueprint(Blueprint):
    name = "aws-lambda-url-docker"

    def docker(self, *args):
        self.project.run("docker", *args, env={"DOCKER_CLI_HINTS": "false"})

    def build(self) -> None:
        if self.feature_enabled("docker"):
            image_name = self.project.name
            version = self.project.user_options.python_version
            primary_tag_name = f"{image_name}:{version}"
            self.docker("build", "-t", primary_tag_name, ".")
            for tag_name in ["latest"]:
                self.docker("tag", primary_tag_name, tag_name)
        elif self.feature_enabled("zip"):
            # TODO: there might be value in moving this to terraform, to avoid depending on
            #       bluecopier when doing builds
            source_path = self.project.output_path / "src"
            build_path = self.project.output_path / "build"
            build_path.mkdir(exist_ok=True, parents=True)
            vendor_path = str((build_path / VENDOR_PATH).relative_to(self.project.output_path))
            logger.info('Installing vendor dependencies')
            self.project.run("pip", "install", "-t", vendor_path, "-e.",  "--upgrade", "-q")
            self.project.run("pip", "install", "-t", vendor_path, "apig-wsgi", "--upgrade", "-q")

            logger.info('Building lambda zip package')
            zip_package = self.project.output_path / "build" / "package.zip"
            with zipfile.ZipFile(zip_package, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for entry in source_path.rglob("*.py"):
                    zip_file.write(entry, entry.relative_to(source_path))
                for entry in build_path.rglob("*"):
                    if entry.name == "package.zip":
                        continue
                    zip_file.write(entry, entry.relative_to(build_path))

    def deploy(self) -> None:
        if self.feature_enabled("docker"):
            import boto3
            ecr = boto3.client("ecr", profile="nilhad")
            token = ecr.get_authorization_token()
            authorization_data = token["authorizationData"][0]
            username, password = authorization_data["authorizationToken"].split(":")
            registry = authorization_data["proxyEndpoint"]
            self.docker("login", "-u", username, "-p", password, registry)

            if ecr.describe_repositories(repositoryNames=[self.project.name])["repositories"]:
                print("Repository already exists")
            self.docker("push")
        #     docker push $(ECR)/$(AWS_ECR_REPO):$(TAG)
        # self.add_variable("aws_ecr_repo", self.project.name)
        # self.add_variable("aws_ecr_registry", registry)
        # self.add_variable("aws_ecr_username", username)

