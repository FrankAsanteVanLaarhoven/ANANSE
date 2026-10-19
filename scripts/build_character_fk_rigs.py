"""Build mapped, executable FK authoring rigs without a second runtime leg solve."""
import json,os,traceback
from pathlib import Path
import unreal

root=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'control-rigs.json'
if out.exists():raise RuntimeError('Preserve previous evidence')
jobs=[dict(name='CR_AnanseSpider',dest='/Game/Production/Characters/SpiderRig_v001',
    mesh='/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY',count=102,
    tests=['jaw','hand_upper_l','hand_upper_r','hand_lower_l','hand_lower_r','tarsus_front_l','tarsus_front_r','tarsus_rear_l','tarsus_rear_r','abdomen_01']),
 dict(name='CR_OseboLeopard',dest='/Game/Ananse/Characters/OseboLeopard/Rig',
    mesh='/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard',count=64,
    tests=['jaw','hand_L','hand_R','foot_L','foot_R','tail_01','tail_06','ear_L','ear_R'])]
result=dict(status='failed',assets=[])
try:
    for job in jobs:
        path=job['dest']+'/'+job['name']
        if unreal.EditorAssetLibrary.does_asset_exist(path):raise RuntimeError('Existing authored rig preserved: '+path)
        mesh=unreal.load_asset(job['mesh']);assert isinstance(mesh,unreal.SkeletalMesh)
        bp=unreal.ControlRigBlueprintFactory.create_new_control_rig_asset(path)
        bp.set_auto_vm_recompile(False)
        bp.set_editor_property('preview_skeletal_mesh',mesh)
        hierarchy=bp.get_editor_property('hierarchy');hc=bp.get_hierarchy_controller()
        bones=list(hc.import_bones_from_skeletal_mesh(mesh,''));assert len(bones)==job['count']
        controls={};mapping=[]
        for key in bones:
            parents=hierarchy.get_parents(key,False);parent=controls.get(str(parents[0].name),unreal.RigElementKey()) if parents else unreal.RigElementKey()
            name=str(key.name);settings=unreal.RigControlSettings()
            if name in ['root','pelvis']:
                settings.control_type=unreal.RigControlType.EULER_TRANSFORM
                value=hierarchy.make_control_value_from_euler_transform(unreal.EulerTransform(scale=[1,1,1]))
            else:
                settings.control_type=unreal.RigControlType.ROTATOR
                value=hierarchy.make_control_value_from_rotator(unreal.Rotator())
            control=hc.add_control(name+'_ctrl',parent,settings,value,False,False)
            hierarchy.set_control_offset_transform(control,hierarchy.get_local_transform(key,True),True)
            controls[name]=control;mapping.append(dict(bone=name,control=str(control.name),type=str(settings.control_type)))
        controller=bp.get_controller()
        begin=controller.add_unit_node_from_struct_path('/Script/ControlRig.RigUnit_BeginExecution','Execute',unreal.Vector2D(0,0),'AuthoringForwardSolve')
        assert begin
        previous=begin.find_pin('ExecuteContext').get_pin_path()
        for i,key in enumerate(bones):
            name=str(key.name)
            getter=unreal.RigUnit_GetTransform();getter.item=controls[name];getter.initial=False
            setter=unreal.RigUnit_SetTransform();setter.item=key;setter.initial=False;setter.weight=1.;setter.propagate_to_children=True
            getnode=controller.add_unit_node_with_defaults(getter.static_struct(),getter.export_text(),'Execute',unreal.Vector2D(-400,120*i),name+'_ReadControl')
            setnode=controller.add_unit_node_with_defaults(setter.static_struct(),setter.export_text(),'Execute',unreal.Vector2D(100,120*i),name+'_WriteBone')
            assert getnode and setnode
            assert controller.add_link(getnode.find_pin('Transform').get_pin_path(),setnode.find_pin('Value').get_pin_path())
            assert controller.add_link(previous,setnode.find_pin('ExecuteContext').get_pin_path())
            previous=setnode.find_pin('ExecuteContext').get_pin_path()
        bp.recompile_vm()
        rig=bp.create_control_rig();assert rig
        assert rig.execute('Forwards Solve')
        live=rig.get_hierarchy();checks=[]
        for name in job['tests']:
            key=unreal.RigElementKey(type=unreal.RigElementType.BONE,name=name);control=unreal.RigElementKey(type=unreal.RigElementType.CONTROL,name=name+'_ctrl')
            before=live.get_global_transform(key).rotation
            live.set_control_value(control,live.make_control_value_from_rotator(unreal.Rotator(pitch=15)),unreal.RigControlValueType.CURRENT)
            assert rig.execute('Forwards Solve')
            after=live.get_global_transform(key).rotation
            delta=sum((getattr(before,k)-getattr(after,k))**2 for k in ['x','y','z','w'])
            assert delta>1e-5,'Executable FK control did not change '+name
            checks.append(dict(bone=name,quaternion_squared_delta=delta,executed=True))
            live.set_control_value(control,live.make_control_value_from_rotator(unreal.Rotator()),unreal.RigControlValueType.CURRENT)
            assert rig.execute('Forwards Solve')
        bp.set_auto_vm_recompile(True)
        assert unreal.EditorAssetLibrary.save_loaded_asset(bp)
        result['assets'].append(dict(path=bp.get_path_name(),native_class=bp.get_class().get_name(),
            mesh=mesh.get_path_name(),bones=len(bones),controls=len(controls),mapping=mapping,pose_checks=checks,
            role='Executable FK authoring rig. Runtime uses the separate clip graphs and existing spider contact solve.',
            runtime_bound=False,joint_limits_reviewed=False,reopened=False))
    result['status']='compiled_executed_saved_pending_reopen'
except Exception:
    result['exception']=traceback.format_exc();raise
finally:out.write_text(json.dumps(result,indent=2)+'\n')
