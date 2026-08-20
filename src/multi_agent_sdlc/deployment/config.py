import os

from dotenv import load_dotenv

load_dotenv(override=True)

DEPLOYMENT_BUCKET = os.getenv("DEPLOYMENT_BUCKET", "multi-agent-sdlc-deployments")
EC2_INSTANCE_ID = os.getenv("EC2_INSTANCE_ID")
