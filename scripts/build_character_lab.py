"""Build a new isolated engineering Character Lab, preserving campaign maps."""
from pathlib import Path
import os,json
import unreal
report=Path(os.environ['ANANSE_LAB_REPORT']);map_path='/Game/Characters/AnanseSpider/Lab_v001/L_AnanseCharacterLab'
if report.exists() or unreal.EditorAssetLibrary.does_asset_exist(map_path):raise RuntimeError('Lab/report exists; no overwrite.')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.new_level(map_path)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);cube=unreal.load_asset('/Engine/BasicShapes/Cube.Cube')
floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-50));floor.set_actor_label('Character Lab floor');floor.set_actor_scale3d(unreal.Vector(40,40,1));floor.static_mesh_component.set_static_mesh(cube)
ramp=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(900,0,80),unreal.Rotator(0,0,15));ramp.set_actor_label('15 degree test ramp NOT CONTACT QUALIFIED');ramp.set_actor_scale3d(unreal.Vector(8,4,.2));ramp.static_mesh_component.set_static_mesh(cube)
actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(0,0,110))
light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,1000),unreal.Rotator(-45,-30,0));light.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
actors.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,900)).light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',unreal.AnanseCharacterLabMode)
assert levels.save_current_level();report.write_text(json.dumps({'map':map_path,'status':'SAVED_NOT_RENDERED','game_mode':'AnanseCharacterLabMode','character':'ananse','quality':'ENGINEERING_PROXY','actor_count':len(actors.get_all_level_actors())},indent=2)+'\n')
