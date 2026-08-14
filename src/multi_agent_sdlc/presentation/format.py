from multi_agent_sdlc.agents.tester.model import TesterSummary
from multi_agent_sdlc.presentation.plan_formatter import format_items


def format_verification_block_review(
    tester_summary: TesterSummary,
) -> str:
    lines: list[str] = [
        "VERIFICATION BLOCK REVIEW",
        "=" * 72,
        "",
        f"Overall status: {tester_summary.overall_status}",
        "",
        "ADDRESSED TASKS",
        *format_items(tester_summary.addressed_task_ids),
        "",
        "PASSED TASKS",
        *format_items(tester_summary.passed_task_ids),
        "",
        "RELATED TASKS",
        *format_items(tester_summary.related_task_ids),
        "",
        "VERIFICATION RESULTS",
        "=" * 72,
    ]

    for result in tester_summary.verification_results:
        lines.extend(
            [
                "",
                result.verification_type.replace("_", " ").upper(),
                "-" * 72,
                f"Status: {result.status}",
                (
                    "Command: "
                    + (" ".join(result.command) if result.command else "None")
                ),
                (
                    "Exit code: "
                    + (
                        str(result.exit_code)
                        if result.exit_code is not None
                        else "None"
                    )
                ),
                (
                    "Verified tasks: "
                    + (
                        ", ".join(result.verified_task_ids)
                        if result.verified_task_ids
                        else "None"
                    )
                ),
                "",
                "Summary",
                result.summary,
            ]
        )

    lines.extend(
        [
            "",
            "IMPLEMENTATION FAILURES",
            "=" * 72,
        ]
    )

    if tester_summary.implementation_failures:
        for index, failure in enumerate(
            tester_summary.implementation_failures,
            start=1,
        ):
            lines.extend(
                [
                    "",
                    f"{index}. {failure.description}",
                    f"Related tasks: "
                    + (
                        ", ".join(failure.related_task_ids)
                        if failure.related_task_ids
                        else "None"
                    ),
                    "",
                    "Evidence",
                    failure.evidence,
                ]
            )
    else:
        lines.append("None")

    lines.extend(
        [
            "",
            "UNRESOLVED ISSUES",
            "=" * 72,
        ]
    )

    if tester_summary.unresolved_issues:
        for index, issue in enumerate(
            tester_summary.unresolved_issues,
            start=1,
        ):
            lines.extend(
                [
                    "",
                    f"{index}. {issue.description}",
                    f"Owner: {issue.owner}",
                    (
                        "Related tasks: "
                        + (
                            ", ".join(issue.related_task_ids)
                            if issue.related_task_ids
                            else "None"
                        )
                    ),
                    "",
                    "Evidence",
                    issue.evidence,
                ]
            )
    else:
        lines.append("None")

    lines.extend(
        [
            "",
            "CODER REPAIR REQUESTS",
            "=" * 72,
        ]
    )

    if tester_summary.coder_repair_requests:
        for index, request in enumerate(
            tester_summary.coder_repair_requests,
            start=1,
        ):
            lines.extend(
                [
                    "",
                    f"{index}. Repair request",
                    "-" * 72,
                    (
                        "Related tasks: "
                        + (
                            ", ".join(request.related_task_ids)
                            if request.related_task_ids
                            else "None"
                        )
                    ),
                    "",
                    "Affected files",
                    *format_items(
                        request.affected_files,
                        indentation="  ",
                    ),
                    "",
                    "Failed criteria",
                    *format_items(
                        request.failed_criteria,
                        indentation="  ",
                    ),
                    "",
                    "Observed behavior",
                    request.observed_behavior,
                    "",
                    "Expected behavior",
                    request.expected_behavior,
                    "",
                    "Evidence",
                    request.evidence,
                ]
            )
    else:
        lines.append("None")

    return "\n".join(lines)
