# 05-Owner 重构影响评估与适配方案

- 版本：1.0
- 状态：已定义（评估已完成，适配未开始）
- 评估日期：2026-11-04
- 上级：[架构入口](../README.md)
- 基线：`origin/main` @ `d77d9db6`（代码 82,305 行 / 35 个 `*_runtime.py`）
- 依据：四项独立调研（Owner 间耦合 / 群体模拟 / 角色智能体 / 司命）

---

<a id="headline"></a>

## 一、结论摘要

### 1.1 三条主结论

**结论一：分层本身不贵，补三条空合同才贵。**

原型已验证：`owner_runtime_base.py` 被 15 个 runtime 采用后净减 275 行。管道层（幂等、revision、receipt 的重复）收敛成本很低。

真正贵的是三件**从未真正实现**的事：

| 合同 | 现状 | 证据 |
|---|---|---|
| **投影** | 205 处 `rebuild()`，91.7% 全量重建；gameplay 内仅 2 处真增量 | 全量 `read_events()` 扫描 304 处 |
| **revision 校验** | `pinned_revisions` 333 处，但 `event_store` 里出现 0 次 | 从不与实际 revision 校验 |
| **可见性** | 字段存在，读取端不查 | `event_store.py` grep 零命中 |

**这三条在 v2 里是 L0 的强制项。落地它们是"补上从未实现的能力"，不是"新增功能"。**

**结论二：存在三个"第二真相"，重构会放大它们。**

| # | 第二真相 | 位置 | 规模 |
|---|---|---|---|
| 1 | **B0 热表**：6 个字段直接写入，无 Owner、无事件、无 receipt | `world.py:780-788`、`hot_state.py:44-339` | 自建列式存储 + revision 域 + 原子批次 |
| 2 | **司命 Heavenly Graph**：`*` 通配订阅复制全部 gameplay 事件 | `main.py:2229`、`authority_graph_projector.py:43` | revision 用 `max(payload, producer_ts)` 混推 |
| 3 | **司命三套状态副本**：state tree / situation layer / narrative core | `siming_state_tree.py:9`、`siming_global_situation.py:105` | 均无 `source_owner` / `source_revision` |

**这三处在引入分层后不会自动消失，反而会因为"多了一层声明"而更难对齐。必须先收口。**

**结论三：三个智能体底座与 Owner 的耦合方式完全不同，适配策略不能统一。**

| 底座 | 耦合形态 | 适配难度 | 关键断点 |
|---|---|---|---|
| **群体模拟** | 自有第二真相 + 三条读取路径并存 | **高** | B0 热表无 Owner 归属 |
| **角色智能体** | 通过 8 key 的 descriptor 白名单 | **中**（但失败是静默的） | L3 候选集会塌空 |
| **司命** | 事件订阅 + 字符串前缀推断 | **中** | `DOMAIN_BY_EVENT_PREFIX` |

---

<a id="coupling-map"></a>

## 二、当前耦合全景

### 2.1 Owner 之间的耦合

**41 条 runtime→runtime 依赖边，0 个循环依赖**（DAG 可拓扑排序）。这是好消息：分层有确定的顺序。

最大的三个枢纽：

| Owner | 被几个 Owner 读 | 特点 |
|---|---|---|
| `inventory` | **9** | 签名一改，全库连锁 |
| `economy` | **8** | 59 个事件类型，31 处 `rebuild()`（全库最多） |
| `organization_government` | 10 个外部事件前缀 | 7,077 行，68 个事件类型，同时是最大读取方 |

`construction_production` 特殊：读 4 个但被 6 个读，是双向枢纽。

**三处绕过封装的穿透**：

| 位置 | 内容 |
|---|---|
| `ecology_runtime.py:25` | 跨 Owner import `economy_runtime._take_weather_quote_admission_issuer` |
| `construction_production_runtime.py:54` 等 3 处 | import `patch_runtime._canonical_digest` |
| `organization_government_runtime.py` 等 | 13 处函数内延迟 import，掩盖依赖 |

### 2.2 机制重复的量化

| 机制 | 重复份数 | 收敛成本 |
|---|---|---|
| `_digest` | 17 份，**3 套规范** | 低（已验证） |
| `_duplicate` | 8 份，7 份互不相同 | 低（已验证） |
| `_rejected_append` | 8 份，其中 4 份逐字节相同 | 低（已验证） |
| 池/预留 | **4 套**（inventory / economy / resource_body / commerce） | **高** |
| 状态机迁移校验 | 2 套独立实现 | 中 |
| receipt 类 | 11 个 | 中 |

**管道层便宜，语义层贵。** 这个区分贯穿整个评估。

### 2.3 语义不一致（重构成本主体）

| 项 | 不一致点 |
|---|---|
| `result_digest` | 3 类前缀（裸 hex / `sha256:` / 手工拼）+ 5 种摘要对象 |
| `pinned_revisions` | 2 套键名（逻辑名 vs 真实 stream_id），约 24 处混用；**且从不被 store 校验** |
| `idempotency_key` | 8 处加 `{actor}:` 前缀，其余不加；key 模板至少 25 种 |
| `transaction_id` | `transaction:` 96 处 vs `tx:` 4 处 |

---

<a id="three-truths"></a>

## 三、必须先解决的三个第二真相

### 3.1 B0 热表

**现状**：群体模拟自建了一个列式存储，直接写 `fatigue` / `need_pressure` / `starvation_credit` / `activity_phase` / `next_due_tick` / `last_update_tick`。

```python
world.py:780-788  commit_batch_atomic(...) 直接改字段
hot_state.py:109-130  自建 revision 域
hot_state.py:187-226  自建原子批次
```

**为什么不引入分层也会出问题**：

这六个字段在 Owner 侧**没有对应事实**：

| B0 字段 | Owner 侧对应 |
|---|---|
| `fatigue` | Survival 的 `NeedState` 是 `need_ref/value/last_tick`，语义不同 |
| `need_pressure` | 无 |
| `starvation_credit` | 无 |
| `activity_phase` | 无对应状态机 |

**引入分层后**：若把 `fatigue` 声明为 `pool`，B0 会往私有槽写与 Owner pool 并行的值，且 revision 域不同 → **双真相 + 冲突**。

**处置**：必须先给这六个字段定 Owner 归属，再谈分层。

### 3.2 司命 Heavenly Graph

**现状**：`main.py:2229` 用 `*` 通配订阅**全部** gameplay 事件，由 `authority_graph_projector.py:43` 复制成图节点。

```python
# 全仓唯一的 Owner → 司命 投影适配器
authority_graph_projector.py:22-32  DOMAIN_BY_EVENT_PREFIX
  靠 "gameplay.inventory." 这类字符串前缀推 Owner domain
```

revision 用 `max(payload_revision, producer_ts)` **混推**，与 Owner 真 revision 不同源。

**处置**：这个前缀表换成 FactType → projection contract 声明，是**最小改动、最大收益**的一处。同时把 `*` 订阅改为按 FactType 订阅。

### 3.3 司命的三套状态副本

| 副本 | 位置 | revision |
|---|---|---|
| `InMemorySimingStateTree` | `siming_state_tree.py:9` | 无 |
| `SimingGlobalSituationLayer.snapshots` | `siming_global_situation.py:105` | 无，且**从未接线** |
| `SimingNarrativeCore` | `siming_narrative_core.py:18` | 仅自身 +1 |

全部无 `source_owner` / `source_revision` / 对账机制。

**处置**：新建 `OwnerFactQuery` 端口，三套都改吃它。

---

<a id="breakpoints"></a>

## 四、断点清单（按底座）

### 4.1 群体模拟

| # | 断点 | 位置 | 失败形态 |
|---|---|---|---|
| G1 | B0 六个字段无 Owner 归属 | `world.py:780`、`continuous.py:58-110` | 双真相 + revision 冲突 |
| G2 | `activity_phase` 是未声明状态机，允许集合硬编码 4 处 | `continuous.py:24-30`、`hot_state.py:338` 等 | 4 处本地定义与声明层重复 |
| G3 | 到期判定是未声明 process，与 `ScheduledObligation` 两套并存 | `hot_state.py:342-421`、`obligations.py:277` | 本地堆无合法归属 |
| G4 | 读侧按**事件类型白名单**而非 FactType | `store_projection_assembler.py:122-128` | **静默漏读，无报错** |
| G5 | 准入是字符串黑名单 | `inventory_owner_adapter.py:22-24` | 新字段名需人工加，否则透传 |
| G6 | principal / event_family 全是字面量（21 处 `_PRINCIPAL`） | `batch.py` 等 | 声明层接管后静默走旧路径 |
| G7 | `settlement_participant_scope` 单值 | `inventory_owner_adapter.py:156-177` | 多 FactType 参与者需升 schema |
| G8 | 恢复 digest **哈希源码文本** | `recovery.py:20-29` | 实现重构即让历史 checkpoint 全部失效 |
| G9 | B0 delta 用 `difference(HOT_FIELDS)` 拒绝未登记字段 | `siming_contracts.py:159` | 新增原语被硬拒 |

**G8 特别值得注意**：它对 `continuous.py/hot_state.py/world.py` 等源码取 sha256。任何实现改动都会让历史 checkpoint 失效。**这会在重构期间制造大量假阳性失败。**

### 4.2 角色智能体

> **2026-11-04 复核并修订。** 原始条目按 `origin/main` @ `d77d9db6` 记录，行号与实际代码不符，A1 的因果链也已修正。**0.5.1 / 0.5.2 / 0.5.3 已在 `refactor/shared-owner-base` 落地并通过回归对照**（见五、阶段 0.5）。

| # | 断点 | 位置 | 失败形态 | 状态 |
|---|---|---|---|---|
| A1 | **`supported_intents` 的空列表哨兵** | `l3_planner.py:122,134,215`（三处白名单已收敛为常量）+ `:449` 选择逻辑 | **L3 候选集静默塌空** | ✅ 0.5.1 已收口 |
| A2 | presence 裸 `character_ref` 匹配 + 全函数单 `except` | `combat_target_catalog.py:26-37` | 静默 `return []`，**整角色目录清零** | ✅ 0.5.3 已收口 |
| A3 | ESM 私有 mini-machine | `esm_service.py:151`（16 个 `machine_id`） | `machine+holding+place` 手写特例；`get_state_machine_template` **全仓无外部调用者** | 暂不动（未接线资产） |
| A4 | revision 假设 `int` | `l4_executor.py:332` `int(value)` | 当前两端都是 `int`，**不会抛错**；风险只在未来换类型时兑现 | 暂不动，建议加类型契约测试 |
| A5 | 两套声明口径并存 | `StateGroupRegistry` vs FactType | **全仓 0 处 `FactType`** —— 不是"两套并存"，是新的那套尚未落地 | 表述已修正，阶段 3 可选目标 |
| A6 | 角色侧直写 store | `learning_authority.py:241` `append_batch` | **不是 bug**：`authority:character:learning` 是刻意的 learning grant 权威；风险是绕过 Owner revision 校验 | 中期包进 `OwnerFactQuery` 写端口 |

**A1 的机制与旧描述不同。** 真实因果链：

```
生产者写 supported_intents=[]（falsy 但 key 存在）
→ "supported_intents" in item 为真，intent in [] 为假
→ 所有 target-required（14 个）意图都被 strip
→ 只剩 [None] 兜底 → diagnosis=blocked:"target_required"
→ 全 prune → P 为空 → 只能选 observe
```

条件 key 不在白名单**不会**导致塌空——它在 `:134` 已注明只影响描述文本，不产生 diagnosis。真正的杀手是 `[]` 与"未声明=全支持"的缺省语义冲突。**旧描述的"条件 key → unknown"推导是错的。**

**A2 的故障范围比旧描述更大。** `presence` 用 `row.payload.get("character_ref") == actor` 只匹配完整 `character:x` 拼写，而同函数内 `life` 已用 `{actor, actor.removeprefix("character:")}` 双拼写。一旦拼写不符，`next()` 抛 `StopIteration`，被整个函数的 `except` 吞掉，返回 `[]`——**同角色所有其他目标一并消失**，不是单个目标消失。

### 4.3 司命

| # | 断点 | 位置 | 失败形态 |
|---|---|---|---|
| S1 | 硬编码 3 个 payload 键名 | `siming_state_tree.py:36-42` | 读不到事实 |
| S2 | `event_type` 字符串白名单 | `siming_observe.py:6-14` | 与 FactType 枚举无对应 |
| S3 | **字符串前缀推 Owner domain** | `authority_graph_projector.py:22-32` | 全仓唯一适配器，必重写 |
| S4 | 固定 node_type 注册表 | `heavenly_graph_semantics.py:22-38` | |
| S5 | `WorldFactMemoryEntry` 无 `fact_type_ref` | `siming_heavenly_memory.py:45-51` | |
| S6 | 资格判定只认 actor id | `siming_policy.py:37-41` | |
| S7 | `siming.environment_request` 死路径 | `siming_event_producer.py:146` | 无订阅者 |
| S8 | `char_b` 硬编码 | `siming_runtime.py:1497,1523,1924` | 绕过 roster |

**可原样保留**：`siming_contracts.py` 全族（已带 revision_vector + digest）、`owner_adapters.py` 三个 adapter、`siming_coordinator.py`。**这些已经是正确的接缝。**

---

<a id="adaptation-order"></a>

## 五、适配顺序

顺序由依赖决定，不由难度决定。

### 阶段 0：收口第二真相（前置，不可跳过）

| 步 | 内容 | 为什么必须最先 |
|---|---|---|
| 0.1 | 给 B0 六个字段定 Owner 归属 | 否则分层永远留第二真相 |
| 0.2 | `*` 通配订阅改为按 FactType 订阅 | 否则第二本账随重构放大 |
| 0.3 | `recovery.py` 的源码哈希改为语义指纹 | 否则重构期间 checkpoint 全失效，无法区分真假失败 |

**0.3 是一个容易被忽略但影响巨大的前置**：如果不改，每次重构都会让大量恢复测试失败，而这些失败是假的。

### 阶段 0.5：角色侧静默失败收口（已落地）

**插在 0.3 与 1.1 之间的独立阶段。** 原计划把 A1/A2 归入阶段 1.1，与 FactType 适配器一起做；复核后改为主张提前，理由：

- 0.5 三步**不依赖 FactType，也不依赖 B0 收口**，只动 `l3_planner.py` 与 `combat_target_catalog.py`，fan-out 是全部断点里最低的。
- A1 属于"系统健康但角色不动"，与 G8 源码哈希一样是**假信号源**——它会持续污染后续每一次重构的失败判读。若不先修，1.1 落地时无法区分"FactType 接错了"和"候选集本来就塌了"。

| 步 | 内容 | 依赖 |
|---|---|---|
| 0.5.1 | 三处白名单收敛为模块常量；`supported_intents` 语义显式化；新增 `perception_only` 表达"可感知但不可行动" | 无 |
| 0.5.2 | 候选集 `observation_only` / `empty_presented` 地板 + `candidate_floor` 接入冻结输入 | 无 |
| 0.5.3 | `combat_target_catalog` 按目标粒度隔离异常；presence 双拼写；stream 名收敛；`last_rejected` 记录 | 无 |

**关键设计约束（落地时确立，1.1 必须遵守）**：

1. **`floor` 不进 `digest`。** `runtime_trace_export.py:78-82` 用四键重算 `candidate_digest`；把 `floor` 并入会让所有历史与当前 trace 判 `compilation_digest_mismatch`。因此 `floor` 是独立字段 + 独立 context 键，`diagnostics` 保持"只记候选级原因"的原语义（已有测试精确断言其长度）。
2. **`supported_intents=[]` 不再是"感知但不可行动"的表达方式。** 改为显式 `perception_only=True`；空列表且无该标记＝生产者契约违约，会以 `target_action_not_supported` 被可见地 prune。
3. **感知目标只保留 visibility 条件。** 继承生产者的 `range: unknown` 会让它在条件阶段被 `condition_unknown` 剪掉，真实原因被掩盖。

**验收**：`test_character_candidate_compiler.py` 新增 5 项（感知目标以原因进 pruned、空列表缺陷可见、两类地板、可行动候选抑制地板）；改动前后 75 个既有失败逐项一致，零新增。

### 阶段 1：建立唯一适配器（先于任何 FactType 落地）

| 步 | 内容 | 位置 |
|---|---|---|
| 1.1 | **descriptor 适配器**：FactType 事实 → 现有五元组 | 在此基础上扩展（A1/A2 已由 0.5 收口） |
| 1.2 | `OwnerFactQuery` 端口 | 收口 S1/S2/S5 |
| 1.3 | `authority_graph_projector` 前缀表 → FactType 声明 | 收口 S3 |

**1.1 是关键**：把 `supported_intents / required_conditions / affordance_result.status / owner_route / target_revision_vector` 五元组的来源从硬白名单换成 FactType 声明，且**声明集合可扩展**。0.5.1 已把前两项的来源从内联字面量收敛为模块常量与 `perception_only` 契约，1.1 在这一层之上升级来源，而不是重做扩展点。

### 阶段 2：管道层收敛（低风险，可并行）

| 步 | 内容 | 已证 |
|---|---|---|
| 2.1 | `_digest` / `_duplicate` / `_rejected_append` 归一 | ✓ 原型已验证 |
| 2.2 | 统一 `pinned_revisions` 语义并接入 store 校验 | 需先定语义 |
| 2.3 | 统一 `idempotency_key` 命名空间规则 | 需逐域确认 |

**2.2 是新发现的缺陷**：`pinned_revisions` 333 处但从不校验。补上它属于"修缺陷"，会改变现有行为，需单独评估。

### 阶段 3：FactType 试点（低 fan-out）

| 建议 | 理由 |
|---|---|
| `debt_runtime` | 954 行，`_duplicate` 已是逐字节复制品 |
| `credential_runtime` | 272 行，fan-out 低 |
| `ownership_runtime` | 367 行，`active_right_by_asset` 单值映射是已知缺陷 |

**不要先动 `inventory` / `economy` / `organization_government`。** 它们是三大枢纽，试点失败会连锁。

### 阶段 4：语义层收敛

池的 4 套实现收敛为 1 套。这是最贵的一步，且必须在试点验证 FactType 契约之后。

### 阶段 5：枢纽迁移

按依赖反序：先被依赖少的，后被依赖多的。

---

<a id="why-order-matters"></a>

## 六、为什么顺序不能颠倒

三个反例，每一个都会导致返工：

| 若先做 | 会发生什么 |
|---|---|
| 先建 FactType 再收口 B0 | B0 的 6 个字段无 Owner 可声明，被迫发明一个 |
| 先动 inventory（枢纽）再试点 | 9 个 Owner 连锁失败，无法定位是试点错还是枢纽错 |
| 不改 `recovery.py` 源码哈希先重构 | 每次改动都让大量恢复测试失败，真假难辨 |

---

<a id="cost"></a>

## 七、成本信号

| 阶段 | 相对成本 | 说明 |
|---|---|---|
| 0 收口第二真相 | 中 | 3 处，但每处都需要设计决策 |
| 1 唯一适配器 | **中高** | 3 个端口，但决定后续一切 |
| 2 管道收敛 | 低 | 原型已证净减 275 行 |
| 3 试点 | 中 | 3 个低 fan-out runtime |
| 4 语义层 | **高** | 池的 4 套归一 |
| 5 枢纽迁移 | **最高** | 三大枢纽，回归面最大 |

**注意**：`organization_government_runtime.py` 单文件 7,077 行、68 个事件类型，占全部重构面约 1/4。

---

<a id="what-not-to-do"></a>

## 八、明确不做的事

| 不做 | 理由 |
|---|---|
| 重写 34 个 runtime | 成本收益相反，且它们承载了业务逻辑 |
| 把原生 Owner 改成托管 | Dispatch/Politics/Economy 的规则无法数据化 |
| 在阶段 0 之前引入 FactType | 会把第二真相固化进声明层 |
| 一次性迁移全部域 | 回归风险不可控 |

---

<a id="open-questions"></a>

## 九、需要裁决的事项

### 9.1 必须你定

| # | 问题 | 影响 |
|---|---|---|
| Q1 | **B0 六个字段的 Owner 归属** | 决定阶段 0 能否开始 |
| Q2 | **第二本真相账（Heavenly Graph）现在就砍还是保留** | 决定司命适配策略 |
| Q3 | `pinned_revisions` 补上校验是否算"行为改变"，需不需要单独评审 | 影响阶段 2.2 |

### 9.2 技术判断（可自行决定）

| # | 项 | 建议 |
|---|---|---|
| T1 | 试点选 `debt` / `credential` / `ownership` | 低 fan-out + 逐字节重复 |
| T2 | `recovery.py` 源码哈希改语义指纹 | 必须改 |
| T3 | descriptor 五元组可扩展化 | 必须做 |

---

<a id="acceptance"></a>

## 十、验收

迁移完成的判据不是"全部测试通过"——[已知基线失败清单](../09-验收/06-已知基线失败清单.md) 记录基线就有 201 个失败。

正确判据：

```
1. 相对基线无新增失败
2. 三个阶段门各自的专项证据
3. 三个第二真相收口后，能证明"从 Owner 事实重建"而非"从私有副本重建"
```

第三条是最本质的：**如果删除所有私有副本后系统仍能重建，才算真正收口。**
