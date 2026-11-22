# Architecture v2 迁移规格（目标二）

- 版本：0.1 草案，待项目负责人确认
- 日期：2026-11-22
- 性质：**范围与完成判据规格。** 不表示任何迁移已获放行，也不改写 [2026-11-09 执行规格](2026-11-09-architecture-v2-execution-spec.md)。
- 配套计划：[迁移计划](../plans/2026-11-22-architecture-v2-migration.md)
- 设计依据：[architecture-v2 入口](../../architecture-v2/README.md) 及其链接契约；迁移路径见 [08-迁移](../../architecture-v2/08-迁移/01-迁移路径.md)。

## 一、与 11-09 规格的关系

| | 11-09 规格（目标一） | 本规格（目标二） |
|---|---|---|
| 目的 | 以有限切片证明 v2 机制可行 | 把现有 Owner、读取路径、规则与玩法组合按 v2 迁移 |
| 范围 | G0 基线、G1 选定 12 单元、G2 三切片、G3 首域 credential | 全部写事实的 Owner，及 L0–L5 各层的生产实现 |
| 状态 | G0–G2 已收口，G3 首域已收口，G4 改为逐域探针，G5 搁置 | 本文起草时尚无任何任务完成 |
| 处置 | 保持有效，不再扩范围 | 11-09 的 G0–G3 成果作为本规格的 **M0 之前的既成输入** |

目标二不是"G3 之后的更多域"。目标一只证明机制能工作，目标二要求系统整体达到 v2 文档写的形态。两者的差距在下文逐层列出。

## 二、起点（2026-11-22 读取的事实）

证据来源：代码仓库 `integration` 标签 `integration-2026-11-21` @ `0e67fe81` 的静态检查；线程 A、B 的 worktree 状态；冻结记录与盘点报告。**没有运行测试。** 线程 A、B 的未提交改动只读了文件清单与 diff 统计，没有逐行审阅。

| 层 | v2 要求 | 起点现状 |
|---|---|---|
| L0 | `read_as(principal)` 为唯一玩法读取入口；三时间；epoch 栅栏保护生产流；投影按 cursor 增量推进 | `read_as` 只存在于 `character_agent/storage/session_store.py`，gameplay 层无；`known_time` 只在 3 个文件；`presented_time` 0 命中；epoch 栅栏默认不启用、无生产流受保护；投影仍以全量 `rebuild` 为主（`05-Owner重构影响评估` 数字，写于 11-04，**未重测**）；读取点盘点 987 处，871 处"未判定" |
| L1 | 六原语生产实现 | 校验器只接受 `machine`（`fact_type_registry.py:114-115`）；Pool、Bond、Holdings、Process、Place **无通用类**；Pool/Bond 只有 `scripts/architecture-v2-prototypes/` 原型；`ownership_runtime` 由线程 A 在扩 Bond 生命周期（未提交） |
| L2 | 每个 Owner 的事实都声明为 FactType | credential 一个 Machine `fact:credential:*:link` + `holder`；线程 B 正在声明 debt/contract 的 23 个事件类型（未提交）。其余 Owner 零声明 |
| L3 | 22 个已列名 Owner 的 native/stewarded 声明、写集、`denies`、跨事实不变式 | `REGISTERED_OWNER_IDS` 由代码登记；credential 已归 `Ownership`；其余 Owner 无声明 |
| L4 | YAML 规则包完整内容（实体类型、池定义、状态机、受击剖面、聚合模型、命令目录等）、父包叠层、`content_hash`、迁移事件 | 加载器 `load_pack` 在 `rule_pack_validator.py`，只识别 `fact_types`、`machine_defs`、`models`；唯一的包是 `packs/credential_reference/` |
| L5 | reaction / pipeline / workflow / play_pattern 的注册与执行 | **0 实现**（无 `play_pattern`；代码里的 `Pipeline`/`Reaction` 类与 v2 无关） |
| 共享机制 | `OwnerRuntimeBase`、`OwnerCommitBuilder`、`ProjectionCheckpointer`/`StoreReadSnapshot` | `owner_runtime_base.py` 30 行，只含 `replay_duplicate`、`rejected_result`；`OwnerCommitBuilder`、`StoreReadSnapshot` 在 `backend/app` 无命中 |
| 第二真相 | B0 热表、司命 Graph、司命三套副本须先收口 | 盘点时（G3 分支 `d6c30d58`）仍存在；main 的 `FACT_TYPE_REGISTRY` 订阅已替换部分 `*` 通配，**未重核** |

另有两处文档缺口：
- [01-Owner定义](../../architecture-v2/04-Owner/01-Owner定义.md) 声称 23 个 Owner，表中只列 22 个（原生 10、托管 12）；**Combat** 在 `denies` 示例中出现，却不在任一表里。
- 迁移文档与待决清单里的数字多写于 11-03/04，不能当现状引用。

## 三、目标二的成功标准

以下全部满足才称"迁移完成"。每条都要有产物，不接受口头结论。

1. **Owner 覆盖。** 每个写事实的 Owner 都有 L3 声明（`kind`、`writes`、`denies`、跨事实不变式、`commands`、`resolvers`、`reads`），分类经 D5 由项目负责人裁定；所有 `writes` 指向已注册 FactType；校验器能报告 `owner_overlaps_owner`。
2. **FactType 覆盖。** 每个 Owner 的现有事实都已声明为 FactType，含 `primitive`、`visibility`、`resolution_order`、`event_schema_ref`；事件类型进入图投影器（协议 P-3）。有偏离的，登记为"已知偏离"，不得写成已满足。
3. **原语单实现。** 每个已用原语只有一份生产实现，通过其不变量和固定向量；旧域内的重复实现要么迁移到它，要么登记保留理由。**Process 归并（8 个模块）** 是否在范围内，见第六节决定项。
4. **L0 强制。** 凡迁移后的域，其面向主体的读取点经 `read_as` 或在读取边界清单中标注"可信权威/恢复"；`known_time` 在这些域的读取中强制；至少一条生产流受 epoch 栅栏保护，且 B4 前置设计项已落成设计并有实现路径。`presented_time` 随 G5，不在本标准内。
5. **规则包。** 加载器覆盖 `04-规则包文件格式` 的全部内容类型；父包叠层、`content_hash`、迁移事件、"仅非运行态热加载"均有测试；校验器规则按 `03-校验器规则` 分级，H1–H12 不可降级。
6. **L5。** reaction、pipeline、workflow、play_pattern 可注册、可校验、可执行；结构上无 `writes`；Demo 所需的最小集（`07-玩法组合/02-守城Demo定义` 中的 reaction 与 pipeline）可运行。
7. **回放。** 每个迁移域满足 R1（幂等记录、digest、原 receipt）、R2（`committed_event_ids` 可解析、事务一致、事件数匹配）、R3（删除 checkpoint 后 `state_digest` 一致）。
8. **探针。** 每个迁移域冻结后做一次"只加声明/规则包"的新增，记录 `backend/` 代码改动行数；失败按[分水岭实验](../../architecture-v2/08-迁移/04-分水岭实验.md) §四归因。
9. **下游核查。** 每个迁移域的所有直接/间接读取方有清单与专门测试。G3 已证明"现有测试通过"不能替代这一项。
10. **基线。** 相对冻结基线（22 个失败节点、1,169 节点选集）无新增失败；全量运行按里程碑执行并如实记录。**每个迁移单元必须把自己的定向测试登记进选集**（见第五节 U11），选集随迁移增长，不再固定为 1,169 节点。
11. **第二真相。** B0 热表、司命 Graph、司命三套副本已有 Owner 归属或已裁决为"保留并登记"，且"删除私有副本后能从 Owner 事实重建"得到证明。

### 不构成成功的情形

- 全部测试通过；
- 单元测试或原型通过；
- 只完成声明而没有读取方核查；
- 在 UE 或 Godot 里没有运行证据就宣称"已接入"；
- 性能、十三州容量、玩法体验：另走性能基准和玩法证据文档，不由迁移完成推出。

## 四、范围

**包含：** 第三节全部条目；11-09 规格中尚未完成的 G1 剩余机制迁移；协议文件规定的两线程协作所需的文档与测试。

**不包含：**
- 重写 runtime，或把原生 Owner 改成托管（Dispatch/Politics/Economy 类规则无法数据化，见 [01-迁移路径](../../architecture-v2/08-迁移/01-迁移路径.md) §三）。原生 Owner 的迁移是**声明加登记**：FactType、Resolver 进同一注册表（D3），代码保留。
- 修改领域规则、产品行为、Demo 范围、关卡、美术、UI。
- 修复全部历史基线失败。缺陷修复另开轨道，除非阻塞某个迁移单元。
- G5（UE/Agent 接入）：保持 11-17 的搁置决定。**B4 前置设计项不属于 G5**，属于本规格 M2。

## 五、迁移单元与完成定义

**迁移单元** = 一个 runtime 或一个可独立回退的 runtime 子域。一次迁移一个单元，沿用 11-09 约束：每个单元单独提交、可独立回退、与冻结基线对照。

**单元完成定义（DoD）：**

| # | 条件 | 来源 |
|---|---|---|
| U1 | Owner 声明存在且分类已裁定 | 成功标准 1 |
| U2 | 事实已声明 FactType；偏离已登记 | 成功标准 2 |
| U3 | 事件 schema 在图可见的注册表中，P-3 断言通过 | 协议 P-3 |
| U4 | 共享机制：能用 `owner_runtime_base` 等的已用；因语义差异保留的写明理由（digest、`result_digest`、`pinned_revisions`、幂等键前缀、`_append` 形态沿用 G1 口径，不统一） | `02-共享Owner基类` §七 |
| U5 | R1、R2、R3 有证据；R2 属行为改变，单独提交 | G3 口径 |
| U6 | 读取方清单 + 专项测试；改持久事件的类型、版本、字段前先枚举读取方并取得项目负责人确认 | 代码仓库 `AGENTS.md` |
| U7 | 面向主体的读取点已分类；`visibility` 非占位，或占位被明确登记为偏离 | 成功标准 4 |
| U8 | 规则包能承载的设定已在包里；Resolver 已注册 | 成功标准 5 |
| U9 | 探针记录；基线对照无新增失败 | 成功标准 8、10 |
| U10 | 证据文件列出所有改动的代码与数据文件，并写明"已验证 / 仅静态 / 未验证" | 11-09 约束 |
| U11 | **本单元的定向测试已登记进选集**：`docs/verification/selection/<unit>.json`，schema 与 `absorb-main-3bf3418e/*.json` 相同（`head` / `description` / `tests[].test_name/outcome/failures`），登记后该单元永久进入每次合并的回归范围 | 成功标准 10；2026-11-22 决定 |

### U11 的细则

- **登记什么：** 能发现该单元回归的最小节点集——该单元新增或修改的定向测试，加上覆盖它依赖路径的既有测试。不是整个测试文件的全量，也不是只挑一两个正例。
- **谁登记：** 迁移该单元的线程；文件放在 `docs/verification/selection/`，**一个单元一个文件**，避免共享文件冲突。
- **基线怎么定：** 登记时记录当时的实际 outcome。若某节点在 `absorb-main` 基线里本就是失败，须先按 P-2 在 `claims/` 登记，否则登记文件里出现 `failed` 会被合并门禁当作"新增失败来源"。
- **谁维护：** 单元后续被改动时，由改它的线程更新自己的文件；不得由别的线程代为增删。
- **代价：** 选集随迁移增长，每次合并的选集运行时间随之变长。这是有意的取舍：**宁可合并慢，也不要迁移过的单元脱离回归覆盖。** 超过可控规模时由项目负责人决定分片或分波次运行，不由线程自行裁剪。

不得宣称：某单元"满足 v2"，除非 U1–U11 全部有证据；缺一项就写缺哪一项。

## 六、需要项目负责人决定的事项

| # | 决定 | 推荐 | 理由 |
|---|---|---|---|
| S-1 | **Combat** 的分类。它在 `denies` 示例里出现、不在 22 个 Owner 表中 | M0 先盘点代码里实际负责 Combat 的 runtime，再裁定：原生或托管，或并入既有 Owner | 不盘点就裁定会重复 11-04 评估的"凭文档推断"问题 |
| S-2 | B0 六字段的 Owner 归属（Q1） | 迁移到涉及它们的域之前必须定；不能在声明层发明新 Owner | `05-Owner重构影响评估` §六：先建 FactType 再收口 B0 会被迫发明 Owner |
| S-3 | 司命 Heavenly Graph：砍掉或保留（Q2）。司命三套副本改吃 `OwnerFactQuery` 端口 | 保留，但订阅改为按 FactType；三套副本在 M7 收口 | 与 main 已部分切换的方向一致，代价最小 |
| S-4 | `pinned_revisions` 补 Store 校验算不算行为改变（Q3） | 算；单独评审、单独提交，不夹在域迁移里 | 333 处引用从未被校验，补上会改变现有路径 |
| S-5 | **Process 归并**（8 个模块）是否在本规格内 | **已决定（2026-11-22）：在范围内**，排在 M4 之后，先做 Demo 需要的过程类型 | 承接映射标为风险最高；不排则成功标准 3 无法满足 |
| S-6 | 枢纽（inventory、economy、organization_government、resource_body、patch）是否纳入 | **已决定（2026-11-22）：纳入**，排最后一波，进入前须有前序波次的回归证据 | 回归面最大；`05` 建议不先动 |
| S-7 | 迁移完成后，11-09 规格的"逐域探针"是否并入本规格成功标准 8 | 并入 | 避免两套判据 |
| S-8 | **通用 Contract runtime 的 Owner 归属**（2026-11-22 由线程 B 汇报暴露）。该 runtime 同时服务政府评估、设施验收、公共工坊、磨坊服务等合同；v2 文档没有明确映射 | **已决定（2026-11-22）：按事实域拆分，不新建 Owner**——政府评估 → Government，设施验收 → Production/Facility，工坊与服务 → Economy/Production；Contract runtime 退为跨域编排（L5 workflow）或声明层。具体拆分清单以 M0-1 的事实清单为准 | `01-Owner定义` §六要求新 Owner 同时满足四条；一个"通用合同"runtime 更可能是编排层而非事实域。直接把 debt 的 `Economy / Market` 套到全部合同会把互不相关的事实用一个 Owner 绑在一起 |
| S-9 | 线程 B 工作区里两份未跟踪文件（`debt_contract_event_schema.py` 与其测试）的处置。来源未核实，不是本轮 B 写的 | **已决定（2026-11-22）：移出工作区保存**（移到 `D:\Temp` 下独立目录），不作为迁移起点；若日后复用，按 M4 流程从头走（设计文档 + P-3 断言 + P-4 归属说明） | 来源不明的代码不该直接进入迁移；它列了 5 个 `gameplay.commerce.*` 事件，归属本身未定（与 S-8 相邻） |

D2（严格）、D3（代码模型进同一注册表）、D4（拓扑生成 `resolution_order`）、D5（由项目负责人裁定）、D9（仅非运行态）已于 2026-11-16 批准，本规格沿用。D6 只限已测 session 读取切片；扩大读取强制前需另行测量。D7、D8、D10 在对应域或里程碑依赖它们时决定。

## 七、风险与停止条件

在 11-09 规格的停止条件之上追加：

- 单元的改动需要修改存储核心（`event_store.py`、`models.py`）：停止，报告。沿用此前纪律。
- 单元需要改动共同禁区（`economy_runtime.py`、`inventory_runtime.py`）而当前波次未排到：停止。
- 两线程对同一基线失败节点方向相反的修复：双方都不改，报告。
- 探针需要改动 Owner 或 runtime 代码：记录缺口，先形成架构决策再扩大；不放宽零代码改动判据。
- 迁移改动令图投影器静默丢事件（P-3）：停止当前单元。
- 发现令牌、密钥、凭证：停止。
- 原语不变量与现有域语义冲突（如 ownership 单资产单权利）：不在域里绕过，回到 L1 修原语。

## 八、本规格不证明什么

- 不证明性能（需 `09-验收/03-性能基准` 的四个基准实测）。
- 不证明玩法好玩、十三州规模、双端等价（C++ 与 Python 固定向量）。
- 不证明 UE/Godot 接入。
- 本规格里"起点"一节的数字来自静态读取，进入 M0 时须按当前提交重测。

## 九、状态记录

起草日期 2026-11-22。已确认：S-5（纳入 Process 归并）、S-6（纳入枢纽）；S-1 Combat 先盘点（M0-1）再裁定。S-2、S-3、S-4、S-7 待确认，S-2 至 S-4 在 M0-3 复核之后决定。
