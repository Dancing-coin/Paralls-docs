# 02-领域Owner详细契约

> 版本：1.0（职责拆分版）
> 更新日期：2026-10-30
> 评审状态：职责归位与静态一致性核对；不替代产品待决项裁决或实现评审。
> 实现状态：本篇为目标合同；已有实现仅按原始证据日期记录，不代表全量实现或运行验收完成。
> 验证范围：本轮仅重组文档，未执行代码、UE、PIE 或性能验证。原始设计、实现盘点和证据日期分别保留。

[技术架构入口](../README.md) · [唯一 Owner 注册表](01-Owner注册表.md#owner-registry)

<a id="domain-contracts"></a>

## 详细领域合同的阅读边界

完整名单与唯一事实边界只维护于 [Owner 注册表](01-Owner注册表.md#owner-registry)。本篇按因果链保留已有详细 Static Data、State、Command、Resolver、Authority、Event/Result 和 Query/Projection 合同；下文原 P0/P1/P2 标签仅代表旧需求优先层级，正式执行顺序见生产计划，不与表现 P0—P3、V0—V5 或 A—F 批次混用。

<a id="military-domain"></a>

## 位置、军令、军事组织与战场因果

### Guoshang 新 Owner 清单

以下 P0/P1/P2 仅保留早期需求分组，不能当作串行建设顺序或冻结名单。最终 23 个逻辑 Owner、验收批次与全量 UE 协作节奏以[基础设施与 Owner 建设总计划](../../production/基础设施与Owner建设总计划.md)为准，包含本节未单列展开的 Ownership、Economy、Territory、Politics、Campaign 等领域。Owner 与部署进程无关：获准 UE 实现可提交本域事实，Command/表现适配器不可写事实；ESM 仅是可选的已审核交互适配合同，Godot 执行器需替换。

### 第一阶段 P0：县城守城可玩闭环

### Presence / Movement Owner

**唯一事实**：角色、队伍、传令批次和器械的实际位置、占用、到达、阻挡和脱离。

- Static Data：导航区域、道路、门、桥、地形代价、占用规则、可通行标签；
- Runtime State：当前位置、目标位置、移动阶段、占用者、路径 revision、阻挡原因；
- Command：`move`、`follow`、`hold_position`、`withdraw`、`reroute`；
- Resolver：速度、体力、地形、门禁、占用、碰撞、临时阻挡和可见证据；
- Event：`move_started`、`arrived`、`blocked`、`rerouted`、`intercepted`、`withdrawn`；
- 连接：角色 L4 和群体 B1 只能请求移动，UE 提供接触/占用证据；
- 投影：角色当前位置摘要、队伍位置、命令可达性和玩家可见路径。

这是事实 Owner；UE Navigation、动画和寻路库只是执行/表现工具。

### Command / Dispatch Owner

**唯一事实**：命令的传达节点、抵达、理解、接受、拒绝、过期和执行跟踪；授权依据引用 Organization/Government/基础能力权威，不在 Dispatch 另造指挥权。

- Static Data：命令类型、有效期、可传达媒介、节点权限、优先级、失效条件；
- Runtime State：命令版本、传令批次、当前中继节点、目标接收者、状态和时间；
- Command：`issue_order`、`relay_order`、`ack_order`、`reject_order`、`cancel_order`、`expire_order`；
- Resolver：发令者身份、通信覆盖、传令路径、目标权限、内容完整性和时效；
- Event：`order_issued`、`messenger_departed`、`order_received`、`order_understood`、`order_accepted`、`order_rejected`、`order_expired`；
- 连接：县令、将领和角色智能体提出命令；群体模拟按职责和预案承接；
- 投影：玩家看到实际传达节点，角色只收到自己合法知道的命令信息。

它与 Presence/Transport 协作，但不拥有角色位置或物资库存。

### Organization / Military Command Owner

**唯一事实**：岗位、军队层级、指挥权、授权范围、继任链、队伍编制和预案归属。

- Static Data：组织类型、军制层级、岗位资格、继任规则、命令覆盖范围、预案模板；
- Runtime State：当前任职、有效授权、队伍成员、指挥头目状态、继任待处理项；
- Command：`assign_role`、`grant_authority`、`issue_plan`、`handover_command`、`activate_contingency`；
- Resolver：身份、岗位、上级授权、失能状态、组织 revision、候选继任资格；
- Event：`role_assigned`、`authority_granted`、`plan_activated`、`command_handed_over`、`succession_committed`；
- 连接：角色设定提供身份与能力摘要，不能自行宣布有指挥权；B0/B1 读取预案，B2/B3 才可进行高影响判断；
- 投影：组织树、命令链、继任链、队伍任务和权限状态。

Paralls 的 `OrganizationAuthority` 可作为窄基础，但县城军政一体的军令、营队和继任需新增 Guoshang 规则。

### Combat / Damage Owner

**唯一事实**：攻击尝试、命中、格挡、伤害评估和战斗接触结果。Combat 产出伤害评估，不直接拥有目标生命、伤势、护甲耐久或持续状态效果。

- Static Data：武器、兵种、攻击原语、伤害类型、命中/格挡规则；引用护甲和身体规则但不复制其权威配置；
- Runtime State：攻击姿态、冷却、接触和攻击执行阶段；
- Command：`attack`、`defend`、`charge`、`shoot`、`retreat`、`capture`；
- Resolver：距离、朝向、体力、技能、武器、地形、碰撞、目标状态和伤害评估规则；
- Event：`attack_started`、`hit_confirmed`、`damage_assessed`、`attack_resolved`；身体功能限制由 Body 确认，倒地/死亡等生命周期转换由 LifeState 确认，俘获后的拘押/编制关系由 Organization 的战俘子域确认；
- 连接：角色智能体提出战斗意图，UE 提供接触和命中证据，群体模拟只提交低精度战斗候选；
- 投影：战斗反馈、伤害评估及下游 Owner 确认的伤势、失能、死亡和队伍损失。

**关联 Owner**：Body 写生命、伤势、部位功能和身体失能；Equipment 写护甲耐久；Status 写流血等持续效果。UE 本地 Combat Domain Owner 可按第一阶段路线负责近场 Combat 事实的最终结算；若其结算涉及 Body/Equipment/Status，必须请求这些 Owner 的授权 fragment 并共同提交，不能把相关字段纳入 Combat 的私有写集。动画、未确认命中和角色自报伤害不能成为最终事实。

**Body / Resource Owner 合同**：唯一事实为生命、体力、身体部位、伤势、身体功能和由此产生的能力限制。接收 Combat 的伤害评估、Status 的持续效果 tick、医疗流程的治疗请求及动作资源成本，由 Body 生成自己授权的 fragment；按注册模型提交 `damage_applied`、`injury_changed`、身体功能与体力消耗/恢复事件。生命按事件结算，连续体力按模拟时间窗口积分，动作准入与成本扣除/预留不得并发超支。近场推荐在 UE runtime 内与 Combat 本地协作，不以 Agent 推理或后端逐次往返作为扣血/扣体力的必经路径；任一事实作用域同一时刻只有一个有效 `authority_epoch` 和 canonical writer。

**LifeState Owner 合同**：独立拥有存活、倒地、濒死、死亡等生命周期转换。Body 提供身体与阈值依据，Status 等域提供适用效果依据，LifeState 按自身版本化条件授权转换；`health == 0` 不自动等于 `dead`。近场支持与 Body 同步的 UE-local 实现；普通治疗必须校验生命周期，不能用延迟回血覆盖已确认死亡。该完整合同为 Guoshang 目标，不能把 Paralls 当前有界的初始 alive / confirmed case-death 支持称为完整生命周期状态机。

**近场协作与提交合同**：Combat、Body/Resource、Equipment、Status、LifeState 和战场 Morale 可共同部署在 UE，由本地路由和调用生成各域授权结果。静态资源定义、模型版本、适用绑定、更新节奏与延迟预算必须登记。本地计算完成不等于提交完成；可靠本地提交只有注册为该事实流唯一权威后才能产生最终 receipt，后端随后只同步投影；若只有后端 canonical store，则回执前保持 pending/predicted。详见[近场领域实时协作](../05-运行时接入/01-UE本地提交与Paralls同步.md#local-domain-collaboration)。

**Equipment Owner 合同**：拥有护甲/装备耐久、防护状态、破损和装备关系；Combat 可以请求防护计算，不能写耐久。伤害批次需固定 Equipment revision，并与 Body 结果共同提交或记录待完成义务。

**Status / Effect Owner 合同**：拥有流血、中毒、燃烧、感染、眩晕等效果实例的来源、强度、层数、时限、tick、退出条件和 revision。按效果规则产生 Body 伤害/恢复请求；只提交效果实例事件，不直接修改生命值。UE VFX、AnimNotify 和 GameplayEffect 可作为呈现/触发适配，不是 canonical writer。

### Morale / Formation Owner

**唯一事实**：按显式作用域注册的个人/队伍士气、阵型、纪律、溃退、重整和关键目标压力；角色主观情绪、信念与解释仍归 Character Agent。

- Static Data：兵种编组、阵型模板、训练度、士气阈值、指挥加成、溃退规则；
- Runtime State：士气、阵型、纪律、队伍压力、队伍任务、重整阶段；
- Command：`set_formation`、`advance`、`hold`、`rally`、`retreat`、`reform`；
- Resolver：命令是否抵达、队伍能力、地形、伤亡、粮水、指挥状态、敌我压力；
- Event：`formation_changed`、`morale_shifted`、`routed`、`rallied`、`reformed`、`objective_pressure_changed`；
- 连接：Organization 提供合法命令，Combat、Supply、Command 提供事实输入，B0/B1 生成低精度压力信号；
- 投影：队旗、阵型、士气等级、当前任务、拒绝/重规划原因。

它必须读取多个系统的已确认结果，但只写自己的士气和阵型事实。

近场战场士气须支持 UE 高频协作，推荐显式注册 UE-local 权威实现，按伤亡、军旗、鼓舞、指挥等事件加周期压力窗口评估，不要求每画面帧全量重算。个人所见、队伍汇报与全局事实须按输入合同区分，不能让未知伤亡直接成为角色认知。明确状态限制及时生效，Agent 结合士气、私有心智与命令自主判断；同一士气不必产生同一行为。切换群体模拟/Agent 或近远场不自动转移士气写权。

<a id="presence-semantics"></a>

## Presence 语义提交点

### P0 可玩闭环 Owner

本节只定义第一阶段必须被实际内容激活的 Owner 规则，不缩减[五阶段 Owner 基础设施范围](01-Owner注册表.md#owner-registry)。未在本节展开的 Ownership、Economy、Politics、Territory 和 Campaign 仍须按第 6.2—6.4 节完成正式 Authority 和 fixture 验证。

### Presence / Movement

唯一事实是角色、队伍、传令批次、运输批次和器械的实际位置、占用、到达、阻挡、绕行、拦截和脱离。

UE 的 `CharacterMovement`、NavMesh、EQS、AIController 和碰撞提供局部执行与证据；Presence Owner 负责承认位置事实。不能把 Actor 坐标每帧写入 EventStore。

语义提交点至少包括：`move_started`、`arrived`、`blocked`、`rerouted`、`intercepted`、`withdrawn`。

<a id="military-semantics"></a>

## Dispatch、Organization、命中与士气语义

### Command / Dispatch

唯一事实是命令的传令节点、抵达、理解、接受、拒绝、过期和执行跟踪。发令授权来自 Organization/Government/基础能力权威，Dispatch 校验并引用，不再造一份授权。

第一阶段至少支持：求援、守城、坚守城门、调动队伍（原三队数量待D03确认）、调拨军需、请求修缮、请求生产、请求护送。

### Organization / Military

最小组织为：县令/守城统治者、亲卫、营指挥头目、一营三队（原县城配置，数量待D03确认）、传令兵、工坊负责人、军需负责人、村落负责人。必须支持岗位、授权、指挥范围、预案版本和继任。

### Combat / Damage

UE 负责高频局部执行、输入、碰撞、命中候选和即时反馈；近场推荐共同承载 Combat、Body/Resource、Equipment、Status、LifeState 与战场 Morale 的获准实现，按统一 Command/Event/Receipt 合同通过本地调用协作。Combat 结算攻击/命中/格挡和伤害评估；Equipment 按固定 revision 结算防护与耐久，Body 应用剩余伤害并确认伤势和身体能力限制，Status 维护流血等效果，LifeState 根据授权依据确认倒地/濒死/死亡。需要同一语义提交点时由各 Owner 提供授权 fragment 并按依赖原子提交，Paralls 不得为同一事实再建第二写入者；正式提交位置见 [本地可靠提交合同](../05-运行时接入/01-UE本地提交与Paralls同步.md#local-commit)。

语义提交点按事实 Owner 区分：Combat 提交攻击尝试、命中确认、格挡和 `damage_assessed`；Equipment 提交防护结算、耐久/破损；Body 提交 `damage_applied`、伤势、功能和体力变化；LifeState 提交生命周期转换；Status 提交效果创建、tick 生命周期、减轻和解除，并向 Body 请求周期数值变化；俘获由组织/战俘事实 Owner 确认。Objective 只读取这些已确认结果判胜负。动画完成不能替代任何提交事件。

### Morale / Formation

读取伤亡、军旗、补给、指挥、疲劳、地形和敌压的已确认事件，只写士气、阵型、纪律、溃退和重整事实。角色 Agent 可以提出 rally、withdraw、protect_standard 等意图，但不能直接改士气。

近场个人/队伍士气采用显式登记的 UE-local 实现，按事件触发与周期压力评估及时影响阵型和行动约束，不逐次等待 Agent 或后端推理。个人感知与队伍报告按来源过滤，私有恐惧、解释和自主选择仍归角色智能体；不以同一士气数值强制所有角色作同一判断。

<a id="dispatch-authorization"></a>

## Dispatch 只验证和引用授权

Dispatch 负责命令的发出/传递/接收/取消等事实；授权事实来自 Organization、Government 或明确基础权威。旧材料中的“命令授权”在 Dispatch 语境仅指授权依据校验，不能生成另一份相互冲突的许可。

<a id="objective-authority"></a>

## Objective 的确认边界

胜负只能由 Objective 依据正式事件、配置和依赖完整性确认；控制事实由 Territory 等实际领域确认，Objective 不直接写入战斗、占领或死亡。援军、敌退、控制、投降、LifeState 和逃跑等触发及时评估；具体胜负条件、30 日体验目标及可选行动由正式产品文维护。

<a id="resource-domains"></a>

## 库存、运输、生产设施、人口劳作与生存

### 第一阶段 P1：县城持续运转

### Inventory / Resource Owner

**唯一事实**：资源批次、数量、质量、容器、预留、转移、消耗、损失和存储关系；装备关系/耐久归 Equipment，法律产权归 Ownership，容器空间位置引用 Presence。

- Static Data：粮、盐、水、草料、木材、石料、铁料、箭矢、油、金汁、檑木等物品定义、规格、堆叠、质量和保质规则；
- Runtime State：容器、数量、质量、污染、预留、损耗和存储容量；产权与装备状态仅保存外域引用，不复制写权；
- Command：`reserve`、`load`、`unload`、`consume`、`transfer`、`destroy`；`equip` 由 Equipment 或跨域 Workflow 承接，Inventory 只处理本域转移/预留；
- Resolver：权限、容量、重量、兼容性、污染、保质期和成本；
- Event：`reserved`、`loaded`、`delivered`、`consumed`、`spoiled`、`lost`、`transferred`；
- 连接：Production、Transport、Combat、Survival、Government 读取其投影，不直接写库存；
- 投影：县城库存、军需库存、个人背包、仓储容量和短缺预警。

Paralls 现有模块中的容器、负重、装备和运输片段须按目标写集拆分核验：容器/数量归 Inventory，装备归 Equipment，运输阶段归 Transport；再补多规格军需与围城消耗链。

### Transport / Logistics Owner

**唯一事实**：运输批次、承运人、路线阶段、护送、抵达、损失、拦截和恢复。

- Static Data：载具、驮畜、道路容量、路线、运输速度、护送规则、拦截规则；
- Runtime State：批次、货物预留引用、Presence 位置引用、目标、护送、阶段与损失记录；实际货物增减由 Inventory 提交；
- Command：`create_shipment`、`dispatch`、`escort`、`reroute`、`intercept`、`recover`；
- Resolver：库存预留、Presence、路线、敌方控制、天气、护送和玩家干扰；
- Event：`shipment_created`、`departed`、`rerouted`、`intercepted`、`partially_lost`、`delivered`；
- 连接：Inventory 提供货物事实，Presence 提供空间事实，Command Owner 传递命令，群体模拟推进远处运输；
- 投影：粮道状态、预计抵达、实际损失、运输队位置和可干预窗口。

Paralls 的 TransportRecord 只是运输批次状态窄纵切，尚不等于完整寻路、拦截和绕行系统。

### Production / Facility Owner

**唯一事实**：登记设施/设备的完整度、机械开闭/闩锁、工作状态、工艺、工单、工序、产出认证和故障。工单参与关系引用 Work 的劳力/班次及 Organization 的岗位授权，物资预留引用 Inventory，不取得这些领域的写权。

- Static Data：设施、工艺、配方、材料规格、工种、设备、产能、质量和失败规则；
- Runtime State：设施状态、工作班组、生产任务、输入预留、进度、产出和停工原因；
- Command：`open_facility`、`assign_work`、`start_production`、`pause_production`、`complete_production`、`repair_facility`；
- Resolver：设备、匠人、材料、岗位、工艺条件、时间、质量和安全；
- Event：`facility_opened`、`work_assigned`、`production_started`、`production_progressed`、`output_certified`、`production_failed`；
- 连接：Organization 提供岗位，Inventory 提供材料，Population/Work 提供劳力，Command/Character 提供请求；
- 投影：工坊状态、生产队列、材料短缺、预计产出和停工原因。

### Population / Work Owner

**唯一事实**：居民登记、工作关系、工种、班次、家庭责任、劳力可用性和调派结果。

- Static Data：职业、技能门槛、工作条件、班次、家庭责任模板、训练路径；
- Runtime State：当前工种、岗位、班次、家庭义务、是否可调派；疲劳/伤病是 Survival/Body/Status 的只读投影，不作为 Work 的独立可写数值；
- Command：`assign_job`、`request_recruitment`、`train`、`rest`、`reassign`、`mobilize`；
- Resolver：技能、身体状态、组织许可、待遇、家庭责任、当前岗位和拒绝/延迟规则；
- Event：`job_assigned`、`assignment_delayed`、`training_started`、`mobilized`、`rest_started`、`work_refused`；
- 连接：B0/B1 负责低成本推进和候选，Character Agent 负责个体判断，Organization/Production 负责岗位和任务；
- 投影：居民工作表、岗位缺口、可用劳力、训练状态和调派原因。

它不替代 Character Core：工作事实属于公共世界账，角色是否愿意、理解和记住属于角色记忆账。

### Survival Owner 与 Medical Workflow

**Survival Owner 唯一事实**：饥渴、疲劳等客观生存指标。生命/体力/伤势由 Body Owner 拥有；流血/感染等状态效果由 Status Owner 拥有；物资由 Inventory Owner 拥有。

- Static Data：生存指标消耗曲线、单位、边界、公式和条件阈值；
- Runtime State：饥渴、疲劳等生存指标；可以读取 Body/Status 投影，但不复制其权威状态；
- Command：`consume_supply`、`rest`；进食意图由角色 Agent 产生，组织配给可作为有来源的 Command；
- Resolver：环境、劳作、营养、休息和身体基线对生存指标的影响；
- Event：`need_increased`、`survival_metric_changed`、`rest_completed`；
- 连接：Inventory 提供已确认的消费结果与药材库存，Production 提供产出认证；角色 L1 接收 Survival/Body/Status 的受限身体投影；
- 投影：饥渴、疲劳等指标和生存条件。

Medical Workflow 是非领域 Owner 的流程组件：记录治疗请求、方案步骤、执行进度、依赖 receipts 和开放义务；发出 typed Command，编排 Inventory、Body、Status，并在所需 receipts 到齐后更新流程结果。它不提交生存指标、库存、生命、伤势或效果事实。药物不能由治疗动画直接扣除，补血不能由恢复组件旁路写入。UE 输入、治疗动作、进度、GAS 效果和反馈均可改造复用；若将身体/效果结算部署在 UE 内，须显式声明对应事实 Owner 的执行位置、唯一写入口及暂停/恢复策略。规则、部署和异常验收见[UE、Workflow 与 WRK 边界](../05-运行时接入/01-UE本地提交与Paralls同步.md#workflow-wrk-boundary)。

<a id="resource-contract-supplement"></a>

## 资源字段、来源、绑定与运输后果

### Inventory / Resource

首批物资：粮食、水、盐、草料、药材、木材、石料、铁料、箭矢、武器、檑木、金汁、火油、马匹、驮畜、工具和现金/贸易物资。

每种物资至少区分：数量、质量、容器、预留、产权、保管、事实控制、存储容量、污染/损坏和当前位置。

Inventory 还必须通过领域内的 Model Binding 区分食品变质、木材腐朽、铁料锈蚀和箭矢受潮等模型。只有资源标签、仓库/容器能力、作用域、生命周期和输入 revision 同时满足时，模型才可被 Inventory Owner 选中。模型结果不能由调用者直接提交为 `spoiled` 或 `quality_loss`，必须经过 Inventory Authority 的评估、revision 校验和事件提交。

来源约束：

- 县城周边可有木厂和石矿场；
- 本地没有盐原产地；
- 铁料来自外部，但县城有铁料储备；
- 农具等铁器可作为可回收铁料来源；
- 木材和石材可以来自城内房屋、家具和设施拆解，但会损害居住和防御设施。

### Transport / Logistics

运输批次记录货物预留、承运人、路线阶段、当前位置、护送、阻挡、绕行、拦截、损失和入库 receipt。

UE 负责局部路径执行和实时表现，Transport Owner 负责批次事实。玩家站在路线、敌方攻击运输队或路线被封锁时，必须得到等待、绕行、拦截、损失或放弃之一的明确结果，不能瞬移到达。

<a id="production-contract-supplement"></a>

## 生产完整公式、模型分工与认证

### Production / Facility

设施、设备、匠人、原料、生产任务和产出认证分开记录。一个集中铁匠坊和多个分散铺子可以在设备、匠人、原料和组织许可齐全时组合成生产线；生产由本域 Numeric / Condition / Hybrid 模型协作处理：Condition 判断能否开工，Numeric 计算产能/质量/数量，Hybrid 推进工序与中断状态；版本化 Static Data 和 Binding 固定适用范围：

```text
产出 = 配方基础产能
     × 设备状态
     × 匠人技能
     × 原料质量
     × 劳力可用性
     × 工艺/时间条件
     × 安全与中断修正
```

首个 Demo 的内容切片只要求箭矢、简易武器、修城木料/石料和一种攻守消耗品可生产；完整武器、护甲和复杂器械的配方数据留在后续阶段，Production Owner 的领域模型、跨域预留、取消、停工、产出认证和回放能力第一阶段即交付；原料/成品数量归 Inventory，劳力/班次归 Work。

<a id="body-domains"></a>

## 生存、身体和 Medical 的领域边界

### Survival / Medical

第一阶段内容切片只启用粮、水、盐、疲劳、伤势、医舍队列和劳动能力对守城的可观察影响。缺粮、缺水或缺盐不能直接扣一个全局混乱值，必须经过消费、生存指标、身体状态、劳力、组织和士气逐层产生后果。治疗动画和交互可由 UE 传统路径执行；库存消耗、生命/伤势变化、状态效果变化必须分别经 Inventory、Body、Status Owner 提交。医疗流程负责串接这些回执；UE-local authoritative 只能通过 Owner Manifest 显式启用，不能由 Pawn/Buff/动画自行加血。

<a id="social-government"></a>

## 社会、情报与政务

### 第一阶段 P2：社会、情报和后续战争扩展

### Social / Influence Owner

**唯一事实**：公共关系事实、公开声望、非政治承诺、影响力变化和社会后果证据；个人私有态度归角色心智，派系公共政治承诺与政治立场归 Politics。

- Static Data：关系类型、社会身份、派系、声望规则、承诺模板和证据等级；
- Runtime State：可共享关系边、非政治承诺、声望、矛盾和暴露范围；私人信念不复制为本域可写事实；
- Command：`speak`、`negotiate`、`promise`、`threaten`、`recruit`、`betray`、`report`；
- Resolver：身份、关系、证据、场合、利益、传播范围和可信度；
- Event：`statement_made`、`promise_recorded`、`relationship_changed`、`influence_changed`；政治转向由 Politics 提交；
- 连接：角色智能体拥有主观 Social Memory，Owner 只确认社会事件和公开后果；群体模拟产生影响边候选；
- 投影：公开关系、声望趋势、承诺状态和可见社会证据。

### Information / Intelligence Owner

**唯一事实**：情报来源、报告、可信度、传播路径、误报、泄露和已确认的知情范围。

- Static Data：信息类型、来源可信度、传播媒介、保密级别、识别规则和有效期；
- Runtime State：情报记录、来源、可信度、已知角色、传播节点、过期和冲突；
- Command：`observe`、`scout`、`report`、`relay_information`、`verify`、`suppress`、`leak`；
- Resolver：视野、距离、身份、传播媒介、来源关系和报告一致性；
- Event：`information_observed`、`report_submitted`、`report_received`、`report_verified`、`misinformation_spread`；
- 连接：角色只接收私有感知/合法收到的信息，群体模拟产生情报候选，Command Owner 传递实际报告；
- 投影：玩家掌握的情报、来源、可信度、时效和传播路径。

### Government / Policy Owner

**唯一事实**：政令、许可、封锁、征发、配给、治安和制度窗口。

- Static Data：政策、权限、适用范围、例外、持续时间、惩罚和撤销规则；
- Runtime State：有效政令、政策 revision、辖域、执行状态、例外和申诉；
- Command：`issue_policy`、`order_gate_closure`、`requisition`、`ration`、`permit`、`revoke_policy`；
- Resolver：统治者身份、辖域、组织授权、资源、时间、冲突政策和执行能力；
- Event：`policy_issued`、`gate_closure_ordered`、`requisition_recorded`、`ration_changed`、`permit_granted`、`policy_revoked`；
- 连接：角色提出政令意图，Organization 验证职位，Command/Information 处理传达，Population/Inventory/Transport 执行后果；城门机械开闭/闩锁归 Facility，实际通行归 Presence，控制归 Territory，政令不能直接生成 `gate_closed` 机械事实；
- 投影：玩家可见政令、执行覆盖、例外、执行失败和民众知情范围。

<a id="domain-dependencies"></a>

## 公共契约与数值结算

伤害/体力/效果的并发、死亡和医疗中断详见 [结算合同](../04-模型与结算/02-数值状态效果与跨Owner结算.md#numeric-settlement)；角色能否知道某一事实详见 [受限投影](../02-公共契约/03-受限查询与投影.md#restricted-projections)；执行节奏仅引用 [唯一完整 UE 协作矩阵](../05-运行时接入/01-UE本地提交与Paralls同步.md#ue-cadence-matrix)。
