"""New map revisions: replace presentation while retaining original gameplay roots."""
import unreal, json, os, hashlib, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=True);report=out/'scenery.json';assert not report.exists();section=os.environ['ANANSE_FORMS_SECTION'];source=ROOT/'SourceArt/Environments/MarketSanctuary/Forms_v002';contract=json.loads((source/'source-status.json').read_text());native=json.loads((ROOT/'.local/verification/forms-scenery-20261015/native-01/native.json').read_text());dest='/Game/Ananse/Environments/Forms_v002';tools=unreal.AssetToolsHelpers.get_asset_tools();meshes={};result={'status':'failed','creative_approved':False}
try:
 for item in contract['exports']:
  path=dest+'/'+item['group']+'/'+item['group']
  if not unreal.EditorAssetLibrary.does_asset_exist(path):
   task=unreal.AssetImportTask()
   for k,v in dict(filename=str(source/item['file']),destination_path=dest+'/'+item['group'],automated=True,replace_existing=False,save=True,async_=False).items():task.set_editor_property(k,v)
   pipeline=unreal.InterchangeGenericAssetsPipeline();pipeline.set_editor_property('import_offset_rotation',unreal.Rotator());override=unreal.InterchangePipelineStackOverride();override.set_editor_property('override_pipelines',[unreal.SoftObjectPath(pipeline.get_path_name())]);task.set_editor_property('options',override);tools.import_asset_tasks([task]);assets=[unreal.load_asset(p)for p in task.get_editor_property('imported_object_paths')];found=[a for a in assets if isinstance(a,unreal.StaticMesh)];assert len(found)==1;mesh=found[0]
   for a in assets:
    if isinstance(a,unreal.Material):a.set_editor_property('two_sided',True);unreal.MaterialEditingLibrary.recompile_material(a);assert unreal.EditorAssetLibrary.save_loaded_asset(a)
  else:mesh=unreal.load_asset(path)
  assert isinstance(mesh,unreal.StaticMesh);meshes[item['group']]=mesh
 config={'market-lab':('L_Market_PresentationRefined','L_Market_PresentationForms','Lab'),'market-episode':('L_Market_EpisodeRefined','L_Market_EpisodeForms','Episode'),'sanctuary-episode':('L_Sanctuary_EpisodeRefined','L_Sanctuary_EpisodeForms','Episode')}
 old,name,mode=config[section];path='/Game/Ananse/Maps/Refinement_v007/'+name;assert not unreal.EditorAssetLibrary.does_asset_exist(path)
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert levels.new_level_from_template(path,'/Game/Ananse/Maps/Refinement_v003/'+old)
 def frame(a):
  p=a.get_actor_location();r=a.get_actor_rotation();z=a.get_actor_scale3d();return [p.x,p.y,p.z,r.pitch,r.yaw,r.roll,z.x,z.y,z.z]
 original=list(actors.get_all_level_actors());before={a.get_path_name():{'transform':frame(a),'action':str(a.get_editor_property('action'))if isinstance(a,unreal.AnanseInteractable)else None,'character':str(a.get_editor_property('character_id'))if isinstance(a,unreal.AnanseInteractable)else None}for a in original};replacements=[]
 for actor in original:
  label=actor.get_actor_label()
  if isinstance(actor,unreal.StaticMeshActor):
   component=actor.static_mesh_component;mesh=component.get_editor_property('static_mesh');group=contract['wall_map'].get(label)
   if label=='Web anchor visible marker':group='WebAnchor'
   if mesh and 'SanctuaryFoliage' in mesh.get_path_name():group='SanctuaryLeaves'
   if group:
    visual=actors.spawn_actor_from_class(unreal.StaticMeshActor,actor.get_actor_location(),actor.get_actor_rotation());visual.set_actor_label('Authored replacement '+group+' WIP');visual.static_mesh_component.set_static_mesh(meshes[group]);visual.static_mesh_component.set_collision_profile_name('NoCollision');component.set_visibility(False,False)
    # Existing textured surfaces are reused on new masonry/wood where applicable.
    for i in range(visual.static_mesh_component.get_num_materials()):
     material=visual.static_mesh_component.get_material(i);key=next((key for key in ['WeatheredWood','WarmPlaster']if material and key in material.get_name()),None)
     if key:visual.static_mesh_component.set_material(i,unreal.load_asset('/Game/Ananse/Environments/Refinement_v002/M_'+key))
    replacements.append({'kind':'static','label':label,'mesh':meshes[group].get_path_name(),'collision':'original actor retained; visual NoCollision'})
  if isinstance(actor,unreal.AnanseInteractable):
   identity=str(actor.get_editor_property('character_id'));action=str(actor.get_editor_property('action'));key={'aso-yaa':'AsoYaa','esi':'EsiHuman'}.get(identity)
   if key:
    family=json.loads((ROOT/'.local/verification/story-cast-20261015'/('native-'+key)/(key+'-native.json')).read_text());mesh=unreal.load_asset(family['mesh']);idle=unreal.load_asset(next(iter(family['clips'].values())));assert isinstance(idle,unreal.AnimSequence)
    component=actor.get_editor_property('character_visual');component.set_skeletal_mesh_asset(mesh);component.set_editor_property('relative_location',unreal.Vector(0,0,-actor.get_actor_location().z));component.set_editor_property('relative_rotation',unreal.Rotator(0,180,0));actor.set_editor_property('presentation_idle',idle);actor.get_editor_property('label').set_editor_property('relative_location',unreal.Vector(0,0,200));replacements.append({'kind':'existing-human-NPC','identity':identity,'mesh':mesh.get_path_name(),'idle':idle.get_path_name()})
   else:
    group='StoryStone'if section=='sanctuary-episode'else'LedgerStand'if action=='ledger'else'NoticeStand';actor.get_editor_property('prop_visual').set_static_mesh(meshes[group]);replacements.append({'kind':'prop','action':action,'identity':identity,'mesh':meshes[group].get_path_name()})
 for actor in original:
  prior=before[actor.get_path_name()];assert frame(actor)==prior['transform']
  if isinstance(actor,unreal.AnanseInteractable):assert str(actor.get_editor_property('action'))==prior['action']and str(actor.get_editor_property('character_id'))==prior['character'];assert actor.get_editor_property('mesh').get_collision_enabled()!=unreal.CollisionEnabled.NO_COLLISION
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',unreal.load_class(None,native['modes'][mode]));assert levels.save_current_level();result.update(status='saved_pending_rendered_gameplay_review',map=path,template='/Game/Ananse/Maps/Refinement_v003/'+old,replacements=replacements,meshes={k:v.get_path_name()for k,v in meshes.items()},original_transforms_actions_identities_unchanged=True,old_maps_unchanged=True,remaining='Anonymous watchman stays a labelled blockout; final art/audio/navigation/mobile remain open')
except Exception:result['exception']=traceback.format_exc();raise
finally:report.write_text(json.dumps(result,indent=2)+'\n')
