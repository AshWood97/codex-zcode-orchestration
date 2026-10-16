# Evaluation protocol

Installation checks and deterministic controller tests are not measurements of coding quality. Keep model assignments fixed at the user's chosen values. Do not claim a local quality gain from external benchmarks or mocked model responses.

## Staged experiment

Use 12 non-held-out tuning tasks (3 bug fixes, 3 features, 3 cross-module changes, 3 follow-up changes). Tune only task contracts/routing and test validity. Then freeze prompts/config and evaluate 24 unseen tasks (6 per category), three repetitions per arm. For Codex compare previous setup, new models with previous workflow, new workflow, and a strong single-agent control under the same explicit budget. ZCode uses Gemini 3.8 Flash in every arm; compare old versus new workflow and a single-agent control. Keep evaluator/hidden tests independent and avoid leaking held-out outcomes back into prompts during the run.

Primary: hidden functional correctness, escaped severe defects, regression rate, acceptance-test validity, quality on a follow-up change. Secondary: reviewer false positives/false negatives, erroneous refutations, unnecessary changes, repair waves, integration failures, duration and tokens. Always publish denominators, task mix, repeats, version hashes and uncertainty; aggregate averages alone can hide serious failures. A blind scorer sees candidate artifacts and requirements, not role/model labels.

## Required adversarial scenarios

1. Wrong acceptance assertion: appeal with requirement evidence; never silently weaken it.
2. Worker attempts to skip/weaken a frozen test: reject ownership/diff.
3. True finding wrongly dismissed, and a valid singleton finding: keep unresolved/confirmed until counterevidence.
4. Components pass separately but fail together: final integrated verification detects it.
5. Mock replaces the core behavior: test-quality review rejects the purported coverage.
6. Test not run, environment failure, or stale results: no successful verification.
7. Model unavailable or effective configuration differs: no silent model fallback.
8. Interrupted writer/recovery: no duplicate writer or lost evidence.
9. Gate revise followed by unchanged receipt: no new verdict request.
10. Real repair plus fresh bound tests: new review/gate, old evidence archived.
11. Test run creates cache/build output: allowed in disposable clone, never integrated.
12. Test run mutates tracked code/config: reject verification.

Deterministic tests can establish controller invariants for scenarios 2, 4, 6-12. Scenarios requiring semantic judgment (wrong assertions, genuine/refuted findings, mock validity) require real task executions and human/independent ground truth. Do not mark them passed merely because a role prompt contains the rule. No default candidate-search expansion until it wins a held-out comparison without increasing serious defects.
