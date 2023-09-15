import enum


# List of most common licenses
class License(enum.StrEnum):
    APACHE = "Apache-2.0"
    BOOST = "BSL-1.0"
    GNU_AGPL = "AGPL-3.0-or-later"
    GNU_GPL = "GPL-3.0-or-later"
    GNU_LGPL = "LGPL-3.0-or-later"
    MIT = "MIT"
    MPL = "MPL-2.0"
    UNLICENSE = "Unlicense"


class CodeHosting(enum.StrEnum):
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"


class CloudProvider(enum.StrEnum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class Runtime(enum.Enum):
    NODE12 = "nodejs", "12"
    NODE14 = "nodejs", "14"
    NODE16 = "nodejs", "16"

    PYTHON37 = "python", "3.7"
    PYTHON38 = "python", "3.8"
    PYTHON39 = "python", "3.9"
    PYTHON310 = "python", "3.10"
    PYTHON311 = "python", "3.11"

    def __init__(self, language: str, version: str) -> None:
        self.language = language
        self.version = version
