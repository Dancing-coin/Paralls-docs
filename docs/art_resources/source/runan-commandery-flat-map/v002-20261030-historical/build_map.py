"""Rebuild the evidence-led county-seat map; run from any working directory."""
from pathlib import Path
import csv
import hashlib
import json
import math
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2]
VERSION = HERE.name
EVIDENCE = ART / 'evidence/runan-commandery-flat-map' / VERSION
OUT = ART / 'staging/runan-commandery-flat-map' / VERSION
OUT.mkdir(parents=True, exist_ok=True)
roster = json.loads((HERE / 'county-roster.json').read_text(encoding='utf-8'))
ids = [83172, None, 83167, 83174, 82040, 43318, 82015, 82588,
       None, 83019, None, 82578, 83166, 82047, 82026, 43359,
       83099, 83171, 83098, 83168, 43328, 83173, 83169, 43324,
       82070, 83170, 82552, 83032, 83034, 43378, 43366, 82593,
       43325, None, None, 43374, 43348]
notes = {
    '平舆': '郡治。数据库记今平舆县射桥镇古城村，不取现代县城。',
    '新阳': '《史记正义》引《括地志》有真阳县西南四十二里说；乾隆《大清一统志》卷089有太和县西北六十里说，方向冲突，暂不强行定位。',
    '北宜春': '《读史方舆纪要》卷五十引《括地志》记汝宁府西南六十七里；缺核实后的遗址坐标。',
    '㶏强': 'CHGIS 名称编码为[氵隐]强。时间字段仅25—29，源注另记同址县30—265；本图按源注落点。',
    '灈阳': '《读史方舆纪要》卷五十记遂平县东南。《水经注》载吴房以东、上蔡以西；不取隋灈阳县的吴房同址坐标。',
    '西华': '依《郡国志》列入；CHGIS 源注有顺帝时属淮阳国说。名册与年代断面有差异，不能据此图认定某年郡界。',
    '安城': '按《郡国志》书安城，亦见安成；不是江西安成。',
    '鲖阳': 'CHGIS begin=206；源注明确为公元前206置、东汉因之，按源注处理数据库符号错误。',
    '富波': '保留《郡国志》名册写法，不自动改作富陂。',
    '宋': '宋公国；原新郪，属县级单位，并非一般县。',
    '定颍': '《水经注》卷31潕水条记过县北；《读史方舆纪要》卷五十记上蔡县北；乾隆《大清一统志》卷168又作西平县北，位置记载有异，缺可核验坐标。',
    '固始': '汉寝改固始。今临泉一带说与今固始一带说并存；不直接套用现代固始县城，也不取陈郡同名县。',
}
geo_url = 'https://zh.wikisource.org/wiki/讀史方輿紀要/卷五十'
rows = []
for i, (name, ident) in enumerate(zip(roster['names_in_text_order'], ids), 1):
    r = dict(number=i, name=name, longitude=None, latitude=None,
             status='位置待考', source_url=geo_url, chgis_id=None,
             note=notes.get(name, 'CHGIS 治所记录；县级归属以《郡国志》名册为本。'))
    if ident:
        j = json.loads((EVIDENCE / f'canonical-counties/hvd_{ident}.json').read_text(encoding='utf-8'), strict=False)
        r.update(longitude=float(j['spatial']['longitude']), latitude=float(j['spatial']['latitude']),
                 status='数据库治所', chgis_id=f'hvd_{ident}', source_url=j['uri'],
                 database_temporal=j['temporal'], database_source_note=j.get('source note', ''),
                 coordinate_license=j['license'])
    rows.append(r)
assert len(rows) == len({r['name'] for r in rows}) == 37
located = [r for r in rows if r['longitude'] is not None]
pending = [r for r in rows if r['longitude'] is None]
assert len(located) == 32 and len(pending) == 5
(HERE / 'counties.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
with (HERE / 'counties.csv').open('w', encoding='utf-8-sig', newline='') as f:
    fields = ['number', 'name', 'longitude', 'latitude', 'status', 'chgis_id', 'source_url', 'note']
    w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); w.writeheader(); w.writerows(rows)

W, H = 4200, 3000
PAPER, INK, MUTED = '#F4F0E6', '#253D37', '#75827A'
GRID, RED, GOLD = '#DADDD1', '#A64436', '#9C7041'
im = Image.new('RGB', (W, H), PAPER)
d = ImageDraw.Draw(im)
def font(size, serif=False):
    return ImageFont.truetype('C:/Windows/Fonts/simsun.ttc' if serif else 'C:/Windows/Fonts/msyh.ttc', size)
def text(x, y, value, size=34, fill=INK, serif=False, **kwargs):
    d.text((x, y), value, font=font(size, serif), fill=fill, **kwargs)
def line(xy, fill=GRID, width=2):
    d.line(xy, fill=fill, width=width)

text(140, 83, '汝南郡', 112, serif=True)
text(151, 218, '东汉 · 三十七城县治分布考证图', 42)
text(145, 290, '名册依据《后汉书·郡国志》  /  顺帝时期名册口径，非指定汉末年份断面', 28, MUTED)
d.rectangle((3430, 100, 4060, 255), outline=RED, width=3)
text(3475, 125, '考证候选稿', 46, RED, True)
text(3475, 194, '32 处落点 · 5 处待考', 26, RED)
line([(140, 360), (4060, 360)], INK, 3)

# Equirectangular projection at 33 N; the map frame is not an administrative boundary.
west, east, south, north = 113.5, 116.85, 31.98, 33.97
x0, y0, x1, y1 = 190, 460, 2920, 2392
sx = (x1 - x0) / (east - west)
sy = sx / math.cos(math.radians(33))
def xy(lon, lat):
    return x0 + (lon - west) * sx, y1 - (lat - south) * sy
map_top = xy(west, north)[1]
for lon in [113.5, 114, 114.5, 115, 115.5, 116, 116.5]:
    x, _ = xy(lon, south)
    line([(x, map_top), (x, y1)])
    text(x, y1 + 30, f'{lon:g}°E', 25, MUTED, anchor='mt')
for lat in [32, 32.5, 33, 33.5]:
    _, y = xy(west, lat)
    line([(x0, y), (x1, y)])
    text(x0 - 25, y, f'{lat:g}°N', 25, MUTED, anchor='rm')
text(206, 451, '县治位置', 31, MUTED)
text(2920, 451, '北', 38, INK, anchor='rt')
d.polygon([(2897, 505), (2880, 554), (2897, 544), (2914, 554)], fill=INK)

# Reserve all marker boxes before label placement, then choose non-overlapping label boxes.
point_boxes = []
for r in located:
    x, y = xy(r['longitude'], r['latitude'])
    point_boxes.append((x - 22, y - 22, x + 22, y + 22))
occupied, placements = [], []
def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])
for r in sorted(located, key=lambda r: r['name'] not in ['平舆', '召陵']):
    x, y = xy(r['longitude'], r['latitude'])
    label = f"{r['number']:02d} {r['name']}"
    fs = 44 if r['name'] in ['平舆', '召陵'] else 39
    tw = d.textlength(label, font=font(fs)); th = fs + 18
    options = []
    for dist in [32, 65, 105, 145]:
        options.extend([(x + dist, y - th / 2), (x - tw - dist, y - th / 2),
                        (x - tw / 2, y - th - dist), (x - tw / 2, y + dist)])
    best = None
    for tx, ty in options:
        box = (tx - 8, ty - 3, tx + tw + 8, ty + th)
        if box[0] < x0 or box[2] > x1 or box[1] < map_top or box[3] > y1:
            continue
        if any(overlap(box, b) for b in occupied + point_boxes):
            continue
        best = (tx, ty, box); break
    if best is None:
        raise ValueError(f'No collision-free position for {label}')
    tx, ty, box = best
    occupied.append(box)
    color = RED if r['name'] in ['平舆', '召陵'] else INK
    if math.hypot(tx + tw / 2 - x, ty + th / 2 - y) > 160:
        line([(x, y), (max(tx, min(x, tx + tw)), ty + th / 2)], MUTED, 2)
    d.rectangle(box, fill=PAPER)
    text(tx, ty, label, fs, color)
    if r['name'] == '平舆':
        d.rectangle((x - 15, y - 15, x + 15, y + 15), fill=RED)
        d.rectangle((x - 8, y - 8, x + 8, y + 8), fill=PAPER)
    elif r['name'] == '召陵':
        d.ellipse((x - 19, y - 19, x + 19, y + 19), outline=RED, width=3)
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=RED)
    else:
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=INK)
    placements.append(dict(name=r['name'], point=[x, y], label_bbox=box))

# Modern distance scale, independent of historical li units.
scale_x, scale_y = 215, 2310
length = 50 / (111.32 * math.cos(math.radians(33))) * sx
line([(scale_x, scale_y), (scale_x + length, scale_y)], INK, 5)
for tick in [0, .5, 1]:
    line([(scale_x + length * tick, scale_y - 10), (scale_x + length * tick, scale_y + 10)], INK, 3)
text(scale_x, scale_y + 17, '0', 25, MUTED)
text(scale_x + length, scale_y + 17, '50 km', 25, MUTED, anchor='rt')

# Complete index: all 37 entries, including counties, marquisates and the Song dukedom.
line([(3040, 430), (3040, 2440)], GRID, 3)
text(3160, 433, '三十七城全目', 55, serif=True)
text(3160, 510, '编号依《郡国志》原文次序', 26, MUTED)
for i, r in enumerate(rows):
    col, row = divmod(i, 19)
    xx, yy = 3160 + col * 470, 592 + row * 72
    color = GOLD if r['status'] == '位置待考' else INK
    suffix = ' *' if r['status'] == '位置待考' else ''
    text(xx, yy, f"{r['number']:02d}", 27, MUTED)
    text(xx + 65, yy - 3, r['name'] + suffix, 37, color)
text(3160, 2030, '* 位置待考，共五处', 30, GOLD)
text(3160, 2090, '方框  平舆：汝南郡治', 29)
text(3160, 2142, '红圈  召陵：项目关注县', 29, RED)
text(3160, 2210, '实点  CHGIS 治所坐标', 29)
text(3160, 2270, '坐标表示数据库复原位置，', 27, MUTED)
text(3160, 2312, '不代表遗址测绘精度。', 27, MUTED)
text(3160, 2375, '未绘未经核实的郡界、县界及古河道。', 25, MUTED)

line([(140, 2510), (4060, 2510)], INK, 2)
text(145, 2546, '尚待定位', 43, GOLD, True)
pending_lines = [
    '02 新阳：正阳西南与界首北两说待辨。    09 北宜春：古籍记汝宁府西南，遗址坐标待核。',
    '11 灈阳：吴房以东、上蔡以西，不能套用隋代同名县。    34 定颍：古籍方位记载有异，治所待核。',
    '35 固始：临泉与今固始两说并存；暂不将现代固始县城标作汉代治所。',
]
for i, s in enumerate(pending_lines):
    text(460, 2552 + i * 60, s, 31, INK)
text(145, 2790, '依据：《后汉书·郡国志》名册；Harvard / Fudan CHGIS 治所记录；《水经注》《读史方舆纪要》补查。', 26, MUTED)
text(145, 2835, '地图参考：Zunkir《Han orientaux 140》（CC BY-SA 4.0）；仅核查大范围方位，未描摹界线。', 25, MUTED)
text(145, 2880, '研究用候选图 · CHGIS 数据 CC BY-NC 4.0 · 县级单位含县与国 · 西华等存在年代口径差异 · 2026-10-30 / v002', 25, MUTED)

for i, a in enumerate(placements):
    for b in placements[i + 1:]:
        assert not overlap(a['label_bbox'], b['label_bbox']), (a['name'], b['name'])
path = OUT / 'runan_county_seats.png'
im.save(path, optimize=True, dpi=(300, 300))
preview = im.copy(); preview.thumbnail((1680, 1200)); preview.save(OUT / 'runan_county_seats_preview.jpg', quality=92)
report = dict(version=VERSION, roster_count=len(rows), unique_names=37, plotted_count=len(located),
              pending_count=len(pending), pending_names=[r['name'] for r in pending],
              dimensions=list(im.size), format='PNG', size_bytes=path.stat().st_size,
              sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
              label_overlaps=0, projection='Equirectangular, standard parallel 33 N',
              boundary_and_watercourse_reconstruction=False,
              image_model='No image model for v002: deterministic placement preserves the cited coordinates and names',
              ue_changes=False, placements=placements)
(EVIDENCE / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'placements'}, ensure_ascii=False, indent=2))
print(path)
