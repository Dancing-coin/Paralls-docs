import bpy
from collections import Counter
img=bpy.data.images['DiffuseColor_Texture']; px=list(img.pixels); w,h=img.size
result={'size':[w,h],'samples':{}}
for name in ['body_mesh','head_mesh']:
 o=bpy.data.objects[name]; uv=o.data.uv_layers.active.data; rows=[]
 for p in o.data.polygons:
  u=sum(uv[i].uv.x for i in p.loop_indices)/len(p.loop_indices); v=sum(uv[i].uv.y for i in p.loop_indices)/len(p.loop_indices)
  k=4*(min(h-1,max(0,int(v*h)))*w+min(w-1,max(0,int(u*w))))
  rgb=tuple(round(c,2) for c in px[k:k+3]); center=o.matrix_world@p.center
  rows.append((rgb,round(center.z,3)))
 result['samples'][name]={'colors':Counter(rgb for rgb,z in rows).most_common(),'color_heights':[(rgb,min(z for c,z in rows if c==rgb),max(z for c,z in rows if c==rgb)) for rgb in dict(rows)]}
