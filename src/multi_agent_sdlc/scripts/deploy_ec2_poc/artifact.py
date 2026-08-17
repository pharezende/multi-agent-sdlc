from multi_agent_sdlc.scripts.deploy_ec2_poc.models import DeploymentArtifact
from multi_agent_sdlc.scripts.deploy_ec2_poc.models import ValidatedProject
import hashlib
import tarfile
import tempfile
from pathlib import Path


EXCLUDED_NAMES = {
    ".git",
    ".venv",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    "htmlcov",
    ".coverage",
    ".env",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
}


def package_project(
    project: ValidatedProject,
) -> DeploymentArtifact:
    project_directory = project.project_directory.resolve()

    artifact_directory = Path(tempfile.mkdtemp(prefix="deploy-ec2-poc-"))

    artifact_path = artifact_directory / f"{project_directory.name}.tar.gz"

    with tarfile.open(
        artifact_path,
        mode="w:gz",
    ) as archive:
        for path in sorted(project_directory.rglob("*")):
            if _should_exclude(
                path,
                project_directory,
            ):
                continue

            relative_path = path.relative_to(project_directory)

            archive.add(
                path,
                arcname=relative_path.as_posix(),
                recursive=False,
            )

    sha256 = _calculate_sha256(artifact_path)

    return DeploymentArtifact(
        path=artifact_path,
        sha256=sha256,
    )


def _should_exclude(
    path: Path,
    project_directory: Path,
) -> bool:
    relative_path = path.relative_to(project_directory)

    if any(part in EXCLUDED_NAMES for part in relative_path.parts):
        return True

    if path.suffix in EXCLUDED_SUFFIXES:
        return True

    return False


def _calculate_sha256(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)

    return digest.hexdigest()
