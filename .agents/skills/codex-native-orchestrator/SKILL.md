---
name: codex-native-orchestrator
description: Plan, implement and check scoped repository work with native Codex roles when explicitly invoked or authorized by the current Ultra runtime. Keep simple work in the host; no automatic tests or extra acceptance gates.
---

# Codex Native Orchestration

## Activation: manual invocation or Ultra

Only the primary/host agent coordinates this workflow. Delegated children execute their assigned packet and never start another orchestration.

A new task requires either entrypoint:

- **Manual:** The user selects **Codex Native Orchestration** from the skill/slash menu or directly invokes `$codex-native-orchestrator` with a task. Typing `/codex` only filters the menu. Questions, quotations, screenshots and requests to inspect or edit this skill are not invocations.
- **Ultra:** The latest trusted runtime/developer `<multi_agent_mode>` instruction says **"Proactive multi-agent delegation is active"**, and the repository task benefits from division of the requested work. Simple questions and localized edits remain in the host.

Ordinary/Max task matching, the word `ultra`, full access, saved model settings, available agent tools and earlier skill use do not activate this skill. A later explicit-request-only runtime instruction disables automatic activation for new tasks. Unknown mode requires manual invocation. Keep `policy.allow_implicit_invocation: false`; the [activation block](references/activation.md) loads this skill conditionally.

Both entrypoints use the same workflow. Continue unfinished work from its existing plan and results; do not restart completed steps. Re-evaluate activation for independent new tasks. Do not inspect or change the host model/effort to match a role.

## Execution boundary

Do only the user's requested work and deliver the minimum working result. Do not add compatibility layers, defensive wrappers, future abstractions, adjacent refactors, duplicate inspections or extra output files for hypothetical benefit.

Do not calculate SHA-256, MD5, checksums, fingerprints or signatures, create `.sha256` files, or add integrity/evidence layers by default. Hashing is allowed only when the user explicitly requests published checksums, deduplication, cache-hit decisions, or rejection against a known digest, and the result is actually published or consumed by that requested operation. A digest without a downstream consumer is forbidden. "Just in case", professionalism and future traceability are not authorization.

Do not author or run tests, builds, benchmarks, A/B experiments, mutation checks or test suites unless explicitly requested by the user. Do not disguise them as checks. An orchestration invocation or Ultra mode does not request testing. Do not add subagents, full reviews or extra gates merely for reassurance.

When a proposed addition exceeds the requested scope, stop that addition, ask one sentence — “我想加 X，因为 Y，是否允许？” — and wait. Do not do it first or ask about routine work already authorized.

## Plan → implement → check → fix or release

1. **Plan:** Understand the goal, relevant source, constraints, dependencies and completion conditions. Decide the smallest implementation before editing. Keep one proportionate plan in the conversation; revise only facts that changed. The host plans simple work. Use one `conductor` only when the requested decomposition needs it; it is not a mandatory startup gate.
2. **Implement:** The host or one suitable writer makes the scoped change. Delegate only actual parts of the authorized work. Share the relevant plan and paths, not the whole conversation. Order dependent edits; use parallel writers only when the requested work actually needs independent parts.
3. **Check once:** The host or one `reviewer` compares the actual result/diff with the requirements and relevant callers. This is a focused content/code inspection, not command execution, a test phase or a full-repository audit. Choose one owner; do not repeat the same check in the host and another role. A review-only request produces findings and never authorizes edits.
4. **Fix or release:** For an implementation request, fix concrete in-scope defects, then inspect only the repair and directly affected paths. Reuse unchanged conclusions. If the result meets the request and no concrete issue remains, deliver immediately. No automatic Guardian, fresh reviewer, test rerun, diagnostic escalation or fixed number of repair waves. If a repair needs new scope or a missing decision, explain that specific blocker.

See [routing](references/routing.md) when assigning work, [delegation](references/delegation-contract.md) when forming a packet, and [checking](references/quality-workflow.md) for the completion boundary.

## Roles and runtime

| Roles | Model | Effort |
| --- | --- | --- |
| conductor, explorer, researcher, worker, reviewer, finding_validator, test_author, tester | `gpt-6.1-sol` | `max` |
| scout, mechanic, check_runner | `gpt-6-luna` | `max` |
| design_critic, debugger, guardian | `gpt-6-astra` | `xhigh` |

The JSON manifest defines the named role models and efforts. Preserve them; do not silently substitute. Use native agent tools directly. `test_author`, `tester`, `check_runner`, `guardian`, `design_critic` and `finding_validator` are explicit-request-only specialist roles, not a pipeline. Their presence does not require using them. A missing test report, digest or Guardian verdict is not a reason to block normal completion.

Default to one writer and at most four children, only as needed. Honor `root-only`, `max agents N` and `read-only`; `root-only` uses the host for planning, implementation and inspection. Children cannot delegate. Sandbox metadata describes the requested profile, not stronger permissions than the active session grants.

If named-role metadata is stale, use a fresh generic child with the exact manifest model/effort and current role prompt when the runtime supports that. If it cannot, report the dispatch limitation without choosing a different model.

Version 4 removes the old persistent CLI controller, mandatory test/evidence schemas and final-gate machinery. Do not run `native-begin`, `native-gate`, `run` or `revise-run` from an older package as a hidden prerequisite. Existing historical run files are left alone; resume the requested work using its useful plan and results in the current chat. Do not create replacement ledgers, compatibility layers or migration receipts. Save progress to a file only if the user requests it.
