# 领域模型注册、绑定与 Owner 评估架构

状态：`Guoshang 最新设计基线；模型参数、公式实现和运行时接入仍需逐项验收`

## 1. 结论

领域 Owner 不应把所有玩法规则写成 Owner 内部的固定分支，也不应把所有领域抽象成一个万能模型。正确的结构是：

```text
领域 Owner
  + 领域内可复用的 Numeric / Condition / Hybrid Model
  + 版本化 Static Data
  + Applicability Binding
  + Evaluation Context
  + Owner-specific Effect Mapping
  -> Owner Authority
  -> EventStore / Receipt / Projection / Replay
```

模型可以在**同一事实领域内**通过参数、条件、状态机、适用绑定和效果映射复用，以支持同类但不同的玩法情况；模型不能跨领域取得事实写权，也不能让一个 Owner 变成另一个 Owner。

例如，食品变质和木材腐朽都属于“存储物资状态变化”问题，可以由 Inventory Owner 使用同一类模型运行时承载不同模型；但它们不是同一个模型，也不能直接套用相同参数。Inventory 仍然是唯一提交库存质量、数量和可用性变化的 Owner。

## 2. 模型的三种类型

### 2.1 数值模型 Numeric Model

负责根据固定输入计算数量、比例、进度、损耗、风险或评分。

```text
固定输入 + 版本化参数 + 时间窗口
  -> 数值结果
```

示例：

- 食品质量每日损失；
- 木材含水率和腐朽进度；
- 运输预计抵达时间和损耗量；
- 工坊产能和工时；
- 队伍士气变化；
- 护甲耐久损失和体力消耗。

数值模型不能直接改写世界事实，只能返回数值结果或 Owner-authorized proposal。

### 2.2 条件模型 Condition Model

负责判断资格、门槛、可用性、风险和状态转移条件。

```text
固定输入
  -> true / false / unknown
```

示例：

- 仓库是否具备食品存储能力；
- 粮食是否仍可食用；
- 道路是否可通行；
- 工坊是否满足开工条件；
- 命令是否仍然有效；
- 队伍是否满足撤退条件。

`unknown` 必须是正式结果。缺少输入或输入过期时，不能默认为 `false`、零值或成功。

### 2.3 混合模型 Hybrid Model

负责把条件、数值和状态机组合成一个可回放的领域过程。

```text
条件判断
  -> 数值计算
  -> 阈值/滞回判断
  -> 状态转移
  -> Owner 效果映射
```

示例：

```text
fresh -> at_risk -> spoiled -> unusable
planned -> loaded -> in_transit -> delayed -> delivered
planned -> reserved -> running -> starved -> completed
```

混合模型可以决定“建议进入什么状态”，但最终事实事件仍由拥有该状态的 Owner 提交。

## 3. 领域内泛化边界

模型泛化必须遵循以下边界：

| 可以复用 | 不能复用 |
|---|---|
| 同一领域内的模型运行时、输入校验、单位处理和版本机制 | 跨领域直接复用事实写权 |
| 同类过程的公式结构、状态机结构和参数结构 | 用 Inventory 模型直接写 Politics 或 Body |
| 食品变质、木材腐朽、铁料锈蚀等同类存储损耗模型 | 把不同资源强行套成同一套参数 |
| 不同设施、物资和环境的适用绑定 | 让模型自行决定自己适用于哪些对象 |
| 同一领域内的效果映射模板 | 让模型绕过 Owner 写其他领域事件 |

因此，“换模型”必须理解为：

```text
保留 Owner 的事实、命令和不变量
替换领域内的模型包、参数和绑定
```

不能理解为：

```text
任意模型插入任意 Owner 后自动获得新领域能力
```

## 4. Model Definition

每个模型都必须注册为版本化 Static Data，不允许只在 Owner 代码里隐式存在。

```text
model_id
model_type: numeric | condition | hybrid
model_version
domain_owner_id
input_schema
output_schema
formula_refs
condition_refs
state_machine_ref
effect_mapping_ref
unit_definition
rounding_policy
clamp_policy
missing_input_policy
evaluation_cadence
determinism_policy
invariant_refs
```

关键约束：

1. `domain_owner_id` 必须明确模型归属领域；
2. 模型版本必须可固定、可查询、可回放；
3. 输入和输出必须有 schema 和单位；
4. 缺失输入、过期输入和未知输入必须有显式策略；
5. 随机模型必须固定 seed policy 和算法版本；
6. 模型不能声明其他领域的 canonical writer。

## 5. Applicability Binding

模型本身不决定适用对象。适用关系必须作为独立 Static Data 注册，并允许被设施、政策或运行时状态启用/停用。

```text
binding_id
model_id
binding_version
target_type
target_tags
required_capabilities
required_facility_state
required_scope
active_window
priority
conflict_policy
input_source_contract
binding_revision
```

绑定来源分三类：

1. **类型级绑定**：某类资源默认候选模型，例如 `food` 候选食品变质模型；
2. **设施级绑定**：某个仓库、工坊或道路设施具备特定能力；
3. **运行时绑定**：污染、封存、改造、损坏、政令或安全状态临时启用/停用模型。

模型启用必须同时满足：

```text
目标类型匹配
AND 标签匹配
AND 所需能力存在
AND 作用域匹配
AND 生命周期有效
AND 输入源可读且 revision 有效
```

## 6. Evaluation Context

一次模型评估必须固定输入，不能在计算过程中混用不同时间或不同 revision 的数据。

```text
evaluation_id
owner_id
subject_refs
world_tick
time_window
input_revision_vector
model_version
binding_revision
formula_versions
condition_versions
evaluation_order
seed_policy
budget
```

模型结果至少包含：

```text
evaluation_id
model_ref
input_revision_vector
condition_results
numeric_results
state_transition
proposed_effects
warnings
next_evaluation_time
```

模型结果不是事件。Owner 必须重新校验不变量、权限、当前 revision 和跨域授权后，才能生成事件或授权 fragment。

## 7. 示例：食品变质与木材腐朽

### 7.1 食品仓库

Static Data：

```text
resource:grain:wheat@1
tags: [food, grain]
model_binding: food_spoilage_v3

facility:warehouse:food@1
capabilities: [storage, food_storage]
bindings: [food_spoilage_v3, pest_damage_v1]
```

Inventory 自有 Runtime State 与只读输入引用（温湿度/通风由已登记环境来源或 Facility 提供，必须固定 revision；Inventory 不另造环境事实）：

```text
lot_ref
quantity
quality
age
container_ref
environment_temperature_ref + source_revision
environment_humidity_ref + source_revision
facility_ventilation_ref + source_revision
packaging_state
contamination_state
binding_revision
```

数值模型：

```text
quality_loss = base_rate
             * temperature_factor
             * humidity_factor
             * packaging_factor
             * contamination_factor
             * facility_condition_factor
             * elapsed_time
```

条件/混合模型：

```text
fresh -> at_risk -> spoiled -> unusable
```

只有资源带有 `food` 标签、仓库拥有 `food_storage` 能力且绑定处于有效窗口时，模型才会被 Inventory Owner 选中。

### 7.2 木材仓储

木材可以复用同一个“存储损耗模型运行时”，但使用不同模型包：

```text
model_id: wood_decay_v1
domain_owner_id: inventory
inputs: moisture, exposure, wood_species, treatment, elapsed_time
states: sound -> damp -> decayed -> unusable
```

食品模型不能直接用于木材，因为输入 schema、状态语义、阈值和效果映射都不同。二者共享的是 Inventory 领域的模型基础设施，而不是共享同一业务公式。

## 8. 其他领域示例

### 8.1 Transport

```text
数值模型：路程、速度、负重、抵达时间、损耗
条件模型：道路开放、容量、护送、敌方控制、拦截资格
混合模型：planned -> dispatched -> delayed -> rerouted -> intercepted -> delivered
```

Transport Owner 提交运输阶段；Presence Owner 提交位置/占用；Inventory Owner 提交实际货物损失和入库。

### 8.2 Production

```text
数值模型：产能、工时、原料损耗、质量和产出数量
条件模型：设施、设备、匠人、材料、岗位和许可
混合模型：planned -> reserved -> running -> starved -> completed/failed
```

Production Owner 认证生产过程和产出，不能伪造 Inventory 的原料扣除或 Population 的劳力状态。

### 8.3 Combat

```text
数值模型：命中与伤害评估（Combat）
关联领域分别评估：护甲吸收/耐久（Equipment）、体力成本/身体伤害（Body）
条件模型：距离、朝向、武器可用、目标有效、证据时效
混合模型：windup -> contact -> hit_confirmed -> assessed -> interrupted
```

Combat、Equipment、Body、Status 分别拥有自己的事实，模型可以在同一受控批次中生成授权 fragment，但不能合并事实边界。

## 9. Owner 的最新设计指导

每个 Owner 除原有七部分外，必须增加模型依赖合同：

```text
Model Dependencies
  ├─ allowed_model_types
  ├─ model_registry_scope
  ├─ applicability_binding_scope
  ├─ input_owner_refs
  ├─ output_effect_mapping
  ├─ evaluation_cadence
  ├─ model conflict policy
  ├─ version pin policy
  └─ replay / migration policy
```

Owner 的完整责任变为：

1. 定义自己的 canonical facts；
2. 定义允许哪些模型参与本领域结算；
3. 从 Registry 解析模型和 Binding；
4. 固定模型、条件、Binding 和输入 revision；
5. 调用模型进行评估；
6. 校验权限、不变量和跨域授权；
7. 提交自己的事件和 receipt；
8. 为模型结果提供投影、回放和恢复；
9. 在模型升级时执行版本迁移或保持旧模型回放；
10. 拒绝未注册、越权、过期、冲突或输入不完整的模型评估。

## 10. 不应出现的设计

- 把公式写死在 Owner 的大量 `if/else` 中，导致新情况必须改写 Owner；
- 让调用者直接提交 `next_value`、`quality_loss` 或 `spoiled=true`；
- 只保存 `policy_ref` 字符串，却没有可解析的模型版本和输入合同；
- 把 ConditionRecord 当作 Condition Model；记录状态不等于定义判断规则；
- 让同一领域的多个模型分别使用不同的库存 revision，造成重复扣减；
- 用模型直接产生跨领域事实事件；
- 修改模型后让历史事件按新公式重算；
- 用 `hybrid` 模糊表达执行位置、权威归属和模型组合关系。

## 11. 第一阶段基础设施验收

第一阶段不需要制作所有五阶段内容，但必须用正式 fixture 证明模型基础设施可泛化：

- 同一 Inventory Owner 分别运行食品变质和木材腐朽模型；
- 不匹配的资源标签、设施能力或作用域被拒绝；
- 数值、条件和混合模型均能固定版本并写入评估上下文；
- 模型结果只能通过 Inventory Owner 提交库存事件；
- 公式升级后旧事件仍按旧版本 replay；
- 绑定停用后新窗口不再评估旧模型；
- 两个损耗模型不会在同一库存 revision 上重复扣减；
- 删除投影后可从事件流重建模型导致的库存结果；
- 暂停期间不推进模型评估、tick 或状态转移；
- Bridge 断线、重复投递和未知结果不会重复消费库存。

## 12. 与现有文档的关系

- [01-Owner 分类与 Paralls 实现对照](01-Owner分类与Paralls实现对照.md)：定义 Owner 边界和现有实现状态；
- [02-角色档案、权威状态与心智状态对接](02-角色档案、权威状态与心智状态对接.md)：定义角色档案和状态如何成为模型合法输入；
- [03-数值规则、状态效果与跨 Owner 结算](03-数值规则、状态效果与跨Owner结算.md)：定义公式、条件、效果和跨域事务；
- [02-Guoshang 新 Owner 需求与统一 Command 规范](../02-Guoshang新Owner需求与统一Command规范.md)：定义 Owner 七部分和统一 Command；
- [05-第一阶段县城守城 Demo 设计与执行路线](../05-第一阶段县城守城Demo设计与执行路线.md)：定义第一阶段切片和基础设施阶段门。



## 12. UE 与 Paralls 的模型执行一致性

模型合同独立于宿主。UE 原生与 Paralls 实现必须共享模型/Binding/Static Data 版本、单位/精度、随机算法/seed、稳定顺序及输入 revision，使用固定输入向量验证等价；不默许 C++ 和 Python 各自维护可漂移的同名公式。迁移按时间边界与 authority epoch 交接，历史回放应用已确认事件或固定旧版本恢复，不能用新公式重算旧损耗。

模型评估频率与画面帧率、提交窗口、投影同步和 Agent 决策分别登记，逐域基线见[建设总计划第 11.2 节](../08-基础设施与Owner建设总计划.md#112-全量-owner-的-ue-协作与节奏矩阵)。温湿度、火场/烟雾等共享输入先明确权威来源；未知输入按模型策略返回 unknown/拒绝，不能以“环境模型”绕过领域归属。ESM 适配与否不改变这些规则。
