"""New controlled contact fixtures; existing imported assets/maps are never rewritten."""
from pathlib import Path
import os,json
import unreal
report=Path(os.environ['ANANSE_CONTACT_LAB_REPORT']);dest='/Game/Characters/AnanseSpider/ContactLab_v006/L_AnanseContactLab'
if report.exists() or unreal.EditorAssetLibrary.does_asset_exist(dest):raise RuntimeError('Fresh map/report required')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.new_level(dest)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);cube=unreal.load_asset('/Engine/BasicShapes/Cube.Cube')
def box(label,pos,scale,rotation=None):
 a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos),rotation or unreal.Rotator());a.set_actor_label(label);a.static_mesh_component.set_static_mesh(cube);a.set_actor_scale3d(unreal.Vector(*scale));role='flat' if label=='Flat support' else 'ramp' if label.startswith('15degree') else 'steps' if label.startswith('20cm') else 'uneven' if label.startswith('Uneven') else 'access_ramp' if label.startswith('Moving support access') else 'landing';a.set_editor_property('tags',[unreal.Name('AnanseFixture:'+role)]);return a
box('Flat support', (0,0,-50),(40,40,1))
box('15degree ramp 400cm long',(450,0,50),(4,4,.2),unreal.Rotator(pitch=15,yaw=0,roll=0))
box('Ramp landing',(800,0,110),(3,4,.2))
for i in range(5):box('20cm step '+str(i+1),(0,500+100*i,10*(i+1)),(4,1,.2*(i+1)))
for i in range(4):box('Uneven 10-20cm patch '+str(i),(-500,500+100*i,5+2.5*i),(4,1,.1+.05*i))
box('Moving support access ramp',(-900,200,50),(4,4,.2),unreal.Rotator(pitch=15,yaw=90,roll=0))
a=actors.spawn_actor_from_class(unreal.AnanseContactSupport,unreal.Vector(-900,500,110));a.set_actor_scale3d(unreal.Vector(4,2,.2));a.set_editor_property('tags',[unreal.Name('AnanseFixture:moving')])
box('Disappearing support safety catch',(-900,750,90),(4,3,.2))
a=actors.spawn_actor_from_class(unreal.AnanseContactSupport,unreal.Vector(-900,750,110));a.set_actor_scale3d(unreal.Vector(4,3,.2));a.set_editor_property('tags',[unreal.Name('AnanseFixture:disappearing')]);a.set_editor_property('bDisappearing',True);assert a.get_editor_property('bDisappearing')
actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(0,0,110))
light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,1000),unreal.Rotator(pitch=-45,yaw=-30,roll=0));light.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
actors.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,900)).light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',unreal.AnanseCharacterLabMode)
assert levels.save_current_level();report.write_text(json.dumps({'map':dest,'status':'SAVED_NOT_QUALIFIED','fixtures':{'flat':True,'ramp_degrees':15,'step_height_cm':20,'uneven_cm':[10,15,20,25]},'actor_count':len(actors.get_all_level_actors())},indent=2)+'\n')
