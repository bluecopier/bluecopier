import dataclasses
import http
import logging
from functools import cached_property
from typing import TYPE_CHECKING

from github import Auth, Github, GithubException
from github.AuthenticatedUser import AuthenticatedUser
from github.Organization import Organization

if TYPE_CHECKING:
    from bluecopier.project import Project

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class VCS:
    project: "Project"

    def load_blueprints(self) -> None:
        raise NotImplementedError

    def init(self) -> None:
        raise NotImplementedError

    def publish(self) -> None:
        raise NotImplementedError


@dataclasses.dataclass
class GitVCS(VCS):
    project: "Project"

    def load_blueprints(self) -> None:
        self.project.load_blueprint("gitignore", directly_included=False)

    def publish(self) -> None:
        raise NotImplementedError


@dataclasses.dataclass
class GitHubVCS(GitVCS):
    def load_blueprints(self) -> None:
        super().load_blueprints()
        self.project.load_blueprint("github", directly_included=False)

    def git(self, *args: str) -> None:
        self.project.run("git", *args)

    def init(self) -> None:
        root_path = self.project.output_path
        git_path = root_path / ".git"
        if not git_path.exists():
            logger.info("Creating Git repository")
            self.git("init", "-q")
        self.git("add", ".")
        self.git("commit", "-q", "-am", "Initial commit")
        self.git("branch", "-M", "main")
        logger.info("Committed and configured remotes.")

    def _get_token(self) -> str:
        opt = self.project.user_options
        return opt.secrets["github"]["token"]

    @cached_property
    def github(self) -> Github:
        token = self._get_token()
        auth = Auth.Token(token)
        g = Github(auth=auth)
        return g

    def get_owner(self) -> AuthenticatedUser | Organization:
        """Get the owner of the repository.

        :return: The owner of the repository
        :rtype: AuthenticatedUser | Organization
        """
        owner: AuthenticatedUser | Organization
        github_org = self.project.user_options.github_org
        owner = self.github.get_organization(github_org) if github_org else self.github.get_user()
        return owner

    def publish(self) -> None:
        """Publish the project to GitHub."""
        opt = self.project.user_options
        homepage = opt.project_homepage
        owner = self.get_owner()
        if not homepage:
            homepage = f"https://github.com/{owner.name}/{opt.project_name}"
        try:
            repo = owner.create_repo(
                name=opt.project_name,
                description=opt.project_description,
                homepage=homepage,
                private=opt.project_private,
                has_issues=False,
                has_projects=False,
                has_wiki=False,
                allow_merge_commit=False,
                allow_squash_merge=True,
                allow_rebase_merge=True,
            )
        except GithubException as e:
            if e.status != http.HTTPStatus.UNPROCESSABLE_ENTITY:
                raise
            match e.data:
                case {"errors": [{"message": "name already exists on this account"}]}:
                    logger.error("Push failed, project exists on github already")
                    return
        else:
            self.git("remote", "add", "origin", repo.ssh_url)
            self.git("push", "-u", "origin")
