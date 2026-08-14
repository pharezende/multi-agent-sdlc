SUBMIT_REVIEWER_SUMMARY_DESCRIPTION = """
Submit the final structured handoff summary for the Reviewer stage.

Call this tool only when:
- the implementation has been reviewed against the approved DevelopmentPlan,
  current repository state, and available verification evidence; or
- no further safe review work can continue because of a genuine blocker.

This is a terminal Reviewer action. Call it alone. After calling it, do not
request additional repository inspection, search, diff, verification,
analysis, build, packaging, or application-execution operations.

Populate the summary only with evidence from:
- the original request and approved DevelopmentPlan;
- the current Coder handoff;
- the current Tester handoff and verification results;
- the previous Reviewer handoff, when performing a re-review;
- repository files and code actually inspected;
- repository searches and diffs actually performed;
- concrete engineering issues observed during the review;
- unresolved blockers or limitations that prevented completion of the review.

The summary must:
- provide a concise overall assessment of the implementation;
- use overall_status="passed" when no material engineering issues remain;
- use overall_status="repair-required" when one or more material issues require
  changes before the workflow can proceed;
- use overall_status="blocked" when insufficient evidence or another genuine
  blocker prevents the review from being completed;
- identify only material and actionable findings;
- identify the affected project-relative file or component when possible;
- explain why each finding matters;
- state the required correction or expected outcome without implementing it;
- distinguish required repairs from optional or stylistic improvements;
- report unresolved review limitations or blockers;
- when re-reviewing, assess whether previous material findings were adequately
  addressed based on the current repository state;
- provide concise handoff information for the next workflow stage.

Do not:
- call this tool while more safe review work remains;
- call it together with another tool;
- modify, create, delete, or rewrite repository files;
- implement fixes;
- act as the Coder or Tester;
- duplicate routine Tester verification without a concrete review reason;
- request repairs for purely cosmetic or subjective preferences;
- invent findings merely to produce review feedback;
- claim that previous findings were resolved without inspecting sufficient
  current evidence;
- claim that unperformed inspection or verification succeeded;
- claim that deployment, merge, release, or other downstream work succeeded;
- invent files, code behavior, findings, commands, verification results,
  blockers, or successful outcomes;
- return the final summary as ordinary text or Markdown instead of calling this
  tool.
""".strip()
