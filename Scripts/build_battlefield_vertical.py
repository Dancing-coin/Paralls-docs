import unreal as u
import math, random

E = u.get_editor_subsystem(u.EditorActorSubsystem)
L = u.get_editor_subsystem(u.LevelEditorSubsystem)
world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert L.get_current_level().get_path_name() == '/Game/Battle/Lvl_Battlefield_Vertical'

def rot(p=0,y=0,r=0):
    return u.Rotator(pitch=p, yaw=y, roll=r)

def spawn(cls, label, loc=(0,0,0), yaw=0):
    a = E.spawn_actor_from_class(cls, u.Vector(*loc), rot(yaw=yaw))
    a.set_actor_label(label)
    return a

def static(label, mesh, loc, scale=(1,1,1), mat=None, yaw=0, folder='Environment'):
    a = spawn(u.StaticMeshActor, label, loc, yaw)
    a.set_actor_scale3d(u.Vector(*scale))
    a.static_mesh_component.set_static_mesh(mesh)
    if mat: a.static_mesh_component.set_material(0, mat)
    a.set_folder_path(folder)
    return a

def height(x,y):
    return 650*(1-math.exp(-(y/5500.0)**4)) + 160*math.sin(x/3900.0)*math.sin(y/2800.0) + 24*math.sin(x/1200.0+.4)*math.cos(y/1500.0)

# Safe for the non-partitioned slice: keep WorldSettings and never touch WP actors.
for a in list(E.get_all_level_actors()):
    if not isinstance(a, u.WorldSettings): E.destroy_actor(a)

terrain = u.load_asset('/Game/Battle/Meshes/SM_BattleTerrain')
mat_grass = u.load_asset('/Game/Battle/Materials/M_BattleGrass')
mat_timber = u.load_asset('/Game/Battle/Materials/M_Timber')
mat_rock = u.load_asset('/Game/Battle/Materials/M_Rock')
mat_blue = u.load_asset('/Game/Battle/Materials/M_BannerBlue')
mat_red = u.load_asset('/Game/Battle/Materials/M_BannerRed')
mat_leaf = u.load_asset('/Game/Battle/Materials/M_Foliage')
assert terrain
static('Battlefield terrain / rolling valley', terrain, (0,0,0), mat=mat_grass, folder='Terrain')

sun = spawn(u.DirectionalLight, 'Sun / late afternoon', (0,0,10000))
sun.set_actor_rotation(rot(p=-32,y=-38), False)
sun.light_component.set_editor_property('mobility', u.ComponentMobility.MOVABLE)
sun.light_component.set_editor_property('intensity', 4.0)
fill = spawn(u.SkyLight, 'Sky fill', (0,0,2500))
fill.light_component.set_editor_property('mobility', u.ComponentMobility.MOVABLE)
fill.light_component.set_editor_property('intensity', 0.8)
try: fill.light_component.set_editor_property('real_time_capture', True)
except: pass
spawn(u.SkyAtmosphere, 'Sky atmosphere', (0,0,0))
fog = spawn(u.ExponentialHeightFog, 'Valley haze', (0,0,-300))
fog.component.set_editor_property('fog_density', .0012)

# Charge lane markers: timber stakes and team standards.
cylinder = u.load_asset('/Engine/BasicShapes/Cylinder')
plane = u.load_asset('/Engine/BasicShapes/Plane')
sphere = u.load_asset('/Engine/BasicShapes/Sphere')
for enemy,x,flagmat in [(False,-1400,mat_blue),(True,4200,mat_red)]:
    for team in range(1,4):
        y=(team-2)*1500; z=height(x,y); side='Enemy' if enemy else 'Allied'
        static(f'{side} standard pole {team}', cylinder, (x,y,z+250), (.10,.10,5.0), mat_timber, folder='Standards')
        f=static(f'{side} company banner {team}', plane, (x,y+90,z+420), (1.8,1.2,1), flagmat, folder='Standards')
        f.set_actor_rotation(rot(y=90), False)

unit_cls=u.load_class(None,'/Script/mcp.BattleUnit')
rider_cls=u.load_class(None,'/Script/mcp.BattleRiderCharacter')
for enemy,x0 in [(False,-850),(True,3800)]:
    for company in range(1,4):
        for idx in range(12):
            row,col=divmod(idx,4); x=x0+(row*170 if enemy else -row*170); y=(company-2)*1500+(col-1.5)*180
            a=spawn(unit_cls, ('Red' if enemy else 'Blue')+f' / Company {company} / Soldier {idx+1:02d}', (x,y,height(x,y)+100), 180 if enemy else 0)
            a.set_editor_property('unit_id',('enemy' if enemy else 'player')+f'_company_{company}_soldier_{idx+1:02d}')
            a.set_editor_property('army_id','army_enemy' if enemy else 'army_player')
            a.set_editor_property('formation_slot',company)
            a.configure_appearance(u.LinearColor(.62,.04,.02,1) if enemy else u.LinearColor(.03,.15,.60,1), company==1, company==2, idx==0)
            a.set_folder_path(('Enemy' if enemy else 'Allied')+f'/Company {company}')
for idx in range(6):
    x=-2450-(idx//3)*230; y=(idx%3-1)*280
    a=spawn(rider_cls,f'Gold / Guard squad / Rider {idx+1:02d}',(x,y,height(x,y)+110))
    a.set_editor_property('unit_id',f'player_guard_{idx+1:02d}')
    a.set_editor_property('army_id','army_player'); a.set_editor_property('formation_slot',0)
    a.configure_appearance(u.LinearColor(.72,.38,.04,1),False,False,idx==0)
    a.set_folder_path('Allied/Guard squad')

# A small amount of authored cover, leaving the centre open for the charge.
rng=random.Random(23)
for i in range(28):
    x=rng.uniform(-9500,11000); y=rng.choice([-1,1])*rng.uniform(4300,10000); z=height(x,y); s=rng.uniform(1.4,3.4)
    static(f'Valley rock {i:02d}',sphere,(x,y,z+40),(s,s*.7,s*.5),mat_rock,rng.uniform(0,360),'Environment/Rocks')
    if i%3==0:
        static(f'Tree trunk {i:02d}',cylinder,(x+180,y,z+220),(.30,.30,4.2),mat_timber,folder='Environment/Trees')
        static(f'Tree canopy {i:02d}',sphere,(x+180,y,z+560),(4.4,4.1,4.8),mat_leaf,folder='Environment/Trees')

start=spawn(u.PlayerStart,'Mounted commander start',(-2450,0,height(-2450,0)+110),0); start.set_folder_path('Player')
ws=world.get_world_settings(); ws.set_editor_property('default_game_mode',u.load_class(None,'/Script/mcp.BattleGameMode'))
L.set_level_viewport_camera_info(u.Vector(-7600,-8200,5200),rot(p=-25,y=43,r=0))
assert L.save_current_level()
u.EditorAssetLibrary.save_directory('/Game/Battle',only_if_is_dirty=True,recursive=True)
u.log('BATTLEFIELD_VERTICAL_SUCCESS: non-partitioned terrain + 72 infantry + 6 mounted guards + standards')
