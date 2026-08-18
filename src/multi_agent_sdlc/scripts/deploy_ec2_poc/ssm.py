from multi_agent_sdlc.scripts.deploy_ec2_poc.models import ApplicationVerificationResult
import shlex

import boto3
from botocore.exceptions import WaiterError

from multi_agent_sdlc.scripts.deploy_ec2_poc.models import (
    DeploymentResult,
    UploadedArtifact,
)


DEPLOYMENT_DIRECTORY = "/opt/multi-agent-sdlc-poc"
REMOTE_ARTIFACT_PATH = "/tmp/multi-agent-sdlc-deployment.tar.gz"
HEALTH_URL = "http://localhost:8000/api/health"


def verify_application(
    deployment: DeploymentResult,
) -> ApplicationVerificationResult:
    script = "\n".join(
        [
            "set -euo pipefail",
            f"cd {shlex.quote(DEPLOYMENT_DIRECTORY)}",
            "docker compose ps",
            (
                "for attempt in $(seq 1 12); do "
                f"if curl --fail --silent --show-error "
                f"{shlex.quote(HEALTH_URL)}; then "
                "exit 0; "
                "fi; "
                "sleep 5; "
                "done; "
                "exit 1"
            ),
        ]
    )

    session = boto3.Session(
        profile_name="multi-agent-sdlc",
    )

    ssm_client = session.client("ssm")

    response = ssm_client.send_command(
        InstanceIds=[deployment.instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={
            "commands": [script],
        },
    )

    command_id = response["Command"]["CommandId"]

    waiter = ssm_client.get_waiter("command_executed")

    try:
        waiter.wait(
            CommandId=command_id,
            InstanceId=deployment.instance_id,
            WaiterConfig={
                "Delay": 5,
                "MaxAttempts": 60,
            },
        )
    except WaiterError:
        pass

    invocation = ssm_client.get_command_invocation(
        CommandId=command_id,
        InstanceId=deployment.instance_id,
    )

    exit_code = invocation["ResponseCode"]

    return ApplicationVerificationResult(
        instance_id=deployment.instance_id,
        command_id=command_id,
        passed=exit_code == 0,
        exit_code=exit_code,
        stdout=invocation.get(
            "StandardOutputContent",
            "",
        ),
        stderr=invocation.get(
            "StandardErrorContent",
            "",
        ),
    )


def deploy_to_ec2(
    artifact: UploadedArtifact,
    instance_id: str,
) -> DeploymentResult:
    s3_uri = f"s3://{artifact.bucket}/{artifact.key}"

    script = "\n".join(
        [
            "set -euo pipefail",
            (
                f"aws s3 cp "
                f"{shlex.quote(s3_uri)} "
                f"{shlex.quote(REMOTE_ARTIFACT_PATH)}"
            ),
            (
                f"echo "
                f"{shlex.quote(f'{artifact.sha256}  {REMOTE_ARTIFACT_PATH}')} "
                "| sha256sum -c -"
            ),
            f"rm -rf {shlex.quote(DEPLOYMENT_DIRECTORY)}",
            f"mkdir -p {shlex.quote(DEPLOYMENT_DIRECTORY)}",
            (
                f"tar -xzf "
                f"{shlex.quote(REMOTE_ARTIFACT_PATH)} "
                f"-C {shlex.quote(DEPLOYMENT_DIRECTORY)}"
            ),
            f"cd {shlex.quote(DEPLOYMENT_DIRECTORY)}",
            "docker compose up -d --build --force-recreate --wait --wait-timeout 60",
            "docker compose up -d --wait --wait-timeout 60",
        ]
    )

    session = boto3.Session(  #
        profile_name="multi-agent-sdlc",
    )

    ssm_client = session.client("ssm")

    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={
            "commands": [script],
        },
    )

    command_id = response["Command"]["CommandId"]

    waiter = ssm_client.get_waiter("command_executed")

    try:
        waiter.wait(
            CommandId=command_id,
            InstanceId=instance_id,
            WaiterConfig={
                "Delay": 5,
                "MaxAttempts": 120,
            },
        )
    except WaiterError:
        pass

    invocation = ssm_client.get_command_invocation(
        CommandId=command_id,
        InstanceId=instance_id,
    )

    return DeploymentResult(
        instance_id=instance_id,
        command_id=command_id,
        exit_code=invocation["ResponseCode"],
        stdout=invocation.get(
            "StandardOutputContent",
            "",
        ),
        stderr=invocation.get(
            "StandardErrorContent",
            "",
        ),
    )
