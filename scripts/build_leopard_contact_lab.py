"""Create bounded feline fixtures without altering the accepted character labs."""
import json,os
from pathlib import Path
import unreal
dest='/Game/Ananse/Maps/CharacterLabs/LeopardContact_v001/L_LeopardContactLab'
out=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'contact-lab.json'
if out.exists() or unreal.EditorAssetLibrary.does_asset_exist(dest):raise RuntimeError('Preserve existing evidence/level')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.new_level(dest)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);cube=unreal.load_asset('/Engine/BasicShapes/Cube')
def box(name,pos,scale,role,rotation=None):
 a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos),rotation or unreal.Rotator());a.set_actor_label(name)
 a.static_mesh_component.set_static_mesh(cube);a.set_actor_scale3d(unreal.Vector(*scale));a.set_editor_property('tags',[unreal.Name('AnanseFixture:'+role)]);return a
box('Flat catch floor',(0,1000,-50),(40,40,1),'flat')
box('15 degree feline ramp',(0,400,50),(3,4,.1),'ramp',unreal.Rotator(pitch=15))
for i in range(4):box('10cm step '+str(i),(-90+60*i,800,5*(i+1)),(.6,4,.1*(i+1)),'steps')
for i,height in enumerate([5,10,15]):box('Uneven '+str(height)+'cm',(-90+90*i,1200,height/2),(.9,4,height/100),'uneven')
for y,role in [(1600,'moving'),(2000,'disappearing')]:
 a=actors.spawn_actor_from_class(unreal.AnanseContactSupport,unreal.Vector(0,y,30));a.set_actor_scale3d(unreal.Vector(4,4,.2));a.set_editor_property('tags',[unreal.Name('AnanseFixture:'+role)])
 if role=='disappearing':
  a.set_editor_property('bDisappearing',True);box('20cm safety catch',(0,y,10),(4,4,.2),'flat')
actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(-140,0,110))
sun=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,1000),unreal.Rotator(pitch=-45,yaw=-30));sun.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
sky=actors.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,800));sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
mode=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Ananse/Characters/OseboLeopard/Runtime_v001/BP_OseboLeopardLabMode');assert mode
world.get_world_settings().set_editor_property('default_game_mode',mode);assert levels.save_current_level()
out.write_text(json.dumps(dict(map=dest,role='development qualification fixtures',speed_cm_s=45,ramp_degrees=15,step_cm=10,uneven_cm=[5,10,15],moving_amplitude_cm=25,disappearing_drop_cm=20,status='saved_not_executed'),indent=2)+'\n')
