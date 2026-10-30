from pathlib import Path
from collections import Counter, defaultdict
from urllib.parse import unquote, urlsplit
import hashlib, json, os, re, sys

ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
SRC=B/'original_PRD'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(dst,src): return os.path.relpath(ROOT/dst,(ROOT/src).parent).replace('\\','/')
def link(dst,src,label=None,anchor=''): return '['+(label or Path(dst).stem)+']('+rel(dst,src)+(('#'+anchor) if anchor else '')+')'
def slug(s):
 s=re.sub(r'<[^>]*>','',s)
 s=re.sub(r'\[([^\]]+)\]\([^)]*\)',r'\1',s)
 return re.sub(r'[^\w\- ]','',s.replace('`','').lower()).replace(' ','-')
def headings(text):
 out=[];counts=Counter();fence=False
 for n,l in enumerate(text.splitlines(),1):
  if re.match(r'^\s*(```|~~~)',l): fence=not fence;continue
  if fence:continue
  m=re.match(r'^#{1,6}\s+(.+?)\s*#*$',l)
  if m:
   h=m.group(1);s=slug(h);c=counts[s];counts[s]+=1
   out.append((n,h,s+(f'-{c}' if c else '')))
 return out
def anchors(p):
 t=p.read_text(encoding='utf-8-sig')
 return {s for _,_,s in headings(t)}|set(re.findall(r'<a\s+(?:name|id)=[\"\x27]([^\"\x27]+)',t))
def text_links(t):
 # Markdown links within code samples are illustrative, not navigation.
 t=re.sub(r'(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$','',t)
 t=re.sub(r'`[^`\n]+`','',t)
 for m in re.finditer(r'!?\[[^\]\n]*\]\((<[^>]+>|(?:[^()\n]|\([^()\n]*\))+)\)',t):
  x=m.group(1).strip()
  if x.startswith('<') and x.endswith('>'):x=x[1:-1]
  else:x=re.sub(r'\s+[\"\x27].*?[\"\x27]$','',x)
  yield x
 for m in re.finditer(r'(?m)^\s*\[[^\]]+\]:\s*(\S+)',t):yield m.group(1).strip('<>')
def docs():
 active=[ROOT/'AGENTS.md']+sorted(p for p in (ROOT/'docs').rglob('*.md') if '_backups' not in p.relative_to(ROOT/'docs').parts)
 return active+[p for p in [B/'MIGRATION.md',B/'CHECK_RESULTS.md',B/'BACKUP_VERIFIED.md'] if p.exists()]

def migrations():
 result=[]
 for f in sorted(B.glob('migration_*.json')):
  d=json.loads(f.read_text(encoding='utf-8'))
  raw=d if isinstance(d,list) else d.get('entries',d.get('sections',d.get('mappings',[])))
  for x in raw:
   src=x.get('source',x.get('source_path',x.get('original_path')))
   line=x.get('source_lines',x.get('original_lines',{}))
   if isinstance(line,list):a,b=line
   else:a=x.get('source_start',line.get('start'));b=x.get('source_end',line.get('end'))
   target=x.get('target_path',x.get('target',''))
   target,sep,fragment=target.partition('#')
   anchor=x.get('target_anchor',fragment)
   if not src or a is None or b is None:raise ValueError((f.name,x))
   result.append({'source':src,'start':a,'end':b,'heading':x.get('source_heading',x.get('original_section','')),'target':target,'anchor':anchor,'disposition':x.get('disposition',x.get('treatment','保留/合并')),'note':x.get('note',x.get('notes','')),'mapping_file':f.name})
 return result

def coverage(entries):
 out=[]
 for p in sorted(SRC.rglob('*')):
  if not p.is_file():continue
  src='docs/PRD/'+p.relative_to(SRC).as_posix()
  lines=p.read_text(encoding='utf-8-sig').splitlines();maps=[x for x in entries if x['source']==src]
  covered=set(i for x in maps for i in range(x['start'],x['end']+1))
  missing=[i for i,l in enumerate(lines,1) if l.strip() and i not in covered]
  missing_heads=[(n,h) for n,h,s in headings('\n'.join(lines)) if n not in covered]
  out.append({'source':src,'lines':len(lines),'nonempty_lines':sum(bool(x.strip()) for x in lines),'mapped_nonempty_lines':sum(bool(x.strip()) and i in covered for i,x in enumerate(lines,1)),'missing_lines':missing,'missing_headings':missing_heads,'mappings':len(maps)})
 return out

def write_migration(entries):
 (B/'MIGRATION.json').write_text(json.dumps({'schema_version':1,'date':'2026-10-30','meaning':'记录原章节去向；不证明运行实现','entries':entries,'coverage':coverage(entries)},ensure_ascii=False,indent=2),encoding='utf-8')
 s='# PRD 文档迁移对照\n\n- 日期：2026-10-30\n- 原始来源：original_PRD（20份原始字节副本）\n- 状态：文档重组记录；并非运行验收。正式/合并/待决/历史均给出明确去向。元信息和旧修订史可只保留于不可变备份，不成为第二份活跃规则。\n- 机器记录：[MIGRATION.json](MIGRATION.json)；检查：[CHECK_RESULTS.md](CHECK_RESULTS.md)。\n\n'
 for src in sorted({x['source'] for x in entries}):
  source=SRC/Path(src).relative_to('docs/PRD') if src.startswith('docs/PRD/') else B/'additional_originals'/src
  ls=source.read_text(encoding='utf-8-sig').splitlines()
  s+='## '+Path(src).name+'\n\n原始副本：'+link(source.relative_to(ROOT).as_posix(),(B/'MIGRATION.md').relative_to(ROOT).as_posix())+'。\n\n|原章节/行范围|新维护位置|处理|\n|---|---|---|\n'
  for x in sorted((x for x in entries if x['source']==src),key=lambda x:(x['start'],x['end'])):
   label=x['heading'] or next((l.lstrip('# ') for l in ls[x['start']-1:x['end']] if l.startswith('#')),'段落/元信息')
   label=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',label)
   target=link(x['target'],(B/'MIGRATION.md').relative_to(ROOT).as_posix(),anchor=x['anchor'])
   s+='|'+label.replace('|','\\|')+f'（L{x["start"]}–{x["end"]}）|'+target+'|'+str(x['disposition']).replace('|','\\|')+'|\n'
  s+='\n'
 (B/'MIGRATION.md').write_text(s,encoding='utf-8')

def stubs(entries):
 originals={('docs/PRD/'+p.relative_to(SRC).as_posix()):p for p in SRC.rglob('*.md') if p.name!='README.md' or p.parent!=SRC}
 refs=defaultdict(set)
 for p in docs():
  for url in text_links(p.read_text(encoding='utf-8-sig')):
   raw,_,frag=unquote(url).partition('#')
   if not raw or re.match(r'^[a-zA-Z][\w+.-]*:',raw):continue
   target=(p.parent/raw).resolve()
   if target.is_relative_to(ROOT):
    key=target.relative_to(ROOT).as_posix()
    if key in originals and frag:refs[key].add(frag)
 for src,old in originals.items():
  maps=[x for x in entries if x['source']==src]
  unique=[]
  for x in maps:
   if x['target'] not in unique:unique.append(x['target'])
  if not unique:raise ValueError('No route: '+src)
  s='# 文档已按职责迁移\n\n- 更新日期：2026-10-30\n- 版本：1.0（旧路径兼容指引）\n- 评审状态：导航；不新增产品决策\n- 实现状态：本页不证明实现\n\n此旧路径仅保留兼容引用，不再维护原正文。当前目标为县城守城 Demo；骑将冲阵独立开发/验收已取消。\n\n'
  for target in unique:s+='- '+link(target,src)+'\n'
  s+='\n原文和逐章节去向见'+link((B/'MIGRATION.md').relative_to(ROOT).as_posix(),src,'本次迁移对照')+'；原始完整副本见'+link(old.relative_to(ROOT).as_posix(),src,'只读历史备份')+'。\n'
  oldheads={a:(n,h) for n,h,a in headings(old.read_text(encoding='utf-8-sig'))}
  if refs[src]:
   s+='\n## 旧章节锚点兼容\n\n'
   for anchor in sorted(refs[src]):
    n,h=oldheads.get(anchor,(0,anchor))
    candidates=[x for x in maps if x['start']<=n<=x['end']]
    if not candidates:candidates=maps
    x=min(candidates,key=lambda x:x['end']-x['start'])
    s+=f'<a id="{anchor}"></a>\n\n'+h+' → '+link(x['target'],src,anchor=x['anchor'])+'。\n\n'
  (ROOT/src).write_text(s,encoding='utf-8')

def verify(entries):
 errors=[];link_count=0;anchor_count=0;mds=docs();decoded=0;unclosed=[]
 cache={}
 for p in mds:
  try:t=p.read_text(encoding='utf-8-sig');decoded+=1
  except UnicodeError as e:errors.append({'file':p.relative_to(ROOT).as_posix(),'error':str(e)});continue
  fence=None
  for n,l in enumerate(t.splitlines(),1):
   m=re.match(r'^\s{0,3}(`{3,}|~{3,})',l)
   if m:
    if fence is None:fence=(m.group(1)[0],len(m.group(1)),n)
    elif m.group(1)[0]==fence[0] and len(m.group(1))>=fence[1]:fence=None
  if fence:unclosed.append({'file':p.relative_to(ROOT).as_posix(),'line':fence[2]})
  for url in text_links(t):
   url=unquote(url)
   if re.match(r'^[a-zA-Z][\w+.-]*:',url) or url.startswith('//'):continue
   path,_,fragment=url.partition('#')
   if path.startswith('/Game/'):continue
   dest=(p.parent/path).resolve() if path else p.resolve();link_count+=1
   if not dest.exists():errors.append({'file':p.relative_to(ROOT).as_posix(),'url':url,'error':'missing_path'});continue
   if fragment and dest.is_file() and dest.suffix.lower()=='.md':
    anchor_count+=1
    if dest not in cache:cache[dest]=anchors(dest)
    if fragment not in cache[dest]:errors.append({'file':p.relative_to(ROOT).as_posix(),'url':url,'error':'missing_anchor'})
 cov=coverage(entries)
 map_errors=[]
 for x in entries:
  dest=ROOT/x['target']
  if not dest.exists():map_errors.append({'target':x['target'],'error':'missing_path'})
  elif x['anchor'] and x['anchor'] not in anchors(dest):map_errors.append({'target':x['target'],'anchor':x['anchor'],'error':'missing_anchor'})
 original_manifest=json.loads((B/'backup_manifest.json').read_text(encoding='utf-8'))
 original_rows=original_manifest if isinstance(original_manifest,list) else original_manifest.get('files',original_manifest.get('entries',[]))
 backup_errors=[]
 for x in original_rows:
  path=x.get('backup_path',x.get('backup_relative_path',''))
  p=B/path if path else SRC/Path(x.get('original_path',x.get('path'))).relative_to('docs/PRD')
  if not p.exists() or p.stat().st_size!=x.get('bytes',x.get('size')) or sha(p)!=x['sha256']:backup_errors.append(str(p))
 additional=json.loads((B/'additional_manifest.json').read_text(encoding='utf-8'))
 for x in additional:
  p=B/x['backup_path']
  if not p.exists() or p.stat().st_size!=x['bytes'] or sha(p)!=x['sha256']:backup_errors.append(str(p))
 before=json.loads((B/'art_resources_before.json').read_text(encoding='utf-8'))
 before_rows=before if isinstance(before,list) else before.get('files',before.get('entries',[]))
 allowed={x['original_path'] for x in additional}
 art_errors=[];observed_differences=[];unchanged=0;intended_changes=[];manifest_count=0;manifest_errors=[]
 for x in before_rows:
  path=x.get('path',x.get('relative_path',x.get('original_path','')))
  p=ROOT/path
  if not p.exists():art_errors.append({'path':path,'error':'removed'});continue
  if 'manifest' in p.name.lower() or 'manifests' in p.relative_to(ROOT).parts:
   manifest_count+=1
   if (x.get('sha256') and sha(p)!=x['sha256']) or p.stat().st_size!=x.get('bytes',x.get('size')):manifest_errors.append(path)
  if path in allowed:
   intended_changes.append(path)
   continue
  size=x.get('bytes',x.get('size'))
  if size is not None and p.stat().st_size!=size:observed_differences.append({'path':path,'difference':'size_changed','before_bytes':size,'current_bytes':p.stat().st_size,'handling':'本次整理未编辑；保留当前文件，未恢复或覆盖'})
  elif x.get('sha256') and sha(p)!=x['sha256']:observed_differences.append({'path':path,'difference':'hash_changed','handling':'本次整理未编辑；保留当前文件，未恢复或覆盖'})
  else:unchanged+=1
 result={'date':'2026-10-30','documentation_only':True,'markdown_files':len(mds),'utf8_decoded':decoded,'local_links_checked':link_count,'local_anchors_checked':anchor_count,'link_errors':errors,'unclosed_fences':unclosed,'migration_entries':len(entries),'migration_target_errors':map_errors,'coverage':cov,'backup_files_checked':len(original_rows),'additional_backups_checked':len(additional),'backup_errors':backup_errors,'original_backup_files':len([p for p in SRC.rglob('*') if p.is_file()]),'original_backup_bytes':sum(p.stat().st_size for p in SRC.rglob('*') if p.is_file()),'art_existing_files_checked':len(before_rows),'art_unchanged_unmodified_files':unchanged,'art_intentionally_edited_indices':intended_changes,'art_observed_unowned_differences':observed_differences,'art_existing_manifests_checked':manifest_count,'art_manifest_errors':manifest_errors,'art_errors':art_errors}
 baseline_paths={x.get('path',x.get('relative_path',x.get('original_path',''))) for x in before_rows}
 current_yaml=list((ROOT/'docs/art_resources/manifests').rglob('*.yaml'))
 result.update({'art_original_yaml_manifests_checked':sum('/manifests/' in p and p.endswith('.yaml') for p in baseline_paths),'art_current_yaml_manifests':len(current_yaml),'art_manifests_added_outside_baseline':[p.relative_to(ROOT).as_posix() for p in sorted(current_yaml) if p.relative_to(ROOT).as_posix() not in baseline_paths]})
 (B/'CHECK_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in result.items() if k not in ['coverage','link_errors','migration_target_errors']},ensure_ascii=False))
 print('LINK_ERRORS',json.dumps(errors,ensure_ascii=False))
 print('MAPPING_ERRORS',json.dumps(map_errors,ensure_ascii=False))
 print('COVERAGE_GAPS',json.dumps([x for x in cov if x['missing_lines']],ensure_ascii=False))
 return result

if __name__=='__main__':
 entries=migrations()
 if '--stubs' in sys.argv:stubs(entries)
 if '--migration' in sys.argv:write_migration(entries)
 result=verify(entries)
 failures=sum(len(result[k]) for k in ['link_errors','unclosed_fences','migration_target_errors','backup_errors','art_errors','art_manifest_errors'])
 failures+=sum(bool(x['missing_lines'] or x['missing_headings']) for x in result['coverage'])
 sys.exit(1 if failures else 0)
