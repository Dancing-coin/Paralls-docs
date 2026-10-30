from pathlib import Path
import json, os, re

ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
SRC=B/'original_PRD'
M=[]
DEMO='玩法系统/05-第一阶段县城守城Demo设计与执行路线.md'
PLAN='玩法系统/08-基础设施与Owner建设总计划.md'
CASE='玩法系统/04-衣带诏刘备玩家完整时序案例.md'
OLD='烽火王座：汉末群雄_骑将冲阵垂直切片策划案_v0.1.md'

def rel(dst,src): return os.path.relpath(ROOT/dst,(ROOT/src).parent).replace('\\','/')
def link(dst,src,label=None,anchor=''): return '['+(label or Path(dst).stem)+']('+rel(dst,src)+anchor+')'
def meta(title,source,status='整理版；继承原文评审状态，非新增产品批准',impl='设计/计划；本次未核验代码或UE运行，不代表已实现'):
 return f'# {title}\n\n- 版本：1.0（职责拆分版）\n- 更新日期：2026-10-30\n- 评审状态：{status}\n- 实现状态：{impl}\n- 来源：{source}\n\n'
def write(dst,title,body,source,status=None):
 p=ROOT/dst;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(meta(title,source,**({'status':status} if status else {}))+body.strip()+'\n',encoding='utf-8')
def take(src,a,b,dst,anchor,disposition='正式保留'):
 lines=(SRC/src).read_text(encoding='utf-8-sig').splitlines()
 M.append({'source':'docs/PRD/'+src,'source_start':a,'source_end':b,'target':dst,'target_anchor':anchor,'disposition':disposition})
 return f'\n<a id="{anchor}"></a>\n\n'+'\n'.join(lines[a-1:b]).strip()+'\n'

scope='docs/PRD/05-阶段与可玩切片/县城守城Demo/体验目标与范围.md'
coverage='docs/PRD/05-阶段与可玩切片/县城守城Demo/可玩切片与需求覆盖.md'
accept='docs/PRD/05-阶段与可玩切片/县城守城Demo/验收标准.md'
stages='docs/PRD/05-阶段与可玩切片/阶段与切片对照表.md'
prod='docs/production/基础设施与Owner建设总计划.md'
execp='docs/production/县城守城Demo执行计划.md'
valid='docs/validation/验证与证据规范.md'
tests='docs/validation/县城守城Demo/测试用例与证据索引.md'
characters='docs/PRD/04-内容与剧本/召陵县/角色、势力与初始状态.md'
scenario='docs/PRD/04-内容与剧本/召陵县/目标、事件与胜负配置.md'
decision='docs/PRD/00-产品总纲/设计决策与待决问题.md'
reg='docs/architecture/03-Owner领域/01-Owner注册表.md'
deploy='docs/architecture/05-运行时接入/01-UE本地提交与Paralls同步.md'

write(scope,'县城守城 Demo：体验目标与范围',
 '## 当前目标\n\n当前独立开发和验收目标统一为县城守城 Demo；骑将冲阵只作为历史方案和可吸收机制来源。玩家在有限身份权限、合法已知情报和连续世界约束下完成“军情—求援—守城—胜负”。骑乘、视角、传令、士气、阵型与目标仅按本 Demo 需要接入。\n\n'+
 '三队配置在县城旧设计和角色需求中另有独立来源，暂列待决；`10/22/34` 不设为当前强制命令映射，3–8 分钟冲阵不作为当前验收时长。参见'+link(decision,scope)+'。\n\n'+
 take(DEMO,53,83,scope,'source-demo-goals')+
 '## 体验与规则入口\n\n'+
 '- 玩家循环：合法获知军情 → 暂停评估 → 求援/布防 → 恢复并观察传令、战斗与资源后果 → 核查/追加命令或亲自介入 → 结局。暂停不刷新未知信息或完成世界事务。\n'+
 '- 出城、袭扰、截粮、护送、破坏、说服与秘密运输为可选方式；留城守备可取得胜利。\n'+
 '- 亲战提高局部影响但增加指挥可达性风险；修城、生产、救治竞争资源；服从可受能力、恐惧、疲劳、家庭责任和判断限制。详细规则由玩法模块维护。\n'+
 '- 场景、角色、初始资源、时间与胜负配置由'+link(scenario,scope)+'及'+link(characters,scope)+'维护；不在总纲复制配置。\n'+
 '- 长期全领域能力合同与未启用领域 fixture 不等于已制作全国内容；正式注册表见'+link(reg,scope)+'。\n\n'+
 '## 放行与范围控制\n\n'+link(coverage,scope)+'定义各切片覆盖；'+link(accept,scope)+'是验收要求的唯一维护位置。缺少运行证据的切片仍为开发中/未核验。当前文档整理不标记任何阶段通过。',
 '原05 §§1–4、8、11–13、17；2026-10-30用户确认的目标调整')

write(characters,'召陵县：角色、势力与初始状态',
 '## 身份和初始权限\n\n玩家是县城最高军政统治者；“最高”不等于跨辖域、跨通信和组织的无限权限。身份/授权正式规则引用'+link('docs/PRD/01-全局规则/玩家身份、权限与操作入口.md',characters)+'。\n\n'+
 take(DEMO,482,491,characters,'source-demo-roster')+
 '\n> 三队在原县城设计中有独立要求；不能仅因取消骑将冲阵就删除，也不能在本次整理重新批准为硬下限。见'+link(decision,characters,anchor='#d03')+'。其余数量为保留的县城设计配置，尚无运行验证。\n\n'+
 '## 阵营与初始状态\n\n守方为县署、亲卫、营级指挥与守军、传令和军需/工坊/医舍人员；两个村落有负责人和生产劳动人口。攻方有主战、军旗、器械、指挥与运输职能；外部援军独立推进。角色身份、岗位、身体、财产、知情、关系和心智分别引用对应正式模块与技术事实边界。\n\n初始姓名、等级、兵力、忠诚、训练、伤病、士气、敌军规模、援军路线/速度及人物关系数值原文未冻结；不以示例填充。美术角色交付见'+link('docs/art_resources/requirements/召陵县/角色素材需求.md',characters)+'；模型可见不代表角色规则已实现。\n\n'+
 '## 初始资源配置\n\n'+take(DEMO,386,400,characters,'source-demo-resources')+
 '\n上述资源种类与来源是召陵县配置；数量/质量/预留/保管等通用规则维护于'+link('docs/PRD/02-玩法模块/资源、生产、经济与运输.md',characters)+'。资源数量、品质、仓储容量和消耗率均待配置评审，不在此猜测。',
 '原05 §§3、9.1、11.1；原07角色素材需求（交付规格另见art_resources）')

write(scenario,'召陵县：目标、事件与胜负配置',
 '## 空间与时间配置\n\n县城、两个村落、田林道路、桥梁/浅河、攻方营地/器械工地/粮站和野战粮道共享连续世界，布局见'+link('docs/PRD/04-内容与剧本/召陵县/场景布局与功能分区.md',scenario)+'。\n\n'+
 take(DEMO,506,510,scenario,'source-demo-time')+
 '\n## 命令内容目录\n\n以下是场景启用命令及玩家含义，不是第二份信封/schema；条件、权限、幂等和回执引用'+link('docs/architecture/02-公共契约/02-Command事件与Receipt.md',scenario)+'及'+link('docs/PRD/03-跨模块流程/命令传递、执行与指挥权轮替.md',scenario)+'。\n\n'+
 take(DEMO,493,504,scenario,'source-demo-commands')+
 take(DEMO,365,380,scenario,'source-demo-endings')+
 '\n## 事件与过程约束\n\n合法军情触发玩家求援/布防机会；援军按路线、通信、接战和交接结果推进。敌军每天对营地、器械、粮站、侦察和攻城施压；运输受阻、截击、生产停工、伤病和短缺经模块规则影响战场。事件配置不得直接改伤害、资源、政治承认或胜负。\n\n县城失守与投降的精确组合、逃离责任范围判定、援军交接字段和各触发阈值尚待评审，见'+link(decision,scenario)+'；“30天”是约定窗口，不是绕过结算的跳时脚本。\n\n## 配置版本与证据\n\n本页保留设计配置，不包含真实测试通过记录。测试方法见'+link(tests,scenario)+'，内容数据/阈值冻结时记录版本与关联用例。',
 '原05 §§3、8.6、11；未决数值不补造')

write(coverage,'县城守城 Demo：可玩切片与需求覆盖',
 '## 切片共同口径\n\n每个切片都需玩家选择、世界后果、可见反馈和因果解释同时成立；只有接口、假数据、单测不算可玩完成。下列原稿完整保留目标/工作范围；“通过标准”统一由'+link(accept,coverage)+'维护，原段落中的标准移作需求覆盖说明。三队原要求标为待决，不因旧方案自动强制。\n\n'+
 take(DEMO,542,605,coverage,'source-demo-v0-v5')+
 '\n## 覆盖补充\n\nV2/D 必须同步提供 Inventory 弹药/药品即时子流与 Facility 城门机械/城防完整度子域，不能延后至 F；V4 结束前完成全量 Owner 能力与跨阶段 fixture；V5 是整合与质量，不是补齐缺失架构。Owner 名称及别名只引用'+link(reg,coverage)+'，部署节奏引用'+link(deploy,coverage)+'。\n\n执行顺序见'+link(execp,coverage)+'；证据要求见'+link(valid,coverage)+'。',
 '原05 §12.3、§12.4；原08 §§7–8')

# The acceptance wording is maintained here, not duplicated in the slice scope.
p=ROOT/coverage
t=p.read_text(encoding='utf-8')
t=re.sub(r'\*\*通过标准：\*\*[^\n]*',lambda m:'**需求约束：** '+m.group(0).split('**通过标准：**',1)[1].strip()+'（正式验收见同目录《验收标准》）',t)
p.write_text(t,encoding='utf-8')

write(accept,'县城守城 Demo：验收标准',
 '## 使用与判定\n\n这是阶段验收要求的正式维护位置。所有条目当前状态为“要求保留，未在本次执行”；没有日志/receipt/回放/定向截图不得写为通过。具体测试步骤与真实证据索引在'+link(tests,accept)+'；共用证据规则见'+link(valid,accept)+'。\n\n'+
 take(DEMO,721,740,accept,'source-demo-acceptance')+
 take(DEMO,805,819,accept,'source-demo-definition-of-done')+
 '\n## 切片放行边界\n\n- V0：只验世界壳，时间/位置/暂停恢复连续；不得标记玩法Demo。\n- V1：下令、送达、理解/接受、执行和结果可区分；离开现场后自治连续。\n- V2：可操作守城战、身体/体力/士气及时响应；可靠本地提交通过崩溃/回放验证，预测不得冒充最终事实；三项延迟按Manifest预算登记和实测。\n- V3：两条胜利与三类失败均可完成，首次Alpha；不强制出城。\n- V4：资源社会后果和23领域完整包及跨阶段fixture成立。\n- V5：完整Candidate与性能稳定性；V0–V4可单独启动回归。\n\n三队数量及失守/投降组合等未决项见'+link(decision,accept)+'；未决项不得伪写已验收。',
 '原05 §§13、17和§12.3切片放行要求；原08 G1–G7的证据归入validation')

write(stages,'阶段与切片对照表',
 '## 四种编号不可混用\n\n|体系|用途|当前维护位置|\n|---|---|---|\n|世界扩展五阶段|由召陵县向更广世界/政治军事规模扩展；草案未自动过审|'+link('docs/PRD/00-产品总纲/世界扩展路线.md',stages)+'|\n|基础能力门0–12|检查合同、内核、Owner、UE及质量能力，不是串行排程|本页首次/持续关系；建设任务见production|\n|建设批次A–F|按依赖安排I01–I10和领域交付，不是世界章节|'+link(prod,stages)+'|\n|可玩切片V0–V5|每次有独立可运行入口与玩家闭环|'+link(coverage,stages)+'|\n\n旧骑将冲阵Phase0–4及3–8分钟流程仅历史；建筑分阶段和美术A–E批次是资源工作维度，不与上述编号混同。\n\n'+
 take(DEMO,606,621,stages,'source-demo-capability-map')+
 '\n## 批次与切片\n\nA冻结合同 → B/V0 → C/V1 → D/V2 → E/V3 → F/V4 → V5。领域模型与资源工作从B开始并行；V3可以受控正式配置验证主线，但不等于资源社会完整。全量Owner能力门必须在V4结束前通过。\n\n本次仅整理文档，所有实际阶段通过情况须查证据索引，不能由本表推断。',
 '原五阶段大纲；原05 §§12.3–12.6；原08 §§1、3、8')

write(prod,'基础设施与 Owner 建设总计划',
 '## 范围与依赖\n\n本计划维护工作包、任务和依赖；规则/字段/Owner清单以'+link('docs/architecture/README.md',prod)+'为准，23领域只在'+link(reg,prod)+'注册，完整交付包及事实边界不在计划重复维护。县城内容排程见'+link(execp,prod)+'。全部复选框是原计划待办，不是完成证据。\n\n'+
 take(PLAN,29,85,prod,'source-plan-goals-packages')+
 take(PLAN,143,209,prod,'source-plan-tasks-batches')+
 take(PLAN,301,331,prod,'source-plan-responsibilities')+
 take(PLAN,351,359,prod,'source-plan-start-order')+
 '\n## 正式规格与验证依赖\n\n'+
 '- 写权地图、基础权威与Owner完整包：'+link(reg,prod)+'；细合同与部署节奏见'+link(deploy,prod)+'。\n'+
 '- 三本账、模型/Binding/评估、跨Owner结算及三本账查询：'+link('docs/architecture/README.md',prod)+'按职责导航。\n'+
 '- 征发运输生产、医疗、采购欠款、控制转移和政治后果：'+link('docs/architecture/04-模型与结算/02-数值状态效果与跨Owner结算.md',prod)+'及PRD跨模块流程。\n'+
 '- G1–G7为证据门，见'+link(valid,prod,anchor='#g1-g7')+'；不是另一份已完成进度表。\n\n本次未运行A1代码扫描、UE检查或任一建设任务；现状分析必须按当前代码/测试重新核验。',
 '原08 §§2–4、7–8、12–15；重复技术规格合并进architecture')

write(execp,'县城守城 Demo 执行计划',
 '## 执行入口\n\n当前目标只按'+link(scope,execp)+'推进；基础设施任务由'+link(prod,execp)+'维护，本页安排县城切片依赖和止损。切片范围见'+link(coverage,execp)+'，通过要求见'+link(accept,execp)+'；场景和资产使用各自规格，不能以计划重写权威事实。\n\n'+
 take(DEMO,512,541,execp,'source-demo-dual-track')+
 '\n## 当前切片顺序\n\nA合同与基线 → B/V0世界壳 → C/V1传令 → D/V2实时守城 → E/V3主线Alpha → F/V4资源社会与全量领域 → V5整合。V0不是玩法Demo；V3不是完整资源社会Demo；不等待全量基础设施串行做完才进入可玩验证。\n\n'+
 take(DEMO,635,720,execp,'source-demo-gates')+
 take(DEMO,792,804,execp,'source-demo-risks')+
 '\n## 下一步与进度\n\n本次完成文档归属整理；没有标记任何实现任务完成。后续先按基础设施计划A1–A5核验与冻结，再拆任务卡；现存用户改动和已有资产需要独立读取，不从旧文档推断实现。\n\n所有UE/导入/构建操作另遵守'+link('AGENTS.md',execp)+'；本轮未启动这些操作。',
 '原05 §§12.1–12.2、12.6、16；原08实际排程引用')

write(valid,'验证与证据规范',
 '## 设计、实现和证据分开\n\n设计合同写“要求/目标”；建设任务写“计划/待办”；真实实现状态必须有当前代码、测试、运行记录。设计案例的日志、时间、run_id和置信度均为示意，不能登记为执行证据。文档迁移校验只证明文档整理，不证明UE玩法完成。\n\n'+
 take(DEMO,622,634,valid,'source-demo-slice-evidence')+
 take(DEMO,779,790,valid,'source-demo-evidence-discipline')+
 '\n<a id="g1-g7"></a>\n\n## G1–G7 证据门\n\n'+
 take(PLAN,333,349,valid,'source-plan-evidence-gates')+
 '\n## 记录格式与判定\n\n每条真实记录填写：日期/操作者、代码与数据版本、合同/模型版本、硬件、入口/固定剧本、实际步骤、预期/实际、Command/事件/receipt关联、日志/截图相对路径、资源/Actor/PIE状态、帧率/加载/内存/显存、replay差异、结论、已知风险。结论只用“未执行/阻塞/通过/失败”；推断与观察分栏。\n\n截图应来自CaptureEditorImage/Slate或实际PIE；不得以桌面截图冒充。预算先登记后测量；历史硬件数字不得充当永久保证。各切片至少成功、失败/拒绝、暂停恢复与回放；未提供证据不能标记完成。\n\n县城用例和真实证据入口见'+link(tests,valid)+'；资源来源/授权和可见验证沿用'+link('docs/art_resources/README.md',valid)+'。',
 '原05 §§12.5、15；原08 §14；AGENTS验证纪律')

write(tests,'县城守城 Demo：测试用例与证据索引',
 '## 当前证据状态\n\n本次只整理文档；下列用例全部“未在本次执行”。原文的验收目标、计划复选框、案例日志及历史资产可见记录不等于县城Demo通过。真实运行记录按'+link(valid,tests)+'登记，正式通过条件由'+link(accept,tests)+'维护。\n\n'+
 take(DEMO,741,778,tests,'source-demo-test-cases')+
 '\n## 切片测试与证据登记\n\n|切片|入口/配置版本|真实记录|状态|\n|---|---|---|---|\n|V0|待实际核验|无本次运行证据|未执行|\n|V1|待实际核验；三队配置待决|无本次运行证据|未执行|\n|V2|待实际核验本地可靠提交|无本次运行证据|未执行|\n|V3|待实际核验五结局|无本次运行证据|未执行|\n|V4|待实际核验资源社会链与全量Owner|无本次运行证据|未执行|\n|V5|待实际整合/性能验证|无本次运行证据|未执行|\n\n历史美术导入/视口证据只从'+link('docs/art_resources/asset_registry.md',tests)+'追溯原日期、资产和条件，不归并为本表通过。',
 '原05 §14；实际证据保持空缺且明确未执行')

# Preserve the full old slice once, explicitly historical, with useful-item routing.
archive='docs/archive/PRD/骑将冲阵垂直切片（已取消独立开发）.md'
old=(SRC/OLD).read_text(encoding='utf-8-sig')
write(archive,'骑将冲阵垂直切片（已取消独立开发）',
 '> 状态：2026-10-30用户明确取消独立开发切片与独立验收目标。以下正文仅保留历史语境；其中“必须/阶段/通过”等词不再构成当前Demo要求。当前目标以'+link(scope,archive)+'为准。\n\n'+
 '## 有用条目迁移\n\n|历史主题|当前去向|处理|\n|---|---|---|\n|骑乘、移动、三视角|'+link('docs/PRD/02-玩法模块/具身操作、骑乘与视角.md',archive)+'|按县城需要吸收|\n|军制、预案、自主行动|'+link('docs/PRD/02-玩法模块/军制、指挥与自主行动.md',archive)+'|保留系统边界|\n|传令/控制权轮替|'+link('docs/PRD/03-跨模块流程/命令传递、执行与指挥权轮替.md',archive)+'|按正式规则整合|\n|士气/阵型/旗帜/将领/器械|'+link('docs/PRD/02-玩法模块/士气、阵型与战场目标.md',archive)+'|按县城需要吸收|\n|三队、10/22/34、3–8分钟|'+link(decision,archive)+'|不由旧方案自动强制|\n|实现阶段/验收|'+link(stages,archive)+'|旧排程历史化|\n\n## 历史原文\n\n'+old,
 '原骑将冲阵垂直切片策划案完整正文；原始字节副本保存在本轮backup',status='历史归档；取消独立开发，非当前验收规范')
M.append({'source':'docs/PRD/'+OLD,'source_start':1,'source_end':len(old.splitlines()),'target':archive,'target_anchor':'历史原文','disposition':'历史归档；有用机制合并'})

# Case: full narrative is an illustrative scenario; formal contract paragraphs become references.
case='docs/PRD/04-内容与剧本/设计案例/衣带诏刘备时序案例.md'
case_text=(SRC/CASE).read_text(encoding='utf-8-sig')
case_text=case_text[case_text.index('## 1. 案例目的'):]
case_text=case_text.replace('### 2.4 世界真相层 Owner','### 2.4 案例协作者（非 Owner 注册表）')
case_text=case_text.replace('## 4. 完整运行日志','## 4. 完整时序示意日志（未执行）')
case_text=case_text.replace('### T+21：玩家暂停并等待市场高峰','### T+21：玩家暂停规划，恢复后等待市场高峰')
write(case,'衣带诏刘备时序案例',
 '> 本文为未实现的设计案例，不是县城Demo范围、历史史实考证、运行日志或验收证据。所有run_id、时间节奏、置信度、物资数值、事件与日志均为说明用示例。完整叙事与分支保留，不以整理日期宣称批准或接入。\n\n'+
 '## 正式规则引用与示例纠偏\n\n- Owner与基础协作者区分：'+link(reg,case)+'；WRK/EventStore/医疗Workflow不是新增领域Owner。\n- 权威/查询/三本账：'+link('docs/architecture/README.md',case)+'；私有信念/情绪/解释归角色心智，不归公共Information/Social。\n- `[SOC] trust/suspicion`与`[INFO] cao_cao_private_belief`是旧案例的心智简写，若公开关系事实需另有Social/Information合法来源；不能照抄成公共写权。\n- `[SURV] horse_feed`是消费情境简称，草料库存与扣量归Inventory；Survival只处理自身领域后果。\n- 暂停中“调整亲卫等待位置”只能编辑待发送草案；实际移动/等待到市场高峰必须恢复后发生。\n- “WRK唯一推进world_tick”表示逻辑时间权威，不表示所有域只能由UE宿主或某一个进程结算。\n- 常态6小时/日、危机1小时等示例节奏以及两匹马、四日口粮、三日草料只属于本案例，不是召陵县配置。\n\n'+case_text,
 '原04完整时序案例；示例权威缩写按正式规则标注纠偏',status='设计案例；未作产品/技术验收')
M.append({'source':'docs/PRD/'+CASE,'source_start':1,'source_end':1239,'target':case,'target_anchor':'正式规则引用与示例纠偏','disposition':'设计案例保留；公共规则只引用正式位置'})

# Responsibility-specific templates preserve the useful field groups of the original.
tmpl='游戏策划案模板.md'
groups=[('产品总纲与全局规则模板.md','产品总纲与全局规则模板',[(17,82),(85,116),(231,245)]),('玩法模块与跨模块流程模板.md','玩法模块与跨模块流程模板',[(117,173),(250,280),(313,332)]),('内容与剧本模板.md','内容与剧本模板',[(174,249)]),('阶段范围与验收模板.md','阶段范围与验收模板',[(349,375),(418,428)]),('技术契约模板.md','技术契约模板',[(376,393)]),('制作计划与风险模板.md','制作计划与风险模板',[(394,417)]),('验证记录模板.md','验证记录模板',[(333,348)]),('美术交付模板.md','美术交付模板',[(281,312)])]
for fn,title,spans in groups:
 dst='docs/templates/PRD/'+fn
 body='> 本文件是填写结构，不是已批准需求。删去不适用字段，填写来源和评审状态；一条规则仅在正式职责文档维护，其他主题以相对链接引用。不得复制完整Owner表/公共契约或把模板占位符当作实现。\n\n'
 for a,b in spans: body+=take(tmpl,a,b,dst,'source-template-'+str(a),'适用模板保留')
 body+='\n## 元信息与可追溯性\n\n版本 / 更新日期 / 评审状态 / 实现状态 / 来源与决策 / 唯一维护位置 / 关联规则 / 未决项 / 验证方法与真实证据。跨模块流程另列前置条件、步骤/责任域、成本/回执、部分完成、取消/失败恢复；不要为流程新建Owner。\n'
 write(dst,title,body,'原《游戏策划案模板》按职责拆分；占位内容仅用于新文档')
write('docs/templates/PRD/README.md','PRD 适用模板',
 '按文档职责选择下列模板，不再复制大而全策划案。共同元信息记录版本、日期、评审/实现状态和来源；引用正式规则，不复制第二份维护正文。\n\n'+ '\n'.join('- '+link('docs/templates/PRD/'+x[0],'docs/templates/PRD/README.md') for x in groups)+
 '\n\n原模板使用说明、版本历史仅作为模板来源保存在原始备份，不构成项目需求。', '原《游戏策划案模板》')
M += [{'source':'docs/PRD/'+tmpl,'source_start':1,'source_end':16,'target':'docs/templates/PRD/README.md','target_anchor':'','disposition':'模板使用说明合并'}, {'source':'docs/PRD/'+tmpl,'source_start':429,'source_end':433,'target':'docs/templates/PRD/README.md','target_anchor':'','disposition':'模板来源历史保留于备份'}]

# Link former cross-section references in newly split source passages to their canonical locations.
routes={1:scope,2:scope,3:characters,4:scope,5:'docs/architecture/README.md',6:reg,7:'docs/architecture/README.md',8:'docs/PRD/02-玩法模块/军制、指挥与自主行动.md',9:'docs/PRD/02-玩法模块/资源、生产、经济与运输.md',10:deploy,11:scenario,12:execp,13:accept,14:tests,15:valid,16:execp,17:accept}
for dst in [scope,coverage,accept,characters,scenario,stages,execp]:
 p=ROOT/dst;t=p.read_text(encoding='utf-8')
 t=re.sub(r'第\s*(\d+)(?:\.\d+)?(?:[—–－-]\d+(?:\.\d+)?)?\s*节',lambda m:link(routes.get(int(m.group(1)),execp),dst,'正式规格/计划'),t)
 p.write_text(t,encoding='utf-8')
# Plan source section references point to architecture or validation, not its old ordinal numbering.
p=ROOT/prod;t=p.read_text(encoding='utf-8')
t=re.sub(r'第\s*(5|6|11)(?:\.\d+)?\s*节',lambda m:link(deploy if m.group(1)=='11' else reg,prod,'正式合同'),t)
t=t.replace('05 中的基础设施能力门',link(stages,prod,'阶段对照中的基础设施能力门'))
p.write_text(t,encoding='utf-8')

(B/'migration_primary.json').write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'primary_documents_written':len(list((ROOT/'docs/templates/PRD').glob('*.md')))+14,'migration_entries':len(M)},ensure_ascii=False))
