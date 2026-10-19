"""Import the locally authored feline family through the qualified GLB path."""
import hashlib,json,os,traceback
from pathlib import Path
import unreal

source=Path(os.environ['ANANSE_LEOPARD_GLB']).resolve()
root=Path(__file__).resolve().parents[1]
if not source.is_relative_to(root/'SourceArt/Characters/OseboLeopard'):
    raise RuntimeError('Only the project-owned authored leopard source is accepted')
report=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'leopard-import.json'
dest='/Game/Ananse/Characters/OseboLeopard/Authored_v001'
if report.exists() or unreal.EditorAssetLibrary.does_directory_exist(dest):
    raise RuntimeError('Preserve existing import and report; use a reviewed new revision')
result=dict(status='failed',source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    engine=unreal.SystemLibrary.get_engine_version(),destination=dest)
try:
    task=unreal.AssetImportTask()
    for key,value in dict(filename=str(source),destination_path=dest,automated=True,replace_existing=False,save=True,async_=False).items():
        task.set_editor_property(key,value)
    pipeline=unreal.InterchangeGenericAssetsPipeline()
    pipeline.set_editor_property('import_offset_rotation',unreal.Rotator(pitch=0,yaw=-90,roll=0))
    options=unreal.InterchangePipelineStackOverride()
    options.set_editor_property('override_pipelines',[unreal.SoftObjectPath(pipeline.get_path_name())])
    task.set_editor_property('options',options)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    assets=[unreal.load_asset(p) for p in task.get_editor_property('imported_object_paths')]
    meshes=[a for a in assets if isinstance(a,unreal.SkeletalMesh)]
    clips=[a for a in assets if isinstance(a,unreal.AnimSequence)]
    result['objects']=[dict(path=a.get_path_name(),native_class=a.get_class().get_name()) for a in assets if a]
    if len(meshes)!=1 or len(clips)!=9:raise RuntimeError('Expected one actual SkeletalMesh and nine distinct actions; found %d/%d'%(len(meshes),len(clips)))
    mesh=meshes[0];skeleton=mesh.get_editor_property('skeleton')
    if not skeleton or any(c.get_editor_property('skeleton')!=skeleton for c in clips):raise RuntimeError('Animation family mismatch')
    names=['IdleGuard','Patrol','RunPursuit','TurnStop','Investigate','CaptureReach','StaggerRecover','Command','LimbIsolation']
    mapped={}
    for name in names:
        matches=[c for c in clips if name in c.get_name()]
        if len(matches)!=1:raise RuntimeError('Missing or ambiguous authored action '+name)
        mapped[name]=matches[0].get_path_name()
    result.update(status='IMPORTED_PENDING_POSE_AND_NATIVE_ACCEPTANCE',mesh=mesh.get_path_name(),
        skeleton=skeleton.get_path_name(),clips=mapped,
        physics=mesh.get_editor_property('physics_asset').get_path_name() if mesh.get_editor_property('physics_asset') else None,
        conversion=dict(source_units='metres',native_units='centimetres',source_forward='+Z glTF',native_forward='+X',task_yaw=-90,uniform_scale=1),
        creative_approval=False,campaign_mapping_approved=False)
except Exception:
    result['exception']=traceback.format_exc();raise
finally:
    report.write_text(json.dumps(result,indent=2)+'\n')
