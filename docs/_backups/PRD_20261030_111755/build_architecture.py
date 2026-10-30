from pathlib import Path
import re, json, os

ROOT = Path(__file__).resolve().parents[3]
BACKUP = ROOT / 'docs/_backups/PRD_20261030_111755'
SOURCE = BACKUP / 'original_PRD/玩法系统'
OUT = ROOT / 'docs/architecture'
P = {
 'index':'README.md',
 'boundary':'01-系统边界/01-系统边界与权威写入.md',
 'baseline':'01-系统边界/02-现状基线与证据.md',
 'ledgers':'01-系统边界/03-三本账与WRK.md',
 'time':'02-公共契约/01-时间身份与控制权.md',
 'command':'02-公共契约/02-Command事件与Receipt.md',
 'query':'02-公共契约/03-受限查询与投影.md',
 'handoff':'02-公共契约/04-多精度与Handoff.md',
 'registry':'03-Owner领域/01-Owner注册表.md',
 'domains':'03-Owner领域/02-领域Owner详细契约.md',
 'character':'03-Owner领域/03-角色档案事实与心智.md',
 'models':'04-模型与结算/01-领域模型注册绑定与评估.md',
 'settlement':'04-模型与结算/02-数值状态效果与跨Owner结算.md',
 'ue':'05-运行时接入/01-UE本地提交与Paralls同步.md',
 'agent':'05-运行时接入/02-Agent群体与动画接入.md',
 'esm':'05-运行时接入/03-ESM复用与迁移.md',
 'recovery':'06-存档与可观测性/01-存档回放与故障恢复.md',
 'evidence':'06-存档与可观测性/02-可观测性与验收证据.md',
}
T = {k:Path(v).stem for k,v in P.items()}
T['index']='Guoshang 技术架构'
S = {
 'a':'01-Paralls现有Owner与接入分析.md',
 'b':'02-Guoshang新Owner需求与统一Command规范.md',
 'c':'03-基建Owner传统方案与Paralls兼容方案.md',
 'd':'Owner体系/README.md',
 'e':'Owner体系/01-Owner分类与Paralls实现对照.md',
 'f':'Owner体系/02-角色档案、权威状态与心智状态对接.md',
 'g':'Owner体系/03-数值规则、状态效果与跨Owner结算.md',
 'h':'Owner体系/04-领域模型注册、绑定与Owner评估架构.md',
 'demo':'05-第一阶段县城守城Demo设计与执行路线.md',
 'plan':'08-基础设施与Owner建设总计划.md',
 'spec':'docs/superpowers/specs/2026-10-27-ue-paralls-fidelity-alignment-design.md',
 'master':'docs/PRD/烽火王座：汉末群雄_总策划案_v1.0.md',
 'stages':'docs/PRD/国殇：汉末_五阶段战争世界设计大纲_v0.1.md',
}
LINES = {k:((ROOT/v) if k=='spec' else (BACKUP/'original_PRD'/Path(v).name) if k in ('master','stages') else (SOURCE/v)).read_text(encoding='utf-8-sig').splitlines() for k,v in S.items()}
DOCS={k:[] for k in P}
ROUTES=[]

def rel(origin, target, anchor=''):
    return Path(os.path.relpath(OUT/P[target], (OUT/P[origin]).parent)).as_posix() + (('#'+anchor) if anchor else '')

def link(origin,target,anchor='',label=None):
    return '['+(label or T[target])+']('+rel(origin,target,anchor)+')'

def raw(src,start,end):
    return '\n'.join(LINES[src][start-1:end]).strip()

def route(src,start,end,target,anchor,disposition='moved',note=''):
    # Split at every source heading: leaf sections are traceable independently.
    indices=[start]+[i for i in range(start+1,end+1) if re.match(r'^#{1,6} ',LINES[src][i-1])]+[end+1]
    for lo,hi in zip(indices,indices[1:]):
        if not any(x.strip() for x in LINES[src][lo-1:hi-1]): continue
        ROUTES.append({'source_path':S[src] if S[src].startswith('docs/') else 'docs/PRD/玩法系统/'+S[src], 'source_lines':{'start':lo,'end':hi-1},'source_heading':next((x.lstrip('# ').strip() for x in LINES[src][lo-1:hi-1] if re.match(r'^#{1,6} ',x)), '段落/表格'), 'target_path':'docs/architecture/'+P[target], 'target_anchor':anchor, 'target':'docs/architecture/'+P[target]+'#'+anchor,'disposition':disposition,'note':note})

def text_block(target,anchor,title,content):
    DOCS[target].append('<a id="'+anchor+'"></a>\n\n## '+title+'\n\n'+content.strip()+'\n')

def add(target,anchor,title,src,start,end,disposition='moved',note=''):
    body=raw(src,start,end)
    # Source headings become descriptive subheadings; old section numbers are not a second hierarchy.
    cleaned=[]
    for line in body.splitlines():
        m=re.match(r'^(#{2,6})\s+(.*)$',line)
        if m:
            title0=re.sub(r'^(?:\d+(?:\.\d+)*[.、]?\s+|[A-N][.、]\s+)','',m.group(2))
            line='### '+title0
        cleaned.append(line)
    text_block(target,anchor,title,'\n'.join(cleaned))
    route(src,start,end,target,anchor,disposition,note)

def ref(src,start,end,target,anchor,note,disposition='consolidated'):
    route(src,start,end,target,anchor,disposition,note)

def write(keys):
    for key in keys:
        dest=OUT/P[key];dest.parent.mkdir(parents=True,exist_ok=True)
        header='# '+T[key]+'\n\n> 版本：1.0（职责拆分版）\n> 更新日期：2026-10-30\n> 评审状态：职责归位与静态一致性核对；不替代产品待决项裁决或实现评审。\n> 实现状态：本篇为目标合同；已有实现仅按原始证据日期记录，不代表全量实现或运行验收完成。\n> 验证范围：本轮仅重组文档，未执行代码、UE、PIE 或性能验证。原始设计、实现盘点和证据日期分别保留。\n'
        if key!='index': header+='\n'+link(key,'index',label='技术架构入口')+' · '+link(key,'registry','owner-registry','唯一 Owner 注册表')+'\n'
        dest.write_text(header+'\n'+'\n'.join(DOCS[key]),encoding='utf-8')

def build_index_registry():
    text_block('index','technical-reference','技术权威与阅读入口', '''本目录统一维护公共技术合同、逻辑 Owner、领域结算和运行时接入；产品目标与玩法体验由 `docs/PRD/` 的正式分区维护，建设批次与切片排程由生产计划维护。技术目录不重新建立“骑将冲阵”独立产品目标。

所有实现状态分开记为：**已定义、可执行、已接入、已验收**。本轮完成的是文档结构与合同归位，不把设计文本、模块存在或静态复核升级成实现完成。

| 技术主题 | 权威入口 |
|---|---|
'''+ '\n'.join('| '+label+' | '+link('index',k,a)+' |' for label,k,a in [
('系统边界与唯一写权','boundary','system-boundaries'),('现状、证据日期与缺口','baseline','evidence-baselines'),('三本账与WRK','ledgers','three-ledgers'),('时间、身份、控制与暂停','time','time-identity-control'),('Command/Event/Receipt与失败','command','command-event-receipt'),('受限Query/UI投影','query','restricted-projections'),('多精度、lease与handoff','handoff','handoff'),('唯一23逻辑Owner名单及Manifest','registry','owner-registry'),('领域详细合同','domains','domain-contracts'),('角色档案、事实与心智','character','character-state'),('模型注册、Binding与评估','models','domain-models'),('数值、效果与跨域结算','settlement','numeric-settlement'),('UE本地提交/同步与完整节奏矩阵','ue','ue-paralls'),('Agent/群体/语义动画','agent','agent-population'),('ESM复用与迁移','esm','esm-migration'),('存档/回放/恢复','recovery','save-replay-recovery'),('观测、fixture与证据','evidence','acceptance-evidence')]))
    text_block('index','authority-rules','维护规则', '''- 23 个逻辑领域 Owner 的完整注册表只维护在注册表一处；宿主、模块、分区与工作流不增加计数。
- 全量 UE 协作与节奏矩阵只维护在 UE/Paralls 接入文档，其他文档链接引用。
- 公共信封、时间/身份、epoch、lease、receipt、暂停与受限投影只在公共契约维护；领域文仅细化本域规则。
- 医疗是 Medical Workflow；Composite 是组合流程；Ability/Skill、ESM、表现层与 WRK 不因名称新增领域写权。
- 唯一 canonical EventStore 表示唯一逻辑权威账本，不能误写成所有事实必须由 Python 后端提交。获准本地可靠提交可最终确认；只有后端提交端时本地保持 pending/predicted。
- 原始 PRD 的只读副本和逐节迁移清单在 `docs/_backups/PRD_20261030_111755/`；旧专题不再构成并行正式规范。''')
    text_block('index','historical-spec','历史设计与未决差异', '''既有 [2026-10-27 fidelity draft](../superpowers/specs/2026-10-27-ue-paralls-fidelity-alignment-design.md) 保持原样。其双轴精度、lease、连续性、语义动画和验收细节在本目录按主题引用；其旧产品目标、旧实施顺序与 draft 状态不能覆盖当前产品和生产计划。

该 draft 的 UE 时钟措辞统一解释为选定部署下的时钟入口/投影，而非允许多份可写世界时钟；笼统“UE Owner”按当前领域注册表逐域解释。角色 embodiment/intent lease 不能替代领域 authority_scope/epoch。断线战术脑只能在明确登记的降级控制权与有效意图/许可内工作，不能自动产生新的 C3 自主意图。

待决项必须带来源：跨区域环境事实归属尚待登记；SGC-3 真实 handoff 完整性仍须实现证据；具体响应预算与时间倍率等待实测，不填虚构已测数值。旧 draft 要求“进入实现计划前真实 handoff”的过程约束与当前排程差异交生产计划裁决。''')
    # One merged table: final order from 08, expanded content scope from 05.
    p_rows=[x for x in LINES['plan'][92:115] if x.startswith('|')]
    d_rows=[x for x in LINES['demo'][187:211] if x.startswith('|')]
    demo={x.split('|')[1].strip():[p.strip() for p in x.split('|')[1:-1]] for x in d_rows}
    text_block('registry','owner-registry','唯一逻辑领域 Owner 注册表', '''本表是唯一完整名单：**23 个**逻辑领域写权。别名不重复计数；一个模块可承载多个 Owner，同一 Owner 可按区域/实体流分区。宿主数量和近远场精度不改变逻辑领域。建设批次、任务依赖与放行时间归生产计划；本表保留第一阶段/后续内容覆盖和领域完成标准，不以排程代替合同。

完整近场/远场分类见 '''+link('registry','ue','ue-cadence-matrix','UE 协作与节奏矩阵')+'''，这里不复制第二套部署名单。

| # | Owner | 唯一事实与关键边界 | 事实覆盖补充 | 第一阶段内容 | 后续扩展 | 领域能力标准 |
|---|---|---|---|---|---|\n'''+ '\n'.join('| '+' | '.join([p.split('|')[1].strip(),p.split('|')[2].strip(),p.split('|')[3].strip()]+demo[p.split('|')[2].strip()][1:])+ ' |' for p in p_rows))
    ref('plan',87,115,'registry','owner-registry','最终23名单和事实边界迁入唯一注册表；批次列由production维护')
    ref('demo',180,213,'registry','owner-registry','按08最终23顺序合并第一阶段/后续覆盖与能力标准；Medical行转下方Workflow')
    add('registry','non-owner-responsibilities','不计入领域名单的职责','plan',117,125)
    text_block('registry','medical-workflow','Medical Workflow', '医疗只拥有治疗请求、方案步骤、执行进度与待完成义务。医舍队列、治疗中断和回执汇总可扩展到长期护理；它编排 Inventory、Body、Status，并校验 LifeState，不取得这些领域的写权。流程状态可恢复。详见 '+link('registry','settlement','medical-workflow','医疗结算与中断')+'。')
    add('registry','owner-classification','Owner 分类轴与支撑组件','e',5,35)
    add('registry','owner-manifest','完整 Registry / Manifest 字段','e',95,120)
    add('registry','seven-part-contract','七部分领域合同与模型依赖','b',132,166)
    add('registry','owner-delivery','每个 Owner 的完整交付包','plan',127,141)
    add('registry','delivery-details','完整包的补充字段与状态目录','demo',215,232)
    add('registry','cross-stage-coverage','跨阶段事实覆盖审查','demo',234,249)
    write(['index','registry'])

def build_foundations():
    text_block('boundary','system-boundaries','系统边界与唯一最终写权', '''Owner 是对某类事实的唯一最终写权，不是模块、宿主、模型、Actor 或工作流的别名。逻辑领域以唯一注册表为准；运行宿主与领域写权分离。UE 可以承载获准 Owner 的本地实现，Actor、动画、Ability、Timer 和 Gateway 不因此自动取得事实写权。

以下原始架构图保留的是因果链与分工语义；其中 Godot 是 Paralls 历史表现端，Guoshang 的运行宿主为 UE。任何“UE Owner”均按具体领域、作用域和 authority epoch 解释，不存在覆盖所有事实的引擎通用写权。''')
    for x in [('paralls-spine','已有结算脊柱与接入原则','a',10,27),('source-neutral-command','统一行动来源与事实边界','b',10,66),('long-world-boundary','连续战争世界与传统能力边界','c',12,29),('integration-principles','接入原则','a',169,176),('architecture-map','组件架构与写权图','e',122,153),('non-goals','技术非目标','b',458,466)]: add('boundary',*x)
    add('boundary','demo-causal-chain','组件分类与唯一因果链','demo',130,168)
    # The old classification line contains a second full roster; replace with the canonical link.
    DOCS['boundary'][-1]=re.sub(r'^\| Domain Owner \|[^\n]+$', '| Domain Owner | '+link('boundary','registry','owner-registry','唯一逻辑领域 Owner 注册表')+' 中登记的领域 | 对本领域事实做准入、结算和唯一写入 | 是，且只写自己的事实流 |',DOCS['boundary'][-1],flags=re.M).replace('### 五类组件边界','### 组件类别与宿主边界')
    add('boundary','technical-success','正式基础设施、连续性、有限知情和实时约束','plan',34,39)
    text_block('boundary','shared-infrastructure','共享基础设施能力与基础权威', '''以下 I01—I10 是共享基础设施能力，不计入领域 Owner 数量；批次、首次交付和持续验收的排程由生产计划维护。

| 工作包 | 必须建设的能力 |
|---|---|
'''+ '\n'.join('| '+ ' | '.join([c.strip() for c in row.split('|')[1:3]])+' |' for row in LINES['plan'][73:83]))
    text_block('boundary','shared-infrastructure-acceptance','共享能力的持续验收语义', '''| 工作包 | 不随排程丢失的验收语义 |
|---|---|
| I01 | 交接不更换角色身份；旧 authority epoch 不可写 |
| I02 | 所有来源同路；近场允许受控本地调用 |
| I03 | 确认后崩溃不丢事件、不重复结算；后端与本地权威路径分别验收 |
| I04 | 暂停不推进时间、命令传递、Agent、动画和领域变化 |
| I05 | 正式模型链覆盖所有适用领域；领域内复用、跨域写入拒绝 |
| I06 | 迟到报告、误报、未知和全知隔离均有正式验证 |
| I07 | 交付真实流程；流程不能替代 Owner 写领域事实 |
| I08 | 单一推进和交接可回归；视野内已激活角色持续控制获准语义动画 |
| I09 | 连接、可靠本地提交、全链恢复和回放分别有证据 |
| I10 | 每轮交付证据；最终汇总验收和可启动试玩包 |''')
    ref('plan',68,83,'boundary','shared-infrastructure','完整能力列迁入技术规范；交付批次列仅由production维护')
    add('boundary','foundation-authority','身份、时间和能力授权的基础权威','plan',85,85)
    text_block('boundary','integration-ownership','技术责任分工与集成', '''人员配置和任务排程见生产计划。技术分工保持单一负责人和统一 schema/写权评审；实际代码文件须经过盘点后登记，不能把本设计当成已接入事实。

| 工作线 | 负责范围 | 对外交付 | 不得承担的写权 |
|---|---|---|---|
'''+ '\n'.join(LINES['plan'][306:311])+'\n\n'+raw('plan',313,313))
    ref('plan',301,313,'boundary','integration-ownership','保留完整技术分工及边界；人员、批次与任务排程由production维护')

    text_block('baseline','evidence-baselines','设计状态、证据日期与当前实现', '''本篇是原始盘点的归位，**没有在 2026-10-30 重新运行或验证代码**。

| 来源 | 原始日期与状态 | 允许得出的结论 |
|---|---|---|
| Paralls 接入分析 | 2026-10-30 静态复核，原 v0.2 | current 只表示源文记录的代码/测试/正式运行时文档证据；planned 仍为目标 |
| 统一 Command 需求 | 2026-10-30 需求草案，原 v0.2 | 合同要求，不代表运行接入 |
| Guoshang 实现盘点 | 2026-10-28 PRD 基础设计 | 保留当时盘点，未经本轮刷新 |
| Fidelity 对齐 spec | 2026-10-27 draft | 历史设计输入，不可升级为生产证据 |

源文列出的本机 Paralls 路径只用于证据追踪；它们不成为运行时硬编码或新的机器配置保证。''')
    for x in [('paralls-baseline','Paralls 已有窄基线','a',61,81),('connection-gaps','连接状态与不能宣称完成的部分','a',148,167),('reference-sources','历史参考源与定位','a',178,190),('reuse-categories','四类复用方式','c',31,38),('compatibility-inventory','基础能力兼容盘点','c',40,66),('guoshang-20261028','Guoshang 2026-10-28 代码盘点','c',68,98),('owner-current-baseline','Owner 与当前 Paralls 实现的关系','e',81,93)]: add('baseline',*x)
    for k,ranges in {'a':[(1,8)],'b':[(1,8)],'c':[(1,10)],'e':[(1,3)],'f':[(1,3)],'g':[(1,5)],'h':[(1,3)]}.items():
        for lo,hi in ranges: ref(k,lo,hi,'baseline','evidence-baselines','来源标题/元信息已归入日期与证据表，不继承原版本号作为正式文件名')

    add('ledgers','three-ledgers','真相、记忆与表现三本账','a',29,59)
    add('ledgers','writeback','世界确认后的三本账回写','b',417,426)
    add('ledgers','dataflow','Owner 数据流与投影','e',175,192)
    add('ledgers','demo-ledgers','三本账在县城场景中的边界','demo',170,178)
    add('ledgers','wrk','WRK 的完整职责与禁区','c',180,213)
    add('ledgers','wrk-demo-contract','WRK 窗口、暂停和恢复补充','demo',251,266)
    add('ledgers','pause-ledger-link','三本账和暂停的共同边界','c',170,178)
    text_block('ledgers','wrk-authority','WRK 不接管领域写权','WRK 管理时间、窗口、预算、固定读集、依赖、重试、超时、开放义务和恢复；不能把调度结果自行变成领域事实。统一暂停的控制 epoch、回调隔离与提交屏障见 '+link('ledgers','time','pause','暂停合同')+'；工作流的部分完成与补偿见 '+link('ledgers','settlement','numeric-settlement','跨 Owner 结算')+'。')

    text_block('time','time-identity-control','共享时间、稳定身份与控制合同', '''共享身份/时间/能力授权具有明确基础权威和唯一写入口；领域不得各自复制可写时钟和授权表。角色/实体身份贯穿近远场、死亡、表现加载与存档恢复。

`world_tick` 是逻辑世界的单调时间基准；UE 时钟入口只是所选部署下对同一时间合同的实现/投影。渲染时间和网络健康检查的 wall-clock 不等于世界时间。事件发生、角色获知、画面呈现分别用 `event_time`、`known_time`、`presented_time`，迟到报告不能改写发生时间。''')
    add('time','identity-time-fidelity','连续性、时钟与版本的历史设计要求','spec',40,62)
    text_block('time','authority-epoch','领域写权 epoch 与两种 lease', '''必须分别登记：
- 领域 `authority_scope` / `authority_epoch`：哪个提交端能确认哪类事实流；旧 epoch 被 fencing 后不再可写。
- `intent lease`：哪个推进者可以为角色产生新的自主意图。
- `embodiment lease`：哪个执行/表现绑定当前身体动作；玩家接管与 Agent 的优先级由控制合同处理。

三者不可互相代替。C/P 精度切换、Actor 创建/销毁或 possession 不自动转移 Body/Combat 等领域写权。注册字段见 '''+link('time','registry','owner-manifest','Owner Manifest')+'；控制与领域迁移边界见 '+link('time','handoff','handoff','Handoff')+'。')
    add('time','cadence-contract','六种独立节奏与体力窗口','g',183,198)
    add('time','numeric-cadences','数值、角色与动画推进方式','plan',279,290)
    add('time','pause','暂停、时停、control_epoch 与回调隔离','spec',384,396)
    text_block('time','pause-authority','暂停的统一解释','暂停可以编辑/排队意图；不得使传令、Agent 新决策落地、语义动画、领域积分或计时器推进。网络与模型响应可返回，但进入隔离区；恢复后对 epoch、TTL、revision 和权限重新准入。当前计划也服从暂停。WRK 屏障不能只停止画面或仅停止某一个宿主。')

    add('command','command-event-receipt','Intent、Command、Event 与来源中立性','b',34,66)
    add('command','gateway','Command Gateway 完整信封、生命周期与职责','b',68,130)
    add('command','receipt','EventStore 与 Receipt 的最小完整合同','demo',296,320)
    add('command','military-command-sequence','发布守城命令的完整协作时序','b',373,408)
    add('command','legacy-local-sequence','传统 UE 与正式提交链时序','c',144,168)
    add('command','owner-sequence','领域模型和事实提交时序图','e',155,173)
    text_block('command','failure-recovery','失败、未知结果与恢复的共同语义', '''拒绝、取消、超时、部分完成、执行失败和提交结果未知必须可区分；不能把超时等同未提交。未知结果优先按 `command_id` / 幂等键查询原 receipt，不能重新生成事实或先补偿再查询。重复请求返回原确认结果；retry 不重复结算。

短事务在同一受控提交端通过各 Owner 授权 fragment 组成 AtomicEventBatch；跨端流程由步骤 receipt、开放义务、恢复游标和新事件补偿恢复，不假称全局原子提交。详见 '''+link('command','settlement','cross-owner-transactions','跨域事务')+' 与 '+link('command','recovery','save-replay-recovery','恢复合同')+'。')
    ref('demo',268,294,'command','gateway','统一信封/来源/生命周期和准入与本篇完整合同合并，不另建第二个Command规范')

    add('query','restricted-projections','角色的合法查询、感知与禁止读取','a',102,117)
    text_block('query','query-ledgers','三本账投影、UI 与调试隔离', '''正式玩法读取必须经 Query/Projection，附身份、作用域、权限、时空范围、感官/注意/通信条件与来源证据；真相账不能直接喂给角色、玩家地图或普通 HUD。

SelfState 只暴露角色可知的身体/需求状态和 freshness；公共事实经事件、观察或报告进入记忆，迟到、误报、未知、过期都保留。已提交的 debug receipt 不代表该角色已经知情。`event_time`、`known_time_by_recipient`、`presented_time` 不能混用。

跨域 Resolver 读取固定版本的受限投影/授权片段，记录读集 revision；模型输入未知必须返回 unknown 或按显式策略拒绝，不以缺省全知值补足。角色私有档案与记忆按 admission / knowledge cut 进入获准上下文，C2 预热不提前暴露。''')
    text_block('query','query-related','相关合同','角色事实、档案与心智字段见 '+link('query','character','character-state','角色状态')+'；固定输入和 unknown 策略见 '+link('query','models','domain-models','领域模型')+'；连续性快照隔离见 '+link('query','handoff','handoff','handoff')+'。')

    text_block('handoff','handoff','精度与权威交接的总合同', '''认知 C 轴和表现 P 轴独立；不是每个高表现对象都运行完整 Agent，也不是 Agent 激活就取得任意身体/事实写权。这里的协议是目标合同，SGC-3 真实链路仍需要独立运行证据。

历史 spec 的“UE Owner”统一细化为具体获准领域 Owner；其中身体/死亡事实归 Body、Status、LifeState 对应写入口。ready 只表示预热完成，成功的 handoff receipt 和 fencing 才允许新推进者生效。''')
    add('handoff','fidelity-axes','双轴精度与组合矩阵','spec',64,95)
    add('handoff','continuity-state','完整连续性状态 schema','spec',136,182)
    add('handoff','handoff-protocol','触发、请求、快照、lease 顺序与失败恢复','spec',184,284)
    add('handoff','activation-contract','群体升级、降级与游标','demo',322,329)
    add('handoff','authority-migration','领域迁移、并发结算与中断边界','g',139,148)
    add('handoff','cross-host-handoff','近远场四步交接与持续条件','plan',292,299)
    text_block('handoff','handoff-safety','断线和控制权的适用边界', '''同一角色/窗口只能有一个推进者；旧命令、旧 lease 和旧 authority epoch 均受 fencing。C2 预热不能读取未获准私有记忆；未知提交结果先查询或作为开放恢复状态带入，不可丢弃。

控制权移交不改变角色身份，不会自动迁移 Body 等领域事实写权；身体/领域写权迁移必须单独完成 Manifest、提交端和 epoch 交接。断线只允许在登记的 fallback 权限、有效 lease/TTL 和已准入计划内安全继续；不能为“本地战术脑”默许无限产生新的 C3 自主策略。''')
    write(['boundary','baseline','ledgers','time','command','query','handoff'])

def build_domains_models():
    text_block('domains','domain-contracts','详细领域合同的阅读边界','完整名单与唯一事实边界只维护于 '+link('domains','registry','owner-registry','Owner 注册表')+'。本篇按因果链保留已有详细 Static Data、State、Command、Resolver、Authority、Event/Result 和 Query/Projection 合同；下文原 P0/P1/P2 标签仅代表旧需求优先层级，正式执行顺序见生产计划，不与表现 P0—P3、V0—V5 或 A—F 批次混用。')
    add('domains','military-domain','位置、军令、军事组织与战场因果','b',168,254)
    add('domains','presence-semantics','Presence 语义提交点','demo',331,341)
    add('domains','military-semantics','Dispatch、Organization、命中与士气语义','demo',343,363)
    text_block('domains','dispatch-authorization','Dispatch 只验证和引用授权','Dispatch 负责命令的发出/传递/接收/取消等事实；授权事实来自 Organization、Government 或明确基础权威。旧材料中的“命令授权”在 Dispatch 语境仅指授权依据校验，不能生成另一份相互冲突的许可。')
    text_block('domains','objective-authority','Objective 的确认边界','胜负只能由 Objective 依据正式事件、配置和依赖完整性确认；控制事实由 Territory 等实际领域确认，Objective 不直接写入战斗、占领或死亡。援军、敌退、控制、投降、LifeState 和逃跑等触发及时评估；具体胜负条件、30 日体验目标及可选行动由正式产品文维护。')
    ref('demo',365,380,'domains','objective-authority','只迁入领域写权和正式依据；胜负产品阈值迁入县城Demo体验与验收，不复制产品规则')
    add('domains','resource-domains','库存、运输、生产设施、人口劳作与生存','b',265,333)
    add('domains','resource-contract-supplement','资源字段、来源、绑定与运输后果','demo',386,406)
    add('domains','production-contract-supplement','生产完整公式、模型分工与认证','demo',408,422)
    add('domains','body-domains','生存、身体和 Medical 的领域边界','demo',424,426)
    add('domains','social-government','社会、情报与政务','b',335,371)
    text_block('domains','domain-dependencies','公共契约与数值结算','伤害/体力/效果的并发、死亡和医疗中断详见 '+link('domains','settlement','numeric-settlement','结算合同')+'；角色能否知道某一事实详见 '+link('domains','query','restricted-projections','受限投影')+'；执行节奏仅引用 '+link('domains','ue','ue-cadence-matrix','唯一完整 UE 协作矩阵')+'。')

    add('character','character-state','角色数据分区、静态档案与动态事实/心智','f',5,101)
    add('character','character-flow','角色架构、时序与数据流图','f',132,186)
    add('character','immediate-private-boundary','强制即时反应、士气与私有判断','g',213,221)
    text_block('character','character-admission','角色状态与领域的交界','档案的 authored_static、事实 world_dynamic、私有心智 agent_private 各守写权；Dossier admission、profile_revision、SelfState 的来源/版本/freshness 必须固定。动机压力不会直接消耗公共库存，Agent 只能提出 ActionIntent，再经公共 Command 合同。控制与 handoff 不迁移 Body 写权，详细治疗/受伤因果见 '+link('character','settlement','medical-workflow','医疗工作流')+'。')

    add('models','domain-models','同域复用、模型类型与泛化边界','h',5,111)
    add('models','model-definition','完整 Model Definition','h',113,144)
    add('models','applicability-binding','完整 Applicability Binding 与匹配','h',146,181)
    add('models','evaluation-context','完整 Evaluation Context 与结果','h',183,217)
    add('models','food-wood-examples','食品变质和木材腐朽完整参考模型','h',219,282)
    add('models','other-domain-examples','运输、生产与战斗模型示例','h',284,315)
    add('models','model-responsibilities','Owner 模型职责与反例','h',317,356)
    add('models','model-dependency','领域 Owner 对模型的依赖合同','e',36,56)
    add('models','reference-implementation-contract','正式模型链及仓储边界切窗','plan',226,237)
    add('models','model-related-documents','领域模型与相邻主题的关系','h',373,379)
    text_block('models','model-execution-link','执行一致性和证据','模型/Binding/Static Data 的版本、单位、随机算法/seed、稳定顺序和输入 revision 是跨宿主共同合同；C++/Python 固定向量等价性、旧版本回放与 unknown 环境输入见 '+link('models','ue','model-equivalence','UE 与 Paralls 模型一致性')+'。评估、积分、提交、同步和 Agent 决策频率分别登记，禁止额外建立万能损耗 Owner。')

    add('settlement','numeric-settlement','Numeric、Condition、Hybrid 与状态效果','g',7,72)
    add('settlement','cross-owner-transactions','短事务、长流程、开放义务与补偿','g',74,99)
    add('settlement','atomicity-scope','跨 Owner 原子性的提交端边界','b',410,415)
    add('settlement','medical-workflow','受伤、防护、流血和治疗完整因果','f',103,130)
    text_block('settlement','body-serialization','Body 串行化、幂等和终局保护', '''Body 对伤害、持续效果 tick、恢复与治疗实行同一事实流的 revision/CAS 串行化；并发准入不能让体力变成负数或重复消耗。效果 tick 的幂等键至少包含 `effect_id + scheduled_world_tick`，治疗步骤至少包含 `treatment_id + step`。

生命值归零是 Body 输入，不等于自动死亡；倒地、濒死、死亡由 LifeState 按合法依据转移。死亡后的普通迟到治疗不能覆盖终局；治疗中断保留已消费物资和已发生步骤，下一步依 receipt / 开放义务恢复。医疗流程不获得 Inventory、Body、Status 或 LifeState 写权。''')
    add('settlement','transport-interruption','运输被玩家干扰的完整结算','g',223,235)
    add('settlement','settlement-diagrams','结算架构、时序与数据流图','g',237,301)
    add('settlement','required-cross-owner-workflows','九条跨 Owner 因果闭环与中断边界','plan',210,224)
    text_block('settlement','continuous-integration','连续积分、切窗与跨域边界','体力、损耗、效果和生存指标各按本域模型和固定输入切窗；输入改变、阈值、暂停、转仓、设施/通风变化、绑定启停、版本升级与 handoff 都结束当前窗口，不能新旧推进者重复积分。效果、治疗与死亡竞态的迁移规则见 '+link('settlement','handoff','authority-migration','领域交接')+'。未知提交结果先查原 receipt；补偿产生新的合法事件，不擦去真实损失。')
    write(['domains','character','models','settlement'])

def build_runtime_evidence():
    text_block('ue','ue-paralls','UE 承载、Paralls 协作与唯一逻辑提交权威', '''本篇是近场/远场执行、可靠本地提交和同步的唯一技术入口。UE 是执行宿主，不是通用领域 Owner；每个范围显式登记 authority_mode、owner_host、writer、store、scope 和 epoch。近场实时协作不要求每一步跨 Python RPC，分域不等于分进程。

唯一 canonical EventStore 是逻辑权威约束。获准本地可靠持久化并产生 receipt 的提交可以是最终事实；后端只接副本/投影，不再次结算。只配置后端提交端时，UE 在 receipt 前保持 pending/predicted；断线不能把本地预测自动升格为权威。''')
    add('ue','reusable-primitives','Paralls 可复用基础原语','c',100,114)
    add('ue','host-authority-boundaries','传统 UE 与 Paralls 的责任与提交边界','c',118,142)
    add('ue','host-manifest','宿主、模式、写入口、存储和范围登记','e',58,79)
    add('ue','mirror-adapter','UE Presentation / Mirror Adapter 不新增领域','b',256,263)
    add('ue','workflow-wrk-boundary','UE、Workflow、WRK 与 Manifest 分工','g',101,124)
    add('ue','combat-compatibility','Combat、Body、Medical 的七项兼容判据','g',126,137)
    add('ue','local-domain-collaboration','各域本地协作和实时调用链','g',150,181)
    add('ue','local-commit','本地可靠提交与后端同步的完整条件','g',200,211)
    add('ue','high-frequency-execution','帧循环、语义提交点、ESM 和断线边界','demo',428,464)
    add('ue','deployment-authority','高频近场部署与最终确认','plan',239,245)
    add('ue','ue-cadence-matrix','全量 UE 协作与节奏矩阵（唯一完整矩阵）','plan',247,277)
    add('ue','model-equivalence','UE 与 Paralls 模型执行一致性','h',383,387)
    add('ue','fidelity-role-boundaries','历史 Fidelity 设计中的三方职责','spec',97,134)
    text_block('ue','disconnect-recovery','断线、重连与权限边界', '''断线不允许扩大本地 authority_scope、epoch、intent lease 或库存额度。已登记本地权威可按有效授权可靠提交并积累 outbox；后端恢复后按事件身份、稳定序、revision 和 confirmed cursor 对账去重。后端专属提交范围保持 pending/predicted 或明确失败，不伪造最终 receipt。

Agent/执行通道 TTL 到期按 capability manifest 的安全状态处理；仅有 fallback 许可时才可继续已准入计划或受限恢复。旧 control_epoch、乱序 sequence、旧输入 revision、旧 authority epoch 和过期动作均必须被拒绝/隔离。UI 显示 pending、unavailable 或 degraded 的真实状态，不能显示“已完成”掩盖未知提交。''')
    text_block('ue','canonical-runtime-links','部署与排程','逐域事实权威见 '+link('ue','registry','owner-registry','唯一注册表')+'；数值和 Agent 的独立更新合同见 '+link('ue','time','cadence-contract','节奏与窗口')+'；真实本地提交/故障证据见 '+link('ue','evidence','acceptance-evidence','验收规范')+'。矩阵原 D/V2/F 和 A5 等是原生产基线的放行要求，正式排程只由建设总计划维护，不能据此声称已交付。')

    add('agent','agent-population','角色智能体接入和群体单一推进者','a',83,100)
    add('agent','population-continuity','B0/B1/B2/B3 与群体升级','a',119,146)
    add('agent','fidelity-presentation','Agent 激活与动画激活矩阵','demo',466,478)
    add('agent','semantic-execution','命令、意图、执行生命周期与语义动画完整合同','spec',286,382)
    add('agent','activation-budgets','转层触发、预算、持续条件与锁','spec',454,519)
    text_block('agent','fidelity-authority-normalization','旧设计措辞和预算的适用范围', '''本篇保留 2026-10-27 draft 的 schema、优先级、TTL、动画 manifest 和执行生命周期。文内“UE 决定/产生事实”仅指获准领域实现；碰撞/寻路/动画证据经具体 Owner 确认，Actor 自身不写世界事实。旧“本地战术脑”只在获准 fallback 合同内继续计划，不在断线时产生无限新自主意图。

0.25 秒表现候选、0.5 秒 Agent 候选、1.5 倍退出半径等均为设计候选，不是本轮实测。已激活 C3 控制和即时强制限制不能被这些轮询周期延迟；渲染、模拟、评估、提交、投影同步和 Agent 决策分别登记。关键任务、可见性、交互、动作尾段和 handoff 锁决定持续激活；镜头转开不能无条件撤销角色。''')

    add('esm','esm-migration','ESM 复用边界、写入口 fence 与执行器迁移','a',193,208)
    text_block('esm','esm-scheduling-boundary','建设顺序与兼容底线','ESM 只是可选适配/复用路径，不能为了等待适配阻塞既定正式 Owner 合同；不能以 SDK、ESM、Godot 迁移或模块复用重新开放旧事实写入口。原基础设施建设顺序中的技术底线保留：先有事件/时间/恢复与 Command 合同，再由获准领域进入实时和 Agent 链。当前批次/切片的正式依赖见生产计划。')
    ref('c',215,221,'esm','esm-scheduling-boundary','技术边界归本篇；原建设顺序由production维护，不作为第二份排程')

    text_block('recovery','save-replay-recovery','保存、回放、未知提交与故障恢复', '''恢复单元包括：领域事件流及 stream revision、幂等记录/原 receipt、outbox 状态、投影 checkpoint、confirmed cursor、角色/事件/记忆游标、未决命令、开放义务、authority epoch、lease/control epoch、模型/Binding/Static Data 版本、固定输入/随机 seed 和稳定排序。

checkpoint 不能仅保存 Actor 字段；表现可重建，事实不能靠屏幕现状反推。事件回放重建领域状态，再重建受限投影与角色合法记忆。历史模型版本被固定；新公式或新 Binding 不改写历史损耗。schema/模型升级以版本化迁移和新事件表达，不能静默改旧事件。

确认后的进程崩溃必须恢复同一已提交事实与原 receipt；未确认/未知结果先查询幂等记录或提交端。重复 outbox、投影重试、网络乱序、重启及重连不得重复扣血、消费、产出或损耗。跨提交端没有全局 rollback：已发生损失保留，后续通过步骤 receipt、开放义务、补偿事件和恢复游标继续。''')
    text_block('recovery','local-recovery','本地提交、交接与暂停恢复','完整 durable local commit 条件见 '+link('recovery','ue','local-commit','可靠本地提交')+'；fencing、窗口结清、旧 epoch 拒绝与未知状态携带见 '+link('recovery','handoff','handoff','handoff')+'。暂停期间回调隔离，恢复后复核，不把 wall-clock 超时变成世界时间进展。字段与原因必须能在 receipt 中追踪。')
    text_block('recovery','crash-recovery-fixtures','必须覆盖的故障序列', '''- append/receipt/outbox/投影等边界的崩溃；确认后重启事实不丢、重复请求回原 receipt。
- receipt 丢失/乱序、后端断连和重连去重；后端专属提交未确认时不伪装本地最终结果。
- 伤害/效果/治疗/死亡并发；effects 按 effect_id + scheduled_world_tick、治疗按 treatment_id + step 幂等。
- handoff 中 freeze/drain、固定 revision/checkpoint/world_tick、新 epoch fencing，旧写入口与迟到命令被拒绝。
- 投影删除后重建、存档重载与下一阶段 fixture 继承；模型/Binding 版本升级不重写历史。
- 中断治疗、已消费库存、部分交付、运输损失和开放义务恢复；不假回滚已经发生的后果。''')

    text_block('evidence','acceptance-evidence','目标合同、证据与验证状态','以下检查全部是验收要求；本轮仅文档迁移，**未运行 UE、PIE、代码测试、失败注入或性能采样**。已定义、可执行、已接入、已验收分别记录；模块存在/窄测试/静态源码不能替代正式调用证据。通用日志、截图、资源预算和证据目录规范由 validation 正式入口维护。')
    for x in [('owner-ten-checks','每个新 Owner 的十项门槛','b',443,456),('compatibility-checks','传统能力与 Paralls 八项验收','c',223,234),('owner-landing-checks','Owner 三项落地判据','e',194,196),('character-checks','角色档案与事实/心智对接验收','f',188,192),('settlement-checks','结算、实时协作与交接验收补充','g',303,319),('model-fixture-checks','模型基础设施十项 fixture','h',358,371),('slice-evidence','每轮切片的证据要求','demo',622,633),('kernel-command-checks','合同、EventStore、WRK 与查询验收','demo',639,665),('high-frequency-checks','高频桥接、组织、战斗与动画能力检查','demo',673,707),('replay-release-checks','回放、失败注入、性能和可启动包','demo',709,719),('demo-acceptance-matrix','Demo 全链验收矩阵','demo',721,739),('infrastructure-tests','基础设施与高频桥接测试用例','demo',741,766),('evidence-discipline','运行证据和开发纪律','demo',779,790),('risk-stop-rules','技术风险与止损要求','demo',792,803),('fidelity-counterexamples','Fidelity 最低反例集','spec',433,452),('fidelity-protocol-checks','Fidelity 协议、时停、可玩链与证据产物','spec',521,562)]: add('evidence',*x)
    text_block('evidence','full-owner-check','全量领域完成检查','全量 Owner 的可执行规则、唯一写入口、提交/投影/回放/恢复与跨域流程均须按 '+link('evidence','registry','owner-delivery','完整交付包')+' 单独验收；不能以一条跑通链或空壳 receipt 宣称全量领域完成。旧能力门中的完整名单只引用唯一注册表。')
    ref('demo',667,671,'evidence','full-owner-check','全量Owner能力门归位为完整包验收，不复制23名单或第二份排程')
    add('evidence','failure-injection-stop','故障注入、证据齐全与停止扩张条件','plan',345,349)
    text_block('evidence','performance-evidence','性能证据与未测预算','渲染帧率、模拟步、模型评估、提交窗口、投影延迟、Agent 决策/语义动画响应分别测量。60Hz 体验目标与 draft 的数值都是目标/候选，不是本轮运行数据；不得用县城测试推断全国吞吐量。原测试的内存、显存、角色/Actor/资产数量、PIE 状态、定向编辑器/PIE 截图、版本和日志需按正式验证规范归档；大型操作前重新测量，不沿用历史基线。')
    write(['ue','agent','esm','recovery','evidence'])

def finish_routes():
    # Every leaf of all eight assigned originals has an explicit final disposition.
    ref('d',1,44,'index','technical-reference','原专题导航整合入唯一技术入口；共同规则归boundary/registry/UE公共合同')
    ref('b',428,441,'index','historical-spec','旧P0/P1/P2为原需求优先级；正式建设批次与切片排程由production维护','reference')
    ref('c',236,240,'boundary','system-boundaries','结论已合并到系统边界/唯一事实账与宿主分离')
    ref('demo',382,384,'domains','resource-domains','资源内容范围与领域完整能力区分；正式注册表与产品内容分别维护')
    for k in ['a','b','c','d','e','f','g','h']:
        covered=set()
        for r in ROUTES:
            if r['source_path']=='docs/PRD/玩法系统/'+S[k]: covered.update(range(r['source_lines']['start'],r['source_lines']['end']+1))
        gaps=[i for i,s in enumerate(LINES[k],1) if s.strip() and i not in covered]
        if gaps:
            # Only whitespace separators or source section title metadata may remain.
            for i in gaps: ref(k,i,i,'index','technical-reference','源标题/衔接语纳入技术入口；正文叶章节已逐项迁移','reference')

def absorb_product_technical_sections():
    add('boundary','product-responsibility-matrix','产品技术责任矩阵：有限底座与增量领域','master',582,594)
    add('settlement','composite-resolver','组合结算器与 receipt-driven recovery','master',596,600)
    ref('master',602,602,'domains','objective-authority','当前Demo死亡/投降/逃跑仍失败，后续Campaign继任不覆盖当前产品终局；产品验收正式维护','reference')
    add('time','world-cadence-order','连续时钟下的结算层次与推荐因果顺序','master',604,616)
    add('ue','product-technical-boundary','产品层共用的执行与断线技术合同','master',756,760)
    add('baseline','paralls-reference-index','Paralls 本地七组参考路径与有限实现边界','master',762,775)
    add('boundary','five-stage-integration','五阶段共用责任架构与唯一 canonical writer','stages',201,218)
    add('ue','five-stage-ue-contract','UE 执行、上报与受限降级职责','stages',220,227)
    add('agent','five-stage-paralls-contract','Paralls 角色、司命与群体职责','stages',229,235)
    add('boundary','no-authority-bypass','跨层越权禁止','stages',237,240)
    write(['boundary','settlement','time','ue','baseline','agent'])

def finalize_links():
    def to_file(origin,path,anchor=''):
        return Path(os.path.relpath(ROOT/path,(OUT/P[origin]).parent)).as_posix()+(('#'+anchor) if anchor else '')
    prod='docs/production/基础设施与Owner建设总计划.md'
    demo='docs/production/县城守城Demo执行计划.md'
    validations='docs/validation/验证与证据规范.md'
    for key in P:
        p=OUT/P[key]; body=p.read_text(encoding='utf8')
        def replace_link(m):
            label,url=m.group(1),m.group(2)
            stem=url.split('#')[0].replace('\\','/').split('/')[-1]
            fragment=url.split('#',1)[1] if '#' in url else ''
            dest=None
            if stem=='01-Paralls现有Owner与接入分析.md': dest=('esm','esm-migration') if 'esm' in fragment.lower() else ('baseline','evidence-baselines')
            elif stem=='02-Guoshang新Owner需求与统一Command规范.md': dest=('command','gateway')
            elif stem=='03-基建Owner传统方案与Paralls兼容方案.md': dest=('ue','ue-paralls')
            elif stem=='01-Owner分类与Paralls实现对照.md': dest=('registry','owner-registry')
            elif stem=='02-角色档案、权威状态与心智状态对接.md': dest=('character','character-state')
            elif stem=='03-数值规则、状态效果与跨Owner结算.md': dest=('ue','local-domain-collaboration') if fragment.startswith('44') else ('ue','workflow-wrk-boundary') if fragment.startswith('4-') else ('settlement','numeric-settlement')
            elif stem=='04-领域模型注册、绑定与Owner评估架构.md': dest=('models','domain-models')
            elif stem=='08-基础设施与Owner建设总计划.md':
                if fragment: dest=('ue','ue-cadence-matrix')
                else: return '[基础设施与 Owner 建设总计划]('+to_file(key,prod)+')'
            elif stem=='05-第一阶段县城守城Demo设计与执行路线.md': return '[县城守城 Demo 执行计划]('+to_file(key,demo)+')'
            elif stem=='README.md' and 'Owner体系/' in url: dest=('index','technical-reference')
            if dest:
                newlabel={'ue-cadence-matrix':'UE 协作与节奏矩阵','esm-migration':'ESM 复用与迁移','local-domain-collaboration':'近场领域实时协作','workflow-wrk-boundary':'UE、Workflow 与 WRK 边界'}.get(dest[1],T[dest[0]])
                return link(key,*dest,newlabel)
            return m.group(0)
        body=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',replace_link,body)
        replacements={
          '见第 9 节':'见 '+link(key,'esm','esm-migration','ESM 复用与迁移'),
          '正式提交位置见第 10.1 节':'正式提交位置见 '+link(key,'ue','local-commit','本地可靠提交合同'),
          '第 6 节的五阶段 Owner 基础设施范围':link(key,'registry','owner-registry','五阶段 Owner 基础设施范围'),
          '专项验收见该文第 9 节':'专项验收见 '+link(key,'evidence','settlement-checks','结算与实时协作验收'),
          '完整领域包仍按第 5 节验收':'完整领域包仍按 '+link(key,'registry','owner-delivery','Owner 完整交付包')+' 验收',
          '按建设总计划第 11.2 节逐域登记':'按 '+link(key,'ue','ue-cadence-matrix','UE 协作与节奏矩阵')+' 逐域登记',
        }
        for old,new in replacements.items(): body=body.replace(old,new)
        # A former Dispatch coverage alias never creates an authorization writer.
        if key=='registry': body=body.replace('命令授权、传达','命令授权依据校验与引用、传达')
        if key=='registry': body=body.replace('县令、亲卫、一营三队、村落和工坊负责人','县令、亲卫、一营三队（原县城配置，三队数量待决，见 [D03]('+to_file(key,'docs/PRD/00-产品总纲/设计决策与待决问题.md','d03')+')）、村落和工坊负责人')
        if key=='registry': body=body.replace('援军胜利、敌退胜利、失守/投降/死亡/逃跑失败','援军/敌退胜利，投降/死亡/逃跑失败；原表“失守”边界见 [D08]('+to_file(key,'docs/PRD/00-产品总纲/设计决策与待决问题.md','d08')+')，不据本表新增失败阈值')
        if key=='index':
            body+='\n<a id="external-authorities"></a>\n\n## 产品、生产与证据入口\n\n'+ '\n'.join('- ['+label+']('+to_file(key,path)+')' for label,path in [
              ('县城守城 Demo 体验目标与范围','docs/PRD/05-阶段与可玩切片/县城守城Demo/体验目标与范围.md'),
              ('阶段与切片对照表','docs/PRD/05-阶段与可玩切片/阶段与切片对照表.md'),
              ('基础设施与 Owner 建设总计划',prod),('县城守城 Demo 执行计划',demo),
              ('验证与证据规范',validations),('县城守城 Demo 测试用例与证据索引','docs/validation/县城守城Demo/测试用例与证据索引.md')])+'\n'
        if key=='evidence': body+='\n正式证据目录与采集规则见 [验证与证据规范]('+to_file(key,validations)+')；具体 Demo 用例逐项状态见 [测试用例与证据索引]('+to_file(key,'docs/validation/县城守城Demo/测试用例与证据索引.md')+')。\n'
        p.write_text(body,encoding='utf8')

if __name__ == '__main__':
    build_index_registry()
    build_foundations()
    build_domains_models()
    build_runtime_evidence()
    absorb_product_technical_sections()
    finish_routes()
    finalize_links()
    (BACKUP/'migration_architecture.json').write_text(json.dumps({'status':'written_pending_verification','generated_at':'2026-10-30','verification_scope':'documentation_only_no_runtime_validation','entries':ROUTES},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Wrote',len(P),'architecture documents and',len(ROUTES),'leaf migration entries.')
