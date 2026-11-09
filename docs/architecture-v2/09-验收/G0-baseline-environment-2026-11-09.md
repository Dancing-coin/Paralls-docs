# G0 基线环境记录

- 日期：2026-11-09；执行者：Codex。基线取证完成状态以复现比较为准；G0/G1 放行状态见检查清单。

## 代码与范围

- 原路径 `D:\Paralls-phase0-1` 不存在；实际仓库 `D:\Users\User\Documents\paralls-phase-0-demo`。
- 按用户“拉取远端更新”要求，从 `d77d9db6` fast-forward 19 个提交到 `5321266dbd882f45eb6a24dd7b328e9f56746228`；没有合并提交或 runtime 修改。
- 提交：`5321266dbd882f45eb6a24dd7b328e9f56746228 2026-11-08 22:54:27 +0800 docs(siming): 生成另一个AI的执行提示词`。历史 `c5f249bd` 是祖先；历史 201 失败不能推断为当前数量。
- 当前 gameplay：139 个 Python 文件，82358 物理行（bytes.splitlines）。
- 正式范围：冻结 `backend/tests/` 全部 1025 个 `test_*.py`，实际收集 9899 节点；不是旧 15 域/624 文件集合，也不覆盖根目录 scripts 的独立测试/Harness/Godot/UE 验收。
- 示例 `backend/app/gameplay/tests/` 不存在。真实入口是 backend cwd 的 `tests`。

## 环境身份

- OS：`Windows-11-10.0.26200-SP0`；Python：`3.13.5 | packaged by Anaconda, Inc. | (main, Jun 12 2025, 16:37:03) [MSC v.1929 64 bit (AMD64)]`；解释器：`C:\Anaconda3\python.exe`。
- pytest 8.3.4；本机 Python 3.13.5 与 CI 3.12.14 不同；已安装 httpx 0.27.2 与 CI constraints 0.28.1 不同。本轮未安装/升级依赖。
- 根与 backend 均无 requirements.txt。pyproject SHA-256：`ea0dc383dd38e41c101966e74b9499d298e99c76e327c159ae217508a0c57d83`。
- ci-constraints SHA-256：`bf34995ef8447063d664ace8a687469af24eb0347d6c0f0d4caec3c3fb34f98b`。
- 已安装全部 distributions 的版本与 SHA：`615736489422a2cb7a7527a160c4142c0b9a8471dc5f489147e67ee43422e2c1`，见 [环境快照](G0-20261109-5321266d/run1-full/environment.json)。这是可比环境记录，不是可移植容器或锁定镜像。
- 测试文件内容哈希清单：[test-files.json](G0-20261109-5321266d/run1/test-files.json)；后端 app 源文件哈希在每轮 environment.json，含运行前后 Git/HEAD 检查。
- 释放内存后继续；正式测试串行执行。没有启动 UE、导入、美术构建或显存操作。最终资源观测见 final-verification.json。

## 命令与结果

在文档仓库执行以下命令；runner 将 cwd 切换为 backend，给当前进程 sys.path 前置 backend 和 repo。子进程不继承这种 sys.path 注入，这正是数个已保留环境失败的根因。

```powershell
python "docs/architecture-v2/09-验收/G0-20261109-5321266d/run_baseline.py" --repo "D:/Users/User/Documents/paralls-phase-0-demo" --output "<新的绝对证据目录>" --manifest "<绝对路径>/G0-20261109-5321266d/run1/test-files.json"
```

底层 pytest：`pytest tests -v --tb=short -p no:cacheprovider --junitxml=<output>/junit.xml`。新 output 必须不存在；原捕获不可覆盖。

- 第一轮：本地 14:19:17–14:43:19；pytest 1436.03 秒。**9787 passed、108 failed、2 skipped、2 xfailed，总计 9899**；收集错误 0；退出码 1。
- runner 统一 outcome 将 xfailed 归入 skipped，故 results.json 是 skipped=4；细分以终端与 JUnit 为准，不是计数冲突。
- 第二轮：14:43:40–15:10:20；两轮均为 9787 passed、108 failed、2 skipped、2 xfailed，9899 节点。收集顺序、失败顺序、失败 outcome、错误类型/阶段一致；源、依赖与清单哈希一致；无收集错误、代码变更或状态漂移。精确差异见[复现比较](G0-20261109-5321266d/reproducibility-comparison.json)。
- [第一轮日志](G0-20261109-5321266d/run1-full.log)、[结果](G0-20261109-5321266d/run1-full/results.json)、[第二轮日志](G0-20261109-5321266d/run2-full.log)。早期 run1/ 是中断的收集/试运行，smoke/ 是小样本，均不计正式结果。

## 比较规则

build_report.py 的 `g0-stack-v2` 规范化绝对路径（含 repr 双反斜线）、pytest 临时计数器、内存地址、asyncio 明确格式 `Cancelled by cancel scope <hex>` 中的运行时对象 ID、ISO 时间。第二轮唯一原始堆栈差异是 anyio `_backends/_asyncio.py` 生成的该 ID（见本机 anyio 源 575 行）；规范化后为零堆栈差异。保留错误类型、阶段、行号、语义值、UUID、摘要与断言差异。原始捕获哈希仍在 raw_capture_stack_hash；两轮使用同一规则比较，原始证据不覆盖。

相同失败节点/顺序和类型只是第一层；堆栈语义差异必须逐项说明，不能用宽泛正则删掉。当前比较状态：`compared`。技术负责人审批和独立缺陷修复尚未完成。
