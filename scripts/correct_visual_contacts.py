"""Actual globe-conforming eye surfaces and checked two-hand pose on retained rigs."""
import bpy,json,hashlib,struct,shutil,math,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1]
for key,old,new in [('Kwaku','Authored_v023','Authored_v026'),('OseboLeopard','Authored_v011','Authored_v012')]:
 if '--'in sys.argv and key!=sys.argv[sys.argv.index('--')+1]:continue
 root=R/'SourceArt/Characters'/key;src=root/old;out=root/new;assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(src/(key+'.blend')));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');mesh=bpy.data.objects['SK_'+key];rig.animation_data.action=None
 for b in rig.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
 bpy.context.scene.frame_set(0);details={}
 if key=='OseboLeopard':
  for side in ['L','R']:
   eye=bpy.data.objects['Eye_'+side];c=sum((v.co for v in eye.data.vertices),Vector())/len(eye.data.vertices);rx,ry,rz=[max(abs(v.co[i]-c[i])for v in eye.data.vertices)for i in range(3)];mats={m.name for prefix in ['Iris_','Pupil_']for m in bpy.data.objects[prefix+side].data.materials};ids=set()
   for poly in mesh.data.polygons:
    if mesh.data.materials[poly.material_index].name in mats:ids.update(poly.vertices)
   group=mesh.vertex_groups['eye_'+side]
   for i in ids:
    v=mesh.data.vertices[i]
    if not any(a.group==group.index and a.weight>.9 for a in v.groups):continue
    alpha=((v.co.x-c.x)/rx)**2+((v.co.z-c.z)/rz)**2;new_y=c.y-ry*math.sqrt(max(.01,1-alpha))-.0007;delta=new_y-v.co.y
    for shape in mesh.data.shape_keys.key_blocks:shape.data[i].co.y+=delta
    v.co.y=new_y
   for prefix in ['Iris_','Pupil_']:
    part=bpy.data.objects[prefix+side]
    for v in part.data.vertices:alpha=((v.co.x-c.x)/rx)**2+((v.co.z-c.z)/rz)**2;v.co.y=c.y-ry*math.sqrt(max(.01,1-alpha))-.0007
  details['eye_surface_fix']='Iris/pupil vertices conform to actual globe instead of protruding flat discs; original eye bones retained'
 else:
  original=bpy.data.actions['InspectLedger'];bpy.data.actions.remove(original);neutral={b.name:b.rotation_euler.copy()for b in rig.pose.bones}
  def aim(name,a,b):
   d=(b-a).normalized();up=Vector((0,1,0));x=d.cross(up).normalized();z=x.cross(d).normalized();m=Matrix(((x.x,d.x,z.x),(x.y,d.y,z.y),(x.z,d.z,z.z))).to_4x4();m.translation=a;rig.pose.bones[name].matrix=m;bpy.context.view_layer.update()
  targets={}
  for side,sign in [('L',-1),('R',1)]:
   upper=rig.data.bones['upperarm_'+side];lower=rig.data.bones['lowerarm_'+side];S=upper.head_local.copy();T=Vector((sign*.130,-.230,1.087));a=upper.length;b=lower.length;d=(T-S).length;u=(T-S).normalized();along=(a*a-b*b+d*d)/(2*d);height=math.sqrt(max(0,a*a-along*along));pole=Vector((sign,0,-.3));pole=(pole-u*pole.dot(u)).normalized();E=S+along*u+height*pole;aim('upperarm_'+side,S,E);aim('lowerarm_'+side,E,T);aim('hand_'+side,T,T+Vector((-sign*.015,-.010,-.060)));targets[side]=list(T)
   for i in range(5):
    for seg in ['01','02']:rig.pose.bones[f'digit_{side}_{i}_{seg}'].rotation_euler.x=-.8 if i==0 else .55
  bpy.context.view_layer.update();hold={b.name:b.rotation_euler.copy()for b in rig.pose.bones};before={side:list(rig.pose.bones['hand_'+side].head)for side in ['L','R']};action=bpy.data.actions.new('InspectLedger');action.use_fake_user=True;rig.animation_data.action=action
  for frame,pose in [(1,neutral),(14,hold),(67,hold),(82,neutral)]:
   for b in rig.pose.bones:b.rotation_euler=pose[b.name]
   for b in rig.pose.bones:b.keyframe_insert('rotation_euler',frame=frame)
  bpy.context.scene.frame_set(35);bpy.context.view_layer.update();after={side:list(rig.pose.bones['hand_'+side].head)for side in ['L','R']};assert all(math.dist(after[s],targets[s])<1e-4 for s in ['L','R']),(after,targets,before);prop=bpy.data.objects['Ledger_SeparateProp'];world=Matrix.Identity(4);world.translation=Vector((0,-.248,1.045));prop.matrix_world=world;details.update(checked_hand_targets=targets,evaluated_hand_heads=after,new_clip='InspectLedger',held_frames=[14,67],old_rest_bones_retained=True)
 rig.animation_data.action=None
 for b in rig.pose.bones:b.rotation_euler=(0,0,0)
 bpy.context.scene.frame_set(0);bpy.ops.wm.save_as_mainfile(filepath=str(out/(key+'.blend')));bpy.ops.object.select_all(action='DESELECT');mesh.hide_set(False);mesh.select_set(True);rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(out/(key+'.glb')),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
 p=out/(key+'.glb');raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);d['asset'].pop('generator',None);data=json.dumps(d,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
 for filename in ['Ledger.glb','FelineFaceSurface.png']:
  if(src/filename).exists():shutil.copyfile(src/filename,out/filename)
 report=json.loads((src/'visual-corrections.json').read_text());report.update(details);report.update(scene_sha256=hashlib.sha256((out/(key+'.blend')).read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),final_character_accepted=False);(out/'visual-corrections.json').write_text(json.dumps(report,indent=2)+'\n');print('CONTACT_CORRECTION_SAVED',key,new)
