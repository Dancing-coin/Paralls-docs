> 文档状态更新：2026-10-30。历史骑将冲阵计划/规格；2026-10-30取消独立开发与独立验收。正文所有任务/必须/阶段门不再作为当前实施要求。 当前规格见[PRD导航](../../PRD/README.md)；[县城执行计划](../../production/县城守城Demo执行计划.md)。

# 骑将冲阵 UE 垂直切片实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 UE5.8 中先完成一个可玩的灰盒骑将冲阵切片：玩家可骑马、指挥一营三队和一队亲卫，并可自由切换俯视、第三人称、第一人称；同时保留未来接入 Paralls Phase 0 的稳定语义接口。

**Architecture:** 保留现有 Strategy/TopDown 模板作为输入和导航基础，将玩家骑将、战场状态、军制指挥、视角切换和 Paralls Bridge 分成独立边界。UE 是实时运动、碰撞、伤害、士气、阵型和关键目标结算的权威；本地战术脑和 Python Paralls 都只产生语义意图，经过同一套 UE 校验器后执行。三种视角共享同一玩家骑将和同一套命令输入，不复制战斗状态。

**Tech Stack:** UE5.8 C++、Blueprint、Enhanced Input、AIController/NavMesh、StateTree（可选的本地行为实现）、Automation Tests、WebSocket/HTTP Bridge 预留、Paralls `AuthorityEvent`/`CharacterExecutionContract` 语义。

**Spec:** `docs/superpowers/specs/2026-10-21-mounted-charge-vertical-slice/2026-10-21-mounted-charge-vertical-slice-design.md`

## Global Constraints

- 第一阶段先使用灰盒骑兵、步兵和占位目标，后续可替换 Skeletal Mesh、动画、材质和特效而不改变战斗协议。
- 编制固定为：1 名玩家骑将、1 队玩家亲卫、1 营三队玩家军队、敌方指挥头目/军旗/冲车/主战队。
- 命令链固定为“玩家骑将 → 玩家亲卫队 → 营指挥头目 → 营内目标队”。
- 快捷码 `10/22/34` 只属于输入层，运行时协议使用 `follow_player_charge`、`attack_flank`、`encircle_rear`。
- UE 负责位置、马匹、碰撞、伤害、士气、阵型、军旗、指挥官和冲车结算；远端服务不得直接写入这些状态。
- Python Bridge 关闭、断线、意图过期或版本过期时，战斗必须由本地战术脑继续运行。
- 事件和意图必须带 `event_id`/`turn_id`、因果/相关 ID、版本和幂等键，便于回放和未来接入 Paralls。
- 视角切换不得生成第二个玩家角色；俯视、第三人称、第一人称都观察同一骑将和同一战场状态。

## Review Focus

- 从俯视切到第三人称和第一人称时，玩家控制权、骑将位置和命令上下文保持连续；对应 Task 1/Task 2 的视角切换自动化测试和 PIE 验收。
- 玩家在骑马移动中输入 `10/22/34` 时，命令必须经过亲卫和营指挥头目，而不是绕过军制直接移动目标队；对应 Task 4 的命令链测试。
- 营指挥头目失能、重复失能事件或候选全部失能时，继任必须幂等并走回归路径；对应 Task 5 的继任测试。
- Python 返回位置、伤害、骨骼或过期版本时，UE 必须拒绝并回退本地 AI；对应 Task 7 的协议验证测试。
- 目标队、军旗、冲车和敌将状态改变后，士气/阵型/回放事件顺序可解释；对应 Task 6/Task 8 的战场事实和回放测试。

---

### Task 1: 建立三视角相机与玩家骑将控制边界

**Files:**
- Create: `Source/mcp/Variant_Strategy/BattleViewMode.h/.cpp`
- Create: `Source/mcp/Variant_Strategy/BattleRiderCharacter.h/.cpp`
- Create: `Source/mcp/Variant_Strategy/BattleCameraPawn.h/.cpp`
- Modify: `Source/mcp/Variant_Strategy/StrategyPlayerController.h/.cpp`
- Modify: `Source/mcp/Variant_Strategy/StrategyPawn.h/.cpp`（仅保留兼容或迁移入口）
- Create/Modify: `Content/Variant_Strategy/Input/Actions/IA_BattleViewCycle.uasset`、`IA_BattleViewTopDown.uasset`、`IA_BattleViewThirdPerson.uasset`、`IA_BattleViewFirstPerson.uasset`
- Create: `Source/mcp/Tests/BattleViewModeTests.cpp`

**Interfaces:**
- Produces `EBattleViewMode {TopDown, ThirdPerson, FirstPerson}`。
- Produces `UBattleViewModeComponent::SetViewMode(EBattleViewMode)`、`CycleViewMode()` 和当前模式查询。
- `ABattleRiderCharacter` 是唯一玩家骑将 Actor，提供 `GetRiderCommandOrigin()`、`GetRiderCameraAnchor(EBattleViewMode)`。
- `ABattleCameraPawn` 只负责俯视平移/缩放；第三人称和第一人称相机挂在骑将相机锚点上。

- [ ] **Step 1: Write the failing automation tests**：验证三种模式可设置和循环；切换前后玩家骑将 Actor、位置、当前命令上下文不变；无效枚举回退到 `ThirdPerson`。
- [ ] **Step 2: Run the focused automation test**：使用 UE Automation Test 过滤器运行 `BattleViewMode.*`，确认测试先失败。
- [ ] **Step 3: Implement the camera/view boundary**：将现有正交 Strategy 相机能力迁移到 `ABattleCameraPawn`；在骑将上提供第三人称跟随相机和第一人称头部锚点；由 PlayerController 统一切换视图目标或相机激活状态，不复制骑将。
- [ ] **Step 4: Add Enhanced Input bindings**：建议 `V` 循环视角，`1/2/3` 直接选择俯视/第三人称/第一人称；保留鼠标和键盘指挥输入。
- [ ] **Step 5: Run tests and PIE smoke check**：验证三种视角切换、骑将移动连续性、俯视缩放和相机碰撞/遮挡基础行为。

### Task 2: 灰盒骑将、马匹占位和步兵单位

**Files:**
- Create: `Source/mcp/Variant_Strategy/BattleUnit.h/.cpp`
- Create: `Source/mcp/Variant_Strategy/BattleRiderMovementComponent.h/.cpp`（或沿用 CharacterMovement 的可替换适配层）
- Create: `Content/Variant_Strategy/Blueprints/BP_BattleRider.uasset`、`BP_BattleInfantry.uasset`、`BP_BattleGuard.uasset`
- Modify: `Source/mcp/Variant_Strategy/StrategyUnit.h/.cpp`（抽取可复用移动/选择接口，不改变旧模板行为）
- Create: `Source/mcp/Tests/BattleUnitTests.cpp`

**Interfaces:**
- `ABattleUnit` 暴露 `UnitId`、`ArmyId`、`FormationSlot`、`Morale`、`TrainingLevel`、`IsCombatCapable()`。
- `ABattleRiderCharacter` 暴露 `BeginCharge()`、`EndCharge()`、`IsCharging()` 和速度/朝向只读状态。
- `ABattleUnit` 的移动由 AIController/NavMesh 或本地简化编队控制器驱动，不能由远端意图直接设置 Transform。

- [ ] **Step 1: Write failing tests**：验证骑将冲锋状态、步兵单位身份/军队归属和基础训练/士气默认值。
- [ ] **Step 2: Run focused tests and confirm failure**。
- [ ] **Step 3: Implement greybox actors**：使用现有 Manny/Quinn 或简单 Capsule/Mesh 作为占位；骑将先用普通 Character + 马匹占位组件，保证未来替换为真正骑乘骨骼时不改变上层接口。
- [ ] **Step 4: Implement local movement**：骑将支持步行/骑乘占位、加速和冲锋；步兵支持 NavMesh 移动和停止；不在本任务加入复杂战斗伤害。
- [ ] **Step 5: Verify in PIE**：至少同时显示玩家骑将、玩家亲卫、营内三队和敌方主战队，并能移动。

### Task 3: 战场状态、士气、阵型和关键目标

**Files:**
- Create: `Source/mcp/Variant_Strategy/BattleStateTypes.h`
- Create: `Source/mcp/Variant_Strategy/BattleStateSubsystem.h/.cpp`
- Create: `Source/mcp/Variant_Strategy/BattleTargetActor.h/.cpp`
- Create: `Source/mcp/Tests/BattleStateTests.cpp`

**Interfaces:**
- `EBattleFormationState {Formed, Compressed, Disrupted, Flanked, RearThreatened, Routing}`。
- `EBattleMoraleState {Steady, Shaken, Wavering, Routing}`。
- `EBattleTargetType {Commander, Standard, SiegeEngine}`。
- `UBattleStateSubsystem::ApplyBattleFact(const FBattleFact&)` 只接受结构化事实，负责更新 battle/object revision。
- `UBattleStateSubsystem::GetArmySnapshot(FArmyRef)` 返回只读快照，包含士气、阵型、当前预案和指挥官状态。

- [ ] **Step 1: Write failing tests**：覆盖士气阈值 75/45/20、阵型状态转换、军旗/冲车/敌将三类目标状态变化和 revision 递增。
- [ ] **Step 2: Run focused tests and confirm failure**。
- [ ] **Step 3: Implement subsystem and target actors**：UE 结算事实到状态，禁止外部直接写士气/阵型/目标拥有权；为近场 Actor 和中场代理提供同一快照接口。
- [ ] **Step 4: Implement charge contact facts**：冲锋接触、侧翼、后方、目标失能/损毁/夺取转为 `FBattleFact`，由 Subsystem 统一结算。
- [ ] **Step 5: Verify**：PIE 中能观察至少一次敌方阵型变化、士气变化和关键目标状态变化。

### Task 4: 军制层级、预案和 `10/22/34` 命令链

**Files:**
- Create: `Source/mcp/Variant_Strategy/MilitaryDoctrineDataAsset.h/.cpp`
- Create: `Source/mcp/Variant_Strategy/CommandHierarchyComponent.h/.cpp`
- Create: `Source/mcp/Variant_Strategy/BattleCommandTypes.h`
- Modify: `Source/mcp/Variant_Strategy/StrategyPlayerController.h/.cpp`
- Create: `Source/mcp/Tests/CommandHierarchyTests.cpp`

**Interfaces:**
- `UMilitaryDoctrineDataAsset` 保存 `DoctrineId`、`Revision`、编队模板、目标优先级、士气响应、回归路径、继任顺序和训练门槛。
- `UCommandHierarchyComponent::IssueCommand(const FBattleCommandRequest&)` 只接受玩家/合法指挥节点发起的语义命令。
- `UCommandHierarchyComponent::RouteCommand()` 实现“玩家骑将 → 玩家亲卫队 → 营指挥头目 → 营内目标队”。
- `UCommandHierarchyComponent::ResolveSuccession(const FCommanderIncapacitatedFact&)` 必须幂等。
- `FBattleCommandRequest` 包含 `request_id`、`turn_id`、`semantic_intent_id`、目标、预案引用、expected revisions、过期时间和 `idempotency_key`。

- [ ] **Step 1: Write failing tests**：`10` 只路由到第一队、`22` 只路由到第二队、`34` 只路由到第三队；亲卫/营指挥头目/目标队分别产生传递状态；非法 issuer、过期和 revision 冲突被拒绝。
- [ ] **Step 2: Run focused tests and confirm failure**。
- [ ] **Step 3: Implement versioned doctrine assets and hierarchy component**：将预案参数作为可编辑 Data Asset；战场中只允许切换已训练预案。
- [ ] **Step 4: Bind keyboard aliases**：Enhanced Input 数字键只创建语义 `FBattleCommandRequest`，不让 Python 或 UI 重新解释数字码。
- [ ] **Step 5: Verify**：骑将移动中连续发出三种命令，营三队按目标执行，亲卫保持护卫职责。

### Task 5: 营指挥头目、本地战术脑和自动继任

**Files:**
- Create: `Source/mcp/Variant_Strategy/LocalTacticalBrain.h/.cpp`
- Create: `Source/mcp/Variant_Strategy/CommanderComponent.h/.cpp`
- Modify: `Source/mcp/Variant_Strategy/CommandHierarchyComponent.h/.cpp`
- Create: `Source/mcp/Tests/CommanderSuccessionTests.cpp`

**Interfaces:**
- `ULocalTacticalBrain::Evaluate(const FArmySnapshot&, const FVisibleBattleFacts&) -> FBattleIntentProposal`。
- `UCommanderComponent::SelectDoctrineOrIntent()` 根据士气、阵型、训练、预案、目标威胁和角色特质选择高层语义意图。
- `UCommandHierarchyComponent::OnCommanderIncapacitated()` 产生继任事实并保留当前预案和未过期命令。
- 本地决策 cadence 为 0.25–0.5 秒一次，不在 Tick 每帧重规划。

- [ ] **Step 1: Write failing tests**：稳定/动摇/溃退三个士气区间的决策；侧翼/后方威胁优先收缩；指挥头目失能后按继任顺序接管；重复失能事件不重复继任；无人可继任时进入 `leaderless`。
- [ ] **Step 2: Run focused tests and confirm failure**。
- [ ] **Step 3: Implement deterministic local brain**：先用规则评分生成 `hold_formation`、`follow_player_charge`、`attack_flank`、`encircle_rear`、`protect_standard`、`rally_countercharge`、`withdraw_to_fallback_line`、`assume_command`。
- [ ] **Step 4: Implement commander traits**：预留能力、性格、自我认知和 `self_drive/blooded`，但只作为规则评分输入，不直接改世界状态。
- [ ] **Step 5: Verify**：击倒营指挥头目后，次高指挥官继续当前预案；高血性继任者在满足条件时可生成反冲锋意图。

### Task 6: 亲卫护卫、营三队行为和基础冲锋结算

**Files:**
- Create: `Source/mcp/Variant_Strategy/BattleFormationController.h/.cpp`
- Create: `Source/mcp/Variant_Strategy/BattleCombatResolver.h/.cpp`
- Modify: `Source/mcp/Variant_Strategy/BattleUnit.h/.cpp`
- Create: `Source/mcp/Tests/BattleFormationAndChargeTests.cpp`

**Interfaces:**
- `UBattleFormationController::ApplyIntent(const FBattleIntentProposal&)` 将语义意图映射到编队目标和 NavMesh 行为。
- `UBattleCombatResolver::ResolveChargeContact(const FChargeContactInput&) -> FBattleFactBatch` 只返回待结算事实，不直接改最终士气/目标状态。
- 玩家亲卫保持跟随/护卫；营第一队正面、第二队侧翼、第三队后方。

- [ ] **Step 1: Write failing tests**：三队目标位置策略；玩家亲卫护卫半径；正面/侧翼/后方接触事实不同；冲锋不会让一人直接赢得整场战斗。
- [ ] **Step 2: Run focused tests and confirm failure**。
- [ ] **Step 3: Implement formation controller**：先用简化槽位和目标点，不做复杂连续队形求解；同一接口可替换为 StateTree 或更高级群体模拟。
- [ ] **Step 4: Implement charge resolver**：依据速度、方向、阵型和目标类型产生事实，交由 Task 3 Subsystem 结算。
- [ ] **Step 5: Verify**：PIE 中骑将冲入敌阵能造成局部阵型/士气变化，三队仍由营指挥头目统一调度。

### Task 7: UE–Paralls Bridge、意图校验和断线回退

**Files:**
- Create: `Source/mcp/Variant_Strategy/ParallsBattleProtocol.h`
- Create: `Source/mcp/Variant_Strategy/ParallsBridgeSubsystem.h/.cpp`
- Create: `Source/mcp/Variant_Strategy/BattleIntentValidator.h/.cpp`
- Create: `Source/mcp/Variant_Strategy/BattleFactEmitter.h/.cpp`
- Create: `Source/mcp/Tests/ParallsProtocolTests.cpp`

**Interfaces:**
- `UParallsBridgeSubsystem::PublishBattleFact(const FBattleFactEnvelope&)`。
- `UParallsBridgeSubsystem::SubmitIntent(const FCharacterExecutionIntent&)`。
- `UBattleIntentValidator::Validate(const FCharacterExecutionIntent&, const FArmySnapshot&) -> FIntentValidationResult`。
- `UBattleFactEmitter` 将 UE 事实映射为 Paralls `AuthorityEvent` 字段语义。
- Bridge transport 先抽象为本机 WebSocket/HTTP adapter；本任务不要求接入 LLM。

- [ ] **Step 1: Write failing tests**：协议包含 event/turn/correlation/causation/revision/idempotency；拒绝位置、骨骼、动画、伤害、速度、世界写入和最终结算字段；过期/版本冲突/重复 key 被拒绝。
- [ ] **Step 2: Run focused tests and confirm failure**。
- [ ] **Step 3: Implement protocol structs and validator**：生产输出只允许语义 `semantic_intent_id`、目标引用、约束、置信度和版本信息；UE 收到后重新验证。
- [ ] **Step 4: Implement transport lifecycle**：连接、断线、重连、发送队列和 event_id 去重；Bridge 不可用时切换 `LocalTacticalBrain`。
- [ ] **Step 5: Verify**：旁路 Python 建议不改变战斗结果；低风险意图可受控执行；非法/过期意图回退本地 AI 并写入拒绝回执。

### Task 8: 回放、调试 HUD 和切片验收场景

**Files:**
- Create: `Source/mcp/Variant_Strategy/BattleReplayRecorder.h/.cpp`
- Create: `Source/mcp/Variant_Strategy/BattleDebugHUD.h/.cpp`
- Create: `Content/Variant_Strategy/Maps/LVL_MountedCharge.umap`
- Create/Modify: `Content/Variant_Strategy/UI/WBP_BattleCommandStatus.uasset`
- Create: `Source/mcp/Tests/MountedChargeAcceptanceTests.cpp`

**Interfaces:**
- `UBattleReplayRecorder::RecordEvent(const FBattleEventRecord&)`，按 `causation_id`、`correlation_id`、`idempotency_key` 查询。
- Debug HUD 显示当前视角、玩家骑将状态、命令链状态、士气、阵型、关键目标和当前 revision；不显示角色不应知道的全知信息。
- 场景必须包含平地/浅坡、玩家后撤线、敌方阵地、军旗和冲车。

- [ ] **Step 1: Write failing acceptance tests**：验收场景 A–F 覆盖三视角、`10/22/34`、士气/阵型变化、关键目标、继任、断线回退和回放。
- [ ] **Step 2: Run focused tests and confirm failure**。
- [ ] **Step 3: Build graybox map and spawn layout**：按切片规格放置玩家骑将、亲卫、营三队、敌方队伍、军旗、冲车和指挥头目。
- [ ] **Step 4: Add debug HUD and command status**：显示“已下达 → 传递中 → 已送达 → 执行中/失败”，支持开发期观察原因。
- [ ] **Step 5: Run PIE and packaged smoke test**：目标演示时长 3–8 分钟；Bridge 关闭也能完成完整冲阵流程；记录未完成项和性能基线。

### Task 9: 美术资源替换接口与 Paralls 旁路演示

**Files:**
- Create: `docs/superpowers/plans/2026-10-21-mounted-charge-asset-replacement-checklist.md`
- Modify: `Content/Variant_Strategy/Blueprints/BP_BattleRider.uasset`、`BP_BattleInfantry.uasset`、`BP_BattleGuard.uasset`
- Modify: `Content/Variant_Strategy/Maps/LVL_MountedCharge.umap`
- Create: `Config/DefaultGameUserSettings.ini` entries only if profiling requires them

**Interfaces:**
- 灰盒 Actor 的 gameplay component、socket 名称、动画状态枚举和材质参数作为资源替换契约。
- Paralls 旁路演示只消费 scoped `AuthorityEvent`，对比本地决策和远端建议，不默认让远端控制结果。

- [ ] **Step 1: Define replacement checklist**：列出骑将、马匹、步兵、旗帜、冲车的骨骼/碰撞/动画/socket/LOD 替换边界。
- [ ] **Step 2: Validate Blueprint contracts**：替换测试 Mesh 后不改变 `ABattleUnit`、视角、命令和状态接口。
- [ ] **Step 3: Run profiling pass**：记录近场 Actor 数量、NavMesh 查询、决策 cadence、事件吞吐和三视角切换开销。
- [ ] **Step 4: Produce Paralls observation report**：记录 UE 事实、Python 建议、UE 校验结果、回退原因和回放链。

## Implementation Order

按依赖顺序执行：Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7 → Task 8 → Task 9。Task 7 可在 Task 3–5 完成后并行开发协议适配，但只有 Task 6 的本地战斗闭环通过后才允许让远端意图影响结果。

## Self-Review

- 规格中的三视角、灰盒骑兵/步兵、一营三队、一队亲卫、命令链、士气/阵型/关键目标、继任、本地 AI、Paralls AuthorityEvent/ExecutionContract、断线回退和回放均有对应任务。
- 现有 `StrategyPlayerController`、`StrategyPawn`、`StrategyUnit` 的职责被逐步迁移或包裹，没有要求一次性删除模板代码。
- 所有跨任务接口都在前置任务的 Interfaces 中定义，后续任务只依赖稳定语义类型，不依赖具体美术资产。
- 计划没有把 Python 作为 UE 打包运行时脚本；Bridge 是可关闭的外部服务适配层。
- 未在本计划中实现全国地图、硬核通信破译、复杂马匹物理、多人网络或最终美术资源。
