from multi_agent_sdlc.scripts.deploy_ec2_poc.ssm import verify_application
from multi_agent_sdlc.scripts.deploy_ec2_poc.ssm import deploy_to_ec2
from dotenv import load_dotenv
from multi_agent_sdlc.scripts.deploy_ec2_poc.s3 import upload_artifact
import os
from multi_agent_sdlc.scripts.deploy_ec2_poc.artifact import package_project
from multi_agent_sdlc.scripts.deploy_ec2_poc.validation import validate_project
from pathlib import Path

load_dotenv(override=True)

PROJECT_DIRECTORY = Path("/home/pedro/projects/multi-agent-sdlc/sandbox/project_id")
DEPLOYMENT_BUCKET = os.getenv("DEPLOYMENT_BUCKET", "multi-agent-sdlc-deployments")
EC2_INSTANCE_ID = os.getenv("EC2_INSTANCE_ID")


def main() -> None:
    if not PROJECT_DIRECTORY.is_dir():
        raise ValueError(f"Project directory does not exist: {PROJECT_DIRECTORY}")

    if not DEPLOYMENT_BUCKET:
        raise ValueError("DEPLOYMENT_BUCKET environment variable is required.")

    if not EC2_INSTANCE_ID:
        raise ValueError("EC2_INSTANCE_ID environment variable is required.")

    project = validate_project(PROJECT_DIRECTORY)
    artifact = package_project(project)
    uploaded_artifact = upload_artifact(
        artifact,
        bucket=DEPLOYMENT_BUCKET,
    )
    deployment = deploy_to_ec2(
        uploaded_artifact,
        instance_id=EC2_INSTANCE_ID,
    )
    verification = verify_application(
        deployment,
    )

    print(verification.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
