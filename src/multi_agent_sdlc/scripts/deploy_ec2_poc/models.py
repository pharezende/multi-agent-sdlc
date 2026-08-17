from pathlib import Path

from pydantic import BaseModel, ConfigDict


class ValidatedProject(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    project_directory: Path
    dockerfile: Path
    compose_file: Path


class DeploymentArtifact(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    path: Path
    sha256: str


from pydantic import BaseModel, ConfigDict, Field


class UploadedArtifact(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    bucket: str = Field(
        description=("Name of the S3 bucket containing the deployment artifact.")
    )

    key: str = Field(
        description=("S3 object key identifying the uploaded deployment artifact.")
    )

    sha256: str = Field(
        description=(
            "SHA-256 digest of the deployment artifact used for integrity "
            "verification after download."
        )
    )
