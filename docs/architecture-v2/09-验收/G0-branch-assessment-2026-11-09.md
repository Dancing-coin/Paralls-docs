# G0 阻塞与已有分支核验

- 日期：2026-11-09；用户要求保留分支，不合入 main。
- 当前 main：`5321266dbd882f45eb6a24dd7b328e9f56746228`；分支 `origin/refactor/shared-owner-base`：`f89e7380`；共同祖先 `c5f249bd`。main 独有 117 个提交，不能把旧分支的通过直接当作当前版本验证。
- `origin/baseline/env-fix`：`7ad6e2a3`。它提供 `backend/conftest.py` 中 backend/repo 的父进程导入路径；`refactor/shared-owner-base` 有相同内容。它不处理 cwd 相对路径、子进程继承或所有依赖差异，不能据此消除全部 43 项环境分类。
- 上述分支都保留为有用的现有成果；未合并、未修改 main。

## 对 G0 阻塞的证据

| 阻塞 | 分支核验 | 当前版本结论 |
|---|---|---|
| B1 坏幂等收据引用 | 独立提交 `5271d700` 为 package exchange duplicate 增加事件解析、事务一致性与重复引用校验；分支上对应坏引用测试通过。 | 补丁干净应用于 `5321266d` 的隔离副本后，39 项定向回归中该项由失败变通过，38 passed、1 failed；唯一失败是基线已存在的 economy replay fixture 装配问题，无新增失败。**是可移植的候选修复，不是已在 main 修复或 G0 放行。** |
| B2 角色记忆投影 | 旧分支 `test_actual_interaction_failure_reaches_l3_and_new_evidence_clears_recheck_reason` 仍失败。 | 未解除。L3 分支变更存在，但未消除该实测失败。 |
| B3 对象持久化提交 | 旧分支 `test_worktable_finish_use_requires_the_authority_committed_engaged_state` 仍抛 `esm_object_durable_settlement_required`。 | 未解除。 |
| B4 恢复身份/投影契约 | 旧分支两个基线失败用例通过，但它使用按源码指纹算法；main 后续 `f1e18067` 切换为手工语义指纹。旧分支另有两项恢复套件失败。 | 旧算法可作为权衡参考，不能据此判定当前语义指纹契约已解决，也不能直接回退已发布的恢复身份行为。 |

## 范围与后续

`5271d700` 的验证只接入 `_package_exchange_duplicate_result`，不证明其他域的重放路径均具备相同校验。拒绝码与事件读取开销等仍应在独立缺陷轨道审查。共享 Owner 基类、摘要、replay、batch 和读缓存的既有实现可作为 G1 输入，但必须按当前版本重新比较领域摘要、revision、回执和副作用语义；B1 修复与 G1 结构迁移保持分轨。

建议顺序：在独立缺陷分支移植并审查 B1，补充事务/重复引用/空引用等反例并运行相应回归；分别处理 B2/B3 和裁决 B4；之后重新冻结基线与阶段门，保留对现有共享基类的比较。不把这份定向检查视为完整 backend、CI、UE 或 G1 验收。

## 原始证据

- [旧分支定向日志](G0-20261109-5321266d/branch-review-shared-owner.log)：111 passed、4 failed；包括 B1–B4、整个相关测试文件和角色 candidate compiler。
- [旧分支机器结果](G0-20261109-5321266d/branch-review/shared-owner-targeted/results.json)。
- [B1 补丁应用于 main 隔离副本的定向日志](G0-20261109-5321266d/branch-review-b1-on-main.log)：38 passed、1 既有失败。
- [移植后机器结果](G0-20261109-5321266d/branch-review/b1-on-main/results.json)，以及[原基线](G0-20261109-5321266d/run1-full/results.json)。测试 outcome 逐项比较只有 B1 从失败变通过。
- 隔离 worktree：`D:/Temp/paralls-g0-branch-review-20261109`（旧分支，干净）、`D:/Temp/paralls-g0-b1-on-main-20261109`（当前 main + 未提交的 B1 补丁）。后者仅供核查，不是合入或交付分支。
