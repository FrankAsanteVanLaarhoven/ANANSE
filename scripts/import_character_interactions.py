"""Versioned visual/clip import onto the two existing, incompatible skeletons."""
import unreal,os,json,hashlib,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=True);report=out/'native.json';assert not report.exists();result={'status':'failed','creative_approved':False};tools=unreal.AssetToolsHelpers.get_asset_tools()
old=json.loads((R/'.local/verification/story-cast-20261015/native-Kwaku/Kwaku-native.json').read_text())
protected=[R/'Unreal/Content/Ananse/Characters/Kwaku/Story_v001',R/'Unreal/Content/Ananse/Characters/Kwaku/Refined_v002',R/'Unreal/Content/Ananse/Characters/OseboLeopard/Authored_v001']
before={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for folder in protected for p in folder.rglob('*')if p.is_file()}
def import_source(source,dest,skeleton=None,animations=True):
 assert not unreal.EditorAssetLibrary.does_directory_exist(dest)
 task=unreal.AssetImportTask()
 for k,v in dict(filename=str(source),destination_path=dest,automated=True,replace_existing=False,save=True,async_=False).items():task.set_editor_property(k,v)
 pipeline=unreal.InterchangeGenericAssetsPipeline();pipeline.set_editor_property('import_offset_rotation',unreal.Rotator(pitch=0,yaw=-90,roll=0))
 if skeleton:
  common=pipeline.get_editor_property('common_skeletal_meshes_and_animations_properties');common.set_editor_property('skeleton',skeleton);common.set_editor_property('add_curve_metadata_to_skeleton',False);pipeline.get_editor_property('mesh_pipeline').set_editor_property('update_skeleton_reference_pose',False)
 pipeline.get_editor_property('animation_pipeline').set_editor_property('import_animations',animations);options=unreal.InterchangePipelineStackOverride();options.set_editor_property('override_pipelines',[unreal.SoftObjectPath(pipeline.get_path_name())]);task.set_editor_property('options',options);tools.import_asset_tasks([task]);assets=[unreal.load_asset(p)for p in task.get_editor_property('imported_object_paths')];assert all(assets);return assets
def blueprint(name,dest,parent,properties):
 factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',parent);bp=tools.create_asset(name,dest,unreal.Blueprint,factory);unreal.BlueprintEditorLibrary.compile_blueprint(bp);cls=unreal.EditorAssetLibrary.load_blueprint_class(dest+'/'+name);cdo=unreal.get_default_object(cls)
 for k,v in properties.items():cdo.set_editor_property(k,v)
 unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp);return cls
try:
 records={}
 if os.environ.get('ANANSE_KWAKU_ONLY')=='1':records['OseboLeopard']=json.loads((R/'.local/verification/character-interactions-20261016/native-01/native.json').read_text())['characters']['OseboLeopard']
 for key,folder,oldmeshpath,oldbppath,olddefpath,revision in [('Kwaku','Authored_v016',old['mesh'],old['blueprint'],old['definition'],5),('OseboLeopard','Authored_v005','/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard','/Game/Ananse/Characters/OseboLeopard/Runtime_v001/BP_OseboLeopard.BP_OseboLeopard','/Game/Ananse/Characters/OseboLeopard/Data/DA_OseboLeopard.DA_OseboLeopard',2)]:
  if key=='OseboLeopard'and os.environ.get('ANANSE_KWAKU_ONLY')=='1':continue
  dest='/Game/Ananse/Characters/'+key+('/Interactions_v005'if key=='Kwaku'else'/Interactions_v003');source=R/'SourceArt/Characters'/key/folder;previous=unreal.load_asset(oldmeshpath);assert previous;skel=previous.get_editor_property('skeleton');prior=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(previous));assets=import_source(source/(key+'.glb'),dest,skel,False);meshes=[a for a in assets if isinstance(a,unreal.SkeletalMesh)];assert len(meshes)==1;mesh=meshes[0];assert mesh.get_editor_property('skeleton')==skel
  error=unreal.AnanseAnimationAuthoring.correct_interaction_import_frame(mesh);assert error=='ok',str(error)
  error=unreal.AnanseAnimationAuthoring.prepare_interaction_surface(mesh);assert error=='ok',str(error);assert unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem).regenerate_lod(mesh,3,True,False)

  for slot in mesh.get_editor_property('materials'):
   material=slot.get_editor_property('material_interface')
   if isinstance(material,unreal.Material):
    unreal.MaterialEditingLibrary.set_material_usage(material,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
    if key=='Kwaku':unreal.MaterialEditingLibrary.set_material_usage(material,unreal.MaterialUsage.MATUSAGE_MORPH_TARGETS)
    material.set_editor_property('two_sided',True);unreal.MaterialEditingLibrary.recompile_material(material);assert unreal.EditorAssetLibrary.save_loaded_asset(material)
  assert unreal.EditorAssetLibrary.save_loaded_asset(mesh);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh.get_editor_property('physics_asset'))
  measured=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(mesh));assert [(b['name'],b['parent_index'])for b in measured['bones']]==[(b['name'],b['parent_index'])for b in prior['bones']]
  skin_probes=[]
  if key in ['Kwaku','OseboLeopard']:
   qualified=json.loads((R/'.local/verification/character-interactions-20261016/native-03/native.json').read_text())['characters']['Kwaku']['clips'][8]if key=='Kwaku'else list(unreal.load_asset(olddefpath).get_editor_property('clips'))[0].get_path_name();probe_clip=unreal.load_asset(qualified)
   import re,math
   for expected in json.loads((source/'skin-probes.json').read_text())['probes']:
    probe=json.loads(unreal.AnanseAnimationAuthoring.describe_skin_probe(mesh,probe_clip,unreal.Vector(*expected['rest_native']),1.2 if key=='Kwaku'else 0.));assert probe['rest_distance_cm']<.01,probe
    assert {a['bone']for a in probe['influences']}==set(expected['weights']),probe
    point=[float(v)for v in re.findall(r'[XYZ]=(-?[0-9.]+)',probe['skinned_position'])];assert len(point)==3 and all(math.isfinite(v)for v in point)
    if key=='Kwaku':assert math.dist(point,expected['held_native'])<.1,(point,expected)
    skin_probes.append(probe)
  for current,previous_bone in zip(measured['bones'],prior['bones']):
   for field in ['local_translation_cm','scale']:assert max(abs(a-b)for a,b in zip(current[field],previous_bone[field]))<1e-4,(key,current['name'],field)
   a=current['local_rotation_xyzw'];b=previous_bone['local_rotation_xyzw'];assert min(max(abs(x-y)for x,y in zip(a,b)),max(abs(x+y)for x,y in zip(a,b)))<1e-4,(key,current['name'],'rotation')
  olddef=unreal.load_asset(olddefpath);assert olddef;clips=list(olddef.get_editor_property('clips'));properties={'authored_mesh'if key=='Kwaku'else'leopard_mesh':mesh};props=[]
  if key=='Kwaku':
   qualified=json.loads((R/'.local/verification/character-interactions-20261016/native-03/native.json').read_text())['characters']['Kwaku']['clips'][8];clips[8]=unreal.load_asset(qualified);assert clips[8]and clips[8].get_editor_property('skeleton')==skel
   prop_assets=import_source(source/'Ledger.glb',dest+'/Props',None,False);props=[a for a in prop_assets if isinstance(a,unreal.StaticMesh)];assert len(props)==1
   properties.update(authored_clips=clips,refined_face=True,ledger_presentation=True,ledger_mesh=props[0])
  parent=unreal.EditorAssetLibrary.load_blueprint_class(oldbppath.split('.')[0]);assert parent,oldbppath;cls=blueprint('BP_'+key,dest,parent,properties)
  factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.AnanseCharacterDefinition);definition=tools.create_asset('DA_'+key,dest,unreal.AnanseCharacterDefinition,factory)
  for k in ['design_id','character_identity','skeleton_key','engineering_fixture']:definition.set_editor_property(k,olddef.get_editor_property(k))
  for k,v in dict(revision=revision,pawn_class=cls,mesh=mesh,clips=clips).items():definition.set_editor_property(k,v)
  assert unreal.EditorAssetLibrary.save_loaded_asset(definition)
  modes={}
  if key=='Kwaku':
   story=blueprint('BP_KwakuEpisodeInteractions',dest,cls,{'story_campaign_presentation':True})
   for label,parent,pawn in [('Lab',unreal.AnanseCharacterLabMode,cls),('Episode',unreal.AnanseGameMode,story)]:modes[label]=blueprint('BP_Kwaku'+label+'InteractionsMode',dest,parent,{'default_pawn_class':pawn}).get_path_name()
  records[key]={'mesh':mesh.get_path_name(),'skeleton':skel.get_path_name(),'physics':mesh.get_editor_property('physics_asset').get_path_name(),'blueprint':cls.get_path_name(),'definition':definition.get_path_name(),'revision':revision,'clips':[a.get_path_name()for a in clips],'props':[a.get_path_name()for a in props],'modes':modes,'native':measured,'source_scene_sha256':hashlib.sha256((source/(key+'.blend')).read_bytes()).hexdigest(),'source_glb_sha256':hashlib.sha256((source/(key+'.glb')).read_bytes()).hexdigest(),'source_native_skin_probes':skin_probes,'mesh_import_yaw_degrees':-90,'mesh_description_correction_yaw_degrees':90,'retained_animation_import_yaw_degrees':-90}
 assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in before.items())
 result.update(status='saved_reopen_pending_runtime_creative_review',characters=records,protected_originals_unchanged=True)
except Exception:result['exception']=traceback.format_exc();raise
finally:report.write_text(json.dumps(result,indent=2)+'\n')
