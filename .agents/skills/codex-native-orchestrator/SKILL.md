---
name: codex-native-orchestrator
description: Route complex repository work across native Codex agents when explicitly invoked or authorized by the current Ultra runtime mode. Never activate from task matching in ordinary or Max mode. Use the persistent runner for DAG or resumable work.
---

# Codex Native Orchestration

## Activation: manual invocation or Ultra

Only the primary/host agent may start this workflow. Named-role agents and other delegated children execute their assigned packets without starting another Conductor, runner, or final gate.

A new run requires either of these entrypoints:

- **Manual:** The user selects **Codex Native Orchestration** in the skill/slash menu (typing `/codex` filters that menu), or sends a direct `$codex-native-orchestrator` invocation with a task. Questions, quotations, screenshots, document references, and requests to inspect or edit this skill are not invocations of its orchestration workflow.
- **Ultra:** The latest trusted runtime/developer `<multi_agent_mode>` instruction states **"Proactive multi-agent delegation is active"**, and the current repository task materially benefits from independent exploration, implementation, testing, research, or review. This is the Ultra runtime bridge; simple questions and small localized changes stay in the host session.

For the Ultra entrypoint, start automatically without asking the user to select this skill or type its name. Keep the host's selected Ultra mode; only the delegated roles use the fixed efforts below.

Ordinary/Max task matching, full access, a global default effort, the word `ultra` in user or document text, available agent tools, and earlier skill use do not authorize automatic activation. A later runtime instruction returning to explicit-request-only mode revokes Ultra activation for new tasks. Unknown mode does not authorize automatic activation.

Keep `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. The lightweight [global activation instructions](references/activation.md) conditionally load this file; the skill must not be injected for ordinary task matching.

If both entrypoints apply, start one run through one execution mode. Continue an existing, unfinished run for the same authorized objective through its recorded state and entrypoint, including after leaving Ultra; do not start another Conductor. Completed/cancelled runs and earlier conversation history do not authorize an independent new task. Re-evaluate the entrypoints for every independent new task.

Use this skill for repository tasks where independent exploration, implementation, testing, research, or review materially improves the result. Keep small localized changes in the host session. The role topology below is fixed for this installation; do not substitute a model or effort for any named role.

## Quality-first workflow

Use one independent Conductor startup through `native-begin` or `run` before detailed execution. The host owns decisions, integration and delivery. Never start both modes or a second Conductor for the same task. Update the agreed plan with newly discovered facts; do not seek repeated planning approval. Small localized work can remain in the host after startup.

Choose bounded roles with [routing](references/routing.md). Prefer Luna / max for well-specified repetitive work: scout collects facts, mechanic follows an explicit change recipe, and check_runner executes predefined commands. Sol / max handles planning, semantic decisions, implementation, test authoring, review and finding validation. Reserve Astra / xhigh for consequential design review, difficult root-cause diagnosis and the final evidence gate. Escalate on ambiguity or unexpected failure; small edits with unclear behavior are not automatically simple. Apply the [quality workflow](references/quality-workflow.md): requirement-derived acceptance tests, independent execution and code review, evidence-based finding adjudication, and bounded repairs. Every completed authorized orchestration run ends with Reviewer then a controller-isolated Guardian. Each verdict binds one exact evidence revision. A rejected revision can be repaired and rechecked under the same objective; an unchanged revision cannot be resubmitted for a different verdict.

## Fixed role topology

| Role | Model | Effort | Requested sandbox profile |
| --- | --- | --- | --- |
| `conductor` | `gpt-6.1-sol` | `max` | read-only |
| `explorer` | `gpt-6.1-sol` | `max` | read-only |
| `researcher` | `gpt-6.1-sol` | `max` | read-only |
| `worker` | `gpt-6.1-sol` | `max` | workspace-write |
| `design_critic` | `gpt-6-astra` | `xhigh` | read-only |
| `test_author` | `gpt-6.1-sol` | `max` | workspace-write |
| `tester` | `gpt-6.1-sol` | `max` | workspace-write |
| `reviewer` | `gpt-6.1-sol` | `max` | read-only |
| `finding_validator` | `gpt-6.1-sol` | `max` | read-only |
| `debugger` | `gpt-6-astra` | `xhigh` | read-only |
| `guardian` | `gpt-6-astra` | `xhigh` | read-only |
| `scout` | `gpt-6-luna` | `max` | read-only |
| `mechanic` | `gpt-6-luna` | `max` | workspace-write |
| `check_runner` | `gpt-6-luna` | `max` | workspace-write |

The bundled JSON manifest is the sole model/effort authority. Controller dispatch, deployed TOMLs, schemas and role prompts must agree. Never substitute or silently fall back. The host model and effort remain whatever the user selected; do not inspect or pin them to any role. Profile sandbox fields are advisory and do not override the parent session. Effective permissions and runtime are observed separately; report unknown values as `unknown`.

Native dispatch uses fresh named-role agents. If cached role metadata is stale, request a fresh generic agent with the exact manifest model/effort and role prompt, bounded contract and owned paths. If the exact settings cannot be requested, stop dispatch and report the limitation. Existing children retain their original settings. This fallback cannot replace the controller-isolated Guardian.

## Execution and recovery

Use native orchestration for bounded work. Use the persistent runner for explicit DAG/batch/resume/persistence, three or more dependent nodes, two or more independent parallel writers, or cross-turn recovery. File count alone is not a trigger. Honor `runner on`, `runner off`, `root-only`, `max agents N`, and `read-only`; at most four ordinary agents run concurrently. `root-only` does not waive startup, review or final gate.

Default to one implementation writer, with a separate test-author checkout. Shared contracts, schemas and state must be ordered; disjoint path names alone do not prove independence. Runner writers own non-overlapping paths and never stage/commit: the controller verifies and commits. Tester and check_runner nodes integrate no files; generated outputs run in disposable private clones with tracked-source and Git checks. A global `read-only` request disables writable verification too.

Run the controller from this skill directory:

```sh
python3 scripts/codex_native_orchestrator.py --repo /absolute/repository doctor
```

Follow [delegation contracts](references/delegation-contract.md), [runner/recovery](references/runner-and-recovery.md), [evidence](references/evidence-and-review.md) and [version-bound gates](references/guardian-gate.md). Runs remain under `CODEX_HOME/astra-orchestrator/runs`; state records package version, manifest plus prompt/controller fingerprint, baseline and evidence revision. Older runs remain inspectable and cannot silently resume under changed rules. Use the preserved old package to recover old work or explicitly start a newly planned run; never rewrite old hashes to make it pass.

Two candidate implementations are an opt-in experiment in separate native checkouts: compare the same requirements and tests, select one, and integrate only that candidate. The ordinary DAG must reject candidate fields because its writers are additive. Do not enable this by default without the [evaluation protocol](references/evaluation.md).
