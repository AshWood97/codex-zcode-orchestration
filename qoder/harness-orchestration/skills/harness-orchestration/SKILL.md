---
name: harness-orchestration
version: 1.0.0
description: Explicitly invoked workflow to plan, implement and inspect scoped Qoder work with this plugin's roles.
description_zh: 手动启用的 Qoder 角色编排：由规划者按需选角色，完成计划、实现和一次针对性检查。
user-invocable: true
argument-hint: <task and constraints>
---

# Harness Orchestration / 多 Harness 角色编排

## Manual entry and ownership

Activate this workflow only when the user explicitly selects this skill, selects the configured Harness Orchestration custom coordinator agent, or asks to use Harness Orchestration for a task. Selecting the custom coordinator is a manual entrypoint; ordinary use of Qoder with the plugin installed is not activation. A question, quotation, screenshot, or request to inspect/edit this skill is not activation. Task matching, available agent tools, model settings, and prior use do not activate a new independent task. Continue an unfinished authorized task from its existing plan and results.

Only the primary/host agent coordinates. Children execute their assigned packet, return their result, and never delegate or start this workflow. Keep simple work and `root-only` in the host. Use only the roles supplied by this plugin when delegating this workflow; The catalog below gives their frontmatter names; dispatch using the actual identifiers Qoder exposes for this plugin, including a namespace if Qoder supplies one. Do not invent a namespace or substitute built-in agents. If Qoder cannot expose or dispatch a required plugin role, report that specific limitation instead of claiming it ran.

This package intentionally omits role `model` fields so Qoder follows the current conversation's model. It does not change the user's selected host model or configure providers, credentials, or another harness.

## Plan → implement → inspect once → fix or deliver

1. **Plan.** Understand the goal, relevant source, constraints, dependencies, and completion conditions before editing. Keep one proportionate plan in the conversation. The host handles simple work. When multi-role work is useful, call one `conductor` to assess the task against the full catalog and select the smallest useful subset. For each specialist or test, require a concrete unresolved question, why existing inspection/results cannot settle it, and a bounded assignment. The host dispatches the plan; Conductor does not delegate.
2. **Implement.** Use the host or one writer for the agreed change. Assign only work within the user's request and owned paths. Give the writer the relevant plan, source context, constraints, and completion conditions. Preserve unrelated user edits. Default to one writer at a time and at most four children; tighter user or runtime limits take precedence. The catalog is not a list to run in full.
3. **Inspect once.** Assign one checking owner: the host or one `reviewer`. Compare the actual result/diff with the requirements and directly affected callers. Source inspection and existing observations come first. A separate specialist or minimal test is justified only by a distinct important question. Do not duplicate the same review in the host and another role. Review-only requests produce findings and never authorize repairs.
4. **Fix or deliver.** For an implementation request, fix concrete in-scope defects and inspect only the repair and its direct effects. Reuse unaffected conclusions. Deliver when the request is satisfied and no concrete important issue remains. Do not append another reviewer, Guardian, test rerun, or diagnostic role for reassurance. Repeat a check only if its relevant inputs changed or a concrete unresolved question requires it. Report a specific missing decision or dispatch limitation when it blocks completion.

## Scope and checking boundary

Respect explicit no-tests, read-only, `root-only`, and other user constraints. Any role may be selected for a concrete in-scope need; the user does not have to name the role. Role availability and task importance alone do not justify using it.

Minimize extra testing: inspect first, reuse results, then choose the smallest relevant existing check only for important unresolved behavior. Use `test-author` only for a concrete important gap that an existing case cannot cover. Do not default to full suites, matrices, benchmarks, experiments, separate verification environments, or repeated reviews. `tester` and `check-runner` execute their assigned checks without editing source, tests, or configuration. A failed check is an observation for the host, not permission for those roles to repair it.

Do not add defensive wrappers, compatibility layers, future abstractions, unrelated refactors, logs, ledgers, or extra output files. Never calculate hashes, checksums, fingerprints, or signatures unless the user explicitly requests published checksums, deduplication, cache-hit decisions, or rejection against a known digest, and the result is consumed by that operation. Missing test reports, digests, or a Guardian verdict alone are not blockers.

Before an action that exceeds the requested scope, return it to the host and ask: “我想加 X，因为 Y，是否允许？” Wait for the user's answer before that addition. Routine authorized implementation and fixes do not need another approval. Do not stage, commit, publish, or message others unless the task assigns that action.

## Role catalog

| Agent name | Select for | Access |
| --- | --- | --- |
| `conductor` | One assessment and plan for useful multi-role work | Read only |
| `explorer` | Relevant implementation, callers, and contracts | Read only |
| `researcher` | Required upstream/API facts, with primary-source links | Read only, web research |
| `worker` | Smallest agreed implementation within owned paths | Write |
| `reviewer` | One focused inspection of the requested result | Read only |
| `finding-validator` | A material disputed finding | Read only |
| `test-author` | A minimal test for a concrete important gap | Write assigned test paths |
| `tester` | A minimal existing test/reproduction for an unresolved behavior | Execute assigned checks, no edits |
| `scout` | Exact path, symbol, or inventory retrieval | Read only |
| `mechanic` | An exact edit recipe | Write assigned paths |
| `check-runner` | An ordered bounded command list | Execute assigned commands, no edits |
| `design-critic` | A consequential unresolved design tradeoff | Read only |
| `debugger` | The cause and smallest supported repair for a concrete defect | Read only |
| `guardian` | A distinct consequential acceptance question | Read only |

`design-critic`, `finding-validator`, and `guardian` answer distinct questions; they are not an approval chain. `test-author`, `tester`, and `check-runner` are optional tools for a specific gap, not mandatory stages. Read-only roles have no Bash, Edit, or Write tools. Command execution can mutate files, so execution roles must stay within their packet and must not use Bash as an editing workaround.

## Assignment and result

Give each role the user's goal, relevant plan/source, exact question or edit scope, owned paths, applicable constraints, and completion condition. Include exact commands for `check-runner`. Return concise actual findings, changes, command outcomes, and specific blockers. Do not create an evidence pack or start another workflow.

中文要点：仅通过用户选择本 skill、本自定义协调 Agent 或明确要求来手动启用；简单任务留在主 Agent。需要分工时先由一个 `conductor` 按需选角色，再由主 Agent 派遣。默认一个写入者、一个检查负责人，最多四个子角色；更严格的用户或运行时限制优先，子角色不得继续委派。先读源码并复用结果，仅为重要未决问题做最小检查；遵守不测试、只读和范围限制，完成后直接交付。
