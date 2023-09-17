# This file is part of the Bluecopier toolset
import base64
import json
import logging
import zipfile
from functools import cached_property

import docker
import boto3

from bluecopier.blueprint.blueprint import Blueprint

logger = logging.getLogger('lbd')

VENDOR_PATH = "vendor"

AWS = {
    'profile': 'nilhad',
    'region': 'eu-north-1',
    'account_id': '698438934321'
}

class AwsLambdaUrlDockerBlueprint(Blueprint):
    name = "aws-lambda-url-docker"

    @cached_property
    def session(self) -> boto3.Session:
        # TODO: configure aws profile
        return boto3.session.Session(profile_name=AWS['profile'])

    def docker(self, *args):
        self.project.run("docker", *args, env={"DOCKER_CLI_HINTS": "false"})

    def get_docker_registry(self) -> str:
        account_id = AWS['account_id']
        region = AWS['region']
        repo = f'{account_id}.dkr.ecr.{region}.amazonaws.com'
        return repo

    def get_docker_repo(self) -> str:
        return self.project.name

    def get_git_tag(self) -> str:
        result = self.project.run("git", 'rev-parse', '--short', 'HEAD', capture_output=True)
        return result.stdout.decode().strip()

    @property
    def docker_tag_names(self) -> list[str]:
        registry = self.get_docker_registry()
        repo = self.get_docker_repo()
        version = self.get_git_tag()
        return [f"{registry}/{repo}:{version}", f"{registry}/{repo}:latest"]

    def build(self) -> None:
        if self.feature_enabled("docker"):
            first_tag = self.docker_tag_names[0]
            logger.info('Building docker image: %s', first_tag)
            self.docker("build", "-t", first_tag, ".")

            logger.info('Tagging docker images')
            for tag_name in self.docker_tag_names[1:]:
                self.docker("tag", first_tag, tag_name)
        elif self.feature_enabled("zip"):
            # TODO: there might be value in moving this to terraform, to avoid depending on
            #       bluecopier when doing builds
            source_path = self.project.output_path / "src"
            build_path = self.project.output_path / "build"
            build_path.mkdir(exist_ok=True, parents=True)
            vendor_path = str((build_path / VENDOR_PATH).relative_to(self.project.output_path))
            logger.info('Installing vendor dependencies')
            self.project.run("pip", "install", "-t", vendor_path, "-e.",  "--upgrade", "-q")

            logger.info('Building lambda zip package')
            zip_package = self.project.output_path / "build" / "package.zip"
            with zipfile.ZipFile(zip_package, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for entry in source_path.rglob("*"):
                    if entry.suffix == '.pyc' or entry.name == '__pycache__':
                        continue
                    zip_file.write(entry, entry.relative_to(source_path))
                for entry in build_path.rglob("*"):
                    if entry.name == "package.zip":
                        continue
                    zip_file.write(entry, entry.relative_to(build_path))

    def deploy(self) -> None:
        if self.feature_enabled("docker"):
            ecr = self.session.client("ecr")
            # https://boto3.amazonaws.com/v1/documentation/api/1.28.1/reference/services/ecr/client/get_authorization_token.html
            token = ecr.get_authorization_token()

            logger.debug(token)
            authorization_data = token["authorizationData"][0]
            username, password = base64.b64decode(authorization_data["authorizationToken"]).decode().split(":", 1)
            registry_uri = authorization_data["proxyEndpoint"]
            docker_client = docker.from_env()

            logger.info("Docker logging in to %s", registry_uri)
            response = docker_client.login(
                username,
                password=password,
                registry=registry_uri,
                reauth=True)
            if response['Status'] != 'Login Succeeded':
                raise SystemExit(response)
            expires_at = authorization_data["expiresAt"]
            logger.info('Docker login response: %s, expires at %s', response, expires_at)

            repo = self.get_docker_repo()
            try:
                ecr.describe_repositories(repositoryNames=[repo])
            except ecr.exceptions.RepositoryNotFoundException:
                logger.info('Creating ECR repository')
                try:
                    ecr.create_repository(repositoryName=repo)
                except ecr.exceptions.RepositoryAlreadyExistsException:
                    logger.warning('Repository already exists')
                except ecr.exceptions.ClientError as e:
                    raise SystemExit(e)

            registry = self.get_docker_registry()
            version = self.get_git_tag()
            repository = f'{registry}/{repo}'
            for tag in [version, 'latest']:
                logger.info(f'Pushing to {repository}:{tag}')
                for line in docker_client.push(repository=repository, tag=tag,
                                               auth_config={'username': username, 'password': password}).splitlines():
                    line_payload = json.loads(line)
                    status = line_payload.get('status')
                    error = line_payload.get('error')
                    if error:
                        raise Exception(f'Push failed: {error}')

