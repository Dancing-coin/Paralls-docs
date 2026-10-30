from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
BACKUP = ROOT / 'docs/_backups/PRD_20261030_111755'
ORIGINAL = BACKUP / 'original_PRD'
P = 'docs/PRD/'
A = 'docs/architecture/'
DEST = {
    'vision': P+'00-产品总纲/游戏愿景与核心体验.md',
    'roadmap': P+'00-产品总纲/世界扩展路线.md',
    'terms': P+'00-产品总纲/术语表.md',
    'decisions': P+'00-产品总纲/设计决策与待决问题.md',
    'time': P+'01-全局规则/连续世界、时间与暂停.md',
    'identity': P+'01-全局规则/玩家身份、权限与操作入口.md',
    'info': P+'01-全局规则/信息可见性与认知边界.md',
    'movement': P+'02-玩法模块/具身操作、骑乘与视角.md',
    'combat': P+'02-玩法模块/战斗、装备与伤害反馈.md',
    'body': P+'02-玩法模块/角色生存、成长与传承.md',
    'military': P+'02-玩法模块/军制、指挥与自主行动.md',
    'objectives': P+'02-玩法模块/士气、阵型与战场目标.md',
    'resources': P+'02-玩法模块/资源、生产、经济与运输.md',
    'population': P+'02-玩法模块/人口、劳作与聚落运转.md',
    'governance': P+'02-玩法模块/治理、政治与领土控制.md',
    'social': P+'02-玩法模块/社交、关系与情报.md',
    'agents': P+'02-玩法模块/司命与角色智能体体验.md',
    'command': P+'03-跨模块流程/命令传递、执行与指挥权轮替.md',
    'supply': P+'03-跨模块流程/补给、消耗与伤病救治.md',
    'campaign': P+'03-跨模块流程/战役推进与战后结果.md',
    'stages': P+'05-阶段与可玩切片/阶段与切片对照表.md',
    'demo': P+'05-阶段与可玩切片/县城守城Demo/体验目标与范围.md',
    'scope': A+'01-系统边界/01-系统边界与权威写入.md',
    'baseline': A+'01-系统边界/02-现状基线与证据.md',
    'ledgers': A+'01-系统边界/03-三本账与WRK.md',
    'clock': A+'02-公共契约/01-时间身份与控制权.md',
    'contract': A+'02-公共契约/02-Command事件与Receipt.md',
    'owners': A+'03-Owner领域/01-Owner注册表.md',
    'numeric': A+'04-模型与结算/02-数值状态效果与跨Owner结算.md',
    'runtime': A+'05-运行时接入/01-UE本地提交与Paralls同步.md',
    'agenttech': A+'05-运行时接入/02-Agent群体与动画接入.md',
    'evidence': A+'06-存档与可观测性/02-可观测性与验收证据.md',
    'architecture': A+'README.md',
    'art': 'docs/art_resources/standards/角色制作与UE接入标准.md',
    'archive': 'docs/archive/PRD/骑将冲阵垂直切片（已取消独立开发）.md',
    'production': 'docs/production/基础设施与Owner建设总计划.md',
}

# Each entry resolves a substantive heading's own text, not all descendant text.
# Several destinations are intentional when a source section spans responsibilities.
TOTAL = {
  1: [('vision','product-positioning'),('vision','provenance-status'),('runtime','product-technical-boundary')],
  11: [('vision','product-positioning'),('scope','integration-principles')],
  19: [('terms','product-terms')],
  28: [('vision','provenance-status'),('demo','source-demo-goals')],
  36: [('terms','product-terms'),('decisions','d02')],
  47: [('vision','core-experience')],
  55: [('vision','core-experience')],
  66: [('vision','audience-narrative')],
  76: [('vision','reference-games')],
  88: [('vision','product-positioning'),('decisions','d01'),('decisions','d10')],
  104: [('vision','core-experience')],
  108: [('vision','reference-games')],
  114: [('vision','three-loops')],
  149: [('vision','meaningful-decisions')],
  161: [('info','readable-feedback')],
  169: [('identity','operation-entrypoints'),('movement','embodied-movement')],
  173: [('numeric','numeric-settlement')],
  188: [('archive','source-total-metrics'),('vision','experience-validation')],
  204: [('vision','design-pillars')],
  215: [('roadmap','campaign-start-candidates')],
  224: [('time','season-and-cadence')],
  228: [('architecture','technical-reference'),('stages','source-demo-capability-map')],
  240: [('time','continuous-world'),('time','active-pause'),('clock','cadence-contract')],
  246: [('info','three-ledger-semantics'),('info','three-times'),('ledgers','three-ledgers')],
  264: [('time','spatial-continuity')],
  270: [('identity','derived-identity')],
  276: [('identity','permission-sources')],
  285: [('identity','direct-retainers')],
  289: [('identity','command-reachability')],
  302: [('governance','influence-rule')],
  314: [('governance','territory-control')],
  328: [('governance','influence-rule'),('resources','market-actions')],
  334: [('military','autonomy')],
  345: [('military','trained-plans')],
  349: [('command','command-lifecycle'),('contract','military-command-sequence')],
  357: [('objectives','objectives'),('campaign','campaign-flow')],
  363: [('movement','encounter-actions'),('combat','combat-contact')],
  373: [('vision','meaningful-decisions'),('command','command-lifecycle')],
  377: [('objectives','battlefield-state')],
  381: [('military','troop-catalog'),('combat','equipment'),('art','source-modular-character-budget')],
  398: [('objectives','objectives'),('combat','technology-equipment')],
  409: [('combat','technology-equipment'),('resources','technology-economy')],
  426: [('military','troop-catalog'),('roadmap','campaign-start-candidates')],
  432: [('resources','resource-network')],
  452: [('resources','market-actions')],
  465: [('resources','salt-merchant-case'),('supply','supply-flow')],
  471: [('resources','salt-merchant-case'),('governance','territory-control')],
  490: [('body','survival-body')],
  494: [('body','body-social-consequences'),('supply','medical-flow')],
  504: [('body','body-social-consequences'),('social','social-relations')],
  508: [('social','espionage'),('info','legitimate-knowledge')],
  514: [('governance','governance')],
  522: [('governance','governance'),('governance','diplomacy')],
  528: [('resources','resource-network'),('population','population-work')],
  534: [('combat','technology-equipment'),('resources','technology-economy')],
  544: [('body','growth')],
  552: [('body','failure-inheritance'),('decisions','d07')],
  558: [('campaign','war-results'),('roadmap','long-term-acceptance')],
  566: [('agents','siming-candidates')],
  570: [('agents','siming-candidates'),('scope','system-boundaries')],
  576: [('agents','agent-activation'),('agents','population-boundary'),('agenttech','population-continuity')],
  582: [('scope','product-responsibility-matrix'),('baseline','paralls-baseline')],
  596: [('numeric','composite-resolver')],
  604: [('clock','world-cadence-order'),('contract','owner-sequence'),('numeric','cross-owner-transactions')],
  619: [('info','interface-categories')],
  628: [('info','interface-categories')],
  632: [('info','teaching-accessibility'),('time','season-and-cadence')],
  639: [('archive','source-total-riding-slice'),('decisions','d02')],
  645: [('archive','source-total-riding-slice'),('decisions','d03')],
  652: [('archive','source-total-riding-slice'),('decisions','d04')],
  663: [('archive','source-total-riding-slice')],
  667: [('archive','source-total-riding-slice')],
  683: [('archive','source-total-riding-slice'),('vision','experience-validation')],
  695: [('archive','source-total-riding-slice'),('decisions','d05')],
  704: [('archive','source-total-riding-slice')],
  716: [('archive','source-total-milestones'),('decisions','d06')],
  728: [('vision','experience-validation'),('roadmap','long-term-acceptance'),('evidence','acceptance-evidence')],
  743: [('roadmap','long-term-acceptance'),('vision','experience-validation')],
  756: [('scope','architecture-map'),('runtime','product-technical-boundary')],
  762: [('baseline','paralls-reference-index'),('scope','paralls-spine')],
  777: [('vision','source-total-risks')],
  791: [('vision','core-experience'),('vision','design-pillars')],
  797: [('vision','provenance-status')],
}
FIVE = {
  1: [('roadmap','source-status'),('decisions','d01')],
  15: [('roadmap','continuity-roadmap'),('roadmap','county-world'),('production','source-plan-goals-packages')],
  33: [('roadmap','five-stages')],
  47: [('roadmap','county-world')],
  53: [('roadmap','county-world')],
  67: [('roadmap','county-world'),('campaign','campaign-flow')],
  83: [('vision','shared-work-layers'),('identity','derived-identity'),('time','active-pause')],
  94: [('campaign','capability-catalog'),('roadmap','county-world')],
  98: [('campaign','capability-catalog'),('objectives','objectives')],
  108: [('campaign','capability-catalog'),('objectives','objectives'),('decisions','d09')],
  120: [('campaign','capability-catalog'),('social','espionage'),('governance','governance')],
  131: [('population','population-work'),('population','role-transitions'),('military','troop-catalog')],
  171: [('resources','resource-network'),('body','body-social-consequences'),('supply','supply-flow')],
  201: [('scope','five-stage-integration'),('scope','no-authority-bypass')],
  220: [('runtime','five-stage-ue-contract')],
  229: [('agenttech','five-stage-paralls-contract')],
  237: [('scope','no-authority-bypass')],
  241: [('roadmap','technical-continuity'),('scope','five-stage-integration')],
  253: [('roadmap','long-term-acceptance'),('decisions','d09')],
  268: [('roadmap','county-world'),('decisions','d09'),('decisions','d07')],
}

def segments(lines):
    headings=[]
    fence=False
    for i,line in enumerate(lines):
        if line.startswith('```'):
            fence=not fence
        if not fence and re.match(r'^#{1,6} ',line):
            headings.append((i,line))
    out=[]
    for j,(i,heading) in enumerate(headings):
        end=headings[j+1][0] if j+1<len(headings) else len(lines)
        if any(line.strip() and line.strip()!='---' for line in lines[i+1:end]):
            out.append((i+1,end,heading))
    return out

records=[]
coverage=[]
for name,mapping in [('烽火王座：汉末群雄_总策划案_v1.0.md',TOTAL),('国殇：汉末_五阶段战争世界设计大纲_v0.1.md',FIVE)]:
    original=ORIGINAL/name
    lines=original.read_text(encoding='utf-8-sig').splitlines()
    source_segments=segments(lines)
    expected={start for start,end,heading in source_segments}
    assert expected==set(mapping),(name,expected-set(mapping),set(mapping)-expected)
    digest=hashlib.sha256(original.read_bytes()).hexdigest()
    for start,end,heading in source_segments:
        for key,anchor in mapping[start]:
            target=DEST[key]
            path=ROOT/target
            assert path.is_file(),target
            assert f'<a id="{anchor}"></a>' in path.read_text(encoding='utf-8-sig'),(target,anchor)
            disposition='合并保留'
            note='保留原语义并按产品/玩法/技术职责归位；设计描述不作为实现或运行证据。'
            if key in {'scope','baseline','ledgers','clock','contract','owners','numeric','runtime','agenttech','evidence','architecture'}:
                disposition='技术契约或证据迁移'
                note='精确技术定义归唯一architecture权威位置；玩家语义由全局或玩法文档引用，不复制公共契约。'
            if name.startswith('烽火') and (start==188 or 639<=start<=716):
                disposition='历史归档/重定向（取消独立骑将开发与验收）'
                note='独有原文保留在source-total-*历史锚点；三队、10/22/34、3–8分钟、旧阈值与Phase0–4不自动成为当前县城要求。通用能力按县城需要保留。'
            if name.startswith('烽火') and start in {28,36}:
                disposition='范围口径更新，通用状态原则保留'
                note='原文骑战最小实现/第一章限定已被当前县城Demo及23Owner建设路线取代，不继续作为执行门槛。'
            if name.startswith('烽火') and start==797:
                disposition='来源版本保留'
                note='完整原版本表保存在backup_source对应行；provenance-status明确v1.1/v1.2/v1.0源顺序与抬头日期差异，不推断先后或实现状态。'
            if name.startswith('国殇'):
                disposition='设计方向/候选保留，当前Demo范围另维护'
                note='原大纲v0.2为awaiting-user-review；五阶段/职业/资源/地理/灾害目录不自动扩大当前县城交付；已明确的身份、守方、跨日、30世界日分别引用正式配置。'
                if key in {'scope','runtime','agenttech'}:
                    disposition='技术契约迁移'
                    note='统一责任和禁止越权规则迁移到architecture明确锚点；不因UE承载获准Owner Runtime而产生第二权威。'
            records.append({
                'source':'docs/PRD/'+name,
                'source_start':start,'source_end':end,'source_heading':heading,
                'backup_source':'docs/_backups/PRD_20261030_111755/original_PRD/'+name,
                'source_sha256':digest,
                'target':target,'target_anchor':anchor,
                'disposition':disposition,'notes':note,
            })
        coverage.append({'source':name,'start':start,'end':end,'heading':heading,'destinations':len(mapping[start])})

(BACKUP/'migration_product_global.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source_segments':len(coverage),'migration_records':len(records),'by_source':{name:sum(x['source']==name for x in coverage) for name in sorted({x['source'] for x in coverage})},'target_anchors_verified':True},ensure_ascii=False))
