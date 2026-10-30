from pathlib import Path
import re, json, runpy, hashlib

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).parent
NS=runpy.run_path(str(BASE/'build_architecture.py'),run_name='inspect')
OUT=ROOT/'docs/architecture'
FILES=sorted(OUT.rglob('*.md'))
MIGRATION=BASE/'migration_architecture.json'
data=json.loads(MIGRATION.read_text(encoding='utf8'))
issues=[]

def ids(text):
    values=set(re.findall(r'<a id="([^"]+)"',text))
    for line in text.splitlines():
        m=re.match(r'^#{1,6}\s+(.+)',line)
        if m:
            value=re.sub(r'[^\w\-\s\u4e00-\u9fff]','',m.group(1).strip().lower())
            values.add(re.sub(r'\s','-',value))
    return values

texts={p:p.read_text(encoding='utf8') for p in FILES}
for p,text in texts.items():
    explicit=re.findall(r'<a id="([^"]+)"',text)
    if len(explicit)!=len(set(explicit)):issues.append(f'duplicate anchor: {p}')
    if text.count('```')%2:issues.append(f'unbalanced code fence: {p}')
    for field in ['版本：1.0（职责拆分版）','更新日期：2026-10-30','评审状态：','实现状态：','未执行代码、UE、PIE 或性能验证']:
        if field not in text:issues.append(f'missing metadata {field}: {p}')
    for label,url in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',text):
        if re.match(r'^(https?:|mailto:)',url):continue
        path,_,fragment=url.partition('#')
        target=(p.parent/path).resolve() if path else p
        if not target.is_file():issues.append(f'missing target: {p}: {url}')
        elif fragment and fragment not in ids(target.read_text(encoding='utf8')):issues.append(f'missing anchor: {p}: {url}')
    if re.search(r'第\s*\d+(?:\.\d+)*\s*节',text):issues.append(f'stale numbered section: {p}')

for entry in data['entries']:
    target=ROOT/entry['target_path']
    if not target.is_file() or entry['target_anchor'] not in ids(target.read_text(encoding='utf8')):
        issues.append(f'migration target invalid: {entry["target"]}')

coverage={}
for key in ['a','b','c','d','e','f','g','h']:
    source='docs/PRD/玩法系统/'+NS['S'][key]
    covered=set()
    for entry in data['entries']:
        if entry['source_path']==source:covered.update(range(entry['source_lines']['start'],entry['source_lines']['end']+1))
    missing=[i for i,line in enumerate(NS['LINES'][key],1) if line.strip() and i not in covered]
    coverage[source]={'source_lines':len(NS['LINES'][key]),'uncovered_nonblank_lines':missing}
    if missing:issues.append(f'uncovered source: {source}: {missing}')

registry=texts[OUT/NS['P']['registry']]
runtime=texts[OUT/NS['P']['ue']]
roster_count=len(re.findall(r'^\|\s*\d{1,2}\s*\|',registry,re.M))
cadence_count=len(re.findall(r'^\|\s*\d{1,2}\s*\|',runtime,re.M))
if roster_count!=23:issues.append(f'Owner registry row count {roster_count}')
if cadence_count!=23:issues.append(f'UE cadence matrix row count {cadence_count}')
for p,text in texts.items():
    if p not in [OUT/NS['P']['registry'],OUT/NS['P']['ue']] and len(re.findall(r'^\|\s*\d{1,2}\s*\|',text,re.M))==23:
        issues.append(f'duplicate 23 row table: {p}')
    if '| Domain Owner | Presence、Dispatch、Organization' in text:issues.append(f'duplicate inline complete roster: {p}')

# Exact fenced payload preservation catches omitted schemas, formulas and diagrams.
# Each copied payload must survive somewhere in the mapped formal document.
payload_count=0
seen=set()
for entry in data['entries']:
    if entry['disposition']!='moved':continue
    source=entry['source_path']
    key=next((k for k,v in NS['S'].items() if (v if v.startswith('docs/') else 'docs/PRD/玩法系统/'+v)==source),None)
    if not key:continue
    lo=entry['source_lines']['start'];hi=entry['source_lines']['end']
    snippet='\n'.join(NS['LINES'][key][lo-1:hi])
    for block in re.findall(r'```[^\n]*\n(.*?)\n```',snippet,re.S):
        token=(entry['target_path'],block)
        if token in seen:continue
        seen.add(token);payload_count+=1
        if block not in (ROOT/entry['target_path']).read_text(encoding='utf8'):issues.append(f'changed fenced schema/formula/diagram {source}:{lo}-{hi}')

required={
 'registry':['authority_scope','authority_epoch','owner_id','commit_store','execution_host'],
 'command':['read_set_revisions','known_time_by_recipient','next_action / recovery_action','rejected / requeued / partial / cancelled / expired / superseded'],
 'models':['Model Definition','Applicability Binding','Evaluation Context','unknown','seed'],
 'handoff':['effect_id + scheduled_world_tick','treatment_id + step','LifeState revision','authority_epoch'],
 'agent':['started','progress','completed','interrupted','failed','TTL'],
 'ue':['canonical','outbox','pending/predicted','模型/Binding/Static Data'],
}
for key,terms in required.items():
    for term in terms:
        if term not in texts[OUT/NS['P'][key]]:issues.append(f'missing critical term {key}: {term}')

# Check incoming formal architecture references from other newly split areas.
incoming=0
for p in (ROOT/'docs').rglob('*.md'):
    if '_backups' in p.parts or p in texts:continue
    text=p.read_text(encoding='utf-8-sig')
    for url in re.findall(r'\]\(([^)]+)\)',text):
        path,_,fragment=url.partition('#')
        if 'architecture/' not in path.replace('\\','/'):continue
        target=(p.parent/path).resolve();incoming+=1
        if not target.is_file():issues.append(f'incoming architecture target missing: {p}: {url}')
        elif fragment and fragment not in ids(target.read_text(encoding='utf8')):issues.append(f'incoming architecture anchor missing: {p}: {url}')

result={'status':'passed' if not issues else 'failed','scope':'documentation_static_only_no_code_UE_PIE_or_performance_execution','document_count':len(FILES),'line_count':sum(len(t.splitlines()) for t in texts.values()),'migration_entry_count':len(data['entries']),'owner_registry_rows':roster_count,'ue_cadence_rows':cadence_count,'exact_fenced_payloads_verified':payload_count,'incoming_architecture_links_checked':incoming,'coverage':coverage,'issues':issues}
(BASE/'verification_architecture.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
if not issues:
    data['status']='complete'
    data['verification']=result
    data['source_snapshot']='docs/_backups/PRD_20261030_111755/original_PRD'
    data['source_sha256']={source:hashlib.sha256((BASE/'original_PRD'/Path(source).relative_to('docs/PRD')).read_bytes()).hexdigest() for source in coverage}
    MIGRATION.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='coverage'},ensure_ascii=False,indent=2))
raise SystemExit(0 if not issues else 1)
