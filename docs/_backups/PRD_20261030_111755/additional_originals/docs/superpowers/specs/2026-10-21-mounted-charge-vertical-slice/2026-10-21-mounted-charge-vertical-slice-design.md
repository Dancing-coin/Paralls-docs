# 骑将冲阵垂直切片设计规格

**项目：**《国殇：汉末》  
**版本：** v0.1  
**日期：** 2026-10-21  
**适用引擎：** UE5.8（当前为 Strategy/TopDown 模板）  
**后端方向：** 保留接入 `paralls-phase-0-demo` 的 Python CharacterAgent / Siming / Authority Event 体系

## 1. 目标与体验

本切片只验证一个核心瞬间：玩家骑马冲入敌阵，同时通过亲卫队转发命令，改变敌我士气、阵型和一个关键目标的控制权。

玩家不是站在地图外发出全知命令，而是一个会移动的指挥节点。玩家亲自冲阵会带来局部战果和士气影响，但不能直接替代军队的指挥链、传令链或战场结算。

切片完成时，玩家应能清楚感受到以下因果链：

```text
骑将接近敌阵
  -> 亲卫队收到快捷命令
  -> 命令沿近距离指挥链转发
  -> 部队按训练程度和士气执行
  -> 冲锋接触改变阵型与士气
  -> 军旗/敌将/攻城器械的控制状态改变
  -> 若指挥官倒下，次高指挥官接管并继续执行当前预案
```

## 2. 垂直切片范围

### 2.1 场景

- 一张小型野外交战灰盒地图，包含平地、浅坡和一个可争夺的中央目标区。
- 玩家出生点、敌军出生点、双方后撤线各一个。
- 场景内有一面敌军军旗和一台敌方冲车。
- 不制作战略地图、攻城城墙、水战、外交、科技树或多人网络。

### 2.2 参战单位

| 编号 | 单位 | 数量 | 作用 |
|---|---|---:|---|
| P0-C | 玩家骑将/军队最高指挥节点 | 1 | 可骑马移动、冲锋，并通过亲卫队下达军令 |
| P0-BC | 玩家军营指挥头目 | 1 | 接收亲卫传令，选择预案并向营内三队分派任务 |
| P0-G | 玩家亲卫队 | 8–12 | 跟随玩家，作为近身护卫和传令节点 |
| P0-B1 | 玩家军第一队 | 20–30 | 跟随玩家冲锋发起正面进攻 |
| P0-B2 | 玩家军第二队 | 20–30 | 攻击敌军侧翼 |
| P0-B3 | 玩家军第三队 | 20–30 | 包抄敌军后方 |
| E0-H | 敌方指挥头目 | 1 | 决定敌军应对方案，可失能 |
| E0-B | 敌方军旗队 | 6–10 | 保护军旗；军旗是士气目标 |
| E0-S | 敌方冲车操作队 | 6–10 | 保护并操作冲车 |
| E0-L | 敌方主战队 | 20–30 | 形成基础阵型并根据士气自主反应 |

单位数量是灰盒上限，不要求每名士兵都拥有完整 CharacterAgent。近场角色使用独立 Actor，中场单位可使用简化代理；两者共享同一套军队状态和语义意图接口。

### 2.3 可玩时长

一次演示目标为 3–8 分钟。玩家应在前 30 秒内能够发出一次命令，在 2 分钟内看到至少一个阵型或士气结果，在 5 分钟内可能触发关键目标争夺或指挥继任。

## 3. P0 玩家操作

### 3.1 骑乘与冲锋

- 玩家使用第三人称骑乘角色移动。
- 具备待机、加速、冲锋、接触、受击、失能六种表现状态；动画可先使用占位蒙太奇。
- 冲锋结算由 UE 本地战斗权威完成：接触速度、攻击方向、目标阵型状态和玩家当前意图共同决定结果。
- Python/Paralls 不直接设置位置、骨骼、碰撞、伤害或马匹物理。

### 3.2 快捷命令

P0 保留用户提出的数字命令作为输入别名。玩家身边只有一队亲卫；玩家亲卫队是命令接收、确认和转发节点，营指挥头目是军队 AI 的决策节点，营内三队是命令的主要执行单位。命令链固定为“玩家骑将 → 玩家亲卫队 → 营指挥头目 → 营内目标队”。数字码只属于 UI 层，协议使用稳定的语义 ID。

| 快捷码 | 语义命令 ID | 目标 | 默认效果 |
|---|---|---|---|
| `10` | `follow_player_charge` | P0-B1 | 玩家亲卫转发给营第一队，跟随玩家并攻击当前冲锋目标 |
| `22` | `attack_flank` | P0-B2 | 玩家亲卫转发给营第二队，向目标侧翼移动并攻击 |
| `34` | `encircle_rear` | P0-B3 | 玩家亲卫转发给营第三队，绕行后方并优先威胁军旗或敌方指挥头目 |

输入流程：

1. 玩家按下两位数字码。
2. UE 将数字码解析成 `BattleCommandRequest`。
3. UE 验证玩家是否仍是当前军队的有效指挥节点，以及目标是否在玩家可观测/可指挥范围内。
4. 请求先进入玩家亲卫队，再由亲卫队转发给营指挥头目；P0 标准模式允许在距离和视线满足时快速传递。
5. 玩家亲卫队、营指挥头目和营内目标队分别产生 `received`、`accepted`、`rejected` 或 `expired` 状态，形成可追踪的传令链。

快捷码不可被 Python 重新解释。Python 可以返回语义意图，但必须使用协议中的 `semantic_intent_id`。

## 4. 军制预案

### 4.1 预案层级

P0 使用三层军制对象：

```text
军团（Army）
  └─ 营（Battalion）
      └─ 队（Company）
```

本切片只部署玩家的一营三队和一队玩家亲卫，但数据结构必须保留军团层。玩家亲卫属于玩家直属近身指挥节点，不计入营内三队。每层预案包含：

- `doctrine_id`：稳定 ID；
- `revision`：训练后的预案版本；
- `formation_template`：队形和间距模板；
- `command_priority`：目标优先级；
- `morale_response`：不同士气区间的行为；
- `fallback_route`：失序后的回归路径；
- `succession_order`：指挥继任顺序；
- `training_requirement`：临时修改或复杂动作所需训练等级。

### 4.2 P0 预案

- `doctrine_charge_wedge_v1`：营指挥头目令第一队跟随骑将正面冲锋，第二队等待侧翼窗口，第三队绕后；玩家亲卫队负责贴身护卫玩家并把军令送入营指挥链；
- `doctrine_banner_guard_v1`：优先保护己方军旗并保持防御阵；
- `doctrine_fallback_line_v1`：士气崩溃或指挥链中断时回撤到后撤线。

战前编辑器在 P0 中只需要显示预案名称、队伍任务、触发条件和继任顺序；可编辑值写入 Data Asset 或等价的版本化配置。战场中只能切换已训练预案，不能任意修改其内部参数。

### 4.3 临时修改的预留规则

P0 不开放完整临时改案，但必须保留校验接口：

```text
can_modify_doctrine(army_quality, commander_quality, communication_quality,
                   requested_revision) -> accepted | rejected(reason)
```

未来实现中，军队素质、指挥头目素质或通信质量不足时，临时修改会执行失败，并回退到最近一次有效预案；回退结果产生可审计事件，不抹掉原命令。

## 5. 士气、阵型和关键目标

### 5.1 士气

P0 每个队和敌方主战队拥有 `morale`，范围为 0–100。士气是状态结果，不是 Python 可直接写入的变量。

建议阈值：

| 区间 | 状态 | P0 行为 |
|---:|---|---|
| 75–100 | `steady` | 执行当前预案 |
| 45–74 | `shaken` | 执行预案但反应延迟增加、阵型更易被撕裂 |
| 20–44 | `wavering` | 指挥头目优先选择收缩、护旗或撤退 |
| 0–19 | `routing` | 进入溃退路径，停止复杂进攻命令 |

士气变化来源至少包括：

- 玩家骑将冲锋造成的局部冲击；
- 敌我指挥头目失能；
- 军旗被夺、失守或重新夺回；
- 侧翼被攻击、后方被包抄；
- 冲车损毁；
- 队伍伤亡和疲劳；
- 当前预案是否与现场目标冲突。

UE 负责根据战场事实结算增减和阈值转换；Paralls 只能根据收到的观察事实提出 `rally`、`withdraw`、`protect_standard` 等语义意图。

### 5.2 阵型

P0 使用离散阵型状态，不要求第一版实现复杂连续求解：

- `formed`：保持预案队形；
- `compressed`：受压收缩；
- `disrupted`：局部缺口或朝向失稳；
- `flanked`：侧翼暴露；
- `rear_threatened`：后方受威胁；
- `routing`：队伍失去有效阵型。

状态转换由接触方向、目标相对位置、士气和训练等级共同决定。阵型状态需要有 revision，便于拒绝过期的远端意图。

### 5.3 关键目标

关键目标是可被观察、争夺和结算的领域对象：

- `commander:<id>`：敌方指挥头目；
- `standard:<id>`：敌方军旗；
- `siege_engine:<id>`：敌方冲车。

夺旗、指挥头目失能和冲车损毁都必须先由 UE 产生战场事实，再由军队状态系统更新士气或预案。不能由表现层或 Python 直接宣称目标已被夺取。

## 6. 指挥头目与自动继任

### 6.1 指挥头目职责

每个军制节点有一个当前指挥头目。营指挥头目根据以下输入选择已训练预案或产生一个高层语义意图，并将其分派给营内三队：

- 当前可见战场事实；
- 本队士气和阵型；
- 军队训练程度与通信质量；
- 当前预案；
- 指挥官能力、性格和自我认知。

P0 本地 AI 只实现可解释的规则评分；后续 CharacterAgent 才接入更完整的 L1 感知、L2 理解、L3 规划、L4 执行合同。

### 6.2 继任流程

当当前指挥头目失去指挥能力时：

1. UE 发布 `battle.commander_incapacitated`，携带原指挥官、所属军制节点和当前 doctrine revision。
2. `UCommandHierarchyComponent` 根据预案中的 `succession_order` 找到首个仍具备指挥能力的候选人。
3. 新指挥官继承当前正在执行的预案和未过期命令，不自动清空队伍状态。
4. UE 发布 `battle.command_succession_resolved`。
5. 新指挥官在下一次决策窗口中，依据能力、性格和自我认知决定继续、收缩、护旗或撤退。
6. 若候选人全部失能，队伍进入 `leaderless`，只能执行预案中的最低复杂度动作或回归路径。

继任必须幂等：同一 `incapacitation_event_id` 重复到达时不能产生第二次继任。

### 6.3 “血性”预留

角色的“血性”属于自我/士气相关状态，不单独绕过指挥系统。P0 可把它作为 `self_drive` 特质参与规则评分：当队伍处于 `wavering`、关键目标可见且继任者仍有指挥资格时，可能触发 `rally_countercharge`。该结果仍需经过 UE 能力和当前预案校验。

## 7. 最小 AI 行为

### 7.1 本地战术脑

在未连接 Python 时，UE 使用 `LocalTacticalBrain`；连接 Python 后，仍保留同一输入/输出接口作为断线降级和回放确定性实现。

本地决策每 0.25–0.5 秒运行一次，禁止每帧重新规划。每次决策最多输出一个候选意图：

```text
hold_formation
follow_player_charge
attack_flank
encircle_rear
protect_standard
rally_countercharge
withdraw_to_fallback_line
assume_command
```

基础评分顺序：

1. `routing` 或无有效指挥官：优先回归路径/最低复杂度动作；
2. 关键目标受到直接威胁：优先护旗或保护指挥节点；
3. `flanked` / `rear_threatened`：优先收缩或转向威胁；
4. 士气稳定且当前预案匹配：继续当前预案；
5. 玩家命令已送达且未过期：按命令执行；
6. 其他情况：保持队形并观察。

### 7.2 训练和能力门槛

- `training_level` 影响命令接收延迟、阵型保持和复杂意图成功率；
- `commander_quality` 影响重新选择预案和临时修改资格；
- `communication_quality` 影响命令能否被附近亲卫队接收；
- 这些值只影响本地决策和 UE 结算，不能成为 Python 的任意写入入口。

## 8. UE–Paralls 适配边界

### 8.1 总体链路

```text
UE 战场事实
  -> UParallsBridgeSubsystem（WebSocket/HTTP 适配器）
  -> Python Paralls
       CharacterAgent / SimingRuntime / PopulationPlanner
  -> CharacterExecutionContract 或战场语义意图
  -> UParallsBridgeSubsystem
  -> UE 领域校验与战场结算
  -> UE 表现和回执
```

Transport 可以先实现 WebSocket；协议不绑定传输方式，未来可替换为本机 IPC、HTTP 或网络服务。

### 8.2 事件信封

UE 发往 Python 的事件沿用 Paralls `AuthorityEvent` 的字段语义：

```json
{
  "event_id": "evt-battle-000123",
  "event_type": "battle.commander_incapacitated",
  "producer_ts": 123456789,
  "room_id": "battle-room-01",
  "scene_id": "field-demo-01",
  "zone_id": "center",
  "source": {"layer": "ue_battle", "system": "BattleAuthority", "actor_id": "commander:player"},
  "routing": {"audience_mode": "scoped", "routing_mode": "targeted", "target_ids": ["army:player"]},
  "priority": "p0",
  "durability": "reliable",
  "causation_id": "evt-contact-000122",
  "correlation_id": "turn-charge-0007",
  "payload": {
    "battle_revision": 18,
    "commander_ref": "commander:enemy",
    "army_ref": "army:enemy",
    "incapacitation_reason": "wounded"
  }
}
```

约束：

- `event_id` 全局唯一；
- `causation_id` 指向直接原因，`correlation_id` 贯穿一次冲阵或命令回合；
- 事件必须带 `battle_revision` 或领域对象 revision；
- 事件是事实/观察，不是“请直接改世界”的命令；
- 断线重连时按 `event_id` 幂等去重。

P0 必须实现的事件类型：

- `battle.started`；
- `battle.command_issued`；
- `battle.command_received`；
- `battle.morale_changed`；
- `battle.formation_changed`；
- `battle.standard_state_changed`；
- `battle.siege_engine_state_changed`；
- `battle.commander_incapacitated`；
- `battle.command_succession_resolved`；
- `battle.intent_settlement_result`。

### 8.3 战场命令请求

```json
{
  "request_id": "req-command-00010",
  "battle_id": "battle-01",
  "turn_id": "turn-charge-0007",
  "issuer_ref": "commander:player",
  "source_input": {"kind": "keyboard_alias", "value": "10"},
  "semantic_intent_id": "follow_player_charge",
  "target_refs": ["unit:guard-1", "commander:enemy"],
  "doctrine_ref": "doctrine_charge_wedge_v1@3",
  "expected_revisions": {
    "battle": 18,
    "unit:guard-1": 7,
    "commander:player": 4
  },
  "issued_ts": 123456790,
  "expires_after_ms": 3000
}
```

UE 负责创建和校验 `BattleCommandRequest`。Python 可以读取该请求并提供候选解释，但不能篡改 issuer、目标、版本或有效期。

### 8.4 语义意图与执行合同

Python/CharacterAgent 返回的生产形态必须接近 Paralls 的 `CharacterExecutionContract`，并保持 authority-neutral：

```json
{
  "turn_id": "turn-charge-0007",
  "actor_ref": "commander:guard-2",
  "source_ref": "evt-battle-000123",
  "producer_ts": 123456791,
  "target_refs": ["standard:enemy-01"],
  "semantic_intent_id": "attack_flank",
  "semantic_action_id": "battle.attack_flank",
  "source_id": "character_agent_l4",
  "doctrine_ref": "doctrine_charge_wedge_v1@3",
  "expected_revisions": {"battle": 18, "unit:guard-2": 7},
  "confidence": 0.82,
  "constraints": ["requires_commander", "requires_target_visible"],
  "causation_id": "evt-battle-000123",
  "correlation_id": "turn-charge-0007",
  "idempotency_key": "turn-charge-0007:guard-2:attack_flank:1"
}
```

禁止字段包括：位置、旋转、骨骼、动画、速度、伤害数值、物理冲量、世界状态写入和最终结算结果。UE 收到意图后必须重新验证目标、能力、版本、通信和预案，验证通过才调用本地战斗执行器。

### 8.5 结算回执

UE 产生唯一的 `intent_settlement_result`，包含：

- `accepted`、`rejected`、`stale`、`expired`、
o_authority`、`owner_rejected`；
- 被接受的语义动作 ID；
- 使用的 battle/doctrine/unit revision；
- 产生的战场事实 ID 列表；
- 拒绝原因和下一步重试策略；
- `idempotency_key`。

只有结算回执和后续战场事实才能推动士气、阵型、军旗或器械状态。

## 9. Paralls 接入阶段

### 阶段 A：UE 独立灰盒

- UE 实现骑将、一队玩家亲卫、玩家一营三队、敌军、军旗、冲车、士气、阵型和继任；
- `LocalTacticalBrain` 产出与未来 Python 相同形状的语义意图；
- Bridge 可关闭，所有战斗仍可完整运行；
- 事件写入本地回放日志。

### 阶段 B：Python 旁路观察

- UE 发布 AuthorityEvent；
- Python 只消费 scoped 事件并返回建议；
- UE 继续使用本地 AI 结算；
- 对比本地决策与 Python 建议，不影响战斗结果。

### 阶段 C：Python 受控决策

- 仅允许 `hold_formation`、`protect_standard`、`withdraw_to_fallback_line` 等低风险意图进入准入表；
- UE 对每个意图进行版本、能力和目标校验；
- 拒绝或断线时自动回退本地 AI；
- 所有接受/拒绝结果进入回放。

### 阶段 D：近场 CharacterAgent

- 敌方指挥头目、玩家亲卫队长、玩家营指挥头目和继任者逐步激活完整 CharacterAgent；
- 角色使用私有感知、记忆、规划和 `CharacterExecutionContract`；
- UE 仍是本地运动、碰撞、伤害、阵型与领域结算 owner。

### 阶段 E：Siming / PopulationPlanner

- `SimingRuntime` 只接收公开、scoped 的战场事件并产生高层 catalyst；
- `PopulationPlanner` 用于远处大军的批量候选生成，不直接写入 UE 世界；
- 远处部队和近场角色共享军队状态投影，保持分级连续性；
- 任何世界变化仍必须经过 UE 战场 owner 的受控结算或未来统一领域 owner。

## 10. UE 模块预留

第一版实现可以从现有 Strategy 模板增量加入以下边界，不要求一次完成全部功能：

- `UBattleStateSubsystem`：战场 revision、事件日志、士气/阵型结算入口；
- `UCommandHierarchyComponent`：军制节点、预案、指挥官和继任；
- `UMilitaryDoctrineDataAsset`：版本化军制预案；
- `UBattleFactEmitter`：把 UE 事实转换为 AuthorityEvent；
- `UParallsBridgeSubsystem`：WebSocket/HTTP 传输、幂等、断线和重连；
- `ULocalTacticalBrain`：无后端时生成语义意图；
- `UBattleIntentValidator`：能力、目标、revision、预案和权限校验；
- `UBattleReplayRecorder`：保存命令、事实、意图和结算回执。

这些类应作为可替换边界，不让 `StrategyPlayerController` 直接承担 Python 通信或士气结算。

## 11. 验收场景

### 场景 A：10 号命令改变正面接触

1. 玩家骑马接近敌方主战队。
2. 输入 `10`。
3. UI 显示 `已下达 -> 传递中 -> 已送达 -> 执行中`。
4. 玩家亲卫队贴身跟随并把命令送入营指挥链，营指挥头目确认后令第一队跟随玩家攻击同一目标。
5. 玩家冲锋接触后，敌方局部阵型从 `formed` 变为 `compressed` 或 `disrupted`，敌方士气下降。

### 场景 B：22 号命令造成侧翼压力

1. 敌军正面仍有战斗。
2. 输入 `22`。
3. 玩家亲卫队转发给营指挥头目，营指挥头目令第二队收到命令并绕向侧翼。
4. 侧翼接触后，敌方阵型进入 `flanked`，士气进入 `shaken` 或 `wavering`。

### 场景 C：34 号命令威胁后方目标

1. 输入 `34`。
2. 玩家亲卫队转发给营指挥头目，营指挥头目令第三队绕行后方。
3. 若军旗或敌方指挥头目在可达范围内，营第三队优先选择预案规定目标。
4. UI 能显示当前目标是军旗、敌将或冲车，不显示任意全知信息。

### 场景 D：指挥继任

1. 让敌方指挥头目失能。
2. 事件只产生一次。
3. 次高指挥官接管并继承当前预案和未过期命令。
4. 若继任者具有 `blooded`/高血性特质且士气处于 `wavering`，可能生成 `rally_countercharge`。
5. 若所有候选人失能，敌军进入 `leaderless` 并回归路径。

### 场景 E：断线与过期

1. Python Bridge 断开或返回过期 intent。
2. UE 拒绝过期 intent，并记录原因。
3. 本地战术脑接管，不暂停战斗。
4. 重连后不会重复执行已结算的命令。

### 场景 F：关键目标结算

1. 玩家或亲卫队接触军旗、敌将或冲车。
2. UE 先结算目标状态。
3. 结算事实更新双方士气/预案选择。
4. Python 只收到事实并产生后续建议，不能直接写入目标状态。

## 12. 非目标与风险边界

本切片明确不实现：

- 完整硬核传令、封泥、虎符、破译和传令兵截杀；
- 完整 LLM 驱动的实时每兵决策；
- 全国地图、经济、外交、科技树和文明层；
- 数千单位的最终性能方案；
- 多人同步和网络权威；
- 复杂骑马物理和最终动画品质。

主要风险及处理：

- **通信延迟过于烦琐：** P0 只做标准模式的可感知短延迟，硬核模式留到下一阶段；
- **AI 直接改世界：** 所有远端输出都必须是语义意图，UE 重新校验并结算；
- **断线导致战斗停摆：** 本地战术脑始终存在，Bridge 只改变建议来源；
- **分层模拟不连续：** 近场 Actor、中场代理和远场批量模拟共享军队状态、事件和 revision；
- **范围膨胀：** 先只验证一次冲阵、三个快捷命令、三个关键目标和一次继任。

## 13. 完成定义

垂直切片达到以下条件即可进入实现评审：

- 玩家可以在骑马移动中输入 `10/22/34`；
- 玩家亲卫队能够接收并转发命令，营内三队能够分别执行或拒绝命令，并显示命令状态；
- 敌我士气和阵型至少各有一次可观察的状态转移；
- 军旗、敌方指挥头目和冲车至少有一种可结算的控制变化；
- 指挥头目失能后能按继任顺序自动接管，且重复事件不重复继任；
- Python Bridge 关闭时仍可完整游玩；
- Python 意图过期、版本过期或无权限时会被 UE 拒绝并回退本地 AI；
- 回放日志能按 `causation_id`、`correlation_id` 和 `idempotency_key` 还原一次冲阵；
- 协议中不存在直接设置位置、骨骼、伤害或世界状态的后端字段。








