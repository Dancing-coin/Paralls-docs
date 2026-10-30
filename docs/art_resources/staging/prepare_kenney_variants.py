"""Run through Blender GUI MCP after importing Kenney Mini Arena soldier."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector, Quaternion

out = Path(bpy.data.filepath).parent / 'kenney_variants_v1'
out.mkdir(exist_ok=True)
scene = bpy.context.scene
source = [bpy.data.objects[n] for n in ('character_soldier', 'root', 'body_mesh', 'head_mesh')]
image = bpy.data.images['DiffuseColor_Texture']
pixels = list(image.pixels)
width, height = image.size
actions = {a.name.split('|')[1]: a for a in bpy.data.actions}
source[1].animation_data.action = actions['static']
scene.frame_set(1)
bpy.context.view_layer.update()

def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = .85
    mat.use_backface_culling = False
    return mat

skin = material('GS_Skin', (.65, .38, .23))
steel = material('GS_Iron', (.12, .16, .19))
leather = material('GS_Leather', (.09, .055, .035))
blue = material('GS_TeamBlue', (.025, .18, .7))
red = material('GS_TeamRed', (.65, .025, .015))
gold = material('GS_CommandGold', (.65, .35, .045))

variants = []
for name, team, location in [('Soldier', blue, (-.75, 0, 0)), ('General', red, (.75, 0, 0))]:
    collection = bpy.data.collections.new('GS_' + name)
    scene.collection.children.link(collection)
    copies = {}
    for original in source:
        obj = original.copy()
        if original.data:
            obj.data = original.data.copy()
        obj.name = 'GS_' + name + '_' + original.name
        collection.objects.link(obj)
        copies[original] = obj
    for original, obj in copies.items():
        if original.parent in copies:
            obj.parent = copies[original.parent]
        for modifier in obj.modifiers:
            if modifier.type == 'ARMATURE':
                modifier.object = copies[source[1]]
    root = copies[source[0]]
    root.scale *= 2.3
    root.location = location
    rig = copies[source[1]]
    rig.animation_data.action = actions['static']
    body, head = copies[source[2]], copies[source[3]]
    for obj in (body, head):
        uv = obj.data.uv_layers.active.data
        obj.data.materials.clear()
        for mat in (skin, steel, leather, team, gold):
            obj.data.materials.append(mat)
        for polygon in obj.data.polygons:
            u = sum(uv[i].uv.x for i in polygon.loop_indices) / len(polygon.loop_indices)
            v = sum(uv[i].uv.y for i in polygon.loop_indices) / len(polygon.loop_indices)
            index = 4 * (min(height-1, max(0, int(v*height)))*width + min(width-1, max(0, int(u*width))))
            r, g, b = pixels[index:index+3]
            if r > .8 and g < .45:
                polygon.material_index = 3
            elif b > r + .035:
                polygon.material_index = 4 if name == 'General' else 1
            elif r > .8 and g > .6:
                polygon.material_index = 0
            elif r < .35:
                polygon.material_index = 2
            else:
                polygon.material_index = 1
    # Compress only the original crest above the helmet into a short plume.
    crest = set()
    for polygon in head.data.polygons:
        if polygon.material_index == 3:
            crest.update(polygon.vertices)
    for index in crest:
        vertex = head.data.vertices[index]
        point = source[3].matrix_world @ vertex.co
        point.y = .065 + (point.y - .065) * .27
        point.z = .69 + (point.z - .69) * (.75 if name == 'General' else .25)
        vertex.co = source[3].matrix_world.inverted() @ point
    meshes = [body, head]
    if name == 'General':
        # Six vertices, four triangles, rigidly weighted to original torso.
        data = bpy.data.meshes.new('GS_CommandCape')
        data.from_pydata([(-.17,.17,.33),(.17,.17,.33),(-.23,.24,.18),(.23,.24,.18),(-.26,.3,.055),(.26,.3,.055)], [], [(0,1,3,2),(2,3,5,4)])
        data.materials.append(team)
        cape = bpy.data.objects.new('GS_General_Cape', data)
        collection.objects.link(cape)
        cape.parent = root
        cape.vertex_groups.new(name='torso').add(list(range(6)), 1, 'REPLACE')
        cape.modifiers.new('OriginalRig', 'ARMATURE').object = rig
        meshes.append(cape)
    variants.append((name, root, rig, meshes))

report = {'source': 'Kenney Mini Arena 1.1 / CC0', 'variants': [], 'source_actions': list(actions)}
for name, root, rig, meshes in variants:
    # Export at origin. Keep preview offsets only in the saved .blend.
    original_location = root.location.copy()
    root.location = (0, 0, 0)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in [root, rig] + meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = rig
    rig.animation_data.action = actions['static']
    scene.frame_set(1)
    bpy.context.view_layer.update()
    bpy.ops.export_scene.fbx(filepath=str(out / ('SK_GS_' + name + '.fbx')), use_selection=True, object_types={'MESH','ARMATURE','EMPTY'}, add_leaf_bones=False, bake_anim=False, axis_forward='-Y', axis_up='Z', path_mode='AUTO')
    triangles = sum(sum(len(p.vertices)-2 for p in obj.data.polygons) for obj in meshes)
    report['variants'].append({'name':name, 'triangles':triangles, 'source_bones':len(rig.data.bones), 'materials':sorted(set(m.name for obj in meshes for m in obj.data.materials))})
    if name == 'Soldier':
        for clip in ('idle', 'walk', 'die'):
            rig.animation_data.action = actions[clip]
            scene.frame_start, scene.frame_end = map(int, actions[clip].frame_range)
            bpy.ops.export_scene.fbx(filepath=str(out / ('AN_GS_' + clip + '.fbx')), use_selection=True, object_types={'ARMATURE'}, add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False, bake_anim_simplify_factor=0, axis_forward='-Y', axis_up='Z')
    rig.animation_data.action = actions['idle']
    root.location = original_location
for obj in source:
    obj.hide_set(True)
    obj.hide_render = True
scene.frame_start, scene.frame_end = 1, 82
scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces.active
            space.shading.type = 'MATERIAL'
            space.region_3d.view_distance = 5
            space.region_3d.view_location = Vector((0,0,.95))
            space.region_3d.view_rotation = Quaternion((.92,.38,0,0))
scene.render.resolution_x, scene.render.resolution_y = 1200, 900
scene.render.resolution_percentage = 100
report['blender_file'] = str(out / 'GS_CharacterVariants.blend')
(out / 'preparation_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
result = report
