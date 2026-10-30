"""Verify quantities and geometry in the delivered layout, independently of drawing."""
from pathlib import Path
from collections import Counter
import json
from shapely import wkt
from shapely.geometry import Polygon
from shapely.strtree import STRtree
from PIL import Image

here=Path(__file__).resolve().parent
art=here.parents[2]
data=json.loads((here/'layout.json').read_text(encoding='utf-8'))
buildings=data['buildings']
parcels=[Polygon(h['parcel_m']) for h in data['households']]
roofs=[Polygon(b['polygon_m']) for b in buildings]

def overlaps(geometries):
    tree=STRtree(geometries)
    return [(i,int(j)) for i,g in enumerate(geometries)
            for j in tree.query(g,predicate='intersects')
            if j>i and g.intersection(geometries[j]).area>.01]

counts=Counter(b['kind'] for b in buildings)
assert len(parcels)==2000 and len(roofs)==4286
assert counts['住宅正屋']==counts['住宅附屋']==2000
assert sum(w['households'] for w in data['summary']['wards'])==2000
assert not overlaps(parcels), 'Overlapping household parcels'
assert not overlaps(roofs), 'Overlapping roofs'
assert all(p.buffer(.002).covers(roofs[i*2]) and p.buffer(.002).covers(roofs[i*2+1])
           for i,p in enumerate(parcels)), 'Dwelling roof outside its parcel'
infrastructure={k:wkt.loads(v) for k,v in data['infrastructure_wkt'].items()}
assert all(p.difference(infrastructure['residential_area']).area<.01 for p in parcels)
road_conflicts=[b['id'] for b,g in zip(buildings,roofs)
                if b['kind']!='城门楼' and g.intersection(infrastructure['roads']).area>.01]
assert not road_conflicts, road_conflicts
assert all(g.intersection(infrastructure['water']).area<.01 for g in roofs)
images=[]
for p in sorted((art/'staging/zhaoling-city'/here.name).glob('*')):
    if p.suffix.lower() in {'.jpg','.png'}:
        with Image.open(p) as im:
            im.load()
            images.append({'path':str(p.relative_to(art)),'dimensions':list(im.size),'format':im.format})
result={'status':'passed','households':len(parcels),'roofs':len(roofs),
        'parcel_overlap_pairs':0,'roof_overlap_pairs':0,'roof_road_conflicts':0,
        'roof_water_conflicts':0,'all_dwelling_roofs_within_parcels':True,
        'exceptions':'Four gatehouses intentionally span gate passages; excluded from road-conflict check.',
        'limitations':'Plan geometry only; no archaeology, live population, navigation simulation or UE validation. The AI illustration is from the pre-adjustment plan and is not validated for the reduced county-office footprint.',
        'images':images,'ue_changes':0}
(art/'evidence/zhaoling-city'/here.name/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
