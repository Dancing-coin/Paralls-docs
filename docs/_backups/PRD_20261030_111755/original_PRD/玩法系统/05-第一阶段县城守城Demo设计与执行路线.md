# 第一阶段县城守城 Demo 设计与执行路线

> 文档状态：第一阶段 Demo 基线方案 / 五阶段基础设施基线
> 版本：v0.7
> 日期：2026-10-30
> 适用范围：Guoshang 第一阶段县城守城单人 Demo；UE 5.8 客户端；Paralls 角色智能体、司命和群体模拟接入
> 目标：用第一阶段的召陵县内容验证完整的五阶段基础设施和 Owner 体系；内容范围逐步扩展，基础设施不临时化、不重做
> 依据：
> - [01-Paralls 现有 Owner 与接入分析](01-Paralls现有Owner与接入分析.md)
> - [02-Guoshang 新 Owner 需求与统一 Command 规范](02-Guoshang新Owner需求与统一Command规范.md)
> - [03-基建 Owner 传统方案与 Paralls 兼容方案](03-基建Owner传统方案与Paralls兼容方案.md)
> - [04-衣带诏刘备玩家完整时序案例](04-衣带诏刘备玩家完整时序案例.md)
> - [五阶段战争世界设计大纲](../国殇：汉末_五阶段战争世界设计大纲_v0.1.md)
> - [总策划案](../烽火王座：汉末群雄_总策划案_v1.0.md)
> - [骑将冲阵垂直切片策划案](../烽火王座：汉末群雄_骑将冲阵垂直切片策划案_v0.1.md)

> 场景素材需求：[召陵县第一阶段 Demo 场景素材需求](06-召陵县第一阶段Demo场景素材需求.md)

Owner 分类、角色状态对接、数值规则和跨 Owner 结算的补充基线见[Owner 体系专题](Owner体系/README.md)。

基础设施与全量 Owner 的统一建设批次、最终名单、分工和阶段门见[08-基础设施与 Owner 建设总计划](08-基础设施与Owner建设总计划.md)。本文件继续作为 Demo 体验与 V0—V5 执行路线的依据。

## 1. 方案结论

第一阶段 Demo 不是“骑将冲阵切片”的放大版，也不是多个独立系统拼接的展示场景。它是一段完整的单人县城战争体验：

```text
收到敌军来犯军情
  -> 玩家暂停并确认态势
  -> 立即向外求援，同时组织守城
  -> 县城、村落、攻方营地、粮道和角色按同一世界时钟运行
  -> 玩家通过命令、传令、资源、生产、亲战和代理应对围城
  -> 援兵约 30 个世界日后抵达，或敌军提前崩溃/撤退
  -> 阶段性胜利；县城失守后投降、死亡或逃跑均为失败
```

出城反击、粮道截击、运输护送、夜袭、破坏器械、招降和秘密运输都是可行策略，不是强制任务。玩家可以全程闭城，也可以主动制造更高风险的战场机会；只要守住县城并等到援军，仍然能够胜利。

本 Demo 的核心验证对象是**完整五阶段基础设施能否支撑第一阶段内容**，而不是把基础设施削减成只够演示的临时骨架。资源数量、兵种数量和地图面积可以采用第一阶段内容切片；世界运行内核、Command、EventStore、Owner、三本账、生命周期、投影、回放、恢复和 UE/Paralls 边界必须按五阶段正式架构实现。所有可见结果都必须能够回答：谁提出了什么意图，命令是否实际传达，哪个 Owner 承认了什么事实，角色和玩家何时知道，UE 何时表现出来。

### 1.1 基础设施与内容范围的硬分离

本文件中的“最小”只允许修饰**第一阶段内容规模**，不得修饰基础设施语义、Owner 合同或事实治理能力：

| 范围 | 第一阶段做法 | 五阶段要求 |
|---|---|---|
| 基础设施 | 直接建立正式版本的 WRK、Command Gateway、EventStore、revision、幂等、receipt、projection、checkpoint、replay、recovery、observability 和 UE/Paralls Bridge | 后续阶段复用同一套合同、事件脊柱、时间线、权限和恢复机制，不重建第二套基础设施 |
| Domain Owner | 所有已登记 Owner 都有唯一写权、七部分契约、事件流、receipt、投影、回放、失败/恢复和测试；第一阶段只启用召陵县所需规则和数据规模 | 新增阶段只扩充规则、数据和跨域 Workflow，不改变 Owner 边界或把事实写权转移给 Gateway/WRK |
| 内容规则 | 只制作第一阶段守城需要的县城、村落、粮道、攻方营地、角色和物资 | 第二至第五阶段增加县、郡、州和势力内容，不能迫使基础设施返工 |

因此，“第一阶段先做可玩的守城闭环”是**内容优先级**，不是“先做最小 Owner/最小事件系统”。

## 2. 目标、非目标与反目标

### 2.1 目标

1. 做出一段可连续游玩的县城守城 Demo，至少支持一次完整的“军情—求援—守城—胜负”流程。
2. 建立可延续到后续阶段的世界时间、三本账、Command、Owner、EventStore、revision、幂等、receipt、replay、projection 和 recovery 基础。
3. 让玩家能在有限信息和有限权限下，通过传令、组织、资源和个人行动影响战局。
4. 让角色智能体、群体模拟和 UE 表现使用同一套事实链，且能在近场和远场之间切换而不重置身份或事实。
5. 让每一次胜利、失败、拒绝、延迟、阻挡、拦截和部分完成都可以通过日志和战后摘要复盘。

### 2.2 非目标

- 全国地图、多郡多县、多人联机和联网服务。
- 全量居民使用 LLM；普通居民只需要 B0/B1 低精度推进。
- 完整市场经济、复杂税制、完整政治制度和所有历史剧本的第一阶段内容；相关 Owner 的通用结算、事件和恢复能力仍属于基础设施范围。
- 所有攻城器械、火攻、水攻、地道和完整攻城工程链。
- 大规模高模角色、最终美术、完整配音和复杂 UI 皮肤。
- 让动画、Actor 字段或 GameMode 成为第二套世界真相。

### 2.3 反目标

以下任一情况都视为架构失败，即使画面能播放：

- 打开面板或切换镜头就直接改变远方事实；
- 角色 Agent、群体模拟或 UE 表现层直接写库存、位置、伤害、士气或胜负；
- 事件只能从当前 Actor 状态猜回，不能从事件流重建；
- Bridge 断线时 UE 和 Paralls 各自产生一套互相冲突的结果；
- 玩家不知道命令为什么失败，也无法区分“已下令”和“已执行”；
- 暂停后仍有运输、生产、动画、Agent 或异步回调推进世界；
- 玩家只靠反复单骑冲锋就能稳定解决守城问题。

### 2.4 五阶段基础设施的完成口径

以下能力在第一阶段基础设施阶段门前必须成立，即使对应的全国内容尚未制作：

1. 所有已登记 Domain Owner 都有稳定的 Owner ID、事实范围、唯一写入口、命令集合、事件类型、revision、幂等键、receipt、受限投影、回放和恢复接口；
2. Owner 之间只能通过 Command、授权 fragment、revision pin、receipt 和 Workflow 协作，不共享可写运行对象；
3. WRK 能处理单人暂停、窗口、预算、固定读集、control epoch、lease、超时、重试、未知结果、checkpoint、replay、recovery 和 handoff；
4. EventStore 能承载五阶段跨区域、跨组织和跨时间的事件流，支持原子批次、outbox、投影重建、游标确认和幂等恢复；
5. 三本账和 `event_time / known_time / presented_time` 在第一阶段就使用正式合同，不能先用全知状态或 Actor 字段替代；
6. UE 表现/输入桥接、远场群体模拟、角色 Agent 和 UI 只消费获准投影并提交命令/证据；UE 还可承载显式注册的领域 Owner，以唯一写入口确认本域事实，不能据宿主名称把它排除在权威层之外。

## 3. 玩家角色和场景边界

玩家是该县最高统治者，军政一体，拥有县城范围内的最高行政和军事权限；权限仍受辖域、通信、现实位置、组织授权和命令有效期约束。

Demo 场景由以下连续区域组成：

- 县城：城门、城墙、街区、粮仓、水井、工坊、医舍、民居、县署和指挥所；
- 城外：两个村落、农田、林地、道路、桥梁或浅河；
- 敌方：攻方营地、器械工地、粮站；
- 战区：主要粮道、可发生伏击/追击/援军接战的野战区。

空间规模以能观察命令节点、运输路线、城门和关键目标为准，不以填满地图为目标。所有区域共享同一 `world_tick`、库存、设施、角色身份和占领事实。

## 4. 核心体验循环

### 4.1 玩家循环

```text
观察合法可知情报
  -> 暂停、检查资源/组织/命令可达性
  -> 发出求援和守城 Command
  -> 恢复世界，观察传令、运输、生产和敌军反应
  -> 追问、核查、追加命令或亲自介入
  -> 承担伤亡、短缺、失误和政治后果
  -> 直到援军抵达、敌军撤退、县城失守或玩家失败
```

### 4.2 必须体现的取舍

- 亲自出城会提高局部战斗影响，但会降低对城内命令和传令的可达性；
- 集中资源修城、生产箭矢或救治伤员，会减少其他用途的库存；
- 命令可以发出，但传令可能被阻挡、误解、延迟、截获或过期；
- 角色有服从义务，但可因失效条件、能力、恐惧、疲劳、家庭责任或自身判断拒绝、拖延或改写执行方式；
- 暂停只给玩家思考和下达命令的机会，不会刷新未知情报或完成异步事务。

## 5. 基础设施总架构（五阶段正式基线）

### 5.1 五类组件边界

文档中统一使用以下分类，避免把基础设施误称为玩法 Owner：

| 分类 | 组件 | 责任 | 是否拥有玩法事实 |
|---|---|---|---|
| Domain Owner | Presence、Dispatch、Organization、Government、Combat、Body/Resource、LifeState、Equipment、Status、Morale、Objective、Inventory、Ownership、Economy、Transport、Production、Population、Survival、Social、Politics、Territory、Information、Campaign | 对本领域事实做准入、结算和唯一写入 | 是，且只写自己的事实流 |
| Lifecycle Authority | Activation、Handoff、Continuity、Lease | 保证同一角色/群体在同一窗口只有一个推进者 | 否 |
| Infrastructure | Command Gateway、EventStore、Revision、Idempotency、Replay、Checkpoint | 治理命令、存储事件、回放和恢复 | 否 |
| Workflow | 守城流程、求援流程、进食/医疗流程、生产流程、运输流程 | 编排多个 Owner，等待各自 receipt；只维护流程进度，不拥有被编排领域事实 | 否 |
| Projection Consumer | UE 表现/UI、Character Memory、Population Reader | 消费受限投影、表现和认知结果 | 否 |
| UE Domain Runtime（宿主） | UE 原生获准的领域实现 | 按 Owner Manifest 承载既定领域，不增加第二份 Owner | 仅对应 Owner 的已授权写集，经 canonical 提交 |

`World Truth Layer` 不是万能数据库或万能 Owner，而是各领域 Owner 已提交的事件、EventStore 历史、revision、receipt、回放投影和当前确认状态的组合。

### 5.2 唯一因果链

所有玩家、智能体、角色和群体行为都走同一链路：

```text
Intent
  -> Command
  -> Command Gateway
  -> Evidence
  -> Domain Owner Resolver
  -> Event
  -> Receipt
  -> Projection
  -> Character Memory / UE Presentation
```

- `Intent`：主体主观上想做什么；
- `Command`：请求系统执行什么；
- `Evidence`：UE、场景、Agent 或群体模拟提供的观察/执行证据；
- `Event`：Owner 已确认世界发生的事实；
- `Receipt`：结算结果、revision、原因和下一步；
- `Projection`：给特定消费者的受限读取视图。

### 5.3 三本账

| 账本 | 内容 | 写入条件 | 消费者 |
|---|---|---|---|
| 世界真相账 | Owner 已承认的资源、产权、账户、位置、伤害、组织、运输、生产、人口、政治、辖域、目标和胜负事实 | 领域结算成功并提交 EventStore | 所有合法投影和 Owner |
| 角色记忆账 | 角色实际看到、听到、收到、推断、相信和记住的内容 | 感知、合法传播或自身推理成立 | Character Agent、角色对话和判断 |
| 世界表现账 | UE Actor、动画、音频、UI、镜头和局部物理状态 | 根据真相/行为投影生成，可延迟或降精度 | 玩家和表现层 |

三种时间必须同时记录：`event_time`、`known_time`、`presented_time`。表现出现得晚，不会改变事实发生时间；角色知道得晚，不会获得追溯全知。

## 6. 全量基础设施与 Owner 注册表

本节的 Owner 分类和职责是五阶段基础设施基线。第一阶段不是只实现其中一小部分再把其余部分留给以后，而是完成所有 Owner 的正式接口、注册、事件治理、回放、恢复和测试；第一阶段只在召陵县启用有限的实体、规则和数据规模。

### 6.1 Owner 注册表与五阶段覆盖

| Owner | 唯一事实范围 | 第一阶段启用 | 后续阶段扩展 | 基础设施阶段门 |
|---|---|---|---|---|
| Presence / Movement | 角色、队伍、运输批次、器械的位置、占用、到达、阻挡、绕行、拦截和脱离 | 召陵县、村落、粮道和攻方营地 | 跨县道路、关隘、商路和战线 | 位置提交点、路径 revision、冲突和回滚可回放 |
| Command / Dispatch | 命令授权、传达、理解、接受、拒绝、过期和执行状态 | 求援、守城、调拨、修缮、生产和护送 | 郡县军令、跨区域传令、政令传播 | 同一命令合同覆盖人类、Agent、群体和脚本 |
| Organization / Military | 岗位、层级、指挥权、授权范围、编制、预案、继任 | 县令、亲卫、一营三队、村落和工坊负责人 | 县际、郡级、州级军政组织与军团 | 继任、授权变更和组织 revision 可恢复 |
| Government / Policy | 政令、许可、封锁、征发、配给、治安、制度窗口和行政授权 | 县城封锁、路引、征发、坚壁清野、配给 | 郡县治理、税粮、治理政策和州级政策 | 政策冲突、例外、撤销和执行覆盖有事件流；不写产权或占领控制 |
| Combat / Damage | 攻击尝试、命中、格挡、伤害评估和战斗接触；不拥有生命、伤势、护甲耐久和持续效果 | 骑战、城墙攻防、器械和队伍战斗 | 跨战区、军团和多战线战斗 | UE-local Combat 可结算自身事实；Body/Equipment/Status 各自提交授权结果，同一命中链原子提交或记录开放义务 |
| Body / Resource | 生命、体力、伤势、部位功能与能力限制 | 战斗受伤、动作成本、医舍治疗、劳力状态 | 疫病、军团医疗、长期恢复和人口健康 | 近场与 Combat 本地协作；体力积分/动作准入、唯一写权、revision 和回放可验证 |
| Equipment | 装备关系、防护状态、耐久和破损；物品数量归 Inventory，法律产权归 Ownership | 近场防护、耐久消耗、破损和换装 | 军需换装、修复、缴获与跨阶段装备连续性 | 固定装备 revision，与 Combat/Body 授权片段协作；不得重复扣耐久或以 Actor 字段双写 |
| LifeState | 存活、倒地、濒死、死亡等生命周期转换 | 由身体依据确认倒地/死亡，限制普通治疗 | 复苏、连续性及适用世界规则 | 与 Body 分域；生命归零不自动死亡；近场及时转换，事件/回放/交接可验证 |
| Status / Effect | 流血、中毒、燃烧、眩晕、感染等效果实例及生命周期 | 伤口流血、持续伤害和治疗解除 | 持续伤害、效果组合和跨阶段疾病 | 效果有来源、强度、tick/退出条件；效果表现不直接修改身体数值 |
| Morale / Formation | 个人/队伍士气、阵型、纪律、溃退、重整和目标压力 | 守军、敌军队伍和军旗 | 军团、战线、政治合法性和长期军心 | 近场 UE 协作；输入来源、公式版本、阈值和恢复可审计；不替代 Agent 心智 |
| Inventory / Resource | 物资批次、数量、质量、容器、预留、转移、消耗、损失和存储关系；装备归 Equipment | 粮水盐、草料、木石铁、箭矢和攻守消耗品 | 税粮、贸易、战略仓储和跨区域资源网络 | 规格、质量、污染、容器迁移可回放；不判断法律产权 |
| Ownership / Property | 物资、设施、土地、牲畜、装备和账户权益的法律/契约产权、保管权、使用权、查封和转移 | 县仓、工坊、农具、房屋拆解和征发的产权/保管/使用权区分 | 占领后的接管、商贾资产、税户、继承和跨区域产权 | 产权转移必须有授权、对价/征发理由、争议、证据和可逆恢复；Inventory 只能引用产权结果 |
| Economy / Market | 账户、现金流、报价、订单、债务、税费、合同、市场成交和结算义务 | 现金/贸易物资、军需预算、商人报价和一条可观察的交易链 | 县际商路、税粮、债务、市场夺权和经济战 | 账务结算、合同履约、欠款和价格变化可回放；不得把库存数量直接当作现金流 |
| Transport / Logistics | 运输批次、承运人、路线阶段、护送、抵达、损失、拦截和恢复 | 县城粮道、援军、铁料和生产运输 | 商路、跨县粮网、战略运输和封锁 | 路线、占用、绕行、拦截和部分交付可恢复 |
| Production / Facility | 登记设施/设备完整度、机械开闭/闩锁、工作状态、工艺、工单、进度、产出认证和故障；班组/物资仅引用 | 铁匠坊、木厂、石料点、箭矢和修缮 | 多县生产链、工坊网络、军需和产业迁移 | 领域 Numeric/Condition/Hybrid 模型、配方版本和产出认证可回放；城防设施子域在 V2 前就绪 |
| Population / Work | 居民、家庭、工种、班次、劳力、迁移和调派结果 | 县城、村落、民夫、工匠和运输人员 | 县际迁移、兵源、税户和区域人口网络 | B0/B1 候选与个体 Agent 交接不丢连续性 |
| Survival | 饥渴疲劳等客观生存指标 | 守城补给、劳动能力和个体生存 | 疫病、军团医疗和长期恢复 | 只写自身指标；消耗物资由 Inventory、生命/伤势由 Body、效果实例由 Status 提交 |
| Medical Workflow（非领域 Owner） | 治疗请求、方案步骤、执行进度和待完成义务 | 医舍队列、治疗中断和回执汇总 | 疫病、军团医疗和长期护理 | 编排 Inventory、Body、Status；不取得其事实写权，流程状态可恢复 |
| Social / Influence | 公共关系、非政治承诺、声望、影响力和公开后果；派系公共政治承诺归 Politics | 豪强、村落、商人、将领和居民关系 | 多势力政治、联盟、背叛和招降 | 私有记忆与公共社会事实分离；不直接写公开合法性或辖域 |
| Politics / Legitimacy | 公开承认、派系承诺、合法性、政治授权、外交关系和政治后果 | 征发、封锁、赈济、违约或失守后的公开承认与派系反应 | 任命、表奏、盟誓、质子、联姻、赎俘、外交和治理稳定 | 公开政治事实与个人态度分离；每次承认、违约和关系转移有证据链 |
| Territory / Control | 地块、设施、道路、城池、关隘和战区的事实控制、占领、争夺、辖界和控制转移 | 县城、城门、粮道、村落和敌营的控制状态 | 跨县、郡、州占领，战线、边界和治理接管 | 控制转移必须由军事/治理/公开承认条件共同结算；Objective 只能读取，不得代写 |
| Information / Intelligence | 情报来源、报告、可信度、传播、误报、泄露和知情范围 | 军情、侦察、传令、粮道和敌营信息 | 细作网、跨区域情报、舆论和战略误导 | 知情边界、时间和来源可信度可重建 |
| Objective / Victory | 当前场景目标、胜负条件、结局和结算摘要 | 援军胜利、敌退胜利、失守/投降/死亡/逃跑失败 | 阶段性任务和可追溯结局 | 只能引用已确认事实；失守由 Territory、死亡由 LifeState 等事实 Owner 确认，Objective 不写身体/控制权/合法性 |
| Campaign / Strategic State | 战役、势力和长期战略目标、阶段推进、历史分岔和继承条件 | 用固定 fixture 验证跨阶段存档、目标进度和失败继承，不扩展第一阶段地图 | 战役目标、势力存续、历史分岔、长期继承和战略结算 | 只读取各领域 receipt；阶段推进、继承和分岔必须可回放 |

以上 Owner 的第一阶段实体数量可以很小，但它们不能使用临时字段、隐式全局变量或只支持成功路径的假接口。未被第一阶段内容启用的规则以版本化 Static Data 和空数据集存在，后续阶段通过配置和新领域数据启用。

### 6.2 Owner 正式交付物

“正式实现”不是创建一个接口或返回一个占位 receipt。每个 Owner 在第一阶段基础设施阶段门前必须有可执行的通用准入、规则结算、事件提交、拒绝、恢复和重放路径，并按领域适用性支持部分完成等结果；没有第一阶段实体的规则可以由版本化 Static Data 配置为空，但不能缺少规则引擎、状态机和测试入口。每个 Owner 必须交付：

- Owner Registry 条目：`owner_id`、事实范围、stream 命名、写入口和版本；按[建设总计划全量 UE 协作矩阵](08-基础设施与Owner建设总计划.md#112-全量-owner-的-ue-协作与节奏矩阵)登记 execution_host/mode、scope/epoch、commit_store、触发/模拟/提交节奏与延迟预算；
- 七部分领域契约：Static Data、Runtime State、Command、Rule/Resolver、Authority、Event/Result、Presentation/Query；
- 领域模型依赖合同：允许的模型类型、模型 Registry 范围、Applicability Binding 范围、输入 Owner、效果映射、评估频率、冲突策略、版本固定和迁移/replay 策略；
- 数值模型、条件模型和混合模型的定义、输入/输出 schema、单位、参数、阈值、状态机和适用绑定；模型必须限定在所属领域内，不能跨域写事实；
- 事件目录和状态转移表，明确成功、拒绝、过期、部分完成、取消、损失、补偿和恢复的适用条件；不适用的结果明确拒绝；
- revision/CAS、幂等键、receipt、outbox、checkpoint、replay 和投影重建接口；
- 与角色 Agent、B0/B1 群体模拟、UE Mirror 和 UI 的受限 Query/Projection；
- 跨 Owner 依赖、输入事件、授权 fragment、输出 receipt 和 recovery action；
- Model Evaluation Context：`evaluation_id`、`world_tick`、模型/绑定版本、输入 revision vector、公式/条件版本、评估顺序和下一次评估时间；
- 成功、失败、幂等、旧 revision、暂停、断线、恢复和回放测试。

### 6.3 Owner 阶段启用原则

第一阶段可以暂不制作完整全国税制、跨州运输或军团编制，但不能暂不建立相应 Owner 的基础契约。内容团队交付的是召陵县实体、规则参数和场景数据；基础设施团队交付的是所有 Owner 的正式可扩展接口和治理能力。

### 6.4 五阶段事实覆盖审查

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

## 7. P0 基础设施和 Owner

### 7.1 World Runtime Kernel（WRK）

WRK 负责唯一推进权，不负责计算战斗、库存或生产结果。

必须提供：

- 唯一 `world_tick` 和可暂停的世界时钟；
- 窗口、预算、固定读集、依赖和确定性 seed；
- B0/B1 批次推进和 C2/C3 Agent 激活交接；
- Owner 提交顺序、receipt、confirmed cursor 和 checkpoint；
- control epoch、lease、超时、重试、未知结果查询和恢复任务；
- 暂停/恢复屏障。

暂停规则：切换镜头、地图、工作层和关注对象不暂停；玩家主动暂停时，`world_tick`、Owner 提交、Agent、群体模拟、运输、生产、动画、物理和 handoff 全部冻结。恢复后重新验证 epoch、revision、lease 和证据时效。

### 7.2 Command Gateway

统一命令信封至少包含：

```text
command_id
command_type / command_version
source_kind / principal_ref / actor_ref
subject_ref / target_refs
control_mode
payload
expected_revisions / read_set_revisions
evidence_refs
priority
issued_at / expires_at
causation_id / correlation_id
```

来源统一为 `human`、`player_agent`、`character_agent`、`population_sim`、`scene_script`。所有来源接受相同权限、时效、revision、幂等和失败规则。

命令生命周期：

```text
received -> normalized -> admitted -> queued -> executing -> committed
```

失败必须显式记录：`rejected`、`requeued`、`partial`、`cancelled`、`expired`、`superseded`。

### 7.3 EventStore、Receipt 和 Replay

EventStore 是唯一事件脊柱，必须支持：

- 原子事件批次和 stream revision；
- 幂等键重复提交返回原 receipt，不产生第二次事实事件；
- outbox 和投影重试；
- 从事件流重建领域状态；
- checkpoint、replay、confirmed cursor 和恢复；
- 事件的 `causation_id`、`correlation_id`、来源、时间和 evidence 引用。

每个 receipt 至少包含：

```text
command_id
result_status
owner_kind
committed_events
before_revision / after_revision
reason_code
evidence_refs
event_time
known_time_by_recipient
next_action / recovery_action
```

### 7.4 Activation / Handoff

- B0/B1 只推进低精度状态、候选和升级信号；
- C2/C3 Agent 负责需要记忆、关系、判断和自主意图的角色；
- 同一角色同一时间窗口只能有一个推进者；
- 激活前固定来源 revision 和连续性游标；过期则 requeue；
- 退出高精度时保留已确认结果、未决意图、义务、失败原因和记忆游标；
- 玩家视野内或承担关键任务的角色必须维持可控制语义动画，而不是只播放预制循环。

## 8. P0 可玩闭环 Owner

本节只定义第一阶段必须被实际内容激活的 Owner 规则，不缩减第 6 节的五阶段 Owner 基础设施范围。未在本节展开的 Ownership、Economy、Politics、Territory 和 Campaign 仍须按第 6.2—6.4 节完成正式 Authority 和 fixture 验证。

### 8.1 Presence / Movement

唯一事实是角色、队伍、传令批次、运输批次和器械的实际位置、占用、到达、阻挡、绕行、拦截和脱离。

UE 的 `CharacterMovement`、NavMesh、EQS、AIController 和碰撞提供局部执行与证据；Presence Owner 负责承认位置事实。不能把 Actor 坐标每帧写入 EventStore。

语义提交点至少包括：`move_started`、`arrived`、`blocked`、`rerouted`、`intercepted`、`withdrawn`。

### 8.2 Command / Dispatch

唯一事实是命令的传令节点、抵达、理解、接受、拒绝、过期和执行跟踪。发令授权来自 Organization/Government/基础能力权威，Dispatch 校验并引用，不再造一份授权。

第一阶段至少支持：求援、守城、坚守城门、调动三队、调拨军需、请求修缮、请求生产、请求护送。

### 8.3 Organization / Military

最小组织为：县令/守城统治者、亲卫、营指挥头目、一营三队、传令兵、工坊负责人、军需负责人、村落负责人。必须支持岗位、授权、指挥范围、预案版本和继任。

### 8.4 Combat / Damage

UE 负责高频局部执行、输入、碰撞、命中候选和即时反馈；近场推荐共同承载 Combat、Body/Resource、Equipment、Status、LifeState 与战场 Morale 的获准实现，按统一 Command/Event/Receipt 合同通过本地调用协作。Combat 结算攻击/命中/格挡和伤害评估；Equipment 按固定 revision 结算防护与耐久，Body 应用剩余伤害并确认伤势和身体能力限制，Status 维护流血等效果，LifeState 根据授权依据确认倒地/濒死/死亡。需要同一语义提交点时由各 Owner 提供授权 fragment 并按依赖原子提交，Paralls 不得为同一事实再建第二写入者；正式提交位置见第 10.1 节。

语义提交点按事实 Owner 区分：Combat 提交攻击尝试、命中确认、格挡和 `damage_assessed`；Equipment 提交防护结算、耐久/破损；Body 提交 `damage_applied`、伤势、功能和体力变化；LifeState 提交生命周期转换；Status 提交效果创建、tick 生命周期、减轻和解除，并向 Body 请求周期数值变化；俘获由组织/战俘事实 Owner 确认。Objective 只读取这些已确认结果判胜负。动画完成不能替代任何提交事件。

### 8.5 Morale / Formation

读取伤亡、军旗、补给、指挥、疲劳、地形和敌压的已确认事件，只写士气、阵型、纪律、溃退和重整事实。角色 Agent 可以提出 rally、withdraw、protect_standard 等意图，但不能直接改士气。

近场个人/队伍士气采用显式登记的 UE-local 实现，按事件触发与周期压力评估及时影响阵型和行动约束，不逐次等待 Agent 或后端推理。个人感知与队伍报告按来源过滤，私有恐惧、解释和自主选择仍归角色智能体；不以同一士气数值强制所有角色作同一判断。

### 8.6 Objective / Victory

胜负由 Objective Owner 统一承认：

**胜利：**

- 援军抵达县城并完成阶段性交接；或
- 援军抵达前，敌军被击溃、撤退或解除围城。

**失败：**

- 县城失守后玩家投降；
- 玩家角色死亡；
- 玩家成功逃跑并离开守城责任范围。

出城反击和粮道行动只影响过程和风险，不是必须完成的条件。

## 9. 第一阶段内容切片：资源与社会闭环

为保证 Demo 不是空壳战斗，第一阶段只启用能支撑 30 天守城的内容切片；对应 Owner、事件、回放和恢复能力仍按第 6 节正式基线建设：

### 9.1 Inventory / Resource

首批物资：粮食、水、盐、草料、药材、木材、石料、铁料、箭矢、武器、檑木、金汁、火油、马匹、驮畜、工具和现金/贸易物资。

每种物资至少区分：数量、质量、容器、预留、产权、保管、事实控制、存储容量、污染/损坏和当前位置。

Inventory 还必须通过领域内的 Model Binding 区分食品变质、木材腐朽、铁料锈蚀和箭矢受潮等模型。只有资源标签、仓库/容器能力、作用域、生命周期和输入 revision 同时满足时，模型才可被 Inventory Owner 选中。模型结果不能由调用者直接提交为 `spoiled` 或 `quality_loss`，必须经过 Inventory Authority 的评估、revision 校验和事件提交。

来源约束：

- 县城周边可有木厂和石矿场；
- 本地没有盐原产地；
- 铁料来自外部，但县城有铁料储备；
- 农具等铁器可作为可回收铁料来源；
- 木材和石材可以来自城内房屋、家具和设施拆解，但会损害居住和防御设施。

### 9.2 Transport / Logistics

运输批次记录货物预留、承运人、路线阶段、当前位置、护送、阻挡、绕行、拦截、损失和入库 receipt。

UE 负责局部路径执行和实时表现，Transport Owner 负责批次事实。玩家站在路线、敌方攻击运输队或路线被封锁时，必须得到等待、绕行、拦截、损失或放弃之一的明确结果，不能瞬移到达。

### 9.3 Production / Facility

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

### 9.4 Survival / Medical

第一阶段内容切片只启用粮、水、盐、疲劳、伤势、医舍队列和劳动能力对守城的可观察影响。缺粮、缺水或缺盐不能直接扣一个全局混乱值，必须经过消费、生存指标、身体状态、劳力、组织和士气逐层产生后果。治疗动画和交互可由 UE 传统路径执行；库存消耗、生命/伤势变化、状态效果变化必须分别经 Inventory、Body、Status Owner 提交。医疗流程负责串接这些回执；UE-local authoritative 只能通过 Owner Manifest 显式启用，不能由 Pawn/Buff/动画自行加血。

## 10. UE 高频桥接和表现对齐

23 个 Owner 的近场 UE 要求、事件/窗口分类与远场推进，以[建设总计划第 11.2 节](08-基础设施与Owner建设总计划.md#112-全量-owner-的-ue-协作与节奏矩阵)为统一基线。实时链也包含弹药/药物库存与城门设施等依赖子域；D/V2 前必须就绪，不能将它们隐藏在每次攻击都要等待的后端调用中。其余领域完整包仍按建设批次验收。

ESM 不是本节桥接或所有动作的必经入口。复用范围限于经审核的结构化交互、许可与证据合同；Godot 执行器由 UE 原生实现替换，旧身体/对象写入口按领域映射迁移并失效。详见[ESM 复用与迁移检查](01-Paralls现有Owner与接入分析.md#9-esm-复用边界与迁移检查)。

### 10.1 帧循环和语义提交点

```text
UE 帧循环：
输入 / 移动 / 动画 / 物理 / 局部碰撞

语义提交点：
攻击尝试 / 命中候选 / 到达 / 被阻挡 /
运输装载 / 运输拦截 / 命令送达 / 目标状态变化

Owner 结算：
验证证据、权限、revision、成本
  -> Event + Receipt
  -> Projection / Reconciliation
```

约束：

- 不把每帧移动、骨骼和动画状态写入 EventStore；
- 本地预测只能标记为 predicted，不能冒充 committed；
- Owner 拒绝时必须回滚或修正 UE 表现；
- Bridge 断开时仅在有效本地权威范围内继续确认结果；仅后端提交配置不得离线提升为权威，恢复时按 revision/cursor 对账与补同步；
- 表现账可以缺席、延迟或降精度，不能反写世界真相。

本地高频路径必须同时接入生命、体力、伤势、持续效果、生命周期与战场士气，不能只让 Combat 在 UE 中运行，再为每次扣血/扣体力等待一次后端或 Agent 往返。Owner 职责分域不要求独立进程；Gateway/WRK 可以提供本地准入与调度上下文。受击、体力耗尽和已确认失能等强制约束即时应用，角色自主意图仍由当前意图权持有者决定。

更新节奏按模型分别声明：生命按命中/治疗/效果事件；体力按动作成本与模拟时间积分；士气按伤亡/军旗/指挥等事件加周期压力窗口；长期疲劳/饥渴按生存窗口。画面帧、模型评估、事件提交、投影同步和 Agent 决策不是同一节奏。Static Data/模型/适用绑定固定参数、条件、版本与合法输入，Manifest 登记各链路延迟预算和提交位置，PIE 实测后验收。

近场目标为获准的本地可靠 canonical 提交路径：各 Owner 在唯一逻辑事件账中提交并取得 receipt 后即时确认，后端异步接收已提交事件、更新投影和 Agent 输入，不重新计算。必须实现 revision/CAS、幂等、可靠事件/outbox、崩溃恢复、checkpoint/replay 和 epoch fencing；它不等于缓存一份 UE 数值后无条件上传。若现阶段 canonical store 只在后端，明确作为过渡配置，本地反馈在回执前仍为 pending/predicted，不能据此验收“完整闭环无需后端往返”。不同提交端的跨域结果以开放义务与恢复协调，不假称全局原子。

完整更新节奏、连续体力切窗、角色即时反应、士气可知性、提交/同步和断线合同以[数值结算专题第 4.4—4.7 节](Owner体系/03-数值规则、状态效果与跨Owner结算.md#44-近场部署职责分域实时协作)为准，专项验收见该文第 9 节。

### 10.2 Agent 激活和动画激活矩阵

| 情况 | Agent 推进 | UE Actor | 动画/表现 |
|---|---|---|---|
| 远处普通居民 | B0/B1 | 不生成或低频代理 | 只显示群体投影 |
| 远处运输队 | B1/运输批次代理 | 简化载荷和路线代理 | 低频位置更新 |
| 接近玩家且承担重要任务 | C2/C3 | 激活实体 | 根据命令、状态和环境实时选择动作 |
| 玩家视野内关键角色 | 当前激活的 Agent 持有自主意图权；本地执行器持续执行获准语义 | 持续激活 | 转向、阻挡、交互和反馈实时运行；执行器不自行替代 Agent 选新策略 |
| 战斗中的关键单位 | Agent/群体意图权与 Combat 等领域写权分开登记 | 持续激活 | 本地执行当前计划与强制约束；动作与语义提交点对齐 |
| 玩家主动暂停 | 世界推进全部冻结 | 保留当前状态 | 动画、物理、世界音频和世界时间冻结；UI 可思考/编辑命令草稿，不传达或刷新未知情报 |
| 离开关注范围 | 降级或交接 | 降级或卸载 | 根据投影恢复，不重置身份 |

玩家视野内被激活的角色必须能够依据自己的状态、命令、环境和失败原因控制动画；不能只有一个与 Agent 无关的播放列表。

## 11. Demo 的第一阶段内容配置

### 11.1 角色和组织

- 玩家统治者 1 名；
- 亲卫队 1 队；
- 营指挥头目 1 名；
- 守军三队；
- 传令兵至少 3 名；
- 军需负责人、工坊负责人、医舍负责人各 1 名；
- 关键村民/工匠/商人若干；
- 敌方主战队、军旗队、器械队、指挥头目和运输队。

### 11.2 第一阶段命令

- `request_aid`：向外部援军发出求援；
- `defend_city`：进入县城守备方案；
- `hold_gate`：指定队伍守城门；
- `patrol_wall`：巡查并报告城墙压力；
- `dispatch_supply`：调拨军需；
- `repair_section`：修缮城墙/城门；
- `produce_ammunition`：生产箭矢或简易武器；
- `escort_shipment`：护送运输批次；
- `sortie`：可选出城行动；
- `retreat` / `surrender` / `escape`：失败或主动收束路径。

### 11.3 敌方和时间

默认世界时间为约 30 天的围城窗口；攻方每日推进营地、器械、粮站、侦察和攻城压力。援军抵达时间是约 30 天，不保证玩家能无损等待，玩家必须管理库存、伤病、军心和城墙状态。

时间倍率和真实分钟数在灰盒试玩中校准，但必须保持同一 `world_tick` 和可回放事件顺序，不能用“跳过天数”绕过 Owner 结算。

## 12. 执行路线与阶段门

本路线采用**两条并行轨道、多个纵向切片、持续回归**。基础设施按五阶段正式标准建设，但不要求先把所有基础设施阶段串行做完才进入游戏；玩法每完成一个纵向切片，就必须在 UE 中可操作、可观察、可暂停、可恢复，并能从事件流和 receipt 解释结果。

基础设施阶段门和内容阶段门分开管理。基础设施阶段门未通过时，不得用临时 Owner、Actor 字段、关卡脚本或 UI 旁路替代正式能力；内容阶段门未通过时，不扩张召陵县的资产和玩法数量。

### 12.1 两条并行轨道

| 轨道 | 目标 | 工作方式 | 硬约束 |
|---|---|---|---|
| 基础设施轨道 | 完成五阶段可复用的 WRK、Command、EventStore、Owner、三本账、Activation/Handoff、Projection、Replay、Recovery 和 UE/Paralls Bridge | 先冻结公共合同，再按切片需要实现 Owner 规则，同时用未启用领域 fixture 补齐五阶段覆盖 | 不得用临时 Owner、Actor 字段、关卡脚本或 UI 旁路写世界事实 |
| 可玩内容轨道 | 逐步形成召陵县守城 Demo | 每个纵向切片都从 Command 进入，经过真实 Owner 结算，进入 UE 表现和回放验收 | 每个切片完成后都必须有可运行 PIE/试玩入口，不等最终整合 |

两条轨道共享同一个 `world_tick`、EventStore、Owner Registry、Command Envelope 和验收证据。可玩内容可以限制实体数量和地图范围，但不能替换事实链。

### 12.2 每个纵向切片的固定工作循环

```text
切片目标与失败条件
  -> Owner/Command/Event/Projection 合同
  -> Paralls 规则结算与测试
  -> UE 场景、交互、动画和反馈接入
  -> PIE 可玩验证
  -> 暂停、拒绝、阻挡、断线或失败注入
  -> receipt、三本账、checkpoint、replay 和截图证据
  -> 通过后锁定合同，进入下一切片
```

一个切片只有在“玩家能做出选择、世界产生后果、玩家能看到后果、系统能解释后果”四项同时成立时才算完成。只完成接口、假数据或单元测试，不算纵向切片完成。

### 12.3 纵向切片路线

#### 切片 V0：可运行世界壳

**目标：** 尽早让团队进入 UE，验证世界时钟、暂停、恢复、玩家移动、三本账和基础桥接。

**并行工作：** Owner Registry、Command Envelope、EventStore 原子批次、revision、幂等、receipt、`world_tick`、暂停屏障、checkpoint；召陵县灰盒入口、玩家角色、三视角、基础移动和暂停 UI；表现账只消费投影。

**UE 可玩结果：** 玩家可以进入县城、移动、切换视角、暂停和恢复；恢复后位置、时间和表现不重置。

**通过标准：** 这是可运行壳，不是玩法 Demo；不得有 Actor 字段直接成为世界事实。

#### 切片 V1：军情—命令—传令—队伍响应

**目标：** 形成第一个“玩家能下令并看到组织响应”的完整闭环。

**并行工作：** Command/Dispatch、Organization、Presence、Activation/Handoff 正式规则；县令、亲卫、营指挥头目、一营三队和传令兵；县署/指挥所、传令路线、命令状态 UI 和语义动画；关键角色 C3，普通队伍和居民 B0/B1。

**UE 可玩结果：** 玩家发出 `defend_city`、`hold_gate`、`patrol_wall`，能看到传令兵移动、命令送达、理解/接受/拒绝和三队不同响应。

**通过标准：** 玩家能分辨“已下令、已传达、已接受、执行中、已完成/失败”；玩家离开现场后队伍仍按同一世界时钟自治。

#### 切片 V2：敌情—城防压力—战斗反馈

**目标：** 把 V1 命令链接入实际威胁，形成第一次可操作的守城战斗。

**并行工作：** Combat、Body/Resource、Equipment、Status、LifeState、Morale、Formation、Territory 正式结算和授权 fragment；Inventory 的弹药/药品即时子流与 Production / Facility 的城门机械、城防完整度子域同步交付；近场 Owner 本地调用与可靠提交/outbox；敌方主战队、军旗队、器械队、攻方营地、南门和一段城墙；骑乘/步战、命中反馈、城门/城墙状态、阵型和士气投影。

**UE 可玩结果：** 玩家能亲自参与城门防守，命令三队执行不同任务，并看到命中、伤势、军旗、阵型、士气和城防压力变化。

**通过标准：** 单骑冲锋能影响局部接触但不能稳定替代命令协同；关键伤害、失能、士气和控制变化都可追溯到 Owner receipt。

高频协作还须证明：攻击与冲刺并发不超支，体力耗尽及时限制动作，生命归零由 LifeState 判断后果，士气变化及时反馈而不替代 Agent 判断；本地已确认事件在后端断线/恢复后不重复结算。登记并测量命中到身体反馈、体力耗尽到中断、士气事件到阵型响应延迟；在可靠本地提交未通过崩溃恢复和回放验收前，不能将过渡预测模式当作 V2 的正式权威链完成。

#### 切片 V3：求援—三十日窗口—胜负闭环

**目标：** 首次形成“从收到军情到胜利/失败”的可完成 Demo 主线。

**并行工作：** Government、Information、Objective、Campaign 正式结算；外部援军、援军路线、敌军撤退条件、县城失守条件和五种结局；军情报告、求援命令、三十日时间线、战报和胜负摘要。

**UE 可玩结果：** 玩家收到合法军情后可以暂停、求援、布置守城，持续运行并完成至少两条胜利路径或触发三条失败路径。

**通过标准：** 这是第一个“可玩 Demo Alpha”；胜负只由 Objective 读取已确认事实，不能由剧本脚本直接宣布。

#### 切片 V4：资源—运输—生产—医疗后果

**目标：** 让守城从战斗场景变成持续运转的县城战争社会。

**并行工作：** Inventory、Ownership、Economy、Transport、Production、Population、Survival 正式规则和跨域 Workflow；粮水盐草料、木石铁、箭矢、铁匠坊、分散铺子、粮道、医舍、村落和敌方粮站；仓储、装卸、阻挡/绕行/拦截、工坊队列、医舍队列和短缺反馈。

**UE 可玩结果：** 玩家可以调拨资源、护送运输、修城、生产箭矢、救治伤员；路线被玩家或敌军干扰时出现等待、绕行、损失或失败，而不是瞬移。

**通过标准：** 资源经过产权、账户、库存、运输、生产、消费和身体状态逐层产生后果；所有跨域步骤都有 receipt 和 recovery action。

#### 切片 V5：完整召陵县守城 Demo

**目标：** 将 V0—V4 合并成一段可重复、可暂停、可回放、可失败注入的复杂 Demo。

**并行工作：** 全量 Owner Authority 回归、跨阶段 fixture、Bridge 断线恢复、投影重建、性能和观测；完整县城、村落、粮道、攻方营地、关键角色、资源和攻城目标；近远场激活、Agent—动画对齐、地图/工作层切换、战报和战后因果摘要。

**UE 可玩结果：** 玩家从军情开始，能够求援、守城、战斗、运输、生产、救治，并以援军到达、敌军撤退或失败结局收束。

**通过标准：** 形成可交付 Demo Candidate；V0—V4 仍能单独启动和回归，不允许整合版掩盖单切片回归失败。

### 12.4 基础设施能力门与纵向切片的关系

原先的“阶段 0—12”保留为能力门，但不再表示串行开发顺序：

| 能力门 | 首次必须可用 | 后续责任 |
|---|---|---|
| 阶段 0：基线和证据规范 | V0 开始前 | 每个切片更新实现、缺口、日志和性能证据 |
| 阶段 1：公共合同冻结 | V0/V1 接入前 | 新 Owner 只能扩展版本，不得另建命令/事件协议 |
| 阶段 2：EventStore、WRK、恢复 | V0 可玩前 | 每个切片都必须支持暂停、checkpoint、replay 和 recovery |
| 阶段 3：Command Gateway、Projection | V1 可玩前 | 人类、Agent、群体和 UE 继续走同一入口 |
| 阶段 4：全量 Owner Authority | V4 完成前 | V2/V3 先实现所需 Owner，V4 补齐全量跨阶段 fixture |
| 阶段 5：Presence 和高频桥接 | V0/V1 | 随战斗、运输和动画切片扩展语义提交点 |
| 阶段 6—8：组织、战斗、目标 | V1—V3 | 每个切片保留独立 PIE 剧本 |
| 阶段 9：资源、运输、生产、生存 | V4 | 形成资源后果链并回归 V1—V3 |
| 阶段 10—12：表现、完整剧本、试玩打包 | V5 | 只做整合和质量提升，不改变已冻结事实边界 |

### 12.5 每轮切片的完成证据

每个 V 切片必须单独保存：

- 一个可启动的 PIE/试玩入口和固定测试剧本；
- Command、Owner、revision、epoch、receipt 和事件流导出；
- 至少一条成功路径、一条拒绝/失败路径和一次暂停恢复记录；
- 三本账的关键投影、UE 截图、角色/群体激活记录和动画对齐证据；
- checkpoint/replay 对比结果；
- 当前硬件上的帧率、内存、显存、Actor 数量和加载时间。

任何切片没有这些证据，只能标记为“开发中”，不能标记为“完成”或作为下一切片的稳定基线。

### 12.6 基础设施能力门原表

以下阶段是基础设施能力门和回归清单，不是必须串行完成后才开始 V0—V5 的开发顺序。

### 阶段 0：基线盘点和证据规范

**交付：** 当前 UE Actor/关卡/PIE 状态表；Paralls 当前 Owner 复用表；五阶段 Owner Registry 初版；事件、命令、投影、日志命名规范；资源和性能基线；每个 Owner 的事实范围、写入口和依赖图。

**验收：** 不修改受保护关卡；能说明当前实现、规划能力和缺口；所有 Owner 均有明确的当前/规划状态，不把 planned 当作 current；有一次定向 PIE 截图、日志和 Actor 数量记录。

### 阶段 1：五阶段 Owner 与公共合同冻结

**交付：** 全部 Owner 的正式注册项；七部分领域契约；领域模型 Registry、Numeric/Condition/Hybrid Model 类型目录、Applicability Binding 和 Evaluation Context 合同；Command/Event/Receipt/Projection/Query 类型目录；stream 命名；revision/CAS、幂等键、因果/相关 ID、时间字段、evidence 引用和错误码；跨 Owner Workflow 与授权 fragment 合同；Static Data 版本策略。

近场注册项按建设总计划第 11.2 节逐域登记，并交付 ESM 合同/执行器/旧写入口迁移表；环境事实来源未定不得启用相关模型。近场注册项同时固定 Owner 的执行位置/模式、权威范围/epoch、提交位置、模型更新/触发节奏、积分与切窗策略、Agent 中断权限、延迟预算及断线/恢复合同；不能只登记 Owner 名称后把这些决定留给 Pawn 各自实现。

**验收：** 23 个 Owner 的 Registry、write set、公共合同、宿主/节奏矩阵与 ESM 迁移映射齐全且无重叠写权；schema 能表达成功、拒绝、过期、部分完成、取消、损失和恢复结果，Static Data、模型输入单位/版本、Binding、revision 和 Evaluation Context 可固定，并通过类型/合同 fixture 检查。按领域定义适用的模型、非法绑定、幂等、旧 revision/epoch/lease 与恢复用例，不强迫每个领域都有同一种模型。此门冻结合同；模型实际运行、重复命令仅一批事实、版本冲突拒绝等运行保证由阶段 2—4 随对应纵向切片逐项提供执行证据，不能在合同门提前宣称全量实现完成。

### 阶段 2：EventStore、WRK 和恢复内核

**交付：** `world_tick`、暂停屏障、时间窗口、固定读集、预算、依赖、control epoch、lease、confirmed cursor、checkpoint、replay、outbox、投影重建、恢复任务、超时、重试、未知结果查询和幂等实现。

随 V2 建设获准的本地可靠提交与后端副本同步路径，并验证该事实作用域只有一个 canonical 提交权威；本地事件持久化、receipt、outbox 与崩溃恢复未通过验收前，只能按已声明的后端提交/预测配置运行。

**验收：** 暂停屏障生效后不提交新世界事实，不应用异步结果或推进语义 handoff；外部回调可以到达隔离队列，但不得改变世界、写权或角色知识，恢复后须重新校验；恢复后从同一 tick 继续；事件流可重放所有已登记 Owner 的状态；checkpoint 后继续运行与完整 replay 的结果一致；断线和重复投递不会产生第二次事实。

### 阶段 3：Command Gateway 和受限投影

**交付：** 统一 Command Envelope、来源校验、权限、时效、read set、evidence、状态机、receipt 查询；UE/UI/Agent 三种投影。

**验收：** 人类玩家、角色 Agent 和群体模拟提交相同领域命令时走同一规则；重复幂等键只产生一个事实事件；拒绝、过期、取消和部分完成都有原因。

### 阶段 4：全量 Owner Authority 与跨域 Workflow

**交付：** Presence、Dispatch、Organization、Government、Combat、Body/Resource、LifeState、Equipment、Status、Morale、Objective、Inventory、Ownership、Economy、Transport、Production、Population、Survival、Social、Politics、Territory、Information、Campaign 的正式 Authority；每个 Owner 的唯一写入口、模型依赖合同、可执行规则解析器、事件流、receipt、投影、回放、恢复和测试；跨 Owner Workflow 只通过 Command、授权 fragment 和 receipt 编排。

**验收：** 每个 Owner 都能独立重建自己的 Runtime State，并至少执行一次成功、拒绝和恢复结算；部分完成、损失与补偿按领域适用性验证，不适用时明确拒绝，不制造假流程；任何跨域流程都能列出已提交 Owner、拒绝 Owner、当前 revision 和 recovery action；不得出现 UniversalOwner、Gateway 写领域事实或两个 Owner 写同一事实；第一阶段启用的召陵县数据能走完整链路，未启用的五阶段事实用正式 fixture 完成覆盖验证。

### 阶段 5：Presence、UE Mirror 和高频桥接

**交付：** UE 局部移动/碰撞/动画执行器；Presence 语义提交点；truth revision、预测标记、Owner receipt、回滚/修正。

**验收：** 60Hz 局部移动保持响应；到达、阻挡和绕行可提交；玩家挡住运输路线时不会瞬移；预测被拒绝时可恢复到权威状态。

### 阶段 6：组织、军令和 Agent/Handoff

**交付：** 县令—亲卫—营—三队组织；传令兵路径；授权、继任、预案、激活锁；关键角色 C3 和普通角色 B0/B1 接入。

**验收：** 玩家下达求援和守城命令后能看到传令节点、理解/接受/拒绝和执行结果；玩家离开范围后队伍继续自治；指挥头目失能后可按继任链继续行动。

### 阶段 7：Combat、Morale、Formation

**交付：** 近场骑战、队伍级战斗、命中/伤害/失能、军旗、阵型、士气、溃退/重整。

**验收：** 攻击动画即时响应；Combat、Equipment、Body、Status 分别返回命中/伤害评估、防护耐久、身体变化和效果回执；至少一次阵型变化和士气变化可回溯；单骑冲锋不能稳定替代组织协同。

### 阶段 8：Objective 和胜负闭环

**交付：** 30 天援军窗口、敌方撤退条件、县城失守条件、投降/死亡/逃跑失败、胜负摘要和阶段存档。

**验收：** 至少验证援军胜利、敌军提前撤退胜利、投降失败、死亡失败、逃跑失败五条结局；Objective Owner 能指出触发事件和 receipt。

### 阶段 9：资源、运输、生产和生存

**交付：** 30 天内容切片库存基线；粮水盐草料；箭矢/木料/石料/铁料；铁匠坊和分散铺子；运输批次；一条主要粮道；工坊生产；医舍和伤病。这里的“30 天”限制初始数据规模和试玩窗口，不限制 Inventory、Ownership、Economy、Transport、Production、Population 和 Survival Owner 的通用能力。

**验收：** 资源能经过生产/储存/运输/入库/配给/消费产生连续后果；运输阻挡、敌袭和损失可观察；拆解房屋或农具获得材料会损伤原设施或工具；生产停工有可解释原因。

### 阶段 10：Agent—动画—表现一致性

**交付：** 激活矩阵、语义动画状态、近远场投影切换、暂停冻结、恢复重建、玩家视野内自主角色行为。

**验收：** 关键角色在玩家视野内能依据命令、状态和环境改变动作；离开视野降级后再回来不重置身份、位置和记忆；暂停时动画和 Agent 同时冻结。

### 阶段 11：完整剧本、失败注入和回放

**交付：** 开局军情、求援、守城、围城、资源短缺、运输拦截、角色拒绝、命令过期、Bridge 断线、恢复和五种结局的可重复剧本；增加产权征发、军需欠款、粮道控制争议、赈济后的派系承认和跨阶段 checkpoint fixture。

**验收：** 每个剧本都有事件流、receipt、三本账结果、UE/PIE 截图和日志；从 checkpoint 重放后关键结果一致；至少一个第一阶段存档可加载到第二阶段 fixture，且产权、账户、控制权、政治承认、人口/设施状态和战略目标均由正式 Owner 投影恢复，不允许章节脚本重写。

### 阶段 12：试玩、性能和打包

**交付：** 灰盒试玩包、性能预算、资源索引、测试记录、已知问题和回退版本。

**验收：** 在目标硬件上完成连续试玩；无阻断级命令/暂停/回放错误；报告帧率、内存、显存、加载时间、Actor 数量和 PIE 状态；未验证资源不得覆盖正式资产。

## 13. 验收矩阵

| 类别 | 必须验证 | 通过标准 | 证据 |
|---|---|---|---|
| 纵向切片 | V0—V5 | 每个切片都能独立启动、操作、暂停、恢复和回放；后续切片不能掩盖前一切片回归失败 | PIE/试玩入口、固定剧本、截图、receipt、replay diff |
| 核心目标 | 求援、守城、援军/敌退胜利 | 至少两条胜利路径可完成 | 事件流、胜负 receipt、PIE 截图 |
| 失败结局 | 失守后投降、死亡、逃跑 | 三条失败路径均可触发且不可误报为胜利 | Objective 日志、战后摘要 |
| 时间 | 30 天窗口 | world_tick 单调、暂停冻结、恢复不跳账 | WRK 日志、checkpoint |
| 命令 | 传令、失效、拒绝、过期 | 玩家看到节点、状态和原因 | Command receipt、UI 截图 |
| 三本账 | 真相、记忆、表现分离 | 角色不知道未暴露事实，表现不反写真相 | projection/记忆日志 |
| Owner | 全量 Owner 契约 | 所有已登记 Owner 均有可执行规则、唯一写权、事件流、receipt、投影、回放和恢复接口；第一阶段启用实体可运行，未启用五阶段事实由正式 fixture 覆盖 | Owner registry、契约目录、事件流、replay diff、fixture 报告 |
| 领域模型 | Numeric、Condition、Hybrid、Binding、Evaluation Context | 同一领域至少两种模型可运行；不匹配绑定、过期输入和跨域模型被拒绝；模型结果只能经 Owner 提交 | Model registry、binding trace、evaluation context、事件和 replay diff |
| 跨阶段事实 | 产权、经济、辖域/占领、政治、战略目标 | 第一阶段至少完成一次跨域结算和一次 checkpoint/replay；不得由 UI、章节脚本或 Objective 旁路写入 | Owner receipt、跨阶段 fixture、恢复 diff |
| UE 高频 | 预测、命中、移动、回滚 | 局部响应和最终权威一致 | PIE 录像/日志 |
| Agent | 激活、交接、自主判断 | 关键角色能解释、拒绝或改写执行方式 | handoff、Agent trace |
| 群体 | B0/B1 与 C2/C3 | 升级和降级不丢身份、义务和记忆游标 | continuity trace |
| 资源 | 储存、运输、生产、消费 | 阻挡、损失、停工、短缺有连续后果 | Inventory/Transport/Production receipt |
| 回放 | replay/checkpoint/recovery | 能重建阶段状态和因果链 | replay diff、checkpoint |
| 表现 | 动画和事实对齐 | 动画即时但不冒充提交；暂停同时冻结 | UE Mirror 日志、PIE 截图 |

## 14. 测试用例清单

### 14.1 基础设施测试

- 同一 `command_id` 重复提交返回同一 receipt；
- 旧 `expected_revision` 被拒绝且不产生事实事件；
- 暂停期间提交命令只进入待发送队列，不推进世界；
- 恢复后旧 epoch 的异步结果被拒绝；
- EventStore 删除投影后可由事件流重建；
- checkpoint 之后继续运行与完整 replay 的关键状态一致。
- Ownership、Economy、Territory、Politics 和 Campaign fixture 能通过正式 Command 结算，并在 checkpoint/replay 后保持产权、账户、控制权、政治承认和战略进度一致；
- 同一资产同时发生征发、运输、交易或占领冲突时，只有对应 Owner 能提交事实，其他 Owner 只能收到 receipt 或拒绝原因。
- 同一 Inventory Owner 使用食品变质和木材腐朽两个不同模型时，模型绑定、输入 revision、状态转移和库存结果均可区分并回放；食品模型不得作用于木材，木材模型不得作用于 Body 或 Politics。

### 14.2 高频桥接测试

- 60Hz 本地移动不要求每帧写事件；
- 攻击动画及时出现，伤害等结果须经 receipt 确认；本地权威提交不等待后端同步，后端提交配置则保持 pending 至确认；
- 命中、生命/体力、持续效果、LifeState 和战场士气在 UE 内按各自模型协作，测得的反应延迟满足 Manifest 预算；
- 攻击/冲刺并发成本、体力窗口切分、效果 tick 与暂停/交接均不重复推进；生命归零不绕过 LifeState；
- 个人士气只消费合法感知/报告输入，强制身体反应不等待 Agent 推理，自主策略不被本地反应控制器接管；
- 本地权威提交后、后端同步前崩溃，恢复事件/outbox 后保持 receipt、数值和 replay 一致；仅后端提交配置断线时不产生本地最终事实；
- 过期命中证据被拒绝；
- Bridge 断开后在仍有效的意图/执行许可与本地事实权威范围内继续当前计划或已授权预案，恢复后不重复结算；没有本地授权的范围保持 pending/安全中断，不自动升格权威或新建自主意图；
- Owner 拒绝预测位置或命中时 UE 回滚/修正；
- 玩家站在运输路线时出现等待、绕行或阻塞结果。

### 14.3 玩法闭环测试

- 开局军情只能通过合法报告进入玩家知识；
- 玩家立即求援后，传令和援军状态可追踪；
- 守城命令可因权限、通信、目标失效或过期拒绝；
- 角色可服从、延迟、拒绝或改写失效命令，但不能越过 Owner；
- 运输遭袭、粮道中断、生产停工会影响配给、伤病、士气或敌方撤退；
- 征发、采购、拆解和占领不会越过 Ownership/Economy/Territory；公开后果由 Politics receipt 进入 Social、Organization 和 Objective 投影；
- 援军抵达前击溃敌军和等待援军两条胜利路径均成立；
- 投降、死亡和逃跑是失败，不会被 UI 误显示为阶段胜利。

## 15. 运行证据和开发纪律

每一阶段都必须保存：

- 事件流和 receipt 导出；
- Owner、Command、revision、epoch 和 handoff 日志；
- 资源、Actor 数量、PIE 状态、帧率、内存和显存记录；
- 定向 UE 编辑器截图和 PIE 截图；
- replay/checkpoint 重建结果；
- 资源来源、许可证、面数/纹理预算和导入验证记录。

UE 操作遵守项目 `AGENTS.md`：不清空受保护关卡，不批量导入未经验证资源，只运行一个 UE 实例，内存不足时停止大型操作；任何“完成”结论都必须有日志、资产/Actor 数量、PIE 状态和截图证据。

## 16. 风险与止损规则

| 风险 | 早期信号 | 止损动作 |
|---|---|---|
| 基础设施被玩法细节拖垮 | 事件/命令合同频繁改名 | 冻结 Envelope、Event、Receipt 正式必需字段与版本，减少当轮内容类型，不缩减基础合同 |
| UE 与 Paralls 双写 | 同一结果出现两条不同 receipt | 指定单一 Owner，删除第二写入口，补重放测试 |
| 高频桥接延迟破坏手感 | 扣血/体力或士气响应必须等待后端/Agent | 近场 Owner 本地协作并建设可靠权威提交；过渡预测明确 pending，不能冒充最终完成 |
| 30 天内容过大 | 每天都需要大量独特脚本 | 用统一资源、运输、士气和敌军规则产生变化 |
| 角色 Agent 过早扩张 | 普通居民也要求 C3 | 只激活关键角色，其余 B0/B1 |
| 表现与事实不同步 | 动画完成但 receipt 拒绝 | 增加 reconciliation、回滚和 truth revision 标记 |
| 试玩无法理解因果 | 玩家只看到胜负，不知原因 | 增加命令节点、来源、时效、receipt 和战后因果摘要 |
| 资源系统变成菜单 | 玩家不关心仓储、运输和生产 | 将运输阻挡、库存短缺和工坊停工绑定可见战场后果 |

## 17. Demo 完成定义

只有同时满足以下条件，才能称为“第一阶段县城守城 Demo 完成”：

1. 玩家从敌情开始，能主动求援并组织守城；
2. 世界在同一时间线上持续运行，明确暂停时完全冻结；
3. 至少两条胜利路径和三条失败路径可实际完成；
4. 命令、传令、战斗、资源、运输、生产和目标都有唯一事实 Owner；
5. 角色 Agent、群体模拟和 UE 表现都通过统一 Command/Event/Receipt 链连接；
6. 近场 UE 保持即时手感，远场和后台事实可回放、恢复和重建；
7. 玩家能观察并解释至少一条“情报—命令—执行—资源/战斗后果—胜负”的因果链；
8. 所有结果都有日志、receipt、checkpoint 和定向截图证据；
9. 没有第二套世界真相，也没有把旧骑将冲阵切片误称为完整县城守城 Demo。

完成本方案后，下一份实现计划应按第 12 节的阶段门拆成代码任务；在全量基础设施阶段门通过前，不扩张兵种、地图、剧情或美术资产规模。内容规模可以保持第一阶段切片，但不能以切片名义跳过任何 Owner 的正式合同、测试和恢复能力。

## 18. 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| v0.7 | 2026-10-30 | 对齐 23 Owner 全量 UE 节奏矩阵、ESM 可选合同与 Godot 执行替换；澄清 UE 宿主写权、城门/库存/政治事实边界，修正模型类型、激活与暂停表述及断线验收。 |
| v0.6 | 2026-10-30 | 明确生命、体力、LifeState 与战场士气的 UE 高频协作、模型更新节奏、Agent 即时反应边界、本地权威提交与后端同步；修正死亡写权，补充 V2 与高频恢复验收。 |
| v0.5 | 2026-10-30 | 纳入领域模型架构：新增 Numeric/Condition/Hybrid Model、Static Data、Applicability Binding、Evaluation Context 和模型验收；明确模型只能在所属领域内泛化，补充 Inventory 变质/腐朽模型接入要求。 |
| v0.4 | 2026-10-30 | 将执行路线改为基础设施轨道与可玩内容轨道并行；增加 V0—V5 纵向切片、每轮切片完成证据和能力门映射，明确不再串行完成全部基础设施后才进入 UE。 |
| v0.3 | 2026-10-29 | 补齐五阶段事实 Owner：Ownership、Economy、Politics、Territory、Campaign；增加事实覆盖审查、可执行规则要求、跨阶段 fixture 验证，并明确 30 天只限制内容规模。 |
| v0.2 | 2026-10-29 | 审查并修正基础设施范围：明确第一阶段内容切片与五阶段正式基础设施分离；增加全量 Owner 注册表、Owner 交付物、公共合同冻结、EventStore/WRK 恢复内核、全量 Authority 与跨域 Workflow 阶段门。 |
| v0.1 | 2026-10-28 | 建立第一阶段县城守城 Demo 的体验闭环、UE/Paralls 边界、Owner、资源、暂停、回放、验收和执行路线。 |
