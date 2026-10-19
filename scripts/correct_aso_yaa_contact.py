"""Versioned Aso garment welding, grasp poses and source-derived ledger motion.
Retains the exact rest skeleton; all proposed art remains subject to review.
"""
import bpy,math,json,hashlib,struct,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1];OUT=R/'SourceArt/Characters/AsoYaa/Authored_v017';assert not OUT.exists();OUT.mkdir(parents=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceArt/Characters/AsoYaa/Authored_v007/AsoYaa.blend'));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0);b.location=(0,0,0)
s.frame_set(0);bpy.data.objects.remove(bpy.data.objects['SK_AsoYaa'],do_unlink=True)
rest=[(b.name,b.parent.name if b.parent else None,list(v for row in b.matrix_local for v in row))for b in rig.data.bones]
sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g
g.scene=s;g.parts=[];g.binds={}
# Join and voxel-weld actual robe/sleeve/yoke sheets, with thickness before union.
clothes=[o for o in s.objects if o.type=='MESH'and o.name.startswith(('IndigoOpenRobe','ShoulderYoke_'))];samples=[]
for o in clothes:
 for v in o.data.vertices:samples.append((o.matrix_world@v.co,{o.vertex_groups[a.group].name:a.weight for a in v.groups}))
 for mod in list(o.modifiers):o.modifiers.remove(mod)
 o.hide_render=False;o.hide_set(False)
 sol=o.modifiers.new('SewnThickness','SOLIDIFY');sol.thickness=.006;sol.offset=0
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sol.name)
bpy.ops.object.select_all(action='DESELECT')
for o in clothes:o.select_set(True)
bpy.context.view_layer.objects.active=clothes[0];bpy.ops.object.join();robe=bpy.context.object;robe.name='ContinuousTailoredRobe';robe.data.remesh_voxel_size=.006;bpy.ops.object.voxel_remesh();kd=KDTree(len(samples))
for i,(p,row)in enumerate(samples):kd.insert(p,i)
kd.balance()
for group in list(robe.vertex_groups):robe.vertex_groups.remove(group)
groups={}
for v in robe.data.vertices:
 hits=kd.find_n(robe.matrix_world@v.co,4);weights={}
 for p,i,dist in hits:
  for n,w in samples[i][1].items():weights[n]=weights.get(n,0)+w/max(.001,dist)**2
 top=sorted(weights.items(),key=lambda p:-p[1])[:4];total=sum(w for n,w in top)
 for n,w in top:
  if n not in groups:groups[n]=robe.vertex_groups.new(name=n)
  groups[n].add([v.index],w/total,'REPLACE')
# Smooth transferred fields on connected topology: nearest-sample discontinuities
# otherwise tear the apparent surface around the axilla under large arm rotation.
adj=[set()for _ in robe.data.vertices]
for edge in robe.data.edges:
 a,b=edge.vertices;adj[a].add(b);adj[b].add(a)
fields=[{robe.vertex_groups[q.group].name:q.weight for q in v.groups}for v in robe.data.vertices]
for iteration in range(40):
 nextfields=[]
 for i,v in enumerate(robe.data.vertices):
  if v.co.z<.98 or not adj[i]:nextfields.append(fields[i]);continue
  row={n:w*.45 for n,w in fields[i].items()}
  for j in adj[i]:
   for n,w in fields[j].items():row[n]=row.get(n,0)+.55*w/len(adj[i])
  nextfields.append(row)
 fields=nextfields
for group in list(robe.vertex_groups):robe.vertex_groups.remove(group)
groups={}
for i,row in enumerate(fields):
 top=sorted(row.items(),key=lambda p:-p[1])[:4];total=sum(w for n,w in top)
 for n,w in top:
  if n not in groups:groups[n]=robe.vertex_groups.new(name=n)
  groups[n].add([i],w/total,'REPLACE')
robe.parent=rig;robe.modifiers.new('Deform','ARMATURE').object=rig
# Actual mild smoothing removes voxel stair-stepping, not a render-only seam cover.
mod=robe.modifiers.new('TailoringSurface','SMOOTH');mod.factor=.45;mod.iterations=3;bpy.context.view_layer.objects.active=robe;bpy.ops.object.modifier_apply(modifier=mod.name)
for p in robe.data.polygons:p.use_smooth=True
uv=robe.data.uv_layers.new(name='TailoredUV')
for polygon in robe.data.polygons:
 for li in polygon.loop_indices:
  co=robe.data.vertices[robe.data.loops[li].vertex_index].co;uv.data[li].uv=(.5+co.x,co.z/1.68)

# Set-in sleeves remain distinct sewn pieces. Welding the entire low-rest arm
# into the torso creates an invalid shared armpit surface when the elbow rises.
for side in ['L','R']:
 sleeve=bpy.data.objects['TailoredSleeve_'+side]
 # Flared upper sleeve overlaps the actual yoke seam without joining torso below it.
 for i,v in enumerate(sleeve.data.vertices):
  ring=i//32
  if ring<3:
   c=rig.data.bones['upperarm_'+side].head_local.lerp(rig.data.bones['upperarm_'+side].tail_local,ring/6)
   v.co=c+(v.co-c)*1.08
# More deliberate finger taper/knuckle volume; preserve approved bone identities.
for o in s.objects:
 if o.type=='MESH'and o.name.startswith('ArticulatedDigit_'):
  for i,v in enumerate(o.data.vertices):
   ring=i//12;v.co.y+=.0015*math.sin(math.pi*ring/8)+(.0021 if not o.name.endswith('0')else 0)
# Correct previously inflated palm thickness while retaining knuckle width/length.
for side in ['L','R']:
 palm=bpy.data.objects['Palm_'+side];centre=rig.data.bones['hand_'+side].head_local.lerp(rig.data.bones['hand_'+side].tail_local,.55)
 for v in palm.data.vertices:v.co.y=centre.y+(v.co.y-centre.y)*(.012/.022)-.009
# Thumb skin follows the retained thumb pivots rather than an offset tube.
for side in ['L','R']:
 old=bpy.data.objects['ArticulatedDigit_'+side+'0'];bpy.data.objects.remove(old,do_unlink=True)
 a=rig.data.bones[f'digit_{side}_0_01'];b=rig.data.bones[f'digit_{side}_0_02'];points=[a.head_local.lerp(a.tail_local,i/4)for i in range(5)]+[b.head_local.lerp(b.tail_local,i/4)for i in range(1,5)]
 o=g.tube('ArticulatedThumb_'+side,points,[.0065,.0065,.0065,.006,.0055,.0052,.005,.0045,.0038],bpy.data.materials['Skin'],segments=12)
 for i in range(9):
  t=max(0,min(1,(i-2)/4))
  for name,w in [(a.name,1-t),(b.name,t)]:
   if w>0:
    group=o.vertex_groups.get(name)or o.vertex_groups.new(name=name);group.add(list(range(i*12,(i+1)*12)),w,'REPLACE')
 o.parent=rig;o.modifiers.new('Deform','ARMATURE').object=rig
# CCD-free analytic two-bone authoring: shoulder/elbow/wrist transforms baked to existing bones.
def frame_matrix(head,direction,normal):
 y=direction.normalized();x=y.cross(normal).normalized();z=x.cross(y).normalized();return Matrix(((x.x,y.x,z.x,head.x),(x.y,y.y,z.y,head.y),(x.z,y.z,z.z,head.z),(0,0,0,1)))
def arm(side,wrist,direction):
 up=rig.pose.bones['upperarm_'+side];lo=rig.pose.bones['lowerarm_'+side];hand=rig.pose.bones['hand_'+side];shoulder=up.head.copy();a=up.length;b=lo.length;delta=wrist-shoulder;dist=delta.length;axis=delta.normalized();dist=min(dist,a+b-.0001);c=(a*a+dist*dist-b*b)/(2*dist);height=math.sqrt(max(0,a*a-c*c));pole=Vector((-1 if side=='L'else 1,.2,-.4));pole=(pole-axis*pole.dot(axis)).normalized();elbow=shoulder+axis*c+pole*height

 def aligned(bone,origin,direction):
  restbone=bone.bone;restrot=restbone.matrix_local.to_quaternion();turn=(restbone.tail_local-restbone.head_local).normalized().rotation_difference(direction.normalized());return Matrix.LocRotScale(origin,turn@restrot,Vector((1,1,1)))
 up.matrix=aligned(up,shoulder,elbow-shoulder);bpy.context.view_layer.update();lo.matrix=aligned(lo,elbow,wrist-elbow);bpy.context.view_layer.update();hand.matrix=frame_matrix(wrist,direction,Vector((0,0,-1)));bpy.context.view_layer.update()
# New contact performance replaces only InspectEvidence; other identity clips retained.
action=bpy.data.actions['InspectEvidence'];action.fcurves.clear();rig.animation_data.action=action
phases=[(0,'approach'),(24,'reach'),(48,'first_contact'),(72,'secure_hold'),(108,'inspect'),(144,'gesture_holding'),(180,'return'),(204,'release'),(240,'settle')]
# Right hand grips the right edge, left hand supports the left. Rigid book follows hand_R only after contact.
contact_frames=[];grips={}
for frame in sorted({f for f,label in phases}|set(range(48,181))):
 label=next((name for f,name in phases if f==frame),'held_contact_bake')
 s.frame_set(frame)
 for b in rig.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0)
 bpy.context.view_layer.update()
 if 48<=frame<=180:
  lift=.10*math.sin(math.pi*(frame-48)/132);centre=Vector((0,-.30,1.03+lift));tilt=.12*math.sin(math.pi*(frame-48)/132)
  for side,sign in [('L',-1),('R',1)]:
   arm(side,centre+Vector((sign*.178,0,-.026)),Vector((-sign,0,0)))
   for d in range(5):
    rig.pose.bones[f'digit_{side}_{d}_01'].rotation_euler.x=-.12 if d else .48;rig.pose.bones[f'digit_{side}_{d}_02'].rotation_euler.x=-.08 if d else .40
  bpy.context.view_layer.update()
  for side,sign in [('L',-1),('R',1)]:
   first=rig.pose.bones[f'digit_{side}_0_01'];second=rig.pose.bones[f'digit_{side}_0_02'];start=first.head.copy();target=centre+Vector((sign*.117,.025,0));v=target-start;length=min(v.length,first.length+second.length-.0001);axis=v.normalized();along=(first.length**2+length**2-second.length**2)/(2*length);pole=Vector((sign,0,0));pole=(pole-axis*pole.dot(axis)).normalized();joint=start+axis*along+pole*math.sqrt(max(0,first.length**2-along**2))
   for bone,origin,direction in [(first,start,joint-start),(second,joint,target-joint)]:
    restbone=bone.bone;turn=(restbone.tail_local-restbone.head_local).normalized().rotation_difference(direction.normalized());bone.matrix=Matrix.LocRotScale(origin,turn@restbone.matrix_local.to_quaternion(),Vector((1,1,1)));bpy.context.view_layer.update()
  rig.pose.bones['head'].rotation_euler.x=.12;rig.pose.bones['spine_01'].rotation_euler.x=.025
 elif frame in [24,204]:
  for side,sign in [('L',-1),('R',1)]:arm(side,Vector((sign*.15,-.22,.98)),Vector((-sign,-.15,-.15)))
 for b in rig.pose.bones:
  b.keyframe_insert(data_path='rotation_euler',frame=frame);b.keyframe_insert(data_path='location',frame=frame)
 bpy.context.view_layer.update()
 if frame==48:
  book=Matrix.Translation(centre);grips['ledger_to_hand_R']=[list(row)for row in rig.pose.bones['hand_R'].matrix.inverted()@book]
# Distinct actual finger poses for existing performances, not duplicate clip renames.
pose_patterns={'IdleStrategist':(.12,.10,.15,.19,.22),'NegotiateOpen':(.06,.04,.08,.13,.19),'NegotiateFirm':(.25,.03,.48,.55,.6),'Agreement':(.28,.24,.27,.31,.35),'Refusal':(.08,.02,.06,.09,.12),'ProtectWitnesses':(.17,.05,.10,.15,.22)}
for name,values in pose_patterns.items():
 act=bpy.data.actions[name];rig.animation_data.action=act
 for frame in [0,22,45,68,90]:
  s.frame_set(frame);a=math.sin(math.pi*frame/90)**2
  for side in ['L','R']:
   for d,val in enumerate(values):
    for segment in [1,2]:
     b=rig.pose.bones[f'digit_{side}_{d}_0{segment}'];b.rotation_euler.x=val*a*(1 if segment==1 else .7);b.keyframe_insert(data_path='rotation_euler',frame=frame)
rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0)
s.frame_set(0)
# Editable rigid prop, separately exported; not fused into the character.
cover=g.material('Ledger_IndigoLeather',(.035,.06,.105),rough=.7);paper=g.material('Ledger_Paper',(.60,.48,.29),rough=.9)
ledgerparts=[]
for name,z,dim,mat in [('Ledger_PageBlock',0,(.22,.16,.018),paper),('Ledger_CoverBottom',-.012,(.23,.17,.005),cover),('Ledger_CoverTop',.012,(.23,.17,.005),cover)]:
 bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.name=name;o.scale=dim;o.location=(0,0,z);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);ledgerparts.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in ledgerparts:o.select_set(True)
bpy.context.view_layer.objects.active=ledgerparts[0];bpy.ops.object.join();ledger=bpy.context.object;ledger.name='Ledger_SeparateProp';ledger.hide_render=True;ledger.hide_set(True)
parts=[o for o in s.objects if o.type=='MESH'and o!=ledger]
bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in parts:
 c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.hide_render=False;c.hide_set(False);c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='SK_AsoYaa'
for o in parts:o.hide_render=True;o.hide_set(True)
assert rest==[(b.name,b.parent.name if b.parent else None,list(v for row in b.matrix_local for v in row))for b in rig.data.bones]
for key in mesh.data.shape_keys.key_blocks:key.value=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'AsoYaa.blend'))
def export(obj,path,animations=False):
 bpy.ops.object.select_all(action='DESELECT');obj.hide_set(False);obj.select_set(True)
 if animations:rig.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_animations=animations,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=animations,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=animations)
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
export(mesh,OUT/'AsoYaa.glb',True);mesh.hide_set(True);ledger.hide_render=False;export(ledger,OUT/'Ledger.glb');ledger.hide_render=True;ledger.hide_set(True);mesh.hide_set(False)
report=json.loads((R/'SourceArt/Characters/AsoYaa/Authored_v007/rig-map.json').read_text());report.update(scene_sha256=hashlib.sha256((OUT/'AsoYaa.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((OUT/'AsoYaa.glb').read_bytes()).hexdigest(),vertices=len(mesh.data.vertices),correction='Voxel-welded robe/yoke/sleeves with transferred normalized weights; distinct digit poses; baked two-hand ledger reach/hold/return. Technical contact acceptance PENDING, art REVIEW_REQUIRED.',ledger={'phases':phases,**grips,'size_m':[.23,.17,.029],'contact_qualified':False},creative_approved=False)
for a in report['actions']:
 if a['name']=='InspectEvidence':a.update(frames=241,seconds=8.0)
(OUT/'rig-map.json').write_text(json.dumps(report,indent=2)+'\n');print('ASO_CORRECTIVE_SOURCE',report['scene_sha256'])
