# Changelog

## 3.3.0 — 2026-10-16

The repository is now **Codex + ZCode Orchestration**, renamed from `codex-three-paths` to `codex-zcode-orchestration`. Existing Codex skill names remain stable. This release combines the local quality-workflow upgrades with the repository's existing Windows support.

### Codex Native

- Expand to 14 bounded roles: eight GPT-6.1 Sol/max, three GPT-6 Luna/max, and three GPT-6 Astra/xhigh. Default subagents use Sol/max; the host model stays user-selected.
- Add independent design criticism, acceptance-test authoring, finding validation and root-cause debugging. Keep independent execution, code review and the isolated final Guardian gate.
- Route clear repetitive work to scout, mechanic and check_runner. Require explicit edit recipes or commands; ambiguity returns to the appropriate Sol role.
- Run generated test/build output in disposable verification clones. Reject tracked source or protected Git metadata changes; keep downstream Sol verification for writer plans.
- Bind evidence to the candidate and package fingerprint. Permit bounded repair revisions with fresh verification/review; reject attempts to get a new verdict on unchanged evidence. Require debugger evidence after two failed fixes of the same issue; cap repairs at five waves.
- Keep alternative candidates out of additive DAG integration. Candidate comparisons remain explicit experiments with a shared acceptance basis.
- Preserve the upstream Windows process launch, stdin prompt transport, process-tree cleanup, lock probing, sandbox-accessible workspaces and activation installer. Apply the accessible workspace policy to disposable verification too, and preserve baseline/detailed prompt context in verification packets.
- Include a controlled evaluation protocol. Deterministic tests are not evidence of coding-quality improvement or measured quota savings.

### ZCode

- Publish seven custom role templates and the host AGENTS.md workflow, alongside instructions for built-in Explore and general-purpose.
- Use Gemini 3.8 Flash/high throughout. Substitute the user's provider/model identifier during installation instead of publishing account-specific state.
- Add a preview-first installer with conflict checks, backups, atomic replacement and rollback on failure. Preserve personal guidance outside the managed block.
- Separate test design, execution and review; document test appeals, evidence expiry, finding adjudication, bounded repair and host-enforced isolation.

### Distribution

- Update bilingual installation and role documentation for both tools.
- Retain the independent External Provider and Harness Bridge skills and their Windows fixes.
- Extend the Linux/Windows Python 3.11/3.12 CI matrix to include the ZCode installer tests.

本次发布覆盖本轮 Codex 质量流程、Luna 分工、Sol 主流程和 ZCode 角色升级。没有发布个人配置、provider UUID、API key、任务日志或本机回滚备份。
