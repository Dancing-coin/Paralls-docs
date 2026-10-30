# 04-多精度与Handoff

> 版本：1.0（职责拆分版）
> 更新日期：2026-10-30
> 评审状态：职责归位与静态一致性核对；不替代产品待决项裁决或实现评审。
> 实现状态：本篇为目标合同；已有实现仅按原始证据日期记录，不代表全量实现或运行验收完成。
> 验证范围：本轮仅重组文档，未执行代码、UE、PIE 或性能验证。原始设计、实现盘点和证据日期分别保留。

[技术架构入口](../README.md) · [唯一 Owner 注册表](../03-Owner领域/01-Owner注册表.md#owner-registry)

<a id="handoff"></a>

## 精度与权威交接的总合同

认知 C 轴和表现 P 轴独立；不是每个高表现对象都运行完整 Agent，也不是 Agent 激活就取得任意身体/事实写权。这里的协议是目标合同，SGC-3 真实链路仍需要独立运行证据。

历史 spec 的“UE Owner”统一细化为具体获准领域 Owner；其中身体/死亡事实归 Body、Status、LifeState 对应写入口。ready 只表示预热完成，成功的 handoff receipt 和 fencing 才允许新推进者生效。

<a id="fidelity-axes"></a>

## 双轴精度与组合矩阵

- UE 的动画播放不是 Agent 已经完成行动的证明；只有领域 Owner 的 settlement receipt 才能确认行动结果。

### 两条激活轴

### 认知轴：Agent Fidelity

| 级别 | 名称 | 运行内容 | 适用对象 |
|---|---|---|---|
| C0 | dormant | 不运行独立 Agent；保留可恢复身份和最小状态摘要 | 未进入战区的普通人口、已释放的远场成员 |
| C1 | batch_reasoned | 由 Paralls 批处理群体状态，按固定 cadence 产生群体级意图候选 | 远场普通士兵、运输队成员、援军大部队 |
| C2 | agent_prepared | 预热上下文和可见性摘要，不读取私有记忆，不推进身体或世界状态 | 即将进入中场/近场的角色 |
| C3 | agent_active | 运行角色 L1–L4；输出语义意图和执行语义 | 队长、传令兵、玩家附近关键角色、重要将领 |

认知轴必须复用 Paralls 现有 `ActivationPolicy`、`ProfileActivationAuthority` 和 `PopulationPresenceAuthority` 的边界。SGC-3 当前仍是 `proposed`，因此第一阶段只能把它作为接入目标，不能声称现有 Paralls 已提供完整生产级 handoff。

### 表现轴：UE Presentation Fidelity

| 级别 | 名称 | UE 表现 | 物理/交互能力 |
|---|---|---|---|
| P0 | far_marker | 地图图标、队伍旗标、数量/状态摘要、低频路线段 | 不生成单人碰撞；由战场/物流 Owner 结算群体移动 |
| P1 | mid_proxy | 轻量代理、队伍级移动、局部避让、简化攻击/运输动画 | 代表性碰撞和空间占用；不拥有真实伤害结算 |
| P2 | near_actor | 完整 `AActor`/`ACharacter`、骨骼动画、局部寻路、近场感知、可交互目标 | UE 负责近场移动、碰撞、战斗接触和表现反馈 |
| P3 | focal_actor | 近景完整角色、语音/表情/道具挂点、玩家可追问和可观察回报 | 仍不改变领域 Owner；适用于玩家、队长、重要将领和当前传令兵 |

### 组合矩阵

| 认知 \ 表现 | P0 far_marker | P1 mid_proxy | P2 near_actor | P3 focal_actor |
|---|---|---|---|---|
| C0 dormant | 允许；群体状态摘要 | 允许；仅被动表现 | 不允许，必须先预热/激活 | 不允许 |
| C1 batch_reasoned | 默认组合；远场批处理 | 默认组合；队伍级意图投影 | 允许稳定存在；普通守军由编队执行器驱动，有独立语义交互需求时申请 C3 | 不允许 |
| C2 agent_prepared | 允许，不能写入世界 | 允许，等待执行权 | 允许预热后再申请 handoff | 仅等待 handoff，不接受玩家语义互动 |
| C3 agent_active | 允许；Agent 可为近场目标提前思考 | 允许；Agent 与代理表现异步对齐 | 进入玩家视野后必须启用 Agent-to-Animation 通道 | 重要角色默认组合，必须启用 Agent-to-Animation 通道 |

<a id="continuity-state"></a>

## 完整连续性状态 schema

- 产生诊断日志，不以桥接成功冒充领域结算成功。

### 统一状态模型

每个可被单独识别的角色都拥有一份跨系统的连续性记录。第一阶段至少包含：

```json
{
  "character_id": "char:county:commander-01",
  "population_group_id": "group:county:guard-01",
  "role_ref": "role:county_commander",
  "owner_scope": "army:county",
  "identity_revision": 3,
  "world_tick": 18420,
  "world_mode_revision": 7,
  "cognitive_fidelity": "C3",
  "presentation_fidelity": "P3",
  "presence_revision": 12,
  "body_revision": 9,
  "command_revision": 27,
  "action_revision": 31,
  "location_ref": "space:county:keep-command-yard",
  "location_revision": 44,
  "current_action_ref": "action:escort-messenger-0008",
  "embodiment_lease": {
    "lease_id": "lease:char:county:commander-01:31",
    "holder": "ue.near_actor",
    "epoch": 5,
    "expires_at_world_tick": 18480
  },
  "intent_lease": {
    "lease_id": "intent:char:county:commander-01:31",
    "holder": "paralls.character_agent",
    "epoch": 5,
    "expires_at_world_tick": 18450
  },
  "last_handoff_id": "handoff:0008",
  "last_receipt_id": "receipt:0008",
  "knowledge_cut": 18390
}
```

字段约束：

- `world_tick` 只能来自 UE 战场时钟；暂停时保持不变。
- 每次状态提交都要声明读到的 revision；过期写入必须返回 `stale`，不得静默覆盖。
- `location_ref` 是空间事实引用，不允许用表现层插值坐标替代。

<a id="handoff-protocol"></a>

## 触发、请求、快照、lease 顺序与失败恢复

- `knowledge_cut` 表示角色实际可用的信息截止点，禁止因 UE 发送了全局快照而让角色获得全知。

### Handoff 协议

### 触发条件

表现升级：

- 玩家相机进入角色可见半径；
- 玩家能与角色对话、观察、攻击或被角色攻击；
- 运输队进入可拦截区域；
- 近场碰撞、火灾、围城器械或道路堵塞需要真实空间处理。

表现降级：

- 角色离开观察/交互半径并持续一个稳定窗口；
- 近场战斗结束且没有待结算接触；
- 代理预算不足，需要释放完整 Actor；
- 角色已完成当前动作并回到可批处理状态。

认知升级：

- 角色成为玩家可直接追问的关键回报者；
- 队长/重要将领需要根据私有记忆和动态状态自主决策；
- 中场代理需要解释性意图而非单一群体脚本。

认知降级：

- 角色脱离战区或只需作为群体成员参与结算；
- 连续多个决策窗口没有独立判断价值；
- 角色已完成 handoff 合并并释放私有执行预算。

### Handoff 请求

```json
{
  "message_type": "character_fidelity_handoff_request",
  "handoff_id": "handoff:county:messenger-0008",
  "character_id": "char:county:messenger-08",
  "from": {"cognitive": "C1", "presentation": "P1"},
  "to": {"cognitive": "C3", "presentation": "P3"},
  "world_tick": 18420,
  "world_mode_ref": "county_siege_day_03",
  "world_mode_revision": 7,
  "expected_revisions": {
    "presence": 12,
    "location": 44,
    "command": 27,
    "action": 31
  },
  "snapshot_ref": "snapshot:handoff:0008",
  "handoff_reason": "player_observation_and_interaction",
  "requested_lease_holder": "ue.near_actor",
  "correlation_id": "siege-day-03-player-observation",
  "idempotency_key": "handoff:char:county:messenger-08:12:44"
}
```

### 快照内容

快照必须分为“可共享状态”和“私有认知状态”：

**可共享状态：**

- 身份、编制归属、角色职责和外显姓名；
- 世界 tick、所在空间引用、速度/行动阶段的领域摘要；
- 当前命令、命令有效期、命令 revision 和传令链状态；
- 伤病、疲劳、负重、装备和可执行能力的战场摘要；
- 当前阵型/队伍/运输任务、目标引用和待处理事件；
- 最近一次 UE settlement receipt、未完成动作和恢复策略。

**仅 Paralls 可见的私有状态：**

- 角色私有记忆、关系判断、未公开秘密、主观信念和信息不确定性；
- 角色实际听见/看见/被告知的事实集合；
- L1–L4 的解释、规划和执行上下文。

UE 只能请求一个 privacy-filtered projection，不能读取或生成私有记忆快照。预热阶段不得加载私有记忆；只有获得 Paralls 认知激活资格并完成 owner-bound handoff 后，角色才进入 C3。

### Lease 与交接顺序

1. 当前身体推进者创建 handoff 请求并锁定 `expected_revisions`；认知 lease 是否迁移要单独声明。
2. 接收方校验身份、时间、版本、privacy scope 和能力。
3. 接收方仅准备资源并回复 `ready`，尚未获得写入权；准备期间原推进者继续负责世界执行。
4. 在明确的世界 tick 边界，原推进者排空至该边界的结果并提交最终快照；UE lease 登记在自身同一提交点校验旧 epoch/revision、撤销旧 lease、授予新 lease，epoch 递增。这里仅保证 lease 登记的原子替换，不承诺跨领域全局事务。
5. 接收方查询到已提交的 handoff receipt 后才开始推进；所有世界写入都由领域 Owner 校验 epoch，旧推进者的迟到写入必须被拒绝。Agent 的 `intent_lease` 可保留在 Paralls，不随 Actor 表现升级转移。
6. 桥接层分发 `handoff_receipt` 和 lease 投影。通知丢失时查询原 handoff，不重新创建角色或猜测交接结果；提交前失败保留旧 lease，提交后失败按新 epoch 恢复。

任何时刻都不允许 UE 近场 Actor 和 Paralls Executor 同时拥有同一角色的世界状态写入权。通常 C3 角色由 Paralls 保留动作意图权，UE Actor 持有唯一 embodiment lease，把语义动作映射为连续移动/动画并处理碰撞和结算。表现层可以继续播放已确认的尾动画，但必须标记为 `presentation_tail`，不能产生新的语义行动或世界写入。

### 失败和恢复

| 情况 | 处理 |
|---|---|
| 版本过期 | 返回 `stale`，保留旧事实，重新拉取最新投影后重试 |
| Embodiment lease 冲突 | 拒绝第二个世界推进者，查询当前 lease；旧 lease 超时前不得抢占 |
| Agent intent lease 失效 | 停止接收该 Agent 的新动作意图，保持最后一个有效动作至其 TTL，到期后进入明确安全状态并通知角色 |
| 桥接断线 | UE 使用本地战术脑和已确认命令继续短时降级；Paralls 恢复后从 cursor 补发 |
| UE Actor 创建失败 | 保持 P1/P0 表现，认知仍可为 C3；记录 `presentation_unavailable` |
| Paralls Agent 激活失败 | 保持 C1/C2，UE 使用本地战术脑；不伪造 C3 角色判断 |
| 结算请求超时 | 状态未知，不自动回滚；通过原 `request_id` 查询 receipt |

<a id="activation-contract"></a>

## 群体升级、降级与游标

### Activation / Handoff

- B0/B1 只推进低精度状态、候选和升级信号；
- C2/C3 Agent 负责需要记忆、关系、判断和自主意图的角色；
- 同一角色同一时间窗口只能有一个推进者；
- 激活前固定来源 revision 和连续性游标；过期则 requeue；
- 退出高精度时保留已确认结果、未决意图、义务、失败原因和记忆游标；
- 玩家视野内或承担关键任务的角色必须维持可控制语义动画，而不是只播放预制循环。

<a id="authority-migration"></a>

## 领域迁移、并发结算与中断边界

### 结算位置、交接和失败边界

- UE-local 是正式权威实现的部署选择，并非只能做特效，也不需要先等远端重新算一遍伤害。Combat、Body、Equipment、Status 可共同部署在 UE 内，本地按各自规则产生授权 fragment，再向唯一 canonical EventStore 提交；确认提交前的反馈必须保留 pending/predicted 标记。
- 使用 GAS/AttributeSet/GameplayEffect、Blueprint 或 C++ 均可，但它们须实现指定 Owner 的受控规则/写入口或仅消费投影；不能一边由 GAS 改生命，一边由 Body 再扣同一次伤害。回放应用已提交事件，不重新执行命中检测、随机伤害或物资消耗。
- 执行租约与事实写权分别管理。角色 Agent 或群体模拟换执行方不自动更换 Body 写权；确需迁移 UE/后端权威时，须冻结旧写入口、排清已提交与未知结果、交接 revision/checkpoint/效果下一 tick 游标，再提升 `authority_epoch` 并启用新写入口。迁移失败则保持冻结或恢复旧方，不能两方同时推进。
- 攻击伤害、流血 tick、自然恢复和治疗对 Body 数值的写入共享 Body 的串行 revision/CAS 写入口。Status 先提交或授权对应效果 tick，再以 `effect_id + scheduled_world_tick` 向 Body 发起幂等结算请求；治疗步骤以 `treatment_id + step` 去重。相同时间点采用版本化的稳定结算顺序。死亡由 LifeState 根据 Body 等域依据提交，Body 对普通治疗的准入必须固定并验证 LifeState revision；同批次已有死亡授权时也必须拒绝普通治疗。复活若存在须独立规则，不能被延迟回血意外触发。
- 治疗瞬时生效可采用 Inventory/Body/Status 授权批次；长时包扎、服药和护理应先预留物资，在实际消耗节点提交，后续效果按方案推进。中断时只释放未消耗预留，保留已用药物和已发生效果；“止血”“恢复生命”“伤口愈合”是独立结果，不能用治疗动画完成一次性全改。
- 暂停屏障覆盖 UE Owner、Timer、效果 tick 和异步回调；恢复时验证 epoch、revision 和证据时效。提交结果未知时先查询幂等记录并对账，不能再次扣血/用药，也不能仅凭本地预测宣布死亡或胜利。

全量 23 Owner 的近场 UE 需求、事件与窗口分类以[UE 协作与节奏矩阵](../05-运行时接入/01-UE本地提交与Paralls同步.md#ue-cadence-matrix)为准。下表是部分领域接入示例，不是冻结名单。ESM 不作为统一路由；仅复用审计通过的交互合同，Godot 执行器需 UE 原生替换，旧写权须按域迁移。

<a id="cross-host-handoff"></a>

## 近远场四步交接与持续条件

### 交接顺序

1. 停止旧推进者接收新工作，固定交接边界与输入。
2. 结清连续积分/效果窗口，保存已确认事件、未决命令、开放义务与游标；未知结果先查清或显式带入恢复状态。
3. 通过 authority epoch/lease fencing 失效旧写入口，再启用新推进者；跨提交端交接按正式恢复协议执行。
4. 新推进者从同一角色身份和确认 revision 恢复；迟到旧命令拒绝，动画按当前语义计划续接或合法中断。

镜头离开不等于可无条件关闭角色：仍在视野、关键任务、战斗、交互或交接中的角色依注册矩阵保持需要的语义执行与表现。玩家暂停时这些路径同样服从时停。

<a id="handoff-safety"></a>

## 断线和控制权的适用边界

同一角色/窗口只能有一个推进者；旧命令、旧 lease 和旧 authority epoch 均受 fencing。C2 预热不能读取未获准私有记忆；未知提交结果先查询或作为开放恢复状态带入，不可丢弃。

控制权移交不改变角色身份，不会自动迁移 Body 等领域事实写权；身体/领域写权迁移必须单独完成 Manifest、提交端和 epoch 交接。断线只允许在登记的 fallback 权限、有效 lease/TTL 和已准入计划内安全继续；不能为“本地战术脑”默许无限产生新的 C3 自主策略。
