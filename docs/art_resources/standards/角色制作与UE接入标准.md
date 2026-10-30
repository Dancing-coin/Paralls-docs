# 角色制作与UE接入标准

> 版本：1.0（职责拆分版）
> 评审状态：迁移整理基线；继承原规格的待评审项
> 实现状态：交付合同；本次未验证资产或运行实现
> 整理日期：2026-10-30
> 项目：Guoshang / 《国殇：汉末》
> 来源：原07 v0.3 的通用制作、性能和接入合同

<a id="character-authority"></a>
## 权威边界与条件能力

本篇维护角色比例/材质目标、模型预算、骨架、Socket、动画、命名、导入和资源交付检查；召陵县角色选择、数量与批次在[角色素材需求](../requirements/召陵县/角色素材需求.md)。运行时写权与本地执行只引用 [UE 本地提交与 Paralls 同步](../../architecture/05-运行时接入/01-UE本地提交与Paralls同步.md#ue-paralls)；Agent/群体/动画连续性只引用 [Agent、群体与动画接入](../../architecture/05-运行时接入/02-Agent群体与动画接入.md#agent-population)。本篇记录接口需要消费的事实，不立新的Owner。

原07的“首版预算”和“最小动画集”作为来源设计库保全，均待性能与玩法评审；骑乘、坐骑、三队阵型及对应相机/Socket仅在能力被选用时适用，当前守城 Demo 不因本篇自动新增这些硬验收。原文汉末写实为长期成品质检；当前有登记的 Low Poly/灰盒样本可证明骨架、动作和玩法链路，不能提升为正式成品。

`asset_id` 为稳定家族、`version` 为不可变版本；原07:152“可替换资产版本”的措辞按该现有治理分离理解，角色 `character_id/unit_id/faction_id` 仍是玩法身份。所有示例 `/Game/...` 和 Socket 名保全，示例不代表已生成资产或实机通过。

资源身份、授权、manifest、生命周期和准入规则仅在[资源治理](../README.md)维护；本篇按该规范交付和登记，不重复定义治理状态。

<a id="character-024"></a>
<!-- 原始来源：docs/PRD/玩法系统/07-召陵县第一阶段Demo角色素材需求.md:24-25 -->
## 视觉目标与边界

<a id="character-026"></a>
<!-- 原始来源：docs/PRD/玩法系统/07-召陵县第一阶段Demo角色素材需求.md:26-33 -->
### 写实风硬约束

- 服装、盔甲、武器和坐骑装备以东汉末年为参考，优先使用可解释的结构、缝制、绑扎、铆接、磨损和污渍；不使用现代扣件、塑料、拉链、科幻结构或无依据的西式骑士装饰。
- 角色采用真实人体和马匹比例，衣物、札甲、披帛、腰带、鞍具和武器应有厚度、重量和碰撞关系；不得使用玩具化比例、纯色块身体或刻意棱角化的 Low Poly 外形。
- 写实不等于每个单位都做电影级高模。近景角色保留面部、手部、装备连接和布料层次，中远场通过 LOD、材质实例和动画简化维持同一套写实视觉语法。
- 阵营识别使用旗帜、队标、臂带、披风边、盾面和局部配色，不给整套服装覆盖高饱和纯色；敌我差异必须在无 UI 时也能辨认。
- 角色不使用血腥夸张的永久伤口作为主要识别手段；受击、失能、溃退和死亡通过动作、姿态、装备损坏、旗号和状态投影表达。

<a id="character-034"></a>
<!-- 原始来源：docs/PRD/玩法系统/07-召陵县第一阶段Demo角色素材需求.md:34-41 -->
### 镜头优先级

| 镜头 | 必须看清 | 角色质量要求 |
|---|---|---|
| 第一人称 | 马颈/缰绳、武器、手部、冲锋方向、近距离命中反馈 | 玩家手臂和武器无穿模；马匹颈部、鬃毛、鞍具和缰绳有真实接触关系 |
| 第三人称 | 玩家骑将、亲卫、敌方指挥官、军旗和冲锋姿态 | 玩家与关键角色 LOD0/LOD1 轮廓稳定；动作重心和转向可信 |
| 俯视/远景 | 队伍归属、阵型、军旗、传令方向、溃退与重整 | 角色可用批次/实例化投影承载数量，但旗号、队形和移动状态不丢失 |

<a id="character-064"></a>
<!-- 原始来源：docs/PRD/玩法系统/07-召陵县第一阶段Demo角色素材需求.md:64-77 -->
### 角色资产预算

预算是首版目标，必须在 UE 实测中记录峰值、帧率、纹理流送和同时可见数量后再调整。

| 层级 | LOD0 三角面目标 | LOD1 / LOD2 | 纹理目标 | 材质槽目标 |
|---|---:|---:|---|---:|
| 玩家骑将/敌方将领 | 45k—70k | 25k—40k / 10k—18k | 身体与装备 4K；远层 2K/1K | 4—6 |
| 亲卫/队长/传令兵 | 30k—50k | 16k—28k / 7k—14k | 2K；关键装备可独立 2K | 3—5 |
| 近场步兵/骑兵 | 18k—30k | 10k—18k / 4k—9k | 1K—2K | 2—4 |
| 中远场步兵/民夫 | 10k—18k | 5k—10k / 2k—5k | 1K | 1—3 |
| 远端批次代理 | 不固定 | 由实例化/批次投影决定 | 统一材质实例 | 1—2 |
| 玩家战马 | 35k—55k | 20k—32k / 8k—16k | 2K—4K | 3—5 |
| 驮马/驮畜 | 18k—30k | 10k—18k / 4k—9k | 1K—2K | 2—4 |

<a id="character-100"></a>
<!-- 原始来源：docs/PRD/玩法系统/07-召陵县第一阶段Demo角色素材需求.md:100-101 -->
## 骨骼、动画和运行接口

<a id="character-102"></a>
<!-- 原始来源：docs/PRD/玩法系统/07-召陵县第一阶段Demo角色素材需求.md:102-127 -->
### 骨骼与导入

- 人形角色首选一套项目统一基础骨架；新增骨骼必须说明无法复用的原因，并提供重定向映射表。
- 骑乘角色与战马分离为两个 Skeletal Mesh，通过稳定 Socket 连接；骑手根骨、马鞍和相机锚点不能写死在某个外部资产的绝对路径中。
- 统一使用厘米单位、Z 轴向上、角色面向项目约定的前方；导出前提供静止参考姿势、骨骼层级、根骨位置和比例说明。
- 每个角色必须提供 Physics Asset、简单胶囊/身体碰撞、武器 Socket、手部握持 Socket、骑乘 Socket 和受击区域标识；逻辑体与视觉网格可独立查询。

推荐 Socket：

```text
S_Weapon_Main
S_Weapon_Secondary
S_Shield
S_Flag_Back
S_Hand_R
S_Hand_L
S_RiderRoot
S_Camera_ThirdPerson
S_Camera_FirstPerson
S_Hit_Head
S_Hit_Torso
S_Hit_Limb
```

运行接入遵循[UE 协作与全量 Owner 节奏矩阵](../../architecture/05-运行时接入/01-UE本地提交与Paralls同步.md#ue-cadence-matrix)：近场移动、命中、Body、LifeState、装备、效果和士气在获准的 UE Runtime 协作，执行器采用 UE 原生能力；[ESM](../../architecture/05-运行时接入/03-ESM复用与迁移.md#esm-migration)只复用适合的合同。玩家视野内已激活 Agent 的语义动作由当前有效意图持有者控制；本地受击、体力约束和强制身体反应及时执行，但不得擅自替 Agent 产生新的自主策略。

<a id="character-128"></a>
<!-- 原始来源：docs/PRD/玩法系统/07-召陵县第一阶段Demo角色素材需求.md:128-141 -->
### 第一阶段最小动画集

| 类别 | 必需动画 | 适用角色 |
|---|---|---|
| 基础移动 | Idle、呼吸、转身、Walk、Run、Stop、受阻/绕行 | 全部人形 |
| 骑乘 | Mount、Dismount、Ride Idle、Ride Walk、Ride Run、Ride Turn、Ride Stop | 玩家骑将、骑兵 |
| 命令与传令 | Observe、Signal、Receive Order、Deliver Order、Acknowledge、拒绝/迟疑 | 玩家、亲卫、队长、传令兵 |
| 战斗 | Weapon Ready、Attack 1—2、Block/Guard、Hit React、Stagger、Knockdown | 战斗角色 |
| 状态 | Wounded、Carry、Retreat、Rally、Surrender、Death/Disable | 战斗角色、伤员 |
| 阵型 | Form Up、Hold、Advance、Charge、Break Formation、Reform | 三队、敌军 |
| 生活工作 | Carry、Load、Unload、Forge、Treat、Draw Water、Idle Work | 民夫、工匠、医舍角色 |

攻击动画可以先提供少量可验证动作，但必须保留动作标签、武器类型和命中证据接口；动画结束不等于 Combat 已结算。暂停时所有动画、马匹和队伍状态冻结，恢复后从同一世界时间继续。

<a id="character-142"></a>
<!-- 原始来源：docs/PRD/玩法系统/07-召陵县第一阶段Demo角色素材需求.md:142-149 -->
## 材质、颜色和表现规则

- 使用 PBR 材质，金属、皮革、木材、织物、骨/角、泥尘和血迹必须有可区分的粗糙度与法线响应；不以单一纯色材质覆盖整个人物。
- 玩家和关键角色允许使用 4K 近景贴图，但必须提供 2K/1K 降级版本和纹理流送设置；中远场角色优先共用材质图集和材质实例。
- 角色脸部、手部和武器边缘保留适度磨损；盔甲和服装磨损要遵循角色身份、战斗经历和环境，不使用随机噪声替代制作。
- 己方主识别色使用青蓝/青绿系局部布料、旗带或臂带，敌方使用暗红/赭色局部布料、旗带或臂带；场景中的建筑和地面不得大面积使用相同阵营色。
- 军旗、队旗和令牌属于角色识别的一部分，旗面、旗杆、挂点和阵营字段必须分离；旗帜物品存在/数量读取 Inventory，装备挂接读取 Equipment，位置读取 Presence，部队归属读取 Organization；损坏按实体登记读取 Equipment 或 Facility。Morale 结算军心后果，Objective 消费目标结果，两者不写旗帜物理状态。

<a id="character-150"></a>
<!-- 原始来源：docs/PRD/玩法系统/07-召陵县第一阶段Demo角色素材需求.md:150-186 -->
## 命名、目录和资产包

角色资产沿用统一资源治理：`asset_id` 标识稳定资产家族，`version` 标识不可变版本（原文“可替换的资产版本”见迁移注记），角色身份 ID（如 `character_id`、`unit_id`、`faction_id`）标识玩法中的人/单位，两者不能互相替代。`SK_`、`ABP_`、`AN_`、`MI_`、`PHYS_` 等 UE 名称只是对象映射；Gameplay Component、Owner receipt、阵营/队伍和装备状态必须通过结构化数据关联。

建议 UE 目录：

```text
/Game/Guoshang/Characters/
/Game/Guoshang/Characters/Humanoid/
/Game/Guoshang/Characters/Mounted/
/Game/Guoshang/Characters/Animals/
/Game/Guoshang/Characters/Animations/
/Game/Guoshang/Characters/Materials/
/Game/Guoshang/Characters/Variants/
/Game/Guoshang/Characters/Logic/
```

示例命名：

```text
SK_GS_PlayerCommander
SK_GS_Guard_A
SK_GS_Infantry_Friendly_A
SK_GS_Infantry_Enemy_A
SK_GS_Horse_Player
SK_GS_PackHorse_A
ABP_GS_Humanoid
ABP_GS_Horse
AN_GS_Ride_Run
AN_GS_Order_Deliver
MI_GS_Infantry_Friendly_A
PHYS_GS_PlayerCommander
DT_GS_CharacterRegistry
```

角色资产的来源、许可证、文件校验、目录、生命周期、依赖、证据和回退统一遵循[美术资源管理 README](../README.md)及[manifest 模板](../asset_manifest_template.yaml)。角色 manifest 还必须登记角色身份 ID、批次、骨架/动画/装备依赖、比例、LOD、Physics Asset、Socket、Gameplay Component 和目标 UE 路径；运行时只引用 `/Game/...`，不引用个人电脑绝对路径。

<a id="character-233"></a>
<!-- 原始来源：docs/PRD/玩法系统/07-召陵县第一阶段Demo角色素材需求.md:233-241 -->
## 资源登记字段

每个角色、坐骑、动画包和外部服装组件按[美术资源管理 README](../README.md)登记通用治理字段；本需求额外要求记录：

- 身体/装备三角面数、骨骼数量、动画数量、材质槽、纹理分辨率、LOD 和 Physics Asset；
- 是否含面部、手部、骑乘、武器、旗帜和受击区域；
- 目标角色层级、使用场景，以及与既有角色的替代关系；
- 是否保持现有 Gameplay Component、碰撞接口、相机锚点、命令来源和状态事件。

<a id="source-modular-character-budget"></a>
## 原总策划模块组合预算示例（未验证资产数量）

来源：原 `docs/PRD/烽火王座：汉末群雄_总策划案_v1.0.md:396`，由总策划迁移工作完整读取后提供。以下是设计预算示例，不表示已有资源、下载/导入数量或当前县城 Demo 必交数量；它与上文按镜头距离/角色重要性区分的 LOD 预算并行，不自行换算成独立完整角色套数。

> 装备资产采用模块组合：基础身体约三套、头型十至十二种、甲胄六套、马甲两套、头盔六种、盾六种、武器十八至二十件、马四种。兵种读取装备预设；派系皮肤通过材质、甲色、布衣色、盾徽、旗帜、盔缨和少量甲片体现，不制作二十套独立模型。

模块仍须以稳定资产ID/版本、骨架/装备依赖和manifest登记；这段原设计不会把骑乘及马匹自动提升为当前必须实现的产品验收。


## 完整玩法稿的动画与音频反馈（来源补充）

以下保留完整玩法稿的触发条件、表现目的和优先级。它们不是已制作动作或已接入音频的事实；骑乘、继任及具体关键目标仍按当前产品范围选用，不能借此恢复旧骑将冲阵独立验收。音乐和配音优先级在原文留空，保持待决；音效原文为高优先级。

<a id="gameplay-animation-feedback"></a>
<!-- 原始来源：docs/PRD/烽火王座：汉末群雄_玩法策划案_v0.1.md:679-689 -->
### 8.3 动画与特效

| 触发条件 | 动作 / 特效 | 表现目的 | 优先级 |
|---|---|---|---|
| 玩家开始移动/冲锋 | 骑乘移动、加速、接触动作 | 传达速度、方向和承诺 | 高 |
| 命令发出/中继/抵达/拒绝 | 传令动作、路径/节点提示、状态变化 | 让命令过程可追踪 | 高 |
| 阵型变化 | 队伍重组、压缩、松散、溃散等表现 | 解释战术状态变化 | 高 |
| 士气变化 | 旗帜、队伍动作、图标、声音和状态提示 | 让压力、动摇和恢复可读 | 高 |
| 关键目标变化 | 旗帜、敌将或冲车的归属/损坏/状态效果 | 给出明确目标反馈 | 高 |
| 指挥失能/继任 | 失能、接管、队伍重规划反馈 | 解释控制权变化 | 中 |

<a id="gameplay-audio-requirements"></a>
<!-- 原始来源：docs/PRD/烽火王座：汉末群雄_玩法策划案_v0.1.md:690-697 -->
### 8.4 音频需求

| 类型 | 使用场景 | 情绪或信息目的 | 优先级 |
|---|---|---|---|
| 音乐 | 战场进入、冲突升级、收尾 | 传达节奏和阶段 |  |
| 音效 | 移动、冲锋、命令、军旗、接触、受击、拒绝、继任 | 提供状态与危险提示，补充视觉信息 | 高 |
| 配音 | 传令、关键目标、战报、角色对话 | 提高命令和因果的可辨性 |  |

