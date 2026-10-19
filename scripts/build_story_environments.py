"""Import actual authored environment bytes into new maps; original maps preserved."""
import unreal,os,json,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=Path(os.environ['ANANSE_EVIDENCE_DIR']);OUT.mkdir(parents=True,exist_ok=True);report=OUT/'environments-native.json'
if report.exists():raise RuntimeError('Preserve evidence')
source=ROOT/'SourceArt/Environments/MarketSanctuary/Authored_v001';contract=json.loads((source/'source-status.json').read_text());dest='/Game/Ananse/Environments/Story_v001'
if unreal.EditorAssetLibrary.does_directory_exist(dest):raise RuntimeError('Preserve native source revision')
r={'status':'failed','creative_approved':False,'campaign_maps_changed':False}
try:
 tools=unreal.AssetToolsHelpers.get_asset_tools();meshes={}
 for item in contract['exports']:
  task=unreal.AssetImportTask()
  for k,v in dict(filename=str(source/item['file']),destination_path=dest+'/'+item['group'],automated=True,replace_existing=False,save=True,async_=False).items():task.set_editor_property(k,v)
  pipeline=unreal.InterchangeGenericAssetsPipeline();pipeline.set_editor_property('import_offset_rotation',unreal.Rotator(pitch=0,yaw=0,roll=0));options=unreal.InterchangePipelineStackOverride();options.set_editor_property('override_pipelines',[unreal.SoftObjectPath(pipeline.get_path_name())]);task.set_editor_property('options',options)
  tools.import_asset_tasks([task]);assets=[unreal.load_asset(p)for p in task.get_editor_property('imported_object_paths')];found=[a for a in assets if isinstance(a,unreal.StaticMesh)];assert len(found)==1;meshes[item['group']]=found[0]
  for a in assets:
   if isinstance(a,unreal.Material):a.set_editor_property('two_sided',True);unreal.MaterialEditingLibrary.recompile_material(a);unreal.EditorAssetLibrary.save_loaded_asset(a)
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);maps=[]
 for market in [True,False]:
  path='/Game/Ananse/Maps/Story_v001/'+('L_Market_Authored' if market else 'L_Sanctuary_Authored')
  assert levels.new_level(path)
  floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-50));floor.set_actor_label('Stable gameplay floor; decorative mesh collision disabled');floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(50,40,1) if market else unreal.Vector(24,24,1))
  for group,mesh in meshes.items():
   if market==group.startswith('Sanctuary'):continue
   a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));a.set_actor_label('Authored '+group+' WIP');a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_profile_name('NoCollision')
  actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(-900,-350,160) if market else unreal.Vector(0,-400,160),unreal.Rotator())
  light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,1400),unreal.Rotator(-32,-30,0));light.light_component.set_mobility(unreal.ComponentMobility.MOVABLE);light.light_component.set_editor_property('intensity',3.0);light.light_component.set_editor_property('light_color',unreal.Color(255,221,180,255))
  sky=actors.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,1200));sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE);sky.light_component.set_editor_property('intensity',.7)
  world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',unreal.AnanseCharacterLabMode);assert levels.save_current_level();maps.append(path)
 r.update(status='saved_pending_reopen_render_and_collision_review',meshes={k:m.get_path_name()for k,m in meshes.items()},maps=maps,collision_policy='Decorative authored modules NoCollision. Stable floor authority. Route/collision integration pending; no campaign geometry replaced.',lighting='Dynamic warm sun and sky; no baked/mobile qualification')
except Exception:r['exception']=traceback.format_exc();raise
finally:report.write_text(json.dumps(r,indent=2)+'\n')
