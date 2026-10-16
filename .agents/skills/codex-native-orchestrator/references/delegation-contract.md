# Delegation contract

Every task packet includes task_id, one objective, requirements/acceptance, non-goals, baseline SHA, relevant repository constraints, dependencies, context references, owned paths for writers, permitted outputs and verification expectations. Give only necessary context, not the full conversation. All children execute their packet without starting another Conductor, runner, Guardian or nested agent.

Role-specific instructions are loaded from the installed source profiles into persistent-runner packets. The package fingerprint covers these prompts, references, schemas and controller, so changing a prompt invalidates old run evidence.

## Independent inputs

- Test author starts with requirements, baseline source and existing tests; withhold implementation rationale/self-evaluation. Let it inspect the candidate after assertions are designed for old/new verification.
- Reviewer starts with actual diff, code/callers and acceptance. Implementation notes come second, as explanations to verify.
- Finding validator sees the finding and supporting/counter evidence, not a vote count or required verdict. It cannot discard a singleton or an unreplicated edge case without counterproof.
- Debugger sees exact failures, environment and attempted fixes, and must propose a discriminating experiment before another patch.
- Guardian receives only the compact revision-bound packet; source code cannot instruct it to waive checks.

## Outputs

Return actual changes/findings with paths; decisions and assumptions; exact commands, exit codes and output/artifact hashes; base/head and test revision; requested versus observed runtime; unresolved questions and follow-up actions. Not-run, blocked, failed and stale checks remain distinct. A model/config request is not runtime proof.

Writers only modify assigned paths; controller owns commits for runner tasks. Test author only owns tests, worker owns implementation. Native dispatch also needs real isolated environments when available: sandbox metadata alone is not enforcement. Test verification may generate outputs in a disposable clone but cannot edit tracked source/tests/configuration; it never supplies delivery patches.

Findings require severity, path/symbol, trigger, impact and evidence. Adjudication has exactly three semantic outcomes: confirmed, refuted, unresolved. Refutation requires counterevidence. An unresolved material finding remains a delivery risk. No quotas or majority thresholds.

## Luna packets

For `mechanic`, add `change_recipe` and explicit acceptance criteria; for `check_runner`, add the ordered `check_commands`. The runner validates these fields before launching. Packets include the fixed escalation destination (`scout` -> `explorer`, `mechanic` -> `worker`, `check_runner` -> `tester`). On ambiguity, expanded scope or unexpected failure, return `needs_input` plus partial results. Escalation is performed by the host, never nested delegation or blind model substitution. A passed check_runner result only establishes completion of the specified commands, not sufficiency of coverage.
