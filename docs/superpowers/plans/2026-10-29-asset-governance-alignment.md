> 文档状态更新：2026-10-30。资产治理建设计划，保留待办与历史依据；不是治理验收通过记录。当前资源规范与manifest继续由art_resources维护。 当前规格见[PRD导航](../../PRD/README.md)；[县城执行计划](../../production/县城守城Demo执行计划.md)。

# 召陵县资产治理对齐实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 让建筑资产构建方案、召陵县场景需求、角色需求和资源登记使用同一套权威关系、批次范围、资产身份和文件生命周期。

**Architecture:** 建筑资产构建方案只定义跨场景的建筑技术规范；场景和角色文档只引用这些规范并定义各自的交付范围；资源管理以 manifest 为单一事实来源，登记表只做索引，证据和回退版本与 manifest 绑定。

**Tech Stack:** Markdown、YAML 模板、PowerShell 文本检查；不改 UE 资产、关卡或运行时代码。

**Spec:** `docs/PRD/玩法系统/建筑资产构建方案.md`、`docs/PRD/玩法系统/06-召陵县第一阶段Demo场景素材需求.md`、`docs/PRD/玩法系统/07-召陵县第一阶段Demo角色素材需求.md`

## Global Constraints

- 建筑通用技术规则只在建筑资产构建方案中定义。
- `building_id` 是稳定数据身份，文件名和 UE 对象名只是映射对象。
- 源文件和已批准版本不可覆盖；替换必须产生新版本并保留回退关系。
- 未有来源、依赖、UE 路径和验证证据的资产不得进入“已验证”或“已用于 Demo”。
- 不修改 `/Game/TopDown/Lvl_TopDown`，不导入或批量生成 UE 资产。

## Review Focus

- S1 垂直切片与完整 S1 是否被错误合并；检查场景批次表和完成定义。
- L0 60 件基线与 60—80 件扩展目标是否统一；检查数量表和建筑方案引用。
- 里区块边界与内部 Level Instance/PLA 数量是否被混为同一概念；检查流送章节。
- manifest 是否记录依赖、证据、校验和和回退，而不只是命名；检查资源管理章节和模板。
- 建筑方案、场景需求和角色需求之间是否存在重复字段或相互覆盖；检查文档关系表和链接。

---

### Task 1: 建筑规范权威层级

**Files:**
- Modify: `docs/PRD/玩法系统/建筑资产构建方案.md`

- [x] 增加文档权威范围、冲突裁决、`building_id` 与资产对象映射、里边界和内部包结构说明。
- [x] 增加几何、HLOD、FastGeo、OFPA、Data Layer 和自动检查规则的“下游必须继承”声明。
- [x] 增加资源 manifest 与建筑方案的接口字段，避免在场景文档复制技术参数。

### Task 2: 场景范围与批次对齐

**Files:**
- Modify: `docs/PRD/玩法系统/06-召陵县第一阶段Demo场景素材需求.md`

- [x] 将 S1 拆成批次 A 垂直切片和批次 B 完整核心，修正“L0-L4 完整实现”的歧义。
- [x] 将 L0 统一为 60 件基线、60—80 件扩展目标，并给 L2/L3/L4 项目增加批次标签。
- [x] 将建筑技术参数改为引用建筑方案，只保留召陵县数量、区块、功能和验收差异。
- [x] 增加场景资产与 manifest、依赖图、证据和回退位置的绑定要求。

### Task 3: 角色文档接口统一

**Files:**
- Modify: `docs/PRD/玩法系统/07-召陵县第一阶段Demo角色素材需求.md`

- [x] 角色资产包改用统一 manifest、状态流转、证据和回退规则。
- [x] 明确角色的 `asset_id`、角色身份 ID、UE 路径和 gameplay 组件接口不互相替代。

### Task 4: 资源生命周期与 manifest

**Files:**
- Modify: `docs/art_resources/README.md`
- Modify: `docs/art_resources/asset_registry.md`
- Create: `docs/art_resources/asset_manifest_template.yaml`

- [x] 定义 source/staging/approved/deprecated/evidence/manifests 的目录契约和不可覆盖规则。
- [x] 将登记表改为 manifest 索引，补充依赖、校验和、批准、证据和回退字段。
- [x] 提供可复制的 YAML manifest 模板。

### Task 5: 文档一致性验证

**Files:**
- Test: Markdown 链接、重复 `building_id`、关键术语和 manifest 字段检查

- [x] 检查本地 Markdown 链接存在。
- [x] 检查关键权威术语、批次名称和生命周期状态在相关文档中一致。
- [x] 检查没有将 Low Poly 重新写成阶段一目标，也没有新建 UE 资产或修改关卡。
