"""Static art crossing: visible and collidable together, no mission-state changes."""
import unreal,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);src=R/'SourceArt/Environments/MarketSanctuary/Crossing_v001';tools=unreal.AssetToolsHelpers.get_asset_tools();sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);meshes={};rows=[]
for name in ['GoldenWebCrossing','SanctuaryStream']:
 task=unreal.AssetImportTask()
 for k,v in dict(filename=str(src/(name+'.glb')),destination_path='/Game/Ananse/Environments/Crossing_v001/'+name,automated=True,replace_existing=False,save=True,async_=False).items():task.set_editor_property(k,v)
 p=unreal.InterchangeGenericAssetsPipeline();p.set_editor_property('import_offset_rotation',unreal.Rotator());o=unreal.InterchangePipelineStackOverride();o.set_editor_property('override_pipelines',[unreal.SoftObjectPath(p.get_path_name())]);task.set_editor_property('options',o);tools.import_asset_tasks([task]);found=[unreal.load_asset(p)for p in task.get_editor_property('imported_object_paths')];mesh=next(m for m in found if isinstance(m,unreal.StaticMesh));opts=unreal.StaticMeshReductionOptions();opts.set_editor_property('auto_compute_lod_screen_size',False);settings=[]
 for percent,screen in [(1.,1.),(.5,.4),(.25,.15)]:
  a=unreal.StaticMeshReductionSettings();a.set_editor_property('percent_triangles',percent);a.set_editor_property('screen_size',screen);settings.append(a)
 opts.set_editor_property('reduction_settings',settings);sm.set_lods(mesh,opts);n=mesh.get_editor_property('nanite_settings');n.set_editor_property('enabled',False);mesh.set_editor_property('nanite_settings',n);sm.set_generate_lightmap_uv(mesh,True);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh);meshes[name]=mesh;rows.append({'mesh':mesh.get_path_name(),'lod_triangles':[mesh.get_num_triangles(i)for i in range(3)]})
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);path='/Game/Ananse/Maps/EnvironmentRoute_v002/L_StoryForest_Route';assert levels.load_level(path)
for name in meshes:
 a=actors.spawn_actor_from_class(unreal.AnanseEnvironmentCluster,unreal.Vector(350,-200,0));a.set_actor_label('Route '+name);c=a.get_editor_property('instances');c.set_static_mesh(meshes[name]);c.add_instance(unreal.Transform());c.set_collision_profile_name('NoCollision')
# Low bridge deck; top 16cm, below the existing character step height. Side rails simple boxes.
for x in [-66,0,66]:
 a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(350+x,-200,8));a.set_actor_label('Route collision web deck');a.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));a.set_actor_scale3d(unreal.Vector(.66,1.2,.16));a.static_mesh_component.set_collision_profile_name('BlockAll');a.static_mesh_component.set_visibility(False,False);a.static_mesh_component.set_editor_property('cast_shadow',False);a.set_actor_hidden_in_game(True)
for y in [-62,62]:
 a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(350,-200+y,48));a.set_actor_label('Route collision web rail');a.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));a.set_actor_scale3d(unreal.Vector(2,.04,.8));a.static_mesh_component.set_collision_profile_name('BlockAll');a.static_mesh_component.set_visibility(False,False);a.static_mesh_component.set_editor_property('cast_shadow',False);a.set_actor_hidden_in_game(True)
assert levels.save_current_level();(out/'crossing.json').write_text(json.dumps({'map':path,'meshes':rows,'visual_and_collision_state':'Always on together in this static map; no dynamic mission/ability binding','deck_height_cm':16,'stream':'Opaque shallow surface above preserved floor; no water simulation or new route unlock','creative':'REVIEW_REQUIRED'},indent=2)+'\n')
