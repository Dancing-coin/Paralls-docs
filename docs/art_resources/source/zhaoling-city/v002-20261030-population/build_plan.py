"""Reproducible scenario plan, in metres; roof counts are design quantities."""
from pathlib import Path
from collections import Counter
import json
import math
import random
from PIL import Image, ImageDraw, ImageFont
from shapely import affinity
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import unary_union, voronoi_diagram

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2]
STAGE = ART / 'staging/zhaoling-city' / HERE.name
EVIDENCE = ART / 'evidence/zhaoling-city' / HERE.name
for p in (STAGE, EVIDENCE):
    p.mkdir(parents=True, exist_ok=True)
RNG = random.Random(20261030)
SCALE, OX, OY = 2.4, 220, 370
W, H = 5100, 4400
FONT = 'C:/Windows/Fonts/msyh.ttc'
INK, PAPER = '#353d39', '#f0ecdf'
im = Image.new('RGB', (W, H), PAPER)
d = ImageDraw.Draw(im)

def xy(p):
    return (round(OX + p[0] * SCALE), round(OY + p[1] * SCALE))

def polys(g):
    if g.is_empty:
        return []
    if g.geom_type == 'Polygon':
        return [g]
    return [p for part in getattr(g, 'geoms', []) for p in polys(part)]

def paint(g, fill, outline=None, width=1):
    for p in polys(g):
        pts = [xy(v) for v in p.exterior.coords]
        if p.interiors:
            x0,y0,x1,y1 = p.bounds
            left,top = xy((x0,y0));right,bottom = xy((x1,y1))
            mask = Image.new('L',(right-left+1,bottom-top+1),0)
            md = ImageDraw.Draw(mask)
            md.polygon([(x-left,y-top) for x,y in pts],fill=255)
            for ring in p.interiors:
                md.polygon([(xy(v)[0]-left,xy(v)[1]-top) for v in ring.coords],fill=0)
            im.paste(fill,(left,top,right+1,bottom+1),mask)
        else:
            d.polygon(pts, fill=fill)
        if outline:
            d.line(pts, fill=outline, width=width, joint='curve')
            for ring in p.interiors:
                d.line([xy(v) for v in ring.coords],fill=outline,width=width,joint='curve')

def line(points, fill, width):
    d.line([xy(p) for p in points], fill=fill, width=max(1, round(width*SCALE)), joint='curve')

def text(pos, value, size=30, fill=INK, anchor=None):
    d.text(pos, value, font=ImageFont.truetype(FONT, size), fill=fill, anchor=anchor)

def label(p, value, size=29, color=INK):
    pos = xy(p)
    f = ImageFont.truetype(FONT, size)
    b = d.textbbox(pos, value, font=f, anchor='mm')
    d.rounded_rectangle((b[0]-9,b[1]-5,b[2]+9,b[3]+5), radius=7, fill=PAPER)
    d.text(pos, value, font=f, fill=color, anchor='mm')

roads = [
    ('南北驿路', 12, [(960,1510),(945,1360),(910,1220),(890,1040),(760,900),(770,690),(660,570),(635,400),(620,270),(620,-10)]),
    ('东西市街', 10, [(-10,860),(230,845),(420,780),(600,800),(760,900),(970,800),(1160,650),(1320,580),(1510,560)]),
    ('北部横街', 8, [(55,420),(250,425),(420,460),(635,400),(850,420),(1020,380),(1220,340),(1445,345)]),
    ('南部横街', 8, [(55,1160),(280,1110),(460,1080),(630,1100),(890,1040),(1120,1150),(1445,1190)]),
    ('西部纵街', 7, [(300,425),(310,650),(420,780),(460,1080),(500,1445)]),
    ('东部粮道', 8, [(1030,55),(1020,380),(1040,560),(970,800),(1120,1150),(1170,1445)]),
    ('县署联络街', 7, [(275,350),(280,425),(420,460)]),
    ('东北联络街', 7, [(1445,240),(1260,270),(1020,380)]),
    ('西北支街', 6, [(55,240),(80,240)]),
    ('东南支街', 6, [(1120,1150),(1220,1070),(1445,1070)]),
    ('仓廪支路', 8, [(1027,155),(1110,155)]),
    ('营舍支路', 7, [(1032,485),(1080,485)]),
    ('作坊支路', 6, [(1310,1174),(1310,1220)]),
    ('传舍支路', 6, [(1125,1390),(1161,1390)]),
    ('内城署前路', 6, [(235,292),(235,320),(275,320),(275,350)]),
    ('内城西门路', 5, [(80,240),(90,240),(90,320),(235,320)]),
    ('医舍支巷', 4, [(565,797),(565,820)]),
    ('社祠支巷', 4, [(195,810),(195,847)]),
]
ring = LineString([(43,43),(1457,43),(1457,1457),(43,1457),(43,43)])
road_geom = unary_union([LineString(r[2]).buffer(r[1]/2+2) for r in roads] + [ring.buffer(6)])
city = box(0,0,1500,1500)
inner = box(80,80,400,350)
zones = {
    '县署': (box(165,145,285,285), '#d4b68c'),
    '狱舍': (box(95,190,137,280), '#c3b2a0'),
    '文书吏舍': (box(333,130,385,245), '#d4b68c'),
    '仓廪': (box(1110,70,1390,230), '#d8c389'),
    '驻防营舍': (box(1080,430,1400,540), '#c1b49b'),
    '市肆': (box(795,685,955,815), '#d2ae91'),
    '作坊': (box(1210,1220,1415,1400), '#cda997'),
    '传舍': (box(1030,1350,1130,1430), '#c8b295'),
    '医舍': (box(535,820,600,880), '#bfd0b6'),
    '社祠': (box(160,750,230,810), '#c3c9a6'),
    '候见听讼场': (box(170,292,225,318), '#d0c3a5'),
    '官属舍': (box(300,270,385,340), '#c6b89d'),
    '县学礼仪院': (box(95,95,215,125), '#c4c9ad'),
    '武库': (box(300,95,385,125), '#b9b29f'),
    '内仓': (box(230,95,290,125), '#d2c18e'),
}
canal = LineString([(1490,950),(1280,965),(1150,1000),(1000,1120),(700,1180),(430,1250),(10,1280)])
pond = Point(540,1245).buffer(55).union(Point(1140,1040).buffer(40))
water = canal.buffer(5).union(pond)
gardens = unary_union([box(65,1370,210,1440),box(690,65,790,165),box(1360,720,1435,825),box(85,1010,175,1090)])
reserved = unary_union([inner]+[g[0].buffer(9) for g in zones.values()]+[water.buffer(10),gardens])
res_area = box(65,65,1435,1435).difference(reserved.union(road_geom))

# The 18 ward identifiers retain the project's data grouping, not a claimed Han census.
seeds = [(215,470),(510,210),(835,220),(1230,180),(150,650),(480,610),
         (840,570),(1260,475),(230,950),(610,945),(1050,875),(1330,860),
         (240,1290),(550,1330),(780,1300),(1020,1280),(1310,1320),(1280,1080)]
from shapely.geometry import MultiPoint
cells = list(voronoi_diagram(MultiPoint(seeds), envelope=box(0,0,1500,1500)).geoms)
wards = []
lots = []
for wid, seed in enumerate(seeds,1):
    cell = next(c for c in cells if c.covers(Point(seed)))
    area = cell.buffer(-2).intersection(res_area)
    angle = [-5,0,4,-2,6,0,-4,3,0,5,-3,2,0,-5,3,0,5,-2][wid-1]
    local = affinity.rotate(area,-angle,origin=seed)
    minx,miny,maxx,maxy = local.bounds
    candidates = []
    # 16 x 20 m scenario parcel; 2/6 m row gaps and 4/8 m cross lanes.
    yy = math.floor(miny/50)*50
    row = 0
    while yy+20 < maxy:
        xx = math.floor(minx/20)*20
        col = 0
        while xx+16 < maxx:
            lot = box(xx,yy,xx+16,yy+20)
            world = affinity.rotate(lot,angle,origin=seed)
            if area.covers(world):
                candidates.append({'ward':wid,'x':xx,'y':yy,'angle':angle,'origin':seed,
                                   'parcel':world,'score':world.centroid.distance(Point(seed))+RNG.uniform(0,25)})
            col += 1
            xx += 20 + (4 if col%7==0 else 0)
        yy += 22 if row%2==0 else 26
        row += 1
    candidates.sort(key=lambda c:c['score'])
    wards.append({'id':wid,'seed':seed,'geometry':area,'candidates':candidates})

capacity = sum(len(w['candidates']) for w in wards)
assert capacity >= 2000, f'Only {capacity} candidate plots; revise geometry before drawing.'
quotas = [math.floor(2000*len(w['candidates'])/capacity) for w in wards]
for k in sorted(range(18),key=lambda k:2000*len(wards[k]['candidates'])/capacity-quotas[k],reverse=True)[:2000-sum(quotas)]:
    quotas[k]+=1
for w,n in zip(wards,quotas):
    w['households'] = n
    lots.extend(w['candidates'][:n])
assert len(lots)==2000

# Landscape and infrastructure, true orthographic plan.
paint(city.buffer(32).difference(city.buffer(17)), '#9dbbb8')
paint(city, '#e2dfcc')
paint(res_area, '#e8e2d1')
paint(gardens, '#c6cfac')
paint(water, '#9dbbb8', '#759c9a', 2)
paint(road_geom, '#c9b99c')
paint(inner, '#ddd4b9', '#8a7a61', 5)
inner_paths = unary_union([LineString(pts).buffer(width/2) for name,width,pts in roads if name.startswith('内城')])
paint(inner_paths, '#c9b99c')
paint(box(267,344,283,354), '#c9b99c')
paint(box(76,232,84,248), '#c9b99c')
for name,(g,color) in zones.items():
    paint(g,color,'#9d8d73',2)

buildings = []
def roof(g,kind,ward=None):
    buildings.append({'id':f'B{len(buildings)+1:05d}','kind':kind,'ward':ward,
                      'footprint_m2':round(g.area,2),'polygon_m':[[round(x,3),round(y,3)] for x,y in g.exterior.coords]})
    palette = {'住宅正屋':('#747e7a','#414e4c'),'住宅附屋':('#929789','#697265'),
               '仓廪':('#9d835e','#6b5a43'),'市肆':('#a27d62','#705845'),
               '作坊':('#927768','#68594d')}
    fill,edge=palette.get(kind,('#8d8070','#5b554c'))
    paint(g,fill,edge,1)
    p=g.minimum_rotated_rectangle
    cs=list(p.exterior.coords)
    lengths=[Point(cs[j]).distance(Point(cs[j+1])) for j in range(4)]
    j=lengths.index(max(lengths))
    a=((cs[j][0]+cs[(j+3)%4][0])/2,(cs[j][1]+cs[(j+3)%4][1])/2)
    b=((cs[(j+1)%4][0]+cs[(j+2)%4][0])/2,(cs[(j+1)%4][1]+cs[(j+2)%4][1])/2)
    line([a,b],edge,0.65)

for lot in lots:
    x,y=lot['x'],lot['y'];a=lot['angle'];origin=lot['origin']
    paint(lot['parcel'], '#e6dfce','#b9b29b',1)
    main=affinity.rotate(box(x+2,y+2,x+14,y+9),a,origin=origin)
    annex=affinity.rotate(box(x+2,y+12,x+6,y+18),a,origin=origin)
    roof(main,'住宅正屋',lot['ward']);roof(annex,'住宅附屋',lot['ward'])

def array_roofs(g,kind,n,cols,rw,rh,pad=7):
    x0,y0,x1,y1=g.bounds;rows=math.ceil(n/cols)
    dx=(x1-x0-2*pad)/cols;dy=(y1-y0-2*pad)/rows
    assert rw<dx and rh<dy, (kind,dx,dy)
    for k in range(n):
        x=x0+pad+(k%cols+.5)*dx;y=y0+pad+(k//cols+.5)*dy
        roof(box(x-rw/2,y-rh/2,x+rw/2,y+rh/2),kind)

# County office: three modest successive courts, side offices, no imperial palace.
office=zones['县署'][0]
for y in (163,205,247):
    roof(box(195,y-6,255,y+6),'县署')
for x in (173,267):
    for y in (155,179,203,227,251):
        roof(box(x,y,x+12,y+14),'县署')
for x,y in [(188,147),(245,147),(174,270),(194,270),(214,270),(234,270),(254,270)]:
    roof(box(x,y,x+16,y+8),'县署')
array_roofs(zones['狱舍'][0],'狱舍',4,2,12,22,4)
array_roofs(zones['文书吏舍'][0],'文书吏舍',4,2,15,26,4)
array_roofs(zones['仓廪'][0],'仓廪',24,6,28,19,14)
array_roofs(zones['驻防营舍'][0],'营舍',16,8,25,18,9)
array_roofs(zones['市肆'][0],'市肆',96,12,8,6,7)
array_roofs(zones['作坊'][0],'作坊',48,8,16,13,12)
array_roofs(zones['传舍'][0],'传舍',6,3,20,18,8)
array_roofs(zones['医舍'][0],'医舍',4,2,17,15,6)
array_roofs(zones['社祠'][0],'社祠',4,2,19,14,5)
array_roofs(zones['候见听讼场'][0],'候见听讼场',6,3,14,4,5)
array_roofs(zones['官属舍'][0],'官属舍',12,4,15,11,6)
array_roofs(zones['县学礼仪院'][0],'县学礼仪院',8,4,18,8,6)
array_roofs(zones['武库'][0],'武库',6,3,17,8,6)
array_roofs(zones['内仓'][0],'内仓',8,4,10,8,6)

# Outer rammed-earth wall with four offset gates; gates remain a design assumption.
wall = city.buffer(4).difference(city.buffer(-4))
gatepos=[(620,0),(1500,560),(960,1500),(0,860)]
gatecuts=unary_union([box(x-13,y-13,x+13,y+13) for x,y in gatepos])
paint(wall.difference(gatecuts),'#8e8064','#675f4c',2)
for k,(x,y) in enumerate(gatepos):
    horizontal=k%2==0
    outside=[(x,-40),(1540,y),(x,1540),(-40,y)][k]
    line([(x,y),outside],'#ab987b',11)
    roof(box(x-12,y-6,x+12,y+6) if horizontal else box(x-6,y-12,x+6,y+12),'城门楼')
    offsets = [(-32,22),(32,22),(-32,60),(32,60)] if k==0 else (
        [(-22,-32),(-22,32),(-60,-32),(-60,32)] if k==1 else (
        [(-32,-22),(32,-22),(-32,-60),(32,-60)] if k==2 else
        [(22,-32),(22,32),(60,-32),(60,32)]))
    for dx,dy in offsets:
        cx=x+dx;cy=y+dy
        roof(box(cx-5,cy-5,cx+5,cy+5),'门卒舍')

# Draw water routes and bridges consistently where roads actually intersect.
for name,width,pts in roads:
    crossing=LineString(pts).buffer(width/2).intersection(water.buffer(2))
    paint(crossing,'#ab987b','#786c58',2)

map_art = im.copy()
map_art.crop((100,220,3970,4140)).resize((2300,2330)).save(HERE/'layout-reference.png')

# Readable annotations are kept separate from the generative paint layer.
text((220,80),'召陵县城 · 人口与建筑配置平面推演',78)
text((225,194),'汉末风貌设计情景  /  北向上  /  单位：米  /  v002',34, '#68716a')
text((225,255),'县域人口与城内人口分开估算；城门、街巷和功能位置均为设计推定。',29,'#836e53')
for w in wards:
    if w['households']:
        drawn=[l for l in lots if l['ward']==w['id']]
        c=unary_union([l['parcel'] for l in drawn]).representative_point()
        label((c.x,c.y),f"里{w['id']:02d} · {w['households']}户",27)
for pos,s in [((235,137),'01 县署'),((116,288),'02 狱舍'),((357,128),'03 文书吏舍'),
              ((1255,92),'04 仓廪'),((1240,417),'05 营舍'),((875,674),'06 市肆'),
              ((1310,1207),'07 作坊'),((1080,1340),'08 传舍'),((565,805),'09 医舍'),
              ((195,735),'10 社祠'),((196,294),'11 候见/听讼'),((342,264),'12 官属舍'),
              ((155,91),'13 县学/礼仪'),((342,91),'14 武库'),((260,91),'15 内仓')]:
    label(pos,s,31)
for pos,s in [((620,-28),'北门'),((1545,560),'东门'),((960,1538),'南门'),((-45,860),'西门')]:
    label(pos,s,34)
label((540,1245),'蓄水池',26,'#496b6a')
label((1100,1010),'沟渠',24,'#496b6a')
label((430,1385),'园圃 / 预留地',24,'#64734e')

# North and scale bar.
nx,ny=xy((1510,90));d.polygon([(nx,ny-80),(nx-21,ny),(nx,ny-13),(nx+21,ny)],fill=INK)
text((nx,ny-122),'北 N',30,anchor='mm')
bx,by=xy((70,1538))
for j in range(5):
    d.rectangle((bx+j*100*SCALE,by,bx+(j+1)*100*SCALE,by+17),fill=INK if j%2==0 else PAPER,outline=INK,width=2)
for j in (0,1,3,5):text((bx+j*100*SCALE,by+26),str(j*100),25,anchor='mt')
text((bx+500*SCALE+30,by+10),'m',26)

LX=4040
text((LX,380),'人口 → 户 → 屋',51)
rows=[('县域情景','约 55,000 人'),('城内居民','10,400 人'),('户均假设','5.2 人 / 户'),('住宅院落','2,000 户'),('另计驻防','400 人'),('城内合计','10,800 人'),('住宅正屋','2,000 座'),('厨房 / 附屋','2,000 座'),('公共与经营屋','286 座'),('屋顶体量总计','4,286 座')]
yy=475
for key,val in rows:
    text((LX,yy),key,31,'#74796b');text((LX+850,yy),val,34,INK,anchor='rt');yy+=74
d.line([(LX,yy+5),(4930,yy+5)],fill='#b6af9a',width=2)
yy+=50
for s,size in [('尺度与道路',42),('外城边长约 1,500 m',32),('按周长约 6 km 线索推演',28),('内城置西北，具体分期未核',28),('主街 10–12 m / 次街 6–8 m',28),('里巷 2–8 m，短街错位衔接',28),('18 里为项目分组，非汉代名册',27)]:
    text((LX,yy),s,size);yy+=60 if size<40 else 76
yy+=35
for s,size in [('功能安排',42),('县署：西北内城，三进院落',29),('候见/听讼：署前公共空间',29),('官属舍：县署东南侧',29),('县学/礼仪：内城北侧',29),('武库、内仓：内城北侧',29),('狱舍：署西隔墙，独立出入',29),('仓廪：东北，独立粮运通道',29),('市肆：近东西市街与南门路',29),('作坊：东南，留隔离与排水',29),('营舍：东北交通节点附近',29),('医舍：内街后方，便于转运',29),('门卒舍：分置四门内侧',29)]:
    text((LX,yy),s,size);yy+=62 if size<40 else 76
yy+=30
for s,size in [('证据边界',42),('郡户口总数有文献依据；',29),('召陵县域及城内人口未见确数。',28),('入城人口比例、户型、道路、',29),('官署及设施位置均为设计假设。',29),('医舍为本项目功能概括称谓。',28),('本图不是考古复原或汉末地籍。',29)]:
    text((LX,yy),s,size, '#806c52');yy+=59 if size<40 else 76

text((220,4210),'数量口径：一户画一正屋、一附屋；“屋”指独立屋顶体量，不等于房间数、人口或可进入资产数。',31)
text((220,4265),'依据：《后汉书·郡国志二》汝南郡户口；CHGIS引述召陵内外城线索；秦汉邹县与邺城考古资料作比较。',28,'#697067')
text((220,4320),'史料 / 推算 / 设计分别记录；所有建筑均有坐标与计数表。未修改正式PRD、未导入UE。',27,'#806c52')
dest=STAGE/'zhaoling-population-plan.png'
im.save(dest)
preview=im.copy();preview.thumbnail((2200,2000));preview.save(STAGE/'zhaoling-population-plan-preview.jpg',quality=94)
crop=im.crop((int(OX+350*SCALE),int(OY+500*SCALE),int(OX+1000*SCALE),int(OY+1050*SCALE)))
crop.save(STAGE/'zhaoling-street-detail.png')
im.crop((370,510,1240,1260)).save(STAGE/'zhaoling-inner-city-detail.png')

counts=Counter(b['kind'] for b in buildings)
assert counts['住宅正屋']==2000 and counts['住宅附屋']==2000
assert len(buildings)==4286, counts
summary={'version':HERE.name,'scenario_not_census':True,
    'population':{'commandery_record_people':2100788,'commandery_record_households':404448,'commandery_counties':37,
                  'county_mean_people':round(2100788/37,2),'commandery_people_per_household':round(2100788/404448,4),
                  'scenario_county_people':55000,'scenario_urban_residents':10400,'scenario_people_per_household':5.2,
                  'scenario_urban_households':2000,'additional_garrison':400,'scenario_urban_total':10800},
    'dimensions_m':[1500,1500],'enclosed_area_m2':2250000,'candidate_parcels':capacity,
    'county_office_compound_m2':round(zones['县署'][0].area,2),
    'county_office_compound_mu':round(zones['县署'][0].area/666.6667,2),
    'county_office_share_of_inner_city':round(zones['县署'][0].area/inner.area,4),
    'household_parcel_m2':320,'household_plots_total_m2':640000,
    'residential_roof_footprint_m2':sum(b['footprint_m2'] for b in buildings if b['ward']),
    'building_counts':dict(counts),'total_roof_masses':len(buildings),
    'public_and_commercial_roof_masses':sum(b['ward'] is None for b in buildings),
    'inner_city_public_roof_masses':sum(b['ward'] is None and inner.covers(Polygon(b['polygon_m'])) for b in buildings),
    'wards':[{'id':w['id'],'households':w['households']} for w in wards],
    'roads':[{'name':n,'width_m':w,'polyline_m':p} for n,w,p in roads],
    'output':str(dest),'ue_changes':0}
(HERE/'layout.json').write_text(json.dumps({'summary':summary,'buildings':buildings,
    'infrastructure_wkt':{'roads':road_geom.wkt,'water':water.wkt,'residential_area':res_area.wkt},
    'households':[{'id':f'H{i+1:04d}','ward':l['ward'],'parcel_m':list(l['parcel'].exterior.coords)} for i,l in enumerate(lots)]},ensure_ascii=False,indent=2),encoding='utf-8')
(EVIDENCE/'quantities.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    pass
