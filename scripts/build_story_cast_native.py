"""Import one authored design and create its independent native asset family.
Uses the previously qualified skeletal GLB import, graph and mapped FK rig APIs.
"""
import unreal,json,os,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];KEY=os.environ['ANANSE_CAST_KEY'];OUT=Path(os.environ['ANANSE_EVIDENCE_DIR']);OUT.mkdir(parents=True,exist_ok=True)
report=OUT/(KEY+'-native.json')
if report.exists():raise RuntimeError('Evidence already exists')
rev=os.environ.get('ANANSE_CAST_REV','Authored_v001');source=ROOT/'SourceArt/Characters'/KEY/rev
contract=json.loads((source/'rig-map.json').read_text());dest='/Game/Ananse/Characters/'+KEY+'/Story_v001'
if unreal.EditorAssetLibrary.does_directory_exist(dest):raise RuntimeError('Existing native revision preserved')
r={'status':'failed','key':KEY,'design_id':contract['design_id'],'creative_approved':False,'campaign_binding_changed':False}
try:
 task=unreal.AssetImportTask()
 for k,v in dict(filename=str(source/(KEY+'.glb')),destination_path=dest,automated=True,replace_existing=False,save=True,async_=False).items():task.set_editor_property(k,v)
 pipeline=unreal.InterchangeGenericAssetsPipeline();pipeline.set_editor_property('import_offset_rotation',unreal.Rotator(pitch=0,yaw=-90,roll=0))
 options=unreal.InterchangePipelineStackOverride();options.set_editor_property('override_pipelines',[unreal.SoftObjectPath(pipeline.get_path_name())]);task.set_editor_property('options',options)
 tools=unreal.AssetToolsHelpers.get_asset_tools();tools.import_asset_tasks([task]);assets=[unreal.load_asset(p) for p in task.get_editor_property('imported_object_paths')]
 meshes=[a for a in assets if isinstance(a,unreal.SkeletalMesh)];clips=[a for a in assets if isinstance(a,unreal.AnimSequence)]
 assert len(meshes)==1 and len(clips)==len(contract['actions']),(len(meshes),len(clips))
 mesh=meshes[0];skel=mesh.get_editor_property('skeleton');assert skel
 mapped=[]
 for act in contract['actions']:
  matches=[c for c in clips if c.get_name()==KEY+act['name'] or c.get_name().endswith('_'+act['name']) or c.get_name()==act['name']]
  assert len(matches)==1,(act['name'],[c.get_name() for c in clips]);mapped.append(matches[0]);assert mapped[-1].get_editor_property('skeleton')==skel
 description=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(mesh));assert len(description['bones'])==len(contract['bones'])
 for slot in mesh.get_editor_property('materials'):
  m=slot.get_editor_property('material_interface')
  if isinstance(m,unreal.Material):
   unreal.MaterialEditingLibrary.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH);m.set_editor_property('two_sided',True)
   unreal.MaterialEditingLibrary.recompile_material(m);assert unreal.EditorAssetLibrary.save_loaded_asset(m)
 factory=unreal.AnimBlueprintFactory();factory.set_editor_property('parent_class',unreal.AnanseCastAnimInstance);factory.set_editor_property('target_skeleton',skel)
 abp=tools.create_asset('ABP_'+KEY,dest,unreal.AnimBlueprint,factory)
 response=unreal.AnanseAnimationAuthoring.populate_clip_graph(abp,mapped[0]);assert response is not None and not response,str(response)
 assert unreal.EditorAssetLibrary.save_loaded_asset(abp);animclass=unreal.EditorAssetLibrary.load_blueprint_class(dest+'/ABP_'+KEY);assert animclass
 factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.AnanseCastLabPlayer)
 bp=tools.create_asset('BP_'+KEY,dest,unreal.Blueprint,factory);unreal.BlueprintEditorLibrary.compile_blueprint(bp)
 cls=unreal.EditorAssetLibrary.load_blueprint_class(dest+'/BP_'+KEY);cdo=unreal.get_default_object(cls)
 identities={'Kwaku':'kwaku','AsoYaa':'aso-yaa','EsiHuman':'esi','OseboHuman':'osebo','KojoTortoise':'kojo','KofiHornbill':'kofi','EsiMoth':'esi'}
 family=KEY+'-independent-v001'
 for k,v in dict(design_id=contract['design_id'],family_key=family,character_id=identities[KEY],authored_mesh=mesh,authored_clips=mapped,animation_class=animclass,authoring_height=contract['height_proposal_m']*100).items():cdo.set_editor_property(k,v)
 assert unreal.EditorAssetLibrary.save_loaded_asset(bp)
 factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.AnanseCharacterDefinition)
 da=tools.create_asset('DA_'+KEY,dest,unreal.AnanseCharacterDefinition,factory)
 for k,v in dict(design_id=contract['design_id'],character_identity=identities[KEY],skeleton_key=family,revision=1,engineering_fixture=True,pawn_class=cls,mesh=mesh,clips=mapped).items():da.set_editor_property(k,v)
 assert unreal.EditorAssetLibrary.save_loaded_asset(da)
 # Two mapped leg goals/solvers are authoring assets. Runtime contact is separately pending.
 ik=tools.create_asset('IK_'+KEY,dest,unreal.IKRigDefinition,unreal.IKRigDefinitionFactory());ic=unreal.IKRigController.get_controller(ik);assert ic.set_skeletal_mesh(mesh);assert ic.set_retarget_root('pelvis')
 for side in ['L','R']:
  goal='foot_contact_'+side;assert str(ic.add_new_goal(goal,'foot_'+side))==goal;idx=ic.add_solver('/Script/IKRig.IKRigLimbSolver');assert idx>=0;assert ic.set_start_bone('thigh_'+side,idx);assert ic.connect_goal_to_solver(goal,idx)
  ic.add_retarget_chain('leg_'+side,'thigh_'+side,'foot_'+side,goal);ic.add_retarget_chain('arm_'+side,'clavicle_'+side,'hand_'+side,'None')
 assert unreal.EditorAssetLibrary.save_loaded_asset(ik)
 # Same reviewed executable FK authoring implementation, separate skeleton mapping.
 rigbp=unreal.ControlRigBlueprintFactory.create_new_control_rig_asset(dest+'/CR_'+KEY);rigbp.set_auto_vm_recompile(False);rigbp.set_editor_property('preview_skeletal_mesh',mesh)
 hierarchy=rigbp.get_editor_property('hierarchy');hc=rigbp.get_hierarchy_controller();bones=list(hc.import_bones_from_skeletal_mesh(mesh,''));controls={}
 for key in bones:
  parents=hierarchy.get_parents(key,False);parent=controls.get(str(parents[0].name),unreal.RigElementKey()) if parents else unreal.RigElementKey();name=str(key.name);settings=unreal.RigControlSettings()
  if name=='root':settings.control_type=unreal.RigControlType.EULER_TRANSFORM;value=hierarchy.make_control_value_from_euler_transform(unreal.EulerTransform(scale=[1,1,1]))
  else:settings.control_type=unreal.RigControlType.ROTATOR;value=hierarchy.make_control_value_from_rotator(unreal.Rotator())
  control=hc.add_control(name+'_ctrl',parent,settings,value,False,False);hierarchy.set_control_offset_transform(control,hierarchy.get_local_transform(key,True),True);controls[name]=control
 controller=rigbp.get_controller();begin=controller.add_unit_node_from_struct_path('/Script/ControlRig.RigUnit_BeginExecution','Execute',unreal.Vector2D(0,0),'AuthoringForwardSolve');previous=begin.find_pin('ExecuteContext').get_pin_path()
 for i,key in enumerate(bones):
  name=str(key.name);getter=unreal.RigUnit_GetTransform();getter.item=controls[name];getter.initial=False;setter=unreal.RigUnit_SetTransform();setter.item=key;setter.initial=False;setter.weight=1.;setter.propagate_to_children=True
  getnode=controller.add_unit_node_with_defaults(getter.static_struct(),getter.export_text(),'Execute',unreal.Vector2D(-400,120*i),name+'_ReadControl');setnode=controller.add_unit_node_with_defaults(setter.static_struct(),setter.export_text(),'Execute',unreal.Vector2D(100,120*i),name+'_WriteBone')
  assert controller.add_link(getnode.find_pin('Transform').get_pin_path(),setnode.find_pin('Value').get_pin_path());assert controller.add_link(previous,setnode.find_pin('ExecuteContext').get_pin_path());previous=setnode.find_pin('ExecuteContext').get_pin_path()
 rigbp.recompile_vm();rig=rigbp.create_control_rig();assert rig.execute('Forwards Solve');live=rig.get_hierarchy();checks=[]
 for name in ['head','jaw','hand_L','hand_R','foot_L','foot_R']:
  k=unreal.RigElementKey(type=unreal.RigElementType.BONE,name=name);c=controls[name];before=live.get_global_transform(k).rotation;live.set_control_value(c,live.make_control_value_from_rotator(unreal.Rotator(pitch=15)),unreal.RigControlValueType.CURRENT);assert rig.execute('Forwards Solve');after=live.get_global_transform(k).rotation;delta=sum((getattr(before,n)-getattr(after,n))**2 for n in ['x','y','z','w']);assert delta>1e-5;checks.append({'bone':name,'quaternion_delta_squared':delta});live.set_control_value(c,live.make_control_value_from_rotator(unreal.Rotator()),unreal.RigControlValueType.CURRENT);assert rig.execute('Forwards Solve')
 rigbp.set_auto_vm_recompile(True);assert unreal.EditorAssetLibrary.save_loaded_asset(rigbp)
 # New isolated map per design; never overwrite campaign or earlier lab maps.
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);map_path='/Game/Ananse/Maps/StoryCast_v001/L_'+KEY+'CharacterLab';assert levels.new_level(map_path)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-50));floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(40,40,1));actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(0,0,160))
 light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,1000),unreal.Rotator(-45,-30,0));light.light_component.set_mobility(unreal.ComponentMobility.MOVABLE);actors.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,900)).light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
 modefactory=unreal.BlueprintFactory();modefactory.set_editor_property('parent_class',unreal.AnanseCharacterLabMode);mode=tools.create_asset('BP_'+KEY+'LabMode',dest,unreal.Blueprint,modefactory);unreal.BlueprintEditorLibrary.compile_blueprint(mode);modeclass=unreal.EditorAssetLibrary.load_blueprint_class(dest+'/BP_'+KEY+'LabMode');unreal.get_default_object(modeclass).set_editor_property('default_pawn_class',cls);assert unreal.EditorAssetLibrary.save_loaded_asset(mode)
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',modeclass);assert levels.save_current_level()
 r.update(status='native_assets_compiled_executed_saved_pending_reopen_runtime',mesh=mesh.get_path_name(),skeleton=skel.get_path_name(),physics=mesh.get_editor_property('physics_asset').get_path_name(),blueprint=bp.get_path_name(),generated_class=cls.get_path_name(),definition=da.get_path_name(),animation_blueprint=abp.get_path_name(),ik=ik.get_path_name(),control_rig=rigbp.get_path_name(),map=map_path,clips={a['name']:c.get_path_name() for a,c in zip(contract['actions'],mapped)},bones=description['bones'],rig_execution_checks=checks,source_revision=rev,source_scene_sha256=contract['scene_sha256'],glb_sha256=contract['glb_sha256'],ground_contact_qualified=False,physics_reviewed=False,lods_reviewed=False)
except Exception:r['exception']=traceback.format_exc();raise
finally:report.write_text(json.dumps(r,indent=2)+'\n')
