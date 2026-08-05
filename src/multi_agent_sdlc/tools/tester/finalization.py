from langchain.tools import tool

from multi_agent_sdlc.models import TesterSummary
from multi_agent_sdlc.tools.tester.descriptions import SUBMIT_TESTER_SUMMARY_DESCRIPTION


@tool(
    "submit_tester_summary",
    description=SUBMIT_TESTER_SUMMARY_DESCRIPTION,
)
def submit_tester_summary(
    summary: TesterSummary,
) -> str:
    return "Tester summary accepted."
