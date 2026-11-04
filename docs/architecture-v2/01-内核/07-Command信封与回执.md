# 07-Command 信封与回执

- 版本：1.0
- 状态：已定义
- 上级：[架构入口](../README.md)
- 前置：[权威栅栏与提交](03-权威栅栏与提交.md)、[事件 schema 规格](../02-原语/04-事件schema规格.md)

本文件补齐 v2 的一处内部不自洽：32 处引用命令字段，但没有一处定义信封结构。

---

<a id="three-objects"></a>

## 一、三个对象必须分开

```text
Intent    角色主观上想做什么        agent_private，不是事实
Command   请求系统执行什么          经 Gateway，是请求不是事实
Event     Owner 已确认发生了什么    世界真相
```

典型对照：

| 层 | 内容 |
|---|---|
| Intent | 「我想让东队撤回」 |
| Command | `withdraw_unit(unit:gate-east)` |
| Event | `place.departed{holder:gate-east, from:gate-03}` |

**动画播放、角色说话、群体模拟产出候选，都不能直接成为 Event。**

---

<a id="envelope"></a>

## 二、信封

### 完整字段

```text
command_id            str              全局唯一
command_type          str              见 §三
command_version       int ≥ 1          该命令类型自身的版本
source_kind           enum             见 §四
principal_ref         ref              谁发起的（权限主体）
actor_ref             ref?             实际执行者（可与 principal 不同）
subject_ref           ref?             命令作用于谁（如受令的队伍）
target_refs           list<ref>        目标实体/事实
control_mode          enum             见 §五
payload               object            命令类型定义的参数
expected_revisions    map<ref,int>      期望的 revision，必填
read_set_revisions    map<ref,int>?     读取的其它事实 revision
evidence_refs         list<ref>?        支撑该命令的证据
priority              int              见 §六
issued_at             int              world_tick
expires_at            int?             缺省 = 不过期
causation_id          str              因果链
correlation_id        str              相关链
idempotency_key       str              幂等键
```

### 字段与原语的关系

| 字段 | 归属 |
|---|---|
| `command_id` / `issued_at` / `causation_id` | L0 生成或校验 |
| `expected_revisions` | **必填**，由调用方固定，Gateway 不代填 |
| `payload` | 类型由 L4 `command_catalog` 声明 |
| `target_refs` | 必须解析到已注册的 FactType 或其 scope |

**`expected_revisions` 必填**是有意的：允许 Gateway 代填等于允许「读最新值然后写」，那会让 CAS 失去意义。

---

<a id="command-type"></a>

## 三、command_type 与版本

### 命名

```text
<domain>.<verb>
```

例：

```text
dispatch.issue_order
organization.assign_role
inventory.reserve
equipment.equip
place.move_to
```

`domain` 段必须是某个已注册 Owner 的 `domain`。

### 版本

```text
command_version: int ≥ 1
```

三条规则（与事件 schema 一致）：

| 变更 | 版本 |
|---|---|
| 新增可选 payload 字段 | +1 版本 |
| 新增必填字段 / 删除 / 改类型 | **新 command_type**，不复用旧名 |
| 只改校验规则 | 不改版本，改规则包 |

### 目录

`command_catalog`（L4）必须声明每个命令：

```yaml
dispatch.issue_order:
  version: 1
  handled_by: Dispatch            # 唯一处理 Owner
  payload_schema: issue_order@v1
  requires_authority: true        # 是否需要授权依据
  idempotency_shape: command_id   # 见 §八
```

**`handled_by` 必须唯一。** v1 曾出现 `retreat` 同时归 Combat 与 Morale 的歧义——多 Owner 处理同一命令意味着路由不唯一。

---

<a id="source"></a>

## 四、source_kind

```text
human               玩家直接操作
player_agent        玩家的智能体代理
character_agent     角色自主产生的命令
population_sim      群体模拟产出
scene_script        剧本脚本
```

### 硬约束

**所有来源使用同一套规则。** AI 不能因为是 AI 而获得：

| 不能绕过 | 说明 |
|---|---|
| 权限 | 必须有合法授权 |
| 视野 | 只能基于已知信息 |
| 通信 | 命令必须经传递 |
| 资源 | 消耗照常 |
| revision | CAS 照常 |

`source_kind` 只用于审计与解释，不改变任何校验规则。

---

<a id="control-mode"></a>

## 五、control_mode

```text
player_direct       玩家直接控制的实体
delegated           被授权代理（如玩家指定的将领）
autonomous          自主主体
scripted            剧本驱动
```

| 值 | 要求 |
|---|---|
| `player_direct` | 必须持有该实体的控制权 |
| `delegated` | 必须有有效授权契约（Bond `authority`） |
| `autonomous` | 主体必须有独立的决策权 |
| `scripted` | 必须有剧本许可 |

**控制权不改变事实归属。** 玩家控制某个角色，不等于玩家拥有该角色的 Body 写权——命令仍经该 Owner 校验。

---

<a id="priority"></a>

## 六、优先级

```text
priority: int
```

| 数值 | 含义 |
|---|---|
| 0–99 | 常规 |
| 100–199 | 紧急（战斗中的强制反应） |
| 200+ | 系统级（暂停、恢复） |

**优先级只影响排队顺序，不影响校验。** 高优先级命令同样要过权限与 revision。

---

<a id="lifecycle"></a>

## 七、生命周期

```text
received     Gateway 收到
  ↓
normalized   规范化（默认值填充、引用解析）
  ↓
admitted     通过结构与权限校验
  ↓
queued       进入 Owner 队列
  ↓
executing    Owner 正在结算
  ↓
committed    已提交并取得 receipt
```

### 失败路径

```text
rejected     明确拒绝
expired      超时未决
cancelled    显式取消
superseded   被后续命令取代
partial      部分完成
unknown      结果未知
```

### 状态迁移约束

| 从 | 允许到 |
|---|---|
| `received` | `normalized` / `rejected` |
| `normalized` | `admitted` / `rejected` |
| `admitted` | `queued` / `cancelled` / `expired` |
| `queued` | `executing` / `cancelled` / `expired` / `superseded` |
| `executing` | `committed` / `rejected` / `partial` / `unknown` |

**`committed` 是终态。** `partial` 和 `unknown` 必须进入恢复流程，不得直接回到 `executing`。

---

<a id="idempotency"></a>

## 八、幂等

### 键形状

由 `command_catalog` 的 `idempotency_shape` 声明：

| 形状 | 用于 |
|---|---|
| `command_id` | 大多数命令 |
| `command_id + step` | 过程类命令 |
| `principal_ref + idempotency_key` | 需要跨命令去重时 |
| `effect_id + scheduled_world_tick` | 效果 tick |

### 规则

| 规则 | 说明 |
|---|---|
| 重复提交返回**原 receipt** | 不是新 receipt |
| `payload` 不同但键相同 | 拒绝 `idempotency_key_reused` |
| 键由调用方提供 | Gateway 不生成（除非类型声明为生成） |

---

<a id="gateway"></a>

## 九、Gateway 的职责

### 必须做

| 职责 | 说明 |
|---|---|
| 验证来源与控制模式 | 见 §四、§五 |
| 校验结构与目标 | 引用可解析、类型匹配 |
| 固定读集 | `expected_revisions` 已由调用方给出，Gateway 只校验 |
| 检查控制权 | 是否仍属该主体 |
| 幂等预检 | 查已有记录 |
| 路由 | 到 `handled_by` 指定的 Owner |
| 保存命令审计 | 命令状态不是世界事件 |
| 返回统一结果 | 收集 Owner receipt |

### 不得做

| 禁止 | 理由 |
|---|---|
| 修改任何领域事实 | 通知量写权 |
| 替 Owner 计算结果 | 同上 |
| 保存第二份状态 | 会有两份真相 |
| 把 UI 操作直接变远方事实 | 必须有传递过程 |
| 一个 Owner 拒绝后静默改写另一个 | 破坏分域 |
| 代填 `expected_revisions` | 会让 CAS 失效 |

---

<a id="receipt"></a>

## 十、Receipt

### 字段

```text
receipt_id            str
command_id            str
result_status         enum(见 §七 失败路径 + committed)
owner_ref             ref              哪个 Owner 处理
fact_type_refs        list<ref>        影响的事实
committed_events      list<ref>        已提交的事件
before_revisions      map<ref,int>
after_revisions       map<ref,int>
reason_code           enum?            拒绝或部分完成时
evidence_refs         list<ref>
event_time            int
known_time_by_recipient  map<ref,int>   按接收方的可知时间
next_action           enum?            retry | reconcile | compensate | none
recovery_action       ref?             恢复流程引用
```

### 四种结果语义

| 状态 | 含义 | 禁止的处理 |
|---|---|---|
| `committed` | 已提交 | — |
| `rejected` | 明确拒绝 | 不得重试同一 revision |
| `partial` | 部分提交 | 不得当作全成或全不成 |
| `unknown` | 结果未知 | **不得盲目重发；先按幂等键查询** |

`expired` / `cancelled` / `superseded` 是命令状态，会对应产生相应 receipt。

---

<a id="receipt-chain"></a>

## 十一、一命令多 Owner

### 情形

一个命令可能涉及多个 Owner（如「命中」涉及 Combat / Equipment / Body / Status）。

### 规则

| 规则 | 说明 |
|---|---|
| `handled_by` 是**主 Owner** | 由它协调 |
| 其它 Owner 产出**授权 fragment** | 不是独立 receipt |
| 同一提交端 → 一个 `AtomicEventBatch` + 一个 receipt | |
| 跨提交端 → 多个步骤 receipt + 开放义务 | |

**Receipt 的 `owner_ref` 是主 Owner。** 各 fragment 的出处记在事件的 `owner_fragments` 里。

---

<a id="audit"></a>

## 十二、命令审计不是事实

命令状态（received / queued / executing…）属于 Gateway 的审计记录，**不是世界事件**。

| 区别 | 命令审计 | 世界事件 |
|---|---|---|
| 归谁 | Gateway | Owner |
| 可回放吗 | 可作为证据 | 是唯一真相 |
| 能改变世界吗 | 不能 | 能 |

**不得把「命令已发出」当作「事情已发生」。** 这是本设计里最容易被违反的一条——v1 已明确「受理不等于送达」。

---

<a id="acceptance"></a>

## 十三、验收

| # | 用例 | 期望 |
|---|---|---|
| C1 | 缺 `expected_revisions` | 拒绝 |
| C2 | Gateway 试图代填 revision | 拒绝 |
| C3 | 同一 `command_id` 重复提交 | 返回原 receipt |
| C4 | 同幂等键不同 payload | 拒绝 `idempotency_key_reused` |
| C5 | `handled_by` 声明多个 Owner | 注册拒绝 |
| C6 | AI 来源试图绕过视野 | 拒绝 |
| C7 | 高优先级命令跳过权限校验 | 拒绝 |
| C8 | 命令审计被当作世界事件 | 拒绝 |
| C9 | 跨提交端命令 | 多个 receipt + 开放义务 |
| C10 | `unknown` 结果被盲目重发 | 拒绝；要求先查询 |

---

<a id="open"></a>

## 十四、待决

| 项 | 说明 |
|---|---|
| `priority` 的具体分配规则 | 谁能发 200+ 的系统级命令 |
| 命令队列的容量与淘汰 | 队列满时丢弃策略 |
| 跨 Owner 命令的 fragment 顺序 | 是否由 `resolution_order` 统一定 |
