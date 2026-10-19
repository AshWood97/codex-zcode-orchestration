# ZCode 角色编排 / ZCode orchestration

默认流程：**充分考虑的计划 → 执行 → 检查 → 有问题修改、没问题放行**。主 Agent 评估任务、从全部角色中选取需要的角色，并保持一份计划；检查由主 Agent 或一个 code-reviewer 完成，不重复。Review 只读，修复只处理实现任务内的具体缺陷。完整边界见 [AGENTS.md](AGENTS.md)。

七个自定义角色及两个内置角色保持 **Gemini 3.8 Flash / high**：

| 角色 | 使用范围 |
| --- | --- |
| Explore（内置） | 查清当前任务相关源码和调用链 |
| general-purpose（内置） | 在分配路径内实现最小改动 |
| docs-researcher | 解决必要外部 API/版本事实 |
| code-reviewer | 一次针对请求的只读检查 |
| debugger | 诊断当前任务的具体不明缺陷，无自动轮数触发 |
| design-critic | 规划者判断存在重要且未解决的设计取舍时使用 |
| finding-validator | 规划者判断争议发现会影响结果时使用 |
| test-author | 重要行为需要检查且现有用例缺失时，补最小测试 |
| test-verifier | 重要行为无法通过源码和已有结果判断时，做最小针对性测试 |

规划者可按需选择所有角色，不要求用户逐个点名，也不把全部角色依次跑一遍。尽量少做额外测试，先阅读源码和结果，优先复用现有用例；重要问题仍无法判断才做最小测试，确有缺口才写新用例。不默认添加 hash、审核层、日志、证据包或未来抽象。默认一个写入者，最多四个子智能体；用户明确的不测试、只读等限制仍须遵守。只有超出用户任务范围才先征求同意。

## 安装

使用 Python 3.11+，从自己的 ZCode 模型设置获取 Gemini 的 `provider-id/model-id`。模板中的 `__ZCODE_MODEL_ID__` 是占位符。

```sh
# 预览
python zcode/scripts/install.py --model "your-provider/gemini-3.8-flash-high"

# 安装
python zcode/scripts/install.py --model "your-provider/gemini-3.8-flash-high" --apply
```

默认安装到 `~/.zcode`，可用 `--zcode-home` 指定目录。同名角色内容不同会显示冲突；明确替换时加 `--replace-existing`。安装器不计算前后摘要，不生成备份、收据或日志文件。

`AGENTS.md` 的 `codex-zcode-orchestration:quality` 标记只包围本工作流，标记外的个人规则保留。如果已有未加标记的旧版规则，更新时替换旧工作流，避免新旧规则叠加。

在 ZCode 设置中把内置 Explore 和 general-purpose 设为相同 Gemini 模型和 high 深度，再开始新会话。安装器不写账号状态和文档插件角色。

## English

The host plans the requested work, implements the smallest change and chooses one checking owner. Inspect requirements, the actual result and directly affected callers. Fix concrete in-scope issues in implementation tasks; review-only tasks stay read-only. Deliver as soon as the request is satisfied.

All nine roles keep Gemini 3.8 Flash/high. The host planner may select any role for a concrete in-scope need without the user naming it. Minimize extra testing: inspect first, reuse existing results and prefer the smallest existing check; write new cases only for important gaps. Do not run every role, repeat reviews or add routine matrices, hash/evidence layers or extra artifacts. Explicit user prohibitions remain binding; scope expansions require a question before acting.

Use the commands above with your own provider/model identifier. `--apply` installs; `--replace-existing` explicitly replaces differing roles. Marked guidance preserves surrounding personal rules. Installation produces no digest, backup receipt or log. Configure the two built-in roles in ZCode settings and start a new session.
