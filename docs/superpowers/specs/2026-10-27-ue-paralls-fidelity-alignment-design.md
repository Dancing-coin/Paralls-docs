> 文档状态更新：2026-10-30。历史技术设计草案；本文不是当前实现证据。UE-only时钟、泛称UE Owner和自动fallback等冲突表述按正式architecture契约与设计待决记录理解。 当前规格见[PRD导航](../../PRD/README.md)；[县城执行计划](../../production/县城守城Demo执行计划.md)。技术唯一维护入口见[README](../../architecture/README.md)。

# 《国殇：汉末》UE–Paralls 角色 Fidelity 与 Handoff 对齐设计

**状态：** draft，待评审  
**日期：** 2026-10-27  
**适用阶段：** 第一阶段县城战争 Demo  
**适用运行时：** Unreal Engine 5.8 + 本地 `paralls-phase-0-demo` CharacterAgent / Siming / Population Continuity

## 1. 目的

第一阶段 Demo 同时需要两件事：

1. 世界中有可观察、可移动、可被攻击和被玩家命令影响的军队与运输队；
2. 重要角色仍然由 Paralls 的角色智能体根据身份、人格、动态状态、所知信息和当前命令作出判断。

如果把“Agent 是否激活”和“UE 是否生成完整动画 Actor”当成同一个开关，远场会产生大量不必要的角色运行时开销，近场转入时又会出现身份、命令和位置跳变。反过来，如果两边完全独立，玩家会看到角色正在执行一个动作，而 Agent 仍认为角色处于另一状态，或者同一角色被两个系统同时推进。

本设计采用：

> **认知轴与表现轴分离，连续性合同统一。**

Agent 激活决定角色是否拥有独立的认知与决策节奏；表现激活决定 UE 为角色提供什么粒度的空间、动画和交互表现。两轴可以组合，但所有组合必须共享同一角色身份、世界时间、状态 revision、命令/意图引用和执行权 handoff。

## 2. 目标与非目标

### 2.1 目标

- 让同一 `CharacterRecord` 可以在远场批处理、中场轻量代理、近场完整 Actor 之间迁移而不换人。
- 让 Paralls 的角色判断、UE 的战斗/移动/资源结算和 UE 的动画表现各有明确 Owner。
- 让玩家暂停时进入全局时停：Agent、动画、运输、生产、伤病、命令传递和 handoff 都停止推进；恢复后从同一世界时间继续。
- 让近场角色在玩家站位阻挡、运输遇袭、命令失效、角色违背预期等情况下表现为可解释的世界结果，而不是动画层硬修正。
- 为第一阶段县城战争提供可验证的援军、运输队、普通士兵、队长和重要将领对齐场景。

### 2.2 非目标

- 本文不实现新的 Paralls 世界真相 Owner、第二套时钟、第二套人口调度器或新的全局 Presence 系统。
- 本文不让表现层决定语义意图、伤害、死亡、资源损失、道路占用或命令是否成功。
- 本文不要求第一阶段为每名远场士兵创建完整 `ACharacter` 或完整 CharacterAgent。
- 本文不把 Paralls 当前 Godot 表现链路直接移植为 UE 代码；Godot 文档只作为边界参考。

## 3. 核心原则

### 3.1 对齐什么

下面五项必须统一对齐：

| 对齐项 | 唯一事实来源 | 说明 |
|---|---|---|
| 身份 | 角色/编制身份目录 | `character_id`、编制归属、继任关系不能因转层生成新身份 |
| 世界时间 | UE 战场时钟投影 | 暂停时不前进；Paralls 不用 wall-clock 推进角色或批次 |
| 状态版本 | 领域 Owner 的 `revision` | 位置、命令、身体、士气、阵型、行动阶段分别带 revision |
| 世界执行权 | UE embodiment lease | 同一角色同一时刻只有一个世界状态写入者；Paralls 不与 UE 双重推进位置/身体/战斗事实 |
| 动作意图权 | 当前 intent lease | C3 Agent 可持有角色动作选择权；UE 玩家控制、强制受击/失能等可按明确优先级临时中断 |
| 交接结果 | handoff receipt | 转层成功、拒绝、过期、冲突和重试都可追踪、可幂等重放 |

### 3.2 不统一什么

- Agent 激活不是表现激活。
- 近场完整 Actor 不是语义 Owner。
- `presentation_plan` 不是世界事实，不能直接造成命中、死亡、资源消耗或路径占用。
- Agent 的 `semantic_intent` 不是 UE 的自动执行许可；UE 必须重新校验能力、目标、通信、版本和当前战场事实。
- 玩家视野内已激活角色的动画选择必须表达该 Agent 当前的行动意图和身体反馈；UE 将其映射为本地动画并处理可行性、混合、碰撞和物理约束。
- UE 的动画播放不是 Agent 已经完成行动的证明；只有领域 Owner 的 settlement receipt 才能确认行动结果。

## 4. 两条激活轴

### 4.1 认知轴：Agent Fidelity

| 级别 | 名称 | 运行内容 | 适用对象 |
|---|---|---|---|
| C0 | dormant | 不运行独立 Agent；保留可恢复身份和最小状态摘要 | 未进入战区的普通人口、已释放的远场成员 |
| C1 | batch_reasoned | 由 Paralls 批处理群体状态，按固定 cadence 产生群体级意图候选 | 远场普通士兵、运输队成员、援军大部队 |
| C2 | agent_prepared | 预热上下文和可见性摘要，不读取私有记忆，不推进身体或世界状态 | 即将进入中场/近场的角色 |
| C3 | agent_active | 运行角色 L1–L4；输出语义意图和执行语义 | 队长、传令兵、玩家附近关键角色、重要将领 |

认知轴必须复用 Paralls 现有 `ActivationPolicy`、`ProfileActivationAuthority` 和 `PopulationPresenceAuthority` 的边界。SGC-3 当前仍是 `proposed`，因此第一阶段只能把它作为接入目标，不能声称现有 Paralls 已提供完整生产级 handoff。

### 4.2 表现轴：UE Presentation Fidelity

| 级别 | 名称 | UE 表现 | 物理/交互能力 |
|---|---|---|---|
| P0 | far_marker | 地图图标、队伍旗标、数量/状态摘要、低频路线段 | 不生成单人碰撞；由战场/物流 Owner 结算群体移动 |
| P1 | mid_proxy | 轻量代理、队伍级移动、局部避让、简化攻击/运输动画 | 代表性碰撞和空间占用；不拥有真实伤害结算 |
| P2 | near_actor | 完整 `AActor`/`ACharacter`、骨骼动画、局部寻路、近场感知、可交互目标 | UE 负责近场移动、碰撞、战斗接触和表现反馈 |
| P3 | focal_actor | 近景完整角色、语音/表情/道具挂点、玩家可追问和可观察回报 | 仍不改变领域 Owner；适用于玩家、队长、重要将领和当前传令兵 |

### 4.3 组合矩阵

| 认知 \ 表现 | P0 far_marker | P1 mid_proxy | P2 near_actor | P3 focal_actor |
|---|---|---|---|---|
| C0 dormant | 允许；群体状态摘要 | 允许；仅被动表现 | 不允许，必须先预热/激活 | 不允许 |
| C1 batch_reasoned | 默认组合；远场批处理 | 默认组合；队伍级意图投影 | 允许稳定存在；普通守军由编队执行器驱动，有独立语义交互需求时申请 C3 | 不允许 |
| C2 agent_prepared | 允许，不能写入世界 | 允许，等待执行权 | 允许预热后再申请 handoff | 仅等待 handoff，不接受玩家语义互动 |
| C3 agent_active | 允许；Agent 可为近场目标提前思考 | 允许；Agent 与代理表现异步对齐 | 进入玩家视野后必须启用 Agent-to-Animation 通道 | 重要角色默认组合，必须启用 Agent-to-Animation 通道 |

**关键判断：** 认知和表现的级别可以不同，但共享的 `character_id`、`world_tick`、`state_revision`、`action_ref` 和 `handoff_id` 必须一致。任何需要表现真实接触的行动，都由 UE 近场 Owner 执行并结算；任何需要角色判断的行动，都保留 Paralls 的认知上下文和动作意图权。

## 5. Owner 分工

### 5.1 UE Owner

UE/Guoshang 负责：

- 县城战场时钟、暂停/恢复和可观察的世界时间投影；
- 空间位置、局部寻路、碰撞、堵塞、近场避让和运输路线执行；
- 战斗接触、命中、伤害、死亡/失能、军旗、器械、资源货损等战场事实；
- 命令是否仍有效、目标是否可达、能力与通信条件是否满足；
- 将语义意图转成可执行战术动作，并产生唯一 settlement receipt；
- 近场 `AActor`、动画状态机、蒙太奇、IK、道具挂点和玩家可见反馈；
- 远场和中场表现的生成、释放、插值和回收。

### 5.2 Paralls Owner

Paralls 负责：

- 角色身份的私有认知、人格、记忆、动态状态和所知信息；
- L1 感知解释、L2 解释、L3 规划和 L4 执行语义；
- 自主判断、命令接受/拒绝/改写为可行意图的候选，以及解释性反馈；
- 在收到 UE 事实后更新角色私有时间线和记忆；
- 对角色的 `semantic_intent_id`、`constraints`、置信度和证据 provenance 负责。

Paralls 不负责写入 UE 世界真相，不直接设置位置、速度、骨骼、动画、碰撞、伤害、资源数量、军旗控制权或运输结果。

这里的“不直接设置动画”指 Paralls 不发送 UE 动画资产名、不操作 AnimInstance、不写骨骼或物理参数；它不表示 Agent 对角色动画没有控制权。对于玩家视野内已激活的角色，Paralls 必须通过语义动作和 presentation channel 决定角色“现在要做什么、朝向/姿态意图是什么、何时开始/停止或切换动作”。

### 5.3 共同桥接 Owner

Guoshang 中的 `UParallsBridgeSubsystem`（名称为实现建议）负责协议适配，但不取得领域事实 Owner：

- 传输结构化 envelope；
- 校验 `event_id`、`causation_id`、`correlation_id`、`revision`、privacy scope 和幂等键；
- 维护发送/接收 cursor、重连、重复消息去重和待确认 handoff；
- 将 Paralls 输出路由给对应 UE 领域 Owner；
- 将 UE 的事实和 receipt 回传给对应 CharacterAgent；
- 产生诊断日志，不以桥接成功冒充领域结算成功。

## 6. 统一状态模型

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
- `current_action_ref` 只表示当前执行计划引用，不等于行动已成功。
- `knowledge_cut` 表示角色实际可用的信息截止点，禁止因 UE 发送了全局快照而让角色获得全知。

## 7. Handoff 协议

### 7.1 触发条件

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

### 7.2 Handoff 请求

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

### 7.3 快照内容

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

### 7.4 Lease 与交接顺序

1. 当前身体推进者创建 handoff 请求并锁定 `expected_revisions`；认知 lease 是否迁移要单独声明。
2. 接收方校验身份、时间、版本、privacy scope 和能力。
3. 接收方仅准备资源并回复 `ready`，尚未获得写入权；准备期间原推进者继续负责世界执行。
4. 在明确的世界 tick 边界，原推进者排空至该边界的结果并提交最终快照；UE lease 登记在自身同一提交点校验旧 epoch/revision、撤销旧 lease、授予新 lease，epoch 递增。这里仅保证 lease 登记的原子替换，不承诺跨领域全局事务。
5. 接收方查询到已提交的 handoff receipt 后才开始推进；所有世界写入都由领域 Owner 校验 epoch，旧推进者的迟到写入必须被拒绝。Agent 的 `intent_lease` 可保留在 Paralls，不随 Actor 表现升级转移。
6. 桥接层分发 `handoff_receipt` 和 lease 投影。通知丢失时查询原 handoff，不重新创建角色或猜测交接结果；提交前失败保留旧 lease，提交后失败按新 epoch 恢复。

任何时刻都不允许 UE 近场 Actor 和 Paralls Executor 同时拥有同一角色的世界状态写入权。通常 C3 角色由 Paralls 保留动作意图权，UE Actor 持有唯一 embodiment lease，把语义动作映射为连续移动/动画并处理碰撞和结算。表现层可以继续播放已确认的尾动画，但必须标记为 `presentation_tail`，不能产生新的语义行动或世界写入。

### 7.5 失败和恢复

| 情况 | 处理 |
|---|---|
| 版本过期 | 返回 `stale`，保留旧事实，重新拉取最新投影后重试 |
| Embodiment lease 冲突 | 拒绝第二个世界推进者，查询当前 lease；旧 lease 超时前不得抢占 |
| Agent intent lease 失效 | 停止接收该 Agent 的新动作意图，保持最后一个有效动作至其 TTL，到期后进入明确安全状态并通知角色 |
| 桥接断线 | UE 使用本地战术脑和已确认命令继续短时降级；Paralls 恢复后从 cursor 补发 |
| UE Actor 创建失败 | 保持 P1/P0 表现，认知仍可为 C3；记录 `presentation_unavailable` |
| Paralls Agent 激活失败 | 保持 C1/C2，UE 使用本地战术脑；不伪造 C3 角色判断 |
| 结算请求超时 | 状态未知，不自动回滚；通过原 `request_id` 查询 receipt |
| 释放时仍有未完成近场动作 | 先完成或标记动作中断，再生成 `pending_merge`，不得直接丢弃动作 |
| 玩家位于运输路线 | 由 UE 空间 Owner 产生阻挡事实；运输队等待/改道/请求护送，动画表现服从新路线 |

## 8. 命令、意图与表现对齐

命令链仍为：

```text
玩家县令
  -> 亲卫/传令兵
  -> 营指挥头目
  -> 队/运输队/工坊负责人
  -> UE 领域 Owner 结算
  -> Paralls 角色解释与记忆回写
  -> UE 表现反馈
```

Paralls 输出沿用 `character_agent_execution` 的语义边界：

- 允许：`semantic_intent_id`、`semantic_action_id`、目标引用、约束、置信度、证据、因果和相关 ID；
- 不允许：位置、旋转、骨骼、动画名、速度、伤害、物理冲量、资源扣除和最终结果。

UE 收到意图后必须校验：

1. 命令是否仍在有效期内；
2. 目标是否仍可观测/可达；
3. 角色是否有执行能力、装备和通信条件；
4. 领域 revision 是否匹配；
5. 当前租约是否属于该执行者；
6. 当前战场事实是否允许执行。

通过后由 UE 产生 `accepted` receipt 和实际行动状态；不通过则产生 `rejected`、`stale`、`expired` 或 `owner_rejected` receipt，并将原因以角色可理解的事实回传。`accepted` 只表示请求被接纳，后续仍需 `started`、`progress`、`completed`、`interrupted` 或 `failed`；接纳回执不能释放任务、增加库存或把行动写成成功记忆。动画只显示已确认状态，例如“传令兵正在奔跑”“队伍正在转向”，不显示“命令一定成功”。

### 8.1 Agent-to-Animation 控制通道

玩家视野内、认知级别为 C3 的角色必须保持 `agent_animation_control = enabled`。Agent 是角色自主动作意图和表达选择的 Owner；UE 是动画资产映射、播放、物理约束和实际行动结算的 Owner。该保证也适用于可辨识的远处 P1 角色：可使用低精度姿态/动作类别表现，但必须独立绑定其 Agent，不能混入无法表达该角色意图的群体循环；P0 地图旗标不是身体动画。可见性不能让角色获得玩家相机看到的信息。

C3 激活与进入可见近场前必须通过 `animation_capability_manifest` 准入检查，确认该角色 capability 覆盖第一阶段允许的 locomotion、facing、posture、gesture、combat interrupt 和 safe-hold 语义，并绑定可用 UE 表现。缺少映射时不能宣称该 Agent 已在视野内获得动画控制：角色保持原 fidelity/代理形式，Agent 激活请求等待能力可用；若角色已经在场，则只允许显示最后一个安全状态和 unavailable 提示，不接纳新的自主动作意图。manifest 版本进入 handoff 和 receipt。

这一准入保证角色进入可见 C3 状态后，其有效动作一定存在可执行的表现映射；运行中遇到特定失败仍按中断/安全保持处理。控制链为：

```text
Paralls L3/L4 selected intent + actor_control_frames + presentation_plan
  -> UE AgentAnimationAdapter
  -> capability / state / revision validation
  -> UE AnimInstance / Motion Warping / locomotion / action montage
  -> movement/combat owner settlement
  -> actual state + receipt back to Paralls
```

Agent 的动画控制输出使用稳定语义字段，不绑定具体 UE 资产：

```json
{
  "character_id": "char:county:captain-03",
  "world_tick": 18420,
  "expected_revisions": {"body": 9, "action": 31, "location": 44},
  "action_ref": "action:withdraw-to-east-gate-04",
  "semantic_action_id": "battle.withdraw_to_fallback_line",
  "body_intent": {
    "locomotion": "run_cautious",
    "facing_target_ref": "space:east-gate",
    "posture": "guarded",
    "gesture": "signal_fall_back",
    "interrupt_policy": "interruptible_by_immediate_threat"
  },
  "intent_ttl_world_ticks": 30,
  "presentation_plan": {
    "phase": "begin",
    "priority": "commanded_action",
    "hold_until": "owner_receipt_or_interrupt"
  }
}
```

UE 的 `AgentAnimationAdapter` 按已注册映射把语义动作落到项目动画状态、蒙太奇、Motion Warping 和道具表现；缺失映射时返回 `presentation_unavailable`，不能静默改成与 Agent 意图相反的动作。UE 可以因碰撞、路径不可达、被击中、身体能力不足或动作被打断而约束/拒绝请求，并必须把实际状态和原因回传。UE 不得仅因队伍默认动画或脚本方便而覆盖 Agent 已接受的角色级动作意图。

对 C3 角色，语义意图有效且 UE 执行条件成立时，UE 必须按 Agent 意图驱动动画和动作表现；只有以下有明确事实依据的中断可以暂时覆盖它：

| 优先级 | 驱动来源 | 例子 | 恢复规则 |
|---:|---|---|---|
| 1 | UE 强制身体事实 | 被击中、倒地、失能、死亡、碰撞阻挡、身体能力不足 | UE 产生中断事实与 receipt，回传 Agent；Agent 基于新状态重新选择动作 |
| 2 | 玩家直接控制 | 玩家接管角色移动或攻击 | 玩家取得身体控制 lease；Agent 保留观察/建议，不继续驱动身体动画；释放后重新请求 intent lease |
| 3 | Agent 当前有效意图 | 奔跑到目标、转身、保持戒备、挥手传令、攻击或撤退 | UE 按该意图持续表现，直到更新、完成或发生更高优先级中断 |
| 4 | 被动环境表现 | 呼吸、轻微站姿变化、衣物/马匹 idle | 仅填补无动作意图的空档，不能改变角色行动方向 |

命中、死亡等 UE 强制动画只覆盖被中断的身体通道，不取得角色的认知/意图 Owner；事实回传后 Agent 可选择继续、撤退、求援或其他符合角色状态的行动。多个意图同时到达时按 `action_revision` 和 `expected_revisions` 判定新旧，不能用消息抵达顺序决定胜负。

动画通道按 world tick 消费带 revision 的增量，支持 `begin`、`update`、`hold`、`interrupt`、`complete`。每个动作必须能由当前共享状态重建，避免网络延迟后播放过期蒙太奇。Agent 改变行动时应提交新 `action_ref` 和增量；UE 只在验证通过后切换。动画到达结束帧只产生表现事件，不代表领域动作成功。

对玩家视野内 C3 角色的明确规则：

- C3 角色进入视野时必须先通过 animation capability manifest 并准备好 AgentAnimationAdapter 或兼容的 P1 语义表现通道，再展示可控角色；不能展示后再等待下一次 0.5 秒普通轮询。近场表现不能继续只由队伍循环动画驱动。
- 普通成员若没有独立 C3 Agent，可以由队伍/编队控制；但任何已激活且在视野内的 C3 成员，其个体动画和动作状态必须服从自己的 Agent 意图。
- C3 Agent 不需要每帧输出。未变化时 UE 保持最后一个已确认的 `hold` 状态，并按 UE 本地移动/动画时钟连续播放；暂停时动画时钟冻结。
- `hold` 不是无限期许可：每个 Agent 控制增量带 `intent_ttl_world_ticks`，收到更新、完成或中断回执后刷新/终止；到期后进入明确的安全保持状态并请求 Agent 刷新，不能无限重播旧动作。
- 角色正在移动时，Agent 的朝向、移动/姿态语义必须驱动 UE 动画选择；UE 可求解路径与速度，不可把语义目标替换成另一个行为。
- Agent 通道暂时断开时，保持最后一个安全且已确认的动作直到 intent TTL 到期，停止接纳新的角色自主动作；到期后切到明确的本地安全保持动作，并给该 Agent 返回降级原因。不可继续播放看似新决策的循环动画。
- 如果 C3 角色已在玩家视野中，但 UE 缺少该语义动作的动画映射，不得悄悄降级为无关动作；保持上一个安全动作并报告 `presentation_unavailable`，待映射可用或明确切入本地安全状态。
- 玩家直接控制角色时，玩家输入优先于 Agent 的自主身体命令；Agent 可继续观察和建议，但不可争抢身体控制 lease。

## 9. 暂停/时停规则

暂停是 UE 战场时钟的全局冻结，不是只停玩家输入：

- `world_tick` 不增加；
- Agent cadence 不运行，模型不产生新的决策；
- UE 移动、寻路、碰撞、战斗、生产、伤病、运输、动画状态机和表现插值冻结；
- 暂停中只编辑尚未发出的命令草稿；已送出的命令是既成事实，改令/撤令要在恢复后作为新命令沿实际通信渠道传达，不得远程修改传令兵手中的旧命令；
- 未完成的 handoff 保持原 lease 和 pending 状态；
- 恢复时所有系统从同一 tick 继续，先处理版本/lease 校验，再传达暂停期间编辑的命令；
- 暂停界面可以显示已知状态和玩家计划，但不得揭示角色私有认知或未侦察敌情。

暂停建立统一提交屏障：冻结 tick、领域提交、角色认知回写、动画和 handoff 提交，递增 `control_epoch`。暂停前已发出的模型请求可能仍在计算，返回结果只可进入隔离队列，不能修改角色记忆/计划/世界事实；恢复后校验 `control_epoch`、请求身份、读集和取消状态，旧 epoch 的候选作废并按需要重新请求。暂停期间允许网络收包、查询已提交 receipt 和准备 UI 数据，但不能产生游戏进度。进程存活检测可用 wall-clock，恢复授权必须经屏障控制面记录，不能以 wall-clock 自动让 lease 到期或转移。

## 10. 第一阶段对象映射

| 对象 | 远场 | 中场 | 近场/焦点 | 认知默认 | 说明 |
|---|---|---|---|---|---|
| 援军大部队 | P0 队伍标记、预计抵达日 | P1 纵队代理、路线和旗标 | P2 进入县城/战场时切换 | C1，援军将领 C3 | 30 天前只需群体级结算；关键将领进入观察范围时升级 |
| 粮草/盐/木石运输队 | P0 货运任务和路线段 | P1 车队代理、堵塞/改道 | P2 被袭、拦截、护送 | C1；领队/传令兵 C3 | 货损由 UE 物流/战斗 Owner 结算，表现只投影结果 |
| 普通守军 | P0 队伍数量、士气、阵型 | P1 队形代理和局部避让 | P2 仅在玩家视野/交战点生成代表角色 | C0/C1 | 不为每人运行完整 Agent；身份可按队伍成员记录恢复 |
| 队长/工坊负责人 | P1 队伍代理 | P2 轻量角色 | P3 可追问、下达或解释命令 | C3 | 需要自作主张、拒绝失效命令和解释后果 |
| 重要将领/敌方指挥官 | P1 旗标/队伍代理 | P2 代理角色 | P3 完整角色、战斗和对话 | C3 | 近场动作必须由 UE 结算，Paralls 提供意图和解释 |
| 玩家角色 | 不降级 | P2 | P3 | 玩家控制 + C3 辅助 | 玩家输入优先；角色仍可执行已授权的自主判断 |

## 11. 典型流程

### 11.1 传令兵从城内出发

1. 玩家在暂停中下达“请求援军”命令，恢复后命令进入亲卫/传令链。
2. 传令兵由 P1/C1 进入实际出城路线；玩家可通过地图标记看到“已接令、正在前往东门”。
3. 玩家靠近传令兵时，表现升级为 P3，Paralls 申请 C3，加载其可见事实和私有记忆。
4. 玩家质问传令兵时，答案来自其真实 knowledge cut；若他只知道“东门守军已接令”，不得说成“援军已经出发”。
5. 传令兵离开交互范围后，先提交最后位置/行动/对话 receipt，再降级为 P1/C1。

### 11.2 玩家堵住粮车

1. 粮车在 P1 代理层沿 UE 路网移动。
2. 玩家和马匹占据路线，UE 产生 `route_blocked` 事实；运输任务进入等待、改道或请求护送之一。
3. 若敌方袭击车队，UE 生成战斗和货损事实；Paralls 只收到可见/可传达的结果，不直接决定损失数量。
4. 车队离开近场后，货物库存、任务状态和损失以物流 Owner 的 receipt 为准，P1/P0 只显示结果。

### 11.3 队长违背玩家意图

1. 玩家命令已传达，但目标已失效或队长根据角色状态判断原行动会导致全队覆灭。
2. Paralls 可输出 `withdraw_to_fallback_line` 或 `protect_standard`，附带约束、原因和置信度。
3. UE 校验该意图；若合法则结算为新行动，若不合法则拒绝并要求本地战术脑处理。
4. 玩家地图上看到实际执行状态，并可通过战报或追问获知“原目标已失效/侧翼暴露/通信中断”等自然原因。

### 11.4 反例推演表

| 情况 | 预期控制者/结果 | 必须留下的证据 | 防止的漏洞 |
|---|---|---|---|
| C3 队长由远处进入玩家视野 | 先准备表现绑定，再在有效 handoff 后显示 P1/P2；Agent 的动作意图立即驱动对应表现 | handoff receipt、action ref、当前 body intent | 不出现 Agent 已激活但队伍 idle 循环覆盖个人动作 |
| 玩家转身、遮挡或快速掠过角色 | 视野变化只创建表现降级候选；攻击/对话/动作尾段锁继续有效，离开宽限后再降层 | 可见性 epoch、lock 状态、降级 receipt | 一帧出视野就 despawn，角色正在说话/受击时消失 |
| Agent 输出“奔向东门”，但门被堵 | Agent 意图保留，UE 路径 Owner 返回 `blocked` 并报告可走替代路/无法通过；Agent 再选择等待、绕行或换目标 | path query revision、阻挡事实、后续 action ref | UE 偷偷改目标；Agent 误以为已到达 |
| Agent 只返回了 `accepted`，运输队尚未出发 | 任务保持 accepted/queued；只有 UE 产生 `started` 后才显示正在移动，只有 completed receipt 才记完成 | action lifecycle receipts | 接纳误报完成、库存或战报提前更新 |
| 命令失效时队长自主撤退 | 旧命令标记失效；队长新意图通过能力校验后由 UE 执行，玩家看到新行动并可追问理由 | 命令过期原因、新 action ref、receipt | “服从”规则逼角色继续执行无效/自杀命令，或无痕抗命 |
| 玩家直接接管 Agent 角色 | 玩家身体控制 lease 优先；Agent 仍可感知和给建议，交还后基于新身体/位置 revision 重做决策 | lease epoch、control mode transition | 玩家和 Agent 同时写移动/攻击，松手后回到过期目标 |
| 近场命中/击倒正在播放 Agent 动作 | UE 立即产生身体中断事实并临时覆盖动画；Agent 收到伤害/身体投影后选下一动作 | interrupt event、body revision、receipt | Agent 下一帧把受击动画顶掉，角色穿过受击/倒地状态 |
| Agent 通道延迟、重复或乱序 | 旧 revision 丢弃；重复幂等；当前安全动作保持至 TTL，超时后安全待机并提示降级 | sequence/revision、TTL、stale receipt | 旧“前进”覆盖新“撤退”；动作永久卡住 |
| 玩家暂停时 Agent 请求仍在模型计算 | 暂停提交屏障冻结游戏状态；旧 `control_epoch` 返回结果隔离，恢复后重校验，必要时重请求 | pause epoch、quarantine/drop reason | 暂停期间角色暗中决定或恢复时执行过期决定 |
| 近场动画映射缺失或 Actor 创建失败 | 进入 C3/可见近场前被 manifest 准入拦截；运行中 Actor 创建失败则保留可表达同一语义的 P1 表现，若映射也失败则只保持安全状态并标记 unavailable | presentation capability receipt | UI 声称 Agent 控制，但画面播放随便挑的动作 |
| 多个角色同时抢同一目标/门口 | 各 Agent 可提出意图；UE 空间/行动 Owner 统一排队、避让或拒绝，并将拥堵事实反馈给各角色 | target/space reservation revision、冲突 receipt | 两个角色占同一点、重复分配、动画互相穿插 |
| 角色死亡或失能 | UE 生存/战斗 Owner 提交事实并终止普通 intent lease；Agent 不能用下一条 `begin` 覆盖死亡；必要的临终表达走受限表现合同 | terminal state receipt、lease revoke | 死亡后 Agent 仍跑动/说话或被无声复活 |
| 角色刚进入视野但 handoff 尚未完成 | 暂不展示可交互/自主细节的近场角色；显示可信的旧代理或预热标记，receipt 成功后无跳变切入 | readiness、snapshot revision、handoff receipt | 可见角色没有 Owner 或仍展示陈旧状态 |
| 玩家只看见队伍，没有单人身份 | 维持群体 P1/P0；不临时编造可对话的成员身份；选择某成员个体化前先完成身份/Possession/Agent admission | group/member identity refs | 群体代理拆分后角色身份丢失或伪造记忆 |

本表是本设计的最低反例集。`accepted`/`started`/`progress`/`completed`/`interrupted`/`failed`、双 lease、`control_epoch` 和空间 reservation 都是本设计要求的对齐合同；它们不能仅因 Paralls 当前存在类似字段/机制就宣称已经被 UE 生产调用。

## 12. 转层触发与预算

第一阶段采用确定性规则，不使用每帧距离判断：

- 每 0.25 秒更新 UE 表现候选，但只在 0.5 秒决策窗口申请转层；
- `near_enter_radius`：玩家、敌对攻击者、可交互目标和当前镜头焦点的最大值；
- `near_exit_radius`：进入半径的 1.5 倍，避免边界抖动；
- `combat_lock`：近场战斗、命中确认、运输拦截和对话进行中禁止表现降级；
- `cognitive_interest`：Paralls 的角色重要性、未解决意图和玩家关注度可提高认知等级，但不能越过预算和 privacy gate；
- 远场批次按固定 world cadence 运行，不能使用进程调度顺序或 wall-clock 作为事实推进依据。

所有阈值应在 Data Asset/配置中版本化，并随 `policy_revision` 进入 handoff 审计。

### 12.1 激活后的持续条件

激活不是一次性事件，也不是“距离进入就永久保持”。系统分别计算认知保持锁和表现保持锁。只要保持锁仍有效，对应层级就不能释放；距离离开只会创建降级候选。

**Agent C3 持续条件，满足任一项即可保持：**

- 角色仍拥有未完成的语义行动、待结算意图或有效 execution lease；
- 角色正在被玩家追问、谈话、审讯、下达命令或作为当前战报来源；
- 角色是当前命令链的关键节点（县令、营指挥、队长、传令兵、工坊负责人或敌方重要将领）；
- 角色的私有认知仍影响一个尚未结算的行动，例如敌军主将已决定夜袭但还未进入执行阶段；
- 角色处于需要连续判断的战斗、撤退、护旗、护送、拦截或继任过程中；
- handoff 尚未完成、`pending_merge` 尚未提交或桥接断线仍在短时降级窗口内。

**Agent C3 释放条件，必须同时满足：**

- 没有未完成的语义行动、待结算 receipt 或有效 lease；
- 没有玩家交互、关键命令链职责或连续判断需求；
- 角色已提交最新共享状态、私有记忆回写和 `pending_merge` 结果；
- 经过 `agent_exit_grace_ticks` 的稳定窗口，期间没有重新触发保持锁；
- 新的认知层级已取得合法 activation/presence receipt。

**P2/P3 动画表现持续条件，满足任一项即可保持：**

- 角色在玩家视野、镜头焦点、交互半径或可攻击半径内；
- 角色正在播放不可瞬间截断的动作尾段，例如传递物件、上马、翻越、装填、受击硬直或倒地确认；
- 角色参与近场碰撞、战斗接触、运输拦截、道路堵塞、火灾或器械操作；
- 角色的空间占用会影响玩家或其他近场 Actor 的寻路；
- 对应的 `combat_lock`、`interaction_lock`、`physics_lock` 或 `presentation_tail` 尚未释放；
- 玩家刚离开范围但仍处于 `presentation_exit_grace_ticks`，用于避免边界抖动和画面跳变。

**P2/P3 释放条件，必须同时满足：**

- 离开观察/交互/攻击半径并超过退出滞后窗口；
- 没有近场战斗、碰撞、交互、动作尾段或空间占用责任；
- 当前动作已经提交 UE 领域 Owner 的结果，或已明确标记为中断并写入恢复策略；
- 共享状态快照和最后一帧表现状态已经写入 handoff；
- 新的 P1/P0 表现代理已创建并确认接管位置、行动阶段和旗标状态。

**双锁同时持续的情况：**

- 玩家正在和传令兵/队长/重要将领交互；
- 角色处于玩家可见的近场战斗，并且其自主判断会改变下一步行动；
- 运输队正在被玩家阻挡或遭敌袭，领队需要实时决策且车队需要真实碰撞；
- 角色动作尚未结算，例如命令已接受但队伍尚未完成转向或护旗；
- 角色正在完成继任、撤退或其他不可拆分的指挥交接。

**只有一侧持续的情况：**

- C3/P1：敌方主将距离很远，仍在根据斥候情报思考，但不需要生成完整人形；
- C1/P2：玩家近旁的普通守军有完整站立、行走和受击动画，但由队伍状态机驱动，不运行独立 Agent；
- C2/P1：即将进入视野的传令兵已预热公开上下文，但还没有取得 C3 lease，也不接受玩家语义互动。

因此，“激活角色智能体的动画表现持续”并不是看 Agent 是否还活着，而是看**角色是否仍有未完成的认知责任，以及 UE 是否仍有未完成的空间/表现责任**。两边责任都结束后才允许完整降级；任何一边仍有责任，另一边都必须通过共享 `action_ref`、`world_tick` 和 `handoff_id` 保持可重建的连续性。

## 13. 验证方案

第一阶段不以“画面上人都在动”作为完成标准，而以连续性和 Owner 边界的证据为准。

### 13.1 协议验证

- 同一 `character_id` 远/中/近转层不生成第二身份；
- duplicate `handoff_id` 和 `idempotency_key` 不重复创建 Actor、lease 或事实；
- stale `revision` 被拒绝并可从最新 snapshot 重试；
- embodiment lease 冲突不会出现 UE 与 Paralls 双重写入世界状态，intent lease 与玩家控制交接不会双重驱动身体；
- full replay 与 checkpoint + tail replay 得到同一 handoff/receipt 结果；
- handoff 准备失败、原子提交前失败、提交后通知丢失，都能查询唯一结果并恢复；
- prewarm 不读取私有记忆；
- presentation-only 输出不写入世界事实；
- 玩家视野内 C3 Agent 的 `body_intent` 经 UE 映射后能驱动姿态/移动/动作动画，队伍循环动画不能覆盖个体意图；
- Agent intent 被碰撞/能力/路径约束拒绝或中断时，UE 返回原因，动画与实际行动保持一致；
- Agent 通道断开时不会继续播放新的伪自主动作；暂停时 Agent intent 与动画时钟同时冻结。

### 13.2 时停验证

- 暂停 10 秒期间 `world_tick`、Agent cadence、运输位置、动画时间、战斗和 handoff 状态均不变；
- 暂停中修改的命令在恢复后才出现新的 `received`/`accepted` 事件；
- 暂停前发出的异步 Agent 请求在旧 `control_epoch` 下不能提交动作/记忆/表现状态；
- 恢复后不重复发送暂停前已确认的事件。

### 13.3 可玩场景验证

1. 玩家靠近传令兵：P1/C1 -> P3/C3，身份、位置、当前命令和知识边界连续。
2. 玩家离开传令兵：P3/C3 -> P1/C1，未完成行动进入 `pending_merge`，不丢失。
3. 玩家阻挡粮车：路线事实、等待/改道动画和最终货运结果一致。
4. 粮车遭袭：UE 结算货损，Paralls 只收到可见结果，P0/P1 显示同一库存结果。
5. 队长自主改变行动：地图、战报和角色解释引用同一 `action_ref`、`causation_id` 和 receipt。
6. 重要将领被击倒：UE 产生失能事实，继任和角色私有反馈按 revision 继续，不能由动画直接宣称死亡。
7. 玩家直接接管近场队长后松手：玩家 lease 释放、Agent 基于最新 revision 再决策、UE 动画重新服从新的 Agent 意图。

### 13.4 证据产物

- handoff 事件日志：`event_id`、`handoff_id`、旧/新 fidelity、lease epoch、revision；
- 近场 PIE 截图：传令兵、粮车、队长和重要将领各一张；
- 暂停前/暂停中/恢复后三段日志和世界 tick；
- UE settlement receipt 与 Paralls execution 回执对应表；
- 断线、stale、lease conflict、Actor 创建失败的定向回放记录。

## 14. 分阶段落地顺序

### 阶段 A：UE 独立灰盒

- 先实现 P0/P1/P2 表现层、UE 战场时钟、暂停、局部路网、运输堵塞和近场战斗；
- 用 `LocalTacticalBrain` 代替 Paralls，验证命令、事实、表现和 receipt；
- 不创建第二套角色真相。

### 阶段 B：单角色 C3 接入

- 选一个传令兵或队长作为唯一 C3 角色；
- 接入结构化 `character_agent_execution`，保留 UE 本地降级；
- 完成一个 P1/C1 -> P3/C3 -> P1/C1 的完整 handoff 与回放。

### 阶段 C：批次与关键角色扩展

- 将普通守军和援军接入 C1/P0-P1；
- 将敌方将领、援军将领、工坊负责人接入 C3/P3；
- 补齐队伍状态、运输任务和角色私有反馈的 owner-bound consumer。

### 阶段 D：第一阶段 Demo 验收

- 玩家收到敌来军情后求援并守城；
- 运输、生产、伤病和战斗在暂停/恢复中保持一致；
- 30 天援军到达获得阶段性胜利，或敌军提前溃退获得提前胜利；
- 县城失守后投降、死亡或逃跑均为失败结局；
- 所有可见报告都来自玩家能通过传令兵、斥候、观察和地图标记获得的世界内渠道。

## 15. 风险与待办

- **SGC-3 尚未闭合：** 需要在 Paralls 侧确定 cadence source 和一个 owner-bound consumer；未闭合前只做 UE 独立灰盒和单角色适配。
- **UE/Paralls 双推进：** 由唯一 embodiment lease 防止双写；C3 Agent 的 intent lease 只控制语义动作选择，必须先验证双 lease、epoch 和 receipt 查询，再扩大 C3 数量。
- **表现预算不足：** 远场优先队伍级代理和实例化表现，近场只保留玩家关注对象；不得用生成大量完整 Actor 解决可见性。
- **信息泄漏：** bridge 必须按 `knowledge_cut` 和 privacy scope 投影；调试日志可以完整，游戏 UI 不得直接展示私有字段。
- **动画与结算错位：** 动画状态必须可被中断、回放和从领域状态重建；不能以蒙太奇完成事件作为战斗成功条件。
- **网络/进程断线：** 第一阶段需要本地战术脑和 cursor 补发，但不允许把降级结果伪装成 Paralls 的自主判断。

## 16. 完成定义

本设计进入实现计划前，必须满足：

1. UE 与 Paralls 各自 Owner、禁止写入边界和消息方向已确认；
2. 至少一个角色完成真实 P1/C1 -> P3/C3 -> P1/C1 handoff；
3. 统一身份、世界 tick、revision、lease、receipt 和回放证据可查询；
4. 暂停是全局时停，且恢复后命令、Agent、运输和动画不会重复推进；
5. 运输堵塞/遇袭、命令失效、自主改令和近场战斗都有可见结果与可解释回报；
6. 不把 Paralls 当前 proposed 的 SGC-3 能力误报为已完成生产能力。

## 17. 参考

- Paralls：`docs/superpowers/specs/world-character-siming-authority-mainline/siming-group-world-formalization/03-sgc-3-population-fidelity-continuity-contract.md`
- Paralls：`docs/superpowers/plans/world-character-siming-authority-mainline/siming-group-world-formalization/03-sgc-3-population-fidelity-continuity-plan.md`
- Paralls：`docs/架构/运行时/模块/角色智能体.md`
- Paralls：`docs/架构/运行时/模块/Godot表现与角色入口.md`
- Guoshang：`docs/superpowers/specs/2026-10-21-mounted-charge-vertical-slice/2026-10-21-mounted-charge-vertical-slice-design.md`
