# Owner 体系专题

状态：`Guoshang 设计基线；实现状态以 Paralls 当前代码和 Guoshang 接入证据为准`

本目录补充 Owner 分类、角色档案/状态接入和数值规则结算边界。它与上层玩法系统文档配套，不替代既有的 Paralls Owner 分析、Guoshang 新 Owner 清单、统一 Command 规范或第一阶段 Demo 执行路线。

## 文档导航

| 文件 | 主题 |
| --- | --- |
| [01-Owner 分类与 Paralls 实现对照](01-Owner分类与Paralls实现对照.md) | 基础设施、基础 Owner、原子 Owner、组合 Owner 的定义及其和 Paralls 当前实现的关系 |
| [02-角色档案、权威状态与心智状态对接](02-角色档案、权威状态与心智状态对接.md) | 角色静态设定、角色身体/社会事实、角色私有心智状态如何进入 Owner 结算 |
| [03-数值规则、状态效果与跨 Owner 结算](03-数值规则、状态效果与跨Owner结算.md) | Owner 公式、标签/状态效果、跨域事务、UE、Workflow 与 WRK 边界 |
| [04-领域模型注册、绑定与 Owner 评估架构](04-领域模型注册、绑定与Owner评估架构.md) | 数值模型、条件模型、混合模型、Static Data、Applicability Binding、评估上下文和领域内泛化边界 |

## 与现有玩法系统文档的关系

- [01-Paralls 现有 Owner 与接入分析](../01-Paralls现有Owner与接入分析.md)：Paralls 现有代码和证据基线。
- [02-Guoshang 新 Owner 需求与统一 Command 规范](../02-Guoshang新Owner需求与统一Command规范.md)：Guoshang Command 和新 Owner 需求主文档。
- [03-基建 Owner 传统方案与 Paralls 兼容方案](../03-基建Owner传统方案与Paralls兼容方案.md)：UE 传统玩法与 Paralls 兼容方案主文档。
- [05-第一阶段县城守城 Demo 设计与执行路线](../05-第一阶段县城守城Demo设计与执行路线.md)：第一阶段内容、基础设施和验收路线。
- [08-基础设施与 Owner 建设总计划](../08-基础设施与Owner建设总计划.md)：23 个领域 Owner 的最终名单、公共基础设施、建设批次、分工和验收门。

## 共同架构边界

```text
命令来源：玩家 / 智能体玩家 / 角色智能体 / 群体模拟 / 场景脚本
  -> 统一 Command 治理与路由
  -> 目标领域 Owner 验证公式、条件、权限、成本和 revision
  -> 唯一世界真相账提交事件与 receipt
  -> 角色私有认知投影 / 群体查询投影 / UE 表现投影
```

基础设施支撑事实提交；Owner 拥有事实；Workflow/WRK 组织跨 Owner 过程；角色智能体形成判断和意图；UE 可承载获准领域 Owner 的高频执行，也承载表现。任何协调层、投影层或表现层都不能替领域 Owner 写入世界事实。

## UE 兼容与唯一写权

“兼容 UE 传统方案”不等于 Actor、Ability、Component 或后端各保留一份可写状态。它要求 Owner 的规则和提交合同可以由 UE 高频执行路径调用；每项 canonical fact 仍只有一个 Owner 和一个有效写入口。运行时部署位置、模拟位置和事实写权分别声明，不能用一个含糊的 `hybrid` 同时表达。

伤害链按事实拆分：Combat 结算攻击/命中并给出伤害评估；Equipment 按固定装备 revision 结算防护与耐久；Body 将剩余伤害应用到生命、伤势和身体功能；Status 再基于 Body 的授权结果评估身体条件并创建流血等效果实例。LifeState 根据授权依据确认生命周期转换，生命归零不自动等于死亡。需要同帧反馈时，这些 Owner 可在同一受控运行时生成各自授权的 fragment，并按依赖顺序原子提交；UE Actor 仍是投影/执行对象。治疗由医疗流程协调 Inventory、Body 和 Status Owner，并校验 LifeState，不由治疗动画或 Pawn 的恢复组件直接加血。Objective 只读取已确认死亡等事实并判断结局。

近场推荐将 Combat、Body/Resource、Equipment、Status、LifeState、战场 Morale 的获准实现共同部署在 UE，通过本地调用协作。生命按事件、体力按动作/时间积分、士气按事件与周期压力评估，身体强制反应不等待 Agent 推理；Agent 继续负责自主判断。Owner 计算、canonical 提交和后端投影同步是三个边界：本地可靠提交须正式注册为唯一权威才能即时确认；只有后端 store 时，本地结果在 receipt 前仍为 pending。详见[高频协作与提交合同](03-数值规则、状态效果与跨Owner结算.md#44-近场部署职责分域实时协作)。

23 个 Owner 的完整 UE 协作与更新矩阵统一维护在[总计划第 11.2 节](../08-基础设施与Owner建设总计划.md#112-全量-owner-的-ue-协作与节奏矩阵)，本目录不另排建设顺序。ESM 不是万能 Owner 或全动作入口：已核验交互合同可选复用，Godot 执行器需替换，旧对象/身体写权先迁移，参见[ESM 复核与迁移检查](../01-Paralls现有Owner与接入分析.md#9-esm-复用边界与迁移检查)。
