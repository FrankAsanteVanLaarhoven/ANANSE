"""Retain qualified interaction actions after rejected pose experiments."""
import bpy,json,hashlib,struct,shutil
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1]
for key,revision,corrected,original,clip in [('Kwaku','Authored_v022','Authored_v021','Authored_v016','InspectLedger'),('OseboLeopard','Authored_v010','Authored_v009','Authored_v005','CaptureReach')]:
 root=R/'SourceArt/Characters'/key;out=root/revision;assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(root/corrected/(key+'.blend')));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data.action=None;bpy.data.actions.remove(bpy.data.actions[clip])
 with bpy.data.libraries.load(str(root/original/(key+'.blend')),link=False)as(src,dst):dst.actions=[clip]
 action=dst.actions[0];assert action;action.name=clip;action.use_fake_user=True
 if key=='Kwaku':
  rig.animation_data.action=action;bpy.context.scene.frame_set(35);bpy.context.view_layer.update();prop=bpy.data.objects['Ledger_SeparateProp'];world=Matrix.Identity(4);world.translation=Vector((0,-.248,1.045));prop.matrix_world=world;prop.hide_render=True;shutil.copyfile(root/original/'Ledger.glb',out/'Ledger.glb')
 rig.animation_data.action=None
 for b in rig.pose.bones:b.location=(0,0,0);b.scale=(1,1,1);b.rotation_euler=(0,0,0)
 bpy.context.scene.frame_set(0);bpy.ops.wm.save_as_mainfile(filepath=str(out/(key+'.blend')));mesh=bpy.data.objects['SK_'+key];bpy.ops.object.select_all(action='DESELECT');mesh.hide_set(False);mesh.select_set(True);rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(out/(key+'.glb')),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
 p=out/(key+'.glb');raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);d['asset'].pop('generator',None);data=json.dumps(d,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
 if key=='OseboLeopard':shutil.copyfile(root/corrected/'FelineFaceSurface.png',out/'FelineFaceSurface.png')
 report=json.loads((root/corrected/'visual-corrections.json').read_text());report.update(scene_sha256=hashlib.sha256((out/(key+'.blend')).read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),interaction_clip_restored_from=original,interaction_pose_experiment='REJECTED; retained qualified original action',overall_visual_acceptance='FAIL',human_creative_approval=False);(out/'visual-corrections.json').write_text(json.dumps(report,indent=2)+'\n');print('QUALIFIED_ACTION_RETAINED',key,revision)
