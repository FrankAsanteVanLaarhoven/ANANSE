"""Reopen the saved authoring IK asset in a separate editor process."""
import json
import os
from pathlib import Path
import unreal

report = Path(os.environ['ANANSE_EVIDENCE_DIR']) / 'spider-ik-reopen.json'
if report.exists(): raise RuntimeError('Preserve previous evidence')
rig = unreal.load_asset('/Game/Production/Characters/SpiderRig_v001/IK_AnanseSpider')
assert isinstance(rig, unreal.IKRigDefinition)
c = unreal.IKRigController.get_controller(rig)
assert c.get_skeletal_mesh().get_path_name() == '/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY.AnanseSpider_PROXY'
assert c.get_num_solvers() == 4 and len(c.get_all_goals()) == 4
chains = {str(x.chain_name): x for x in c.get_retarget_chains()}
assert len(chains) == 8
for i, side in enumerate(('front_l', 'front_r', 'rear_l', 'rear_r')):
    name = 'support_' + side
    assert name in chains
    assert str(c.get_retarget_chain_start_bone(name)) == 'femur_' + side
    assert str(c.get_retarget_chain_end_bone(name)) == 'tarsus_' + side
    assert str(c.get_retarget_chain_goal(name)) == 'foot_' + side
    assert str(c.get_start_bone(i)) == 'femur_' + side and c.get_solver_enabled(i)
report.write_text(json.dumps(dict(reopened=True, solver_count=4, goal_count=4,
    chain_count=8, role='authoring only', runtime_bound=False), indent=2) + '\n')
