"""Import masked scenery variants and compile bounded wind/water WPO materials."""
import unreal,json,os,hashlib,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[1];src=R/'SourceArt/Environments/MarketSanctuary/Motion_v001';out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);dest='/Game/Ananse/Environments/Motion_v001';M=unreal.MaterialEditingLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools();sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);cache={};records=[]
def motion_material(old):
 key=old.get_path_name()
 if key in cache:return cache[key]
 name='M_'+old.get_name()+'_'+hashlib.sha256(key.encode()).hexdigest()[:8];path=dest+'/Surface/'+name;# Resume only this task-owned revision after a preserved failed import.
 if unreal.EditorAssetLibrary.does_asset_exist(path):
  mat=unreal.load_asset(path);cache[key]=mat;return mat
 mat=tools.duplicate_asset(name,dest+'/Surface',old);assert isinstance(mat,unreal.Material),key
 custom=M.create_material_expression(mat,unreal.MaterialExpressionCustom,0,600);custom.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
 custom.set_editor_property('description','Bounded visual wind and water, anchored by authored RGBA masks; centimetres')
 custom.set_editor_property('code','''float slow=sin(T*1.4+P.x*.0017+P.y*.0011);
float fast=sin(T*5.3+P.x*.018+P.y*.011);
float gust=.7+.3*sin(T*.37+P.x*.0003);
float sway=(C.r*2.0*slow+C.g*.7*fast+A*1.2*slow)*gust;
return float3(sway,sway*.38,C.b*.6*(sin(T*1.8+P.x*.022+P.y*.014)+.25*sin(T*3.1+P.y*.04))+C.g*.22*fast);''')
 inputs=[]
 for name,cls,output in [('C',unreal.MaterialExpressionVertexColor,''),('T',unreal.MaterialExpressionTime,''),('P',unreal.MaterialExpressionWorldPosition,''),('A',unreal.MaterialExpressionVertexColor,'A')]:
  i=unreal.CustomInput();i.set_editor_property('input_name',name);inputs.append(i)
 custom.set_editor_property('inputs',inputs)
 for name,cls,output in [('C',unreal.MaterialExpressionVertexColor,''),('T',unreal.MaterialExpressionTime,''),('P',unreal.MaterialExpressionWorldPosition,''),('A',unreal.MaterialExpressionVertexColor,'A')]:
  node=M.create_material_expression(mat,cls,-300,600);assert M.connect_material_expressions(node,output,custom,name),(name,output)
 assert M.connect_material_property(custom,'',unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
 M.set_material_usage(mat,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);M.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat);cache[key]=mat;return mat
try:
 for row in json.loads((src/'source-status.json').read_text())['exports']:
  name=row['name'];original=unreal.load_asset('/Game/Ananse/Environments/'+row['source_version']+'/'+name+'/'+name);assert isinstance(original,unreal.StaticMesh),name
  existing=unreal.load_asset(dest+'/'+name+'/'+name) if unreal.EditorAssetLibrary.does_asset_exist(dest+'/'+name+'/'+name) else None
  assert not existing or os.environ.get('ANANSE_RESUME_MOTION_DRAFT')=='1','Existing motion revision preserved; explicitly resume only this task-owned draft'
  task=unreal.AssetImportTask()
  for k,v in dict(filename=str(src/(name+'.glb')),destination_path=dest+'/'+name,automated=True,save=True,replace_existing=True,async_=False).items():task.set_editor_property(k,v)
  pipe=unreal.InterchangeGenericAssetsPipeline();pipe.set_editor_property('import_offset_rotation',unreal.Rotator());override=unreal.InterchangePipelineStackOverride();override.set_editor_property('override_pipelines',[unreal.SoftObjectPath(pipe.get_path_name())]);task.set_editor_property('options',override)
  tools.import_asset_tasks([task])
  mesh=next(unreal.load_asset(p)for p in task.get_editor_property('imported_object_paths')if isinstance(unreal.load_asset(p),unreal.StaticMesh))
  slots=[]
  for i,s in enumerate(mesh.get_editor_property('static_materials')):
   imported=mesh.get_material(i).get_name();matches=[original.get_material(j)for j in range(len(original.get_editor_property('static_materials')))if str(original.get_editor_property('static_materials')[j].material_slot_name)==str(s.material_slot_name)]
   if not matches:
    matches=[original.get_material(j)for j in range(len(original.get_editor_property('static_materials')))if original.get_material(j).get_name().removeprefix('M_')==imported]
   assert len(matches)==1,(name,imported,[(str(t.material_slot_name),str(t.material_slot_name))for t in original.get_editor_property('static_materials')]);old=matches[0]
   # Rigid materials retain the original graph and do not pay WPO shader cost.
   moving=any(s in imported.lower()for s in ['bark','leaf','water','indigo','jade'])
   new=motion_material(old)if moving else old;mesh.set_material(i,new);slots.append({'index':i,'old':old.get_path_name(),'new':new.get_path_name(),'wpo':moving})
  opt=unreal.StaticMeshReductionOptions();opt.set_editor_property('auto_compute_lod_screen_size',False);settings=[]
  for percent,screen in [(1.,1.),(.5,.4),(.22,.15)]:
   s=unreal.StaticMeshReductionSettings();s.set_editor_property('percent_triangles',percent);s.set_editor_property('screen_size',screen);settings.append(s)
  opt.set_editor_property('reduction_settings',settings);sm.set_lods(mesh,opt)
  n=mesh.get_editor_property('nanite_settings');n.set_editor_property('enabled',False);mesh.set_editor_property('nanite_settings',n)
  mesh.set_editor_property('positive_bounds_extension',unreal.Vector(6,6,6));mesh.set_editor_property('negative_bounds_extension',unreal.Vector(6,6,6));assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
  assert mesh.get_num_triangles(0)==original.get_num_triangles(0),(name,mesh.get_num_triangles(0),original.get_num_triangles(0))
  records.append({'name':name,'original':original.get_path_name(),'mesh':mesh.get_path_name(),'triangles':[mesh.get_num_triangles(i)for i in range(3)],'slots':slots,'bounds_padding_cm':6})
 (out/'environment-motion.json').write_text(json.dumps({'status':'saved_pending_reopen_runtime','meshes':records,'materials':[m.get_path_name()for m in cache.values()],'creative':'REVIEW_REQUIRED','mobile':'UNQUALIFIED'},indent=2))
except Exception:
 (out/'failed.json').write_text(json.dumps({'exception':traceback.format_exc(),'completed':records},indent=2));raise
