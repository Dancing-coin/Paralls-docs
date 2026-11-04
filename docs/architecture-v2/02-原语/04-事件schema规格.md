# 04-事件 schema 规格

- 版本：1.0
- 状态：已定义
- 上级：[架构入口](../README.md)
- 前置：[六原语规格](02-六原语规格.md)（只列字段名，本文给出字段级类型与约束）

本文件补齐 L0（写入）、L2（校验）、L4（规则包）、双端等价四处的共同依赖。

---

<a id="why"></a>

## 一、为什么需要这一份

`02-六原语规格` 给出了每个事件类型**有哪些字段名**，例如：

```text
pool.adjusted   { fact_type, previous, delta, next, window_ref, model_ref }
```

但没有给出：字段类型、可否为空、数值精度、版本规则、跨宿主序列化形式。

这四处都需要它：

| 位置 | 需要什么 |
|---|---|
| L0 写入 | 事件落库时的编码与校验 |
| L2 FactType | `event_schema_ref` 指向什么 |
| L4 规则包 | 不变式表达式引用的字段是否存在 |
| 双端等价 | C++ 与 Python 产生逐位相同的字节 |

**没有这一层，前四处各自发明一套，等价性从第一天就不可能成立。**

---

<a id="common-envelope"></a>

## 二、公共封套

所有领域事件共享同一外层，字段由 L0 强制，不由原语定义。

```text
event_id            string          全局唯一，格式 evt:<command_id>:<domain>:<index>
event_type          string          见 §三的类型表
schema_version      int ≥ 1        事件类型自身的版本，不是规则包版本
stream_id           string          = FactType ID
stream_revision     int ≥ 1         该流内的序号
global_sequence     int ≥ 1         全局序号，由 L0 分配
transaction_id      string          所属原子批次
command_id          string          引起该事件的命令
causation_id        string          因果链
correlation_id      string          相关链
visibility_policy   string          见 [可见性强制](../01-内核/02-可见性强制.md)
payload             object          见 §三
```

### 硬约束

| 约束 | 违反后果 |
|---|---|
| `event_id` 全局唯一 | 批次拒绝 |
| `stream_revision` 在同一 `stream_id` 内严格递增、无空洞 | 批次拒绝 |
| `global_sequence` 由 L0 分配，事件不得自带 | 批次拒绝 |
| `payload` 必须是 object，不允许是数组或标量 | 批次拒绝 |

最后一条的理由：`payload` 是数组时，按字段名做可见性过滤和部分投影都不可行。

---

<a id="types"></a>

## 三、类型系统

### 3.1 基础类型

跨宿主等价要求类型集合封闭。只用这八种：

| 类型 | 表示 | 说明 |
|---|---|---|
| `str` | UTF-8 字符串 | 长度 ≤ 512，无控制字符 |
| `int` | 64 位有符号整数 | JSON 中不带小数点 |
| `dec` | 定点小数 | **不用浮点**，见 §3.2 |
| `bool` | 布尔 | |
| `ref` | 字符串，带命名空间前缀 | 如 `fact:...`、`character:...`、`event:...` |
| `enum` | 字符串，取值封闭 | 取值集合由 schema 声明 |
| `list<T>` | 有序数组 | |
| `map<str,T>` | 字符串键映射 | 键排序稳定 |

**明确禁止**：`float`、`null`（用缺省字段代替）、嵌套任意深度（最多 2 层）、二进制。

### 3.2 定点小数 `dec`

浮点在 C++ 与 Python 间不可能逐位一致。`dec` 的定义是：

```text
dec = { "v": <int>, "s": <int> }     // 值 = v / 10^s，s ∈ [0, 6]
```

序列化为 `str`：`"12.3456"`，固定小数位由 schema 声明，不足补零。

例：`health = 62.5` → `"62.5000"`（`scale: 4`）

**为什么不用 JSON number**：`0.1 + 0.2` 在两种语言都可能给出不同位模式；定点整数加固定 scale 可以做到逐位相同。

### 3.3 可选字段

可选字段用**缺省**表示，不用 `null`：

```text
pool.adjusted:
  model_ref: ref      # 可缺省（手工调整时无模型）
```

缺省与 `null` 的区别：缺省表示"不适用"，必须显式在 schema 声明；`null` 表示"不知道"，而"不知道"应走 `unknown` 而非字段值。

---

<a id="schemas"></a>

## 四、六原语事件 schema

以下为字段级规格。`?` 表示可缺省，`≤n` 表示长度上限。

### 4.1 Pool

```text
pool.initialized        v1
  fact_type         ref
  initial           dec(scale per def)
  bound_lower       dec
  bound_upper       dec

pool.adjusted           v1
  fact_type         ref
  previous          dec
  delta             dec
  next              dec
  window_ref        str?            积分窗口；事件触发调整时缺省
  model_ref         ref?            无模型的手工调整可缺省
  reason_code       enum(adjust_reason)

pool.reserved           v1
  fact_type         ref
  reservation_ref   str
  amount            dec
  holder_ref        ref
  purpose_code      enum(reserve_purpose)

pool.released           v1
  fact_type         ref
  reservation_ref   str
  amount            dec
  reason_code       enum(release_reason)?     leftover 时必填

pool.consumed           v1
  fact_type         ref
  reservation_ref   str
  amount            dec            预留量
  actual            dec            ≤ amount
  reason_code       enum(consume_reason)

pool.bound_changed      v1
  fact_type         ref
  previous_lower    dec
  previous_upper    dec
  next_lower        dec
  next_upper        dec
  authority_ref     ref            改界需要授权依据

pool.threshold_crossed  v1
  fact_type         ref
  threshold_ref     str
  direction         enum(enter|exit)
  value             dec
```

### 4.2 Machine

```text
machine.transitioned    v1
  fact_type         ref
  from_state        enum(state)
  to_state          enum(state)
  condition_ref     ref
  condition_revision int ≥ 1
  evidence_refs     list<ref>      ≤ 16

machine.pending         v1
  fact_type         ref
  target_state      enum(state)
  reason_code       enum(condition_unknown|input_missing|input_stale)

machine.locked          v1
  fact_type         ref
  state             enum(state)
  reason_code       enum(terminal|no_transition|policy_blocked)
```

### 4.3 Holdings

```text
holdings.lot_created    v1
  lot_ref           ref
  item_ref          ref
  quantity          dec
  quality           dec?            质量独立为 Pool 时缺省
  container_ref     ref

holdings.reserved       v1
  lot_ref           ref
  reservation_ref   str
  amount            dec

holdings.transferred    v1
  src_lot_ref       ref
  dst_lot_ref       ref
  amount            dec
  step_ref          ref?            过程内转移时必填

holdings.consumed       v1
  lot_ref           ref
  amount            dec
  reason_code       enum(consume_reason)

holdings.split          v1
  source_lot_ref    ref
  result_lot_refs   list<ref>      ≤ 32
  amounts           list<dec>      与 result_lot_refs 等长

holdings.merged         v1
  source_lot_refs   list<ref>      ≤ 32
  result_lot_ref      ref

holdings.lost           v1
  lot_ref           ref
  amount            dec
  reason_code       enum(loss_reason)
```

### 4.4 Bond

```text
bond.granted            v1
  bond_ref          str
  subject_ref       ref
  target_ref        ref
  bond_type         enum(ownership|custody|authority|affiliation|obligation)
  scope             str
  term_expires_at   int?            缺省 = 永久（B3 要求显式语义）
  source_event_ref  ref
  attributes        map<str, dec|str|bool>?   上限 8 项

bond.revoked            v1
  bond_ref          str
  reason_code       enum(revoke_reason)

bond.transferred        v1
  bond_ref          str            旧契
  previous_subject  ref
  new_subject       ref
  new_bond_ref      str            新契（转移产生两条契）

bond.expired            v1
  bond_ref          str
  world_tick        int

bond.superseded         v1
  old_bond_ref      str
  new_bond_ref      str
```

### 4.5 Process

```text
process.started         v1
  process_id        str
  process_def_ref   ref
  input_revisions   map<ref,int>   ≤ 32 项

process.step_done       v1
  process_id        str
  step_index        int ≥ 0
  result_ref        ref?
  receipt_ref       ref

process.interrupted     v1
  process_id        str
  step_index        int
  reason_code       enum(interrupt_reason)
  open_obligations  list<ref>      ≤ 16

process.resumed         v1
  process_id        str
  from_step         int

process.completed       v1
  process_id        str
  output_refs       list<ref>      ≤ 32

process.failed          v1
  process_id        str
  step_index        int
  reason_code       enum(fail_reason)
  compensation_refs list<ref>      ≤ 16

process.cancelled       v1
  process_id        str
  committed_steps   list<int>
  reason_code       enum(cancel_reason)
```

### 4.6 Place

```text
place.occupied          v1
  place_ref         ref
  holder_ref        ref
  occupancy_ref     str

place.vacated           v1
  place_ref         ref
  occupancy_ref     str

place.departed          v1
  holder_ref        ref
  from_ref          ref
  path_ref          ref

place.arrived           v1
  holder_ref        ref
  to_ref            ref

place.blocked           v1
  place_ref         ref
  reason_code       enum(block_reason)
  source_event_ref  ref

place.rerouted          v1
  holder_ref        ref
  previous_path_ref ref
  new_path_ref      ref
  reason_code       enum(reroute_reason)

place.intercepted       v1
  holder_ref        ref
  by_ref            ref
  place_ref         ref
```

---

<a id="enum-closure"></a>

## 五、enum 取值封闭

所有 enum 的取值集合必须由 schema 完整声明，**不允许开放字符串**。

理由：开放字符串会让"新增一种原因码"变成无需评审的行为改变，而原因码是玩家可读解释的一部分。

初始取值（示例，完整表由规则包声明）：

| enum | 取值 |
|---|---|
| `adjust_reason` | damage, heal, integrate, restore, grant, manual_authority |
| `consume_reason` | action_cost, recipe_input, treatment, decay, spoilage |
| `condition_unknown` 等 | 见各原语 |

新增取值需要：改 schema 版本 + 更新规则包 + 过校验器。

---

<a id="versioning"></a>

## 六、版本与兼容

### schema_version

每个事件类型独立版本。三条规则：

1. **只增不改**：已发布的版本不得改变字段语义。
2. **新增可选字段** → 提升版本号，但旧消费者可忽略。
3. **新增必填字段 / 删除字段 / 改变类型** → 新事件类型，不复用旧名。

### 回放

回放按事件携带的 `schema_version` 解释，**不按当前 schema**。这是"回放用旧版本，不用新公式重算"的事件层对应。

### upcaster

需要把旧版本事件转为新版本表示时，用纯函数 upcaster：

```text
upcast(event_type, from_version, to_version, payload) -> payload
```

约束：

- 纯函数，无 IO，无时间，无随机
- 必须在 C++ 与 Python 两端同构实现并固定向量验证
- 不得用于改变事实语义（那是补偿事件，不是升级）

---

<a id="cross-host"></a>

## 七、跨宿主序列化

### 规范形式

事件的规范序列化形式是 **JSON，键排序，无空白，定点数用字符串**：

```json
{"actual":"12.0000","amount":"12.0000","fact_type":"fact:...","reason_code":"action_cost","reservation_ref":"r-1"}
```

摘要与等价性验证都基于这一形式。

### 等价性判定

C++ 与 Python 对同一 `EvaluationResult` 产生的事件，必须：

1. 规范序列化后逐字节相同；
2. `event_id` 相同（由 command_id + domain + index 决定，不含时间戳或随机数）；
3. `payload` 的键集合与取值完全相同。

**禁止在事件中放入时间戳、随机数、指针地址、对象 id**——它们会让同一逻辑操作在不同运行产生不同事件。

---

<a id="validation"></a>

## 八、校验时机

| 阶段 | 校验内容 | 失败 |
|---|---|---|
| 规则包加载 | schema 完整性、enum 取值封闭、类型合法 | 拒绝加载 |
| 事件构造 | 字段类型、必填、长度上限、引用格式 | 拒绝构造 |
| 批次提交 | 封套约束、stream_revision 连续性 | 拒绝提交 |
| 投影重建 | payload 可被该版本解释 | 拒绝重建并报定位 |

**字段级校验失败必须给出可定位的报告**（事件类型、字段名、期望类型、实际值），不是单个布尔值。

---

<a id="what-this-does-not-cover"></a>

## 九、本文件不覆盖

| 项 | 归属 |
|---|---|
| 事件如何被过滤与谁能读 | [可见性强制](../01-内核/02-可见性强制.md) |
| 事件的提交顺序与原子性 | [权威栅栏与提交](../01-内核/03-权威栅栏与提交.md) |
| 事件如何聚合成投影 | 待写：三本账与投影规格 |
| 规则包中 schema 的存放格式 | 待写：规则包文件格式 |
| 具体 enum 的完整取值表 | 规则包（本文件只给规则） |
