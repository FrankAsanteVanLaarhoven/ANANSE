"""Reopen and execute saved authoring rigs; do not modify their source assets."""
import json,os,math
from pathlib import Path
import unreal
root=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'rig-reopen.json'
if out.exists():raise RuntimeError('Preserve previous evidence')
source=json.loads((root/'.local/verification/osebo-family-20261015/native-control-rig-create-02/control-rigs.json').read_text())
results=[]
for record in source['assets']:
    bp=unreal.load_asset(record['path']);assert isinstance(bp,unreal.ControlRigBlueprint)
    hierarchy=bp.get_editor_property('hierarchy');bones=[key for key in hierarchy.get_all_keys() if key.type==unreal.RigElementType.BONE]
    assert len(bones)==record['bones']
    rig=bp.create_control_rig();assert rig and rig.execute('Forwards Solve')
    live=rig.get_hierarchy();checks=[]
    extra=['cloth_02','index_02_upper_l','index_02_upper_r','eye_l','eye_r'] if record['bones']==102 else ['cape_L_02','cape_R_02','digit_L_0_02','digit_R_0_02','eye_L','eye_R']
    for check in record['pose_checks']+[dict(bone=name) for name in extra]:
        name=check['bone'];key=unreal.RigElementKey(type=unreal.RigElementType.BONE,name=name)
        control=unreal.RigElementKey(type=unreal.RigElementType.CONTROL,name=name+'_ctrl')
        before=live.get_global_transform(key).rotation
        live.set_control_value(control,live.make_control_value_from_rotator(unreal.Rotator(pitch=15)),unreal.RigControlValueType.CURRENT)
        assert rig.execute('Forwards Solve')
        after=live.get_global_transform(key).rotation
        delta=sum((getattr(before,k)-getattr(after,k))**2 for k in ['x','y','z','w']);assert delta>1e-5
        error=0
        for bone in bones:
            current=live.get_local_transform(bone).translation;initial=live.get_local_transform(bone,True).translation
            error=max(error,math.sqrt(sum((getattr(current,k)-getattr(initial,k))**2 for k in ['x','y','z'])))
        assert error<=.01,'FK rotation changed local bone length/translation'
        checks.append(dict(bone=name,quaternion_squared_delta=delta,max_local_translation_error_cm=error))
        live.set_control_value(control,live.make_control_value_from_rotator(unreal.Rotator()),unreal.RigControlValueType.CURRENT)
        assert rig.execute('Forwards Solve')
    results.append(dict(asset=record['path'],native_class=bp.get_class().get_name(),bones=len(bones),
        pose_checks=checks,runtime_bound=False,role='Executable FK authoring rig; joint-limit tuning still unapproved'))
# Reopen both real Animation Blueprint classes and skeleton bindings too.
classes=[]
for path,parent in [('/Game/Production/Characters/SpiderRig_v001/ABP_AnanseSpider',unreal.AnanseContactAnimInstance),
                    ('/Game/Ananse/Characters/OseboLeopard/Animations/ABP_OseboLeopard',unreal.AnanseLeopardAnimInstance)]:
    asset=unreal.load_asset(path);assert isinstance(asset,unreal.AnimBlueprint)
    cls=unreal.EditorAssetLibrary.load_blueprint_class(path);assert isinstance(unreal.get_default_object(cls),parent)
    classes.append(dict(asset=asset.get_path_name(),generated_class=cls.get_path_name(),
        skeleton=asset.get_editor_property('target_skeleton').get_path_name()))
assert classes[0]['skeleton']!=classes[1]['skeleton']
out.write_text(json.dumps(dict(status='reopened_executed',rigs=results,animation_blueprints=classes,source_assets_modified=False),indent=2)+'\n')
