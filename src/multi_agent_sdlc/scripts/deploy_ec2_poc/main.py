from dotenv import load_dotenv
from multi_agent_sdlc.scripts.deploy_ec2_poc.s3 import upload_artifact
import os
from multi_agent_sdlc.scripts.deploy_ec2_poc.artifact import package_project
from multi_agent_sdlc.scripts.deploy_ec2_poc.validation import validate_project
from pathlib import Path

PROJECT_DIRECTORY = Path("/home/pedro/projects/multi-agent-sdlc/sandbox/project_id")
DEPLOYMENT_BUCKET = os.getenv("DEPLOYMENT_BUCKET", "multi-agent-sdlc-deployments")
load_dotenv(override=True)


def main() -> None:
    project = validate_project(PROJECT_DIRECTORY)
    artifact = package_project(project)
    uploaded_artifact = upload_artifact(
        artifact,
        bucket=DEPLOYMENT_BUCKET,
    )
    exit()


if __name__ == "__main__":
    main()
