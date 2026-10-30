from pathlib import Path
import json, os, re

ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
SRC=B/'original_PRD'
def rel(dst,src): return os.path.relpath(ROOT/dst,(ROOT/src).parent).replace('\\','/')
def link(dst,src,label=None,anchor=''): return '['+(label or Path(dst).stem)+']('+rel(dst,src)+anchor+')'
def put(dst,text):
 p=ROOT/dst;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.rstrip()+'\n',encoding='utf-8')
def meta(title,source,status='整理版；未替代原有未决评审',impl='设计/计划，未在本次运行验证'):
 return f'# {title}\n\n- 版本：1.0（职责拆分版）\n- 更新日期：2026-10-30\n- 评审状态：{status}\n- 实现状态：{impl}\n- 来源：{source}\n\n'

d='docs/PRD/00-产品总纲/设计决策与待决问题.md'
backup='docs/_backups/PRD_20261030_111755/'
source_names={
 '总策划':'烽火王座：汉末群雄_总策划案_v1.0.md',
 '玩法':'烽火王座：汉末群雄_玩法策划案_v0.1.md',
 '五阶段':'国殇：汉末_五阶段战争世界设计大纲_v0.1.md',
 '骑将':'烽火王座：汉末群雄_骑将冲阵垂直切片策划案_v0.1.md',
 '县城05':'玩法系统/05-第一阶段县城守城Demo设计与执行路线.md',
 '计划08':'玩法系统/08-基础设施与Owner建设总计划.md',
 '场景06':'玩法系统/06-召陵县第一阶段Demo场景素材需求.md',
 '角色07':'玩法系统/07-召陵县第一阶段Demo角色素材需求.md',
 '建筑':'玩法系统/建筑资产构建方案.md'}
def source(k,chapter=''):
 return link(backup+'original_PRD/'+source_names[k],d,k)+chapter
rows=[
('d01','项目名','未决',source('总策划')+'、'+source('五阶段'),'原文同时用“烽火王座：汉末群雄”和“国殇：汉末”；当前目录用Guoshang工作名，不在本次确定正式名称。'),
('d02','取消独立骑将切片','已确认：2026-10-30用户指令',source('骑将')+'；旧mounted-charge计划/规格','骑将冲阵独立开发与独立验收取消；骑乘、镜头、军制、传令、士气、阵型等按县城需求吸收，旧阶段/验收只历史归档。'),
('d03','三队是否当前硬下限','未决：存在独立来源',source('县城05',' §§8.2/8.3、11.1、12.3 V1/V2、能力门6')+'；'+source('角色07'),'县城稿明确守军三队/一营三队，角色需求亦按三队制作；旧骑将取消不能自动否定这些独立条款。本次保留来源与配置候选，未重批硬下限；数量影响组织、UI、角色资产和V1/V2用例。'),
('d04','10/22/34命令映射','未决；不自动强制',source('骑将')+'；'+source('角色07')+'；旧mounted-charge规格/计划','旧PRD语义未填写完整，旧实现计划有follow_player_charge/attack_flank/encircle_rear历史ID；不得将历史ID自动映射为县城强制键位或生产Command。当前场景命令目录另维护。'),
('d05','演示时长和倍率','部分已确认/部分未决',source('骑将')+'；'+source('县城05',' §11.3'),'3–8分钟仅旧冲阵流程；县城约30世界日保留，现实分钟数和倍率等待灰盒校准。不能用跳天绕过结算。'),
('d06','四种阶段编号','口径已区分，具体排期未决',source('五阶段')+'；'+source('县城05',' §12')+'；'+source('计划08',' §§1/3/8'),'世界扩展五阶段、能力门0–12、建设批次A–F、可玩V0–V5职责不同；建筑制作阶段/美术A–E批次与旧Phase0–4另列，不互相替换。'),
('d07','死亡与传承','范围已区分，细则未决',source('玩法')+'；'+source('县城05',' §8.6'),'完整游戏可有继承/控制权延续；县城玩家死亡是本局失败。不能用长期传承绕过Demo失败。继任后的权限/记忆等按模块继续评审。'),
('d08','失守、投降与逃离','未决：摘要与详细条件不同',source('县城05',' §§4/8.6/13/17')+'；原README摘要','详细条件为“失守后玩家投降”，部分摘要简写失守/投降即失败；本次保留详细来源和两者差异，不另定布尔关系。成功逃离守城责任范围是失败，范围/判定阈值待定。'),
('d09','五阶段草案最低内容与当前县城','未决扩展不自动入本轮',source('五阶段')+'；'+source('县城05',' §§2/3/9/11'),'五阶段草案的所有职业、12种资源、2–3村落/灾害等保留为远景候选；县城当前两村等具体内容保留。额外职业/村数/灾害不因“至少”自动扩大本轮。'),
('d10','Low Poly原型与正式写实风','未决：显式措辞冲突',link(backup+'additional_originals/AGENTS.md',d,'原AGENTS')+'；'+link(backup+'additional_originals/docs/art_resources/README.md',d,'原美术索引')+'；'+source('角色07'),'AGENTS保留第一阶段Low Poly实现措辞，美术稿明确不以Low Poly为第一阶段目标、写实比例/PBR。可区分原型与成品层级，但本次不据此宣布已完成风格评审或覆盖任一约束。'),
('d11','断线自主回退','授权边界已保留，策略未决',source('计划08')+'；'+link(backup+'additional_originals/docs/superpowers/specs/2026-10-27-ue-paralls-fidelity-alignment-design.md',d,'10-27草案'),'继续当前计划/已授权预案仅在有效意图TTL、lease/epoch和本地写权内。不能自动授予新自主意图或权威；过期后安全中断、再询问等具体体验待评审。'),
('d12','跨区域环境事实来源','待A2归属评审',source('计划08',' §7 A2及环境段'),'温湿度、雨、火、烟的来源、作用域、版本和推进责任须登记；未覆盖输入保持unknown/拒绝。本次不新增环境Owner，不默认塞给Inventory、ESM或表现层。'),
('d13','美术数量、尺度和性能预算','未决/未实测',source('场景06')+'；'+source('角色07')+'；'+source('建筑'),'原稿存在L1约9类×2与40–60总数、平台600与60cm、18里×60户与1.1万户等差异；950×950m/90万㎡、1.2/2.5km²、5万人、8000可进入建筑候选尺度未验证。HLOD500–2000三角形、FastGeo/流送数值为设计目标非实测；细项在美术待核对清单保留。'),
('d14','资产身份与版本','沿用既有治理；旧表述更正',source('场景06')+'、'+source('角色07')+'；'+link('docs/art_resources/README.md',d,'资源治理'),'既有治理明确asset_id为资产版本族，version单列；不采用旧需求将asset_id等同单一版本的说法。building_id/角色ID、manifest和生命周期沿用现有体系，不迁移或覆盖资源。'),
('d15','旧10-27技术草案与正式契约','冲突条款转历史，接入现状待验',link(backup+'additional_originals/docs/superpowers/specs/2026-10-27-ue-paralls-fidelity-alignment-design.md',d,'10-27草案')+'；'+source('县城05')+'；'+source('计划08'),'UE-only时钟、笼统UE Owner、自动fallback/旧A–D路线等以新职责文档中的唯一写者、正式时间权威、有效授权和可靠本地提交边界为准；原稿未被视为真实实现。'),
('d16','版本日期与评审状态','保留来源，不由时间推断审批',source('总策划')+'；'+source('县城05')+'；'+source('计划08'),'文件名版本与正文版本/日期可能不同；拆分版1.0仅表示整理版本。保留原始备份/历史，不以修改时间裁决产品冲突。'),
('d17','完整游戏待确认字段','仍未决',source('玩法',' §17，第867–890行'),'Q01–Q24原问题逐条保留于下方；本次仅取消旧骑将独立目标，不代答商业、玩法数值、平台/性能或发布问题。'),
('d18','长期内容、历史模式与五城战役','未决',source('总策划')+'；'+source('玩法')+'；'+source('五阶段'),'196–198五城战役、不同历史难度/模式、火药可选分支等保留为长期候选，不擅自安排世界阶段或县城范围；具体历史准确性未在本次考证。'),
('d19','设计与实际接入差距','等待代码/测试/UE证据',source('计划08',' A1')+'；原PRD README审查记录','文档对齐、目标契约、待办复选框、设计案例日志不证明实现；旧Paralls能力分析是来源快照。A1重新核验现有能力/实际接入/目标差距；本次未启动UE、构建、导入或运行测试。')]
text=meta('设计决策与待决问题','2026-10-30用户确认；原20份PRD及相关既有说明','已确认项依用户指令；其余未决，不新作产品决策')
text+='## 维护规则\n\n确认项记录依据；未决项保留双方来源和影响。目录整理不等于评审批准，不能单凭文件修改时间选胜者。无依赖的内容继续整理，涉及待决配置的实施/验收不得伪写通过。\n\n'
for id,title,state,sources,detail in rows:
 text+=f'<a id="{id}"></a>\n\n## {id.upper()} {title}\n\n- 状态：{state}\n- 来源：{sources}\n- 处理与影响：{detail}\n\n'
ls=(SRC/source_names['玩法']).read_text(encoding='utf-8-sig').splitlines()
text+='## 完整游戏待确认问题（原文保留）\n\n单人完整暂停已确定；其他问题继续待决。以下问题不自动扩大县城当前范围。\n\n'
for n,line in enumerate(ls[866:890],1):
 text+=f'<a id="q{n:02d}"></a>\n\n### Q{n:02d}\n\n'+re.sub(r'^\d+\.\s*','',line)+'\n\n'
put(d,text)

readme='docs/PRD/README.md'
dirs=[('00-产品总纲','愿景、世界扩展、术语和决策'),('01-全局规则','时间/暂停、身份权限、信息边界'),('02-玩法模块','玩家行为、条件、成本、结果、反馈'),('03-跨模块流程','命令/指挥权、补给医疗、战役与战后'),('04-内容与剧本','召陵县配置与衣带诏设计案例'),('05-阶段与可玩切片','阶段区分、县城范围、V0–V5覆盖和验收')]
text=meta('Guoshang PRD 导航','原PRD全套职责拆分；迁移详见本轮记录','目录整理完成状态以检查报告为准；产品待决项继续未决','本入口不证明代码/UE实现或运行验收')
text+='## 当前目标与阅读入口\n\n当前开发和独立验收目标为县城守城 Demo。骑将冲阵已取消独立切片/独立验收，机制按县城需要吸收，原方案保留历史。三队有县城稿/角色稿独立来源，数量仍待决；旧10/22/34及3–8分钟不自动强制。\n\n'
for path,label in [('05-阶段与可玩切片/县城守城Demo/体验目标与范围.md','先读：体验目标与范围'),('05-阶段与可玩切片/县城守城Demo/可玩切片与需求覆盖.md','V0–V5可玩覆盖'),('05-阶段与可玩切片/县城守城Demo/验收标准.md','正式验收要求'),('00-产品总纲/设计决策与待决问题.md','设计决策与待决问题')]:
 text+='- '+link('docs/PRD/'+path,readme,label)+'\n'
text+='\n## PRD 分工\n\n'
for folder,purpose in dirs:
 text+=f'### {folder} — {purpose}\n\n'
 for p in sorted((ROOT/'docs/PRD'/folder).rglob('*.md')):
  text+='- '+link(p.relative_to(ROOT).as_posix(),readme,p.stem)+'\n'
 text+='\n'
text+='## 配套文档与唯一维护位置\n\n|职责|入口|\n|---|---|\n'
for path,label in [('docs/architecture/README.md','技术边界/公共契约/领域Owner/模型/接入/持久化'),('docs/production/基础设施与Owner建设总计划.md','建设任务、依赖和批次'),('docs/production/县城守城Demo执行计划.md','县城切片执行与止损'),('docs/validation/验证与证据规范.md','验证方法与证据规则'),('docs/validation/县城守城Demo/测试用例与证据索引.md','县城用例与真实记录'),('docs/art_resources/README.md','资源治理、manifest与生命周期'),('docs/art_resources/requirements/召陵县/场景素材需求.md','召陵县场景交付'),('docs/art_resources/requirements/召陵县/角色素材需求.md','召陵县角色交付'),('docs/templates/PRD/README.md','按职责选择的文档模板'),('docs/archive/PRD/骑将冲阵垂直切片（已取消独立开发）.md','骑将历史方案与有用机制迁移')]:
 text+='|'+label+'|'+link(path,readme)+'|\n'
text+='\nOwner唯一注册表与全量UE节奏矩阵分别在architecture中维护；计划、PRD和美术需求只引用。玩法模块不必与Owner一一对应，医疗等过程保留Workflow性质。\n\n## 迁移与验证记录\n\n'
for name,label in [('BACKUP_VERIFIED.md','修改前备份核验'),('MIGRATION.md','原章节→新章节迁移对照'),('CHECK_RESULTS.md','整理完成静态检查结果')]: text+='- '+link(backup+name,readme,label)+'\n'
text+='\n原路径保留简短迁移指引；原始全文和哈希清单保存在本次备份，不能将旧入口当作第二份正式维护正文。本次未运行UE/Paralls、未构建或导入；历史运行证据保持原日期和范围。\n'
put(readme,text)

# Existing files were backed up and verified before their first modification.
manifest=json.loads((B/'additional_manifest.json').read_text(encoding='utf-8'))
allowed={x['original_path'] for x in manifest}
def edit_existing(path,transform):
 assert path in allowed,path
 p=ROOT/path;old=p.read_text(encoding='utf-8-sig');new=transform(old)
 if new!=old: p.write_text(new,encoding='utf-8')

art='docs/art_resources/README.md'
edit_existing(art,lambda t:t.replace('《烽火王座：汉末群雄》','Guoshang项目').replace('- 召陵县场景需求：`../PRD/玩法系统/06-召陵县第一阶段Demo场景素材需求.md`，定义县城分区、建筑/地编/道具、逻辑锚点、流送和场景验收。',
 '- [召陵县场景需求](requirements/召陵县/场景素材需求.md)与[角色需求](requirements/召陵县/角色素材需求.md)：维护具体交付和逻辑锚点；[通用标准](standards/建筑模块化与流送标准.md)维护制作/流送规则；[场景布局](../PRD/04-内容与剧本/召陵县/场景布局与功能分区.md)维护空间用途。').replace('玩家、亲卫、三队、敌军、指挥官、军旗和攻城器械','玩家、亲卫、守军各职能、敌军、指挥官、军旗和攻城器械')+
 '\n## 文档状态与当前体验\n\n更新：2026-10-30（仅同步导航与当前目标，资源治理不变）。当前县城体验见[体验索引](experience_index.md)；三队等独立来源及风格措辞冲突见[设计决策](../PRD/00-产品总纲/设计决策与待决问题.md)。原型Low Poly与正式写实目标不能仅凭整理自行判定已统一。manifest、版本族ID、来源授权、生命周期与历史证据保持既有体系；本次没有资产导入或重新验证。\n')

idx='docs/art_resources/experience_index.md'
edit_existing(idx,lambda _:meta('县城守城美术体验索引','原骑将体验索引的通用可读性要求；县城正式PRD','体验导航；美术待决项仍未定','未在本次Editor/PIE验证')+
 '## 玩家需要读懂的县城因果链\n\n合法军情 → 暂停评估 → 求援/布防命令 → 传令与队伍响应 → 城门/城墙压力、身体/士气与资源变化 → 援军交接或敌退/失败。美术帮助识别状态和原因，不替代事实提交。正式范围见[县城体验目标](../PRD/05-阶段与可玩切片/县城守城Demo/体验目标与范围.md)。\n\n## 视角与战场可读性\n\n- 俯视读出县城功能区、粮道、城门、敌营、援军路线、压力与后撤方向；反馈必须符合合法知情。\n- 第三人称读出玩家/亲卫、朝向、移动、受击/失能、骑乘或步战；第一人称支持具身感受和操作风险。\n- 守军各职能、敌军、指挥官、军旗与器械用轮廓、装备/旗帜和状态反馈区分，不只依颜色；阵型和士气变化可见。\n- 写实近景与低成本中远景按镜头分层；HLOD/实例代理不冒充近景成品。三队数量/风格/单位预算待决，不自动沿用旧冲阵验收。\n\n## 制作、替换与验证入口\n\n县城先按[场景需求](requirements/召陵县/场景素材需求.md)与[角色需求](requirements/召陵县/角色素材需求.md)所定义批次制作；不另设冲阵优先级。每次替换保持角色身份、Gameplay Component、碰撞/相机锚点、命令来源和事件挂接，逐类小样本验证并保留回退版本。\n\n通用规则见[场景制作标准](standards/场景制作与交互挂接标准.md)和[角色接入标准](standards/角色制作与UE接入标准.md)，资产事实仍由[manifest与登记治理](README.md)维护。\n\n## 待决与历史\n\n单位数量、镜头距离、真实演示时长、材质预算、角色/地编替换优先级继续在[设计决策](../PRD/00-产品总纲/设计决策与待决问题.md)及具体交付规格记录；不在体验索引重定。原骑将独立体验链、中央冲锋路线和三队验收已历史化，原文保存在[本次附加备份](../_backups/PRD_20261030_111755/additional_originals/docs/art_resources/experience_index.md)，旧摆放参考见[历史战场概念](concept_battlefield_layout.md)。\n')

def banner(path,message,extra=''):
 def transform(t):
  return '> 文档状态更新：2026-10-30。'+message+' 当前规格见'+link('docs/PRD/README.md',path,'PRD导航')+'；'+link('docs/production/县城守城Demo执行计划.md',path,'县城执行计划')+'。'+extra+'\n\n'+t
 edit_existing(path,transform)
banner('docs/art_resources/concept_battlefield_layout.md','历史骑将冲阵概念图与摆放说明；独立目标已取消，正文的两队/中央夺旗/必须读图仅描述旧概念，不是当前县城布局。')
for x in manifest:
 path=x['original_path']
 if path.startswith('docs/prompt/'):
  banner(path,'历史实施提示词，已不作为当前开发指令。' if 'demo1_' in path else '历史画面/UI概念提示词，仅视觉参考；其中三队、镜头与命令不构成当前范围、写权或验收。')
 elif 'mounted-charge' in path:
  banner(path,'历史骑将冲阵计划/规格；2026-10-30取消独立开发与独立验收。正文所有任务/必须/阶段门不再作为当前实施要求。')
 elif '2026-10-27-ue-paralls' in path:
  banner(path,'历史技术设计草案；本文不是当前实现证据。UE-only时钟、泛称UE Owner和自动fallback等冲突表述按正式architecture契约与设计待决记录理解。', '技术唯一维护入口见'+link('docs/architecture/README.md',path)+'。')
 elif '2026-10-29-asset-governance' in path:
  banner(path,'资产治理建设计划，保留待办与历史依据；不是治理验收通过记录。当前资源规范与manifest继续由art_resources维护。')

registry='docs/art_resources/asset_registry.md'
edit_existing(registry,lambda t:t.replace('## 阶段一历史视口验证样本（2026-10-22）','<a id="阶段一已验证小批次"></a>\n\n## 阶段一历史视口验证样本（2026-10-22）').replace('## 本轮关卡证据','## 历史关卡证据（原记录日期2026-10-22，非本次验证）')+
 '\n## 2026-10-30 文档整理说明\n\n仅同步导航/历史锚点，资源记录与manifest未改。县城需求见[场景](requirements/召陵县/场景素材需求.md)和[角色](requirements/召陵县/角色素材需求.md)。本页历史关卡、UE路径和可见证据不能证明县城Demo已实现。\n')

# Remove the small overlap in templates: scenario/world content lives in the content template.
p=ROOT/'docs/templates/PRD/产品总纲与全局规则模板.md'
t=p.read_text(encoding='utf-8')
t=re.sub(r'\n<a id="source-template-231"></a>.*?(?=\n## 元信息与可追溯性)', '\n世界设定与叙事字段引用[内容与剧本模板](内容与剧本模板.md)，不在总纲模板重复填写。\n',t,flags=re.S)
p.write_text(t,encoding='utf-8')
mp=json.loads((B/'migration_primary.json').read_text(encoding='utf-8'))
mp=[x for x in mp if not (x['source'].endswith('游戏策划案模板.md') and x['source_start']==231)]
mp.append({'source':'docs/PRD/'+source_names['玩法'],'source_start':863,'source_end':890,'target':d,'target_anchor':'完整游戏待确认问题原文保留','disposition':'待决；旧骑将独立目标备注作废'})
(B/'migration_primary.json').write_text(json.dumps(mp,ensure_ascii=False,indent=2),encoding='utf-8')
print('Wrote decision log, current navigation, eight supporting historical banners and art-index synchronization; originals backed up.')
