from pathlib import Path

from bluecopier.enums import CodeHosting, License
from bluecopier.project import Project
from bluecopier.user_options import UserOptions


def test_roundtrip(tmp_path: Path) -> None:
    output_path = tmp_path
    user_options = UserOptions(
        blueprint_names=["python"],
        code_hosting=CodeHosting.GITHUB,
        raw_features=[],
        license_=License.MIT,
        output_dir=output_path,
        project_homepage="https://example.com",
        project_name="Project name",
        publish=True,
        project_private=True,
        project_description="Description",
        github_org="some org",
    )
    project = Project(user_options=user_options)
    project.write_state()
    loaded = Project.from_path(user_options.output_dir)
    assert loaded.user_options == project.user_options
