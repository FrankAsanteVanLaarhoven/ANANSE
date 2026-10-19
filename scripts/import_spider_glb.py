"""Qualify the supplied rig through the installed Interchange GLB path, editor only."""
import hashlib,json,os,traceback
from pathlib import Path
import unreal
root=Path(__file__).resolve().parents[1]
source=root/'SourceArt/ANANSE_Spider_Character_Kit/assets/proxy-v001/AnanseSpider_PROXY.glb'
report=Path(os.environ['ANANSE_IMPORT_REPORT']);dest=os.environ['ANANSE_IMPORT_DEST']
if report.exists():raise FileExistsError(report)
if not dest.startswith('/Game/Characters/AnanseSpider/') or unreal.EditorAssetLibrary.does_directory_exist(dest):raise RuntimeError('Use a fresh spider content destination.')
result={'status':'failed','source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'destination':dest,'engine':unreal.SystemLibrary.get_engine_version()}
try:
 task=unreal.AssetImportTask()
 for k,v in {'filename':str(source),'destination_path':dest,'automated':True,'replace_existing':False,'save':True,'async_':False}.items():task.set_editor_property(k,v)
 # Installed GLTF ConvertVec3 maps source +Z forward to Unreal +Y.
 # A task-local -90 degree yaw establishes +X forward without changing scale.
 pipeline=unreal.InterchangeGenericAssetsPipeline()
 pipeline.set_editor_property('import_offset_rotation',unreal.Rotator(pitch=0,yaw=-90,roll=0))
 options=unreal.InterchangePipelineStackOverride()
 options.set_editor_property('override_pipelines',[unreal.SoftObjectPath(pipeline.get_path_name())])
 task.set_editor_property('options',options)
 result['basis']={'source_forward':'+Z','engine_default_forward':'+Y','yaw_degrees':-90,'uniform_scale':1}
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 paths=task.get_editor_property('imported_object_paths');assets=[unreal.load_asset(p) for p in paths]
 result['objects']=[{'path':a.get_path_name(),'class':a.get_class().get_name()} for a in assets if a]
 meshes=[a for a in assets if isinstance(a,unreal.SkeletalMesh)];clips=[a for a in assets if isinstance(a,unreal.AnimSequence)]
 if len(meshes)!=1 or len(clips)!=4:raise RuntimeError(f'Expected one skeletal mesh and four clips; got {len(meshes)} / {len(clips)}.')
 skeleton=meshes[0].get_editor_property('skeleton')
 if not skeleton or any(a.get_editor_property('skeleton')!=skeleton for a in clips):raise RuntimeError('Missing or mismatched skeleton.')
 result.update(status='IMPORTED_NOT_RENDERED_OR_BIND_POSE_VALIDATED',skeletal_mesh=meshes[0].get_path_name(),skeleton=skeleton.get_path_name(),animations=[a.get_path_name() for a in clips])
except Exception:
 result['exception']=traceback.format_exc();raise
finally:
 report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2)+'\n')
