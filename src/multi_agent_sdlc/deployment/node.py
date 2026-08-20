import logging

from multi_agent_sdlc.deployment.artifact import package_project
from multi_agent_sdlc.deployment.config import DEPLOYMENT_BUCKET
from multi_agent_sdlc.deployment.config import EC2_INSTANCE_ID
from multi_agent_sdlc.deployment.s3 import upload_artifact
from multi_agent_sdlc.deployment.ssm import deploy_to_ec2
from multi_agent_sdlc.deployment.ssm import verify_application
from multi_agent_sdlc.deployment.validation import validate_project
from multi_agent_sdlc.workflow.state import DevState


logger = logging.getLogger(__name__)


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

    logger.info(
        "Starting deployment for project: %s",
        project_directory,
    )

    logger.info("Validating project.")
    project = validate_project(project_directory)
    logger.info("Project validation completed.")

    logger.info("Packaging project.")
    artifact = package_project(project)
    logger.info(
        "Project packaged successfully: artifact=%s sha256=%s",
        artifact.path.name,
        artifact.sha256,
    )

    logger.info(
        "Uploading deployment artifact to S3 bucket: %s",
        DEPLOYMENT_BUCKET,
    )
    uploaded_artifact = upload_artifact(
        artifact,
        bucket=DEPLOYMENT_BUCKET,
    )
    logger.info(
        "Deployment artifact uploaded successfully: key=%s",
        uploaded_artifact.key,
    )

    logger.info(
        "Deploying artifact to EC2 instance: %s",
        EC2_INSTANCE_ID,
    )
    deployment = deploy_to_ec2(
        uploaded_artifact,
        instance_id=EC2_INSTANCE_ID,
    )
    logger.info(
        "Deployment completed: instance_id=%s command_id=%s",
        deployment.instance_id,
        deployment.command_id,
    )

    logger.info("Verifying deployed application.")
    verification = verify_application(
        deployment,
    )

    if verification.passed:
        logger.info(
            "Deployment verification passed: instance_id=%s",
            verification.instance_id,
        )
    else:
        logger.error(
            "Deployment verification failed: "
            "instance_id=%s exit_code=%s stdout=%r stderr=%r",
            verification.instance_id,
            verification.exit_code,
            verification.command_id,
            verification.stdout,
            verification.stderr,
        )

    return {
        "deployment_result": deployment,
        "deployment_verification": verification,
    }
