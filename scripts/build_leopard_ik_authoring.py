"""Map the imported feline family into its own authoring IK Rig."""
import os,json
from pathlib import Path
import unreal
root=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'leopard-ik.json'
dest='/Game/Ananse/Characters/OseboLeopard/Rig';path=dest+'/IK_OseboLeopard'
if out.exists() or unreal.EditorAssetLibrary.does_asset_exist(path):raise RuntimeError('Preserve existing revision')
source=json.loads((root/'.local/verification/osebo-family-20261015/native-import-v002/leopard-import.json').read_text())
mesh=unreal.load_asset(source['mesh']);assert isinstance(mesh,unreal.SkeletalMesh)
rig=unreal.AssetToolsHelpers.get_asset_tools().create_asset('IK_OseboLeopard',dest,unreal.IKRigDefinition,unreal.IKRigDefinitionFactory())
c=unreal.IKRigController.get_controller(rig);assert c.set_skeletal_mesh(mesh);assert c.set_retarget_root('pelvis')
for side in ['L','R']:
    goal='foot_contact_'+side
    assert str(c.add_new_goal(goal,'foot_'+side))==goal
    index=c.add_solver('/Script/IKRig.IKRigLimbSolver');assert index>=0
    assert c.set_start_bone('thigh_'+side,index);assert c.connect_goal_to_solver(goal,index)
    assert str(c.add_retarget_chain('leg_'+side,'thigh_'+side,'foot_'+side,goal))=='leg_'+side
    assert str(c.add_retarget_chain('arm_'+side,'clavicle_'+side,'hand_'+side,'None'))=='arm_'+side
assert str(c.add_retarget_chain('spine','pelvis','head','None'))=='spine'
assert str(c.add_retarget_chain('tail','tail_01','tail_06','None'))=='tail'
assert c.get_num_solvers()==2 and len(c.get_retarget_chains())==6
assert unreal.EditorAssetLibrary.save_loaded_asset(rig)
out.write_text(json.dumps(dict(path=rig.get_path_name(),mesh=mesh.get_path_name(),solvers=2,goals=2,chains=6,
    role='authoring only; single-node playback remains runtime path',runtime_bound=False,
    contact_accuracy_qualified=False,solver_tuning_reviewed=False),indent=2)+'\n')
