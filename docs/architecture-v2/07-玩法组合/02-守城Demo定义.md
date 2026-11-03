# 02-守城 Demo 的组合定义

- 版本：1.0
- 状态：已定义
- 上级：[架构入口](../README.md)

本文件把县城守城 Demo 表达成一份 `play_pattern`。**它不是新 Owner，不是新 runtime。**

---

<a id="pattern"></a>

## 一、整体

```yaml
play_pattern_id: county_siege@1
content_refs:
  - han_realistic@2.1
  - zhaoling_siege_tuning@1.0
reactions:
  - casualty_to_morale
  - gate_breach_to_presence_reeval
  - supply_low_to_survival_pressure
  - commander_down_to_succession
  - messenger_lost_to_order_expired
  - report_arrival_to_knowledge_update
  - control_shift_to_objective_eval
pipelines:
  - impact_soldier
  - impact_gate
  - impact_siege_engine
  - impact_wall
workflows:
  - reinforcement_request
  - siege_supply_relief
  - medical_treatment
  - gate_repair
  - wall_reinforcement
```

---

<a id="reactions"></a>

## 二、七条 reaction

### 1. casualty_to_morale

```yaml
on: { fact_type: "fact:character:*:lifestate", transition_to: dead }
when: morale_relevant_casualty@1
emit:
  command: recompute_morale
  target: { scope: "group_of(subject)" }
```

**为什么异步**：个人 scope → 队伍 scope，跨 scope 不能同批次。

### 2. gate_breach_to_presence_reeval

```yaml
on: { fact_type: "fact:facility:gate-*:integrity", threshold_crossed: breach }
emit:
  command: reevaluate_passability
  target: { scope: "gate-03" }
```

**关键**：完整度破口后**不自动改通行性**。Presence 独立评估后提交。这是 v1 正确判断的保留。

### 3. supply_low_to_survival_pressure

```yaml
on: { fact_type: "fact:county:*:grain-days", below: 3 }
emit:
  command: raise_survival_pressure
  target: { scope: "garrison:zhaoling" }
```

### 4. commander_down_to_succession

```yaml
on: { fact_type: "fact:character:*:lifestate", transition_to: incapacitated_or_dead }
when: is_commander@1
emit:
  command: start_succession
  target: { scope: "owner_of(subject)" }
```

### 5. messenger_lost_to_order_expired

```yaml
on: { fact_type: "fact:character:*:lifestate", transition_to: dead }
when: is_carrying_order@1
emit:
  command: expire_order
  target: { scope: "order_of(subject)" }
```

### 6. report_arrival_to_knowledge_update

```yaml
on: { fact_type: "fact:information:*:report", event: report_delivered }
emit:
  command: update_knowledge
  target: { scope: "recipient_of(subject)" }
```

这条是**有限知情**的核心：军情到达前玩家不知道，到达后才进入投影。

### 7. control_shift_to_objective_eval

```yaml
on: { fact_type: "fact:county:*:control", event: control_transferred }
emit:
  command: evaluate_objective
  target: { scope: "objective:zhaoling" }
```

Objective 只读已确认事实，不写控制权。

---

<a id="pipelines"></a>

## 三、四条 pipeline

| 管线 | 层数 | atomic | 说明 |
|---|---|---|---|
| `impact_soldier` | 5 | true | 盾→甲→部位→生命/伤势→流血→生命周期 |
| `impact_gate` | 4 | obligation | 门扇→门闩→完整度→通行性（跨宿主） |
| `impact_siege_engine` | 3 | true | 防护棚→结构→残骸 |
| `impact_wall` | 3 | true | 墙体完整度→垛口→通行 |

`impact_gate` 标 `obligation` 而非 `atomic`，因为通行性在 UE、耐久在 Paralls。**这是显式声明，不是运行时判断。**

---

<a id="workflows"></a>

## 四、五个 workflow

### reinforcement_request（求援）

```yaml
steps:
  - authorize:    government.issue_relief_order
  - dispatch:     dispatch.issue_order          depends: [authorize]
  - relay:        presence.move_to              depends: [dispatch]
  - deliver:      dispatch.confirm_delivery     depends: [relay]
  - accept:       organization.accept_command   depends: [deliver]
  - march:        transport.create_shipment     depends: [accept]
  - arrive:       presence.arrive               depends: [march]
timeout: 30 world days (per content)
```

**关键**：受理不等于送达，送达不等于接受，接受不等于执行。四个状态分离。

### siege_supply_relief（补给）

预留 → 运输 → 入库，每步独立 receipt，中断保留已消费。

### medical_treatment（医疗）

校验 → 预留药材 → Body 结算 → Status 解除。Workflow 不写生命、不写库存。

### gate_repair / wall_reinforcement（修缮）

工单 → 材料预留 → 工时推进 → 完整度恢复 → 材料消耗。

---

<a id="what-demo-proves"></a>

## 五、这份定义证明了什么

| 架构主张 | Demo 中如何验证 |
|---|---|
| 同一原语结算不同类型的实体 | `impact_soldier` 与 `impact_gate` 共用 Pool / Machine |
| 新增可受伤实体只需数据 | 加 `impact_wall` 零代码 |
| 过程原语复用 | 求援、补给、修缮用同一 Process |
| 跨 Owner 组合 | 命中 → 士气 → 阵型（异步链） |
| 聚合精度 | 队伍士气用 distribution，个体士气用 none |
| 有限知情 | `report_arrival_to_knowledge_update` |
| 分域不代写 | 门破不自动改通行性 |

---

<a id="what-demo-does-not-prove"></a>

## 六、这份定义**不**证明什么

诚实说明，避免过度宣称：

| 不证明 | 原因 |
|---|---|
| 玩法有趣 | 架构正确性 ≠ 好玩，需试玩 |
| 性能达标 | 需基准测试 |
| 五阶段可扩展 | 需十三州规模的容量验证 |
| 规则密集领域可托管 | Dispatch / Politics / Economy 仍是原生 Owner |
| 双端等价 | 需固定向量执行证据 |

---

<a id="acceptance"></a>

## 七、Demo 验收（沿用 v1 的四项）

一个切片只有在以下四项**同时**成立时才算完成：

1. 玩家能做出选择
2. 世界产生后果
3. 玩家能看到后果
4. 系统能解释后果

**只完成接口、假数据或单元测试，不算切片完成。**

---

<a id="evidence"></a>

## 八、需要的证据

| 证据 | 形式 |
|---|---|
| 零改动新增 FactType | 分水岭实验的运行记录 |
| 同批次与分阶段结果一致 | 固定向量对比 |
| 门破不改通行性 | 事件流展示 |
| 报告延迟生效 | 时间线截图 |
| 全链路可回放 | checkpoint + replay 演示 |
| PIE 可玩 | 截图（非桌面截图） |
