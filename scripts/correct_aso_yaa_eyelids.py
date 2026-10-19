"""Correct lid occlusion in a new scene; preserve the exact rest rig and all motion identities."""
import bpy,json,hashlib,struct,sys,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];old=R/'SourceArt/Characters/AsoYaa/Authored_v004';out=R/'SourceArt/Characters/AsoYaa/Authored_v007';assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(old/'AsoYaa.blend'));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');rig.animation_data.action=None;s.frame_set(0);bpy.data.objects.remove(bpy.data.objects['SK_AsoYaa'],do_unlink=True)
neck=bpy.data.objects.get('Neck')
if neck:bpy.data.objects.remove(neck,do_unlink=True)
for side in ['L','R']:
 o=bpy.data.objects['AsoYaa_OrbicularLid_'+side];key=o.data.shape_keys.key_blocks['Blink_'+side]
 for i,v in enumerate(key.data):
  factor=1.68/1.70;dx=v.co.x/factor-(-1 if side=='L'else 1)*.042;dz=v.co.z/factor-1.609;q=1-(dx/.023)**2-(dz/.014)**2
  if q>=0:v.co.y=min(v.co.y,(-.072-.018*math.sqrt(q)-.004)*factor)
sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g
g.scene=s;g.parts=[];g.binds={};skin=bpy.data.materials['Skin'];factor=1.68/1.70
for side,sign in [('L',-1),('R',1)]:
 vs=[(sign*.042*factor,-.080*factor,(1.609+.025)*factor)];target=[(sign*.042*factor,-.098*factor,1.609*factor)];fs=[];segments=64;rings=12
 for k in range(1,rings+1):
  radius=k/rings
  for j in range(segments):
   a=math.tau*j/segments;dx=.032*radius*math.cos(a);dz=.024*radius*math.sin(a);q=max(0,1-(dx/.023)**2-(dz/.014)**2);vs.append(((sign*.042+dx)*factor,-.078*factor,(1.634+.001*radius*math.sin(a))*factor));target.append(((sign*.042+dx)*factor,(-.072-.018*math.sqrt(q)-.008)*factor,(1.609+dz)*factor))
 for j in range(segments):fs.append((0,1+j,1+(j+1)%segments))
 for k in range(rings-1):
  for j in range(segments):a=1+k*segments+j;b=1+k*segments+(j+1)%segments;fs.append((a,b,b+segments,a+segments))
 cap=g.mesh('UpperLidClosure_'+side,vs,fs,skin);cap.vertex_groups.new(name='head').add(list(range(len(vs))),1,'REPLACE');cap.parent=rig;cap.modifiers.new('Deform','ARMATURE').object=rig;cap.shape_key_add(name='Basis');key=cap.shape_key_add(name='Blink_'+side)
 for v,co in zip(key.data,target):v.co=co
parts=[o for o in s.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in parts:
 c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.hide_render=False;c.hide_set(False);c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='SK_AsoYaa'
for o in parts:o.hide_render=True;o.hide_set(True)
for key in mesh.data.shape_keys.key_blocks:key.value=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'AsoYaa.blend'));bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(out/'AsoYaa.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
p=out/'AsoYaa.glb';raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
r=json.loads((old/'rig-map.json').read_text());r.update(scene_sha256=hashlib.sha256((out/'AsoYaa.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),vertices=len(mesh.data.vertices),parts=[o.name for o in parts],correction='Lid closed surfaces moved ahead of cornea/iris; duplicate neck surface removed. Rest rig and16 motions unchanged.');(out/'rig-map.json').write_text(json.dumps(r,indent=2)+'\n')
sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g
d=bpy.data.cameras.new('LidReview');d.type='ORTHO';d.ortho_scale=.42;c=bpy.data.objects.new('LidReview',d);s.collection.objects.link(c);c.location=(0,-4,1.59);g.aim(c,(0,0,1.59));s.camera=c;s.render.resolution_x=540;s.render.resolution_y=600
for state in ['neutral','closed']:
 for side in ['L','R']:mesh.data.shape_keys.key_blocks['Blink_'+side].value=1 if state=='closed'else 0
 s.render.filepath=str(out/('eyes_'+state+'.png'));bpy.ops.render.render(write_still=True)
print('CORRECTED_LID_SOURCE_SAVED',r['scene_sha256'])
