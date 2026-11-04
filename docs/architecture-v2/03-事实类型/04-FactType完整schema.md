# 05-FactType 完整 schema

- 版本：1.0
- 状态：已定义
- 上级：[架构入口](../README.md)
- 前置：[01-FactType定义](01-FactType定义.md)（字段清单）、[事件 schema 规格](../02-原语/04-事件schema规格.md)

`01-FactType定义` 给出了字段名与命名规范。本文件给出**每个字段的类型、取值域、组合约束与校验规则**。

---

<a id="id"></a>

## 一、标识与身份

### fact_type_id

```text
fact:<domain>:<scope_id>:<name>
```

| 段 | 类型 | 约束 |
|---|---|---|
| `domain` | `str` | 小写字母 + 下划线，长度 2–24，必须是某个已注册 Owner 的 `domain` |
| `scope_id` | `str` | 实体 ID、`global`、或 `*`（仅模板，不用于实例） |
| `name` | `str` | 小写字母 + 数字 + 下划线 + `-`，长度 2–48 |

总长度 ≤ 128。段数恒为 4，不允许嵌套。

### identity

```text
identity: entity_ref | collection_ref | region_ref | singleton
```

`identity` 决定 `scope_id` 段的合法形式：

| identity | scope_id 形式 | 实例数量 | 例 |
|---|---|---|---|
| `entity_ref` | 单实体 ID | 每实体一条流 | `fact:character:char-07:health` |
| `collection_ref` | 集合 ID | 每集合一条流 | `fact:unit:gate-east:morale` |
| `region_ref` | 区域 ID | 每区域一条流 | `fact:region:jizhou:population` |
| `singleton` | 字面量 `global` | 全局唯一 | `fact:world:global:tick-offset` |

**校验**：`identity=singleton` 时 `scope_id` 必须恰为 `global`；其余三者 `scope_id` 不得为 `global`。

---

<a id="primitive-binding"></a>

## 二、原语绑定

### primitive

```text
primitive: pool | machine | holdings | bond | process | place
```

六选一，无默认值，不允许自定义（H1、H2）。

### temporal_effect 的声明方式

`temporal_effect` 不是第七个原语，是 `process` 的子型。声明为：

```text
primitive: process
process_kind: temporal          # 缺省 process_kind = stepwise
```

`process_kind` 只在 `primitive=process` 时合法，其余原语声明它 → 注册失败（`facttype_process_kind_invalid`）。

### 字段-原语合法性矩阵

Not every field applies to every primitive. Illegal combinations are rejected at registration.

| 字段 | Pool | Machine | Holdings | Bond | Process | Place |
|---|---|---|---|---|---|---|
| `aggregation` | ✓ | — | ✓ | — | — | — |
| `refold_model_ref` | 条件 | — | 条件 | — | — | — |
| `temporal_effect` 相关 | — | — | — | — | ✓ | — |
| `state_set_ref` | — | 必填 | — | — | — | — |
| `bond_types` | — | — | — | 必填 | — | — |
| `place_kind` | — | — | — | — | — | 必填 |

「条件」= 仅当 `aggregation=distribution` 时必填。

**理由**：允许无意义的组合会让校验器的规则集膨胀到无法维护。宁可注册失败。

---

<a id="resolution"></a>

## 三、结算顺序

```text
resolution_order: int ≥ 10, 稠密, 同 scope 内唯一
```

### 生成规则

包作者**不手填**整数，只声明偏序（见 [结算顺序](02-结算顺序.md)）。系统拓扑排序后生成整数。

```text
resolve_order:
  before: [ [a, b], [b, c] ]
  unrelated: [ d ]
```

缺 `resolve_order` 声明 → 注册失败（`facttype_resolution_order_missing`）。

### 校验

| 检查 | 拒绝码 |
|---|---|
| 偏序有环 | `facttype_resolution_order_cycle` |
| 同 scope 两个 FactType 得到相同序 | `facttype_resolution_order_duplicate` |
| 序非稠密（有空洞） | `facttype_resolution_order_gap` |

---

<a id="cadence-host"></a>

## 四、节奏与宿主

### cadence

```text
cadence: event | window | step
```

| 值 | 语义 | 允许的 primitive |
|---|---|---|
| `event` | 有事件即结算 | 全部 |
| `window` | 按时间窗口推进，遇边界切窗 | pool, machine, process, holdings |
| `step` | 逐模拟步 | pool, place（仅近场） |

`cadence=step` 且 `host=paralls` → 注册失败（`facttype_step_on_remote_host`）：远端无法逐模拟步推进。

### host

```text
host: ue | paralls | population | either
```

| 值 | 含义 |
|---|---|
| `ue` | 只在 UE 本地承载 |
| `paralls` | 只在后端承载 |
| `population` | 只在群体模拟承载 |
| `either` | 允许任一，运行时按 `authority_epoch` 决定 |

**`host` 不改变 Owner 身份。** 同一 FactType 在两个宿主上必须给出相同结果（固定向量验证）。

### cadence × host 合法矩阵

| | ue | paralls | population | either |
|---|---|---|---|---|
| `event` | ✓ | ✓ | ✓ | ✓ |
| `window` | ✓ | ✓ | ✓ | ✓ |
| `step` | ✓ | ✗ | ✗ | ✓（仅 ue 时生效） |

`either` + `step` 是合法但受限的组合：运行时若选到非 UE 宿主，`cadence` 降为 `window` 并记录降级事件。

---

<a id="visibility-fields"></a>

## 五、可见性字段

```text
visibility:
  class:            public | faction | private | secret | debug_only
  learnable_by:     list<principal_selector>      非空
  channel:          direct | report | rumor | inference | none
  delay:            { model_ref: ref, params: map } | 缺省
  distortion:       { model_ref: ref, params: map } | 缺省
  persistence:      permanent | until_expiry | memory_only
```

### 组合约束

| 组合 | 是否合法 | 理由 |
|---|---|---|
| `channel=none` 且 `learnable_by` 非空 | ✗ | 不可知的通道却声明了可学习者 |
| `class=public` 且 `learnable_by` 不含 `world` | ✗ | 公开事实必须对所有主体可学 |
| `class=debug_only` 且 `channel≠none` | ✗ | 调试事实不进任何传播链 |
| `class=secret` 且 `channel=direct` | ✗ | 秘密不能"亲眼所见"，必须经泄露 |
| `delay` 存在且 `channel=direct` | ✗ | 亲眼所见没有传播延迟 |

`learnable_by` 的选择器语法见 [可见性强制](../01-内核/02-可见性强制.md)。

### principal_selector

```text
world                      所有主体
faction:<ref>              某势力
role:<ref>                 某职位
self                       该事实所属实体
group_of(<selector>)       某选择器的所属集合
owner_of(<fact_type>)      某事实的 Owner
holder_of(<bon_ref>)       某契约的持有者
```

最多嵌套一层。`group_of(group_of(x))` → 注册失败。

---

<a id="invariants"></a>

## 六、不变式引用

```text
invariant_refs: list<invariant_id>
```

每条 `invariant_id` 必须解析到两类之一：

| 来源 | 形式 |
|---|---|
| 原语内置不变量 | `P1`、`M3`、`H2` …（见 [六原语规格](../02-原语/02-六原语规格.md)） |
| Owner 的跨事实不变式 | 见 [跨事实不变式](../04-Owner/02-跨事实不变式.md) 的 `id` |

### 约束

- `invariant_refs` **必须包含**该原语的全部内置不变量，不得选择性引用。
- 不得引用其它 Owner 的不变式（那是跨 Owner 约束，属于该 Owner）。
- 未解析的引用 → 注册失败（`facttype_invariant_unknown`）。

**为什么内置不变量必须全量引用**：允许选择性引用等于允许声明"这个池可以负数"，正是 H1 要防的。

---

<a id="unknown"></a>

## 七、unknown 策略

```text
unknown_policy: reject | propose | degrade
```

| 值 | 缺输入时的行为 |
|---|---|
| `reject` | 拒绝评估，返回 `rejected` + 原因码 |
| `propose` | 返回 `unknown` + 候选，由 Owner 决定 |
| `degrade` | 用降级模型评估，标 `degraded: true` |

**没有「默认零」这个取值。** 这是全局不变式 5 的字段级落实。

规则包不能覆盖此字段的语义（只能为具体 FactType 选择取值）。

---

<a id="full-example"></a>

## 八、完整示例

### 门扇耐久

```yaml
fact_type_id: fact:facility:gate-03:durability
primitive: pool
identity: entity_ref
owner_ref: ProductionFacility

visibility:
  class: faction
  learnable_by: [ faction:zhaoling-garrison ]
  channel: report
  delay: { model_ref: facility_damage_report_delay@1, params: { base_ticks: 5 } }
  persistence: permanent

resolution_order:
  before: [ [fact:character:*:armor-durability, fact:facility:gate-03:durability] ]

event_schema_ref: pool@v1
invariant_refs: [P1, P2, P3, P4, P5, P6, P7,
                 inv_facility_durability_range]

cadence: event
host: either
aggregation: none
unknown_policy: reject
```

### 城门闩锁

```yaml
fact_type_id: fact:facility:gate-03:latch
primitive: machine
identity: entity_ref
owner_ref: ProductionFacility

visibility:
  class: faction
  learnable_by: [ faction:zhaoling-garrison ]
  channel: direct
  persistence: permanent

resolution_order:
  after: [ fact:facility:gate-03:durability ]

event_schema_ref: machine@v1
invariant_refs: [M1, M2, M3, M4, M5]

state_set_ref: machine_def/gate_latch@1
cadence: event
host: either
unknown_policy: propose
```

### 队伍士气

```yaml
fact_type_id: fact:unit:gate-east:morale
primitive: pool
identity: collection_ref
owner_ref: MoraleFormation

visibility:
  class: faction
  learnable_by: [ faction:zhaoling-garrison ]
  channel: report
  persistence: permanent

resolution_order:
  after: [ fact:character:*:lifestate ]

event_schema_ref: pool@v1
invariant_refs: [P1, P2, P3, P4, P5, P6, P7, inv_morale_bounds]

cadence: window
host: either
aggregation: distribution
refold_model_ref: morale_refold@1        # 不守恒，见聚合与精度
unknown_policy: propose
```

---

<a id="rejection-codes"></a>

## 九、注册期拒绝码汇总

| 码 | 条件 |
|---|---|
| `facttype_id_format_invalid` | 不符合四段格式或长度超限 |
| `facttype_domain_unknown` | `domain` 段无对应 Owner |
| `facttype_identity_scope_mismatch` | `identity` 与 `scope_id` 形式不符 |
| `facttype_primitive_unknown` | 原语不在六种内 |
| `facttype_primitive_missing` | 未声明原语 |
| `facttype_process_kind_invalid` | `process_kind` 出现在非 process 原语上 |
| `facttype_field_primitive_invalid` | 字段与原语不兼容（见 §二 矩阵） |
| `facttype_visibility_missing` | 无 `visibility` |
| `facttype_visibility_combination_invalid` | 违反 §五 组合约束 |
| `facttype_resolution_order_missing` | 无 `resolve_order` 声明 |
| `facttype_resolution_order_cycle` | 偏序有环 |
| `facttype_resolution_order_duplicate` | 同 scope 序重复 |
| `facttype_resolution_order_gap` | 序非稠密 |
| `facttype_invariant_unknown` | 引用了未注册的不变式 |
| `facttype_invariant_incomplete` | 未包含原语全部内置不变量 |
| `facttype_refold_missing` | `aggregation=distribution` 但无 `refold_model_ref` |
| `facttype_step_on_remote_host` | `cadence=step` 且 `host` 非 ue |
| `facttype_selector_nesting_invalid` | `principal_selector` 嵌套超过一层 |
| `facttype_owner_unknown` | `owner_ref` 未注册 |
| `facttype_event_schema_unknown` | `event_schema_ref` 未注册 |
