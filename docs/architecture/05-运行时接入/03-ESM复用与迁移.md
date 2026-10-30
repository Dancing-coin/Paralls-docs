# 03-ESM复用与迁移

> 版本：1.0（职责拆分版）
> 更新日期：2026-10-30
> 评审状态：职责归位与静态一致性核对；不替代产品待决项裁决或实现评审。
> 实现状态：本篇为目标合同；已有实现仅按原始证据日期记录，不代表全量实现或运行验收完成。
> 验证范围：本轮仅重组文档，未执行代码、UE、PIE 或性能验证。原始设计、实现盘点和证据日期分别保留。

[技术架构入口](../README.md) · [唯一 Owner 注册表](../03-Owner领域/01-Owner注册表.md#owner-registry)

<a id="esm-migration"></a>

## ESM 复用边界、写入口 fence 与执行器迁移

### ESM 复用边界与迁移检查

以下是 2026-10-30 的静态代码/规格核对，不是 UE 运行验收。ESM 已有语义编排与持久结果能力，并非空壳；它的范围与 Godot 依赖也不能推导成通用 UE 游戏底座。

| 层次 | 当前证据 | Guoshang 处理 |
|---|---|---|
| 结构化语义与结果 | `backend/app/services/esm_service.py` 含对象交互和 `gameplay.esm.object_settled` 事件；示例位置、对象与距离判据有硬编码 | 审核动作、目标、拒绝和结果合同；替换示例数据并将对象字段映射到正式事实域，不照搬世界坐标和判据 |
| 许可与证据 | `backend/app/models/embodied_interaction.py` 有 grant/epoch、revision、幂等、证据引用等；route/writer 枚举仍有现有实现假设 | 保留经审核的许可、attempt、evidence、outcome 语义；schema 版本化适配 UE，不冒充即插即用 |
| 物理通道 | `backend/app/services/physical_interaction_channel.py` 校验语义许可与观察，含 Godot/backend probe 来源 | 仅复用审核过的证据校验思想；它不是 UE 碰撞、寻路或刚体求解器 |
| 具身执行器 | `scripts/interaction/EmbodiedActionController.gd` 是 Godot Node，执行接近、对齐、准备、接触、观察、恢复等阶段 | 由 UE 原生移动、交互、动画和碰撞执行器实现相应阶段；不将 GDScript 当成 UE 依赖 |
| 旧身体结算 | `backend/app/services/embodied_authority_settlement_service.py` 有示例角色 hp/stamina 与结果持久化路径 | 生命/体力写权归 Body，不能与旧街区结算并行写同一角色；事件历史保留，迁移后旧入口由 epoch/路由失效 |
| 正式领域路由 | Paralls `docs/架构/运行时/模块/ESM与交互编排.md`、`GameplayFoundation与领域结算.md` | 请求按事实归属路由到 ESM 的有界合同或 Gameplay Owner，不新增万能 ESM→所有玩法入口 |

接入前按“可复用合同 / 需适配 schema / 需替换执行器 / 需迁移写入口”登记到建设总计划 A1—A5。门扇开闭/门闩/设施完整度归 Production / Facility，通行归 Presence，封城政令归 Government，控制归 Territory；装备关系/耐久归 Equipment，库存归 Inventory，身体归 Body。未映射的环境事实先冻结权威合同，不用 ESM 兜底。

允许直接采用统一 Command → 获准 UE 领域 Owner 的本地路径。只有需要已审核具身交互合同的动作才使用相应适配器；不使用 ESM 也须遵守同一授权、证据、提交、暂停和回放规则。23 个 Owner 的完整部署与更新分类以[UE 协作与节奏矩阵](01-UE本地提交与Paralls同步.md#ue-cadence-matrix)为准。

<a id="esm-scheduling-boundary"></a>

## 建设顺序与兼容底线

ESM 只是可选适配/复用路径，不能为了等待适配阻塞既定正式 Owner 合同；不能以 SDK、ESM、Godot 迁移或模块复用重新开放旧事实写入口。原基础设施建设顺序中的技术底线保留：先有事件/时间/恢复与 Command 合同，再由获准领域进入实时和 Agent 链。当前批次/切片的正式依赖见生产计划。
