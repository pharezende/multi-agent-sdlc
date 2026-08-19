from multi_agent_sdlc.deployment.config import EC2_INSTANCE_ID
from multi_agent_sdlc.deployment.config import DEPLOYMENT_BUCKET
from multi_agent_sdlc.deployment.ssm import verify_application
from multi_agent_sdlc.deployment.ssm import deploy_to_ec2
from multi_agent_sdlc.deployment.s3 import upload_artifact
from multi_agent_sdlc.deployment.artifact import package_project
from multi_agent_sdlc.deployment.validation import validate_project
from multi_agent_sdlc.workflow.state import DevState


def deployer_node(
    state: DevState,
) -> dict[str, object]:
    project_directory = state["project_directory"]
    if project_directory is None:
        raise ValueError("Project directory cannot be None")

    if not project_directory.is_dir():
        raise ValueError(f"Project directory does not exist: {project_directory}")

    if not DEPLOYMENT_BUCKET:
        raise ValueError("DEPLOYMENT_BUCKET environment variable is required.")

    if not EC2_INSTANCE_ID:
        raise ValueError("EC2_INSTANCE_ID environment variable is required.")

    project = validate_project(project_directory)

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

    return {
        "deployment_result": deployment,
        "deployment_verification": verification,
    }
