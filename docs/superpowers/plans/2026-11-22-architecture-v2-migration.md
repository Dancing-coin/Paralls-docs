# Architecture v2 迁移计划（目标二）

- 版本：0.1 草案，待项目负责人确认
- 日期：2026-11-22
- 规格：[迁移规格](../specs/2026-11-22-architecture-v2-migration-spec.md)（成功标准、DoD、停止条件、待决项 S-1 至 S-7）
- 不替代 [2026-11-09 执行计划](2026-11-09-architecture-v2-execution.md)；后者的 G0–G3 成果是本计划的起点。

## 一、执行方式

- 实施交给 Codex；Claude 写提示词、核对提交范围与 diff，不盲信汇报数字。汇报分"已验证 / 仅静态 / 需要决定"。
- 给 Codex 的提示词必须写明：不推送、不 `git add -A`、只暂存指定文件、遇到需改存储核心或共同禁区、令牌密钥凭证、新增失败时停止。
- 每个任务一张任务卡：源提交、测试命令与范围、环境、失败集合、改动文件清单、回退方式。
- 改持久事件的类型、版本或字段前，先枚举读取方，并取得项目负责人确认。
- 基线：`integration-2026-11-21` @ `0e67fe81`，冻结记录 `docs/verification/absorb-main-3bf3418e/`（22 个失败节点，选集 1,169 节点）。每个里程碑结束前重新核对。

## 二、线程分工（一台设备、一个人、两个 Codex 线程）

**原分工的问题：** `docs/v2-coordination/` 的协议按"两位负责人、两台设备"设计，含 `comms/` 交流记录、21:00 申报/22:00 合并、对方的话记为"对方称"。现在只有一个负责人，这些条款只增加开销，没有保护作用。

**按依赖性质分，不按首域分：**

| | 线程 A：机制线 | 线程 B：域线 |
|---|---|---|
| 做什么 | 共享机制、L1 原语、L0、校验器/加载器、L5 引擎 | 单个域的迁移：runtime、`packs/<域>/`、域测试、探针 |
| 独占文件 | `owner_runtime_base`、`fact_type_registry`、`rule_pack_validator`、`app/models/fact_type.py`、`event_schema_registry`，以及将来新建的原语、`read_as`、L5 目录 | 各域 runtime、各域规则包、各域测试 |
| 为什么这样分 | 这些文件的改动影响所有域，必须只有一个写者 | 域之间文件不相交，可并行 |

起点分工（credential→ownership 给 A、debt→contract 给 B）作废：A 现在的主任务是机制，不是某个域。ownership 的 Bond 生命周期属于 L1，仍归 A。

**保留的规则（因为两个 Codex 线程不共享上下文，这是技术需要）：**
1. 文件归属表（`BOUNDARIES.md`）：B 不得改 A 的独占文件，也不得本地临时改。
2. B 需要 A 的文件变化时，写需求文件；A 回应。两个文件合成一个 `docs/v2-coordination/handoff.md`（B 追加需求，A 追加回应，单文件，不要两份）。
3. 协议 P-2：改任何基线失败节点的合同前先登记。两个线程互相看不到对方，11-09 的反向修复就是这样发生的。
4. 协议 P-3：事件类型必须进入图投影器。
5. 提交只暂存指定文件；线程只推各自分支；`main` 不允许合入。
6. 同机并行：各 worktree 独立，`PYTHONPATH` 指向各自 `backend`，核验 `app.__file__`，输出目录各用唯一 run id。

**取消的规则：**
- `comms/` 交流记录；
- `daily/` 的 21:00 申报、22:00 合并时点；改为"负责人认为某线程的某个提交可合并时"随时合并；
- "对方称"的措辞规则；
- 两位负责人一致同意才能改 BOUNDARIES：改为项目负责人一人决定。

**合并：** 第三个线程（或你本人）按需把 A 的提交、B 的提交先后合到 `merge/<日期>`，通过范围检查、claims 检查、密钥扫描、选集后快进 `integration`，打标签。不设审查人。验证深度仍须如实写，选集通过不得写成全量回归通过。

**这些改动落在哪里：** 协议在代码仓库 `docs/v2-coordination/`（分支 `coord/v2-protocol-20261120`，已并入 integration）。本计划只是写明新规则；真正修改协议文件需要另开一次提交，**未经你放行不推送**。

### 一个线程还是两个线程

我的判断：**两个线程仍然有用，但收益取决于 A 的队列不阻塞 B。**

- 两线程有效的时段：A 在做机制，B 在迁一个已有机制够用的域。例如现在，B 做 debt/contract 的事件声明，A 做 Bond。
- 退化成一个线程更好的时段：A 即将改的共享文件正是 B 下一个域需要的。此时 B 只能写需求文件等待，两个线程变成串行加交接成本。
- 单机资源：冻结选集运行方式见协议；G0 的全量串行运行约 1436 秒。两线程同时跑全量会争用 CPU 与磁盘，全量建议错开。

建议：先按两线程推进；每个里程碑结束时检查一次——如果上一个里程碑里 B 有一半以上时间在等 A，下一个里程碑改成单线程顺序执行。

## 三、里程碑与任务

依赖：M0 → M1/M2/M3（可并行） → M4 各波（依赖 M1/M3 对应部分） → M5/M6 → M7 → M8。M5、M6 与 M4 的早期波次可交错。

### M0 盘点与映射（线程 B 做只读；A 参与 S-1 至 S-4 的方案）

| 任务 | 产出 | 备注 |
|---|---|---|
| M0-1 runtime→Owner→FactType 候选映射 | 每个 `*_runtime.py`（35 个）对应哪个 v2 Owner、写哪些事实、是否有第二真相；Combat 实际落点 | 解决 S-1；把 22 个 Owner 逐个落到 runtime |
| M0-2 当前机制采用表 | 在当前 integration 上重测 `owner_runtime_base` / digest / replay / rejected 的采用情况；`OwnerCommitBuilder`、`StoreReadSnapshot` 状态 | 旧表在 G3 分支 `d6c30d58`，已过时 |
| M0-3 第二真相复核 | B0 六字段、司命 Graph 订阅、司命三套副本、`pinned_revisions`，逐项在当前代码上核对是否仍存在 | 解决 S-2 至 S-4 的事实输入 |
| M0-4 读取方静态图 | 以 AST 生成每个 runtime 的导入者与读取者；与读取边界清单（987 点）交叉 | 支撑 U6 |
| M0-5 Command 信封符合度抽查 | `expected_revisions` 必填、`handled_by` 唯一、来源一致规则在现有 Gateway/命令路径的符合情况 | 07-Command 文档未被任何任务检查过 |
| M0-6 波次表 | 按 fan-out、重复机制数、回归面给出域波次（草案见下） | 需你确认 |

**波次草案**（fan-out 来自 G3 分支盘点，`imported_by`；**需 M0-2 在当前提交上重测**）：

| 波 | 域 | 依据 |
|---|---|---|
| 1 | credential（完成）、ownership（A 在做 Bond） | 已启动 |
| 2 | gift(1)、land_right(1)、life_state(1)、action_consequence(1)、reference_data(1)、government_treasury(1)、civilization_capability(2)、bakery_reference(2)、ecology(2)、soul 系列、survival(4)、action_window(3) | 导入者 ≤4 |
| 3 | equipment(7)、modifier(5)、ability(7)、construction_production(7)、econ1_economy(7)、organization_government_social_platform(5)，以及 **debt**（见下） | 导入者 5–7；equipment、modifier 有专项保护（Decimal 摘要、bridge 副作用） |
| 4 | patch_runtime(15)、resource_body(17)、organization_government(17)、economy(19)、inventory(20) | 枢纽；进入前须有第 3 波回归证据 |

`economy_runtime`、`inventory_runtime` 当前是协议规定的共同禁区，第 4 波之前不动。

**2026-11-22 修正（线程 B 汇报后的改动，需 M0-1 复核）：**

- **debt 从第 1 波移到第 3 波。** 理由：线程 B 核实 debt 结算的正式 Owner 是 `Economy / Market`（`01-Owner定义` 与 `REGISTERED_OWNER_IDS` 一致），而 Economy 是导入者最多的枢纽（19），`economy_runtime.py` 是共同禁区；23 个事件类型里还有 5 个 `gameplay.commerce.*` 由 economy 侧写入。按"Owner 处于枢纽就压后"的原则，debt 不能当小域。原草案把它排第 1 波是只看 `debt_runtime.py` 自身导入者数的结果，**口径错了**。
- **contract 暂时无波次。** 通用 Contract runtime 同时服务政府评估、设施验收、公共工坊、磨坊服务等合同，v2 文档没有明确这些合同归哪个 Owner。归属未定之前不排波次、不写规则包。列为决定项 S-8。
- **第 1 波现在只剩已完成的 credential 和进行中的 ownership。** B 的首个域待 M0-6 给出新波次表后再定，不由本文预设。

**M0 停止条件：** 盘点结果与本文假设冲突（例如 Combat 实际在多个 runtime 中分散）时，先报告，不改波次表。

### M1 L1 原语生产实现（线程 A）

顺序按已排波次的需要，不按"六个一起做"。

| 任务 | 触发 | 依据 |
|---|---|---|
| M1-1 Bond | 进行中（ownership）；验收：五种契、scope、term、属性不可变（B7）、撤销/到期/supersede | `02-六原语规格` §四；D1 原型已验证 |
| M1-2 Holdings | 第 2 波起的库存类事实；数量与质量拆分（质量为 Pool） | `03-承接映射` §四 |
| M1-3 Pool | 需要有界、预留、窗口积分、滞回的事实 | 缺口 5 项见承接映射 §二 |
| M1-4 Place | 第 3 波后；占用互斥、通行性独立提交点 | |
| M1-5 Process | 视 S-5；最后做，先归 3 个 | 承接映射 §六："风险最高" |

每个原语的验收：不变量、事件 schema（字段级，见 `04-事件schema规格`）、积分与切窗、聚合、片段格式、固定向量（D1 原型的用例作为参考）。校验器的 "只支持 machine" 限制随之逐个放开。

**M1-1 的分片要求（2026-11-22，线程 A 汇报后补）：** 线程 A 当前把 Bond 生命周期、credential v3 `bond_ref` 迁移、多权利投影、属性白名单移除、Decimal 属性规范化放在同一个未提交工作区（`ownership_runtime.py` 约 +840 行）。这些是不同性质的行为改变，必须拆成可独立回退的提交：

| 片 | 内容 | 性质 |
|---|---|---|
| 1 | Bond 生命周期：grant / revoke / transfer / expire / supersede、事件 schema、投影重建 | 新增能力（L1） |
| 2 | 多权利投影：同资产多 Bond 类型共存，保留 `active_right_by_asset` 兼容视图 | 新增能力（L1） |
| 3 | credential v3 `bond_ref` 迁移 | 跨域读向量变更，须单独提交并列出读取方 |
| 4 | 属性白名单移除 + Decimal 属性规范化 | 行为改变；须说明旧数据与重试路径 |

每片单独跑定向集与相关选集。**尚未运行全量 10,392 节点**，合并前须补，且如实记录跑了什么。

### M2 L0 强制（线程 A；B4 设计由 A 或另开线程）

| 任务 | 说明 |
|---|---|
| M2-1 读取边界清单更新 | 对已迁移域，把"未判定"改成明确分类，产物是清单与分类依据 |
| M2-2 `read_as` | 在 gameplay 读取层建立 `read_as(principal, scope, as_of_tick, fact_types)`；缺证据用明确错误码拒绝；先接入已迁移域的面向主体读取点 |
| M2-3 known_time 推广 | 在已迁移域的读取点计算并保留；`presented_time` 随 G5，不做 |
| M2-4 投影增量推进 | cursor、连续区间校验、失败不安装半成品；删除 checkpoint 后 digest 一致（R3 的通用机制） |
| M2-5 B4 前置设计 | 在线 handoff、受理冻结、恢复证据、`pending`/`reconcile`/`activate`、双 writer 对账、首流 publisher 接线（`epoch-design.md`）；先设计，实现须你确认 |
| M2-6 首条生产流受 epoch 保护 | 依赖 M2-5；选哪条流由你决定 |

D6：性能预算只覆盖已测 session 读取切片。M2-2 扩大读取前先测量。

### M3 共享机制完成（线程 A）

| 任务 | 说明 |
|---|---|
| M3-1 `OwnerCommitBuilder` | 只抽共同骨架；`result_digest`、`pinned_revisions` 命名、幂等键形态由调用方传入，不统一 |
| M3-2 `StoreReadSnapshot` 推广 | 以 head 为键复用事件元组；逐域评估，先测再改 |
| M3-3 R2 推广 | 其余回放路径的事件引用校验。按域并入各域迁移，不集中做；每个域单独提交 |
| M3-4 `pinned_revisions` 校验 | 取决于 S-4 的决定；单独评审与提交 |

### M4 域迁移波次（线程 B 为主；需要机制时走 handoff）

每个单元按规格第五节的 U1–U10。流程：

1. 读取方清单（M0-4）→ 2. 设计文档（只读核对，含已知偏离）→ 3. 事件声明与 P-3 断言 → 4. 声明与规则包 → 5. 回放 R1/R2/R3 → 6. 下游专项测试 → 7. 探针 → 8. 证据文件。

持久事件改动（类型、版本、字段）与 R2 行为改变各自单独提交；前者先经你确认。

**当前状态（2026-11-22，读自两个 worktree 与线程汇报，未审阅代码）：**
- **ownership / credential（A）：** Bond 生命周期等改动未提交，分片要求见 M1-1。
- **debt（B）：** 未开始。Owner 已核实为 `Economy / Market`，按上文修正移到第 3 波。
- **contract（B）：** 未开始，等待 S-8 裁定 Owner 归属。
- **B 工作区里两份未跟踪文件**（`backend/app/gameplay/debt_contract_event_schema.py`、`backend/tests/test_debt_contract_event_schema.py`）：不是本轮 B 写的，来源未核实。处置见 S-9；在裁定前保持原样，不提交。
- **B 本轮只做了只读基线核对**：62 个定向节点通过，未跑选集或全量，未改代码。

### M5 L4 规则包完整化（线程 A）

| 任务 | 说明 |
|---|---|
| M5-1 内容类型 | 加载器逐步支持 `pool_defs`、`entity_types`、`temporal_effects`、`impact_profiles`、`aggregation_models`、`command_catalog`、`bindings`；每增一种须有校验规则与拒绝码 |
| M5-2 父包叠层与 `content_hash` | 整体替换，不逐字段合并；解析路径落入存档 |
| M5-3 迁移事件 | `pack.migrated`，旧段用旧包解释 |
| M5-4 热加载 | 仅非运行态；运行中拒绝 |
| M5-5 校验器规则覆盖 | 对照 `03-校验器规则` 的规则目录，逐条标注已实现 / 未实现；H1–H12 不得降级 |

### M6 L5 引擎（线程 A）

最小集优先，须在对应探针之前落地、不计入探针改动量。

| 任务 | 说明 |
|---|---|
| M6-1 reaction | 注册、校验（循环检测、`emit` 只能是 Command）、异步触发 |
| M6-2 pipeline | `atomic` / `obligation` 声明，同 pipeline 共享 `input_revision_vector`，跨 scope 拒绝同批次 |
| M6-3 workflow | 步骤、开放义务、状态可丢可重建 |
| M6-4 play_pattern | 结构上无 `writes` |
| M6-5 Demo 最小集 | `casualty_to_morale`、`gate_breach_to_presence_reeval`、`report_arrival_to_knowledge_update` 等，依赖对应域已迁移 |

### M7 第二真相收口（线程 A 与 B 按文件归属；须先有 S-2 至 S-4 决定）

- B0 六字段归属；
- 司命订阅按 FactType；
- 司命三套副本改吃 `OwnerFactQuery`；
- 验收：删除私有副本后能从 Owner 事实重建。

### M8 综合验收

- 对照 `01-组合性证据` 的 A1–A7、B1–B3，逐条给出状态与产物；
- 性能基准 B1–B4 实测；
- 全量运行与基线刷新（基线只在 claims 登记"有意修复"后才移除失败节点）；
- 成功标准 1–11 逐条打勾，缺项写缺什么。

## 四、立即要做的事

1. **你确认**规格第六节 S-1 至 S-7。S-5、S-6 直接决定波次表是否收敛。
2. **M0 启动**：把盘点交给线程 B（只读）。M0-6 波次表出来后你确认。
3. **线程 A 当前未提交的 Bond 工作**补一张 M1-1 任务卡（范围、验收、回退），再提交。
4. **线程 B 当前未提交的事件声明**先回答 `commerce` 5 个事件的归属，再继续。
5. 协调协议改写（第二节）：确认后另开一次提交；不推送，等你放行。

## 五、未核实项

- A、B 两个 worktree 的未提交 diff 没有逐行审阅，测试没有运行。
- 波次表的 fan-out 数字来自 G3 分支盘点，吸收 `main` 之后未重测。
- `07-Command信封与回执` 在现有代码里的符合度没人查过。
- main 的 `FACT_TYPE_REGISTRY` 订阅变化对司命 Graph 的实际效果未核实。
- 协议"取消的规则"部分是我的建议，B 负责人是否仍有他人参与，以你的说明为准。
