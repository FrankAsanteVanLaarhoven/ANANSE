"""Refine the saved feline family, never its rest skeleton or movement authority."""
import bpy,math,json,hashlib,struct,sys
from pathlib import Path
from mathutils import Vector,kdtree
import numpy as np
R=Path(__file__).resolve().parents[1];OUT=R/'SourceArt/Characters/OseboLeopard/Authored_v005';assert not OUT.exists();OUT.mkdir(parents=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceArt/Characters/OseboLeopard/Authored_v002/OseboLeopard.blend'))
s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');rig.animation_data.action=None;s.frame_set(0)
def rest():return [(b.name,b.parent.name if b.parent else None,list(v for row in b.matrix_local for v in row))for b in rig.data.bones]
before=rest();actions=sorted(a.name for a in bpy.data.actions)
for b in rig.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g;g.scene=s;g.parts=[];g.binds={}
mats={m.name:m for m in bpy.data.materials};fur=mats['Fur_Gold_Rosettes'];cream=mats['Muzzle_Chest_Cream']
def bind(o,bone):
 for x in list(o.vertex_groups):o.vertex_groups.remove(x)
 o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE');o.parent=rig;o.modifiers.new('Skin','ARMATURE').object=rig;return o
def union(objects,name,voxel,budget):
 samples=[]
 for o in objects:
  for v in o.data.vertices:samples.append((o.matrix_world@v.co,{o.vertex_groups[a.group].name:a.weight for a in v.groups if a.weight>0 and o.vertex_groups[a.group].name in rig.data.bones}))
 kd=kdtree.KDTree(len(samples))
 for i,(p,w)in enumerate(samples):kd.insert(p,i)
 kd.balance();bpy.ops.object.select_all(action='DESELECT')
 for o in objects:
  for m in list(o.modifiers):o.modifiers.remove(m)
  o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 m=o.modifiers.new('ContinuousSurface','REMESH');m.mode='VOXEL';m.voxel_size=voxel;m.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=m.name)
 m=o.modifiers.new('SurfaceRelax','SMOOTH');m.factor=.45;m.iterations=4;bpy.ops.object.modifier_apply(modifier=m.name)
 m=o.modifiers.new('SurfaceBudget','DECIMATE');m.ratio=min(1,budget/len(o.data.vertices));bpy.ops.object.modifier_apply(modifier=m.name)
 for group in list(o.vertex_groups):o.vertex_groups.remove(group)
 groups={}
 for v in o.data.vertices:
  row={}
  for point,i,d in kd.find_n(o.matrix_world@v.co,4):
   for n,w in samples[i][1].items():row[n]=row.get(n,0)+w/max(.0001,d)**2
  row=sorted(row.items(),key=lambda x:x[1],reverse=True)[:4];total=sum(w for n,w in row);assert total>0
  for n,w in row:
   if n not in groups:groups[n]=o.vertex_groups.new(name=n)
   groups[n].add([v.index],w/total,'REPLACE')
 for p in o.data.polygons:p.use_smooth=True
 o.parent=rig;o.modifiers.new('Skin','ARMATURE').object=rig;return o
# Shape the muzzle before unifying the cheek/lid surface; jaw retains its own binding.
for side in ['L','R']:
 o=bpy.data.objects['Muzzle_'+side]
 for v in o.data.vertices:v.co.y=-.14+(v.co.y+.14)*.73;v.co.z=1.838+(v.co.z-1.838)*.88
for name in ['Head_Cheeks_Brow','Neck_Fur']:
 o=bpy.data.objects[name]
 for m in list(o.modifiers):o.modifiers.remove(m)
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('FacialCurvature','SUBSURF');m.levels=2;bpy.ops.object.modifier_apply(modifier=m.name);o.modifiers.new('Skin','ARMATURE').object=rig
head=union([bpy.data.objects[n]for n in ['Head_Cheeks_Brow','Muzzle_L','Muzzle_R','EyeLid_L','EyeLid_R']],'Feline_CheeksMuzzle_Continuous',.0023,11000)
for side in ['L','R']:
 for prefix in ['WhiskerDot_','Brow_']:
  for o in list(s.objects):
   if o.name.startswith(prefix+side):bpy.data.objects.remove(o,do_unlink=True)
 # Eyeballs remain bound to the actual independent eye bones.
 eye=bpy.data.objects['Eye_'+side];centre=sum((v.co for v in eye.data.vertices),Vector())/len(eye.data.vertices)
 for v in eye.data.vertices:v.co=centre+Vector(((v.co.x-centre.x)*.85,(v.co.y-centre.y)*.82,(v.co.z-centre.z)*.80))
 iris=bpy.data.objects['Iris_'+side];pupil=bpy.data.objects['Pupil_'+side]
 for o in [iris,pupil]:
  c=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
  for v in o.data.vertices:v.co=c+(v.co-c)*.85
 # Existing arm/palm/digits become one continuous weighted hand/forearm surface.
 digit_names=['PawDigit_'+side+str(i)for i in range(4)]
 for i,n in enumerate(digit_names):
  old=bpy.data.objects[n];b1=rig.data.bones[f'digit_{side}_{i}_01'];b2=rig.data.bones[f'digit_{side}_{i}_02'];points=[b1.head_local.lerp(b1.tail_local,t/4)for t in range(5)]+[b1.tail_local.lerp(b2.tail_local,t/4)for t in range(1,5)]
  o=g.tube(n+'_Anatomical',points,[.013,.013,.012,.0125,.012,.0115,.0105,.009,.006],fur,segments=16);o.parent=rig
  groups=[o.vertex_groups.new(name=b1.name),o.vertex_groups.new(name=b2.name)]
  for k in range(9):
   t=max(0,min(1,(k-2)/4));ids=list(range(k*16,(k+1)*16));groups[0].add(ids,1-t,'REPLACE');groups[1].add(ids,t,'REPLACE')
  o.modifiers.new('Skin','ARMATURE').object=rig;bpy.data.objects.remove(old,do_unlink=True)
 arm=bpy.data.objects['Arm_'+side]
 for m in list(arm.modifiers):arm.modifiers.remove(m)
 bpy.context.view_layer.objects.active=arm;m=arm.modifiers.new('ArmCurvature','SUBSURF');m.levels=2;bpy.ops.object.modifier_apply(modifier=m.name);arm.modifiers.new('Skin','ARMATURE').object=rig
 union([arm,bpy.data.objects['PawPalm_'+side]]+[bpy.data.objects[n+'_Anatomical']for n in digit_names],'ContinuousArmPaw_'+side,.0027,10000)
# Original rosette tile at consistent physical density, replacing distorted full-atlas spots.
size=1024;yy,xx=np.mgrid[:size,:size];u=xx/size;v=yy/size;rng=np.random.default_rng(17016);rgb=np.empty((size,size,3));rgb[:]=(.64,.32,.075)
for j in range(7):
 for i in range(7):
  cx=(i+.5+rng.uniform(-.19,.19))/7;cy=(j+.5+rng.uniform(-.19,.19))/7;dx=(u-cx+.5)%1-.5;dy=(v-cy+.5)%1-.5;a=np.arctan2(dy,dx);radius=np.sqrt((dx*1.06)**2+(dy*.90)**2);edge=.031*(1+.18*np.sin(5*a+i)+.1*np.cos(3*a+j));ring=(abs(radius-edge)<.007)&(np.cos(3*a+i)>.05);rgb[ring]=(.035,.018,.009);rgb[radius<edge-.008]=(.40,.17,.038)
rgb*=1+.025*np.sin(xx*1.7)[...,None]*np.cos(yy*1.3)[...,None]
image=bpy.data.images.new('OseboRosetteTile_v003',width=size,height=size,alpha=True);image.pixels.foreach_set(np.dstack((rgb,np.ones((size,size)))).astype(np.float32).ravel());image.filepath_raw=str(OUT/'Osebo_Rosettes.png');image.file_format='PNG';image.save();image.pack();p=fur.node_tree.nodes.get('Principled BSDF')
for link in list(fur.node_tree.links):
 if link.to_socket==p.inputs['Base Color']:fur.node_tree.links.remove(link)
node=fur.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;fur.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color']);p.inputs['Roughness'].default_value=.79;p.inputs['Specular IOR Level'].default_value=.2
for o in [o for o in s.objects if o.type=='MESH']:
 if not any(m==fur for m in o.data.materials):continue
 if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
 o.data.update()
 for polygon in o.data.polygons:
  for li in polygon.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;axis=max(range(3),key=lambda i:abs(polygon.normal[i]));o.data.uv_layers.active.data[li].uv=((v.y if axis==0 else v.x)/.40,(v.y if axis==2 else v.z)/.40)
if cream not in list(head.data.materials):head.data.materials.append(cream)
cream_index=list(head.data.materials).index(cream)
for polygon in head.data.polygons:
 c=polygon.center
 if c.y<-.130 and 1.795<c.z<1.865 and abs(c.x)<.098:polygon.material_index=cream_index
# Actual named geometry and unchanged armature/actions are saved before joined GLB export.
parts=[o for o in s.objects if o.type=='MESH'];s.render.resolution_x=900;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.eevee.taa_render_samples=48
for name in ['front','left','right','back','beauty']:
 s.camera=bpy.data.objects['Camera_'+name];s.render.filepath=str(OUT/(name+'_solid.png'));bpy.ops.render.render(write_still=True)
assert rest()==before and sorted(a.name for a in bpy.data.actions)==actions;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'OseboLeopard.blend'))
copies=[];bpy.ops.object.select_all(action='DESELECT')
for o in parts:
 c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.select_set(True);copies.append(c);o.hide_set(True);o.hide_render=True
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(OUT/'OseboLeopard.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True)
p=OUT/'OseboLeopard.glb';raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
(OUT/'refinement-status.json').write_text(json.dumps({'status':'SOURCE_REFINED_PENDING_NATIVE_AND_CREATIVE_REVIEW','scene_sha256':hashlib.sha256((OUT/'OseboLeopard.blend').read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rest_bones_unchanged':rest()==before,'bones':len(before),'actions':actions,'creative_approved':False,'limitations':['Facial acting, fur detail, cape clearance and reference likeness still require review','Original four-digit paw contract retained; no extra digit or weapon','No campaign species substitution']},indent=2)+'\n')
