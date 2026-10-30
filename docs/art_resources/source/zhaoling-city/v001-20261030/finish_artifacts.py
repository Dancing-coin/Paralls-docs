from pathlib import Path
import json,hashlib,yaml
from PIL import Image,ImageDraw,ImageFont
art=Path('docs/art_resources')
v='v001-20261030'
src=art/'source/zhaoling-city'/v
out=art/'staging/zhaoling-city'/v
ev=art/'evidence/zhaoling-city'/v
paper='#F3EFE5'; ink='#2D4039'; muted='#696D62'
def ft(n): return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
files=[]
for kind,title in [('plan','召陵｜县城平面推演图'),('concept','召陵｜城邑概念图')]:
    raw=src/f'{kind}-generated.jpg'
    im=Image.open(raw).convert('RGB'); w,h=im.size
    head=100; foot=178 if kind=='plan' else 115
    frame=Image.new('RGB',(w,h+head+foot),paper); frame.paste(im,(0,head))
    d=ImageDraw.Draw(frame)
    d.text((28,14),title,font=ft(32),fill=ink)
    d.text((30,61),'东汉背景 · 美术推演 · 非考古测绘或确证复原',font=ft(18),fill=muted)
    if kind=='plan':
        d.text((w-84,22),'北 ↑',font=ft(25),fill=ink)
        points=[(255,205),(382,170),(365,290),(600,450),(790,560),(945,668)]
        for n,(x,y) in enumerate(points,1):
            y+=head
            d.ellipse((x-17,y-17,x+17,y+17),fill=paper,outline=ink,width=2)
            d.text((x,y-1),str(n),font=ft(21),fill=ink,anchor='mm')
        labels=['1 县署院落（推演）','2 仓储院落（推演）','3 内城空场（推演）','4 街市（推演）','5 民居（推演）','6 园圃（推演）']
        for i,label in enumerate(labels):
            d.text((30+(i%3)*(w//3),head+h+14+(i//3)*34),label,font=ft(20),fill=ink)
        y=head+h+94
    else:
        y=head+h+16
    d.text((30,y),'依据：CHGIS 引述《中国文物地图集·河南分册》：内外二城、内城在西北；分期未核。',font=ft(17),fill=muted)
    d.text((30,y+29),'城门、街道、建筑及壕沟均为推演；图不具实测比例。模型：Gemini Pro Image Preview',font=ft(17),fill=muted)
    dest=out/f'zhaoling-{kind}.png';frame.save(dest,optimize=True)
    files.append({'kind':kind,'path':dest.relative_to(art).as_posix(),'dimensions':list(frame.size),'size_bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
report={'outputs':files,'model':'gemini-3-pro-image-preview','originals_retained':True,'historical_status':'hypothetical; not archaeologically verified','image_consistency':'same text layout brief; not exact building-for-building correspondence','ue_launched':False,'ue_asset_changes':0,'actor_changes':0,'pie':'not started'}
(ev/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
def record(p):return {'path':p.relative_to(art).as_posix(),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
manifest={'schema_version':'1.0','asset':{'asset_id':'zhaoling-city','version':v,'asset_type':'concept_art','tier':'other','description':'东汉召陵县城平面推演图、城邑鸟瞰概念图'},'source':{'source_kind':'AI_generated','source_url':'https://www.aiartmirror.com/v1/images/generations','historical_reference':'https://chgis.hudci.org/tgaz/placename/hvd_83032','license':'网关AI输出许可待核；CHGIS参考记录CC BY-NC 4.0','authorization_status':'research_candidate','download_date':'2026-10-30','files':[record(p) for p in sorted(src.iterdir()) if p.is_file()]},'exports':{'files':files,'ue_paths':[]},'technical':{'geometry':{'triangles':0,'vertices':0,'nanite':False},'textures':{'resolutions':['x'.join(map(str,f['dimensions'])) for f in files],'usage':'概念讨论；未导入UE'}},'status':{'lifecycle':'候选','owner':'','approver':'','updated_at':'2026-10-30','reason':'有史料约束的美术推演；城内布局及分期未核，商业授权待核'},'verification':{'historical':{'status':'partial_reference_only','evidence':f'source/zhaoling-city/{v}/设计与史料说明.md'},'visual':{'status':'review_required','evidence':f'evidence/zhaoling-city/{v}/validation.json'}},'evidence':{'generation_model':'gemini-3-pro-image-preview','generation_logs':[f'evidence/zhaoling-city/{v}/generation-{k}.json' for k in ['plan','concept']],'ue_import_log':None,'editor_screenshot':None,'pie_screenshot_or_video':None},'lineage':{'parent_version':None,'rollback_target':None,'supersedes':[]},'storage':{'source_path':f'source/zhaoling-city/{v}/','staging_path':f'staging/zhaoling-city/{v}/','approved_path':None,'evidence_path':f'evidence/zhaoling-city/{v}/','manifest_path':f'manifests/zhaoling-city/{v}.yaml'}}
mp=art/'manifests/zhaoling-city'/f'{v}.yaml'
mp.write_text(yaml.safe_dump(manifest,allow_unicode=True,sort_keys=False),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
