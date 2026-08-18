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


class DeploymentResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    instance_id: str = Field(
        description=(
            "Identifier of the EC2 instance where the deployment "
            "command was executed."
        )
    )

    command_id: str = Field(
        description=(
            "Systems Manager Run Command identifier associated " "with the deployment."
        )
    )

    exit_code: int = Field(
        description=("Exit code returned by the remote deployment command.")
    )

    stdout: str = Field(
        description=("Standard output produced by the remote deployment.")
    )

    stderr: str = Field(
        description=("Standard error produced by the remote deployment.")
    )


class ApplicationVerificationResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    instance_id: str = Field(
        description=(
            "Identifier of the EC2 instance where application "
            "verification was executed."
        )
    )

    command_id: str = Field(
        description=(
            "Systems Manager Run Command identifier associated "
            "with application verification."
        )
    )

    passed: bool = Field(
        description=(
            "Whether all remote application verification checks "
            "completed successfully."
        )
    )

    exit_code: int = Field(
        description=("Exit code returned by the remote verification command.")
    )

    stdout: str = Field(
        description=("Standard output produced by application verification.")
    )

    stderr: str = Field(
        description=("Standard error produced by application verification.")
    )
