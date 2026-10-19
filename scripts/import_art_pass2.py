"""New unpublished visual assets on the two existing skeletons and retained clips."""
import unreal,json,os,hashlib,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);result={'status':'failed'};tools=unreal.AssetToolsHelpers.get_asset_tools();module=(R/'scripts/import_character_interactions.py').read_text();scope={};exec(module[module.index('def import_source'):module.index('try:\n records=')],{'unreal':unreal,'tools':tools},scope);prior=json.loads((R/'.local/verification/visual-acceptance-20261016/native-07/native.json').read_text())['characters']
try:
 rows={}
 for key,rev,num in [('Kwaku','Authored_v035',11),('OseboLeopard','Authored_v021',7)]:
  old=prior[key];skel=unreal.load_asset(old['skeleton']);source=R/'SourceArt/Characters'/key/rev;dest='/Game/Ananse/Characters/'+key+'/ArtPass2_v003';assets=scope['import_source'](source/(key+'.glb'),dest,skel,False);meshes=[a for a in assets if isinstance(a,unreal.SkeletalMesh)];assert len(meshes)==1;mesh=meshes[0];assert unreal.AnanseAnimationAuthoring.correct_interaction_import_frame(mesh)=='ok';assert unreal.AnanseAnimationAuthoring.prepare_interaction_surface(mesh)=='ok';assert unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem).regenerate_lod(mesh,3,True,False)
  for slot in mesh.get_editor_property('materials'):
   material=slot.get_editor_property('material_interface')
   if isinstance(material,unreal.Material):
    for usage in [unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH,unreal.MaterialUsage.MATUSAGE_MORPH_TARGETS]:unreal.MaterialEditingLibrary.set_material_usage(material,usage)
    material.set_editor_property('two_sided',True);unreal.MaterialEditingLibrary.recompile_material(material);assert unreal.EditorAssetLibrary.save_loaded_asset(material)
  mesh.set_editor_property('physics_asset',unreal.load_asset(old['physics']));assert unreal.EditorAssetLibrary.save_loaded_asset(mesh);definition_old=unreal.load_asset(old['definition']);clips=list(definition_old.get_editor_property('clips'));properties={'authored_mesh'if key=='Kwaku'else'leopard_mesh':mesh,'authored_clips'if key=='Kwaku'else'leopard_clips':clips};cls=scope['blueprint']('BP_'+key,dest,unreal.load_class(None,old['blueprint']),properties);factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.AnanseCharacterDefinition);definition=tools.create_asset('DA_'+key,dest,unreal.AnanseCharacterDefinition,factory)
  for field in ['design_id','character_identity','skeleton_key','engineering_fixture']:definition.set_editor_property(field,definition_old.get_editor_property(field))
  for n,v in dict(revision=num,pawn_class=cls,mesh=mesh,clips=clips).items():definition.set_editor_property(n,v)
  assert unreal.EditorAssetLibrary.save_loaded_asset(definition);rig=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(mesh));before=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(unreal.load_asset(old['mesh'])));assert rig['bones']==before['bones'];assert len(rig['morph_targets'])>=12
  rows[key]={'mesh':mesh.get_path_name(),'skeleton':skel.get_path_name(),'physics':mesh.get_editor_property('physics_asset').get_path_name(),'blueprint':cls.get_path_name(),'definition':definition.get_path_name(),'revision':num,'clips':[c.get_path_name()for c in clips],'rig':rig,'source':str(source.relative_to(R)),'source_scene_sha256':hashlib.sha256((source/(key+'.blend')).read_bytes()).hexdigest(),'source_glb_sha256':hashlib.sha256((source/(key+'.glb')).read_bytes()).hexdigest()}
 result.update(status='saved_pending_reopen_and_runtime',characters=rows,creative_approved=False)
except Exception:result['exception']=traceback.format_exc();raise
finally:(out/'native.json').write_text(json.dumps(result,indent=2)+'\n')
