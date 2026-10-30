"""Run inside Unreal Editor: py <project>/Scripts/build_battlefield.py.
Only rebuilds the dedicated /Game/Battle/Lvl_Battlefield scene.
"""
import unreal as u
import math
import os
import random

ROOT = u.Paths.convert_relative_path_to_full(u.Paths.project_dir())
OUT = os.path.join(ROOT, 'Saved', 'BattlefieldBuild')
os.makedirs(OUT, exist_ok=True)
E = u.get_editor_subsystem(u.EditorActorSubsystem)
L = u.get_editor_subsystem(u.LevelEditorSubsystem)
A = u.AssetToolsHelpers.get_asset_tools()
M = u.MaterialEditingLibrary


def height(x, y):
    # Traversable central valley, rolling shoulders and distant hills.
    shoulders = 650 * (1 - math.exp(-(y / 5500) ** 4))
    waves = 160 * math.sin(x / 3900) * math.sin(y / 2800)
    ripples = 24 * math.sin(x / 1200 + .4) * math.cos(y / 1500)
    return shoulders + waves + ripples


def material(name, color, noise=False, two_sided=False):
    path = '/Game/Battle/Materials/' + name
    mat = u.load_asset(path)
    if not mat:
        mat = A.create_asset(name, '/Game/Battle/Materials', u.Material, u.MaterialFactoryNew())
    M.delete_all_material_expressions(mat)
    mat.set_editor_property('two_sided', two_sided)
    p = M.create_material_expression(mat, u.MaterialExpressionVectorParameter, -400, 0)
    p.set_editor_property('parameter_name', 'TeamColor')
    p.set_editor_property('default_value', u.LinearColor(*color))
    M.connect_material_property(p, '', u.MaterialProperty.MP_BASE_COLOR)
    if noise:
        pos = M.create_material_expression(mat, u.MaterialExpressionWorldPosition, -1000, 300)
        n = M.create_material_expression(mat, u.MaterialExpressionNoise, -800, 300)
        n.set_editor_property('scale', .005)
        M.connect_material_expressions(pos, '', n, 'Position')
        low = M.create_material_expression(mat, u.MaterialExpressionConstant3Vector, -800, 500)
        low.set_editor_property('constant', u.LinearColor(color[0]*.5, color[1]*.5, color[2]*.5, 1))
        mix = M.create_material_expression(mat, u.MaterialExpressionLinearInterpolate, -100, 0)
        M.connect_material_expressions(p, '', mix, 'A')
        M.connect_material_expressions(low, '', mix, 'B')
        M.connect_material_expressions(n, '', mix, 'Alpha')
        M.connect_material_property(mix, '', u.MaterialProperty.MP_BASE_COLOR)
    rough = M.create_material_expression(mat, u.MaterialExpressionConstant, -100, 450)
    rough.set_editor_property('r', .85)
    M.connect_material_property(rough, '', u.MaterialProperty.MP_ROUGHNESS)
    M.recompile_material(mat)
    u.EditorAssetLibrary.save_loaded_asset(mat)
    return mat


def mesh_import(name, filename):
    path = '/Game/Battle/Meshes/' + name
    if u.EditorAssetLibrary.does_asset_exist(path):
        return u.load_asset(path)
    task = u.AssetImportTask()
    task.filename = filename
    task.destination_path = '/Game/Battle/Meshes'
    task.destination_name = name
    task.automated = True
    task.save = True
    task.replace_existing = True
    # Leave options unset so AssetTools selects the importer from the file
    # extension. In particular, OBJ files must not receive FbxImportUI.
    A.import_asset_tasks([task])
    mesh = u.load_asset(path)
    if not mesh:
        raise RuntimeError('Mesh import failed: ' + path)
    return mesh


def ground_mesh():
    file = os.path.join(OUT, 'SM_BattleTerrain.obj')
    size, n = 48000, 161
    # OBJ vertices are written with Z as up, matching Unreal's coordinate system.
    with open(file, 'w') as f:
        f.write('o BattleTerrain\n')
        for j in range(n):
            y = -size/2 + j*size/(n-1)
            for i in range(n):
                x = -size/2 + i*size/(n-1)
                f.write('v %.5f %.5f %.5f\n' % (x, height(x,y), -y))
        for j in range(n-1):
            for i in range(n-1):
                a = j*n+i+1
                # The second OBJ axis is inverted above to make Z-up, so wind
                # triangles in the opposite order to keep their normals up.
                f.write('f %d %d %d\nf %d %d %d\n' % (a,a+n,a+1,a+1,a+n,a+n+1))
    mesh = mesh_import('SM_BattleTerrain', file)
    body = mesh.get_editor_property('body_setup')
    body.set_editor_property('collision_trace_flag', u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    u.EditorAssetLibrary.save_loaded_asset(mesh)
    return mesh


def spawn(cls, label, x=0, y=0, z=0, yaw=0):
    actor = E.spawn_actor_from_class(cls, u.Vector(x,y,z), u.Rotator(0,yaw,0))
    actor.set_actor_label(label)
    return actor


def static(label, mesh, loc, scale=(1,1,1), mat=None, yaw=0, folder='Environment'):
    actor = spawn(u.StaticMeshActor, label, *loc, yaw=yaw)
    actor.set_actor_scale3d(u.Vector(*scale))
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    if mat: comp.set_material(0,mat)
    actor.set_folder_path(folder)
    return actor


def main():
    assert L.get_current_level().get_path_name().startswith('/Game/Battle/Lvl_Battlefield'), 'Open the dedicated battlefield first.'
    terrain = ground_mesh()
    grass = material('M_BattleGrass', (.16,.205,.075,1), True)
    timber = material('M_Timber', (.13,.065,.025,1))
    rock = material('M_Rock', (.17,.19,.15,1), True)
    brown = material('M_Horse', (.19,.075,.028,1))
    unit = material('M_UnitColor', (.05,.22,.55,1))
    blue = material('M_BannerBlue', (.025,.16,.5,1), two_sided=True)
    red = material('M_BannerRed', (.48,.035,.02,1), two_sided=True)
    leaf = material('M_Foliage', (.08,.15,.035,1), True)
    # Only the newly copied battlefield level is cleared. Original template remains intact.
    for actor in E.get_all_level_actors():
        if not isinstance(actor, (u.WorldSettings,)):
            E.destroy_actor(actor)
    ground = static('Battlefield / rolling grass valley', terrain, (0,0,0), mat=grass, folder='Terrain')
    ground.static_mesh_component.set_collision_profile_name('BlockAll')
    sun = spawn(u.DirectionalLight, 'Sun / late afternoon', z=10000)
    sun.set_actor_rotation(u.Rotator(-32,-38,0), False)
    sun.light_component.set_editor_property('mobility', u.ComponentMobility.MOVABLE)
    sun.light_component.set_editor_property('intensity', 4.0)
    sun.light_component.set_editor_property('atmosphere_sun_light', True)
    sky = spawn(u.SkyAtmosphere, 'Sky atmosphere')
    fill = spawn(u.SkyLight, 'Sky fill', z=2000)
    fill.light_component.set_editor_property('mobility', u.ComponentMobility.MOVABLE)
    fill.light_component.set_editor_property('real_time_capture', True)
    fill.light_component.set_editor_property('intensity', .8)
    fog = spawn(u.ExponentialHeightFog, 'Valley haze', z=-300)
    fog.component.set_editor_property('fog_density', .003)
    start = spawn(u.PlayerStart, 'Mounted commander start', -2400,0,height(-2400,0)+110)
    start.set_folder_path('Player')
    mode = u.load_class(None, '/Script/mcp.BattleGameMode')
    u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_world_settings().set_editor_property('default_game_mode', mode)
    cylinder = u.load_asset('/Engine/BasicShapes/Cylinder')
    sphere = u.load_asset('/Engine/BasicShapes/Sphere')
    plane = u.load_asset('/Engine/BasicShapes/Plane')
    # Standards provide visible team identity and a concrete future command objective.
    for enemy, x, flagmat in [(False,-1000,blue),(True,4200,red)]:
        for team in range(1,4):
            y = (team-2)*1500
            z = height(x,y)
            side = 'Enemy' if enemy else 'Allied'
            static(side+' standard pole '+str(team), cylinder, (x,y,z+240), (.08,.08,4.8), timber, folder='Standards')
            flag = static(side+' company banner '+str(team), plane, (x,y+80,z+400), (1.6,1.1,1), flagmat, folder='Standards')
            flag.set_actor_rotation(u.Rotator(0,0,90),False)
            flag.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
    cls = u.load_class(None, '/Script/mcp.BattleUnit')
    rider_cls = u.load_class(None, '/Script/mcp.BattleRiderCharacter')
    # 1 battalion = 3 companies; 12 infantry per company, plus one guard squad.
    for enemy, x0 in [(False,-900),(True,3800)]:
        for company in range(1,4):
            for index in range(12):
                row, col = divmod(index,4)
                x = x0 + (row*150 if enemy else -row*150)
                y = (company-2)*1500+(col-1.5)*150
                a = spawn(cls, ('Red' if enemy else 'Blue')+' / Company %d / Soldier %02d'%(company,index+1), x,y,height(x,y)+100,180 if enemy else 0)
                a.set_editor_property('unit_id', ('enemy' if enemy else 'player')+'_company_%d_soldier_%02d'%(company,index+1))
                a.set_editor_property('army_id', 'army_enemy' if enemy else 'army_player')
                a.set_editor_property('formation_slot', company)
                a.set_folder_path(('Enemy' if enemy else 'Allied')+'/Company '+str(company))
                a.configure_appearance(u.LinearColor(.5,.045,.025,1) if enemy else u.LinearColor(.035,.16,.5,1),company==1,company==2,index==0)
    for index in range(6):
        x,y = -2650-(index//3)*220, (index%3-1)*260
        a=spawn(rider_cls,'Gold / Guard squad / Rider %02d'%(index+1),x,y,height(x,y)+100)
        a.set_editor_property('unit_id','player_guard_%02d'%(index+1))
        a.set_editor_property('army_id','army_player')
        a.set_editor_property('formation_slot',0)
        a.configure_appearance(u.LinearColor(.6,.35,.055,1),False,False,index==0)
        a.set_folder_path('Allied/Guard squad')
    # Scattered stones and tree groups on valley shoulders leave a clear charge corridor.
    rng = random.Random(23)
    for i in range(44):
        x,y = rng.uniform(-10000,12000),rng.choice([-1,1])*rng.uniform(4200,11000)
        z=height(x,y)
        s=rng.uniform(1.2,3.8)
        static('Valley rock %02d'%i,sphere,(x,y,z+25),(s,s*.65,s*.5),rock,rng.uniform(0,360),'Terrain/Rocks')
        if i%2==0:
            static('Tree trunk %02d'%i,cylinder,(x+200,y,z+210),(.32,.32,4.2),timber,folder='Environment/Trees')
            static('Tree canopy %02d'%i,sphere,(x+200,y,z+540),(4.5,4.2,5),leaf,folder='Environment/Trees')
    u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(-4600,-4400,2600),u.Rotator(-18,38,0))
    L.save_current_level()
    u.EditorAssetLibrary.save_directory('/Game/Battle',only_if_is_dirty=True,recursive=True)
    u.log('BATTLEFIELD_BUILD_SUCCESS: terrain, 72 infantry, 6 guards, 6 standards')

main()
