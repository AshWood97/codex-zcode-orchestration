# Focused checking and completion

Plan from the request and relevant source, implement the smallest change, then inspect the result once against that plan. Understand actual behavior and directly affected callers; do not equate a larger process with higher quality.

A check is a scoped read of the result, diff and relevant context. It does not imply tests, builds, benchmarks, experiments, a security audit or extra agents. Those activities need an explicit user request. Do not relabel tests as verification to bypass this boundary.

Use one checking owner: host or reviewer. Findings identify the concrete trigger, path/symbol, impact and code/content basis. Do not invent findings, demand speculative future protections or treat missing unrequested tests as a defect. Review is read-only and never expands an inspection-only task into repairs.

In an implementation task, the writer fixes an actual in-scope defect. Inspect the repair and its direct effects; keep previous conclusions for unchanged parts. Do not restart planning, rerun completed work or add a fresh review instance by default. Stop and ask only if the next action exceeds the user's scope or requires a missing decision.

Deliver once the requested behavior is implemented and no concrete in-scope defect remains. Report the result, the focused inspection performed and any actual unresolved limitation concisely. No required test report, hash, evidence pack, log archive, sign-off file or Guardian verdict. Never claim an unperformed action was performed.
