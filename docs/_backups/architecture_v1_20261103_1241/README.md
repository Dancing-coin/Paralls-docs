# Guoshang 技术架构

> 版本：1.0（职责拆分版）
> 更新日期：2026-10-30
> 评审状态：职责归位与静态一致性核对；不替代产品待决项裁决或实现评审。
> 实现状态：本篇为目标合同；已有实现仅按原始证据日期记录，不代表全量实现或运行验收完成。
> 验证范围：本轮仅重组文档，未执行代码、UE、PIE 或性能验证。原始设计、实现盘点和证据日期分别保留。

<a id="technical-reference"></a>

## 技术权威与阅读入口

本目录统一维护公共技术合同、逻辑 Owner、领域结算和运行时接入；产品目标与玩法体验由 `docs/PRD/` 的正式分区维护，建设批次与切片排程由生产计划维护。技术目录不重新建立“骑将冲阵”独立产品目标。

所有实现状态分开记为：**已定义、可执行、已接入、已验收**。本轮完成的是文档结构与合同归位，不把设计文本、模块存在或静态复核升级成实现完成。

| 技术主题 | 权威入口 |
|---|---|
| 系统边界与唯一写权 | [01-系统边界与权威写入](01-系统边界/01-系统边界与权威写入.md#system-boundaries) |
| 现状、证据日期与缺口 | [02-现状基线与证据](01-系统边界/02-现状基线与证据.md#evidence-baselines) |
| 三本账与WRK | [03-三本账与WRK](01-系统边界/03-三本账与WRK.md#three-ledgers) |
| 时间、身份、控制与暂停 | [01-时间身份与控制权](02-公共契约/01-时间身份与控制权.md#time-identity-control) |
| Command/Event/Receipt与失败 | [02-Command事件与Receipt](02-公共契约/02-Command事件与Receipt.md#command-event-receipt) |
| 受限Query/UI投影 | [03-受限查询与投影](02-公共契约/03-受限查询与投影.md#restricted-projections) |
| 多精度、lease与handoff | [04-多精度与Handoff](02-公共契约/04-多精度与Handoff.md#handoff) |
| 唯一23逻辑Owner名单及Manifest | [01-Owner注册表](03-Owner领域/01-Owner注册表.md#owner-registry) |
| 领域详细合同 | [02-领域Owner详细契约](03-Owner领域/02-领域Owner详细契约.md#domain-contracts) |
| 角色档案、事实与心智 | [03-角色档案事实与心智](03-Owner领域/03-角色档案事实与心智.md#character-state) |
| 模型注册、Binding与评估 | [01-领域模型注册绑定与评估](04-模型与结算/01-领域模型注册绑定与评估.md#domain-models) |
| 数值、效果与跨域结算 | [02-数值状态效果与跨Owner结算](04-模型与结算/02-数值状态效果与跨Owner结算.md#numeric-settlement) |
| UE本地提交/同步与完整节奏矩阵 | [01-UE本地提交与Paralls同步](05-运行时接入/01-UE本地提交与Paralls同步.md#ue-paralls) |
| Agent/群体/语义动画 | [02-Agent群体与动画接入](05-运行时接入/02-Agent群体与动画接入.md#agent-population) |
| ESM复用与迁移 | [03-ESM复用与迁移](05-运行时接入/03-ESM复用与迁移.md#esm-migration) |
| 存档/回放/恢复 | [01-存档回放与故障恢复](06-存档与可观测性/01-存档回放与故障恢复.md#save-replay-recovery) |
| 观测、fixture与证据 | [02-可观测性与验收证据](06-存档与可观测性/02-可观测性与验收证据.md#acceptance-evidence) |

<a id="authority-rules"></a>

## 维护规则

- 23 个逻辑领域 Owner 的完整注册表只维护在注册表一处；宿主、模块、分区与工作流不增加计数。
- 全量 UE 协作与节奏矩阵只维护在 UE/Paralls 接入文档，其他文档链接引用。
- 公共信封、时间/身份、epoch、lease、receipt、暂停与受限投影只在公共契约维护；领域文仅细化本域规则。
- 医疗是 Medical Workflow；Composite 是组合流程；Ability/Skill、ESM、表现层与 WRK 不因名称新增领域写权。
- 唯一 canonical EventStore 表示唯一逻辑权威账本，不能误写成所有事实必须由 Python 后端提交。获准本地可靠提交可最终确认；只有后端提交端时本地保持 pending/predicted。
- 原始 PRD 的只读副本和逐节迁移清单在 `docs/_backups/PRD_20261030_111755/`；旧专题不再构成并行正式规范。

<a id="historical-spec"></a>

## 历史设计与未决差异

既有 [2026-10-27 fidelity draft](../superpowers/specs/2026-10-27-ue-paralls-fidelity-alignment-design.md) 保持原样。其双轴精度、lease、连续性、语义动画和验收细节在本目录按主题引用；其旧产品目标、旧实施顺序与 draft 状态不能覆盖当前产品和生产计划。

该 draft 的 UE 时钟措辞统一解释为选定部署下的时钟入口/投影，而非允许多份可写世界时钟；笼统“UE Owner”按当前领域注册表逐域解释。角色 embodiment/intent lease 不能替代领域 authority_scope/epoch。断线战术脑只能在明确登记的降级控制权与有效意图/许可内工作，不能自动产生新的 C3 自主意图。

待决项必须带来源：跨区域环境事实归属尚待登记；SGC-3 真实 handoff 完整性仍须实现证据；具体响应预算与时间倍率等待实测，不填虚构已测数值。旧 draft 要求“进入实现计划前真实 handoff”的过程约束与当前排程差异交生产计划裁决。

<a id="external-authorities"></a>

## 产品、生产与证据入口

- [县城守城 Demo 体验目标与范围](../PRD/05-阶段与可玩切片/县城守城Demo/体验目标与范围.md)
- [阶段与切片对照表](../PRD/05-阶段与可玩切片/阶段与切片对照表.md)
- [基础设施与 Owner 建设总计划](../production/基础设施与Owner建设总计划.md)
- [县城守城 Demo 执行计划](../production/县城守城Demo执行计划.md)
- [验证与证据规范](../validation/验证与证据规范.md)
- [县城守城 Demo 测试用例与证据索引](../validation/县城守城Demo/测试用例与证据索引.md)
