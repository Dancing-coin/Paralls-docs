# 01-FactType 定义

- 版本：1.0
- 状态：已定义
- 上级：[架构入口](../README.md)

FactType 是**最小写权单位**。它声明"某一类事实长什么样、归谁写、谁看得见、什么时候算"，不含任何实现。

---

<a id="granularity"></a>

## 一、粒度

```
fact:facility:gate-03:durability      ← 一个具体事实
fact:character:char-07:health         ← 一个具体事实
fact:unit:gate-east-squad:morale      ← 一个具体事实
```

**粒度判据**：一个 FactType 对应一条独立的 revision 流。

若两类事实必须**永远同时**变更且永不分拆，它们才是一个 FactType。否则分开。

反例：把"城门耐久"和"城门闩锁状态"合成 `gate-03:condition` 是错的——两者可以独立变化（闩可开可关，耐久只降）。

---

<a id="fields"></a>

## 二、必填字段

```text
fact_type_id        稳定标识，命名规范见 §四
primitive           pool | machine | holdings | bond | process | place
identity            entity_ref | collection_ref | region_ref | singleton
owner_ref           → L3 Owner，必填
visibility          见 §三，无默认值
resolution_order    稠密唯一整数，由管线拓扑生成
event_schema_ref    → event_schema_registry 注册项
invariant_refs      [原语不变量] + [本域附加]
cadence             事件触发 | 窗口 | 逐模拟步
host                ue | paralls | population | either
aggregation         none | sum | distribution | ordered
refold_model_ref    仅 distribution 必填
unknown_policy      reject | propose | degrade
```

### 三条无默认值

| 字段 | 缺失后果 |
|---|---|
| `visibility` | 注册失败（H3） |
| `resolution_order` | 注册失败（H4） |
| `owner_ref` | 注册失败 |

不给默认值是有意的：默认值会让"忘记声明"变成静默通过，而可见性与结算顺序的错误都是静默的。

---

<a id="visibility"></a>

## 三、visibility 结构

```text
visibility:
  class:        public | faction | private | secret | debug_only
  learnable_by: [principal_selector]
  channel:      direct | report | rumor | inference | none
  delay_model:  model_ref | null
  distortion_model: model_ref | null
  persistence:  permanent | until_expiry | memory_only
```

详见 [可见性强制](../01-内核/02-可见性强制.md)。

---

<a id="naming"></a>

## 四、命名规范

```
fact:<domain>:<scope_id>:<name>
```

| 段 | 规则 |
|---|---|
| `domain` | 小写，单数，来自 L3 Owner 的 domain 名 |
| `scope_id` | 实体 ID 或 `global` |
| `name` | 小写蛇形，描述事实本身而非玩法 |

例：

```
fact:character:char-07:health
fact:character:char-07:stamina
fact:facility:gate-03:durability
fact:facility:gate-03:latch
fact:facility:gate-03:integrity
fact:lot:wheat-07:quantity
fact:lot:wheat-07:quality
fact:unit:gate-east:morale
fact:county:zhaoling:control
fact:character:char-07:status-bleeding
```

**不允许的命名**：

```
fact:combat:hit                    ← 没有 scope，不是事实
fact:siege:progress                ← 玩法状态不是事实
fact:character:char-07:stats       ← 笼统容器，多个 revision 混在一条流
```

---

<a id="revision"></a>

## 五、revision 与流

每个 FactType 在 `(scope, epoch)` 下是一条独立事件流：

```
stream_id = fact_type_id
revision  = 该流的事件序号
```

提交必须携带 `expected_revision`，CAS 失败即拒绝。

**不得跨 FactType 共享 revision。** 共享会让"哪些事实被读过"变得不可判定。

---

<a id="cadence"></a>

## 六、cadence 与 host

| 字段 | 取值 | 含义 |
|---|---|---|
| `cadence` | `event` | 有事件即结算，通常不需逐帧 |
| | `window` | 按时间窗口推进，遇边界切窗 |
| | `step` | 逐模拟步，仅限近场 |
| `host` | `ue` | UE 本地承载 |
| | `paralls` | 后端承载 |
| | `population` | 群体模拟承载 |
| | `either` | 允许任一，运行时按 epoch 决定 |

`host` 不改变 Owner 身份。同一 FactType 在两个宿主上必须给出相同结果（固定向量验证）。

---

<a id="registration"></a>

## 七、注册与校验

注册时执行下列检查，任一失败即拒绝：

```text
facttype_primitive_unknown          primitive 不在六种内
facttype_visibility_missing         无 visibility
facttype_resolution_order_missing   无 resolution_order
facttype_resolution_order_duplicate 同 scope 内重复
facttype_owner_unknown              owner_ref 未注册
facttype_schema_unknown             event_schema_ref 未注册
facttype_refold_missing             aggregation=distribution 但无 refold_model
```

---

<a id="examples"></a>

## 八、示例：县城守城的首批 FactType

| FactType | 原语 | Owner | 可见性 | 频率 |
|---|---|---|---|---|
| `character:char-07:health` | pool | Body | private | event |
| `character:char-07:stamina` | pool | Body | private | window |
| `character:char-07:lifestate` | machine | LifeState | private | event |
| `character:char-07:status-bleeding` | process(temporal) | Status | private | event |
| `character:char-07:armor-durability` | pool | Equipment | private | event |
| `facility:gate-03:durability` | pool | Production/Facility | faction | event |
| `facility:gate-03:latch` | machine | Production/Facility | faction | event |
| `facility:gate-03:integrity` | pool | Production/Facility | faction | event |
| `place:gate-03:passability` | machine | Presence | public | event |
| `lot:wheat-07:quantity` | holdings | Inventory | faction | event |
| `lot:wheat-07:quality` | pool | Inventory | faction | window |
| `unit:gate-east:morale` | pool | Morale | faction | event |
| `unit:gate-east:formation` | machine | Morale | faction | event |
| `county:zhaoling:control` | machine | Territory | public | event |
| `character:char-07:order-0008` | process | Dispatch | report | event |

注意最后一行：**命令是一条 Process 事实**，因为传令有步骤、会中断、有送达与接受。

注意 `place:gate-03:passability`：它是独立的 Machine，"门破了"不自动改通行性——由 Presence 独立评估并提交。
