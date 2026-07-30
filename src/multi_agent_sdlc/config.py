import os
from dotenv import load_dotenv


load_dotenv(override=True)

SANDBOX_ROOT = os.getenv("SANDBOX_ROOT")
