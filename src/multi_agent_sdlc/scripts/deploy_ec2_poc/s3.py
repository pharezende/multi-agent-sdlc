import boto3

from multi_agent_sdlc.scripts.deploy_ec2_poc.models import (
    DeploymentArtifact,
    UploadedArtifact,
)


def upload_artifact(
    artifact: DeploymentArtifact,
    bucket: str,
    prefix: str = "deployments",
) -> UploadedArtifact:
    artifact_path = artifact.path.resolve()

    if not artifact_path.is_file():
        raise ValueError(f"Deployment artifact does not exist: {artifact_path}")

    key = f"{prefix.rstrip('/')}/" f"{artifact.sha256[:12]}-{artifact_path.name}"

    session = boto3.Session(
        profile_name="multi-agent-sdlc",
    )

    s3_client = session.client("s3")

    s3_client.upload_file(
        Filename=str(artifact_path),
        Bucket=bucket,
        Key=key,
        ExtraArgs={
            "Metadata": {
                "sha256": artifact.sha256,
            },
        },
    )

    return UploadedArtifact(
        bucket=bucket,
        key=key,
        sha256=artifact.sha256,
    )
