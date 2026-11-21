# Laya 角色智能体快慢思考总体两阶段实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` in an authorized implementation turn. Implement task by task; unchecked steps are planned work. Native subagents are optional and are not dispatched by this document.

**Goal:** 保留 L1–L4 和完整角色认知，先接通高频 Laya 决策与全面 Deep 分析的并行协作，再将 Laya 接入 Agnes 式多步工具循环。

**Architecture:** 复用 Character coordinator/driver、gateway、原状态/记忆 stores、MindDeltaLedger、L3/L4 和各领域 authority。所有模型产生提案，由原 owner 校验来源、版本、有效期和幂等后提交；动作只调用 actor 当时实际可用的语义能力，脚本和动画由 UE/Godot 本地实现。

**Tech Stack:** 现有 Python、Pydantic、pytest、Godot/UE adapter；Laya 以 CPU 为目标；无新增依赖。

**Spec:** [快慢思考总体规格](../design/fast-thinking-chain.md)。

**Status:** `requirements-adopted / attention-work-added / behavior-family-contract-added / implementation-not-started / values-open / runtime-unverified`，2026-11-18。这里的未开始指本轮架构迁移，不否认原 gateway、L2/L3/L4、状态、TTS 和动作基础的已有实现。

## Global Constraints

- CPU，不设计依赖 CUDA 的方案；没有已批准的毫秒 SLO、token 上限或并发容量，不虚构默认验收线。
- 不设内部快慢分档器；L1 只整理和投影事实，不做复杂度分类、动机解释或策略路由。
- 每个合法输入可唤醒 Laya；不等于逐输入无界推理、不等于逐原子动作询问模型。
- 保留完整 L2、L3、L4、角色隔离、权限与原领域 owner；不增加平行 scheduler、状态库或第二个角色大脑。
- 快慢工作可以重叠；普通/Deep 是逻辑职责，可以同模型不同 effort 或同 provider 不同 model。
- 动作必须来自 actor 当时实际可用的动作能力；允许登记规则内动态组合，不生成任意脚本、clip、raw pose 或物理命令。
- 行为资源族与主动/被动触发方式是两个字段；过渡动作/言语族逐条登记 mode。Passive 只免去角色主动认知调用，不免除引擎/音频资源成本、动作仲裁、speech lease、安全检查或 owner receipt。
- 被动言语只用审核资源表达非命题、非策略的短声/短语；命令、警告、欺骗、承诺、谈判立场和有意影响他人的表达走主动交流路径。
- 认知结果为提案；取消、过期、stale 零新增效应；Deep 不因推理更深而优先覆盖新状态。
- 台词生成、TTS 合成、实际播放、他人听见是不同证据；纯认知更新不伪造 L4 身体命令。
- 流体推理、晶体化经验、注意容量、任务占用、环境负荷、可恢复认知精力是独立维度；注意 ledger 的 owner 不是模型、AffectEngine 或物理资源 owner。
- 不给属性、task cost、恢复率、并行上限、millisecond/token gate 猜值；缺 cost registration 的有意识任务不得默认为免费。
- 参考快照只读；保留既有用户改动、authored 档案、历史证据和旧存档。基础动作规格的存在不代表本轮能力合同已实现。

## Review Focus

- 高频输入夹杂不可合并的攻击/发言/owner 回执：逐来源可追溯，不能被“保留最新快照”吞掉（Task 1/4）。
- 旧 L2 先写后规划改成并行：Laya 有清晰的已提交认知基线，迟到更新不回滚已执行动作（Task 3/4）。
- Deep 与普通模型重复解释同事件：同证据不双计，跨字段更新原子提交，重启后 receipt 不重复（Task 3/5）。
- 方案选择后装备/路径/动画绑定失效：逐步准入拒绝不再可用的能力，不能把模型计划算成成功（Task 6）。
- 资源 reserve/settle/恢复在 cancel/reopen/crash 后出现免费重跑或双扣：严格按原 reservation receipt 幂等恢复（Task 2/10）。
- 工具循环中用户打断或晚到台词：取消传播到模型/工具/语音，闭合窗口不再接纳行动，已发生的事实保留（Task 7/9/10）。

## 实施工作区、文件责任和从属计划

产品代码目标是 `D:/cl-laya`；`D:/Users/User/Documents/paralls-phase-0-demo` 仅为现状参考，不默认双仓复制。执行前重新读取目标仓库的 `AGENTS.md`、`docs/INDEX.md`、`docs/harness.md` 和主线设计入口，核对工作区与当前改动。本文不要求切换分支、合并参考分支或发布。

下表代码路径相对 `D:/cl-laya`；标注 Create 的文件都是 planned。本计划只规定确有责任的新文件，其余扩展原实现，不为每个操作新建服务。

| 责任 | Modify / Create |
|---|---|
| 短输入和来源冻结 | Modify `backend/app/character_agent/reasoning/l1_perception.py`、`runtime/runtime_loop.py`；Create `backend/app/character_agent/models/decision_context.py`（后续未写全前缀者均位于 `backend/app/character_agent/`） |
| 认知提案和唯一提交 | Modify `models/cognition_update.py`、`models/cognition_delta.py`、`mind/delta_ledger.py`、`mind/writeback_policy.py`、`reasoning/l2_reasoner.py`、`storage/session_store.py` |
| 并行回合、Deep 作业及恢复 | Modify `runtime/cognition_continuation.py`、`runtime/runtime_loop.py`、`services/cognition_admission.py`、`services/cognition_coordinator.py`、`services/cognition_driver.py` |
| 模型职责/effort/输出合同 | Modify `gateway/model_provider.py`、`gateway/model_gateway.py`、`gateway/prompt_policy.py`、`gateway/output_validator.py`、`gateway/laya_provider.py` |
| 认知资源合同与账本 | Modify `profile/models.py`、`models/dynamic_state.py`、`models/cognition_delta.py`、`runtime/runtime_loop.py`、`services/cognition_admission.py`、`services/cognition_coordinator.py`、`services/cognition_driver.py`、`storage/session_store.py`；Create `models/attention_resource.py`、`services/attention_resource_owner.py`、必要时 `storage/attention_resource_store.py`（是否独立 store 由 event/receipt 读写核查决定） |
| 能力投影与动态组合 | Modify `skills/models.py`、`skills/service.py`、`planning/l3_planner.py`、`execution/l4_adapter.py`、`execution/l4_executor.py`；Create `models/action_capability.py`、`execution/composite_plan.py` |
| 语音与时效 | Modify `expression/utterance_composer.py`、`expression/utterance_safety.py`、`models/speech_lease.py` 及原 Speech 路由；不重写已实现的 ASR/TTS provider |
| 阶段二操作登记与循环 | Create `models/model_collaboration.py`、`services/model_collaboration.py`；原 coordinator 持有循环生命周期，新增文件仅做操作合同/状态转移，不另建 scheduler |
| 测量与验收 | 扩展 `backend/app/character_agent/evaluation/`；Create `scripts/verification/verify_fast_thinking_chain.py`；新增测试见各 Task |

| 子计划/现有工作 | 本总计划如何承接 |
|---|---|
| [score/noul 两阶段子计划](typed-cognition-implementation.md) | 子 Task 1–4 归本阶段一、复用总 Task 1–4 与 Task 2 的 admission；子 Task 5 归本阶段二 Task 9/10，子 Task 6 提供分类质量/时延证据并归 Task 8/11；不重复实现总上下文、ledger 或模型循环 |
| [UE 动作与感知接入计划](../../superpowers/plans/2026-11-12-ue-action-foundation-and-perception-uplink-plan.md) | 本 Task 6 交付跨引擎语义要求；引擎执行器、动画绑定和实机表现仍由该线设计/实施，并按 Task 8 分别验收 |
| [表达闭环计划](expression-loop-implementation.md) | 保留已有交付及验收，Task 7 只改新架构的 producer、lease、取消和过期接缝 |
| [本地 ASR/语音接入设计](../speech/design/asr-and-speech-integration.md)、[音色池计划](../speech/plans/voice-pool-implementation.md) | 独立工作流；不以快慢架构迁移阻塞提供方/音色资产工作，也不将未实现的收音/UE 播放列为完成 |

## 阶段与依赖

```text
阶段一：1 冻结输入/profile pins → 2 注意账本与 task admission → 3 认知提案写回
                            → 4 快慢并行回合 → 5 全面 Deep
                            → 6 动作能力/组合 → 7 语音接缝 → 8 阶段一验收
       typed 子计划 1–4 复用 1/2/3/4，按 S4/N1 起步补齐实名消费者
阶段二：9 Laya 工具循环 → 10 循环取消/恢复闭环 → 11 总体验收
```

阶段一的 Deep 可以在既有作业机制中连续分析、调用登记只读工具和普通模型；本阶段暂不让每次工具结果回到 Laya 选择下一操作。阶段二才增加这个返回环。完整 L2/Deep 能力不因分阶段而缩水。

### 阶段一三档出口

以下是累计的阶段出口，不改变任务依赖；1a 可作为早期可见成果，1b 补齐资源与提案完整性，1c 才是阶段一完整出口。

| 出口 | 纳入范围 | 验收条件 |
|---|---|---|
| **1a 核心最小** | Task 1；Task 2/3 为并行决策所需的最小 admission、proposal/read-set 与原 owner 提交接缝；Task 4 的快慢并行主路径；typed 子计划中 S4 或 N1 至少一个真实 consumer | L2/Deep pending 时，Laya 仍能通过当前 owner 合法提交来自冻结候选的动作；无已提交解释时不伪造解释；迟到/stale 提案零写；一个 typed 结果能被后续具名 consumer 实际读取。仅可用受控 test policy 验证结构，不宣称数值资源政策有效。 |
| **1b 资源与提案闭合** | 完成 Task 2、Task 3 的持久化账本、成本登记、reservation/settlement/recovery、完整 L2 proposal 与原子 receipt；覆盖取消、重试、重启恢复 | 已登记任务按 owner receipt 准入、结算和恢复；未知数值仍保持 unknown；生产数值 admission 只有在正式量表与成本值冻结后才可开启。过期、重复、冲突 proposal 零新增副作用。 |
| **1c 完整阶段一** | Task 5–8 其余 Deep、typed consumer、动作、表达、CPU 和端侧验收 | 完整 L2 能力保留；普通与 Deep 可异步提案且无覆盖；已登记动作/语音通过 owner 与本地底座验收；CPU、Godot、UE、音频各自满足其适用验收门。玩家切片证据可按独立车道记录，缺少引擎证据不得宣称完整通过。 |

**Task 1 入口门状态（2026-11-20 更新）：** 用户已决定质量证据不足时保留有效承诺与本地反应；仅允许宿主合同确认的低风险、可撤销动作受限执行；高风险、不可逆或破坏承诺的变更需补证据或更完整分析。L3 已校验宿主候选证据，L4 前复核 pending commitment revision；动作证据由 `target_catalog` resolver 提供，统一注册 owner 与 pending 自动超时策略仍待设计。CPU 消融扫描不是正式质量线，且不证明增加 state 必然改善质量；不得以未校准 `p_max`/熵单独作动作门槛。无承诺时的保守玩法行为与正式质量集/通过线由原 owner 和 Task 8 冻结。

## 执行车道与并行边界

路线图中的历史缺口用 `G1–G26` 编号，需求追踪中的 `R1–R16` 是独立命名空间；本计划是[总体路线图](../roadmap/completion.md)中的一个有界实施批次，不取代其余缺口。各 G 项与本计划的覆盖关系见路线图 §2.1 后的映射说明。

**车道 A：核心迁移。** 总 Task 1→2→3→4→5 按依赖顺序串行推进：先冻结输入/profile pins，再建立 attention admission/settlement，之后完成 L2 提案写回、普通回合并行化，最后接入全面 Deep。Typed 子计划 Task 1–4 依附并复用总 Task 1–4 的接口和账本，不另开独立实现车道；S4 fear/stress_load 与 N1 是首批消费者。阶段二 Task 9–11 仍须等待阶段一出口。

**车道 B：玩家垂直切片。** 仅指 Task 6 中交接文档列明的 S1 suggestion 生命周期、S2 触觉 percept 玩家投影、S3 微表现 consumer 与偏好门控，不包括完整动作能力投影/复合计划，也不扩大到嗅觉、热觉或味觉投影。该切片不依赖车道 A 的 Task 1–5 才能定义和验收，但不得改写其认知账本、DecisionContext 或提案提交合同。

两车道可在计划层面并行，代码执行须满足以下条件：各自在独立 worktree/分支工作；开始前列明实际文件所有权；不得同时编辑 `runtime_loop.py`、`main.py` 等共享边界文件，同文件改动由一个 owner 集成或串行处理；跨车道的 schema/事件变更先协调，不得由一条车道擅自扩展另一条合同。若无法维持文件所有权隔离，则代码工作串行，不以逻辑独立推断无冲突。

车道 B 的 Godot 可观察表现属于验收门。交接要求 Godot 运行证据；若目标会话没有可用的 Godot MCP/运行验证路径，或玩家 UI 节点归属未确认，依交接停止条件暂停受影响实现并报告，不以静态测试冒充引擎验收。已经可以独立完成且不触及停止条件的合同分析/测试可继续，但不得宣称玩家切片完成。

### Task 1：冻结输入投影、profile pins 与测量合同

**Files:** 上表输入、gateway 文件；实现测试位于 `backend/tests/test_decision_context.py`、`test_character_laya_provider.py` 与相关 L2/MindFrame 测试。

**Interfaces（planned 内部 API）：** `DecisionContext` 保存 actor/turn、来源事件、已提交认知 revision、目标/承诺 revision、可见证据、可用能力与认知 profile/dynamic/attention revision pins；`build_decision_context(...) -> DecisionContext` 无网络/写回；`project_laya_state(context: DecisionContext) -> dict` 只输出总体规格 §5 的角色可见字段。权限/lease/幂等等完整 pins 留在宿主，不靠删除校验缩短 state。profile 中流体推理/容量/经验引用只作模型许可的角色上下文；运行时预算合同由 Task 2 单独校验，不把资源数值全塞进 Laya 短输入。

**实施记录（2026-11-20，Task 1 实现与 focused 验证完成）：** `D:/cl-laya` 的 `models/decision_context.py` 冻结语义投影、来源引用、候选及 turn/input/memory/policy/snapshot/profile/dynamic/attention/goal/committed-cognition pins；语义 state 有显式顶层白名单，治理 pins 保留在宿主，provider 入口校验 digest 与候选一致性。Laya 投影不包含完整 `capability_envelope` / `cognition_policy`，不静默截断；缺 tokenizer/预算证据时拒绝正式输入预算校验，候选缺必要目标/能力信息时不进入候选集合。缺失事实保持 `unknown`，无本轮 L2 时可从已提交认知构造冻结上下文；当前普通回合仍先等 L2，实际 L3 调度切换归 Task 4。MindFrame/L2/L3 来源引用现按首次出现顺序保留，不按字典序重排。宿主动作准入与 stale commitment revision 门控已有生产接线。

measurement 字段合同和 provider 可观测 evidence 已实现，但 lifecycle timestamps 尚未由 runtime 填充。当前投影固定 A2 CPU 扫描已于 2026-11-20 完成，原始请求/响应和逐级摘要位于 `F:/cl-laya-evidence/task1-current-projection-scan-20261120/`，简明报告位于 `F:/cl-laya-evidence/task1-current-projection-scan-20261120.md`。扫描从生产 `DecisionContext` 冻结投影生成 L0，保留固定候选与 criteria；服务健康报告 pinned checkpoint、`device=cpu` 且无 CPU fallback。45 次调用无截断、每级三次选择一致；char_a/char_c 在 L1 相对 L0 改选，体现输入删减敏感性。样本仅三名 actor，且无独立正确性标签，不证明质量、泛化、并发能力或性能门槛，也不构成 SLO；`p_max`、归一化熵与 L0 一致率不作为正确性或战术准入证据。2026-11-19 扫描仍是旧投影历史基线。Task 1 所要求的固定输入扫描证据项完成，生命周期时间戳和数值 SLO 保持开放。

**扫描过程补记：** 初始停止记录基于当时内存情况写入；用户随后明确要求即使资源条件不足也继续。使用固定 A2 replay 样本运行当前投影后，原始阻塞报告已标记 superseded，当前测量结果和限制见 `F:/cl-laya-evidence/task1-current-projection-scan-20261120.md`。

宿主动作合同的生产门控也已接通：L3 从宿主 `target_catalog` descriptor 读取带版本、动作定义 revision、候选 pins 和 expiry 的 admission evidence；Laya 不能生成该证据。`CharacterTurnCoordinator` active-turn ledger 与冻结 L4 execution contract 是当前承诺 owner；L4 前复核 pending revision，stale 结果在计划/执行请求写入前拒绝。统一动作合同注册表和 pending 承诺自动超时策略仍是后续宿主工作，不由本 Task 复制第二份状态。

Laya `laya_evidence.measurement` 已注册 `input_received_monotonic_ns`、`decision_ready_monotonic_ns`、`l4_accepted_monotonic_ns`、`commitment_started_monotonic_ns`、`queue_wait_ms`、`state_tokens`、`usage`、`cold_start`、`model`、`checkpoint_revision`、`device` 与 `provider_latency_ms`。目前 provider 实测能填 decision-ready、服务端实际提供时的 queue/device/cold-start、返回 usage/model，以及使用 pinned tokenizer 时的 state token 数；无来源的字段保持 null。Task 4 负责把 input-received、L4-accepted、commitment-start 和调度队列时间点接入同一运行时决策证据。数值 SLO 仍不冻结。

- [x] 写失败用例并验证：隐藏对象/他人私有记忆不进入投影；无当前 L2 结果时可从已提交认知构建输入；输入缺失保持 unknown；不可合并事件来源保序；profile/动态状态 revision pin 存在；治理字段不进入语义 state。
- [x] 实现冻结投影、显式顶层白名单及拒绝语义；现有候选 compiler 对缺少必需目标/能力证据的候选返回诊断并阻止进入呈现集合，不以截断删除硬约束。
- [x] 登记 measurement evidence 字段并只填实际可观测值；生命周期时间点在 Task 4 的并行调度接线中填充。数值 SLO 未冻结。
- [x] 用当前冻结投影、固定候选与 criteria 重跑 CPU state/latency scan，报告实际分布与质量限制；不从旧投影线性外推，不冻结未经批准的 SLO。2026-11-20 固定 A2 样本扫描完成，见 F 盘报告与原始 evidence；可用内存约 5.19 GiB，按用户明确指示继续，结束后停止本轮服务。
- [x] 运行 `python -m pytest -q backend/tests/test_decision_context.py backend/tests/test_character_laya_provider.py backend/tests/test_laya_runtime_input_budget.py backend/tests/test_character_agent_l2_reasoning.py backend/tests/test_character_candidate_compiler.py backend/tests/test_mind_frame_turn_boundary.py`；从仓库根目录重跑，153 passed（1.90s）。首次从 backend 子目录误执行、未找到路径，未运行测试。

### Task 2：注意资源账本、cost registry、admission 与恢复

**Files:** 责任表认知资源合同与账本、`runtime/runtime_loop.py`、原 cognition admission/coordinator/driver/session store；Create `backend/tests/test_attention_resource_contract.py`、`backend/tests/test_attention_admission_and_recovery.py`、`backend/tests/test_cognitive_task_cost_registry.py`。

**Owner:** Character runtime/state owner 负责唯一 ledger、receipt 和 admission/recovery；profile/content owner 提供稳定能力、技能证据与 task cost 注册输入；Affect/Need owners 只提供带来源的状态/负荷读写接缝，不写资源余额；status/effect-system owner 提供休息、药物/治疗和环境产生的有效恢复倍率修正，不直接恢复精力。

**Interfaces（planned）：** `CognitiveResourceProfile` 由 profile model 承载稳定 fluid reasoning/attention capacity/concurrency/recovery policy refs/task-cost tendencies；晶体经验引用已有 skill/evidence/registered route，不复制为全局智力数。`CognitiveTaskCostRegistration` 登记 task class、基准成本/容量需求、可暂停/合并语义、合法 effort/work levels、允许的 experience discount evidence、admission/recovery/settlement rules 和 consumer。`AttentionReservation` 固定 actor/job/source/task/profile+policy revision、reserved/spent/released amounts、priority、effort、expiry/cancel generation。`RecoveryRateModifier` 由外部状态/效果提供 actor/effect/source、有效倍率、effective interval 和 revision；attention owner 验证有效期并按“基础恢复政策 × 当前有效倍率”结算余额，外部不能写余额或恢复 receipt。`AttentionLedgerSnapshot` 是 owner 计算的 energy/capacity/ambient-load/task slots/effective recovery multiplier 视图。具体字段、倍率范围、组合/封顶方式和计量单位按当前 store/event contract 与效果系统合同冻结，不虚构数值。

- [x] 核对 dynamic-state、L2 `CharacterDynamicStateDelta`、`MindDeltaLedger`、认知 admission/progress、session event/receipt reader。列出持久读写者、recovery reader 和 legacy snapshots；选择最小 additive 接缝，不能假设 memory-only `CharacterDynamicStateStore` 就是持久账本。
- [x] 写失败用例并运行：未知 task class 不免费 admission；unknown profile cost/energy 保持 unknown 并明确 queue/reject；缺流体/晶体能力值不变成默认高低；物理 stamina/mana/AP 不被注意账本写入；相同 job admission 幂等且 revision 不混 actor。
- [x] **受控 bootstrap policy（仅合同测试）：** 在显式 test configuration 下，仅允许登记过的 task class 取得结构性 test admission/receipt；费用、容量和精力值继续标记为 `unknown`，reservation 不得写成 0 或伪装成数值充足。未知 task class、非 test 配置或生产运行不得沿用此例外，必须明确拒绝/排队。该模式只验证状态机、幂等和 receipt 形状，不验资源公平性、数值合理性或生产准入。
- [x] bootstrap 验收须覆盖：test policy allowlist 之外仍拒绝；receipt 明示 `test_only` 与未知成本；test configuration 不能被生产入口静默启用；切换正式 policy 前冻结并验证 profile、task cost、capacity 和恢复数值。
- [x] 实现唯一 owner 的 test-only reserve/settle/release/recover receipt 状态机：覆盖幂等、partial、取消/过期/stale、crash/reopen 与工作回执去重；金额均保持 unknown，不执行生产容量/精力/并发预留或扣费。
- [x] 建立 recovery tick、外部 `RecoveryRateModifier` 与 ambient-load 的来源/版本/有效期/重复投递合同；生产必须由外部 validator 证明来源。实际余额恢复和负荷数值结算未实现，provider wait/CPU idle/模型输出不恢复，`score` 不写 ledger。
- [x] 登记认知 task class 与预期 consumer 名称，覆盖 Laya choice、完整 L2、score/noul、主动感知、普通/Deep reasoning、临场台词；该表目前是结构 registry，不证明生产 consumer 已接 admission。身体本能、碰撞/受击、已承诺动作 tick 和模板口癖不作为认知任务。
- [x] 覆盖 unknown 数值/生产 fail-closed、test allowlist、receipt 重放、取消/过期/stale 和 ambient source 边界；生产 overcapacity、公平调度、真实成本结算及 lowering effort 的行为验收仍待资源数值与调度接线。
- [x] 运行 Task 2 指定回归及相关 admission/coordinator/session recovery 回归，并记录 receipt 与 recovery 证据；本任务未提交。
- [ ] 冻结生产 profile、task cost、capacity、energy、单位、恢复政策/倍率和 overcapacity 阈值后，将唯一 owner 接入实际生产调度并完成资源准入/结算验收。

**实施记录（2026-11-20，Task 2 结构合同完成）：** 读者/写者扫描确认：`CharacterDynamicStateStore` 仅在 `runtime_loop.py` 与 `session_recovery.py` 中由 session event/reducer/恢复态安装并作为内存动态态投影；L2 `CharacterDynamicStateDelta` 经 `MindDeltaLedgerBuilder`、`MindWritebackPolicyRouter` 写成 `dynamic_state_event`，其字段只有 vigilance/distraction/affect/tension 等，不含认知精力。`CharacterAgentSessionStore` 的 SQLite `character_session_events`、`character_session_receipts`、runtime current/recovery JSON 是持久事件与快照边界；认知 admission/progress 由 `CharacterCognitionAdmissionService`、coordinator/driver 调用 session store，head 仅作点读/待办索引，progress/阶段 receipt 与事件同事务提交。恢复读者为 `session_recovery.py` reducer 和 `runtime_loop.py` `_install_recovery_state`；legacy JSON/JSONL/continuity snapshots 只恢复既有 dynamic state，没有 attention 余额或 reservation，旧能力 profile 缺字段解释为 unknown。最小 additive 接缝是既有 session receipt store，不改 event type、schema 或旧 snapshot。

唯一资源 owner 为新增 `AttentionLedgerOwner`；task registry 为 `CognitiveTaskCostRegistry`；schema 为 `CognitiveResourceProfile`、`CognitiveTaskCostRegistration`、`AttentionReservation`、`RecoveryRateModifier` 与只读 `AttentionLedgerSnapshot`。owner 在 `character_session_receipts` 中按 actor 保存 immutable admission/settle/release、恢复 tick、外部恢复修正和 ambient-load receipts，SQLite transaction 保证原子性；不新增表或迁移。operation key 固定 actor/job/revision，精确重试返回原 receipt；同一 work receipt 在 actor 范围内只能结算一次，后续操作或其他 job 复用会由 owner 拒绝；worker reopen 从 receipt 重建当前 reservation，过期由 owner recover 终态化。commit-before-response、receipt 复用拒绝、partial Deep、cancel/expiry/stale、actor/revision 隔离和外部 receipt 校验均有测试。新增的 receipt 复用测试先以 `DID NOT RAISE` 失败，再在 owner 原子消费检查后通过。

cost registry 的 task class/consumer 关系登记为 `laya_choice` → character decision runtime、`l2_full`/`ordinary_reasoning` → cognition coordinator、`score`/`noul` → typed consumers、`active_perception_analysis` → perception analysis、`deep_reasoning` → deep driver、`dialogue_generation` → dialogue runtime。身体本能、碰撞/受击、已承诺动作 tick 和模板口癖不注册为认知任务。当前这些是 owner/registry 接口映射，尚未把现有生产消费者改接资源 admission；运行时接线保留到后续调度任务，以免未知数值政策改变现有生产行为。生产构造不注入 test bootstrap；未知 task class 明确拒绝，known class 但 profile/cost/energy unknown 时 production 明确拒绝。显式 allowlist test policy 只生成 `test_only=true`、`cost_status=unknown` 的结构回执，不提供免费或数值资源。

恢复仅接收 world tick/rest/sleep/low-load kind，生产必须由外部 tick/modifier validator 证明来源；modifier 固定 actor、effect/source、revision 与完整有效时间区间，tick 整段必须落在有效区间内并以 revision 幂等推进。multiple modifier 的组合规则未知时拒绝；余额变化 `recovered_amount` 保持 null，不能推断恢复量。provider wait/CPU idle/模型输出不属于 tick source。ambient load 数额保持 unknown，只可由同一 source owner 验证的 resolution receipt 关闭。成本、容量、并行上限、恢复倍率、单位及 overcapacity thresholds 均仍 unknown，因此 Task 2 只通过结构合同，**不代表资源政策可用于生产**。

验证（2026-11-21 完成复核）：补充边界用例先观察到 5 项按预期失败，再实现修复并转绿，覆盖 ambient resolution 重试 receipt 幂等、恢复 modifier 身份/重复投递/冲突、revision 引用校验，以及优先级和现存 load 不得绕过 unknown 资源政策。Task 2 指定七个测试文件 `87 passed`；admission/coordinator/driver/stage-store/session-recovery regression `131 passed, 4 warnings`；`python -m compileall -q backend/app`、`git diff --check` 通过。两个之前在全量运行中失败的 population 节点复核出 pytest 子进程继承 Codex 注入的 `GIT_CONFIG_*`，其中空 `GIT_CONFIG_VALUE_0` 令子进程 `git rev-parse HEAD` 失败；仅在单次 pytest 命令环境移除这些变量后，两节点 `2 passed`。

清洁进程环境下完整后端 `python -m pytest -q backend/tests` 收集 10,541 项，结果 `10,503 passed, 2 skipped, 2 xfailed, 34 failed`。34 个失败分布为：`test_calibration_preclosure.py` 1 项、`test_calibration_repair_contracts.py` 1 项、`test_character_development_runner.py` 4 项、`test_character_evaluation_preparation.py` 12 项、`test_character_mind_frame_models.py` 1 项、`test_character_task45_behavior.py` 1 项、`test_p15_runtime_skill_diagnostics.py` 2 项、`test_role_presentation_adapter_contract.py` 1 项、`test_siming_llm_tls_context.py` 10 项、`test_ws_protocol.py` 1 项。与任务开始前计划中逐测试文件记录的 34 项基线比较，每个文件的失败数量一致；当时没有保留所有基线 node id，不能声称已逐 node id 对比。当前失败的代表节点为 `test_calibration_preclosure.py::test_offline_wire_preserves_unknowns_targets_and_source_memory`、`test_calibration_repair_contracts.py::test_budget_official_layout_rejects_individual_truncation_and_boundary`、`test_character_mind_frame_models.py::test_mind_frame_can_be_frozen_to_one_turn_with_digest_and_source_refs`、`test_character_task45_behavior.py::test_task45_headless_probe_observes_shared_path_and_contact_contract`、`test_role_presentation_adapter_contract.py::test_task8_headless_registry_probe_resolves_profiles_and_blocks_rejected_registration`、`test_ws_protocol.py::test_websocket_character_agent_execution_emits_scheduling_round_trace`；其余失败落在上述文件的同一既有分类中。原因仍为既有 Task 1 Laya/profile/evaluation 改动与 calibration fixture/source pins 差异，以及原有 Siming TLS/websocket 差异；失败没有落在 Task 2 新增 attention owner、registry 或测试文件中。相较任务开始前记录的分类基线，通过数增加 5，来自新增 Task 2 用例；本轮另确认前述 2 个 population 失败是环境注入问题，不属于代码回归。未修改或隐藏任何全量失败。

本轮全量测试的 34 个失败 node id 如下。早先基线证据只保存了逐文件分类计数，所以本轮可核对文件级计数一致，无法回溯证明每个旧 node id 均相同。

```text
tests/test_calibration_preclosure.py::test_offline_wire_preserves_unknowns_targets_and_source_memory
tests/test_calibration_repair_contracts.py::test_budget_official_layout_rejects_individual_truncation_and_boundary
tests/test_character_development_runner.py::test_runner_preserves_rejected_real_response_and_does_not_grade_it
tests/test_character_development_runner.py::test_runner_rejects_changed_wire_and_truth_before_any_provider_call
tests/test_character_development_runner.py::test_runner_stops_changed_input_version_and_retains_already_issued_call
tests/test_character_development_runner.py::test_runner_uses_real_adapter_mapping_and_flushes_diagnostic_only_results
tests/test_character_evaluation_preparation.py::test_abo_projection_does_not_inherit_runtime_numeric_defaults
tests/test_character_evaluation_preparation.py::test_authored_profile_reaches_shared_wire_without_private_backbone
tests/test_character_evaluation_preparation.py::test_empty_development_selection_cannot_claim_ready
tests/test_character_evaluation_preparation.py::test_final_and_independent_holdout_remain_unopened
tests/test_character_evaluation_preparation.py::test_fixture_profiles_have_source_evidence_without_abo_defaults
tests/test_character_evaluation_preparation.py::test_missing_or_hidden_targets_cannot_receive_fixture_admission
tests/test_character_evaluation_preparation.py::test_model_input_never_contains_grading_answers
tests/test_character_evaluation_preparation.py::test_preparation_is_repeatable_and_full_wire_matches_runtime_serializer
tests/test_character_evaluation_preparation.py::test_preparation_materializes_frozen_frames_and_independent_reference_universe
tests/test_character_evaluation_preparation.py::test_reference_universe_detects_compiler_omission
tests/test_character_evaluation_preparation.py::test_same_authority_trajectory_cannot_cross_splits
tests/test_character_mind_frame_models.py::test_mind_frame_can_be_frozen_to_one_turn_with_digest_and_source_refs
tests/test_character_task45_behavior.py::test_task45_headless_probe_observes_shared_path_and_contact_contract
tests/test_p15_runtime_skill_diagnostics.py::test_resolved_profile_wire_bytes_match_pre_diagnostic_t3_baseline[char_a-ee5377b429cc058fe5b3a35d8e7de69b8056def528e19b8f68137782bcb43d27]
tests/test_p15_runtime_skill_diagnostics.py::test_resolved_profile_wire_bytes_match_pre_diagnostic_t3_baseline[char_b-3f07dcc6c01aa2148b66def7ff12be82fc401bdb310b0a896d752265b27c23e1]
tests/test_role_presentation_adapter_contract.py::test_task8_headless_registry_probe_resolves_profiles_and_blocks_rejected_registration
tests/test_siming_llm_tls_context.py::test_ca_environment_change_applies_when_provider_is_rebuilt
tests/test_siming_llm_tls_context.py::test_concurrent_first_posts_construct_only_one_context
tests/test_siming_llm_tls_context.py::test_context_is_lazy_and_isolated_between_providers
tests/test_siming_llm_tls_context.py::test_context_preserves_ca_environment_precedence[default]
tests/test_siming_llm_tls_context.py::test_context_preserves_ca_environment_precedence[directory]
tests/test_siming_llm_tls_context.py::test_context_preserves_ca_environment_precedence[file_over_directory]
tests/test_siming_llm_tls_context.py::test_failed_context_initialization_can_retry[invalid]
tests/test_siming_llm_tls_context.py::test_failed_context_initialization_can_retry[missing]
tests/test_siming_llm_tls_context.py::test_sequential_posts_reuse_one_verified_context_but_close_each_client
tests/test_siming_llm_tls_context.py::test_transport_errors_keep_context_and_close_temporary_client[http-SimingLlmProviderError]
tests/test_siming_llm_tls_context.py::test_transport_errors_keep_context_and_close_temporary_client[timeout-SimingLlmProviderTimeout]
tests/test_ws_protocol.py::test_websocket_character_agent_execution_emits_scheduling_round_trace
```

**Task 2 状态（2026-11-21）：** 结构合同、持久 receipt、fail-closed test/production 边界及指定测试完成。账本、cost registry、admission、settlement、release、recovery 的唯一 owner 与 SQLite receipt 持久化边界如上；crash/reopen、retry、idempotency、cancel/expiry/stale、partial 和恢复 modifier 证据已覆盖。Task 3 可基于显式 test-only receipt 继续结构实现，因此 Task 2 不阻塞 Task 3 的合同工作；生产消费者接线、正式资源 admission 与资源公平性仍被未知 profile、cost、capacity、energy 和 recovery 数值阻塞。全部数值与单位继续为 `unknown`，不得宣称资源政策已可用于生产。测量 lifecycle 时间点仍留给 Task 4。

### Task 3：完整 L2 的提案化、生产权与先后顺序

**Files:** 上表认知、store 与 coordinator 文件；Create `backend/tests/test_cognition_proposal_ordering.py`；与 typed 子 Task 3 共用提交路径，并以 Task 2 attention reservation/settlement receipts 作为独立认知工作成本证据。

**Interfaces:** 扩展原 `cognition_update/cognition_delta` 合同为 `CognitionProposal`：proposal/source/evidence、actor、producer/task/schema/model、base read-set、created/expiry、字段/命题、取消代次。原 owner 接纳入口返回持久 receipt，不新增写者。首版严格验证所有声明的 read-set；不做自动 rebase 或任意字段合并。

- [x] 写失败用例并运行：保留摘要、风险/模糊度、注意、belief/social/higher-order/dynamic/goal hints 全部原输出；同事件同任务重试返回原 receipt；不同输出/交付对相同来源不双计；取消/过期/stale 零写；重启后重复接纳无新增事件。
- [x] 将原 L2 结果映射和提交分开，保留原消费者。Task 3 没有切换任何维度 producer：解释摘要、belief/social/higher-order 与 L2 dynamic delta 仍经 `l2_reasoner`、`_plan_l2_effects`、`_plan_cognition_update` 进入原 Character owner；need pressure 仍由 `NeedTensionEngine` 计算并写入 `NeedTensionStore`，其到 dynamic delta 的既有映射仍归 `AffectEngine`。不同提案只要声明的 read-set 已过期即拒绝；一次提案相关更新随原 stage receipt 原子提交。
- [x] 补并发用例：两个独立 SQLite session store 连接争用同一 actor revision 时只有一个 `commit_cognition_stage` 成功；L2 晚到结果不能覆盖较新 fear；取消与提交在原事务边界裁决；状态写入不撤销已有 owner receipt；重开后从已提交状态恢复。
- [x] 运行 `python -m pytest -q backend/tests/test_cognition_proposal_ordering.py backend/tests/test_character_agent_cognition_writeback.py backend/tests/test_character_mind_delta_ledger.py backend/tests/test_character_mind_writeback_policy.py backend/tests/test_cognition_completion_revision.py`；提交前 Task 3 回归为 `99 passed`，`compileall` 与 `git diff --check` 通过。

**实施记录（2026-11-21，Task 3 结构实现）：** 新增严格冻结的 `CognitionProposal`，绑定 actor、原始来源引用、`l2_reasoner/l2_full` producer/task、可得时的 model ref、完整 actor read-set digest、创建/过期时间、取消代次及完整 `CharacterInterpretation`。L2 原有解释摘要、风险/模糊度、注意目标、belief/social/higher-order/dynamic deltas 与 goal hints 均随 proposal 保存；既有 L2 消费事件不删除、不改 owner。提案进入原 `CharacterCognitionCoordinator.freeze_l2`，随原 `commit_cognition_stage` before/after/events receipt 原子提交；无新表和第二 writer。原 actor pins 复核失败则 stage 不写；取消入口仅终止未提交阶段，已有 stage receipt 时拒绝取消，继续原恢复路径。未给旧持久 `CharacterCognitionProgress` 添加字段，避免改变历史 progress digest。

新增 `test_cognition_proposal_ordering.py` 覆盖完整 proposal/read-set、stage receipt 重启重放不双写、取消零 L2 写、较新 fear 状态阻止迟到 proposal 覆盖。Task 3 专项及相邻 regression `177 passed`，`compileall` 与 `git diff --check` 通过。资源 reservation 仍因 Task 2 生产数值未知而未接入；model ref 若 provider completion 没有可信字段则保持 null。取消通过原 cognition progress terminal 表达，不独立产生状态事件。

**状态说明：** 当前完成提案合同、持久接纳与原子写回的结构闭环；成本 reservation 生产接线、跨 provider 的真实 model identity、Task 4 并行双进度与完整连续输入调度仍未完成，不能据此声称全阶段认知链已完成。

**Task 3 后续提交（2026-11-21）：** `30c3ac23` 在原 L2 stage transaction 中增加 actor/task/source evidence receipt，并新增另一 delivery 对同一来源的重复提案拒绝用例。定向 Task 3 回归 `98 passed`，覆盖同 proposal 响应丢失重放与不同 proposal 零新增写入。由于 provider model identity 仍不可观测，此测试证明来源去重，不证明真实跨 provider 运行验收；provider identity、同 revision 并发竞争及 typed producer 维度交接仍未完成。

**Task 3 收口（2026-11-21）：** 并发回归新增于 `91268d87`，仅修改 `backend/tests/test_cognition_proposal_ordering.py`。它用两个独立 SQLite 连接竞争同一 actor revision，确认只有一笔 stage transaction 提交；Task 3 指定回归为 `99 passed`。Task 3 代码提交为 `67bcb71d`、`30c3ac23` 与测试补充 `91268d87`。`CognitionProposal.model_ref` 在无可信 provider evidence 时保持 `null`；重复来源去重不依赖模型身份，因此覆盖不同模型重复结果，但没有真实跨 provider identity evidence。Task 3 未切换 dynamic/need producer，现有责任映射如上。Task 3 已完成当前 L2 producer 的提案、原子 owner receipt、过期/stale/取消和并发合同。

**Task 3 范围裁定：** 原 Task 3 并发条目中的“Deep 晚到不覆盖玩家脱险后的恐惧”依赖尚未存在的 Task 5 Deep producer。现阶段以 L2 stale-pin 测试证明原 owner 的基线保护；Deep producer 的对应端到端回归移入 Task 5，必须在那里再验其复用相同 read-set 和 owner transaction。若 Deep 使用独立 writer，该延期将暴露覆盖风险，不能标为通过。

**Task 4 当前状态（2026-11-21）：** `24adf24b` 已将 owner 接收时的 `monotonic_ns` 冻结进普通输入的 L3 request context，并以 measurement/L3/runtime/provider 回归验证（`144 passed`）；provider 的 `decision_ready` 采样点已有。后续工作区实现让普通 perceived input 在已有已提交解释时并发准备 L3 当前决策与完整 L2，两个 provider 可任一先完成；没有已提交解释时仍先完成 L2，再按原顺序准备 L3。快慢结果共享同一 runtime continuation、冻结上下文和当前 actor owner，覆盖取消、迟到回执、上下文变更后的慢结果拒绝、独立 provider retry 及不重复派发 execution。计划指定的五个认知测试文件及相关等待器、WebSocket 和对话回归，本轮运行 `176 passed`。

**Task 4 自审结论（2026-11-21 更新）：** 快慢并行决策已使用共享冻结上下文和版本校验，已提交解释缺失时仍先完成 L2；慢结果在快决策提交后按 stale pins 拒绝。新增的 `laya_evidence.measurement` 类型、L3 evidence 传递、runtime 输入/decision-ready/L4/commitment 时间点及 provider slot 本地等待测量已通过定向测试和 SQLite reopen。Task 4 仍为 `in progress`：`PendingCognitionTurn` 双 lane continuation 仍在进程内，缺少重启与 commit-before-response crash 恢复；普通有效输入遇到同 actor pending turn 仍返回 `actor_busy`/`requeued`，没有持久 admission 和后续重新调度证据；capacity/resource 数值继续为 `unknown`，不宣称资源准入或容量通过。

**线 1 复核与提交（2026-11-21）：** Task 2 的 `f13c0bc1` 提交 `attention.py`、`attention_ledger.py`、`cognitive_task_registry.py` 和三个对应测试文件。Task 1/2 联合定向复核为 `179 passed`。Task 3 的 `67bcb71d` 提交 `cognition_proposal.py`、`cognition_admission.py`、`cognition_coordinator.py` 和 `test_cognition_proposal_ordering.py`。复核发现取消可在 resume 读取进度与写入之间插入，导致已取消的工作写入事件。现在在原 session 事务内检查 progress、读取 stage receipt 并复核 pins 后提交事件。新增 actor/task/source evidence receipt，在原 L2 stage receipt 与事件同事务提交；相同来源经另一个 delivery、即使输出不同也零新增写入，同 proposal 的提交后重放继续幂等。过期、前置取消、冲突完成、较新状态覆盖保护及提交响应丢失后的重开重放有回归。最新 Task 3 指定回归 `98 passed`，`compileall` 和 `git diff --check` 通过。provider 未提供可信 model identity，因此 `model_ref` 仍为 null；不同真实 provider/model 的来源证据交接和 typed producer 维度交接仍未验证，不能标成通过。Task 3 没有引擎专属改动；全量 harness 的静态部分通过，`character-agent-execution` 因缺少 Godot executable 阻塞，归线 3 实机验收。产品代码补充提交 `30c3ac23` 仅含 coordinator 与 proposal ordering test。

### Task 4：普通回合并行化与连续输入

**Files:** 上表 continuation、admission、coordinator/driver、runtime；Create `backend/tests/test_fast_slow_parallel_turn.py`。

**Interfaces:** 现有 `CognitionRequest`/prepared job 增加当前决策与认知分析的独立进度，但绑定同一冻结上下文。`DecisionContext` 与 `CognitionProposal` 复用 Task 1/3；有意识工作 admission 复用 Task 2 的 attention owner；状态/持久化仍由原 coordinator/store 所有。

- [x] 以受控 pending provider 写失败测试：L2 未完成时，Laya 可选并提交合法当前动作；无当前解释时不创建虚构解释；普通有效输入持久进入 admission；重复输入复用原 admission，不重启已接纳承诺。Deep 的并行路径归 Task 5。
- [x] 把同步“等完整 L2 再 L3”改成共享冻结上下文和版本校验下的并行进度。L3 使用已提交认知加本轮可见事实；慢提案沿原 owner stage receipt 提交，旧 pins 不能覆盖快 lane 已提交状态。取消、重开恢复、terminal receipt 写入失败和重复来源有回归；continuity floor 与模型错误走原路径。
- [ ] 按固定 CPU/checkpoint 报 lifecycle、queue、input/output 分布，不设未经批准的 SLO；此项移入 Task 8 验收。
- [x] 接通可观测的 lifecycle 时间点与本地 provider-slot wait；无来源字段保持 null，数值 SLO 未冻结。Task 8 的 CPU/checkpoint/输入输出分布尚未验收。
- [ ] 在原 admission/slots 中隔离当前决策与慢作业资源；合并可替换快照时保留 causation，不合并独立攻击、发言、取消或 owner receipt。**Blocked decision:** 普通/Deep slot 容量和 cost 仍为 `unknown`，不得加默认数值；正式资源隔离尚未实现或验收。
- [x] 运行 Task 4 定向回归并验证取消、恢复及原普通回合路径后提交。`test_fast_slow_parallel_turn.py`、`test_fast_slow_entrypoints.py`、admission/coordinator/driver/stage-store、wait、completion-revision 与 measurement-lifecycle 合计 `172 passed`；`compileall` 和 `git diff --check` 通过。

**Task 4 线 1 补充记录（2026-11-21）：** Task 4 measurement 变更提交为 `b715cee4`，文件为 `decision_context.py`、`l3_planner.py`、`runtime_loop.py`、`character_turn_coordinator.py`、`character_agent_runtime.py`、`cognition_wait.py` 与三个对应测试文件。计划指定的五个核心测试文件为 `83 passed`；扩展等待器、completion-revision 和 WebSocket 回归为 `213 passed, 1 failed`。唯一失败 `test_websocket_character_agent_execution_emits_scheduling_round_trace` 发送 legacy `approach` 请求；当前入口拒绝该 legacy social-spatial action 并只回错误 ack，与测试要求 scheduling trace 的断言不相符。`compileall` 与 `git diff --check` 通过。该失败作为当前基线不一致保留，未扩大到线 1 后端之外修复。Task 4 尚未完成连续输入持久 admission/重新调度、双 lane 恢复与 commit-before-response crash 测试；旧承诺保留通过既有 L3/L4 owner 路径验证，不代表队列与恢复合同完成。

**Task 4 持久 admission 与双 lane 恢复（2026-11-21）：** 普通有效输入现写入原 session receipt store，重复/并发 delivery 保留一个 source admission；现有 `CharacterCognitionDriver` 轮询恢复队列，不增加 scheduler 或 state owner。SQLite reopen 后，快 lane 已提交时只恢复原冻结 L2 request；慢 checkpoint 保存完整 revision vector 与 read-set digest。新增恢复断言先因 checkpoint timeline pin 与实际派发 job 不一致失败，随后将 checkpoint 保存移到 pin 绑定之后，定向恢复用例通过。另覆盖两 lane 已提交但 terminal receipt 写入失败后的重开恢复，确认不重放 execution/interpretation；driver 恢复、并发重复 admission、普通/并行入口、取消、wait 与 measurement 回归共 `172 passed`，`compileall`、`git diff --check` 通过。线 1 提交 `9e2fc6ab` 修改 `cognition_continuation.py`、`runtime_loop.py`、`cognition_driver.py`、`test_character_cognition_driver.py`、`test_fast_slow_parallel_turn.py`；继承的 `models/__init__.py` 不属于本次 Task 4 提交。Task 4 仍 `in progress`：快/慢 provider slot 尚未隔离，容量与 cost 决策保持 `unknown`；CPU/checkpoint/input-output 分布移交 Task 8。没有修改 UE/Godot 产品代码。独立攻击、发言和 owner receipt 未被 admission 合并，现有取消和 owner receipt 路径仍分别工作；还需后续集成证据继续核验。

**Task 4 本线程复核（2026-11-21）：** 在 `cbf47a0a` 重跑并行回合、入口、driver、admission、progress、completion revision、wait 与 measurement 核心回归，`144 passed, 4 warnings`。扩展到 dialogue lifecycle 与 WebSocket 的回归为 `255 passed, 3 failed, 108 warnings`；失败是已记录的 dialogue cancellation 参数化两例，以及旧 `approach` WebSocket scheduling trace 断言，均未由本轮 Task 4 改动引入。provider-slot 隔离/资源数值与 CPU 分布仍未验收，Task 4 保持 `in progress`，不能写成生产资源准入完成。原始输出位于 `F:/cl-laya-evidence/task4-followup-20261121/`。

### Task 5：全面 Deep Model 与普通模型职责配置

**Files:** gateway、coordinator/driver 和 continuation；Create `backend/tests/test_deep_cognition_workflow.py`。

**Interfaces:** 扩展原作业合同为 `DeepCognitionJob`，包含目标问题、可见上下文/read-set、允许工具、模型 budget、attention reservation、取消/expiry、partial/final 状态。输出 `CognitionProposal`、目标提案、经 Task 6 校验的行动提案；工具结果带 evidence refs。普通/Deep 的 provider/model/effort 分别 pin 到证据，物理服务可复用。执行 effort 与流体智力分开；工作负载同时受 profile、policy、任务登记及 attention ledger 约束。

- [x] 合同测试覆盖同模型不同 effort、不同模型配置、requested/actual model evidence、provider usage budget、read-only tools、递归 Deep 拒绝、来源受限的 partial/final 和完整认知/目标/复合行动提案；未报告的 actual model/effort 保持 unknown。
- [ ] 生产路径尚未创建或派发 `DeepCognitionJob`；现有 production slow-goal composition 仍执行 legacy `goal_proposal:v1`，Deep composition 测试通过 admission 注入 job。生产 Deep 的 model、effort、预算和 attention reservation 来源均未冻结，不可添加默认值。需接通显式配置后的生产 job 创建与调度，并验证无配置时明确不启动。
- [x] 扩展既有 `goal_proposal_trigger` progress，保留 legacy consumer；Deep round history 与 frozen job 随原 session receipt 持久化，普通模型可先给 partial 再由 Deep 协作，read-only evidence/goal-history 工具返回 source refs，proposal 只经原 Character cognition 与 goal owner 原子提交。provider error、partial/budget failure、expiry 与 terminal receipt 使用原 progress owner。
- [ ] 目标级委托去重、attention reservation/settlement、生产多 actor/capacity admission，以及 late action proposal 经 Task 6 capability/决策窗口校验仍未接通。现有 actor 单 pending-goal 互斥不证明目标级幂等。
- [x] Deep focused regression 已运行：`test_deep_cognition_workflow.py`、`test_character_cognition_admission.py`、`test_character_slow_goal_atomic_acceptance.py`、`test_character_slow_goal_coordinator.py`、`test_character_slow_goal_main.py` 共 `74 passed`。其中 production composition 仅验证 legacy goal proposal 路径；Deep 的生产派发未验证。运行时环境产生一条既存 Starlette/httpx deprecation warning。

**Task 5 线 1 状态（2026-11-21）：** 部分合同和原 owner 写回路径已完成，Task 5 保持 `in progress`。后端只新增 Deep cognition 结构与 provider/coordinator 支持，未修改 UE/Godot 产品代码。测试已验证冻结 read-set、普通/Deep 逻辑角色、effort/model 请求证据、预算、多轮只读工具、取消/expiry 拒绝及 SQLite receipt/reopen 的原子恢复；未经授权的认知/目标/动作直写路径未增加。Deep 实际 model identity 若 provider 未报告仍为 null。生产触发与 job 创建、任务注册/attention reservation、目标级去重、late action window 和真实 provider 运行未验收。提交 `008edb32` 包含 16 个已核实归属的文件：Deep contract/gateway `goal_proposal.py`、`model_gateway.py`、`model_provider.py`、`output_validator.py`、`prompt_policy.py`、`deep_cognition.py`；producer/read-set 与原 owner `cognition_proposal.py`、`runtime_loop.py`、`cognition_admission.py`、`cognition_coordinator.py`、`session_store.py`；回归 `test_character_cognition_admission.py`、`test_character_slow_goal_atomic_acceptance.py`、`test_character_slow_goal_coordinator.py`、`test_character_slow_goal_main.py`、`test_deep_cognition_workflow.py`。指定 Deep/coordinator/completion regression 为 `120 passed`；admission/atomic/coordinator/main 组合 regression 为 `74 passed`；`compileall` 和 `git diff --check` 通过，均有一条既存 Starlette/httpx deprecation warning。继承的 `models/__init__.py` 排除在提交之外。后续继续阶段一前必须保留以上未完成项，不能把局部 Deep workflow 测试写成 Task 5 全部完成。

**Task 5 attention 生命周期补充（2026-11-21）：** 提交 `b43718bb` 将 Deep job 与同一 session store 中的 attention reservation 绑定。启动及每轮 provider 回执前复核 reservation receipt、actor/source、task class、expiry 和 cancel generation；partial、completed、cancelled、failed、stale 与 expired 状态通过原 owner 更新，proposal/progress 与最终 settlement 共用原 session transaction。生产 owner 增加基于持久 cognition progress receipt 的 work receipt 校验。提交改动为 `backend/app/character_agent/models/attention.py`、`backend/app/character_agent/services/attention_ledger.py`、`backend/app/character_agent/services/cognition_coordinator.py`、`backend/app/character_agent/services/cognition_driver.py`、`backend/app/main.py`、`backend/tests/test_attention_admission_and_recovery.py`、`backend/tests/test_character_cognition_coordinator.py`、`backend/tests/test_character_slow_goal_coordinator.py`、`backend/tests/test_character_slow_goal_driver_dispatch.py`、`backend/tests/test_character_slow_goal_main.py`；继承的 `backend/app/character_agent/models/__init__.py` 未纳入。

- [x] 新增 failed release 与 attention settlement rollback 用例。`test_failed_cognitive_work_releases_its_attention_reservation` 在干净 `cbf47a0a` 基线上因 `attention_release_reason_invalid` 失败，在当前实现通过。
- [x] Task 5 focused regression 为 `150 passed, 6 warnings`；`compileall -q backend/app backend/tests` 与 `git diff --check` 通过。
- [ ] 生产 admission/job 创建仍未接入。当前可运行的 reservation 仅为 test-only；profile、cost、capacity、energy、effort 和模型预算的产品值继续保持 unknown，不能将其写成生产资源策略完成。

**Task 5 全量回归差异记录（2026-11-21）：** 当前工作区全量后端结果为 `10,590 passed, 43 failed, 2 skipped, 2 xfailed`，完整 node id 和输出保存在 `F:/cl-laya-evidence/task5-attention-lifecycle-20261121/`。43 个失败 node 在干净 HEAD `cbf47a0a` 单独重跑后为 `32 failed, 11 passed`；在 Task 1 前的 `30c3ac23` 为 `21 failed, 22 passed`。Task 1 代码点 `25bc89b0` 的差异集合为 11 项，其中 4 项在该代码点失败、7 项在后续提交后失败，具体归因仍须按各测试合同核实。整套运行失败的 11 个 TLS context 用例在隔离 node 回归中通过，显示 suite-order/environment 相关性，尚未定位污染来源。以上比较没有证明当前 Task 5 引入全量回归，也不能代替逐项失败归因；Task 5 保持 `in progress`。

### Task 6：实际动作能力、动态组合与本地执行边界（线 1 后端合同）

**Files:** 上表 skills、L3/L4 和两个 Create 文件；Create `backend/tests/test_action_capability_projection.py`、`backend/tests/test_composite_action_plan.py`。Godot/UE 实现位置由其动作底座子设计列明，不在本任务猜测新增引擎类。

**Owner:** 线 1 Character runtime/action capability owner 冻结引擎无关语义 entry、能力投影、复合计划验证、suggestion 生命周期和私有 percept 投影合同。Godot action-base、HUD/玩家触觉显示、micro-expression consumer、偏好门控、动画/资源接线和运行验收归线 3；UE action-base、adapter、动画/资源接线和运行验收归线 2。线 1 只核查既有引擎接口并输出交接，不修改 UE/Godot 产品代码。表达计划的引擎消费回执分别由线 2/3 实现。

**Interfaces:** `ActionCapabilityProjection` 包含 actor/runtime、语义 action/version、targets、参数 schema/单位/合法值、可用性理由、revision 和 claims；`CompositeActionPlan` 包含可用能力引用、有界步骤依赖、顺序/允许并行、取消窗口及已声明 fallback。把 `family`、逐条 `activation_mode`、`effect_class`、trigger/state 条件和 engine realization support 作为既有能力/资源注册合同的元数据，不另造 dispatcher。`validate_composite_plan(plan, capabilities)` 只校验，不替模型选择战术。

- [x] 写后端结构合同失败用例并运行：能力按 actor、availability、realization 与 revision 筛选；参数缺失/越界、claim 冲突、未登记组合算子、依赖环和 fallback 环拒绝；`move THEN guard` 与兼容 claims 的并行返回 runtime-check warning。该合同只校验，不选择战术或执行动作。
- [x] 结构化能力记录新增 `action_family`、`activation_mode`、`effect_class`、trigger/state conditions；被动条目必须有 trigger，`presentation_only` 不允许 claims。纯结构合同尚未由生产能力源提供，也尚未接入 L3/L4 producer/consumer。
- [ ] **线 2/3 交接，未实现/未运行：** 引擎本地输入在 Laya/provider pending 时的强制反应、transition entry 仲裁、真实资源播放和 owner 回执属于引擎底座。每端需证明 stale capability、装备/资源移除、取消/expiry、claims 冲突和 fallback 失败均不伪造完成；不得把后端结构合同测试记为引擎验收。
- [ ] **线 2/3 交接，未实现/未运行：** `micro_expression_plan` 后端在 `backend/app/character_agent/execution/l4_executor.py` 生成。Godot 线 3 接入 `scripts/character/CharacterActor.gd`、`RolePresentationAdapter.gd` 与合格的本地表现资源，回传 `started/completed/interrupted/suppressed/unsupported`；UE 线 2 复用同一语义与回执字段接入其角色/动画 owner。无 consumer、资源绑定或支持时不得报告成功。自动表现偏好门控只在线 3 consumer 可验证后实施。
- [ ] **线 1 后端缺口：** suggestion 当前只有 `CharacterSuggestionPacket` 下发（`runtime_loop.drain_suggestion_packets`、`main._as_character_agent_suggestion_envelopes`）；没有终态 lifecycle、接受入口或幂等 receipt。packet 未携带服务端 expiry、原始 L3 候选/read-set pins 或 L3/L4 owner receipt。需要先确定 expiry clock/policy，并在原 L3/L4 owner 建立接受复核和 receipt；接受不能合成为玩家命令。**Blocked decision：** suggestion 有效期数值/时钟源没有现成配置，本轮未造默认值。
- [ ] **线 3 交接，未实现/未运行：** Godot `character_agent_suggestion` 当前无消费；待线 1 acceptance protocol 与 owner receipt 合同落定后，再由线 3 在角色 observer/player UI 消费 accepted/rejected/expired/superseded 状态。目标核查入口为 `scripts/ui/CharacterObserverPanel.gd` 与 `scripts/phase0/MainDemoController.gd`；不能把建议显示或点击记录为玩家命令。
- [x] 新增服务端触觉投影模型与白名单函数：仅输出 `intensity_band` 与 `knowability`；actor 不匹配、freshness 非 current/recent、clock domain 不同或过期时不输出；unknown 不猜。focused tests 覆盖引用字段不泄漏。
- [x] **线 1 backend source integration：** `candidate_percept_service.py` 只把已登记的 `state_after=light` 映射为 `light`，其他值保持 `unknown`；只从显式 `ttl_ms` 派生 expiry，并保留 producer clock domain。`per_character_percept_filter.py` 按目标 actor 或 source actor 限制触觉 owner；runtime 仅在 expiry 晚于 producer tick 且有 clock domain 时建立带 `current` freshness 的私有触觉投影。服务端 allowlist 只返回强度档与可知性，并检查 actor、freshness、clock domain 与 expiry。缺失 TTL 时不补默认值且不产生玩家投影。
- [ ] **线 3 producer dependency：** 当前 Godot `TactileFactEmitter.gd` 仍传 `ttl_ms=null`，因此现有 Godot 路径不会产生玩家触觉投影。线 3 需从实际触觉来源提供获准的有效期与同域 clock contract；在此之前 HUD 无 percept 时隐藏。不得以静态后端合同声称 Godot 已接通。
- [ ] **线 3 交接，未实现/未运行：** 消费经授权的 actor-local tactile projection 并仅显示实际强度档/可知性，不显示对象/角色/evidence refs 或全局事实；无 percept、权限不足、unknown freshness、clock mismatch 或过期均隐藏。目标入口为 `scripts/ui/CharacterObserverPanel.gd`、角色 HUD 和 `scripts/phase0/MainDemoController.gd`。当前仓库未发现 tactile HUD consumer；手柄震动/空间音频不在本线实现范围。
- [ ] **线 3 交接，未实现/未运行：** 将 human-controlled actor 纳入同一能力/行为条目 consumer；主动命令与 agent suggestion 来源分开。消费者接通后，由线 3 在现有 settings owner 下实现小动作/微表情/小口癖偏好 gate，验证取消尚未开始的表现而不抑制身体事实、必要反应、正式 gameplay action 或玩家主动输入。偏好粒度、默认值、持久化和同步尚未冻结。
- [x] **现有单动作准入 owner 复核：** production candidate 仍由宿主 `target_catalog` descriptor 提供 admission evidence，`DecisionContext` pin candidate id、definition revision、catalog/capability revisions 与 expiry；L3 只从冻结候选中选择，L4 使用原 execution contract 复核。`test_decision_context.py`、`test_character_capability_action_vertical.py`、`test_character_agent_l3_planning.py` 与 action routing regression 共 `111 passed`。这不代表新增 `ActionCapabilityProjection`/`CompositeActionPlan` 已接入 production L3/L4；复合计划仍是 validator contract，生产 proposal/admission 未完成。
- [ ] 线 1 将能力合同接入原 L3/L4 admission 与每一步开始复核；当前新增模型未被现有 candidate builder / L3 planner / L4 executor 消费，不能标记组合行动准入完成。
- [x] 输出两引擎共用字段表，逐端映射语义 ID/version/units、targets、parameters、availability/revision、claims、commitment/cancel/fallback 与 typed receipt；保留 Godot `CharacterActionAssetDescriptor.gd` 对 `atomic_sequence` 的限制，复合方案不能塞入资产 descriptor。
- [x] 静态核查并形成线 2/3 交接基线；没有修改 UE/Godot 产品代码，也没有运行引擎。
- [x] 运行 Task 6 后端定向回归 `test_action_capability_projection.py`、`test_composite_action_plan.py`、`test_private_percept_projection.py`、`test_character_execution_contract.py`、`test_character_agent_l4_execution.py`、`test_character_skill_service.py`、`test_character_skill_realization_handoff.py`：`87 passed`；`compileall` 与 `git diff --check` 通过。存在 FastAPI `on_event` deprecation warnings。

**Task 6 线路交接（2026-11-21；静态核查，不是引擎验收）**

| 线路 | 已核实入口与 owner | 交付接口/依赖 | 验收证据要求 | 当前状态 |
|---|---|---|---|---|
| 线 1 → 线 2 UE | `D:/Users/User/Documents/Unreal Projects/Guoshang/Source/mcp/Variant_Strategy/BattlePlayerController.cpp` 当前直接处理玩家移动/冲锋输入；`BattleRiderCharacter.cpp` 持有冲锋行为；`BattleUnit.cpp` 引用 `/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed`。本次静态读取未发现通用 Character action capability/adapter owner。 | UE 从当前角色、装备、动作注册和已资格化资源提供 `ActionCapabilityProjection`；本地 adapter 消费 `CompositeActionPlan` 的语义 ID、revision、targets、typed params、claims、expiry/cancel/fallback，并回传 typed realization/authority receipt。资源依赖为已登记骨架 profile、符合该 profile 的 qualified action/animation binding 与其资格报告；具体资源需由线 2 asset owner 选择。 | 编译/automation tests；单角色唯一仲裁、实际能力缺失 fail-closed、每步 revision 与取消复核、owner receipt；UE PIE/真实资源的两角色场景结果。 | **待线 2 实现；未验证。** 本轮未改 UE 文件、未运行 UE。当前 UE checkout `main`，产品代码路径只读。 |
| 线 1 → 线 3 Godot 动作/表现 | `scripts/character/AgentControllerAdapter.gd` 是语义动作入口；`CharacterActionAssetDescriptor.gd` 校验 phase 1 descriptor 并拒绝 `atomic_sequence`；`ActorActionArbiter.gd`/`ResourceClaimScheduler.gd` 仲裁与 claims；`CharacterPresentationAdapter.gd` 是表现接缝；`CharacterActor.gd` 为 actor runtime。 | 从角色当前装备/descriptor/绑定投影可用能力；消费共用复合计划语义字段与取消/expiry/revision；复合步骤保留在 runtime plan，不写进 descriptor。微表现条目须由 presentation owner 消费并回 `started/completed/interrupted/suppressed/unsupported`。 | Godot headless/editor tests；两角色真实场景覆盖无绑定/过期/取消/claims/fallback；至少一个合格微表情与小动作的可见结果和逐项 receipt。 | **待线 3 实现；未运行。** 本轮未改 Godot 文件、未启动 Godot。 |
| 线 1 → 线 3 suggestion | `backend/main.py` 仅下发 `character_agent_suggestion`；Godot 当前无同名 consumer。`scripts/ui/CharacterObserverPanel.gd` 与 `scripts/phase0/MainDemoController.gd` 是 UI/transport 核查入口。 | 线 1 先提供带服务端 suggestion ref/expiry/L3 pins 的 response contract 和持久幂等终态；线 3 才能发送 decision 并显示服务端终态。accept 必须重新经过原 L3/L4 与 owner receipt，不能转译为 `player_input` 或玩家命令。 | 重复 accept/reject 幂等；过期和 superseded 零执行/语音/状态副作用；accept 经 L3/L4 revalidation 并有 owner receipt；Godot UI 显示状态与真实响应对齐。 | **线 1 contract 未闭合；线 3 无 consumer；均未验证。** |
| 线 1 → 线 3 tactile projection | `scripts/phase0/MainDemoController.gd` 绑定 `TactileFactEmitter`；后端从明确的 `state_after`、`ttl_ms` 和 clock domain 构建 actor-private typed percept，再经 allowlist 生成仅含强度档与可知性的输出。当前 Godot emitter 的 `ttl_ms` 仍为空。 | 线 3 `CharacterObserverPanel.gd`/角色 HUD 只消费服务端 allowlist 输出，不能读取 raw fact。线 3 需提供真实有效期和同域 clock contract；手柄与空间音频不属于线 1 实现。 | 同 actor authorized percept 才显示；unknown 保持 unknown；无 percept/权限/freshness/expiry/clock 校验失败隐藏；UI 证据不得含 subject/actor/evidence refs。 | **线 1 后端条件接缝已实现；当前 Godot 输入缺 TTL，故无有效生产投影；线 3 无显示 consumer；两端均未做运行验收。** |
| 线 3 自动表现偏好 | 本次未发现 preference consumer route；`l4_executor.py` 生成 `micro_expression_plan`。 | 等微表现 consumer 存在后由线 3 接 settings owner 的取消代次/偏好 gate。 | 关闭只取消尚未开始的舒适性表现，不改身体事实、受击反应、正式 gameplay action 或玩家主动输入；验证 started 与 suppressed 回执。 | **交由线 3；粒度/默认值/持久化待产品 owner 冻结，未验证。** |

**线 2/3 共用字段映射（合同交接，不表示引擎已实现）：**

| 合同层 | 线 1 语义字段 | 线 2 UE owner 输入/消费 | 线 3 Godot owner 输入/消费 |
|---|---|---|---|
| 能力投影身份与边界 | `actor_id`、`runtime_id`、`revision`、`expires_at`、`max_composite_steps`、`composition_operators`、`conflicting_claim_pairs` | 由当前 UE actor/action owner 按运行时能力、资源与 revision 生成；每次执行前检查 expiry/revision。 | 由当前 `CharacterActor`/descriptor/arbiter 按装备、登记动作与资源绑定生成；每次执行前检查 expiry/revision。 |
| 单项能力 | `capability_ref`、`semantic_action_id`、`action_family`、`version`、`activation_mode`、`effect_class`、trigger/state 条件、targets、availability/reason、realization status/ref、claims、typed parameters（type/unit/range/enum） | 映射 UE 本地语义动作、资格化资源与现有角色/动画 owner；未知或缺绑定时标 unavailable/unknown，不伪造 ready。 | 映射 `CharacterActionAssetDescriptor.gd` 与现有 action registry/arbiter；复合步骤保留在 runtime plan，不写入禁止 `atomic_sequence` 的资产 descriptor。 |
| 复合计划与逐步准入 | `plan_id`、actor/revision、expiry/cancel generation、step id/capability revision/targets/parameters/fallback、`then`/`parallel` edges | UE adapter 在计划启动和每个 step 开始时复核能力 revision、targets、claims、依赖、取消与 fallback。 | Godot adapter 在计划启动和每个 step 开始时复核能力 revision、targets、claims、依赖、取消与 fallback。 |
| 执行回执 | 复用 `CharacterExecutionFeedback` 的 `execution_contract_ref`、`turn_id`、`actor_ref`、lifecycle、`local_feedback_ref`、`authority_receipt_ref`、`authority_status`、reason；复合计划不得另建 writer/receipt owner。 | 每个正式 gameplay step 关联现有 L4 execution contract 与 UE authority receipt；presentation-only 只回本地表现 lifecycle。 | 每个正式 gameplay step 关联现有 L4 execution contract 与 Godot owner receipt；presentation-only 回 `started/completed/interrupted/suppressed/unsupported`。 |

该映射尚未由 UE/Godot 消费者实现验证。唯一发现的 tactile emitter 强度证据为 `light`，线 1 合同当前只接受 `light`/`unknown`；其他强度档须由 percept owner 提供正式词表后再扩展，不得由引擎或 projection 临时解释。

**Task 6 线 1 合同提交（2026-11-21）：** `ea965d02901a44b68ed4c85766884aedb07bf95c` 修改 `action_capability.py`、`private_percept_projection.py` 及三个对应测试文件。Task 6 七文件定向回归为 `87 passed`，`compileall` 与 `git diff --check` 通过；`test_fallback_rejects_unmet_step_dependencies` 先以 fallback 被错误接受而失败，加入已完成步骤校验后通过。私有 tactile projection 只开放 `light`/`unknown` 强度与 knowability，避免任意文本成为玩家可见档位。该提交不接生产能力源、L3/L4 admission、suggestion lifecycle 或 tactile producer。

**Task 6 触觉来源接入复核（2026-11-21）：** `D:/cl-laya` commit `f4e128d2`，改动 `runtime_loop.py`、`candidate_percept.py`、`character_perceived.py`、两个 percept services 和三个对应测试文件；未包含继承的 `models/__init__.py`，未修改 UE/Godot 产品代码。红测先验证未授权 actor 会收到 object-targeted tactile candidate、raw tactile 无法生成 allowlist 输出；改后两项定向测试 `2 passed`。后端/L1/action contract/session recovery 回归 `248 passed, 2 deselected, 5 warnings`，现有单动作 L3/L4 admission 与 routing `111 passed, 5 warnings`；`compileall` 与 `git diff --check` 通过。两个未纳入通过数的 node 为 `test_handle_envelope_raw_visual_fact_matches_legacy_visual_fact_runtime_messages` 和 `test_every_runtime_append_uses_single_transaction_entrypoint`；前者此前已在干净 `088d76ae` 复现，后者检查的两个直接 `append_event` 调用位于本提交未改的路径，Task 8 仍需在全量失败基线中逐 node 复核。Task 6 保持 `in progress`，复合 proposal/admission、生产 suggestion expiry 与 L3/L4 acceptance revalidation 未完成；当前 Godot emitter 仍无 TTL，实际触觉 UI、微表现和引擎验收均交线 3/线 2，未验证。
**Task 6 状态：** 线 1 已完成本地结构合同、fallback 环拒绝和私有触觉投影 allowlist 模型的 focused tests；没有完成生产能力源到 L3/L4 的接线、suggestion terminal lifecycle、suggestion expiry/acceptance revalidation 或 actor-local percept producer 到玩家投影的接线。线 2/3 均只有静态交接，动作/动画/触觉 HUD/微表现和引擎运行没有验收。因此 Task 6 保持 `in progress`，不可勾选成全部完成。

### Task 7：台词、TTS 与动作并行的接缝（线 1 服务端范围）

**Files:** 上表 expression/speech 文件；Create `backend/tests/test_model_speech_lifecycle.py`；复用原 speech lease、提供方和播放/感知路径。

**Owner:** 线 1 Character expression/speech owner 持有台词内容、受众安全、TTS/provider 接缝和 speech lease 生命周期。UE/Godot 音频播放、引擎表现、接收端 perception/understanding 接线及运行验收分别归线 2/3；线 1 定义合成、播放、接收端感知的回执边界并交接，不实现引擎播放代码。

**Interfaces:** Laya 选择语义交流意图；普通模型生成台词；Deep 可提出交流目的和内容提案，仍过同一出口。行为资源可引用 `utterance_templates.v1` 的受限内容或已登记预录音频；条目的 family/mode/effect class 不替代既有内容检查。现有 speech lease 绑定 actor/target/request/expiry；先核实并扩展原 lease owner，使其能为已登记被动 vocalization 表达合法 audience/scope 与 cancel pins，再接触发器；不另建无许可的播放旁路。TTS adapter 只消费已准入文本和稳定 voice profile。

**Task 7b：台词内容与角色化验收。** `share_info` 最少传达一项说话角色有依据、对接收者有用的具体信息，能回答发生了什么/在哪里/针对谁/当前状态/风险或需要之一；明确区分已感知事实与推断并保留不确定性。内容只能来自角色已感知、已提交或获准使用的事实/记忆/推断，经过事实、时效、受众与隐私检查。没有实质信息时拒绝 `share_info` 内容，允许改选其他合法意图或沉默；不得退回“我有一件事要告诉你”等空泛模板。质量验收使用同一事件和不同角色各自可用证据，检查内容有根据、有差异且不矛盾，并要求无有效信息时沉默。不得为了差异性编造建议或事实。

- [ ] 写失败用例并运行：动作先行、台词 pending；旧承诺取消后才生成的台词不合成/不播放；已合成但过期的音频不入播放队列；Deep 不绕过受众/事实检查；移动和语音按 claims 并行。
- [ ] 为 Task 7b 写内容级验收：有具体可追溯信息、带不确定性的推断、无有效分享内容时不说 `share_info`；同事件三角色依据各自可见事实/记忆形成有差异且不矛盾的台词。审阅中确认的空泛台词必须被拒绝；表达风格不得覆盖事实和权限边界。
- [ ] 覆盖同一 transition utterance family 的主动与被动 entry：受击痛声/短促惊呼/无命题应声只能由明确触发条件使用登记内容、不等待模型；缺绑定/模板/音频/合法 audience lease 时抑制；命令、警告、欺骗、承诺、谈判和策略消息不能走 passive path。
- [ ] 对 human-controlled actor 应用同一 speech lease、受众与取消规则；玩家可关闭自动口癖/被动短语而不影响玩家主动输入。设置变更后尚未播放的旧 generation/lease 必须按原取消代次作废，已经播放的事实保留。
- [ ] 分别断言 utterance proposal、内容审查、TTS synth、audio playback、receiver perception/understanding 状态；旧输入/target/lease 过期后不启动，已发生播放事实不因取消删除。Active generation 使用原 attention task admission；passive trigger 不建主动认知 reservation，但不宣称零系统资源成本。
- [ ] 连接新模型 producer 和原 utterance/lease 入口，传播取消与 expiry；保留已完成的 ASR/TTS provider。流式首段、已播放片段和对方感知分别记证据，取消不删除已实际听到的片段。
- [x] 运行上述 Task 7 指定回归并扩展覆盖 `test_expression_loop_p3_delivery.py`、动作路由和 skill shadow；结果 `345 passed`，`compileall` 与 `git diff --check` 通过。回归中的 TTS stub 不构成真实 provider、UE/Godot 播放或接收者感知验收。
- [x] 线 1 为 `share_info` 增加冻结 proposal 合同，绑定 actor/target、producer/task、可得 model ref、source 与 recipient-relevance refs、revision pins 和单调时钟有效期；L4 出口校验权限、来源、受众相关性、时效和版本。无 proposal、裸文本、陈旧/过期提案和规格已列明的泛化正文不会成为 `share_info` 台词。普通/Deep producer 尚未接入该入口。
- [x] 线 1 的语音响应按 actor/请求/目标固定 audience plan 并持久保存合成响应；相同请求重放返回既有音频，不重复合成；同一请求改写文本在 TTS 前拒绝。后端不再从合成结果直接写接收者 auditory percept，接收者输入须来自引擎实际感知路径。
- [ ] L4 execution 尚未复用 `DialogueCoordinator` 的 `SpeechLease`。该 Coordinator 自有的 queued/expired/cancelled TTS 测试通过，但不能证明 L4 speech 的 lease、取消代次或动作并行。无 lease 时的 L4 TTS 生产门仍未闭合。
- [ ] Task 7b 的三角色内容质量、普通/Deep 生产生成、事实/推断差异与一致性审阅未完成；本轮只拒绝已确认的泛化示例，不能据此宣称通用语义质量判定完成。
- [ ] 合成、引擎播放、接收角色的感知/理解仍是分开的验收门。本轮只完成线 1 的冻结受众与合成响应 receipt，没有接收 playback 或 perception receipt。

**Task 7 线路状态与交接（2026-11-21；静态核查，不是引擎验收）**

| 状态/线路 | 已核实入口与交接内容 | 依赖与验收证据 | 当前结果 |
|---|---|---|---|
| 线 1 已完成 | `backend/app/character_agent/models/speech_content.py`、`expression/utterance_composer.py` 与 `execution/l4_executor.py` 提供 source-pinned `share_info` 合同和 fail-closed 出口。`backend/app/services/character_expression_delivery.py` 只冻结并记录受众资格；`backend/app/main.py` 对精确响应重放复用持久音频，对身份相同而文本不同的请求先拒绝。 | 指定后端回归 `345 passed`；`compileall` 和 `git diff --check` 通过。 | 部分线 1 合同完成；Task 7 整体仍 `in progress`。producer 和 L4 lease 尚未接入。 |
| 交由线 3 Godot | `scripts/autoload/BackendBridge.gd` 收到 `dialogue_response` 后发 `dialogue_received`；`scripts/character/CharacterActor.gd` 的 `apply_dialogue` 调用 `SpatialVoiceController.play_voice`；`scripts/audio/SpatialVoiceController.gd` 解析/播放 WAV 或 stub，开始播放时调用 `AuditoryFactEmitter`；`scripts/l1/facts/emitters/AuditoryFactEmitter.gd` 输出 speaker-active、reachability 和 ambient-noise raw facts。`scripts/verification/verify_tts_godot_playback.py` 与 `TTSGodotLivePlaybackProbe.gd` 是现有真实播放验证入口。线 3 需把 speech/action ref、target、lease/取消状态贯穿本地播放，区分 accepted/started/completed/interrupted，并由接收者实际感知事件进入 L1；当前 emitter 的播放开始信号不证明完整播放或 receiver understanding。 | 依赖有效 voice profile、provider 生成的合格 WAV、actor 的 SpatialVoiceController 和连接的 AuditoryFactEmitter。验收需两角色真实场景，覆盖过期/取消、实际播放 start/completion、受众资格和接收者 L1 percept 来源；如要求理解，再单独提供理解证据。 | 交由线 3；本轮没有改 Godot 代码或运行 Godot。 |
| 交由线 2 UE | 对 `D:/Users/User/Documents/Unreal Projects/Guoshang/Source` 的只读搜索未找到 `dialogue_response`、TTS payload、speech playback 或 receiver-perception adapter。由线 2 选择角色/音频 owner 接收共享 response/lease 语义，绑定 actor、target、request/ref、expiry/cancel generation 和播放 receipt，不把合成成功视为播放。 | 依赖线 2 选择并资格化的 voice/audio resource、角色音频播放 owner 和接收者感知 owner。验收需编译/automation 与 UE PIE 两角色场景，提交 start/completion/interruption 和接收端感知证据。 | 交由线 2；本轮没有改 UE 代码或运行 UE。 |
| 尚未验证 | 普通/Deep 文本 producer 到 proposal 的真实运行、L4 speech 对 `DialogueCoordinator` lease 的复用、动作已提交而台词 pending 的并行、取消/expiry 后零 TTS、response commit-before-response crash、流式已播放片段、真实 TTS provider 与接收者感知/理解。 | 普通/Deep provider role 配置和可审计 model/effort evidence；L4 可用 deadline/lease owner 接口；端侧 voice/audio 资源及引擎运行环境。 | 不得由本轮后端测试或本地 TTS stub 标记通过。 |

**Task 7 本轮提交记录（2026-11-21）：** `cbf47a0a`，提交 `Add source-pinned speech content proposals`。改动文件为 `assets/dialogue/utterance_templates.example.yaml`、`backend/app/character_agent/execution/l4_executor.py`、`backend/app/character_agent/expression/utterance_composer.py`、`backend/app/character_agent/models/speech_content.py`、`backend/app/main.py`、`backend/app/services/character_expression_delivery.py`、`backend/tests/test_character_agent_action_request_routing.py`、`backend/tests/test_character_skill_runtime_shadow.py`、`backend/tests/test_expression_loop_p3_delivery.py`、`backend/tests/test_expression_loop_speech.py`、`backend/tests/test_model_speech_lifecycle.py`。Task 7 focused 回归 `118 passed`；扩展 speech/dialogue/TTS/lease/L4 回归 `649 passed, 2 failed`。两项失败 `test_cancelled_completion_is_zero_write_and_cannot_release_next_token[dialogue_generation]`、`...[tts]` 在干净 Task 6 HEAD `ea965d02` 上同样失败，不能计为本提交回归。`compileall` 与 `git diff --check` 通过。继承的 `backend/app/character_agent/models/__init__.py` 未纳入提交。Task 7 仍 `in progress`；上述普通/Deep producer、L4 speech lease、动作并行、取消/过期和 crash 边界继续列为未验证，UE/Godot 播放与接收端感知继续分别交线 2/3。

### Task 8：阶段一后端闭环与 CPU 测量（引擎门另行交接）

**Files:** evaluation、planned verification script、本规格/计划和专项计划；真实证据按目标仓库 retention/export 规则存放。

**Owner:** 线 1 Character runtime/evaluation owner 固定后端输入轨迹、CPU/checkpoint/输入输出分布及可持久化账本证据。UE/Godot action-base owners 分别承担引擎能力、动作承诺和本地表现验收，依赖资源与证据单列交接，不以模型输出或后端测试替代引擎回执。

- [ ] 建立受控酒楼轨迹：仇家出现 → 抬刀 → B 到门侧掩护并提醒 → A 改从窗口离开 → B 重选 → A 脱险。逐项记录 B 私有输入、Laya 候选/choice、普通/Deep 分析、S4/N1 提案、状态 revision、动作承诺与 authority receipt。
- [ ] 使用既有已批准评测夹具与 pin 做质量/性能比较；不得在本任务中静默刷新 fixture hash。若原夹具任务仍未闭合，先报告其基线差异和依赖，不把新建酒楼轨迹当作原夹具的替代品。另建带可审查选择标准的场景质量集，区分安全/低风险、可撤销与高风险/不可逆变化；扫描 `p_max`/熵只作诊断指标，不能替代正确性标签或单独控制准入。
- [ ] 使用 Task 1 当前投影扫描结果与已批准评测夹具进行正式质量/性能对照；不得静默刷新 fixture hash。另建带可审查选择标准的场景质量集，区分安全/低风险、可撤销与高风险/不可逆变化；扫描 `p_max`/熵只作诊断指标。
- [ ] 用同一酒楼轨迹、输入/随机种子和可见证据，对比总体规格 §6.2.1 的四类角色组合：经验丰富/流体普通、经验不足/流体强、经验与流体强且容量恢复高、流体强但当前过载。分别记录已登记技能/evidence、动作能力投影、每项任务 reservation/settlement、ambient load、可并行工作、拒绝/暂停/partial、负荷解除和精力恢复；不得以角色描述替代运行数据。
- [ ] 覆盖行动自动化与并行失败：无 registered expertise、动作未出现在当前能力投影、动作承诺窗口不允许修改时，模型不得调用脚本/动作；动作本地持续推进不扣连续思考成本；没有 attention admission 时 Deep 不得启动；释放未决负荷不能返还已消耗精力，恢复也不能由 provider wait 或模型文本触发。
- [ ] 按总体规格 §11.1 逐条验收八个场景：本地受击反应、被动动作过渡、主动过渡表现、疼痛/惊吓/用力短声、自动应声/预设短语、主动警告/下令、失效后抑制、过渡动作升级正式 gameplay contract。分别保存 actor/entry/trigger/mode/family/ability or lease revision、attention reservation、执行阶段、owner/audio/perception receipts 与拒绝原因。
- [ ] 加入 human-controlled actor 验收：确认角色仍接收私有 percept；嗅觉/触觉/热觉/味觉的 raw fact、actor-local percept、玩家可见反馈分开记证据；前三种已有部分代码通路，味觉和玩家呈现仍需实现；无 percept、unknown 或权限不足时不把全局事实显示给玩家。
- [ ] 验收微表现完整生命周期：同一玩家偏好与状态输入下，开启时 consumer 确实表现已绑定的微表情/小动作并返回回执，关闭时表现被抑制并返回原因；身体事实、必要反应、正式 gameplay action 和玩家主动命令仍有效。分别验证未绑定资源、引擎不支持、取消代次过期和动作仲裁冲突，不把计划生成/排队当执行成功。
- [ ] 两个 transition families 各准备主动和被动 entry；forced-reaction family 只允许 passive entry。验证角色没有绑定、资源版本/引擎实现缺失、受众无效、取消代次过期、多角色专属资源串用时 fail closed。文档和离线合同通过不能代替 UE/Godot 实际运行、真实 TTS、接收方听见/理解证据。
- [ ] 冻结 CPU、checkpoint、输入字段包络和任务；扫描 state 长度及输入频率，记录质量/时延/排队/取消/多 actor 容量。把测量起止点、毫秒通过线、token 上限、队列/Deep 容量提交为明确决策；未批准数值前只标 measured，不能通过性能门。
- [ ] Godot 先以两角色验证语义合同与真实执行；UE 按其底座计划复用同一合同和场景断言，独立提供运行/PIE 和后端回执。某端能力缺失时保持该端 blocked/unverified，后端 contract pass 不冒充引擎通过。
- [ ] 运行阶段一新用例和相关回归；跨 runtime/store 的广泛改造按目标仓库要求运行后端全测及 `python scripts/verification/harness.py --profile all`。导出本轮证据，分类记录旧失败与新失败，不改旧 fixture/hash 掩盖差异。

**阶段一出口：** 完整 L2 保留；当前动作不等完整分析；Deep 能力矩阵、typed consumer、认知资源 reserve/settle/recovery、写回/恢复和动作合同有证据。玩家角色的控制权与 agent suggestion 边界、嗅觉/触觉/热觉 actor-local 感知、微表现真实 consumer 与回执分别列证据；味觉和玩家感官呈现未完成时保持开放。自动表现关闭选项只有在 consumer 的实际抑制路径验收后才能标记通过。CPU SLO、Godot、UE、音频各有单列门，不以其中一项通过代替其余。进入阶段二可基于后端合同门安排开发，但不提前宣称阶段一全部验收通过。

## 阶段二：Laya 接入 Agnes 式工具循环

### Task 9：操作候选来源与逐步返回 Laya

**Files:** 上表 collaboration 两个 Create 文件、gateway 和 coordinator；Create `backend/tests/test_laya_model_collaboration_loop.py`；承接 typed 子计划 Task 5，不另写第二套循环。

**Interfaces:** `CollaborationOperation` 登记 operation ID/version、输入/输出 schema、权限、budget、取消及可见性；`CollaborationStep` 冻结候选映射和 read-set；`CollaborationResult` 引用工具 receipt/模型输出；`advance_collaboration(...)` 在原 coordinator 内推进一步。普通模型可提出参数、命题和动态组合，校验后才能成为新的冻结候选。

- [ ] 写失败用例并运行：候选由登记操作＋当前目标/状态/工具能力投影形成；未知工具/权限不足/参数不完整不可选；Laya 的 choice 只能映射原候选；空候选明确结束，不猜操作。
- [ ] 登记逻辑操作：读取许可证据/记忆/能力、请求普通模型、请求 Deep、运行已登记 typed task、提出认知/行动方案、结束/报告 partial。每项写明实际 consumer、参数来源和限额；阶段一 API 与提交边界保持复用。
- [ ] 接通 `Laya 选择操作 → 工具或模型执行 → typed result → 新 step 冻结 → Laya 再选择`。有界循环节点送 Laya；工具内部分页/格式化、Deep 内部分析与身体原子动作不强制逐次返回 Laya。
- [ ] 运行 `python -m pytest -q backend/tests/test_laya_model_collaboration_loop.py backend/tests/test_cognition_model_collaboration.py`（后者由 typed 子 Task 5 交付）；验证两套测试用同一循环实现后提交。

### Task 10：闭环中的并行、取消、执行窗口与恢复

**Files:** collaboration、coordinator/driver、store、L3/L4 和 speech lease；Create `backend/tests/test_collaboration_recovery_and_execution.py`。

**Interfaces:** step/job/proposal 保留各自原 source/read-set/expiry/cancel pins；loop revision 不是刷新旧证据的授权。行动提案只有经有效 L3/L4 窗口接纳才产生承诺，分析循环自身无执行权。

- [ ] 写失败用例并运行：工具等待期间有效承诺继续；新输入唤醒当前决策；旧 loop 不能挤占最新决策；Deep 返回后 Laya 可继续取证或修订方案；预算耗尽/递归 Deep 明确 partial/reject。
- [ ] 连接跨模型/工具/台词取消；玩家打断或新证据使原 read-set 过期时，旧 step/proposal 零写。可继续的分析必须重新冻结输入，不能改旧请求的版本来绕过检查。
- [ ] 补故障恢复轨迹：工具返回后提交前崩溃、认知提交后响应前崩溃、动作提交后循环恢复；复用 receipt，不重复评分写回、发言或执行。禁止自动回滚已发生世界效果。
- [ ] 运行 `python -m pytest -q backend/tests/test_collaboration_recovery_and_execution.py backend/tests/test_cognition_completion_revision.py backend/tests/test_character_cognition_stage_store.py backend/tests/test_model_speech_lifecycle.py`；记录结果再提交。

### Task 11：新旧架构对比与总体验收

**Files:** evaluation、`scripts/verification/verify_fast_thinking_chain.py`；本总体规格/计划、typed 子计划、主路线和对应实现报告。

- [ ] 固定同一酒楼轨迹/角色可见证据/UUID，对比旧同步 L2→L3、阶段一并行、阶段二协作循环：首个合法承诺时间、L2 能力保留、后续改策、工具往返、stale 拒绝、认知/动作/语音重复效应。区别“记录的历史基线”和“本轮实跑”，不重解释旧证据。
- [ ] 分开验收 choice 正确候选映射、score 尺度/分布与消费者、noul 极性/校准、普通/Deep 的证据质量；按已批准 CPU SLO 报 p50/p95/p99、冷/热、多角色、队列和取消率。性能或质量未过则保留该门未完成。
- [ ] 运行全部新增 focused/contract 用例及因跨域改造要求的后端全测/`harness --profile all`；另列真实 provider、Godot、UE、TTS/播放/听见证据，记录运行环境、版本和原始结果，不以离线桩替代。
- [ ] 按 `planned → implemented-focused-verified → real-provider-verified → consumer-accepted` 更新实际项；总体运行状态只在所有适用门通过后改为 accepted，开放数值或缺失引擎证据不得标成完整完成。

## 开放决策与阶段门

| 未定内容 | 负责人/落点 | 冻结期限 |
|---|---|---|
| 认知精力量表、任务成本映射、容量/ambient load 折算与恢复条件 | attention owner + profile/content owner 以 Task 2 证据收敛；用户批准角色属性范围 | 生产 admission 开启前；冻结前只允许显式 test-only 的结构性合同验收，数值保持 unknown |
| 外部恢复倍率范围、来源组合/上限、药物与环境效果的时效及回放 | attention owner + status/effect-system owner；总计划 Task 2 | 外部修正接入或持久化前；须有 source/revision/effect interval 与幂等恢复证据 |
| 有意识并发上限、优先级、Deep outstanding/每项工具工作预算 | Character runtime owner 依 Task 2/5/9 负载和任务语义冻结 | Task 2/5/9 真实 admission 启用前；不以任意默认值宣布达标 |
| 主观费力的 `score` S8 consumer | cognition/content owner 先证明后续理解、表达或复盘 consumer；运行时账本不可作为 consumer | 无具名 consumer 时 deferred，不发 score task |
| 快路径风险/可撤销分级、无承诺时保守行为、正式质量集与质量通过线；latency 起止点、毫秒 SLO、token 包络 | 用户已决定：质量证据不足时限制为宿主校验的低风险可撤销动作，高风险/不可逆动作补证据或更完整分析；扫描分布不作置信门槛。玩法语义和数值由 Task 8/原 owner 冻结 | Task 3/4 实现分级提交接缝；Task 8 前冻结质量集与运行时分类合同，正式性能验收前冻结数值 |
| 动作承诺默认值、复合算子/参数档、Godot/UE adapter 接口 | 动作底座 owner 按 Task 6 要求补充各端规格 | 对应能力进入真实候选前 |
| 各认知维度 producer 交接、严格 read-set 的细化范围 | 原 Character/state owner；与 typed 子计划共用 | Task 3 对应消费者启用前 |
| 真实 provider model/effort 支持与预算 | gateway owner 实测并 pin 配置 | Task 5/8/9 真实模型验收前 |

## 回退与状态更新规则

按原 admission/task 配置停用新增 producer/协作操作；显式交回认知字段生产权。保留已提交状态、ledger、receipt、旧事件 reader、当前有效动作及原 choice 路径；不删除历史事件，不倒回世界事实。新作业取消后允许原连续性兜底继续，失败原因明确可查。

本文件编写完成只代表总体实施工作已拆清。本轮不执行以上产品代码、模型启动、引擎操作、训练、提交或发布。总体规格与本计划是入口，typed 子规格/计划负责细分任务，旧草案保留历史含义。
