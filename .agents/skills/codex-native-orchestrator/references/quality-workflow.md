# Quality workflow

## Acceptance before implementation approval

Map requirements to assertions. For a bug fix, show the old version fails because of the target behavior and the repaired version passes. Import, installation and environment failures are not reproductions. For new features cover boundaries, error paths and contract interactions. Refactors must preserve behavior; do not demand old-version failure. Mocks cannot bypass the behavior being tested. Choose property, differential, integration or targeted mutation tests where they answer a concrete risk, not to inflate coverage.

The host checks the test author's reasoning and freezes the reviewed test revision/hash. Workers may read development tests but must not modify them. A wrong test is possible: an implementation-side appeal must show a requirement conflict or counterexample; test_author revises it with a recorded reason, then independent review and execution refresh the evidence. Held-out evaluation tests stay hidden from candidate generation; ordinary development tests need not be hidden.

After integration, Tester executes checks in a separate disposable copy. The controller checks tracked files and protected Git metadata before/after; output caches never enter integration. This is a boundary check, not a proof against transient edits or every external tool side effect. Record environment and effective permissions honestly.

## Review and repair

Reviewer inspects the final code and test validity. Apply only relevant lenses: security/authorization; transactions/retries/concurrency; cross-module integration; measured performance; real UI/backend interaction; maintainability and unnecessary abstraction. A simulated UI or mocked service result does not establish end-to-end behavior.

Disputed findings go to finding_validator. confirmed needs evidence; refuted needs counterproof; unresolved preserves uncertainty. A valid singleton is not outvoted. The validator diagnoses, the worker repairs, and the tester executes reproductions. The host resolves requirements and final integration.

After two unsuccessful fixes for the same issue, use debugger before another attempt. Limit the task to five automatic repair waves; stop with the remaining defect/evidence if exhausted. Fresh scoped review covers original findings, new diff and impacted callers, rather than repeatedly rereading the entire repository. Code/tests/requirements/dependencies/environment changes invalidate affected evidence. Never relabel stale evidence as a new run.

Native and runner final rejections can be repaired under the same task with the revision-bound receipt in guardian-gate.md. Repeated verdict requests on the same tree are blocked; changed intent, contracts or ownership require replanning, not a repair receipt.

## Conditional candidate comparison

Use two isolated native checkouts only for a consequential uncertainty. Both receive the same baseline, requirements, acceptance suite and budget; do not feed one candidate's solution to the other. Preserve candidate ID, base SHA, patch SHA/hash, test revision, distinguishing tests, review and selection reason in the host ledger. Select one candidate and integrate only its patch. Additive runner DAGs reject candidate_id/candidate_group. Enable this route by default only after held-out local evaluation shows a repeatable quality gain.
