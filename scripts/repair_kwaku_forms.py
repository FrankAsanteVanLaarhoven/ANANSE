"""Repair editable Kwaku surfaces without changing the existing rig or actions."""
import bpy, math, json, hashlib, struct, sys
from pathlib import Path
from mathutils import Vector, kdtree
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'SourceArt/Characters/Kwaku/Authored_v006/Kwaku.blend'
OUT=ROOT/'SourceArt/Characters/Kwaku/Authored_v008'
assert not OUT.exists(), 'Preserve existing source revisions'
OUT.mkdir(parents=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.context.scene
rig=next(o for o in s.objects if o.type=='ARMATURE')
rest=lambda:[(b.name,b.parent.name if b.parent else None,tuple(v for row in b.matrix_local for v in row))for b in rig.data.bones]
before=rest(); actions=sorted(a.name for a in bpy.data.actions)
rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
s.frame_set(0)
bpy.data.objects.remove(bpy.data.objects['SK_Kwaku'],do_unlink=True)
sys.path.insert(0,str(ROOT/'scripts'))
import character_mesh_tools as g
g.scene=s;g.parts=[];g.binds={}
mats={m.name:m for m in bpy.data.materials}

def bind(o,bone):
 for group in list(o.vertex_groups):o.vertex_groups.remove(group)
 o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE')
 o.parent=rig
 for m in list(o.modifiers):o.modifiers.remove(m)
 o.modifiers.new('Skin','ARMATURE').object=rig
 return o

def nearest_union(objects,name,voxel):
 samples=[]
 for o in objects:
  for v in o.data.vertices:
   weights={o.vertex_groups[a.group].name:a.weight for a in v.groups if o.vertex_groups[a.group].name in rig.data.bones and a.weight>0}
   samples.append((o.matrix_world@v.co,weights))
 kd=kdtree.KDTree(len(samples))
 for i,(p,w)in enumerate(samples):kd.insert(p,i)
 kd.balance();bpy.ops.object.select_all(action='DESELECT')
 for o in objects:
  for m in list(o.modifiers):o.modifiers.remove(m)
  o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 m=o.modifiers.new('SurfaceJoin','REMESH');m.mode='VOXEL';m.voxel_size=voxel;m.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=m.name)
 m=o.modifiers.new('SurfaceRelax','SMOOTH');m.factor=.35;m.iterations=2;bpy.ops.object.modifier_apply(modifier=m.name)
 m=o.modifiers.new('LimbTopologyBudget','DECIMATE');m.ratio=min(1,6500/max(1,len(o.data.vertices)));bpy.ops.object.modifier_apply(modifier=m.name)
 for gr in list(o.vertex_groups):o.vertex_groups.remove(gr)
 groups={}
 for v in o.data.vertices:
  w={}
  for p,i,d in kd.find_n(o.matrix_world@v.co,4):
   for n,a in samples[i][1].items():w[n]=w.get(n,0)+a/max(.0001,d)**2
  chosen=sorted(w.items(),key=lambda x:x[1],reverse=True)[:4];total=sum(a for n,a in chosen);assert total>0
  for n,a in chosen:
   if n not in groups:groups[n]=o.vertex_groups.new(name=n)
   groups[n].add([v.index],a/total,'REPLACE')
 for face in o.data.polygons:face.use_smooth=True
 o.modifiers.new('Skin','ARMATURE').object=rig;o.parent=rig
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
 return o

# Continuous wrist/ankle joins. Digits retain their independent existing weights.
for side in ['L','R']:
 arm=bpy.data.objects['Arm_'+side];hand=bpy.data.objects['Hand_'+side]
 for v in hand.data.vertices:
  v.co.y=-.025+(v.co.y+.025)*.82
  if v.co.z>.77:v.co.z+=.012*((v.co.z-.77)/.031)
 bpy.context.view_layer.objects.active=arm
 m=arm.modifiers.new('ArmCurvature','SUBSURF');m.levels=2;bpy.ops.object.modifier_apply(modifier=m.name)
 sign=-1 if side=='L' else 1
 bridge=bind(g.tube('WristBridge_'+side,[(sign*.277,0,.845),(sign*.277,-.015,.80),(sign*.277,-.025,.77)],[.028,.024,.025],mats['Skin']),'hand_'+side)
 nearest_union([arm,hand,bridge],'ContinuousArmHand_'+side,.0018)
 leg=bpy.data.objects['Leg_'+side];foot=bpy.data.objects['Foot_'+side]
 for v in leg.data.vertices:
  if v.co.z<.15:
   t=max(0,(.15-v.co.z)/.061);v.co.z-=.026*t;v.co.y-=.025*t
 bpy.context.view_layer.objects.active=leg;m=leg.modifiers.new('LegCurvature','SUBSURF');m.levels=1;bpy.ops.object.modifier_apply(modifier=m.name)
 bridge=bind(g.tube('AnkleBridge_'+side,[(sign*.098,0,.18),(sign*.098,-.012,.12),(sign*.098,-.025,.07)],[.033,.033,.033],mats['Skin']),'foot_'+side)
 nearest_union([leg,foot,bridge],'ContinuousLegFoot_'+side,.002)
 sole=bpy.data.objects['SandalSole_'+side]
 for v in sole.data.vertices:v.co.z=max(0,(v.co.z-.0068)*1.2345)

# Raise the neckline into the neck base; authoritative bones/capsule do not move.
shirt=bpy.data.objects['Kwaku_TailoredShortSleeveShirt']
for v in shirt.data.vertices:
 t=max(0,min(1,(v.co.z-1.10)/.077));v.co.z+=.043*t*(1-min(1,abs(v.co.x)/.25))
collar=g.loft('SewnNeckOpening',[(0,0,1.175,.069,.063),(0,0,1.210,.061,.055),(0,0,1.235,.053,.048)],mats['Cream_Linen'],segments=48)
# Remove caps so the collar has a real opening.
import bmesh
bm=bmesh.new();bm.from_mesh(collar.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if len(f.verts)>4],context='FACES');bm.to_mesh(collar.data);bm.free();bind(collar,'neck')
body=bpy.data.objects['Kwaku_ContinuousSkin']
for v in body.data.vertices:
 p=v.co
 if 1.19<p.z<1.295 and abs(p.x)<.065:
  t=max(0,1-abs(p.z-1.235)/.06);p.x*=1-.16*t;p.y*=1-.12*t
 # Local nose falloff; preserve head bounds and eye bone placement.
 q=((p.x/.033)**2+((p.z-1.343)/.032)**2)
 if p.y<-.085 and q<1:p.y+=.014*(1-q);p.x*=1-.10*(1-q)

# Replace displaced free-floating trim with a curved, UV-mapped woven ribbon.
for o in list(s.objects):
 if o.name.startswith(('DiagonalSash','SashWovenEdge','WovenChevron','LidSurface','Mouth')):bpy.data.objects.remove(o,do_unlink=True)
size=512;y,x=np.mgrid[:size,:size];u=x/size;v=y/size
grain=.95+.025*np.sin(x*math.pi*.5)+.02*np.cos(y*math.pi*.5)
rgb=grain[...,None]*np.array((.018,.043,.105));tile=(v*12)%1
motif=(abs(tile-.5-abs((u*3)%1-.5)*.65)<.048)| (u<.035)|(u>.965)
rgb=np.where(motif[...,None],np.array((.62,.34,.09)),rgb)
image=bpy.data.images.new('KwakuWovenRibbon_v007',width=size,height=size,alpha=True);image.pixels.foreach_set(np.dstack([rgb,np.ones((size,size))]).astype(np.float32).ravel());image.filepath_raw=str(OUT/'WovenRibbon_albedo.png');image.file_format='PNG';image.save();image.pack()
woven=mats['Indigo_Woven'].copy();woven.name='IndigoWoven_v007';node=woven.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;woven.node_tree.links.new(node.outputs['Color'],woven.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
verts=[];uv=[];faces=[];a=Vector((-.125,-.125,1.215));b=Vector((.135,-.126,.835));direction=(b-a).normalized();across=Vector((-direction.z,0,direction.x))
for i in range(25):
 t=i/24;centre=a.lerp(b,t);centre.y-=.006*math.sin(math.pi*t)
 for j in range(7):verts.append(tuple(centre+across*((j/6-.5)*.105)));uv.append((j/6,t))
for i in range(24):
 for j in range(6):k=i*7+j;faces.append((k,k+1,k+8,k+7))
ribbon=g.mesh('FittedWovenSash',verts,faces,woven,uv=uv);bind(ribbon,'chest');m=ribbon.modifiers.new('ClothThickness','SOLIDIFY');m.thickness=.0025;bpy.context.view_layer.objects.active=ribbon;bpy.ops.object.modifier_apply(modifier=m.name)
tab=bpy.data.objects['TabardFront'];tab.data.materials.clear();tab.data.materials.append(woven)
for poly in tab.data.polygons:
 for li in poly.loop_indices:
  p=tab.data.vertices[tab.data.loops[li].vertex_index].co;tab.data.uv_layers.active.data[li].uv=((p.x+.067)/.134,(p.z-.409)/.41)
trouser=mats['Cream_Linen'].copy();trouser.name='TrouserTwill_v007';p=trouser.node_tree.nodes.get('Principled BSDF')
for link in list(trouser.node_tree.links):
 if link.to_socket==p.inputs['Base Color']:trouser.node_tree.links.remove(link)
p.inputs['Base Color'].default_value=(.19,.135,.082,1)
for side in ['L','R']:
 o=bpy.data.objects['CroppedTrousers_'+side];o.data.materials.clear();o.data.materials.append(trouser)

# Curved upper/lower lids actually cover the eye surface at closure.
eyes={}
for side in ['L','R']:
 eye=bpy.data.objects['Eye_'+side];co=[v.co for v in eye.data.vertices];centre=Vector(tuple((min(v[i]for v in co)+max(v[i]for v in co))/2 for i in range(3)));centre.y=-.084;eyes[side]=centre
 for upper in [True,False]:
  verts=[];faces=[];sign=1 if upper else -1
  for j in range(13):
   beta=sign*(.44+(math.pi/2-.44)*j/12)
   for i in range(25):
    alpha=-math.pi/2+math.pi*i/24;verts.append(tuple(centre+Vector((.024*math.cos(beta)*math.sin(alpha),-.017*math.cos(beta)*math.cos(alpha),.017*math.sin(beta)))))
  for j in range(12):
   for i in range(24):k=j*25+i;faces.append((k,k+1,k+26,k+25))
  o=g.mesh(('UpperLid_'if upper else'LowerLid_')+side,verts,faces,mats['Skin']);bind(o,'head');o.vertex_groups.new(name='lid_'+side).add(list(range(len(verts))),1,'REPLACE')
lip=mats['Skin'].copy();lip.name='LipSkin_v007';lip.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.105,.035,.024,1)
for upper in [True,False]:
 points=[(-.027,-.095,1.310),(-.013,-.101,1.312 if upper else 1.305),(0,-.103,1.311 if upper else 1.303),(.013,-.101,1.312 if upper else 1.305),(.027,-.095,1.310)]
 bind(g.tube('UpperLip'if upper else'LowerLip',points,[.0015,.0025,.003,.0025,.0015],lip),'jaw')

# Export mesh is built from the same editable parts; only source bones bind skin.
parts=[o for o in s.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in parts:
 c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.hide_render=False;c.hide_viewport=False;c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();export=bpy.context.object;export.name='SK_Kwaku';export.shape_key_add(name='Basis')
for side in ['L','R']:
 key=export.shape_key_add(name='Blink_'+side);group=export.vertex_groups['lid_'+side];centre=eyes[side]
 for vertex in export.data.vertices:
  if not any(a.group==group.index and a.weight>.5 for a in vertex.groups):continue
  p=vertex.co-centre;beta=math.asin(max(-1,min(1,p.z/.017)));alpha=math.atan2(p.x/.024,-p.y/.017);sign=1 if beta>=0 else-1;t=max(0,min(1,(abs(beta)-.44)/(math.pi/2-.44)));closed=sign*(t*math.pi/2-.055*(1-t))
  key.data[vertex.index].co=centre+Vector((.024*math.cos(closed)*math.sin(alpha),-.017*math.cos(closed)*math.cos(alpha),.017*math.sin(closed)))
for o in parts:o.hide_render=True;o.hide_set(True)
export.hide_render=False;export.hide_set(False)
assert rest()==before and sorted(a.name for a in bpy.data.actions)==actions
s.render.resolution_x=900;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.eevee.taa_render_samples=48
for name in ['front','left','right','back','beauty']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(OUT/(name+'_solid.png'));bpy.ops.render.render(write_still=True)
for side in ['L','R']:export.data.shape_keys.key_blocks['Blink_'+side].value=1
s.camera=bpy.data.objects['front'];s.render.filepath=str(OUT/'blink_closed.png');bpy.ops.render.render(write_still=True)
# Ray samples inspect actual evaluated lids, not requested target values.
evaluated=export.evaluated_get(bpy.context.evaluated_depsgraph_get());hits=[]
for side,centre in eyes.items():
 for dx in [-.009,0,.009]:
  for dz in [-.004,0,.004]:
   hit,p,n,index=evaluated.ray_cast(Vector((centre.x+dx,-2,centre.z+dz)),Vector((0,1,0)));material=evaluated.data.materials[evaluated.data.polygons[index].material_index].name if hit else'NONE';hits.append({'side':side,'dx':dx,'dz':dz,'material':material});assert material=='Skin',(side,dx,dz,material)
for k in export.data.shape_keys.key_blocks:k.value=0
for side in ['L','R']:rig.pose.bones['upperarm_'+side].rotation_euler.x=-.9;rig.pose.bones['lowerarm_'+side].rotation_euler.x=-.7
s.camera=bpy.data.objects['beauty'];s.render.filepath=str(OUT/'deformation_review.png');bpy.ops.render.render(write_still=True)
for b in rig.pose.bones:b.rotation_euler=(0,0,0)
s.camera=bpy.data.objects['beauty'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kwaku.blend'))
bpy.ops.object.select_all(action='DESELECT');export.select_set(True);rig.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'Kwaku.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
p=OUT/'Kwaku.glb';raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
status={'status':'REPAIRED_WIP_PENDING_NATIVE_AND_CREATIVE_REVIEW','scene_sha256':hashlib.sha256((OUT/'Kwaku.blend').read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rest_bones_unchanged':rest()==before,'actions':actions,'bone_count':len(before),'vertices':len(export.data.vertices),'triangles':sum(len(p.vertices)-2 for p in export.data.polygons),'closed_eye_evaluated_ray_samples':hits,'creative_approved':False,'limitations':['Independent digit posing and sleeve/neck clearance still require visual review','Original proportions/skeleton/eleven clips retained','No final facial acting, recordings or platform acceptance']}
(OUT/'refinement-status.json').write_text(json.dumps(status,indent=2)+'\n')
print('REPAIRED_SOURCE_SAVED',len(export.data.vertices))
