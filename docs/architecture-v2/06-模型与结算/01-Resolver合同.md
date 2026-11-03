# 01-Resolver 合同

- 版本：1.0
- 状态：已定义
- 上级：[架构入口](../README.md)

Resolver 是**纯函数**。它计算，不写事实。

---

<a id="definition"></a>

## 一、合同

```text
输入  固定输入（revision 已冻结）+ 版本化参数
输出  EvaluationResult
禁止  读写外部状态、读写事件账、调用 Owner、产生副作用
```

### EvaluationResult

```text
evaluation_id
model_ref
model_version
input_revision_vector
result_status      resolved | unknown | rejected
value              数值结果（若适用）
condition_result   true | false | unknown
state_transition   from → to（若适用）
proposed_effects   [effect_spec]
warnings           [string]
next_evaluation_time
```

**Resolver 结果不是事件。** Owner 必须重新校验不变量、权限、当前 revision 与跨域授权后，才能生成事件或授权 fragment。

---

<a id="writes-fact-types"></a>

## 二、writes_fact_types

每个 Resolver 必须声明它会影响哪些事实类型：

```yaml
model_id: armor_mitigation_v3
model_type: numeric
writes_fact_types:
  - "fact:character:*:armor-durability"
  - "fact:character:*:health"
```

### 校验

```text
每个 writes_fact_types 的 owner_ref
  == 该 FactType 注册时的 owner_ref
```

不等即 `resolver_owner_mismatch`，注册拒绝。

**这条把 v1 的反复禁令变成硬校验**：v1 在四处反复写"模型不能跨领域取得写权"，但没有任何机制阻止它；v2 里它是加载失败。

---

<a id="three-types"></a>

## 三、三种计算形态（保留 v1 分类）

Numeric / Condition / Hybrid **不是事实形状**，是计算形态。与六原语正交。

| 形态 | 输出 | 用途 |
|---|---|---|
| `numeric` | 数值 | 损耗、产能、伤害、进度 |
| `condition` | `true / false / unknown` | 资格、门槛、状态转移条件 |
| `hybrid` | 条件 + 数值 + 状态转移候选 | 组合判定 |

一个 Pool FactType 通常由 numeric Resolver 结算，一个 Machine FactType 通常由 condition Resolver 驱动。**两轴独立**。

### unknown 是正式结果

`condition` 必须返回三值。缺输入、输入过期、输入冲突时返回 `unknown`，**不返回 false、零或成功**。

调用方必须显式处理三值；无法处理时向上传播 `unknown`，不能默认。

---

<a id="hybrid-split"></a>

## 四、Hybrid 要拆开

这是 v2 相对 v1 的实质改动之一。

v1 的反例第八条已经点出隐患：

> 用 `hybrid` 模糊表达执行位置、权威归属和模型组合关系

### 旧形态

```yaml
model_id: food_spoilage_v3
model_type: hybrid
# 一个模型内部同时管：
#   quality 数值衰减
#   fresh → at_risk → spoiled → unusable 状态机
#   elapsed_time 进度
```

问题：一个 hybrid 模型出了偏差，无法判断是数值错了还是状态转移错了；三者共享一个 revision，无法独立回放。

### 新形态

```yaml
# 拆成三个 FactType
fact:lot:wheat-07:quality      pool      numeric resolver
fact:lot:wheat-07:condition    machine   condition resolver
fact:lot:wheat-07:age          process   hybrid resolver（推进）

# 由 L5 管线串联
pipeline: spoilage_chain
  steps: [quality_tick, condition_eval, age_advance]
  atomic: obligation
```

### 收益

| 项 | 旧 | 新 |
|---|---|---|
| revision | 一个 | 三个独立 |
| 可见性 | 一个 | 三个可不同 |
| resolution_order | 无 | 三个可排序 |
| 回放粒度 | 整体 | 逐项 |
| 授权主体 | 一个 | 可按事实分 |
| 定位错误 | 难 | 直接指向出错的事实 |

**表达力一点没丢。**旧设计的 hybrid 模型实际上一直在做管线的事，只是把它藏在了一个模型里。

---

<a id="data-vs-code"></a>

## 五、两类模型，同一张注册表

原生 Owner 的规则不可能全变成数据。因此注册分两类，**但注册表是同一张**：

| | 托管 Owner 的模型 | 原生 Owner 的模型 |
|---|---|---|
| 实现 | 包内数据（参数 + 表 + 曲线） | Python / C++ 代码 |
| 注册内容 | 同左 | `model_id` + `input/output_schema` + `determinism_policy` + `writes_fact_types` |
| 版本固定 | 包版本 | 代码版本号 |
| 双端等价 | 固定向量验证 | 同样需要验证 |

这样"模型不允许只在代码里隐式存在"这条守住了，同时不逼着把政治承认写成配置。

---

<a id="determinism"></a>

## 六、确定性

所有 Resolver 必须声明：

```yaml
determinism_policy:
  numeric_precision: fixed_point | decimal | float64
  rounding: half_up | floor | truncate
  iteration_order: resolution_order    # 唯一允许值
  random: none | seeded
  seed_source: world_tick | command_id  # 若 seeded
```

### 禁止项

| 禁止 | 原因 |
|---|---|
| 遍历 `dict` / `unordered_map` | Python 与 C++ 顺序不同 |
| 浮点比较 | 平台差异 |
| 系统时间 | 不可回放 |
| 未固定 seed 的随机 | 不可回放 |
| 读取全局可变状态 | 批次间不一致 |

最容易被忽略的是第一条：**遍历顺序必须来自注册表的顺序表，不能来自容器的自然顺序。**

---

<a id="missing-input"></a>

## 七、缺失输入策略

```yaml
missing_input_policy: reject | propose | degrade
```

| 值 | 行为 |
|---|---|
| `reject` | 拒绝评估，返回 `rejected` + 原因 |
| `propose` | 返回 `unknown` + 候选，交由 Owner 决定 |
| `degrade` | 用降级模型评估，标记 `degraded: true` |

**没有"默认零"这个选项。** 这条是 L1 原语 `unknown_policy` 在 Resolver 侧的对应。

---

<a id="registration"></a>

## 八、注册校验

```text
resolver_writes_undeclared     输出事实类型未在 writes_fact_types 声明
resolver_owner_mismatch        writes_fact_types 的 owner ≠ FactType 的 owner
resolver_input_undeclared      读取了未在 reads 声明的 FactType
resolver_missing_determinism   未声明确定性策略
resolver_not_pure              声明了副作用
```

---

<a id="acceptance"></a>

## 九、验收

| # | 用例 | 期望 |
|---|---|---|
| R1 | 模型输出未声明的事实类型 | 注册拒绝 |
| R2 | 模型声明写其它 Owner 的事实 | 注册拒绝 |
| R3 | 条件缺输入 | 返回 `unknown`，不返回 false |
| R4 | 同输入跑两次 | 结果逐位相同 |
| R5 | C++ 与 Python 跑固定向量 | 结果相同 |
| R6 | 模型升级后回放旧事件 | 用旧版本，不用新公式 |
| R7 | Resolver 内访问系统时间 | 注册拒绝 |
