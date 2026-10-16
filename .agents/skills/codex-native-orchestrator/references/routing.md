# Routing

Start one Conductor through the chosen native or runner entrypoint. It returns objective, constraints, acceptance, dependencies, role contracts and integration order. Do not inspect/change the host model. Do not start a second Conductor after exploration; the host updates the same plan with evidence. A persistent DAG is immutable; if new facts make it invalid, preserve results and explicitly replan rather than changing hashes or reusing stale evidence.

| Role | Trigger | Required output |
| --- | --- | --- |
| conductor | Every authorized new orchestration run | Bounded startup plan; no edits or delegation |
| explorer | Repository surface/call path uncertain | Exact paths, contracts, existing tests, unknowns |
| researcher | External/versioned API fact affects the decision | Primary sources, version assumptions, implications |
| design_critic | Consequential architecture, shared contract, data or recovery decision | Concrete counterexamples, tradeoffs and minimal amendments before implementation |
| test_author | Material behavior change needing acceptance/regression tests | Test-only patch, requirement/assertion map, evidence the tests are valid |
| worker | Scope and contracts understood | Owned-path implementation, actual checks and risks |
| tester | Behavior/public contract/dependency/state/integration changes | Executed checks on exact candidate, outputs/hashes and gaps |
| reviewer | Final integrated result; fresh instance after repair | Material findings from actual diff and relevant callers, test-quality assessment |
| finding_validator | Disputed material finding | confirmed/refuted/unresolved with evidence, never majority voting |
| debugger | Same issue has failed two fixes, or causal diagnosis is unclear | Hypotheses, discriminating experiment and minimal repair direction |
| guardian | Verification plus Reviewer approve the exact revision | Isolated evidence gate: approve/revise/block |
| scout | Exact search targets, inventories or repeated evidence collection | Paths and facts; uncertainty goes to explorer |
| mechanic | Scope and transformation already decided; repetitive bounded edits | Recipe-bound patch and checks; ambiguity goes to worker |
| check_runner | Exact commands and environment already specified | Ordered raw execution evidence; failures/coverage questions go to tester |

Model/effort assignments are authoritative in the bundled manifest and summarized in SKILL.md. Use Sol / max for the normal reasoning and delivery path: conductor, explorer, researcher, worker, test_author, tester, reviewer and finding_validator. Astra / xhigh is limited to design_critic for consequential design uncertainty, debugger for difficult causal diagnosis or two failed fixes of the same issue, and the controller-isolated guardian after review. Design and debugging specialists return evidence and direction; the Sol worker implements the resulting decision. Do not add duplicate Astra planning, implementation or review just because a task is long or spans many files. Preserve the existing acceptance criteria, independent tests, review and evidence-bound final gate. Reviewer inspects code; Guardian checks the evidence package. Neither replaces test execution. Native test-author and worker use separate owned paths/checkouts. Freeze independently reviewed acceptance tests before final implementation acceptance. Test amendments require a documented appeal; do not let workers rewrite tests to pass.

Default to one implementation writer. Parallel exploration/research or independent modules is useful; shared schema, interfaces, state and dependent call chains need ordered integration. Keep at most four ordinary agents. Special security, performance, concurrency, UI, integration and maintainability checks are risk lenses supplied to reviewer/tester rather than always-on roles. A simplification proposal is read-only; worker implements an accepted change and affected tests rerun.

Runner triggers: explicit DAG/batch/resume/persistence, three dependent nodes, two genuinely independent parallel writers, or recovery across turns. Multi-file alone is not a trigger. `runner off` and `root-only` use native execution; `max agents N` clamps 1..4. Global `read-only` is a capability ceiling, including caches: choose nonwriting commands or report blocked verification. Normal tester nodes use `verification_workspace=disposable` and remain `writes=false`; only generated outputs may change, and nothing is integrated. `verification_workspace=read-only` runs in the existing read-only context.

The host owns final integration and acceptance. Do not invent parallel work, restart a finished role merely to seek agreement, or spawn nested agents.

## Luna execution tier

Use Luna / max by default for these clearly specified subtasks even when the overall assignment is difficult. The Conductor/host sets boundaries and supplies the recipe; Luna executes rather than making missing design decisions. Existing Sol/Astra roles and the final review/gate remain in place. Do not silently change a named role's model or the global default model to achieve routing.

- `scout`: locate a named function, list uses of a configuration key, inventory tests, collect failure excerpts. `explorer` handles ambiguous call chains and impact analysis; `researcher` handles external version/API claims.
- `mechanic`: apply an explicit mapping or established boilerplate/formatting rule with precise `owned_paths`, `change_recipe` (non-empty array), and `acceptance_criteria`. No frozen-test weakening, new behavior/design, security/concurrency/migration decisions, public-contract or dependency changes. If matches are ambiguous or a check fails, stop with partial-work evidence and escalate to `worker`.
- `check_runner`: provide an explicit ordered `check_commands` array; run it in the same disposable verification mechanism as Tester. Do not select coverage, fix the environment, update dependencies/snapshots, diagnose failure or approve delivery. Return `needs_input` at the first failed command/unexpected precondition and hand the evidence to `tester`.

The host decides the handoff and launches the stronger role if needed; child agents never delegate. Preserve partial patches and logs, confirm the original writer has stopped, and transfer ownership before further writing. A pending/uncertain writer is never duplicated. Transport recovery retains existing limits; semantic failure is not permission for repeated Luna guessing.

For persistent writer plans, a Sol `tester` downstream of every writer is still required. Luna check results supplement that verification and do not replace final coverage judgment. Split bulk command execution from critical behavioral checks; do not mechanically rerun identical commands on the unchanged candidate just to give two roles work. Small native tasks may use host-checked Luna command evidence with the normal independent Reviewer/Guardian gate. A plan with only `check_runner` after a writer is rejected by the runner.
