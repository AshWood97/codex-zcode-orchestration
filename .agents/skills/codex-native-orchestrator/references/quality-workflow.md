# Focused checking and completion

Plan from the request and relevant source, implement the smallest change, then inspect the result once against that plan. Understand actual behavior and directly affected callers; do not equate a larger process with higher quality.

A check is a scoped read of the result, diff and relevant context. It does not imply tests, builds, benchmarks, experiments, a security audit or extra agents. The planner may select a specialist or minimal targeted test for a concrete important question that inspection cannot resolve. User naming of a role is not required. Keep an explicit no-tests or read-only request binding, and describe a test honestly as a test.

Use one checking owner: host or reviewer. Findings identify the concrete trigger, path/symbol, impact and code/content basis. Do not invent findings, demand speculative future protections or treat missing tests alone as a defect. A specific unresolved behavior can justify a focused test; test absence by itself cannot. Review is read-only and never expands an inspection-only task into repairs.

In an implementation task, the writer fixes an actual in-scope defect. Inspect the repair and its direct effects; keep previous conclusions for unchanged parts. Update the existing plan only for new facts. Do not restart planning, repeat unaffected work or add a fresh review instance by default. A materially changed input may justify rerunning its affected check; an unresolved consequential question may justify a different specialist with a distinct scope. Stop and ask only if the next action exceeds the user's scope or requires a missing decision.

Deliver once the requested behavior is implemented and no concrete in-scope defect remains. Report the result, the focused inspection performed and any actual unresolved limitation concisely. No required test report, hash, evidence pack, log archive, sign-off file or Guardian verdict. Never claim an unperformed action was performed.
