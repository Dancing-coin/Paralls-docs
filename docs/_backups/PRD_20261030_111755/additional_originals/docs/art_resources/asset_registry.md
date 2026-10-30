# 资源 Manifest 索引

本表只索引 manifest，不替代 manifest 中的事实字段。每一行必须能定位到 `docs/art_resources/manifests/<asset_id>/<version>.yaml`；没有 manifest 的资源只能保持“候选”。

## 索引字段

| 字段 | 要求 |
|---|---|
| `asset_id` / `version` | 稳定资产族 ID 与不可覆盖的版本号 |
| `building_id` / 角色身份 ID | 建筑或角色的玩法身份；非适用类型留空 |
| 批次 / 区块 / 类型 | 对应场景或角色需求的交付范围 |
| manifest 路径 | `manifests/<asset_id>/<version>.yaml` |
| 状态 | 只能使用 README 定义的生命周期状态 |
| UE `/Game/...` 路径 | 实际导入结果，不填个人电脑绝对路径 |
| 依赖 / 证据 / 回退 | 指向 manifest、evidence 和 rollback target |

| 资源 | `asset_id` / 版本 | 来源 | 类型 | 当前状态 | manifest / UE 路径 | 阶段目标 | 备注 |
|---|---|---|---|---|---|---|---|
| `战士.fbx` | `candidate-warrior` / `v0` | `F:\download\4169  中式古代人物出征大军骑兵士兵骑马弓箭手官兵SU模型C4D素材(1)\S861\中式古代人物_出征大军_骑兵_士兵_骑马人SU模型` | FBX，约 67MB | 候选 | `manifests/candidate-warrior/v0.yaml` / 待导入 | 阶段二单文件验证 | 先检查骨骼、动画、材质、比例、授权；不得批量导入 |
| Asian Armour 候选角色 | `candidate-asian-armour` / `v0` | `F:\download\UE5中国古代武侠客士兵人物角色江湖动画 Asian Armour` | UE `.uasset`，目录约 861 个 | 候选 | `manifests/candidate-asian-armour/v0.yaml` / 待导入 | 阶段二挑选 1 个步兵和 1 个骑兵/武将 | 不得复制整个目录；先登记依赖和许可证 |
| Low Poly 人物资源（历史占位记录） | `deprecated-low-poly-character` / `v0` | 不再作为阶段一目标 | 角色 | 弃用 | `manifests/deprecated-low-poly-character/v0.yaml` / 无 UE 路径 | 不进入当前阶段 | 保留记录以便追溯；新资源必须符合[角色素材需求](../PRD/玩法系统/07-召陵县第一阶段Demo角色素材需求.md)的汉末写实风和 UE 验收要求 |
| Low Poly 战场地编资源（历史占位记录） | `deprecated-low-poly-battlefield` / `v0` | 不再作为阶段一目标 | 地形/植被/掩体 | 弃用 | `manifests/deprecated-low-poly-battlefield/v0.yaml` / 无 UE 路径 | 不进入当前阶段 | 保留记录以便追溯；场景改用写实比例、材质和远景代理分层 |
| Quaternius Universal Base Characters Standard | `candidate-quaternius-universal` / `v0` | https://quaternius.itch.io/universal-base-characters / CC0 | FBX/glTF，Standard 免费包约 122MB（页面标注）；本地下载尝试文件为 HTML 重定向页，尚未取得有效 ZIP | 候选 | `manifests/candidate-quaternius-universal/v0.yaml` / 待导入 | 阶段一角色身体/骨架基线 | 页面标明 6 个基础模型、Humanoid rig、平均约 13k tris、可用于个人/教育/商业项目；现代基础人形，不直接作为汉末服装 |
| Quaternius Animated Knight Pack | `candidate-quaternius-knight` / `v0` | https://quaternius.com/packs/knightcharacter.html / CC0 | FBX/OBJ/Blend，Google Drive 文件夹；未下载 | 候选 | `manifests/candidate-quaternius-knight/v0.yaml` / 待导入 | 阶段一将领轮廓/动作参考 | 西式骑士风格，只作轮廓/动画参考，不直接视为汉末定稿 |
| 汉末写实风角色小样设计 | `design-han-end-realistic-character` / `v0` | 项目设计稿（非外部资源） | 计划使用现有 `/Game/Battle/Characters/SK_Battle_Infantry` 骨架，补齐写实服装、装备、LOD 和动画 | 制作中 | `manifests/design-han-end-realistic-character/v0.yaml` / `/Game/Battle/Characters/SK_Battle_Infantry` | 阶段一士兵/将领 | 必须保持 gameplay component、碰撞接口和相机锚点 |

## 阶段一历史视口验证样本（2026-10-22）

| 资源 | `asset_id` / 版本 | 来源/许可证 | UE 路径 | 用途与预算 | 状态/证据 |
|---|---|---|---|---|---|
| Kenney Nature Kit | `kenney-nature-kit` / `v0` | https://kenney.nl/assets/nature-kit / CC0 | `/Game/Battle/Imported/NatureKit/SM_TreeOak`, `/Game/Battle/Imported/NatureKit/SM_FenceSimple` | 2 棵树、2 条后撤线；历史上用于远景代理样本 | 待验证；2026-10-22 有视口验证记录，当前治理资料待补；见 manifest |
| Kenney Castle Kit | `kenney-castle-kit` / `v0` | https://kenney.nl/assets/castle-kit / CC0 | `/Game/Battle/Imported/CastleKit/SM_BattleHills`, `SM_RocksSmall`, `SM_Flag`, `SM_Catapult` | 1 个浅丘、2 组岩石、3 面旗帜、1 台投石车 | 待验证；历史视口验证含退化切线警告，当前治理资料待补；见 manifest |
| 阶段一颜色材质 | `battle-materials-v1` / `v0` | 项目内创建，无外部授权 | `/Game/Battle/Materials/MI_Battle01_Grass`, `MI_Battle01_Allied`, `MI_Battle01_Enemy`, `MI_Battle01_Road`, `MI_Battle01_Objective` | 草地、蓝/红阵地区、棕色道路、黄色目标；单材质实例 | 待验证；有历史关卡可见记录，当前治理资料待补；见 manifest |

## 角色变体小样（2026-10-22）

来源：Kenney Mini Arena 1.1，https://kenney.nl/assets/mini-arena，CC0；原包存于 `docs/art_resources/source/kenney_mini-arena.zip`，解包于 `docs/art_resources/staging/kenney_mini-arena/`。本轮只对原人物做了轻量配色和轮廓修改，未从头制作高细节模型。以下文件在 Blender 中完成准备，但 UE 朝向、比例、碰撞、LOD、动画和 PIE 可见结果尚未验证；当前生命周期为“待验证”，不得进入 `approved/`。

| 文件 | `asset_id` / 版本 | 文件大小 | 几何/骨架 | 目标 UE 路径 | 状态 |
|---|---|---:|---|---|---|
| `SK_GS_Soldier.fbx` | `kenney-variant-soldier` / `v0` | 59,676 bytes | 513 三角面，6 根骨骼；蓝色士兵，5 个材质槽 | `/Game/Battle/Imported/Characters/KenneyVariants/SK_GS_Soldier` | 待验证；见 `manifests/kenney-variant-soldier/v0.yaml` |
| `SK_GS_General.fbx` | `kenney-variant-general` / `v0` | 68,220 bytes | 517 三角面，6 根骨骼；红/金将领，含简化披风，5 个材质槽 | `/Game/Battle/Imported/Characters/KenneyVariants/SK_GS_General` | 待验证；见 `manifests/kenney-variant-general/v0.yaml` |
| `AN_GS_idle.fbx`, `AN_GS_walk.fbx`, `AN_GS_die.fbx` | `kenney-variant-animations` / `v0` | 合计 199,540 bytes | 待机、行走、失能；源包另含更多动作，当前只选玩法所需三段 | `/Game/Battle/Imported/Characters/KenneyVariants/Animations` | 待验证；见 `manifests/kenney-variant-animations/v0.yaml` |

变体工作文件为 `docs/art_resources/staging/kenney_variants_v1/GS_CharacterVariants.blend`，Blender 截图证据为 `docs/art_resources/evidence/20261022_kenney_variants_blender.png`，准备记录为 `docs/art_resources/staging/kenney_variants_v1/preparation_report.json`。UE 中的朝向、比例、碰撞、LOD、动画和 PIE 可见结果均尚未验证，不进入正式资产状态。

## 本轮关卡证据

- 关卡：`/Game/Battle/Lvl_Battle01`
- 关卡文件：`Content/Battle/Lvl_Battle01.umap`
- 回退副本：`docs/art_resources/deprecated/20261022_before_readability/Lvl_Battle01.umap.bak`
- 静态布局：草地底色、左右阵地区、三段道路、中央目标平台/圆台、双方单位占位、玩家与两名亲卫占位。
- 当前仅为静态可读场景；移动、命令、士气和胜负逻辑尚未作为本轮验收项。

## 登记规则

补充网上资源时必须先建立 manifest，并填写来源 URL、许可证、下载日期、文件大小、面数/纹理预算、源/导出文件 SHA-256、依赖图、导入资产路径、实际用途、UE 日志/截图证据、批准人和回退位置。未填写完整前，状态保持为“候选”，不得进入正式 Demo。已有历史表格行也必须逐步补建对应 manifest，不能把本索引当作唯一事实来源。
| 汝南郡平面地图概念测试 | `runan-commandery-flat-map` / `v001-20261030` | 用户授权AI生成；模型 `gemini-3-pro-image-preview` | 二维概念图 | 候选 | `manifests/runan-commandery-flat-map/v001-20261030.yaml` / 未导入 | 汝南郡地图视觉测试 | 主县名可读；郡界/县位/河名未考证；Flare通道失败证据已保留；输出许可待核验 |
