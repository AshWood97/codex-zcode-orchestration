# Qoder: Harness Orchestration / 多 Harness 角色编排

[中文](#中文) · [English](#english) · [Repository / 仓库](https://github.com/AshWood97/harness-orchestration)

## 中文

这个目录把现有角色语义适配为 Qoder 桌面插件：一个手动启用的 `harness-orchestration` skill，以及完整 14 个按需选择的插件角色。Codex 与 ZCode 的原文件、安装路径和入口保持不变。插件角色省略 `model`，由 Qoder 沿用当前对话模型；不携带 Codex 模型标识、provider 配置、凭据、Hooks 或 MCP。

### 安装到 Qoder CN 桌面端

1. 使用交付的 `harness-orchestration-qoder-1.0.0.zip`，或按下方命令打包。ZIP 根目录必须直接包含 `.qoder-plugin/plugin.json`。
2. 在 Qoder CN 打开 **Extensions → Plugins → Add Plugin → 上传 Plugin**，导入插件 ZIP，安装到本机。
3. 新建一个名为 **Harness Orchestration** 的自定义 Agent，在其插件选择项中选择本插件，并把 [coordinator-instructions.txt](coordinator-instructions.txt) 的内容粘贴到指令中。自定义 Agent 是协调入口；14 个执行角色由插件的 `agents/` 提供。
4. 显式选择这个自定义 Agent 后提出任务，即手动启用工作流；也可以在普通 Qoder 对话中显式选择同名 skill 或要求“使用 Harness Orchestration 完成……”。仅安装插件不会自动启用编排。

角色表中的名字来自各文件的 `name`。运行时使用 Qoder 实际显示的本插件角色标识；如果平台加上命名空间，沿用完整标识，不自行编造前缀。14 个角色是可选目录；Team 当前最多 5 个成员，按任务只选必要组合。

### 打包

在 macOS/Linux 的仓库根目录执行：

```sh
cd qoder/harness-orchestration
zip -r /tmp/harness-orchestration-qoder-1.0.0.zip .qoder-plugin agents skills LICENSE
```

这会把安装包写到仓库之外。导入 ZIP 时不要再包一层 `harness-orchestration/` 目录。

```text
qoder/
├── coordinator-instructions.txt
└── harness-orchestration/
    ├── .qoder-plugin/plugin.json
    ├── agents/                  # 14 个 Markdown 角色
    ├── skills/harness-orchestration/SKILL.md
    └── LICENSE
```

### 工作方式

简单任务留在主 Agent。需要分工时，一个 `conductor` 先理解需求并选择最小角色组合，主 Agent 负责派遣。默认一个写入者、一个检查负责人，最多四个子角色；更严格的用户或运行时限制优先，子角色不得再委派。流程是**计划 → 实现 → 检查一次 → 修复具体问题或交付**；修复后只看直接影响，复用已有结论。

先读源码和已有结果，仅为重要未决行为做最小针对性检查；确有重要缺口才新增测试。遵守不测试、只读、`root-only`、`max agents` 等限制。专项角色须回答不同的实质问题，不构成固定审批链。不默认跑全套测试、计算 hash/checksum/指纹/签名、生成日志或额外产物。超范围先征求用户同意。

### 角色与权限

只读角色仅有 `Read, Grep, Glob`；`researcher` 另有 `WebFetch, WebSearch`。写入角色有 `Read, Grep, Glob, Bash, Edit, Write`。`tester`、`check-runner` 有 `Read, Grep, Glob, Bash`，仅执行分配的命令，不得通过 Bash 绕过禁止编辑的限制。

| Agent / 角色名 | Purpose / 用途 | Access / 权限 |
| --- | --- | --- |
| `conductor` | Assess and plan / 评估任务、按需选角色 | Read only / 只读 |
| `explorer` | Locate implementation and callers / 定位实现与调用链 | Read only / 只读 |
| `researcher` | Resolve upstream/API facts / 核实上游及 API 事实 | Read + web / 只读与网页查询 |
| `worker` | Implement the agreed change / 按计划实现 | Write / 写入指定路径 |
| `reviewer` | Inspect the requested result / 检查请求范围的结果 | Read only / 只读 |
| `finding-validator` | Resolve a disputed finding / 裁定有争议的具体发现 | Read only / 只读 |
| `test-author` | Cover a concrete important gap / 补足重要测试缺口 | Write test paths / 写入指定测试路径 |
| `tester` | Run a minimal targeted check / 执行最小针对性检查 | Commands, no edits / 执行命令、禁止编辑 |
| `scout` | Retrieve exact paths or symbols / 精确检索路径或符号 | Read only / 只读 |
| `mechanic` | Apply an exact edit recipe / 执行明确修改步骤 | Write / 写入指定路径 |
| `check-runner` | Run an assigned command list / 执行指定命令列表 | Commands, no edits / 执行命令、禁止编辑 |
| `design-critic` | Resolve a design tradeoff / 处理实质设计取舍 | Read only / 只读 |
| `debugger` | Diagnose a concrete defect / 定位具体缺陷原因 | Read only / 只读 |
| `guardian` | Resolve a distinct acceptance question / 判断独立的重要验收问题 | Read only / 只读 |

角色语义来自 [Codex Native 角色源](../.agents/skills/codex-native-orchestrator/roles)，Qoder 文件名及 `name` 使用 kebab-case：`finding_validator` → `finding-validator`、`test_author` → `test-author`、`check_runner` → `check-runner`、`design_critic` → `design-critic`。

### 验证边界

2026-10-21 已在 Qoder CN 桌面端（内置 `qodercli 1.1.69`）完成 ZIP 导入及角色发现：插件已启用，Agent 页面显示本插件提供 14 个角色。自定义 **Harness Orchestration** 协调器已绑定本插件，可在新任务的执行器菜单中选择。当前默认模型设置为 **DeepSeek-Flash / max**；一次只读检查成功调用实际角色标识 `harness-orchestration:conductor`，子角色 2 秒完成，主任务 5 秒内成功，共 2 次模型迭代，没有文件、命令或网络工具调用。这项检查证明安装、发现和单角色分派成功，不代表全部 14 个角色均已执行。

当前清单按官方 CLI 插件格式把 `agents` 声明为 Markdown 文件路径数组，兼容桌面导入器的文件路径要求。旧版随附的离线 `validate_qoder_plugin.py` 只接受单一路径，不能验证这个数组字段；当前清单格式以桌面导入校验为准。其他角色执行、独立模型路由及权限执行不在此次验证范围。本包不配置账户或 provider，也不保证跨 Harness 的统一运行时；后续适配器可继续放入本仓库。

参考：[插件](https://docs.qoder.com/zh/qoder/plugins)、[子 Agent](https://docs.qoder.com/zh/qoder/subagents)、[Agent 格式及工具](https://docs.qoder.com/zh/extensions/subagent)、[CLI 插件格式](https://docs.qoder.com/zh/cli/plugins-reference)。

## English

This package adapts the existing role semantics to Qoder desktop: one manually activated `harness-orchestration` skill and all 14 optional plugin agents. Existing Codex and ZCode files, installation paths, and activation markers are preserved. Agent `model` fields are omitted so Qoder follows the current conversation model. The package contains portable prompts without Codex model IDs, provider settings, credentials, hooks, or MCP servers.

### Install in Qoder CN desktop

1. Use the delivered `harness-orchestration-qoder-1.0.0.zip`, or package it using the command below. The ZIP root must directly contain `.qoder-plugin/plugin.json`.
2. Open **Extensions → Plugins → Add Plugin → Upload Plugin** in Qoder CN and import the ZIP for local installation.
3. Create a custom agent named **Harness Orchestration**, select this plugin in its plugin picker, and paste [coordinator-instructions.txt](coordinator-instructions.txt) into its instructions. This custom agent coordinates work; the 14 execution roles are provided by the plugin's `agents/` directory.
4. Selecting that custom agent and supplying a task manually activates the workflow. In a regular Qoder conversation, explicitly select the skill or ask to use Harness Orchestration. Installation alone does not activate orchestration.

Use the actual identifiers Qoder exposes for this plugin, including a namespace if one is displayed. The catalog above lists agent frontmatter names. Team currently supports up to five members; choose only the roles needed for the task from the 14-role catalog.

### Package

From the repository root on macOS/Linux:

```sh
cd qoder/harness-orchestration
zip -r /tmp/harness-orchestration-qoder-1.0.0.zip .qoder-plugin agents skills LICENSE
```

The archive is written outside the repository. Its root contains `.qoder-plugin`, `agents`, `skills`, and `LICENSE` directly.

### Workflow and permissions

Keep simple work in the host. For useful multi-role work, one `conductor` assesses the task and selects the smallest useful subset; the host dispatches it. Default to one writer, one checking owner, and at most four children; tighter user or runtime limits take precedence. Children never delegate. Follow **plan → implement → inspect once → fix concrete issues or deliver**, reusing unchanged conclusions after repairs.

Inspect source and existing results before choosing the smallest check for an important unresolved behavior. Add a test only for a concrete important gap. Honor no-tests, read-only, `root-only`, and agent limits. Specialists answer distinct material questions instead of forming an approval chain. Do not default to full suites, digests, logs, or extra artifacts. Ask before expanding scope.

Read-only roles have `Read, Grep, Glob`; `researcher` also has `WebFetch, WebSearch`. Writers have `Read, Grep, Glob, Bash, Edit, Write`. `tester` and `check-runner` have `Read, Grep, Glob, Bash` and execute assigned checks without editing files. They must not use Bash as an editing workaround. The bilingual catalog above lists every role and its purpose.

Semantics come from the [Codex Native role sources](../.agents/skills/codex-native-orchestrator/roles); Qoder names use kebab-case in place of underscores. This adaptation does not copy the Codex runtime model mapping.

### Validation limits

On 2026-10-21, ZIP import and agent discovery passed in Qoder CN desktop with bundled `qodercli 1.1.69`: the plugin was enabled and the Agents page listed all 14 plugin roles. The custom **Harness Orchestration** coordinator was bound to this plugin and can be selected in the executor menu for a new task. With the current default model setting **DeepSeek-Flash / max**, a read-only smoke check successfully invoked the actual identifier `harness-orchestration:conductor`. The role completed in 2 seconds; the host task succeeded in 5 seconds with 2 model iterations and no file, shell, or network tool calls. This verifies installation, discovery, and one-role dispatch; it does not establish execution of all 14 roles.

The manifest follows the official CLI plugin format by listing individual agent Markdown paths in an array, satisfying the desktop importer's file-path requirement. The older bundled offline `validate_qoder_plugin.py` accepts only a single path for this field and cannot validate the array; desktop import validation determines compatibility. Execution of other roles, independent model routing, and permission enforcement are outside this check. This package configures no account or provider and makes no cross-harness runtime guarantee. Further harness adapters can be added to this repository.

References: [Plugins](https://docs.qoder.com/zh/qoder/plugins), [Subagents](https://docs.qoder.com/zh/qoder/subagents), [Agent format and tools](https://docs.qoder.com/zh/extensions/subagent), [CLI plugin format](https://docs.qoder.com/zh/cli/plugins-reference).
