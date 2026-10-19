# Planner-led role selection

Once this skill is activated, conductor evaluates a multi-role task and selects any roles needed to complete it. The host dispatches that plan; children do not delegate. Simple work and root-only stay with the host. User naming of individual roles is not required. Explicit no-tests, read-only and other user constraints take precedence.

Choose a useful subset, never the whole catalog by default. Each specialist must address a concrete question that matters to the requested result; no role is added just because the task is large or "important". State the reason briefly in the existing plan, with no extra forms or logs.

| Concrete need | Role |
| --- | --- |
| Assess an orchestrated task, its dependencies and necessary roles | conductor, once; update the same plan as facts change |
| Relevant source/call path is unknown | explorer; scout for exact factual retrieval |
| An implementation decision depends on an unknown external API fact | researcher |
| Semantic implementation within agreed paths | worker |
| An exact mechanical edit with a known recipe | mechanic |
| Compare the result with requirements and relevant callers | reviewer or host, one owner |
| A concrete defect has an unclear cause | debugger; no retry-count trigger |
| A consequential design tradeoff remains unresolved | design_critic before implementation |
| A disputed finding materially changes the implementation or delivery decision | finding_validator, on that finding only |
| A distinct, consequential acceptance question remains after ordinary inspection | guardian, on that question only; no blanket second review |
| An important behavior needs a targeted check and existing tests lack that case | test_author, only the missing case |
| An important behavior cannot be resolved from inspection or existing observations | tester, the smallest relevant existing test or reproduction |
| A necessary check has an exact bounded command list | check_runner instead of a second tester on the same commands |

Prefer no extra tests when inspection is sufficient. Prefer existing targeted tests over writing new ones. Select test_author only for a demonstrated gap; it does not imply a mandatory tester/reviewer/Guardian chain. Do not run suites, build matrices, benchmarks or experiments by default. Stop when the planned question is resolved. Reuse unaffected results after repairs.

If a bounded task becomes ambiguous, return the specific question and partial result to the host. Update the current plan, then select a different role only if it addresses the new concrete need. Do not silently substitute role models or repeat an already completed investigation.
