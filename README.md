# Harness Orchestration / 多 Harness 角色编排

Plan → implement → inspect → fix or deliver · Codex · ZCode · Qoder

计划 → 执行 → 检查 → 有问题修改、没问题放行 · Codex · ZCode · Qoder

[中文](#中文) · [English](#english)

## 中文

这个仓库提供三个**独立安装、独立选择**的 Codex skill、一套 [ZCode 角色编排包](zcode/README.md)，以及包含 14 个角色和手动 skill 的 [Qoder 插件](qoder/README.md)。仓库现名为 [AshWood97/harness-orchestration](https://github.com/AshWood97/harness-orchestration)，曾用名为 `codex-three-paths`、`codex-zcode-orchestration`，便于后续继续接入其他 Harness；现有 Codex skill 标识、安装路径和 ZCode 入口保持不变。安装三个 Codex skill 后，技能菜单仍显示三个选项，按任务选择即可。

| Skill | 用途 |
| --- | --- |
| [Codex Native Orchestration](.agents/skills/codex-native-orchestrator/SKILL.md) | 由规划者评估任务并按需选择角色，完成实现与检查，尽量少做额外测试。 |
| [Codex External Provider](.agents/skills/codex-external-provider/SKILL.md) | 在**会话启动时**已配置外部 Responses API provider 的前提下，检查当前会话及原生 agent 的路由。 |
| [Codex Harness Bridge](.agents/skills/codex-harness-bridge/SKILL.md) | 把一个有明确边界的任务交给已配置的独立编码 CLI，并由当前 Codex 会话检查结果。 |

三者可以组成工作流程，但不会自动混用模型或偷偷切换 provider：按当前任务选一个 skill；如需在同一工作流程里调用独立 CLI，再明确使用 Harness Bridge。Native 与 External 的会话路由条件不同，不能把 External 当作在已启动的 Native 会话中切换 provider 的按钮。**完全混合路由是未来方向，目前未实现。**

### 安装

在 Codex 中使用内置 `$skill-installer`，请它从本仓库一次安装下面三个路径：

```text
仓库：AshWood97/harness-orchestration
路径：.agents/skills/codex-native-orchestrator
      .agents/skills/codex-external-provider
      .agents/skills/codex-harness-bridge
```

安装器将三个目录分别放入 `$CODEX_HOME/skills/`（默认 `~/.codex/skills/`）。在下一轮对话中，从技能菜单选一个即可；也可以明确写 `$codex-native-orchestrator`、`$codex-external-provider` 或 `$codex-harness-bridge`。如已有同名 skill，先检查现有安装，避免覆盖个人改动。

建议使用 Python 3.11 或更新版本；External 的预检及测试要求至少 3.11。Native 的 skill 安装和命名 agent 配置是两步：安装器只安装 skill；按下方说明部署固定子代理角色后，再启动新会话。当前 Codex 主会话只负责协调，不属于技能配置的角色映射；调用技能不会改变用户选择的主会话模型。External 的 provider、模型目录和凭据只放在个人配置及环境变量中，参照[示例](.agents/skills/codex-external-provider/examples/user-config.example.toml)和[设置说明](.agents/skills/codex-external-provider/references/provider-setup.md)。Harness Bridge 的私有配置从[示例](.agents/skills/codex-harness-bridge/config.example.json)创建，参照[设置说明](.agents/skills/codex-harness-bridge/references/setup.md)；仅安装要用的 CLI。

#### Native 角色与流程

默认流程是 **充分考虑的计划 → 最小实现 → 一次针对需求的检查 → 有问题修改、没问题放行**。简单任务留在主会话；复杂任务只分派确实需要完成的部分。检查由主会话或一个 reviewer 负责，不重复做同一轮检查；修复后只看修复和直接影响。用户只要求 Review 时保持只读。

| 角色 | 模型 | 推理强度 |
| --- | --- | --- |
| conductor、explorer、researcher、worker、reviewer、finding_validator、test_author、tester | `gpt-6.1-sol` | `max` |
| scout、mechanic、check_runner | `gpt-6-luna` | `max` |
| design_critic、debugger、guardian | `gpt-6-astra` | `xhigh` |

保留 14 个角色的模型。多角色任务先由 **Conductor 评估并从全部角色中选择实际需要的角色**，主会话负责派遣；简单任务和 root-only 留在主会话。design_critic、finding_validator、guardian、test_author、tester、check_runner 都可按具体需要选择，**不要求用户逐个点名，也不要求每次调用全部角色**。

尽量少做额外测试：先读源码和结果、复用已有观察；重要行为无法据此判断时才安排最小针对性测试，优先现有用例，确有缺口才补新测试。专项审查须对应一个尚未解决且影响结果的具体问题，不能重复普通 review。默认一个实现者、最多按需四个子智能体；不默认跑全套测试、构建矩阵、A/B 或连续审核。用户明确的不测试、只读等限制仍优先遵守。

默认禁止 hash/checksum/指纹/签名与额外产物。仅当用户明确要求发布校验、去重、缓存命中或对照已知摘要做拒绝，且结果实际用于该操作时才计算。超出用户任务范围的动作先问一句“我想加 X，因为 Y，是否允许？”，等答复再做。详见[执行规则](.agents/skills/codex-native-orchestrator/SKILL.md)。

将 `.agents/skills/codex-native-orchestrator/roles/*.toml` 放到个人 `CODEX_HOME/agents`，把清单中的 `config_values` 合并到 `CODEX_HOME/config.toml`，保留其他设置和用户选择的主模型。不要追加重复 TOML 键。开始新会话加载更新后的提示词。

#### 技能与 Ultra 入口

从技能菜单选择 **Codex Native Orchestration** 或直接用 `$codex-native-orchestrator` 加任务，手动启用。普通/Max 不按任务内容自动启用。

Ultra 自动入口仅以当前受信 runtime/developer 的 **“Proactive multi-agent delegation is active”** 指令为准；适合分工的项目任务自动加载技能，简单任务仍留在主会话。文字 `ultra`、截图、完整权限和历史使用均不算启用信号。主会话模型和深度不变。两种入口使用完全相同的按需选择规则：多角色任务由 Conductor 评估，主会话派遣所需角色，没有固定的 Tester → Reviewer → Guardian 流水线。

安装后可将带标记的入口合并到个人 `CODEX_HOME/AGENTS.md`，保留其他规则；不加 `--apply` 时只显示是否需要更新：

```sh
python /absolute/path/to/CODEX_HOME/skills/codex-native-orchestrator/scripts/install_activation.py --apply
```

安装脚本不计算摘要，不生成备份凭据或日志。

**v4 移除了旧持久 CLI runner、哈希证据机制和自动最终 gate**，以及只服务于这些机制的 schema/测试。旧 `native-begin`、`native-gate`、`run`、`revise-run` 等控制器命令不再提供；工作直接由原生 agent 工具协调。旧运行记录不改动，续接时复用已有计划和结论，不迁移、不重复执行，也不默认生成新账本。

### ZCode 角色编排

[ZCode 安装说明](zcode/README.md)提供七个自定义角色，配合 Explore 和 general-purpose，模型保持 **Gemini 3.8 Flash / high**。主 Agent 承担规划者职责，采用相同的计划、执行、检查流程；可自行选择必要的测试或专项角色，尽量少做额外测试，无需用户逐个点名。

安装器合并带标记的工作流并保留个人规则，不计算前后 hash 或生成备份凭据。模型的 provider 标识由使用者提供；内置角色仍在 ZCode 设置中配置。文档插件角色不属于本次代码编排。

### Qoder 角色编排

[Qoder 安装说明](qoder/README.md)提供 `harness-orchestration` 桌面插件：完整 14 个角色和一个手动启用的 skill。角色省略 `model` 以沿用当前对话模型，只读角色没有 Bash/Edit/Write，保留默认一个写入者、最多四个子角色、一个检查负责人和按需最小检查的规则。

在 Qoder CN 中通过 **Extensions → Plugins → Add Plugin → 上传 Plugin** 导入 ZIP；ZIP 根目录须直接包含 `.qoder-plugin/plugin.json`。创建 **Harness Orchestration** 自定义协调 Agent、选择本插件，并粘贴 [协调指令](qoder/coordinator-instructions.txt)。显式选择该协调 Agent、同名 skill 或明确要求使用编排即可启用。14 角色是可选目录，Team 最多 5 个成员；按任务选用角色。打包命令及中英文完整步骤见 [Qoder README](qoder/README.md)。

### 公开仓库与验证范围

本仓库只包含源码、文档、占位符示例和测试。不要提交 API key、真实 provider URL、个人 `config.toml`、私有模型目录、任务 brief、运行日志或报告。External 的预检需要可信的运行时 provider/model 身份；配置检查本身不证明远端请求的实际路由。Harness Bridge 的适配器测试使用模拟 CLI，不代表所有真实 CLI 版本或服务端都已验证。DeepSeek Harness 仍是实验性支持。

Native/ZCode/Qoder 的日常任务和仓库改动不自动触发测试矩阵。现有安装器测试保留供维护者明确选择执行；External Provider 与 Harness Bridge 的原有 CI 仅在它们自身路径发生变化时运行。见[变更记录](CHANGELOG.md)。

## English

This repository contains three Codex skills that are **installed and selected independently**, a [ZCode role orchestration package](zcode/README.md), and a [Qoder plugin](qoder/README.md) with 14 roles and a manual skill. The repository is now [AshWood97/harness-orchestration](https://github.com/AshWood97/harness-orchestration), previously `codex-three-paths` and `codex-zcode-orchestration`, leaving room for future harness adapters. Existing Codex skill identifiers, installation paths, and ZCode entrypoints are preserved. Installing the three Codex skills adds three entries to the picker; select the one needed for the task.

| Skill | Purpose |
| --- | --- |
| [Codex Native Orchestration](.agents/skills/codex-native-orchestrator/SKILL.md) | Let the planner select necessary native roles for implementation and inspection, minimizing extra tests. |
| [Codex External Provider](.agents/skills/codex-external-provider/SKILL.md) | Check routing for a Codex session and native agents **started with** a configured external Responses API provider. |
| [Codex Harness Bridge](.agents/skills/codex-harness-bridge/SKILL.md) | Send one bounded job to a configured coding CLI and review its evidence from the current Codex session. |

The skills can participate in one workflow, but they do not automatically mix models or switch providers. Select a skill for the current task and explicitly invoke Harness Bridge if a bounded subprocess is useful. Native and External have different session routing requirements; External cannot change the provider of a session that has already started. **Fully mixed routing is a possible future enhancement, not a current feature.**

### Install

In Codex, ask the built-in `$skill-installer` to install these three paths from this repository:

```text
Repository: AshWood97/harness-orchestration
Paths: .agents/skills/codex-native-orchestrator
       .agents/skills/codex-external-provider
       .agents/skills/codex-harness-bridge
```

The installer places each directory in `$CODEX_HOME/skills/` (default `~/.codex/skills/`). On the next turn, select one from the skill picker, or invoke `$codex-native-orchestrator`, `$codex-external-provider`, or `$codex-harness-bridge` directly. Inspect any existing skill with the same name before updating it so local changes are preserved.

Python 3.11 or newer is recommended; External preflight and tests require at least 3.11. Installing the Native skill and configuring named agents are separate steps: the installer adds the skill, while the deployment below installs the fixed subagent roles. The current Codex session coordinates work but is not one of the skill's named roles; invoking the skill does not change its selected model. Start a new session after deployment. Keep External provider settings, model catalogs, and credentials in user configuration and environment variables, using the [example](.agents/skills/codex-external-provider/examples/user-config.example.toml) and [setup guide](.agents/skills/codex-external-provider/references/provider-setup.md). Create a private Harness Bridge configuration from its [example](.agents/skills/codex-harness-bridge/config.example.json) and [setup guide](.agents/skills/codex-harness-bridge/references/setup.md); install only the CLIs you plan to use.

#### Native roles and workflow

Use **plan → implement → inspect once → fix concrete issues or deliver**. Understand the requirements and relevant source before editing. Keep simple work in the host and delegate only necessary parts of the requested implementation. One owner, either the host or reviewer, inspects the result and directly affected callers. After a repair, inspect that repair and its effects; reuse unchanged conclusions. Review-only requests never authorize edits.

| Roles | Model | Effort |
| --- | --- | --- |
| conductor, explorer, researcher, worker, reviewer, finding_validator, test_author, tester | `gpt-6.1-sol` | `max` |
| scout, mechanic, check_runner | `gpt-6-luna` | `max` |
| design_critic, debugger, guardian | `gpt-6-astra` | `xhigh` |

All 14 role models are preserved. For multi-role work, **Conductor assesses the task and selects any roles it needs**, and the host dispatches them. Simple work and root-only remain in the host. Specialist and test roles do not require the user to name them. Select a useful subset; do not run the entire catalog.

Minimize extra testing: inspect source/results and reuse existing observations first. Choose the smallest targeted check only for important unresolved behavior, preferring existing cases and writing new tests only for a concrete gap. A specialist review must answer a distinct material question, not repeat ordinary review. Default to one writer and at most four children as needed. No routine suites, build matrices, experiments or multi-round approval chains. Explicit user prohibitions still take precedence.

Do not calculate hashes, checksums, fingerprints or signatures unless the user explicitly requests published checksums, deduplication, cache-hit decisions or known-digest rejection and the result serves that operation. Do not create extra files or logs for traceability. Ask before a scope-expanding action, then wait. See the [skill](.agents/skills/codex-native-orchestrator/SKILL.md).

Place the role TOMLs in personal `CODEX_HOME/agents` and merge the manifest's `config_values` into personal `CODEX_HOME/config.toml`. Preserve unrelated settings and the user's host model; avoid duplicate keys. Start a new session to load updated prompts.

#### Manual and Ultra entrypoints

Keep `allow_implicit_invocation: false`. Select **Codex Native Orchestration** in the skill menu or directly invoke `$codex-native-orchestrator` with a task. Ordinary/Max task matching does not activate it.

The Ultra entrypoint requires the current trusted runtime/developer instruction **"Proactive multi-agent delegation is active"**. It loads the skill for suitable repository work while simple tasks remain in the host. Text saying `ultra`, screenshots, permissions, saved settings and past usage are not activation. Both entrypoints use the same planner-led selection: Conductor assesses multi-role work, the host dispatches the necessary roles, and no fixed Tester/Reviewer/Guardian chain is imposed. Delegated children do not orchestrate.

Run `python /absolute/path/to/CODEX_HOME/skills/codex-native-orchestrator/scripts/install_activation.py --apply` to merge the marked personal AGENTS.md entrypoint, preserving other guidance. Omit `--apply` for a read-only check. It creates no digest, backup receipt or log.

**Version 4 removes the old persistent CLI runner, hash evidence machinery and automatic final gate**, together with their dedicated schemas/tests. The old controller commands, including `native-begin`, `native-gate`, `run` and `revise-run`, are no longer available. Coordinate work through native agent tools. Historical run files remain untouched; reuse useful plans and results without a migration layer or replacement ledger.

### ZCode role orchestration

The [ZCode package](zcode/README.md) retains seven custom roles plus built-in Explore and general-purpose, all using **Gemini 3.8 Flash / high**. The host acts as planner, selects any roles needed for concrete in-scope questions, and chooses one owner per check. It may select test or specialist roles without user naming, while minimizing extra tests and avoiding repeated review.

The installer merges marked guidance, preserves surrounding personal rules and creates no digest or backup receipt. Supply your own provider/model identifier; set built-in role models in ZCode settings. Document-plugin roles are outside this coding workflow.

### Qoder role orchestration

The [Qoder package](qoder/README.md) ships a desktop plugin named `harness-orchestration`, with all 14 roles and one manually activated skill. Agent `model` fields are omitted to follow the conversation model. Read-only roles have no Bash/Edit/Write tools. The workflow defaults to one writer, at most four children, one checking owner, and minimal checks for concrete unresolved questions.

Import the ZIP in Qoder CN through **Extensions → Plugins → Add Plugin → Upload Plugin**. The ZIP root must directly contain `.qoder-plugin/plugin.json`. Create a custom coordinator named **Harness Orchestration**, select this plugin, and paste the [coordinator instructions](qoder/coordinator-instructions.txt). Select that coordinator, select the skill, or explicitly ask to use orchestration to activate it. Choose necessary roles from the 14-role catalog; Team supports up to five members. See the [bilingual installation and packaging guide](qoder/README.md).

### Public repository and verification limits

This repository contains only source code, documentation, placeholder examples, and tests. Do not commit API keys, real provider URLs, personal `config.toml`, private model catalogs, task briefs, run logs, or reports. External preflight requires trusted runtime provider/model identity; a configuration check alone does not prove remote request routing. Harness Bridge adapter tests use stub CLIs and do not establish compatibility with every live CLI version or service. DeepSeek Harness support remains experimental.

Native/ZCode/Qoder tasks and repository changes do not automatically trigger test matrices. Existing installer tests remain available for an explicitly chosen maintenance run. External Provider and Harness Bridge retain CI only for changes to their own paths. See the [changelog](CHANGELOG.md).

## License

MIT. See [LICENSE](LICENSE).
