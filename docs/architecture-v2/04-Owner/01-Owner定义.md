# 01-Owner 定义

- 版本：1.0
- 状态：已定义
- 上级：[架构入口](../README.md)

Owner 是**唯一拥有写权的单位**。L0/L1/L2/L4/L5 都不是 Owner。

---

<a id="two-kinds"></a>

## 一、两类 Owner

判据只有一个：**是否存在无法由数据表达的 Resolver。**

| | 原生 Owner（native） | 托管 Owner（stewarded） |
|---|---|---|
| 判据 | 有自有 Resolver，规则无法数据化 | 只有写集与不变式，机制全由原语提供 |
| 实现 | 保留独立 runtime | FactType 声明 + 规则包，**无 runtime** |
| 数量（估计） | 8–10 | 6–8 |
| 变更成本 | 改代码 | 改数据 |

### 原生 Owner

| Owner | 为何必须原生 |
|---|---|
| Command / Dispatch | 传递链、送达与接受语义、失真 |
| Organization / Military | 继任、授权范围、编制与预案 |
| Government / Policy | 政令冲突、例外、撤销 |
| Information / Intelligence | 传播、核验、误报 |
| Economy / Market | 撮合、报价、债务结算 |
| Social / Influence | 公共关系、声望演化 |
| Politics / Legitimacy | 承认、派系承诺、外交 |
| Territory / Control | 争夺状态、控制转移条件 |
| Objective / Victory | 胜负条件组合 |
| Campaign / Strategic | 阶段推进、继承、分岔 |

### 托管 Owner

| Owner | 为何可以托管 |
|---|---|
| Body / Resource | 生命、体力、伤势——全是池与状态机 |
| Equipment | 防护、耐久、破损——池 |
| Status / Effect | 效果实例——temporal_process |
| LifeState | 生命周期——状态机 |
| Morale / Formation | 士气和阵型——池 + 状态机 + 聚合 |
| Survival | 饥渴疲劳——池 |
| Inventory / Resource | 数量、预留、质量——holdings + pool |
| Ownership / Property | 产权、保管、使用——bond |
| Production / Facility | 工坊状态、完整度、门闩——池 + 状态机 |
| Population / Work | 岗位、班次——bond + 状态机 |
| Transport / Logistics | 运输批次——process |
| Presence / Movement | 位置、占用——place |

**这个划分不是绝对的**：一个托管 Owner 可以在某个子域上"长"出一个 Resolver，此时该子域升级为原生。反之原生 Owner 的部分事实可以托管。

---

<a id="fields"></a>

## 二、Owner 声明字段

```text
owner_id            稳定、手写、可审计
kind                native | stewarded
domain              短名，用于 FactType 命名
writes              [fact_type_pattern]      必填
denies              [fact_type_pattern]      邻域禁止，显式
invariants          [跨 fact_type 的域不变式]
commands            [command_type]
resolvers           [model_id]               原生必填，托管为空
reads               [fact_type_pattern]
default_scope       authority_scope 默认值
host                ue | paralls | either
```

### writes 用 pattern 而非枚举

```
writes: ["fact:character:*:health", "fact:character:*:stamina"]
```

因为事实与实体是一对多：Body 管所有角色的生命，不是管某一个。

### denies 是显式否定

v1 已正确要求这份"禁止写的邻域事实"清单。v2 保留并要求可被校验器读取。

例：

```text
owner: Combat
  writes: ["fact:engagement:*:*"]
  denies: ["fact:character:*:health",
           "fact:character:*:armor-durability",
           "fact:character:*:status-*",
           "fact:character:*:lifestate"]
```

Combat 产出伤害评估，不能写生命、耐久、效果、生命周期。

---

<a id="why-invariants"></a>

## 三、为什么 Owner 必须是责任单位

这是 Owner 与 FactType 的区别所在，也是本层存在的理由。

### 反例：预留不超过总量

```text
fact:lot:wheat-07:quantity      Holdings    → Inventory 写
fact:lot:wheat-07:reserved      Pool？      → 同上
```

"预留 ≤ 总量"这条不变式**跨两个 FactType**。

若 Owner 只是写入权限的集合，这个不变式没有归属——登记只说两者都归 Inventory 写，没人负责检查它们的关系。

### 所以

```text
Owner = 写集 + 跨事实不变式 + 命令词汇 + 可用 Resolver
```

四者缺一不可。**跨事实不变式是 Owner 的核心内容，不是附属说明。**

其他跨事实不变式的例子：

| Owner | 跨事实不变式 |
|---|---|
| Inventory | 预留 ≤ 总量；容器容量 ≥ 内容物之和 |
| Body | 生命为 0 时体力必须为 0；伤势与身体功能一致 |
| Equipment | 装备耐久为 0 时防护等级必须为 0 |
| Morale | 阵型状态与队伍士气阈值一致 |
| Territory | 控制状态与 Presence 的占领事实一致 |
| Dispatch | 命令的接受不得早于送达 |

---

<a id="owner-instance"></a>

## 四、Owner Instance

同一逻辑 Owner 可以有多个实例：

```text
Inventory Owner
  ├─ instance @ county:zhaoling:granary
  ├─ instance @ county:zhaoling:armory
  └─ instance @ village:east:store

Morale Owner
  ├─ instance @ character:char-07
  ├─ instance @ squad:gate-east
  └─ instance @ garrison:zhaoling
```

实例共享 Owner 的规则与不变式，各自持有独立的 scope 与 epoch。

**实例不产生新的 Owner 层。** 这是与"父 Owner → 子 Owner"的根本区别。

---

<a id="no-hierarchy"></a>

## 五、Owner 之间是平级协作

```
✗ SiegeOwner
    ├─ Combat
    ├─ Inventory
    └─ Objective

✓ Combat, Inventory, Objective 平级
  守城 = play_pattern（L5），不是 Owner
```

Owner 之间只通过四种方式交互：

1. **Command** —— 请求另一个 Owner 做事
2. **授权 fragment** —— 同一批次的协作提交
3. **revision pin** —— 读取时固定版本
4. **receipt** —— 获知结果

**不存在"上级 Owner 直接写下级事实"的路径。**

---

<a id="new-owner"></a>

## 六、新增 Owner 的门槛

v2 的目标是**减少**新增 Owner，不是方便新增。新增必须同时满足：

1. 存在既有 23 个都不拥有的独立事实域；
2. 该事实域有**无法由数据表达的 Resolver**，因此不能托管；
3. 该事实域有跨事实不变式，因此不能只作为 FactType 挂在既有 Owner 下；
4. 不与其他 Owner 的 `writes` 相交。

4 条全部成立才新增。**只是"加一种数值"或"加一种可受伤实体"，一律走规则包，不新增 Owner。**
