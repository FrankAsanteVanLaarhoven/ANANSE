"""Opt-in review definitions; no publication or canonical identity migration."""
import unreal,os,json,hashlib,traceback,math,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=True);report=out/'native.json';assert not report.exists();result={'status':'failed','creative_approved':False};tools=unreal.AssetToolsHelpers.get_asset_tools()
# Reuse the exact qualified import and Blueprint preparation functions, not a new importer.
module=(R/'scripts/import_character_interactions.py').read_text();scope={};exec(module[module.index('def import_source'):module.index('try:\n records=')],{'unreal':unreal,'tools':tools},scope);import_source=scope['import_source'];blueprint=scope['blueprint']
# Functions resolve their shared globals through the supplied import scope.
protected=json.loads((R/'.local/verification/visual-acceptance-20261016/protected.json').read_text())
prior=json.loads((R/'.local/verification/character-interactions-20261016/native-05/native.json').read_text())['characters']
try:
 records={}
 for key,revision,number in [('Kwaku','Authored_v028',8),('OseboLeopard','Authored_v012',5)]:
  old=prior[key];previous=unreal.load_asset(old['mesh']);olddef=unreal.load_asset(old['definition']);skeleton=previous.get_editor_property('skeleton');before=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(previous));dest='/Game/Ananse/Characters/'+key+'/Visual_v003';source=R/'SourceArt/Characters'/key/revision;continued=unreal.EditorAssetLibrary.does_directory_exist(dest);assets=([unreal.load_asset(n)for n in unreal.EditorAssetLibrary.list_assets(dest,recursive=True,include_folder=False)]if continued else import_source((source/'NativeImport/Kwaku.glb')if key=='Kwaku'else source/(key+'.glb'),dest,skeleton,key=='Kwaku'));meshes=[a for a in assets if isinstance(a,unreal.SkeletalMesh)];assert len(meshes)==1;mesh=meshes[0];
  if continued:assert json.loads(unreal.AnanseAnimationAuthoring.describe_rig(mesh))['lod_count']==3
  else:
   assert unreal.AnanseAnimationAuthoring.correct_interaction_import_frame(mesh)=='ok';assert unreal.AnanseAnimationAuthoring.prepare_interaction_surface(mesh)=='ok';assert unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem).regenerate_lod(mesh,3,True,False)
  for slot in mesh.get_editor_property('materials'):
   material=slot.get_editor_property('material_interface')
   if isinstance(material,unreal.Material):
    unreal.MaterialEditingLibrary.set_material_usage(material,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH);unreal.MaterialEditingLibrary.set_material_usage(material,unreal.MaterialUsage.MATUSAGE_MORPH_TARGETS);material.set_editor_property('two_sided',True);unreal.MaterialEditingLibrary.recompile_material(material);assert unreal.EditorAssetLibrary.save_loaded_asset(material)
  assert unreal.EditorAssetLibrary.save_loaded_asset(mesh);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh.get_editor_property('physics_asset'));after=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(mesh));assert len(after['bones'])==len(before['bones'])
  for a,b in zip(after['bones'],before['bones']):
   assert a['name']==b['name']and a['parent_index']==b['parent_index']
   for field in ['local_translation_cm','scale']:assert max(abs(x-y)for x,y in zip(a[field],b[field]))<1e-4
   assert min(max(abs(x-y)for x,y in zip(a['local_rotation_xyzw'],b['local_rotation_xyzw'])),max(abs(x+y)for x,y in zip(a['local_rotation_xyzw'],b['local_rotation_xyzw'])))<1e-4
  clips=list(olddef.get_editor_property('clips'));
  if key=='Kwaku':
   newclips=[a for a in assets if isinstance(a,unreal.AnimSequence)];assert len(newclips)==1;clips[8]=newclips[0]
  parent=unreal.load_class(None,old['blueprint']);properties={'authored_mesh'if key=='Kwaku'else'leopard_mesh':mesh};
  if key=='Kwaku':properties['authored_clips']=clips
  cls=blueprint('BP_'+key,dest,parent,properties);factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.AnanseCharacterDefinition);definition=tools.create_asset('DA_'+key,dest,unreal.AnanseCharacterDefinition,factory)
  for name in ['design_id','character_identity','skeleton_key','engineering_fixture']:definition.set_editor_property(name,olddef.get_editor_property(name))
  for name,value in dict(revision=number,pawn_class=cls,mesh=mesh,clips=clips).items():definition.set_editor_property(name,value)
  assert unreal.EditorAssetLibrary.save_loaded_asset(definition);records[key]={'mesh':mesh.get_path_name(),'definition':definition.get_path_name(),'blueprint':cls.get_path_name(),'skeleton':skeleton.get_path_name(),'physics':mesh.get_editor_property('physics_asset').get_path_name(),'clips':[a.get_path_name()for a in clips],'revision':number,'rig':after,'source':str(source.relative_to(R)),'source_scene_sha256':hashlib.sha256((source/(key+'.blend')).read_bytes()).hexdigest()}
 assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in protected.items());result.update(status='saved_pending_runtime_visual_rejection_review',characters=records,protected_unchanged=True)
except Exception:result['exception']=traceback.format_exc();raise
finally:report.write_text(json.dumps(result,indent=2)+'\n')
