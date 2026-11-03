# 02-共享 Owner 基类

- 版本：1.0
- 状态：已定义
- 上级：[架构入口](../README.md)
- 对应迁移阶段：阶段 2
- 证据源：`D:\Paralls-phase0-1`，HEAD `c5f249bd`，`backend/app/gameplay/`

本文件是阶段 2 的实施方案。**行为保持重构，不改语义。**

---

<a id="measured-duplication"></a>

## 一、实测重复

不是估算，是逐项统计的结果。

| 重复项 | 数量 | 证据 |
|---|---|---|
| runtime 文件 | 34 个 | `*_runtime.py`，合计 43758 行 |
| 各自的错误类 | 17 个 | `class *RuntimeError(ValueError)` |
| 各自的 `_digest` | 17 份，**5 个不同变体** | 见下 |
| 各自的 `_PRINCIPAL` 常量 | 30+ 处 | 字面量硬编码在类里 |
| 全量投影重建调用 | 55 处 | `rebuild(self._store.read_events())` |

### `_digest` 不是逐字重复（v1.1 更正）

**初版称"17 份都是同一个 sha256 helper"，实测后更正：实为 5 个不同变体。**

| 变体 | 特征 | 模块 | 能否合并 |
|---|---|---|---|
| **A 规范** | 具名 `default`，Mapping 优先 | ownership, equipment, inventory | — |
| **A′ 顺序无关** | `__dict__` 优先于 Mapping | ability | ✓ 已验证等价 |
| **B 宽松** | `default=str`，接受任意类型 | government_treasury, economy | ✓ 已验证等价 |
| **B′ 带前缀** | `"sha256:" + ...` | action_window, civilization_capability, ecology_platform, reference_data | ✗ **输出格式不同** |
| **C 特化** | 显式处理 `Decimal` | modifier | ✗ **收到 Decimal 时不崩溃** |

### 实测的等价性

用 8 组输入（plain / nested / unicode / float / empty / none / Decimal / bytes）逐模块验证：

| 结论 | 模块 |
|---|---|
| 与规范 A **完全等价** | ability、equipment、inventory（3 个） |
| 仅在 Decimal / bytes 上不同，但**这两类值不可达** | contract、credential、debt、economy、gift、government_treasury、land_right（7 个） |
| **输出格式不同**（带 `sha256:` 前缀，71 字符 vs 64） | action_window、civilization_capability、ecology_platform、reference_data（4 个） |
| **必须保留**（Decimal 可达） | modifier（1 个） |

「不可达」的判定依据：

- `contract` / `credential` / `debt` / `gift` / `government_treasury` / `land_right` 源码中不含 `Decimal`，也不含 `bytes`；
- `economy` 含 `bytes`，但 `secrets.token_bytes(32)` 的结果在进入事件前已转成 `.hex()` 字符串。

### 一个必须记录的教训

**C 变体不是冗余代码，它防的是一个真实崩溃。**

实测：把 `StatModifier`（其 `value` 是 `Decimal`）放入摘要输入，

```
modifier 方言 → 成功：2cffcbb68b34ece3
规范 A      → TypeError: Decimal
```

`effective_stats.StatModifier.value` 与 `modifier_runtime.ModifierInstanceState.modifier` 都携带 Decimal，且会经 `__dict__` 进入摘要。**若按初版计划统一成规范 A，modifier 域会直接抛异常。**

这条验证了迁移文档 §二 的原则是必要的：**判据是"差异在不变量与语义"，不是"看起来像重复"。**

### 标准提交前序

7 个 runtime 采用完全相同的四步：

```python
digest = _digest(command)
duplicate = self._duplicate(idempotency_key, digest)
if duplicate is not None:
    return duplicate
projection = self._projector.rebuild(self._store.read_events())
```

`_duplicate()` 的实现也完全一致（`ownership_runtime.py:322-331`）：

```python
record = self._store.get_idempotency_record(self._PRINCIPAL, idempotency_key)
if record is None:
    return None
if record.payload_digest != digest:
    raise XxxRuntimeError("idempotency_key_reused")
result = self._store.get_by_idempotency(self._PRINCIPAL, idempotency_key)
if result is None:
    raise XxxRuntimeError("xxx_idempotency_missing_result")
return result.model_copy(update={"idempotency_status": "duplicate_replayed"}, deep=True)
```

**唯一的差别是异常类名和 message 前缀。** 这一条经 7 域逐行比对确认成立。

---

<a id="append-verdict"></a>

### 逐行比对结论：`_append` 不是重复

原计划把 `_append` 一起抽掉。**逐行比对后否掉了这个计划。** 7 个域实为 7 种形态：

| 域 | 签名 | `pinned_revisions` | `result_digest` | 幂等键 | 特殊行为 |
|---|---|---|---|---|---|
| ownership | 单事件参数 | 包装后 dict | `_digest(event)` | 原样 | — |
| credential | events 列表 | `dict(revisions)` | 直接复用 digest | 原样 | 无 visibility 字段 |
| debt | events 列表 | 前缀映射 `debt_settlement:{stream}` | — | 原样 | **经 `SettlementPlan.from_command_envelope` 构造 `GameplayCommandEnvelope`** |
| equipment | 9 个参数 | 三套不同命名（stream/dict key/前缀） | `_digest(events)` | **`{actor_ref}:{key}` 加前缀** | **提交后触发 `resource_modifier_bridge.sync_equipment_transaction`** |
| gift | transaction_id 参数 | `revisions` | digest | 原样 | **无 `_append` 方法**，内联调用 |
| land_right | — | 三流不同来源 | `_digest(event)` | 原样 | **无 `_append` 方法**，内联调用 |
| contract | 单 revision | `{STREAM: revision}` | digest | 原样 | — |

**四种实质差异**：

1. **幂等键形态不同**：equipment 加 `{actor_ref}:` 前缀，其余原样。这不是风格差异——它决定了不同 actor 的同名 key 是否冲突。
2. **`pinned_revisions` 三套命名约定**：裸 stream / 短名（`"ownership"`）/ 前缀（`debt_settlement:`）。pin 的语义靠字符串约定，没有统一。
3. **`result_digest` 两种算法**：对 `digest`、对 `_digest(event)`、对 `_digest(events)`。同一批事件可能算出不同摘要。
4. **debt 与 equipment 有额外路径**：debt 用 `SettlementPlan` 而非裸 batch；equipment 提交后有副作用。

### 因此修正原方案

`OwnerCommitBuilder` **只能抽共同骨架，不能统一这四项**：

```python
OwnerCommitBuilder.build(
    principal, command_id, transaction_id,
    idempotency_key,          # 由调用方决定是否加前缀
    payload_digest,           # 由调用方决定用哪个算法
    events, expected_stream_revisions,
    pinned_revisions,         # 由调用方构造，不统一命名
    visibility_policies,      # 新增必填，替换硬编码
)
```

builder 只做：组装 dict、填 `outbox_entries: []`、填 `projection_refresh_hints: []`、计算 `event_id` / `transaction_id` 的默认格式。

**统一命名与算法是后续工作，不是阶段 2。** 现在统一会改变幂等语义与 pin 语义，属于行为改变。

### 这条发现提高了阶段 2 的风险评级

原文档把 `_append` 归入"看起来重复、实际不该合并"是**对的**，但当时只是猜测；现在是逐行证据。同时它暴露出：**同一批事件在不同域可能产生不同 `result_digest`**，这会影响幂等重放的正确性，需要单独核查。

---

<a id="what-is-not-duplication"></a>

## 二、看起来重复、实际不该合并的部分

先划清边界，避免把领域规则误抽成机制。

| 看似重复 | 实际 | 处置 |
|---|---|---|
| `_append()` 的 event dict 构造 | 各域的 `event_type`、`payload`、stream 名不同 | 抽**构造器**，保留每域的 payload schema |
| 各域的校验 `if` 分支 | 领域规则 | **不抽**。这是原生 Owner 的核心 |
| `_rejected_append()` | 形态一致但 reason code 不同 | 抽，reason code 作参数 |
| 各域的 projection 类 | 字段完全不同 | **不抽**。只抽重建协议 |
| `MunicipalDrought*` 之类特化命令 | 领域特例 | **不抽**，留在域内 |

**判据**：若两处代码的差异只在常量与类型名，是重复；若差异在不变量与语义，不是重复。

---

<a id="three-modules"></a>

## 三、抽三个模块，不是一个大基类

初始设想是"一个共享基类"。实测后修正为三个职责不同的模块——因为它们的复用方式不同。

```
OwnerRuntimeBase       每次调用都走的前序（命令摘要/幂等/投影）
OwnerCommitBuilder     构造 AtomicEventBatch（纯函数，无状态）
ProjectionCheckpointer 投影增量重建与 checkpoint（有状态，可缓存）
```

### 为什么不是一个大基类

| 模块 | 复用方式 | 若并入基类 |
|---|---|---|
| 前序 | 继承 | 可以 |
| 构造器 | 静态调用，无 `self` | 会强迫所有 Owner 共享同一个 `self` 状态 |
| Checkpointer | 需要按 scope 缓存 | 会强迫所有 Owner 共享同一个缓存生命周期 |

三者生命週期不同，合并会让基类变成"什么都做一点"的对象——正是万能 Owner 的雏形。

---

<a id="module-1"></a>

## 四、OwnerRuntimeBase

```python
class OwnerRuntimeBase:
    PRINCIPAL: ClassVar[str]          # 每域必须覆盖
    STREAM: ClassVar[str]             # 每域必须覆盖

    def __init__(self, *, store: GameplayEventStore) -> None:
        self._store = store

    def _digest(self, value: object) -> str:
        """17 份重复实现归一。"""

    def _duplicate(self, idempotency_key: str, digest: str) -> AppendBatchResult | None:
        """完全一致的幂等重放逻辑。"""

    def _replay(self, command_id: str, idempotency_key: str, digest: str) -> AppendBatchResult | None:
        """前两步合并，减少调用方样板。"""

    def _rejected(self, command_id: str, error_code: str, stage: str) -> AppendBatchResult:
        """统一拒绝回执。"""
```

### 关键约束

| 约束 | 理由 |
|---|---|
| **不提供** 投影重建 | 各域投影类型不同，无法在基类给签名 |
| **不提供** 任何 `if` 判断 | 领域规则必须留在子类 |
| **不提供** event payload 构造 | schema 归各域 |
| 子类可以完全不用基类 | 迁移是渐进的，不强制 |

最后一条很重要：**基类不应成为必须继承的东西。** 它是消除重复的工具，不是新的一层。

---

<a id="module-2"></a>

## 五、OwnerCommitBuilder

从 `ownership_runtime.py:333-337` 的 `_append()` 提炼。那是一个 5 行的密集 dict 构造，被复制到多个域。

```python
@dataclass(frozen=True)
class EventSpec:
    event_type: str
    payload: dict
    schema_version: int = 1

class OwnerCommitBuilder:
    @staticmethod
    def build(
        *,
        principal: str,
        command_id: str,
        idempotency_key: str,
        payload_digest: str,
        stream_id: str,
        events: list[EventSpec],
        expected_revisions: dict[str, int],
        pinned_revisions: dict[str, int] | None = None,
        visibility_policies: list[str] | None = None,
    ) -> dict:
        """构造可直接交给 EventStore.append_batch 的批次。"""
```

### 与现有形态的对应

| 现有 | 新 |
|---|---|
| `transaction_id = f"tx:{command_id}"` | 保持 |
| `event_id = f"evt:{command_id}:{domain}"` | 保持 |
| `stream_revision: 0`、`global_sequence: 0` | 保持（由 store 填） |
| `visibility_policy: "authority_only"` | **改为必填参数** |
| `result_digest` | 由 builder 计算 |

### 顺手修掉的一个洞

现有代码里 `visibility_policy` 是硬编码字面量：

```
"project"          56 处
"authority_only"   46 处
```

**全部硬编码，没有一处来自 FactType 声明。**

这正是 [可见性强制](../01-内核/02-可见性强制.md) 无法落地的原因之一：连写入端都没有统一的来源。改为必填参数后，写入端至少有了单一入口。

这一改动**不改变现有行为**（每域传入它原本硬编码的值），但为阶段 3 的读取端过滤铺路。

---

<a id="module-3"></a>

## 六、ProjectionCheckpointer

### 发现的性能问题

现有模式是**每条命令都全量重建投影**：

```python
projection = self._projector.rebuild(self._store.read_events())
```

`read_events()` 无参数时从 `global_sequence = 1` 开始（`event_store.py:376`），返回全部事件的深拷贝：

```python
return [event.model_copy(deep=True) for event in events]
```

分布：

| runtime | 全量重建次数 |
|---|---|
| `economy_runtime` | 25 |
| `contract_runtime` | 11 |
| `debt_runtime` | 6 |
| `credential_runtime` | 6 |
| `ownership_runtime` | 4 |

**成本是 O(事件总数) 每条命令。** 30 世界日守城会产生大量事件，这会成为明显瓶颈。

### 已有的解药，但没人用

投影类**已经支持** `checkpoint_at` 参数：

```python
def rebuild(self, events, *, checkpoint_at: int | None = None) -> OwnershipProjection:
    if checkpoint_at is None:
        return self._reduce(events)
    prefix = self._reduce([e for e in events if e.global_sequence <= checkpoint_at])
    ...
```

但调用方几乎全部传 `None`。`checkpoint_at=` 只在 5 处出现，且都在特化命令里。

### 设计

```python
class ProjectionCheckpointer:
    """按 (projector, scope) 缓存投影，避免每条命令全量重建。"""

    def get(self, projector, scope: str, head: int):
        """返回 (投影, 是否需要重建)。

        若缓存 revision == head，直接返回缓存；
        否则只读取 (cached_revision, head] 的增量事件并推进。
        """

    def invalidate(self, scope: str) -> None:
        """epoch 变更或迁移时清空。"""
```

### 这条改动的定位

| 项 | 说明 |
|---|---|
| 是否行为保持 | **是**。投影结果完全相同，只改读取范围 |
| 是否属于阶段 2 范畴 | 是。它与基类抽取同属"消除重复机制" |
| 是否必须与基类一起做 | **否**。可独立进行，风险更低 |
| 收益 | 把 O(事件总数) 降为 O(增量) |

**但它引入缓存，缓存带来一致性风险。** 因此建议：基类抽取先做（纯机械），Checkpointer 后做（需要验证）。

---

<a id="migration-order"></a>

## 七、迁移顺序

按风险从低到高。

### 第一批：纯工具归一（低风险）

| 步骤 | 内容 | 状态 | 说明 |
|---|---|---|---|
| 1 | 抽出 `_digest` | **已完成** | 迁移 10 域，保留 5 域，见 §一 |
| 2 | 抽出 `_duplicate` / `_replay` | **已完成** | 迁移 6 域，equipment 按理由保留 |
| 3 | 抽出 `_rejected_append` | **已完成** | 迁移 8 域（全部） |
| 4 | 抽 `OwnerCommitBuilder` | 未开始 | 见下 |

这批**不改变任何控制流**，只是把重复代码移到一处。

### 实际执行结果（2026-11-03）

分支 `refactor/shared-owner-base`，6 个提交：

```
5271d700 fix     幂等回放校验（缺陷修复，与重构分离）
570c04e3 refactor 抽取 owner_runtime_base，首域 ownership_runtime
b0122468 refactor 迁移 10 域到共享 digest
a5fa6491 refactor 5 域改走共享 replay_duplicate
3fa58415 refactor 8 域改走共享 rejected_result
674ab036 refactor fixed_offer_purchase 改走共享 replay_duplicate
```

| 项 | 迁移 | 保留 | 保留理由 |
|---|---|---|---|
| `_digest` | 10 | 4 + 1 | 4 个输出带 `sha256:` 前缀（格式不同）；1 个（modifier）Decimal 可达 |
| `_duplicate` | 6 | 1 | equipment 已含完整回执校验，合并会降低其校验强度 |
| `_rejected_append` | 8 | 0 | 两处差异（stage、transaction_prefix）参数化解决 |

### 一个反复出现的模式

三次迁移都遇到同一件事：**"看起来重复"的代码里，总有一处藏着实质差异**。

| 轮次 | 初判 | 实测 |
|---|---|---|
| `_digest` | 17 份逐字重复 | 5 个变体，其中 modifier 的 Decimal 分支防的是真实崩溃 |
| `_duplicate` | 7 份逐字重复 | equipment 有 8 项额外校验 |
| `_rejected_append` | 同一处差异 | 还多出 `tx:` vs `transaction:` 前缀差异 |

**判据必须逐行实测，不能凭结构相似下结论。** 这条已在三次迁移中各自验证一次。

### 步骤 4 的前置：`result_digest` 已核查完毕

逐行比对发现同一批事件在不同域可能算出不同 `result_digest`：

| 域 | `result_digest` |
|---|---|
| ownership / land_right | `_digest(event)`（单事件） |
| equipment | `_digest(events)`（列表） |
| credential / gift / contract | 直接复用命令 payload 的 `digest` |

**核查结论：不能统一。**

三处证据：

1. **不参与幂等判定**。`event_store.py` 全文 grep `result_digest` 零命中；幂等只看 `payload_digest`（`event_store.py:221`、`:1116`）。
2. **但它是恢复校验字段**，被至少 9 处读取比对：

   | 位置 | 用途 |
   |---|---|
   | `prediction_authority.py:131` | 预测回执与批次一致性 |
   | `resource_body_runtime.py:374`、`:1199` | 资源/身体恢复校验 |
   | `resource_recovery.py:357` | 恢复对账 |
   | `soul_sources.py:182`、`:207` | 灵魂域来源校验 |
   | `population_continuity/recovery.py:44`、`:51` | 连续性恢复 |
   | `services/equipment_command_service.py:309` | 装备命令校验 |
   | `services/equipment_prediction_service.py:86` | 装备预测校验 |

3. 每个域的自校验与自己的算法自洽，因此**当前不出错**；但一旦统一算法，历史事件的恢复校验会全部失败。

所以 `result_digest` 必须由调用方传入，builder 不得代算。

**这条比预想严重**：它不是"风格不统一"，而是"每个域各有一套恢复完整性算法"。统一它属于行为改变，且会破坏历史数据，不在阶段 2 范围内。

### 第二批：投影重建（中风险）

| 步骤 | 内容 | 验证 |
|---|---|---|
| 5 | 抽 `ProjectionCheckpointer`，先在 1 个域启用 | 该域投影结果与全量重建逐字段相同 |
| 6 | 推广到其他域，每次一个 | 同上 |

### 不允许的合并

- ❌ 把领域校验挪进基类
- ❌ 统一各域的 `event_type` 命名
- ❌ 合并各域的 projection 类
- ❌ 统一 `pinned_revisions` 的命名约定（三种约定并存，统一会改变 pin 语义）
- ❌ 统一幂等键形态（equipment 的 `{actor_ref}:` 前缀有实际语义）
- ❌ "顺手"改业务逻辑

---

<a id="verification"></a>

## 八、验证方式

行为保持重构的核心验证是**结果不变**。

```text
对每一批改动：
  1. 记录改动前全部测试结果快照
  2. 执行改动
  3. 运行全量测试
  4. 逐项对比，任何差异 = 失败
```

补充手段：

| 手段 | 用途 |
|---|---|
| 事件 payload 逐字段对比 | 证明 builder 产生完全相同的事件 |
| 投影对象序列化对比 | 证明 checkpointer 结果一致 |
| 固定命令序列重放 | 证明幂等语义未变 |

### 需要的测试基线

现状约 1000 个测试文件。开始前必须确认：

- 全部通过的 commit 作为起点
- 记录通过数量与耗时
- 任一域迁移后，通过数量不得减少

---

<a id="risk"></a>

## 九、风险

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| 隐式行为差异 | 中 | 高 | 逐域对比，不批量改 |
| ~~各域 `_append` 有细微差别未被发现~~ | — | — | **已核实：实为 7 种形态，见 §二** |
| `result_digest` 算法不统一影响幂等 | **中** | **高** | **抽 builder 前单独核查**，见 §七 步骤 4 前置 |
| 基类变成"什么都做" | 中 | 中 | 三个模块分离；基类只做前序 |
| Checkpointer 缓存失效 | 中 | 高 | 缓存在 epoch 变更时强制清空 |
| 大量测试因 import 变化而失败 | 低 | 低 | 保留旧名作为别名 |

**当前最高风险是 `result_digest` 的三种算法并存。** 它可能影响幂等重放的正确性，而幂等被破坏是静默的——重投不会报错，只会产生第二次事实事件。

比 `_append` 形态差异更危险：形态差异是可见的，摘要不一致是不可见的。

---

<a id="what-this-does-not-fix"></a>

## 十、阶段 2 不解决什么

明确边界，防止把阶段 2 当成万灵药：

| 不解决 | 属于 |
|---|---|
| 可见性读取端过滤 | 阶段 3 |
| 三本账时间 | 阶段 3 |
| epoch 栅栏 | 阶段 3 |
| FactType 声明 | 阶段 4 |
| 规则包与管线 | 阶段 4 |
| 零改动新增 FactType | 阶段 5 |

**阶段 2 只做一件事：消除重复。** 它让后续改动只需要改一处，但不改变任何能力。

---

<a id="effort"></a>

## 十一、成本信号

| 批次 | 涉及文件 | 相对成本 |
|---|---|---|
| 第一批（工具归一） | 约 20 个 runtime | 中 |
| 第二批（投影缓存） | 约 8 个 runtime | 中高 |

对比：如果不做阶段 2，阶段 3 的三个洞要各自在 34 个域里改一遍，且每次都要重新理解一遍各域的自定义实现。

**阶段 2 是后续所有阶段的前置减重。**
