import os


def build_sandbox_environment() -> dict[str, str]:
    """Create an environment isolated from the orchestrator's Python setup."""
    environment = os.environ.copy()

    # Do not expose the orchestrator's active virtual environment to uv.
    environment.pop("VIRTUAL_ENV", None)

    # Do not leak custom Python import/runtime configuration.
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)

    # Prevent imports from the user's global site-packages directory.
    environment["PYTHONNOUSERSITE"] = "1"

    return environment
