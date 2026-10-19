"""Reopen imported mesh and saved pawn bindings; independently qualify units."""
import unreal,os,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);report=out/'native-assets.json'
if report.exists():raise RuntimeError('Preserve prior evidence')
source=json.loads((root/'.local/verification/osebo-family-20261015/native-import-v002/leopard-import.json').read_text())
mesh=unreal.load_asset(source['mesh']);assert isinstance(mesh,unreal.SkeletalMesh)
cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Ananse/Characters/OseboLeopard/Runtime_v001/BP_OseboLeopard')
cdo=unreal.get_default_object(cls);assert isinstance(cdo,unreal.AnanseLeopardLabPlayer)
assert cdo.get_editor_property('leopard_mesh')==mesh
clips=cdo.get_editor_property('leopard_clips');assert len(clips)==9
assert all(isinstance(c,unreal.AnimSequence) and c.get_editor_property('skeleton')==mesh.get_editor_property('skeleton') for c in clips)
mode=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Ananse/Characters/OseboLeopard/Runtime_v001/BP_OseboLeopardLabMode')
assert unreal.get_default_object(mode).get_editor_property('default_pawn_class')==cls
probe='/Game/Production/Qualification/DCCUnits_v001'
if unreal.EditorAssetLibrary.does_directory_exist(probe):raise RuntimeError('Preserve earlier probe revision')
task=unreal.AssetImportTask()
for k,v in dict(filename=str(root/'.local/verification/osebo-family-20261015/blender-qualification/dimension-probe.glb'),destination_path=probe,automated=True,replace_existing=False,save=True,async_=False).items():task.set_editor_property(k,v)
pipeline=unreal.InterchangeGenericAssetsPipeline();pipeline.set_editor_property('import_offset_rotation',unreal.Rotator(pitch=0,yaw=-90,roll=0))
options=unreal.InterchangePipelineStackOverride();options.set_editor_property('override_pipelines',[unreal.SoftObjectPath(pipeline.get_path_name())]);task.set_editor_property('options',options)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
probes=[unreal.load_asset(p) for p in task.get_editor_property('imported_object_paths')]
probes=[p for p in probes if isinstance(p,unreal.StaticMesh)];assert len(probes)==1
bounds=probes[0].get_bounds();extent=bounds.box_extent;dims=[extent.x*2,extent.y*2,extent.z*2]
assert all(abs(a-b)<.01 for a,b in zip(dims,[75,50,200]))
report.write_text(json.dumps(dict(status='reopened_bindings_and_unit_probe_passed',pawn_class=cls.get_path_name(),
    mesh=mesh.get_path_name(),skeleton=mesh.get_editor_property('skeleton').get_path_name(),clips=[c.get_path_name() for c in clips],
    physics=mesh.get_editor_property('physics_asset').get_path_name(),probe_dimensions_cm=dims,
    native_movement_tested=False,creative_approval=False),indent=2)+'\n')
