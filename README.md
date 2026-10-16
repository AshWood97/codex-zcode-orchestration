# Codex + ZCode Orchestration / Codex 与 ZCode 多角色编排

Quality-first role orchestration for Codex and ZCode · Native agents · External providers · Harness delegation

Codex 与 ZCode 的代码质量优先编排 · 原生 agent · 外部 provider · 独立 harness

[中文](#中文) · [English](#english)

## 中文

这个仓库提供三个**独立安装、独立选择**的 Codex skill，以及一套 [ZCode 角色编排包](zcode/README.md)。仓库由 `codex-three-paths` 更名而来，原有三个技能标识和安装路径保持不变。安装全部三个后，技能菜单仍显示三个选项；使用时直接选所需的那个，不会再出现“总入口”或第二次模式选择。

| Skill | 用途 |
| --- | --- |
| [Codex Native Orchestration](.agents/skills/codex-native-orchestrator/SKILL.md) | 使用 Codex 原生 agent 协调任务；需要批量、依赖或跨轮恢复时使用持久化 runner。 |
| [Codex External Provider](.agents/skills/codex-external-provider/SKILL.md) | 在**会话启动时**已配置外部 Responses API provider 的前提下，检查当前会话及原生 agent 的路由。 |
| [Codex Harness Bridge](.agents/skills/codex-harness-bridge/SKILL.md) | 把一个有明确边界的任务交给已配置的独立编码 CLI，并由当前 Codex 会话检查结果。 |

三者可以组成工作流程，但不会自动混用模型或偷偷切换 provider：按当前任务选一个 skill；如需在同一工作流程里调用独立 CLI，再明确使用 Harness Bridge。Native 与 External 的会话路由条件不同，不能把 External 当作在已启动的 Native 会话中切换 provider 的按钮。**完全混合路由是未来方向，目前未实现。**

### 安装

在 Codex 中使用内置 `$skill-installer`，请它从本仓库一次安装下面三个路径：

```text
仓库：AshWood97/codex-zcode-orchestration
路径：.agents/skills/codex-native-orchestrator
      .agents/skills/codex-external-provider
      .agents/skills/codex-harness-bridge
```

安装器将三个目录分别放入 `$CODEX_HOME/skills/`（默认 `~/.codex/skills/`）。在下一轮对话中，从技能菜单选一个即可；也可以明确写 `$codex-native-orchestrator`、`$codex-external-provider` 或 `$codex-harness-bridge`。如已有同名 skill，先检查现有安装，避免覆盖个人改动。

建议使用 Python 3.11 或更新版本；External 的预检及测试要求至少 3.11。Native 的 skill 安装和命名 agent 配置是两步：安装器只安装 skill；按下方说明部署固定子代理角色后，再启动新会话。当前 Codex 主会话只负责协调，不属于技能配置的角色映射；调用技能不会改变用户选择的主会话模型。External 的 provider、模型目录和凭据只放在个人配置及环境变量中，参照[示例](.agents/skills/codex-external-provider/examples/user-config.example.toml)和[设置说明](.agents/skills/codex-external-provider/references/provider-setup.md)。Harness Bridge 的私有配置从[示例](.agents/skills/codex-harness-bridge/config.example.json)创建，参照[设置说明](.agents/skills/codex-harness-bridge/references/setup.md)；仅安装要用的 CLI。

#### Native 固定编排与部署

| 角色 | 模型 | 推理强度 |
| --- | --- | --- |
| Sol 主流程：conductor、explorer、researcher、worker、test_author、tester、reviewer、finding_validator | `gpt-6.1-sol` | `max` |
| Luna 明确重复工作：scout、mechanic、check_runner | `gpt-6-luna` | `max` |
| Astra 专项与验收：design_critic、debugger、guardian | `gpt-6-astra` | `xhigh` |

共 14 个角色。默认子智能体也是 Sol/max。明确搜索交给 scout，按既定规则的重复编辑交给 mechanic，预定命令交给 check_runner；遇到歧义分别交回 explorer、worker、tester。Luna 不替代测试覆盖判断或最终验收。重要设计才调用 design_critic；同一问题两次修复失败或因果难明时调用 debugger。

Conductor 是每次授权运行的独立启动阶段。测试设计、测试执行和代码审查相互独立；实质发现使用 confirmed/refuted/unresolved 三态核验。Tester/check_runner 可以在隔离副本生成缓存和构建输出，但不能改变受跟踪源码、测试或 Git 元数据，也不整合输出。每个 writer 仍需下游 Sol Tester 验证。Reviewer 通过后运行隔离的 Guardian；结论绑定准确的代码、测试和配置版本，修复后更新证据再验收，同一版本不能反复要求改判。最多五轮修复。模型或配置不符时停止派遣。详见[质量流程](.agents/skills/codex-native-orchestrator/references/quality-workflow.md)及[路由规则](.agents/skills/codex-native-orchestrator/references/routing.md)。

把本仓库 `.agents/skills/codex-native-orchestrator/roles/*.toml` 的 14 个配置放入个人 `CODEX_HOME/agents`，并将清单中的 `config_values` 合并到个人 `CODEX_HOME/config.toml`。这些值仅配置子代理，不包含全局 `model` 或 `model_reasoning_effort`。不要覆盖配置文件中的其他设置或追加重复的 TOML 键。从本仓库检出目录运行检查命令；已运行的会话和 agent 不会自动切换模型。

```sh
python3 .agents/skills/codex-native-orchestrator/scripts/codex_native_orchestrator.py --repo "$PWD" doctor
```

Native 的独立 Codex CLI 会沿用显式代理环境变量；在 macOS 上，缺少这些变量时自动读取已启用的系统 HTTP/HTTPS 代理。输出留档和超时、中断清理详见[恢复说明](.agents/skills/codex-native-orchestrator/references/runner-and-recovery.md)。

#### Ultra 自动入口

选择 Codex 的 **Ultra** 思考模式后，适合分工的复杂项目任务会自动进入这套编排，无需再手动选择技能。普通模式和 Max 仍通过技能菜单或 `$codex-native-orchestrator` 手动启动；简单 Ultra 问题仍由主会话处理。主会话保留用户选择的 Ultra，固定模型和思考深度仅用于各个子角色。

安装技能和 14 个角色后，运行下面的命令，将带标记的入口规则合并到个人 `CODEX_HOME/AGENTS.md`。脚本保留其他说明，更新前备份，并使用实际安装路径；不指定 `--apply` 时只检查。

```sh
python /absolute/path/to/CODEX_HOME/skills/codex-native-orchestrator/scripts/install_activation.py --apply
```

启动新会话后生效。自动入口以当前运行时的主动委派指令为准，不以文档中的 `ultra` 字样或保存的默认设置为准。可用 `codex -c 'model_reasoning_effort="ultra"' debug prompt-input` 检查当前客户端发出的模式指令；该命令无需模型调用。

Windows 默认安装的新任务会把隔离代码副本放在 `~/Documents/Codex/NativeOrchestrator/workspaces/RUN_ID`，以供只读沙箱访问；私有状态与日志仍位于 `CODEX_HOME/astra-orchestrator`。历史运行路径保持可读。

### ZCode 角色编排

[ZCode 安装说明](zcode/README.md)提供七个自定义角色：code-reviewer、test-verifier、design-critic、test-author、finding-validator、debugger、docs-researcher。配合内置 Explore 和 general-purpose，共九个代码角色，统一使用 **Gemini 3.8 Flash / high**。文档插件自带的 visual-judge 不属于这套代码角色。

安装器默认只预览，实际安装时备份旧文件、合并带标记的 AGENTS.md 工作流，并保留个人规则。模型的 provider 标识由使用者提供，不分发本机账号状态。两个内置角色在 ZCode 设置中选择相同模型。ZCode 的隔离、版本绑定和修复上限由主 Agent 按规则执行；它没有复用 Codex 的持久控制器或独立 Guardian 进程。

### 公开仓库与验证范围

本仓库只包含源码、文档、占位符示例和测试。不要提交 API key、真实 provider URL、个人 `config.toml`、私有模型目录、任务 brief、运行日志或报告。External 的预检需要可信的运行时 provider/model 身份；配置检查本身不证明远端请求的实际路由。Harness Bridge 的适配器测试使用模拟 CLI，不代表所有真实 CLI 版本或服务端都已验证。DeepSeek Harness 仍是实验性支持。

本轮新增角色、独立测试、证据修订和节省额度的分层路由；[变更记录](CHANGELOG.md)列出完整内容。控制器测试和安装测试不代表模型质量或额度节省的 A/B 实测；参照[评估协议](.agents/skills/codex-native-orchestrator/references/evaluation.md)。

运行现有测试：

```sh
for skill in codex-native-orchestrator codex-external-provider codex-harness-bridge; do
  PYTHONDONTWRITEBYTECODE=1 python3.11 -B -m unittest discover \
    -s ".agents/skills/$skill/tests" -p 'test_*.py' -q || exit 1
done
python3.11 -B -m unittest discover -s zcode/tests -p 'test_*.py' -q
```

## English

This repository contains three Codex skills that are **installed and selected independently**, plus a [ZCode role orchestration package](zcode/README.md). The repository was renamed from `codex-three-paths`; existing skill identifiers and installation paths are unchanged. Installing all three adds three entries to the skill picker. Select the skill you need once for the task; there is no umbrella skill or second mode picker.

| Skill | Purpose |
| --- | --- |
| [Codex Native Orchestration](.agents/skills/codex-native-orchestrator/SKILL.md) | Coordinate native Codex agents, using the persistent runner when task dependencies, batches, or recovery require it. |
| [Codex External Provider](.agents/skills/codex-external-provider/SKILL.md) | Check routing for a Codex session and native agents **started with** a configured external Responses API provider. |
| [Codex Harness Bridge](.agents/skills/codex-harness-bridge/SKILL.md) | Send one bounded job to a configured coding CLI and review its evidence from the current Codex session. |

The skills can participate in one workflow, but they do not automatically mix models or switch providers. Select a skill for the current task and explicitly invoke Harness Bridge if a bounded subprocess is useful. Native and External have different session routing requirements; External cannot change the provider of a session that has already started. **Fully mixed routing is a possible future enhancement, not a current feature.**

### Install

In Codex, ask the built-in `$skill-installer` to install these three paths from this repository:

```text
Repository: AshWood97/codex-zcode-orchestration
Paths: .agents/skills/codex-native-orchestrator
       .agents/skills/codex-external-provider
       .agents/skills/codex-harness-bridge
```

The installer places each directory in `$CODEX_HOME/skills/` (default `~/.codex/skills/`). On the next turn, select one from the skill picker, or invoke `$codex-native-orchestrator`, `$codex-external-provider`, or `$codex-harness-bridge` directly. Inspect any existing skill with the same name before updating it so local changes are preserved.

Python 3.11 or newer is recommended; External preflight and tests require at least 3.11. Installing the Native skill and configuring named agents are separate steps: the installer adds the skill, while the deployment below installs the fixed subagent roles. The current Codex session coordinates work but is not one of the skill's named roles; invoking the skill does not change its selected model. Start a new session after deployment. Keep External provider settings, model catalogs, and credentials in user configuration and environment variables, using the [example](.agents/skills/codex-external-provider/examples/user-config.example.toml) and [setup guide](.agents/skills/codex-external-provider/references/provider-setup.md). Create a private Harness Bridge configuration from its [example](.agents/skills/codex-harness-bridge/config.example.json) and [setup guide](.agents/skills/codex-harness-bridge/references/setup.md); install only the CLIs you plan to use.

#### Native fixed roles and deployment

| Role | Model | Reasoning effort |
| --- | --- | --- |
| Sol main workflow: conductor, explorer, researcher, worker, test_author, tester, reviewer, finding_validator | `gpt-6.1-sol` | `max` |
| Luna bounded repetitive work: scout, mechanic, check_runner | `gpt-6-luna` | `max` |
| Astra specialists and final gate: design_critic, debugger, guardian | `gpt-6-astra` | `xhigh` |

There are 14 roles; the default subagent is also Sol/max. Scout collects bounded facts, mechanic follows an explicit edit recipe, and check_runner executes predefined commands. Ambiguity escalates to explorer, worker, or tester respectively. Luna does not replace coverage judgment or final acceptance. Use design_critic for consequential design decisions and debugger for difficult causal diagnosis or two failed fixes of the same issue.

Conductor runs once at startup. Test authoring, execution, and review remain independent, with confirmed/refuted/unresolved finding adjudication. Tester/check_runner may generate outputs in disposable clones while tracked code, tests and Git metadata remain unchanged; no output is integrated. Every writer still requires downstream Sol Tester verification. Reviewer approval precedes the isolated Guardian gate. Evidence binds the exact candidate, tests and configuration; repairs refresh that evidence, and an unchanged revision cannot seek another verdict. Repairs are bounded to five waves. Configuration drift stops dispatch. See the [quality workflow](.agents/skills/codex-native-orchestrator/references/quality-workflow.md) and [routing rules](.agents/skills/codex-native-orchestrator/references/routing.md).

Place the 14 `.agents/skills/codex-native-orchestrator/roles/*.toml` profiles in your personal `CODEX_HOME/agents`, and merge the manifest's `config_values` into your personal `CODEX_HOME/config.toml`. These values configure subagents only; they do not include the global `model` or `model_reasoning_effort`. Preserve unrelated settings and avoid duplicate TOML keys. Run the check from this repository checkout. Running sessions and agents do not switch models automatically.

#### Manual invocation and Ultra entrypoint

Native orchestration keeps `allow_implicit_invocation: false`. Select **Codex Native Orchestration** from the skill/slash menu (`/codex` filters the list), or invoke `$codex-native-orchestrator` with a task, to start it manually. Ordinary and Max task matching do not start the workflow.

After installing the skill and 14 roles, run `python /absolute/path/to/CODEX_HOME/skills/codex-native-orchestrator/scripts/install_activation.py --apply`. It backs up personal `CODEX_HOME/AGENTS.md` and merges only the marked [activation block](.agents/skills/codex-native-orchestrator/references/activation.md), resolving the real installed skill path and preserving unrelated guidance. Omit `--apply` for a read-only check. Start a new session after installation.

Select **Ultra** in Codex and send a suitable complex repository task normally: the entrypoint automatically loads this workflow, without another skill selection. The host retains the selected Ultra mode; fixed role models and efforts apply only to delegated roles. Only the latest trusted runtime/developer instruction announcing active proactive delegation authorizes this entrypoint. Full access, saved effort defaults, screenshots, and earlier skill use are not signals. Simple Ultra tasks remain in the host session. The current client's mode instructions can be inspected without a model call using `codex -c 'model_reasoning_effort="ultra"' debug prompt-input`.

Both entrypoints use the same custom roles and controller flow, with one startup per run. Delegated children do not activate nested orchestration. Existing unfinished tasks resume their recorded run; independent tasks re-evaluate the entrypoints.

```sh
python3 .agents/skills/codex-native-orchestrator/scripts/codex_native_orchestrator.py --repo "$PWD" doctor
```

The independent Native Codex CLI honors explicit proxy environment settings. On macOS, enabled system HTTP/HTTPS proxies fill absent proxy settings. See the [recovery guide](.agents/skills/codex-native-orchestrator/references/runner-and-recovery.md) for private transcripts and timeout/interruption cleanup.

### ZCode role orchestration

The [ZCode installation guide](zcode/README.md) includes seven custom roles: code-reviewer, test-verifier, design-critic, test-author, finding-validator, debugger and docs-researcher. Together with built-in Explore and general-purpose, all nine code roles use **Gemini 3.8 Flash / high**. Document-plugin visual-judge agents are outside this code workflow.

The installer previews by default, backs up replacements, and merges a marked AGENTS.md workflow while preserving personal guidance. Users supply their own provider identifier; account state is not distributed. Set the two built-in agents to the same model in ZCode settings. ZCode relies on its host agent to enforce isolation, evidence binding and repair limits; it does not reuse Codex's persistent controller or isolated Guardian process.

### Public repository and verification limits

This repository contains only source code, documentation, placeholder examples, and tests. Do not commit API keys, real provider URLs, personal `config.toml`, private model catalogs, task briefs, run logs, or reports. External preflight requires trusted runtime provider/model identity; a configuration check alone does not prove remote request routing. Harness Bridge adapter tests use stub CLIs and do not establish compatibility with every live CLI version or service. DeepSeek Harness support remains experimental.

See the [changelog](CHANGELOG.md) for the role, quality-workflow and routing upgrades. Controller and installation tests do not establish model quality or measured quota savings; use the [evaluation protocol](.agents/skills/codex-native-orchestrator/references/evaluation.md).

Run the existing tests:

```sh
for skill in codex-native-orchestrator codex-external-provider codex-harness-bridge; do
  PYTHONDONTWRITEBYTECODE=1 python3.11 -B -m unittest discover \
    -s ".agents/skills/$skill/tests" -p 'test_*.py' -q || exit 1
done
python3.11 -B -m unittest discover -s zcode/tests -p 'test_*.py' -q
```

## License

MIT. See [LICENSE](LICENSE).
