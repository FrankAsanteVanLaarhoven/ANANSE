"""Create a mapped authoring IK Rig without changing runtime pose ownership."""
import json
import os
from pathlib import Path
import unreal

DEST = '/Game/Production/Characters/SpiderRig_v001'
PATH = DEST + '/IK_AnanseSpider'
report = Path(os.environ['ANANSE_EVIDENCE_DIR']) / 'spider-ik-authoring.json'
if report.exists() or unreal.EditorAssetLibrary.does_asset_exist(PATH):
    raise RuntimeError('Preserve existing asset/report; choose a reviewed new revision')
mesh = unreal.load_asset('/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY')
if not isinstance(mesh, unreal.SkeletalMesh):
    raise RuntimeError('Existing qualified spider mesh unavailable')
rig = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    'IK_AnanseSpider', DEST, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
if not isinstance(rig, unreal.IKRigDefinition):
    raise RuntimeError('IK Rig creation failed')
controller = unreal.IKRigController.get_controller(rig)
assert controller.set_skeletal_mesh(mesh)
assert controller.set_retarget_root('pelvis')
chains = []
for side in ('front_l', 'front_r', 'rear_l', 'rear_r'):
    start, end, goal = 'femur_' + side, 'tarsus_' + side, 'foot_' + side
    assert str(controller.add_new_goal(goal, end)) == goal
    solver = controller.add_solver('/Script/IKRig.IKRigLimbSolver')
    assert solver >= 0 and controller.set_start_bone(start, solver)
    assert controller.connect_goal_to_solver(goal, solver)
    assert str(controller.add_retarget_chain('support_' + side, start, end, goal)) == 'support_' + side
    chains.append(dict(chain='support_' + side, start=start, end=end, goal=goal, solver=solver))
for side in ('upper_l', 'upper_r', 'lower_l', 'lower_r'):
    name, start, end = 'arm_' + side, 'clavicle_' + side, 'hand_' + side
    assert str(controller.add_retarget_chain(name, start, end, 'None')) == name
    chains.append(dict(chain=name, start=start, end=end))
assert controller.get_num_solvers() == 4
assert len(controller.get_retarget_chains()) == 8
assert unreal.EditorAssetLibrary.save_loaded_asset(rig)
report.write_text(json.dumps(dict(path=rig.get_path_name(), mesh=mesh.get_path_name(),
    native_class=rig.get_class().get_name(), chains=chains,
    role='authoring only; runtime remains the existing native contact proxy',
    runtime_bound=False, solve_accuracy_tested=False,
    limitations='Limb authoring solver defaults require tuning; not a replacement for the custom contact envelope.'), indent=2) + '\n')
