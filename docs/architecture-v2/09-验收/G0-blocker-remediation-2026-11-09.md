# G0 阻塞修复记录

- 原始基线：`5321266dbd882f45eb6a24dd7b328e9f56746228`，原始失败分类和两轮结果保持不变。
- 独立修复分支：`codex/g0-b3-ingress-20261109`，验证提交 `776011a6027ef76600555125a410204f9f494571`。
- 本记录是缺陷修复轨道，不代表架构迁移完成或 G1 放行。

## 修复范围

| 阻塞 | 修复与边界 |
| --- | --- |
| B1 | 移植 `refactor/shared-owner-base` 的独立补丁，校验 package exchange 幂等收据引用的事件和事务；补充空、重复、乱序和错误事务引用反例。其他领域重放路径不在此修复范围。 |
| B2 | 在预算约束内优先召回当前关注目标的活动失败事项对应的最新知识，并忽略类型不合法的目标引用。 |
| B3 | 玩家对象持久化入口要求控制器绑定、授权空间样本和请求 ID，经 ESM 权威提交并恢复最新占用投影；未授权的旧入口明确拒绝。现支持牌匾 inspect 和工作台 use/finish_use。旧无凭证测试节点已由授权入口的状态、拒绝和无额外写入测试接替。 |
| B4 | 保留已发布 checkpoint 指纹，并对绑定的内核源码进行规范化身份校验。部署必须能读取 Python 源文件；Python 3.12 环境完整测试尚待验证。 |

## 中间全量回归

较早提交 `ef4a4f6d` 的完整运行收集 9903 项，9792 passed、107 failed、2 skipped、2 xfailed，见[日志](G0-20261109-5321266d/blocker-fixes-final.log)和[机器结果](G0-20261109-5321266d/blocker-fixes-final/results.json)。原基线四个失败节点转为通过：B1、B2 和 B4 的两个节点。另有三个原通过节点失败：两个 Godot 探针在新工作区找不到全局类；管理授权测试在该工作区单独重跑通过，完整运行差异原因尚未证实。该运行不包含最终 B3 入口，不能作为最终提交的全量证据。

## 最终提交验证

- `776011a6` 的完整 backend 测试收集 9916 项：9807 passed、105 failed、2 skipped、2 xfailed；收集错误为零，退出码 1。见[日志](G0-20261109-5321266d/final-776011a6.log)和[机器结果](G0-20261109-5321266d/final-776011a6/results.json)。
- 与原基线逐节点比较：B1、B2、B4 的两个测试共四项由失败转通过；原 B3 无凭证节点被移除，由授权入口中覆盖状态转换、拒绝及无额外写入的测试接替。新增 18 个节点均通过。
- 两个原通过的 Godot 探针在新 worktree 全量运行中因全局类索引缺失失败；在该 worktree 使用 Godot 4.6.3 headless editor 初始化索引后分别重跑，2 passed。此复跑不改变完整运行的原始结果。
- `character-memory-consistency`、`embodied-authority-settlement` 和 `gameplay-event-replay` 三个 harness profile 通过。`--profile all` 在第一个 `docs` profile 失败后停止：`docs/INDEX.md` 引用的 `docs/11月份分析/README.md` 在原始提交中不存在，其余 79 个 profile 未执行。导出证据位于 `D:/Temp/paralls-g0-harness-776011a6` 和对应三个 profile 的 `D:/Temp/paralls-g0-harness-*-776011a6` 目录。
- Python 3.13.5 定向与全量结果不代替 CI Python 3.12.14 的完整运行；本地 3.12 环境缺少 `zlib_ng`。没有客户端或 UE PIE 端到端证据。

G0 仍未放行：需要处理或接受剩余失败、完成相应环境及客户端验证，并取得阶段门审批。旧入口行为调整需要客户端采用已授权的请求路径。
