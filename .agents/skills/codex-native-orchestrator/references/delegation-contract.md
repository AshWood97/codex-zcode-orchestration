# Bounded task packets

Give each child one objective, the relevant requirements, source/context, owned paths for edits, constraints, dependencies and a concise expected result. Include the user's execution boundary. For mechanic, supply the exact edit recipe. For a specialist or test role, identify the concrete task question, why existing inspection/results are insufficient, and the smallest assigned scope. A planner selection within the user's request is sufficient; do not demand a separate user request naming that role. Respect explicit user prohibitions.

Use existing chat results and readable diffs directly. Do not require baseline hashes, output digests, artifact signatures, logs, receipts or a separate packet file. Do not forward unrelated conversation history.

Children do only their packet and never delegate. Writers modify only their assigned paths. Reviewers, researchers and planners stay read-only. A review finding is not permission for the reviewer to fix code. Existing files and user edits outside the task remain untouched.

Return the actual change or answer with useful paths, concrete findings and any specific blocker. No ceremonial evidence bundle or duplicate check. For assigned commands, report the command and actual result in chat; do not create logs by default.
