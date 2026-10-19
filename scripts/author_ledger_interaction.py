"""Author a two-hand ledger pose against real prop geometry on the existing rig."""
import bpy,math,json,hashlib,struct,sys
from pathlib import Path
from mathutils import Vector,Matrix,kdtree
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];OUT=R/'SourceArt/Characters/Kwaku/Authored_v015';assert not OUT.exists();OUT.mkdir(parents=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceArt/Characters/Kwaku/Authored_v011/Kwaku.blend'))
s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');mesh=bpy.data.objects['SK_Kwaku'];rig.animation_data.action=None
def neutral():
 for b in rig.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
 bpy.context.view_layer.update()
neutral();s.frame_set(0)
sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g;g.scene=s;g.parts=[];g.binds={}
# Replace noisy transferred arm weights with authored ring topology and axial blends.
old_mesh=mesh;blink_samples={}
for side in ['L','R']:
 group=old_mesh.vertex_groups['lid_'+side];rows=[(v.co.copy(),old_mesh.data.shape_keys.key_blocks['Blink_'+side].data[v.index].co.copy())for v in old_mesh.data.vertices if any(a.group==group.index and a.weight>.5 for a in v.groups)];kd=kdtree.KDTree(len(rows))
 for i,(p,q)in enumerate(rows):kd.insert(p,i)
 kd.balance();blink_samples[side]=(kd,rows)
bpy.data.objects.remove(old_mesh,do_unlink=True)
skin=bpy.data.materials['Skin']
for side in ['L','R']:
 old=bpy.data.objects['ContinuousArmHand_'+side];bpy.data.objects.remove(old,do_unlink=True)
 upper=rig.data.bones['upperarm_'+side];lower=rig.data.bones['lowerarm_'+side];hand_bone=rig.data.bones['hand_'+side];points=[];radii=[];distances=[];travel=0
 specs=[(upper.head_local,upper.tail_local,12,.047,.033),(lower.head_local,lower.tail_local,12,.033,.023),(hand_bone.head_local,hand_bone.tail_local,7,.023,.031)]
 for segment,(a,b,count,r0,r1)in enumerate(specs):
  for i in range(0 if segment==0 else 1,count+1):
   t=i/count;points.append(a.lerp(b,t));radii.append(r0+(r1-r0)*t);distances.append(travel+(b-a).length*t)
  travel+=(b-a).length
 o=g.tube('ContinuousArmHand_'+side,points,radii,skin,segments=32);groups={name:o.vertex_groups.new(name=name)for name in ['upperarm_'+side,'lowerarm_'+side,'hand_'+side]};j1=upper.length;j2=j1+lower.length
 for ring,d in enumerate(distances):
  t=max(0,min(1,(d-j1+.023)/.046));t=t*t*(3-2*t);h=max(0,min(1,(d-j2+.018)/.036));h=h*h*(3-2*h);row={'upperarm_'+side:(1-t)*(1-h),'lowerarm_'+side:t*(1-h),'hand_'+side:h}
  for n,w in row.items():
   if w>0:groups[n].add(list(range(ring*32,(ring+1)*32)),w,'REPLACE')
  if d>j2:
   centre=points[ring]
   for vertex in o.data.vertices[ring*32:(ring+1)*32]:vertex.co.y=centre.y+(vertex.co.y-centre.y)*.60
 o.parent=rig;o.modifiers.new('Skin','ARMATURE').object=rig
parts=[o for o in s.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in parts:
 c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.hide_set(False);c.hide_render=False;c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='SK_Kwaku';mesh.shape_key_add(name='Basis')
for side in ['L','R']:
 key=mesh.shape_key_add(name='Blink_'+side);group=mesh.vertex_groups['lid_'+side];kd,rows=blink_samples[side]
 for vertex in mesh.data.vertices:
  if any(a.group==group.index and a.weight>.5 for a in vertex.groups):
   co,i,d=kd.find(vertex.co);assert d<1e-6;target=rows[i][1].copy();x=target.x-(-.041 if side=='L'else .041);z=target.z-1.3795;target.y=min(target.y,-.062-.024*math.sqrt(max(.01,1-(x/.025)**2-(z/.018)**2))-.002);key.data[vertex.index].co=target
for o in parts:o.hide_set(True);o.hide_render=True
leather=next(m for m in bpy.data.materials if m.name=='Leather');paper=g.material('LedgerPaper',(.64,.53,.33),rough=.88);brass=g.material('LedgerClasp',(.48,.25,.06),metal=.7,rough=.4)
def box(name,lo,hi,mat):
 verts=[(x,y,z)for x in [lo[0],hi[0]]for y in [lo[1],hi[1]]for z in [lo[2],hi[2]]];faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)];o=g.mesh(name,verts,faces,mat);bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('BoundCoverEdges','BEVEL');mod.width=.0015;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);return o
prop_parts=[box('Ledger_Pages',(-.085,-.008,-.053),(.085,.008,.053),paper),box('Ledger_FrontCover',(-.089,-.012,-.057),(.089,-.008,.057),leather),box('Ledger_BackCover',(-.089,.008,-.057),(.089,.012,.057),leather),box('Ledger_Spine',(-.089,-.012,-.057),(-.084,.012,.057),leather),box('Ledger_Clasp',(.072,-.014,-.012),(.093,.014,.012),brass)]
bpy.ops.object.select_all(action='DESELECT')
for o in prop_parts:o.select_set(True)
bpy.context.view_layer.objects.active=prop_parts[0];bpy.ops.object.join();prop=bpy.context.object;prop.name='Ledger_SeparateProp';prop.location=(0,-.248,1.045);prop.hide_render=True
# Preserve original eleven motion categories; replace only this revision's real InspectLedger keys.
old=bpy.data.actions['InspectLedger'];bpy.data.actions.remove(old);action=bpy.data.actions.new('InspectLedger');action.use_fake_user=True;rig.animation_data.action=action
def key(frame):
 for b in rig.pose.bones:b.keyframe_insert('rotation_euler',frame=frame)
neutral();key(1)
def aim_bone(name,head,tail):
 b=rig.pose.bones[name];d=(tail-head).normalized();z=Vector((0,1,0));x=d.cross(z).normalized();z=x.cross(d).normalized();rotation=Matrix(((x.x,d.x,z.x),(x.y,d.y,z.y),(x.z,d.z,z.z))).to_4x4();rotation.translation=head;b.matrix=rotation;bpy.context.view_layer.update()
def hold():
 for side,sign in [('L',-1),('R',1)]:
  upper=rig.data.bones['upperarm_'+side];lower=rig.data.bones['lowerarm_'+side];S=upper.head_local.copy();T=Vector((sign*.094,-.228,1.087));a=upper.length;b=lower.length;d=(T-S).length;u=(T-S).normalized();along=(a*a-b*b+d*d)/(2*d);height=math.sqrt(max(0,a*a-along*along));pole=Vector((sign,0,-.3));pole=(pole-u*pole.dot(u)).normalized();E=S+along*u+height*pole
  aim_bone('upperarm_'+side,S,E);aim_bone('lowerarm_'+side,E,T);aim_bone('hand_'+side,T,T+Vector((-sign*.015,-.010,-.060)))
  for i in range(5):
   for segment in ['01','02']:rig.pose.bones[f'digit_{side}_{i}_{segment}'].rotation_euler.x=.40 if i==0 else .55
 bpy.context.view_layer.update()
hold();key(14);key(67);neutral();key(82);s.frame_end=82
rig.animation_data.action=action;s.frame_set(35);bpy.context.view_layer.update();prop.hide_render=False
# Prop is separate; its offset is derived from the evaluated right hand at the held pose.
world=prop.matrix_world.copy();hand=rig.pose.bones['hand_R'].matrix.copy();local=hand.inverted()@world;prop.parent=rig;prop.parent_type='BONE';prop.parent_bone='hand_R';prop.matrix_world=world
# Preserve the evaluated source-space matrix explicitly; Blender bone parenting includes tail offset.
prop.matrix_world=world;bpy.context.view_layer.update()
attachment={'bone':'hand_R','armature_space_hand_to_prop':[list(r)for r in local],'source_world_prop':[list(r)for r in world],'source_units':'metres','native_units':'centimetres','source_forward':'-Y','native_forward':'+X'}
# Measure rendered mesh vertices nearest actual solid prop, not requested hand targets.
prop_eval=prop.evaluated_get(bpy.context.evaluated_depsgraph_get());pm=prop_eval.to_mesh();pv=[prop_eval.matrix_world@v.co for v in pm.vertices];pf=[list(p.vertices)for p in pm.polygons];tree=BVHTree.FromPolygons(pv,pf);prop_eval.to_mesh_clear();me=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());ev=me.to_mesh();probes=[]
for side in ['L','R']:
 candidates=[];valid={g.index for g in mesh.vertex_groups if g.name=='hand_'+side or g.name.startswith('digit_'+side+'_')}
 for v in mesh.data.vertices:
  if any(a.group in valid and a.weight>.25 for a in v.groups):
   point=me.matrix_world@ev.vertices[v.index].co;hit=tree.find_nearest(point)
   if hit:candidates.append((hit[3],v.index,list(point),list(hit[0])))
 distance,index,point,hit=min(candidates);probes.append({'side':side,'actual_evaluated_vertex':index,'distance_cm':distance*100,'point':point,'prop_surface':hit})
me.to_mesh_clear();assert all(x['distance_cm']<2 for x in probes),probes
s.camera=bpy.data.objects['beauty'];s.render.filepath=str(OUT/'ledger_interaction.png');bpy.ops.render.render(write_still=True)
prop.parent=None;prop.matrix_world=Matrix.Identity(4);prop.hide_render=False;bpy.ops.object.select_all(action='DESELECT');prop.select_set(True);bpy.ops.export_scene.gltf(filepath=str(OUT/'Ledger.glb'),use_selection=True,export_format='GLB',export_animations=False,export_skins=False)
prop.parent=rig;prop.parent_type='BONE';prop.parent_bone='hand_R';prop.matrix_world=world;prop.hide_render=True
rig.animation_data.action=None;neutral();s.frame_set(0);s.camera=bpy.data.objects['beauty'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kwaku.blend'))
bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(OUT/'Kwaku.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
for file in ['Kwaku.glb','Ledger.glb']:
 p=OUT/file;raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
status={'status':'SOURCE_INTERACTION_AUTHORED_PENDING_NATIVE_CREATIVE_REVIEW','scene_sha256':hashlib.sha256((OUT/'Kwaku.blend').read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256((OUT/'Kwaku.glb').read_bytes()).hexdigest(),'actions':sorted(a.name for a in bpy.data.actions),'attachment':attachment,'held_pose_contact_probes':probes,'creative_approved':False,'limitations':['Nearest surface probes are limited contact evidence, not full finger/palm penetration or natural grasp approval','Thumb rest shape proposed; retained original pivots','Source face and clothing remain WIP; no final likeness claim']};(OUT/'interaction-status.json').write_text(json.dumps(status,indent=2)+'\n');print('LEDGER_SOURCE_CONTACTS',probes)
