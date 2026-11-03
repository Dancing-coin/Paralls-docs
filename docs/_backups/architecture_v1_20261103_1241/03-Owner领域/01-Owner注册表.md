# 01-Owner注册表

> 版本：1.0（职责拆分版）
> 更新日期：2026-10-30
> 评审状态：职责归位与静态一致性核对；不替代产品待决项裁决或实现评审。
> 实现状态：本篇为目标合同；已有实现仅按原始证据日期记录，不代表全量实现或运行验收完成。
> 验证范围：本轮仅重组文档，未执行代码、UE、PIE 或性能验证。原始设计、实现盘点和证据日期分别保留。

[技术架构入口](../README.md) · [唯一 Owner 注册表](01-Owner注册表.md#owner-registry)

<a id="owner-registry"></a>

## 唯一逻辑领域 Owner 注册表

本表是唯一完整名单：**23 个**逻辑领域写权。别名不重复计数；一个模块可承载多个 Owner，同一 Owner 可按区域/实体流分区。宿主数量和近远场精度不改变逻辑领域。建设批次、任务依赖与放行时间归生产计划；本表保留第一阶段/后续内容覆盖和领域完成标准，不以排程代替合同。

完整近场/远场分类见 [UE 协作与节奏矩阵](../05-运行时接入/01-UE本地提交与Paralls同步.md#ue-cadence-matrix)，这里不复制第二套部署名单。

| # | Owner | 唯一事实与关键边界 | 事实覆盖补充 | 第一阶段内容 | 后续扩展 | 领域能力标准 |
|---|---|---|---|---|---|
| 01 | Presence / Movement | 位置、占用、到达、阻挡、改道；NavMesh 和 Actor 连续轨迹是执行/证据，按语义边界承认事实 | 角色、队伍、运输批次、器械的位置、占用、到达、阻挡、绕行、拦截和脱离 | 召陵县、村落、粮道和攻方营地 | 跨县道路、关隘、商路和战线 | 位置提交点、路径 revision、冲突和回滚可回放 |
| 02 | Command / Dispatch | 命令的传达、理解、接受、拒绝、过期与执行跟踪；实际执行结果引用目标 Owner receipt | 命令授权依据校验与引用、传达、理解、接受、拒绝、过期和执行状态 | 求援、守城、调拨、修缮、生产和护送 | 郡县军令、跨区域传令、政令传播 | 同一命令合同覆盖人类、Agent、群体和脚本 |
| 03 | Organization / Military | 岗位、层级、编制、指挥授权、预案、继任；战俘子域管理拘押/编入关系 | 岗位、层级、指挥权、授权范围、编制、预案、继任 | 县令、亲卫、一营三队（原县城配置，三队数量待决，见 [D03](../../PRD/00-产品总纲/设计决策与待决问题.md#d03)）、村落和工坊负责人 | 县际、郡级、州级军政组织与军团 | 继任、授权变更和组织 revision 可恢复 |
| 04 | Government / Policy | 政令、许可、封锁、征发和配给规则；不直接改变产权或库存 | 政令、许可、封锁、征发、配给、治安、制度窗口和行政授权 | 县城封锁、路引、征发、坚壁清野、配给 | 郡县治理、税粮、治理政策和州级政策 | 政策冲突、例外、撤销和执行覆盖有事件流；不写产权或占领控制 |
| 05 | Information / Intelligence | 报告、来源、可信度、传播与知情范围；不拥有角色私人理解 | 情报来源、报告、可信度、传播、误报、泄露和知情范围 | 军情、侦察、传令、粮道和敌营信息 | 细作网、跨区域情报、舆论和战略误导 | 知情边界、时间和来源可信度可重建 |
| 06 | Combat / Damage | 攻击、接触、命中、格挡、伤害评估；不写生命、耐久或死亡 | 攻击尝试、命中、格挡、伤害评估和战斗接触；不拥有生命、伤势、护甲耐久和持续效果 | 骑战、城墙攻防、器械和队伍战斗 | 跨战区、军团和多战线战斗 | UE-local Combat 可结算自身事实；Body/Equipment/Status 各自提交授权结果，同一命中链原子提交或记录开放义务 |
| 07 | Body / Resource | 生命、体力、伤势、身体功能和能力限制；不拥有物资或死亡转换 | 生命、体力、伤势、部位功能与能力限制 | 战斗受伤、动作成本、医舍治疗、劳力状态 | 疫病、军团医疗、长期恢复和人口健康 | 近场与 Combat 本地协作；体力积分/动作准入、唯一写权、revision 和回放可验证 |
| 08 | Equipment | 装备关系、防护状态、耐久与破损；装备物品的数量由 Inventory 管，产权由 Ownership 管 | 装备关系、防护状态、耐久和破损；物品数量归 Inventory，法律产权归 Ownership | 近场防护、耐久消耗、破损和换装 | 军需换装、修复、缴获与跨阶段装备连续性 | 固定装备 revision，与 Combat/Body 授权片段协作；不得重复扣耐久或以 Actor 字段双写 |
| 09 | Status / Effect | 效果实例、强度、来源、tick/退出生命周期；周期伤害请求 Body 结算 | 流血、中毒、燃烧、眩晕、感染等效果实例及生命周期 | 伤口流血、持续伤害和治疗解除 | 持续伤害、效果组合和跨阶段疾病 | 效果有来源、强度、tick/退出条件；效果表现不直接修改身体数值 |
| 10 | LifeState | 存活、倒地、濒死、死亡等规则转换；health==0 是依据，不是自动死亡 | 存活、倒地、濒死、死亡等生命周期转换 | 由身体依据确认倒地/死亡，限制普通治疗 | 复苏、连续性及适用世界规则 | 与 Body 分域；生命归零不自动死亡；近场及时转换，事件/回放/交接可验证 |
| 11 | Morale / Formation | 个人/队伍士气、纪律、阵型状态、溃退和重整；不替代 Agent 的情绪、信念和决定 | 个人/队伍士气、阵型、纪律、溃退、重整和目标压力 | 守军、敌军队伍和军旗 | 军团、战线、政治合法性和长期军心 | 近场 UE 协作；输入来源、公式版本、阈值和恢复可审计；不替代 Agent 心智 |
| 12 | Territory / Control | 地块、道路、设施与城池的控制、争夺和占领；位置、产权和政治承认各有自己的 Owner | 地块、设施、道路、城池、关隘和战区的事实控制、占领、争夺、辖界和控制转移 | 县城、城门、粮道、村落和敌营的控制状态 | 跨县、郡、州占领，战线、边界和治理接管 | 控制转移必须由军事/治理/公开承认条件共同结算；Objective 只能读取，不得代写 |
| 13 | Objective / Victory | 场景目标、胜负与摘要；只读取已确认控制、生命周期和援军等结果 | 当前场景目标、胜负条件、结局和结算摘要 | 援军/敌退胜利，投降/死亡/逃跑失败；原表“失守”边界见 [D08](../../PRD/00-产品总纲/设计决策与待决问题.md#d08)，不据本表新增失败阈值 | 阶段性任务和可追溯结局 | 只能引用已确认事实；失守由 Territory、死亡由 LifeState 等事实 Owner 确认，Objective 不写身体/控制权/合法性 |
| 14 | Campaign / Strategic State | 战役目标、阶段推进、继承与历史分岔；不让章节脚本重写下层事实 | 战役、势力和长期战略目标、阶段推进、历史分岔和继承条件 | 用固定 fixture 验证跨阶段存档、目标进度和失败继承，不扩展第一阶段地图 | 战役目标、势力存续、历史分岔、长期继承和战略结算 | 只读取各领域 receipt；阶段推进、继承和分岔必须可回放 |
| 15 | Inventory / Resource | 批次、数量、质量、容器、预留、转移、消耗和存储状态；不写法律产权 | 物资批次、数量、质量、容器、预留、转移、消耗、损失和存储关系；装备归 Equipment | 粮水盐、草料、木石铁、箭矢和攻守消耗品 | 税粮、贸易、战略仓储和跨区域资源网络 | 规格、质量、污染、容器迁移可回放；不判断法律产权 |
| 16 | Ownership / Property | 所有权、保管权、使用权、查封与转移；不把持有物品等同法律拥有 | 物资、设施、土地、牲畜、装备和账户权益的法律/契约产权、保管权、使用权、查封和转移 | 县仓、工坊、农具、房屋拆解和征发的产权/保管/使用权区分 | 占领后的接管、商贾资产、税户、继承和跨区域产权 | 产权转移必须有授权、对价/征发理由、争议、证据和可逆恢复；Inventory 只能引用产权结果 |
| 17 | Economy / Market | 账户、报价、订单、债务、税费、合同与结算义务；现金不能只靠库存字段代替 | 账户、现金流、报价、订单、债务、税费、合同、市场成交和结算义务 | 现金/贸易物资、军需预算、商人报价和一条可观察的交易链 | 县际商路、税粮、债务、市场夺权和经济战 | 账务结算、合同履约、欠款和价格变化可回放；不得把库存数量直接当作现金流 |
| 18 | Transport / Logistics | 承运批次、路线阶段、护送、交付和损失记录；位置归 Presence，货物增减归 Inventory | 运输批次、承运人、路线阶段、护送、抵达、损失、拦截和恢复 | 县城粮道、援军、铁料和生产运输 | 商路、跨县粮网、战略运输和封锁 | 路线、占用、绕行、拦截和部分交付可恢复 |
| 19 | Production / Facility | 登记设施/设备的物理完整度、机械开闭/闩锁、工作状态、工艺、工单、进度、故障与产出认证；不自写原料和成品数量 | 登记设施/设备完整度、机械开闭/闩锁、工作状态、工艺、工单、进度、产出认证和故障；班组/物资仅引用 | 铁匠坊、木厂、石料点、箭矢和修缮 | 多县生产链、工坊网络、军需和产业迁移 | 领域 Numeric/Condition/Hybrid 模型、配方版本和产出认证可回放；城防设施子域在 V2 前就绪 |
| 20 | Population / Work | 居民/家庭的公共登记、工种、班次、劳力可用和调派；档案技能不复制，身体与疲劳只读 | 居民、家庭、工种、班次、劳力、迁移和调派结果 | 县城、村落、民夫、工匠和运输人员 | 县际迁移、兵源、税户和区域人口网络 | B0/B1 候选与个体 Agent 交接不丢连续性 |
| 21 | Survival | 饥渴、长期疲劳等生存指标；生命/体力归 Body，物资消费归 Inventory | 饥渴疲劳等客观生存指标 | 守城补给、劳动能力和个体生存 | 疫病、军团医疗和长期恢复 | 只写自身指标；消耗物资由 Inventory、生命/伤势由 Body、效果实例由 Status 提交 |
| 22 | Social / Influence | 公开关系、个人/组织承诺、声望和影响力；私人印象在记忆账，派系公共政治承诺由 Politics 管 | 公共关系、非政治承诺、声望、影响力和公开后果；派系公共政治承诺归 Politics | 豪强、村落、商人、将领和居民关系 | 多势力政治、联盟、背叛和招降 | 私有记忆与公共社会事实分离；不直接写公开合法性或辖域 |
| 23 | Politics / Legitimacy | 公开承认、合法性、政治授权、外交及派系公共政治承诺；不等同影响力数值 | 公开承认、派系承诺、合法性、政治授权、外交关系和政治后果 | 征发、封锁、赈济、违约或失守后的公开承认与派系反应 | 任命、表奏、盟誓、质子、联姻、赎俘、外交和治理稳定 | 公开政治事实与个人态度分离；每次承认、违约和关系转移有证据链 |

<a id="non-owner-responsibilities"></a>

## 不计入领域名单的职责

名单之外的职责明确归位：

- **Character Core / Agent：** 复用角色档案与私有心智/记忆权威；不是新增的公共身体或社会事实 Owner。
- **Activation / Handoff / Continuity / Lease：** 推进权治理，不是角色的 LifeState；退出高精度不等于死亡。
- **World Clock / Identity / Capability：** 基础事实与授权权威，按 I01 实现，不与领域 Owner 重复计数。
- **Medical、城防、求援、生产线、征发、交易与进食：** 跨 Owner Workflow，不增加同名万能玩法 Owner。
- **Ability：** 核验已有能力声明、动作准入与授权合同；逐字段映射到基础授权、Body、Status、Equipment、Combat 与 Presence，不以旧模块名新增写权。
- **ESM / embodied：** 可选择复用已核验的结构化交互、执行许可、证据和结果合同，不是统一 Command 的必经入口，不新增万能 ESM Owner。Godot 执行器和桥接代码不能直接用于 UE，需由 UE 原生执行器实现获准合同；旧对象状态、生命/体力等写入口必须映射到相应领域后停用重叠写权。详见[ESM 复用与迁移](../05-运行时接入/03-ESM复用与迁移.md#esm-migration)。
- **精神与灵魂：** 沿用 Paralls 现有 LifeState、Character Core 等合同逐项核验；本计划不把这些名称擅自并入生命/体力，也不新增未经定义的 Spirit/Soul Owner。

<a id="medical-workflow"></a>

## Medical Workflow

医疗只拥有治疗请求、方案步骤、执行进度与待完成义务。医舍队列、治疗中断和回执汇总可扩展到长期护理；它编排 Inventory、Body、Status，并校验 LifeState，不取得这些领域的写权。流程状态可恢复。详见 [医疗结算与中断](../04-模型与结算/02-数值状态效果与跨Owner结算.md#medical-workflow)。

<a id="owner-classification"></a>

## Owner 分类轴与支撑组件

### Owner 和支撑组件

Owner 对一组 canonical facts 承担最终写权，负责定义事实、接受哪些 Command、使用什么公式和条件、校验不变量、提交事件并提供可回放结果。

| 组件 | 职责 | 不拥有的事实 |
| --- | --- | --- |
| EventStore / 三本账基础设施 | 原子提交、事件历史、revision、幂等、receipt、outbox、replay | 不决定领域规则是否合法 |
| Command Gateway | 来源身份、权限上下文、作用域、时效和路由 | 不修改生命、库存、位置或组织事实 |
| Projection / Query | 为 Agent、UE、群体模拟提供受限读取面 | 不拥有被投影的 canonical facts |
| Workflow / WRK | 排程、依赖、预算、交接、恢复和回执跟踪 | 不代替领域 Owner 结算事实 |
| Character Agent | 感知、主观解释、目标排序、意图和执行语义 | 不拥有世界真相，不直接写领域状态 |
| UE Adapter / 表现 | 玩家输入、局部物理/执行证据、动画和视觉反馈 | 不以动画或本地预测确认持久玩法结果 |

### Owner 的分类轴

“基础”和“原子”不是互斥类别；“组合”是过程职责，与它们属于不同分类维度。下文 Composite Owner 是沿用的过程名称，不是第 24 个领域写权，注册时标为 Workflow/协调组件；只有持有明确事实写集的条目进入领域 Owner 名单。

- **基础权威（Foundation Authority）**：世界时间、实体身份与基础能力授权。空间/占用、法律产权、物资容器分别由 Presence、Ownership、Inventory 领域拥有；其基础依赖性质不意味着另建同名基础写权。
- **领域 Owner（Domain Owner）**：拥有业务领域事实，例如库存、身体、生存、装备、状态效果、关系、士气、建筑或生产。
- **原子 Owner（Atomic Owner）**：维护紧密不变量和最小独立写入边界，例如库存数量/预留、护甲耐久或身体生命值。
- **组合 Owner（Composite Owner）**：组织多个领域 Owner 完成过程，例如进食、战斗、生产、运输和城防；不取得下层事实写权。

Owner Registry 应使用独立字段表达：

```text
foundation_scope: foundational | domain
transaction_role: atomic | composite
```

例如 `Inventory` 是 `domain + atomic`，`World Clock` 可以是 `foundational + atomic`，`Survival` 是 `domain + atomic`；进食或医疗则由 Workflow 协调多个原子 Owner。

<a id="owner-manifest"></a>

## 完整 Registry / Manifest 字段

### Owner Registry 最低字段

```text
owner_id / owner_version
foundation_scope / transaction_role
canonical_facts / adjacent_facts_denied
stream_pattern / command_types / owned_events
formula_refs / condition_refs / invariant_refs
model_registry_scope / allowed_model_types / model_binding_scope
input_owner_refs / output_effect_mapping / evaluation_cadence
model_conflict_policy / model_version_pin_policy / model_migration_policy
read_set / input sources / revision pins / visibility
success, rejection, partial, cancel, expiry, compensation events
execution_host / execution_mode / canonical_writer / commit_store
authority_scope / authority_epoch / prediction / reconciliation
simulation_cadence / trigger_types / latency_budget / commit_boundary
commit_authority_scope / outbox_sync_policy / crash_recovery_policy
workflow capabilities / dependencies / open obligations / recovery
projection contracts and role-visible fields
```

Registry 负责发现、版本治理和接口校验，不是任意声明事实的万能入口。

上述字段是目标合同，不能据此宣称现有 Paralls 已实现。Owner 是逻辑写权边界，不要求一 Owner 一进程、一次本地函数调用一次网络往返。近场 Combat、Body、Equipment、Status 可在 UE 中共同部署，通过本地调用生成各自授权结果，再提交同一事件批次；持久化完成并取得 receipt 前只能称为 pending/predicted。UE C++、Blueprint、GAS/AttributeSet/GameplayEffect 可以承载经过改造的 Owner 规则及受控写入口，不能保留绕过该入口的另一条扣血/回血路径。

`commit_store` 是逻辑权威账的合同，不是固定部署到 Python 后端。本地可靠提交若被注册为该事实流的唯一权威，取得 receipt 后即可确认，后端接收副本不重新裁决；若只有后端 store，本地计算完成仍为 pending，不能以异步上传冒充已提交。

<a id="seven-part-contract"></a>

## 七部分领域合同与模型依赖

### 新 Owner 统一需求模板

每个新 Owner 都必须提供以下七部分：

| 部分 | 必须定义 |
|---|---|
| Static Data | 规则版本、类型、配方、阈值、能力、状态转移、权限定义 |
| Runtime State | 本域唯一事实、状态机、revision、时间字段、来源和生命周期 |
| Command | 可接受的命令类型、输入、来源、证据、预期 revision |
| Rule/Resolver | 权限、前置条件、成本、冲突、效果、失败和部分完成计算 |
| Authority | 唯一写入入口、事件流、幂等、CAS、receipt、恢复和回放 |
| Event/Result | 成功、拒绝、延迟、部分完成、过期、损失和补偿事件 |
| Presentation/Query | 给 UE、角色智能体、群体模拟和 UI 的受限投影 |

Owner 之间的组合只能通过 `Command`、已授权 fragment、revision pin 和 receipt 完成，不共享可写内部对象。

### 领域模型依赖合同

七部分契约之外，每个 Owner 必须声明自己的模型依赖合同。模型只允许在所属领域内复用；同一领域可以通过不同 Numeric、Condition 和 Hybrid Model，以及不同 Static Data 参数和 Applicability Binding，支持同类玩法的差异化结算。

```text
Model Dependencies
  ├─ domain_owner_id
  ├─ allowed_model_types
  ├─ model_registry_scope
  ├─ applicability_binding_scope
  ├─ input_owner_refs
  ├─ output_effect_mapping
  ├─ evaluation_cadence
  ├─ conflict_policy
  ├─ version_pin_policy
  └─ migration / replay policy
```

模型本身只返回评估结果，不直接提交世界事实。Owner 必须负责解析模型绑定、固定输入 revision、执行模型、校验不变量并提交自己的事件。`Inventory` 可以使用食品变质、木材腐朽和铁料锈蚀等同领域模型，但这些模型不能跨领域写入 Body、Politics 或 Territory。完整规范见[01-领域模型注册绑定与评估](../04-模型与结算/01-领域模型注册绑定与评估.md#domain-models)。

<a id="owner-delivery"></a>

## 每个 Owner 的完整交付包

### 每个 Owner 都要交付的完整包

对 23 个 Owner 使用同一完成标准，而非同一套业务公式。展示与查询是领域边界的一部分，不表示 Owner 自己播放动画。

- [ ] **事实与不变量：** canonical facts、禁止写入的邻域事实、主体/地域/时间作用域、stream、唯一写入口。
- [ ] **七部分契约：** Static Data、Runtime State、Command、Rule/Resolver、Authority、Event/Result、Presentation/Query。
- [ ] **模型包：** 适用的 Numeric / Condition / Hybrid；输入输出 schema、单位、精度、阈值、状态机、确定性与随机种子策略。无数值计算的 Owner 可声明该类不适用并说明理由，不硬造公式。
- [ ] **适用绑定：** 模型归属、资源/实体标签、设施能力、条件、作用域、有效窗口、优先级与冲突策略；停用和更改也有版本/生效边界。
- [ ] **评估上下文：** 模型/公式/条件/Binding 版本、输入 revision vector、world_tick、时间窗、稳定顺序、来源与 evidence。
- [ ] **权威与部署：** execution_host/mode、canonical_writer、authority_scope/epoch、commit_store、触发/更新节奏、延迟预算、提交边界、预测和校正策略。
- [ ] **提交与结果：** 领域事件、revision/CAS、幂等、receipt、拒绝、取消、过期、部分完成、损失和恢复语义；不适用的结果明确拒绝，不制造假流程。
- [ ] **读取与连续性：** 给玩家、Agent、群体、UE 的受限投影；checkpoint/replay、未知结果查询、未决义务、交接与版本迁移。
- [ ] **证据：** 正常、拒绝、重复、旧 revision/epoch、无效 lease、暂停、断线、崩溃恢复和投影重建测试；适用的跨域流程至少有中断与恢复路径。

复用现有实现也必须通过同一标准。只有接口是“已定义”，规则能运行是“可执行”，连接 UE 是“已接入”，故障与回放证据齐全才是“已验收”。这四个状态分别记录。

<a id="delivery-details"></a>

## 完整包的补充字段与状态目录

### Owner 正式交付物

“正式实现”不是创建一个接口或返回一个占位 receipt。每个 Owner 在第一阶段基础设施阶段门前必须有可执行的通用准入、规则结算、事件提交、拒绝、恢复和重放路径，并按领域适用性支持部分完成等结果；没有第一阶段实体的规则可以由版本化 Static Data 配置为空，但不能缺少规则引擎、状态机和测试入口。每个 Owner 必须交付：

- Owner Registry 条目：`owner_id`、事实范围、stream 命名、写入口和版本；按[UE 协作与节奏矩阵](../05-运行时接入/01-UE本地提交与Paralls同步.md#ue-cadence-matrix)登记 execution_host/mode、scope/epoch、commit_store、触发/模拟/提交节奏与延迟预算；
- 七部分领域契约：Static Data、Runtime State、Command、Rule/Resolver、Authority、Event/Result、Presentation/Query；
- 领域模型依赖合同：允许的模型类型、模型 Registry 范围、Applicability Binding 范围、输入 Owner、效果映射、评估频率、冲突策略、版本固定和迁移/replay 策略；
- 数值模型、条件模型和混合模型的定义、输入/输出 schema、单位、参数、阈值、状态机和适用绑定；模型必须限定在所属领域内，不能跨域写事实；
- 事件目录和状态转移表，明确成功、拒绝、过期、部分完成、取消、损失、补偿和恢复的适用条件；不适用的结果明确拒绝；
- revision/CAS、幂等键、receipt、outbox、checkpoint、replay 和投影重建接口；
- 与角色 Agent、B0/B1 群体模拟、UE Mirror 和 UI 的受限 Query/Projection；
- 跨 Owner 依赖、输入事件、授权 fragment、输出 receipt 和 recovery action；
- Model Evaluation Context：`evaluation_id`、`world_tick`、模型/绑定版本、输入 revision vector、公式/条件版本、评估顺序和下一次评估时间；
- 成功、失败、幂等、旧 revision、暂停、断线、恢复和回放测试。

### Owner 阶段启用原则

第一阶段可以暂不制作完整全国税制、跨州运输或军团编制，但不能暂不建立相应 Owner 的基础契约。内容团队交付的是召陵县实体、规则参数和场景数据；基础设施团队交付的是所有 Owner 的正式可扩展接口和治理能力。

<a id="cross-stage-coverage"></a>

## 跨阶段事实覆盖审查

### 五阶段事实覆盖审查

以下事实不能只作为某个 Owner 的附属字段存在。它们必须有明确的唯一写权，否则后续阶段会出现“库存变了但产权没变”“占领成立但辖域没变”“胜利系统直接写控制权”等无法回放的隐性双写：

| 跨阶段事实 | 唯一 Owner | 允许读取的 Owner | 禁止的替代实现 | 第一阶段验证方式 |
|---|---|---|---|---|
| 法律产权、保管权、使用权、查封和转移 | Ownership / Property | Inventory、Economy、Government、Transport、Production、Social | 把 `owner_id` 写在物品 Actor 或仓库蓝图上并视为事实 | 征发、农具拆解、工坊领料各一条授权和产权 receipt |
| 账户、债务、报价、合同和结算义务 | Economy / Market | Ownership、Inventory、Production、Government、Politics | 用库存数量或 UI 金额直接增减现金 | 一次军需采购/欠款/部分交付的可回放账务链 |
| 地块、设施、道路和城池控制 | Territory / Control | Presence、Government、Combat、Objective、Politics | Objective 或关卡脚本直接把目标标成“已占领” | 用 fixture 验证城门、粮道和村落的控制转移与争议状态 |
| 公开合法性、派系承诺、外交关系和政治授权 | Politics / Legitimacy | Social、Government、Organization、Campaign | 把影响力数值直接当成合法性或命令权限 | 一次征发/赈济/违约导致的公开承认和派系后果 |
| 城门政令 / 机械状态 / 通行 / 控制 | Government / Production-Facility / Presence / Territory 分域 | Dispatch、Combat、Objective、Transport | 发布封城政令就直接写门闩、NavMesh 或控制归属；ESM 统一兜底 | 政令送达但门未关、门损坏不可闩、敌占门仍关闭三个 fixture；各域独立 receipt |
| 战役目标、长期进度、继承和历史分岔 | Campaign / Strategic State | Objective、Territory、Politics、Government、Siming | 由章节脚本或胜负 UI 写下一阶段状态 | 从第一阶段 checkpoint 载入第二阶段 fixture，比较 replay 结果 |

共享环境温湿度、火场/烟雾等模型输入必须在 A2 标明唯一来源、写集、作用域与版本；没有授权来源时为 unknown/拒绝，不能在库存或表现中凭空创造全局状态。超出现有写集的环境事实须先评审扩展合同，再启用玩法。

这些 Owner 的“第一阶段验证”可以使用小规模 fixture，不要求把第二至第五阶段的地图和内容提前制作；但 fixture 必须调用正式 Command、Owner、EventStore、receipt、projection、checkpoint 和 replay，而不是测试专用的旁路写入。这样才能证明第一阶段交付的是可承载五阶段的基础设施，而不是仅能通过首个剧本的模拟接口。
