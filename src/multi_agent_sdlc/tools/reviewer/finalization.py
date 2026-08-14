from multi_agent_sdlc.tools.reviewer.description import (
    SUBMIT_REVIEWER_SUMMARY_DESCRIPTION,
)
from multi_agent_sdlc.agents.reviewer.models import ReviewerSummary
from langchain.tools import tool


@tool(
    "submit_reviewer_summary",
    description=SUBMIT_REVIEWER_SUMMARY_DESCRIPTION,
)
def submit_reviewer_summary(
    summary: ReviewerSummary,
) -> str:
    return ""
