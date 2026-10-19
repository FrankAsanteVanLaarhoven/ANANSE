"""Keep complete arm anatomy inside the tailored sleeve in the held-ledger bend."""
import bpy,sys,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];old=R/'SourceArt/Characters/AsoYaa/Authored_v017';out=R/'SourceArt/Characters/AsoYaa/Authored_v018';assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(old/'AsoYaa.blend'));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0)
s.frame_set(0);bpy.context.view_layer.update();bpy.data.objects.remove(bpy.data.objects['SK_AsoYaa'],do_unlink=True)
changed=[]
for side in ['L','R']:
 obj=bpy.data.objects['Arm_'+side];segments=[(rig.data.bones[n+'_'+side].head_local,rig.data.bones[n+'_'+side].tail_local)for n in ['upperarm','lowerarm']]
 for v in obj.data.vertices:
  p=v.co.copy();choices=[]
  for a,b in segments:
   axis=b-a;t=max(0,min(1,(p-a).dot(axis)/axis.length_squared));q=a+t*axis;choices.append(((p-q).length_squared,q))
  q=min(choices,key=lambda x:x[0])[1];v.co=q+(p-q)*.72
 changed.append({'part':obj.name,'vertices':len(obj.data.vertices),'radial_factor':.72,'reason':'Occluded body surface protruded through sleeve during elbow bend; retain the complete arm with reduced hidden radial volume'})
ledger=bpy.data.objects['Ledger_SeparateProp'];parts=[o for o in s.objects if o.type=='MESH'and o!=ledger];bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in parts:
 c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.hide_render=False;c.hide_set(False);c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='SK_AsoYaa'
for o in parts:o.hide_render=True;o.hide_set(True)
for key in mesh.data.shape_keys.key_blocks:key.value=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'AsoYaa.blend'));bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);rig.select_set(True);p=out/'AsoYaa.glb';bpy.ops.export_scene.gltf(filepath=str(p),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
report=json.loads((old/'rig-map.json').read_text());report.update(scene_sha256=hashlib.sha256((out/'AsoYaa.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),parts=[o.name for o in parts],correction='Connected robe/yoke; separate sewn sleeves; measured support grip; full hold bake; hidden arm-radius clearance correction. Creative review remains open.',sleeve_clearance_changes=changed,animation_and_rest_skeleton_unchanged=True,creative_approved=False);(out/'rig-map.json').write_text(json.dumps(report,indent=2)+'\n');print('SLEEVE_CLEARANCE_SOURCE',report['scene_sha256'])
