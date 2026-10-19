"""Refine the saved Kwaku scene; retain its skeleton/rest matrices/actions.
No source revision is overwritten. Hidden construction remains proposed.
"""
import bpy,math,json,hashlib,struct,sys
from pathlib import Path
from mathutils import Vector,kdtree
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'SourceArt/Characters/Kwaku/Authored_v002/Kwaku.blend'
OUT=ROOT/'SourceArt/Characters/Kwaku/Authored_v006'
if OUT.exists():raise RuntimeError('Preserve the existing revision')
OUT.mkdir(parents=True);bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');factor=1.45/1.70
rest=lambda:[{'name':b.name,'parent':b.parent.name if b.parent else None,'matrix':[list(r)for r in b.matrix_local]}for b in rig.data.bones]
original_rest=rest();original_actions={a.name:sum(len(c.keyframe_points)for c in a.fcurves)if hasattr(a,'fcurves')else len(a.layers)for a in bpy.data.actions}
rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0)
s.frame_set(0)
parts=[o for o in s.objects if o.type=='MESH'];materials={m.name:m for m in bpy.data.materials}
for o in parts:
 for m in list(o.modifiers):
  if m.type=='WIREFRAME':o.modifiers.remove(m)
def weights(o,v):return {o.vertex_groups[g.group].name:g.weight for g in v.groups if g.weight>0 and o.vertex_groups[g.group].name in rig.data.bones}
def sample(objects):
 rows=[]
 for o in objects:
  for v in o.data.vertices:rows.append((o.matrix_world@v.co,weights(o,v)))
 kd=kdtree.KDTree(len(rows))
 for i,(p,w)in enumerate(rows):kd.insert(p,i)
 kd.balance();return kd,rows
skin_parts=[o for o in parts if o.name.startswith(('Torso_','Neck','Head_Facial','Jaw','Nose','Ear_','Arm_','Hand_','Finger_','Leg_','Foot_','Toe_','Lid_'))]
# Soften the original face proportions and retain all existing bone transforms.
def youthful(p):
 p=p.copy();t=max(0,min(1,(p.z/factor-1.40)/.12));t=t*t*(3-2*t)
 p.x*=1+.10*t;p.y*=1+.12*t;p.z+=(p.z-1.47*factor)*.10*t;return p
for o in parts:
 if o.name.startswith(('Head_','Jaw','Nose','Ear_','Neck','Lid_','Eye_','Iris_','Pupil_','Brow_','Mouth','HairCurl')):
  for v in o.data.vertices:v.co=youthful(v.co)
# Reduce exposed sclera and inset the eyes, keeping their rig bindings.
for side in ['L','R']:
 eye=next(o for o in parts if o.name=='Eye_'+side);center=sum((v.co for v in eye.data.vertices),Vector())/len(eye.data.vertices)
 for v in eye.data.vertices:
  d=v.co-center;v.co=center+Vector((d.x*.88,d.y*.72,d.z*.86));v.co.y+=.006
 for prefix in ['Iris_','Pupil_']:
  o=next(o for o in parts if o.name==prefix+side)
  for v in o.data.vertices:v.co.y+=.008
# Weight transfer uses the actual pre-remesh skin, bounded to four influences.
kd,rows=sample(skin_parts)
fusion_parts=[o for o in skin_parts if o.name.startswith(('Torso_','Neck','Head_Facial','Jaw','Nose','Ear_','Lid_'))]
def bind_nearest(obj):
 for g in list(obj.vertex_groups):obj.vertex_groups.remove(g)
 groups={}
 for v in obj.data.vertices:
  combined={}
  for co,index,d in kd.find_n(obj.matrix_world@v.co,4):
   for name,w in rows[index][1].items():combined[name]=combined.get(name,0)+w/max(.0003,d)**2
  chosen=sorted(combined.items(),key=lambda x:x[1],reverse=True)[:4];total=sum(w for n,w in chosen)
  assert total>0
  for name,w in chosen:
   if name not in groups:groups[name]=obj.vertex_groups.new(name=name)
   groups[name].add([v.index],w/total,'REPLACE')
 obj.parent=rig;mod=obj.modifiers.new('Skin','ARMATURE');mod.object=rig

def union(objects,name,voxel):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:
  for m in list(o.modifiers):o.modifiers.remove(m)
  o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 m=o.modifiers.new('ContinuousSurface','REMESH');m.mode='VOXEL';m.voxel_size=voxel;m.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=m.name)
 m=o.modifiers.new('RelaxSurface','SMOOTH');m.factor=.65;m.iterations=3;bpy.ops.object.modifier_apply(modifier=m.name)
 for p in o.data.polygons:p.use_smooth=True
 return o
for o in fusion_parts:
 if o.name.startswith(('Head_Facial','Torso_','Neck','Arm_','Leg_')):
  bpy.context.view_layer.objects.active=o;m=o.modifiers.new('SurfaceCurvature','SUBSURF');m.levels=2 if o.name.startswith('Head_Facial')else 1;bpy.ops.object.modifier_apply(modifier=m.name)
body=union(fusion_parts,'Kwaku_ContinuousSkin',.0035)
bpy.context.view_layer.objects.active=body;m=body.modifiers.new('ControlledTopologyBudget','DECIMATE');m.ratio=min(1,15000/max(1,len(body.data.vertices)));bpy.ops.object.modifier_apply(modifier=m.name);bind_nearest(body)
# Replace the old broad neck plate with connected short sleeves and a real opening.
shirt=next(o for o in s.objects if o.name=='Linen_Shirt');cream=shirt.data.materials[0];sleeves=[]
for vertex in shirt.data.vertices:
 if vertex.co.z>1.36*factor:vertex.co.x*=1.40
for sign,side in [(-1,'L'),(1,'R')]:
 verts=[];faces=[];segments=32
 for cx,cz,rx,ry in [(sign*.185,1.375,.073,.076),(sign*.225,1.26,.073,.074),(sign*.25,1.20,.070,.070)]:
  for j in range(segments):
   angle=j*2*math.pi/segments;verts.append(((cx+rx*math.cos(angle))*factor,ry*math.sin(angle)*factor,cz*factor))
 for ring in range(2):
  for j in range(segments):a=ring*segments+j;b=ring*segments+(j+1)%segments;faces.append((a,b,b+segments,a+segments))
 faces.extend([tuple(reversed(range(segments))),tuple(range(2*segments,3*segments))]);mesh=bpy.data.meshes.new('TailoredSleeve_'+side);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('TailoredSleeve_'+side,mesh);s.collection.objects.link(o);o.data.materials.append(cream);sleeves.append(o)
shirt=union([shirt]+sleeves,'Kwaku_TailoredShortSleeveShirt',.0045)
bpy.context.view_layer.objects.active=shirt;m=shirt.modifiers.new('TailoredMeshBudget','DECIMATE');m.ratio=min(1,6500/max(1,len(shirt.data.vertices)));bpy.ops.object.modifier_apply(modifier=m.name)
# Remove neck volume with an actual Boolean, not a painted dark disk.
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=1,depth=1,location=(0,-.008*factor,1.415*factor));cutter=bpy.context.object;cutter.scale=(.073*factor,.068*factor,.24*factor);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.context.view_layer.objects.active=shirt;m=shirt.modifiers.new('OpenNeckline','BOOLEAN');m.operation='DIFFERENCE';m.object=cutter;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cutter,do_unlink=True)
# Open short sleeve cuffs below the shoulder; leaves the skin arm visible.
import bmesh
bm=bmesh.new();bm.from_mesh(shirt.data);faces=[f for f in bm.faces if abs(f.calc_center_median().x)>.205*factor and f.calc_center_median().z<1.20*factor];bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(shirt.data);bm.free();bind_nearest(shirt)
# Replace bulb-shaped pouches with bevelled leather gussets and flaps.
leather=materials['Leather']
for side,sign in [('L',-1),('R',1)]:
 old=next(o for o in s.objects if o.name=='BeltPouch_'+side);bpy.data.objects.remove(old,do_unlink=True)
 for name,loc,scale in [('Gusset',(sign*.16,-.125,.92),(.045,.026,.063)),('Flap',(sign*.16,-.154,.948),(.047,.008,.028))]:
  bpy.ops.mesh.primitive_cube_add(size=2,location=tuple(x*factor for x in loc));o=bpy.context.object;o.name='Pouch_'+side+'_'+name;o.scale=tuple(x*factor for x in scale);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);m=o.modifiers.new('LeatherSeams','BEVEL');m.width=.006;m.segments=3;bpy.ops.object.modifier_apply(modifier=m.name);o.data.materials.append(leather);g=o.vertex_groups.new(name='pelvis');g.add(list(range(len(o.data.vertices))),1,'REPLACE');o.parent=rig;m=o.modifiers.new('Skin','ARMATURE');m.object=rig
# Contiguous upper/lower eyelid rim with an actual closing target on the export mesh.
for side,sign in [('L',-1),('R',1)]:
 old=bpy.data.objects.get('Lid_'+side)
 if old:bpy.data.objects.remove(old,do_unlink=True)
 center=youthful(Vector((sign*.044*factor,-.098*factor,1.604*factor)));verts=[];n=32
 for inner in [False,True]:
  rx=(.031 if not inner else .022)*factor;rz=(.022 if not inner else .0100)*factor
  for i in range(n):
   a=i*2*math.pi/n;verts.append(tuple(center+Vector((rx*math.cos(a),(.014 if not inner else -.0005)*factor,rz*math.sin(a)))))
 faces=[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];mesh=bpy.data.meshes.new('LidSurface_'+side);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('LidSurface_'+side,mesh);s.collection.objects.link(o);o.data.materials.append(materials['Skin']);g=o.vertex_groups.new(name='head');g.add(list(range(n*2)),1,'REPLACE');g=o.vertex_groups.new(name='facial_blink_'+side);g.add(list(range(n,n*2)),1,'REPLACE');o.parent=rig;m=o.modifiers.new('Skin','ARMATURE');m.object=rig;o['blink_center_z']=center.z
# Actual UVs for new continuous surfaces.
for o in [body,shirt]:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(65),island_margin=.012);bpy.ops.object.mode_set(mode='OBJECT')
# Original procedural woven albedo/normal maps; embedded in interchange bytes.
import numpy as np
size=512;y,x=np.mgrid[0:size,0:size];u=x/size;v=y/size
for matname,base,motif in [('Cream_Linen',(.63,.49,.31),False),('Indigo_Woven',(.018,.042,.12),False),('Leather',(.075,.030,.013),False),('Hair_Pupil',(.008,.004,.002),False)]:
 m=materials[matname];p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.86 if matname!='Leather'else .72;p.inputs['Specular IOR Level'].default_value=.16
 grain=.96+.025*np.sin(x*math.pi*.5)+.015*np.cos(y*math.pi*.5);rgb=np.clip(grain[...,None]*np.array(base),0,1)
 if motif:
  xx=(u*8)%1;yy=(v*8)%1;chev=(abs(yy-.5-abs(xx-.5)*.65)<.055);borders=(xx<.055)|(xx>.945);rgb=np.where((chev|borders)[...,None],np.array((.56,.30,.07)),rgb)
 image=bpy.data.images.new(matname+'_WovenAlbedo_v003',width=size,height=size,alpha=True);rgba=np.dstack((rgb,np.ones((size,size)))).astype(np.float32);image.pixels.foreach_set(rgba.ravel());image.filepath_raw=str(OUT/(matname+'_albedo.png'));image.file_format='PNG';image.save();image.pack();node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
amber=materials['Amber'].node_tree.nodes.get('Principled BSDF');amber.inputs['Base Color'].default_value=(.065,.023,.006,1);amber.inputs['Roughness'].default_value=.25
for o in [o for o in s.objects if o.type=='MESH'and o.name.startswith('HairCurl')]:
 for modifier in list(o.modifiers):o.modifiers.remove(modifier)
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('CurlSilhouetteBudget','DECIMATE');m.ratio=.35;bpy.ops.object.modifier_apply(modifier=m.name);g=o.vertex_groups.get('head')or o.vertex_groups.new(name='head');g.add(list(range(len(o.data.vertices))),1,'REPLACE');m=o.modifiers.new('Skin','ARMATURE');m.object=rig
# Save preserved named parts plus an explicit single native export mesh, with morphs.
parts=[o for o in s.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in parts:
 c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();export=bpy.context.object;export.name='SK_Kwaku';export.shape_key_add(name='Basis')
for side in ['L','R']:
 key=export.shape_key_add(name='Blink_'+side);group=export.vertex_groups['facial_blink_'+side];center=next(o['blink_center_z']for o in parts if o.name=='LidSurface_'+side)
 for vertex in export.data.vertices:
  if any(g.group==group.index and g.weight>.5 for g in vertex.groups):key.data[vertex.index].co.z=center;key.data[vertex.index].co.y-=.0035
# Diagnostic groups never become bones; source weights remain normalized on bone groups.
for o in parts:o.hide_render=True
s.render.resolution_x=900;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.eevee.taa_render_samples=64
for name in ['Key','Fill','Rim']:
 light=bpy.data.objects.get(name)
 if light:light.data.energy={'Key':450,'Fill':180,'Rim':280}[name];light.data.size=3
for b in rig.pose.bones:b.rotation_euler=(0,0,0)
assert rest()==original_rest
bpy.context.view_layer.objects.active=export;export.hide_render=False
# Views use the actual refined, skinned native export geometry.
for name in ['front','left','right','back','beauty']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(OUT/(name+'_solid.png'));bpy.ops.render.render(write_still=True)
export.data.shape_keys.key_blocks['Blink_L'].value=1;export.data.shape_keys.key_blocks['Blink_R'].value=1;s.camera=bpy.data.objects['beauty'];s.render.filepath=str(OUT/'blink_closed.png');bpy.ops.render.render(write_still=True)
for key in export.data.shape_keys.key_blocks:key.value=0
for side in ['L','R']:rig.pose.bones['upperarm_'+side].rotation_euler.x=-.9;rig.pose.bones['lowerarm_'+side].rotation_euler.x=-.7
s.render.filepath=str(OUT/'deformation_review.png');bpy.ops.render.render(write_still=True)
for b in rig.pose.bones:b.rotation_euler=(0,0,0)
s.camera=bpy.data.objects['beauty'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kwaku.blend'))
bpy.ops.object.select_all(action='DESELECT');export.select_set(True);rig.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'Kwaku.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
p=OUT/'Kwaku.glb';raw=p.read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length]);doc['asset'].pop('generator',None);payload=json.dumps(doc,separators=(',',':')).encode();payload+=b' '*((-len(payload))%4);tail=raw[20+length:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(tail))+struct.pack('<II',len(payload),0x4e4f534a)+payload+tail)
report={'status':'REFINED_WIP_REQUIRES_RENDER_DEFORMATION_AND_NATIVE_REVIEW','source_revision':'Authored_v002','design_id':'kwaku-human-v1','scene_sha256':hashlib.sha256((OUT/'Kwaku.blend').read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'original_scene_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'rest_bones_unchanged':rest()==original_rest,'bone_count':len(rig.data.bones),'actions_before':original_actions,'actions_after':[a.name for a in bpy.data.actions],'morph_targets':['Blink_L','Blink_R'],'height_proposal_m':1.45,'vertices':len(export.data.vertices),'triangles':sum(len(f.vertices)-2 for f in export.data.polygons),'creative_approved':False,'limitations':['Reference resemblance and deformation require human review','No final voice/lip-sync or full hand IK','Source armature/rest/actions retained; runtime import still pending']}
(OUT/'refinement-status.json').write_text(json.dumps(report,indent=2)+'\n');print('KWAKU_REFINEMENT_SAVED',len(export.data.vertices))
