from multi_agent_sdlc.models import CoderSummary
from multi_agent_sdlc.tools.coder.descriptions import SUBMIT_CODER_SUMMARY_DESCRIPTION
from langchain.tools import tool


@tool(
    "submit_coder_summary",
    description=SUBMIT_CODER_SUMMARY_DESCRIPTION,
)
def submit_coder_summary(
    summary: CoderSummary,
) -> str:
    return "Coder summary accepted."
