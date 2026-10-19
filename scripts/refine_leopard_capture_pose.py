"""Readable two-paw reach on the existing feline skeleton; no capture gameplay change."""
import bpy,json,hashlib,struct,shutil,math
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];src=R/'SourceArt/Characters/OseboLeopard/Authored_v012';out=src.parent/'Authored_v013';assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(src/'OseboLeopard.blend'));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');mesh=bpy.data.objects['SK_OseboLeopard'];rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
s.frame_set(0);neutral={b.name:b.rotation_euler.copy()for b in rig.pose.bones}
def aim(name,a,b):
 d=(b-a).normalized();up=Vector((0,1,0));x=d.cross(up).normalized();z=x.cross(d).normalized();m=Matrix(((x.x,d.x,z.x),(x.y,d.y,z.y),(x.z,d.z,z.z))).to_4x4();m.translation=a;rig.pose.bones[name].matrix=m;bpy.context.view_layer.update()
targets={}
for side,sign in [('L',-1),('R',1)]:
 upper=rig.data.bones['upperarm_'+side];lower=rig.data.bones['lowerarm_'+side];S=upper.head_local.copy();T=Vector((sign*.225,-.385,1.39));a=upper.length;b=lower.length;d=(T-S).length;u=(T-S).normalized();along=(a*a-b*b+d*d)/(2*d);height=math.sqrt(max(0,a*a-along*along));pole=Vector((sign,0,-.35));pole=(pole-u*pole.dot(u)).normalized();E=S+along*u+height*pole;aim('upperarm_'+side,S,E);aim('lowerarm_'+side,E,T);aim('hand_'+side,T,T+Vector((0,-.085,-.025)));targets[side]=list(T)
 for i in range(4):
  for seg in ['01','02']:rig.pose.bones[f'digit_{side}_{i}_{seg}'].rotation_euler.x=.28
bpy.context.view_layer.update();hold={b.name:b.rotation_euler.copy()for b in rig.pose.bones};bpy.data.actions.remove(bpy.data.actions['CaptureReach']);action=bpy.data.actions.new('CaptureReach');action.use_fake_user=True;rig.animation_data.action=action
for frame,pose in [(0,neutral),(14,hold),(45,hold),(60,neutral)]:
 for b in rig.pose.bones:b.rotation_euler=pose[b.name]
 for b in rig.pose.bones:b.keyframe_insert('rotation_euler',frame=frame)
s.frame_set(35);bpy.context.view_layer.update();actual={side:list(rig.pose.bones['hand_'+side].head)for side in ['L','R']};assert all(math.dist(actual[k],targets[k])<1e-4 for k in targets);rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_euler=neutral[b.name]
s.frame_set(0);bpy.ops.wm.save_as_mainfile(filepath=str(out/'OseboLeopard.blend'));bpy.ops.object.select_all(action='DESELECT');mesh.hide_set(False);mesh.select_set(True);rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(out/'OseboLeopard.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
p=out/'OseboLeopard.glb';raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);d['asset'].pop('generator',None);head=json.dumps(d,separators=(',',':')).encode();head+=b' '*((-len(head))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(head)+len(tail))+struct.pack('<II',len(head),0x4e4f534a)+head+tail);shutil.copyfile(src/'FelineFaceSurface.png',out/'FelineFaceSurface.png');report=json.loads((src/'visual-corrections.json').read_text());report.update(scene_sha256=hashlib.sha256((out/'OseboLeopard.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),capture_reach_actual_hands=actual,capture_reach_targets=targets,capture_gameplay_changed=False);(out/'visual-corrections.json').write_text(json.dumps(report,indent=2)+'\n');print('FELINE_CAPTURE_POSE_CORRECTED',actual)
