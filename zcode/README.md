# ZCode 代码角色编排 / ZCode code-role orchestration

七个自定义角色，加两个内置角色；统一采用 **Gemini 3.8 Flash / high**。主 Agent 负责计划、任务账本、路由、整合和交付。完整规则在 [AGENTS.md](AGENTS.md)。这套配置面向软件开发，文档插件提供的 visual-judge 不在范围内。

| 角色 | 来源 | 职责 |
| --- | --- | --- |
| Explore | 内置 | 搜索仓库、调用链与影响范围；任务包显式附带项目约束 |
| general-purpose | 内置 | 在 owned_paths 内实现；不能修改冻结测试 |
| docs-researcher | 自定义 | 核验官方文档、版本、上游 API 行为 |
| design-critic | 自定义 | 在重要设计实施前提出反例与最小调整 |
| test-author | 自定义 | 从需求独立设计和编写验收测试 |
| test-verifier | 自定义 | 在独立副本运行测试、构建和复现 |
| code-reviewer | 自定义 | 审查实际 diff、调用方及测试有效性 |
| finding-validator | 自定义 | 用证据裁定 confirmed/refuted/unresolved |
| debugger | 自定义 | 两次失败修复后或因果难明时分析根因 |

默认一个实现写入者，总并发不超过四个子智能体。测试设计、执行和代码审查分别提供证据；重要未解决风险阻止完成。整体最多五轮自动修复。候选方案比较仅在明确选择实验时启用。

## 安装

需要 Python 3.11+。先在 ZCode 中配置可用的 Gemini 3.8 Flash 模型；从自己的模型设置获取 `provider-id/model-id`。仓库中的 `__ZCODE_MODEL_ID__` 是安装模板，不能直接当作模型运行，也不是 API key。

在仓库根目录执行，替换示例 provider 标识：

```sh
# 默认只查看目标文件、差异和冲突，不写入
python zcode/scripts/install.py --model "your-provider/gemini-3.8-flash-high"

# 安装七个角色，并合并主 Agent 工作流
python zcode/scripts/install.py --model "your-provider/gemini-3.8-flash-high" --apply
```

默认目标是 `~/.zcode/`，可用 `--zcode-home /your/path` 指定位置。如果同名角色已被修改，安装器会报告冲突并停止；检查预览后，可明确加 `--replace-existing` 替换。旧内容保存在目标目录的 `backups/codex-zcode-orchestration/`，备份清单记录路径及前后哈希。安装失败会恢复已写入的文件；不要把个人备份提交到仓库。

`AGENTS.md` 使用 `codex-zcode-orchestration:quality` 标记更新工作流，保留标记外的个人规则。未加标记但与模板完全一致的旧文件会转换成带标记版本。若已有其他旧版编排规则，请检查并协调重复内容，避免同时保留相互冲突的工作流。

安装后，在 **ZCode → 设置 → 子智能体** 中，将内置 **Explore** 和 **general-purpose** 都设为同一个 **Gemini 3.8 Flash**，思考深度为 **high / 高**。这一步通过产品设置完成；安装器不写私有 `v2/agents-state.json`、provider UUID 或插件角色状态。开始新会话加载角色。

## 能力与验证边界

角色工具清单和 `injectAgentsMd` 使用本轮配置的格式。工具白名单不是文件系统隔离；主 Agent 需要提供真实临时 Git 副本、实际 diff 和命令结果。code-reviewer 只有读取工具，不能被要求自行运行 `git diff`。本包没有 Codex 的持久 DAG 控制器或独立 Guardian 进程。

安装测试验证预览、幂等性、保留个人规则、冲突、备份和失败恢复，不证明某个 ZCode 版本已成功加载角色，也不证明模型质量或实际额度收益。

```sh
python -B -m unittest discover -s zcode/tests -p 'test_*.py' -v
```

## English

This package supplies seven custom coding agents plus a host workflow. Configure built-in Explore and general-purpose as well; all nine use **Gemini 3.8 Flash / high**. The host owns planning, routing, integration and delivery. Test authoring, verification and review are separate; disputed findings require evidence. Use at most four children, one implementation writer by default, and at most five repair waves.

Run the commands above with your own ZCode `provider-id/model-id`. Installation is a dry-run unless `--apply` is present. Existing customized roles require explicit `--replace-existing`; replacements are backed up. The marked workflow preserves surrounding personal AGENTS.md guidance. After installation, select the same model and high reasoning for **Explore** and **general-purpose** in ZCode settings, then start a new session. Private provider state and document-plugin judges are not modified or shipped.

The tool allowlist is not a filesystem sandbox. The host must supply isolated verification checkouts and readable diffs. Installer tests cover file behavior, not live ZCode compatibility, coding-quality gains or measured quota savings. See the shared [evaluation protocol](../.agents/skills/codex-native-orchestrator/references/evaluation.md).
