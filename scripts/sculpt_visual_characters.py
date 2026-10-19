"""Correct existing saved surfaces; preserve rest rigs and independent acceptance gates."""
import bpy,bmesh,math,json,hashlib,struct,sys
from pathlib import Path
from mathutils import Vector,kdtree
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];key=sys.argv[sys.argv.index('--')+1];previous='Authored_v016'if key=='Kwaku'else'Authored_v005';revision='Authored_v021'if key=='Kwaku'else'Authored_v009';src=R/'SourceArt/Characters'/key/previous/(key+'.blend');out=src.parent.parent/revision;assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');rest=[(b.name,b.parent.name if b.parent else None,[list(r)for r in b.matrix_local])for b in rig.data.bones];old_actions=sorted(a.name for a in bpy.data.actions);rig.animation_data.action=None
for b in rig.pose.bones:
 b.location=(0,0,0);b.scale=(1,1,1)
 if b.rotation_mode=='QUATERNION':b.rotation_quaternion=(1,0,0,0)
 else:b.rotation_euler=(0,0,0)
s.frame_set(0);sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g;g.scene=s;g.parts=[];g.binds={};blink={};changed=[]
def bind(o,bone):
 for v in list(o.vertex_groups):o.vertex_groups.remove(v)
 o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE');o.parent=rig
 for m in list(o.modifiers):o.modifiers.remove(m)
 o.modifiers.new('Skin','ARMATURE').object=rig;return o
def cut(o,predicate):
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.delete(bm,geom=[v for v in bm.verts if predicate(v.co)],context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update()
def centroid(o):return sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
def ellipse_lid(side,centre,radii,skin,face_tree):
 vs=[];faces=[];closed=[];cx,cy,cz=centre;rx,ry,rz=radii
 for k in range(9):
  t=k/8
  for j in range(64):
   a=j*math.tau/64;sin=math.sin(a);x=rx*(1.02+.55*t)*math.cos(a);z=rz*(.70+.60*t)*sin*(.6+.4*abs(sin));inner=cy-ry*math.sqrt(max(.015,1-(x/rx)**2-(z/rz)**2))-.0008;hit=face_tree.ray_cast(Vector((cx+x,-1,cz+z)),Vector((0,1,0)),2);outer=hit[0].y-.00001 if hit[0]else cy+.005;y=inner*(1-t)+outer*t;vs.append((cx+x,y,cz+z));zz=z-(rz*.70*sin*(.6+.4*abs(sin)))*(1-t)**1.15;yy=cy-ry*math.sqrt(max(.015,1-(x/rx)**2-(zz/rz)**2))-.0015;closed.append(Vector((cx+x,y+(yy-y)*(1-t)**1.1,cz+zz)))
 for k in range(8):
  for j in range(64):a=k*64+j;b=k*64+(j+1)%64;faces.append((a,b,b+64,a+64))
 o=bind(g.mesh('OrbitalLid_'+side,vs,faces,skin),'head');o.vertex_groups.new(name='lid_'+side).add(list(range(len(vs))),1,'REPLACE');blink[side]=(o,[p.copy()for p in closed]);return o
if key=='Kwaku':
 old=bpy.data.objects['SK_Kwaku'];bpy.data.objects.remove(old,do_unlink=True);skin=bpy.data.materials['Skin'];parts=[o for o in s.objects if o.type=='MESH'and o.name!='Ledger_SeparateProp']
 for o in parts:o.hide_set(False);o.hide_render=False
 # Remove the obsolete neck skin hidden inside the replacement, not camera-hide the jagged overlap.
 cut(bpy.data.objects['Kwaku_ContinuousSkin'],lambda p:p.z>1.185)
 head=bpy.data.objects['Kwaku_FaceNeck_QuadSurface']
 for v in head.data.vertices:
  x,y,z=v.co;front=max(0,min(1,-y/.065));cheek=math.exp(-((abs(x)-.047)/.022)**2-((z-1.353)/.035)**2)
  v.co.x*=1+.055*math.exp(-((z-1.35)/.05)**2);v.co.y-=front*(.0035*cheek+.003*math.exp(-(x/.022)**2-((z-1.35)/.025)**2));v.co.z+=.003*math.exp(-((z-1.29)/.025)**2)
 head.data.update();tree=BVHTree.FromPolygons([v.co for v in head.data.vertices],[list(p.vertices)for p in head.data.polygons]);cut(head,lambda p:p.y<-.030 and any(((p.x-sign*.039)/.0185)**2+((p.z-1.381)/.0095)**2<1 for sign in [-1,1]))
 # Snap the actual open face boundary to a smooth orbital loop instead of leaving grid-shaped cut edges.
 bm=bmesh.new();bm.from_mesh(head.data)
 for v in bm.verts:
  if not any(e.is_boundary for e in v.link_edges)or v.co.y>-.03:continue
  for sign in [-1,1]:
   x=v.co.x-sign*.039;z=v.co.z-1.381
   if abs(x)<.035 and abs(z)<.025:
    a=math.atan2(z/.0098,x/.0204);xx=.0204*math.cos(a);zz=.0098*math.sin(a)*(.6+.4*abs(math.sin(a)));yy=-.0635-.016*math.sqrt(max(.015,1-(xx/.020)**2-(zz/.014)**2))-.0008;v.co=(sign*.039+xx,yy,1.381+zz);break
 bm.to_mesh(head.data);bm.free()
 for side,sign in [('L',-1),('R',1)]:
  for n in ['OrbicularLid_'+side]:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
  centre=Vector((sign*.039,-.0635,1.381));rx,ry,rz=.020,.016,.014
  for name,radii,offset in [('Eye',(rx,ry,rz),(0,0,0)),('Iris',(.007,.0018,.0075),(0,-.0157,0)),('Pupil',(.0032,.001,.0046),(0,-.0172,0))]:
   o=bpy.data.objects[name+'_'+side];c=centroid(o);bounds=[max(abs(v.co[i]-c[i])for v in o.data.vertices)for i in range(3)]
   for v in o.data.vertices:v.co=centre+Vector(offset)+Vector(tuple((v.co[i]-c[i])*radii[i]/bounds[i]for i in range(3)))
  ellipse_lid(side,centre,(rx,ry,rz),skin,tree)
  o=bpy.data.objects['Brow_'+side]
  for v in o.data.vertices:v.co.x=sign*.039+(v.co.x-sign*.041)*.88;v.co.z-=.002;v.co.y+=.001
  for n in ['VermilionUpper','VermilionLower']:
   # Move lip surface together with underlying mouth region in a later full mouth rig; keep neutral expression here.
   pass
  sleeve=bpy.data.objects['SetInSleeve_'+side];chest=sleeve.vertex_groups.get('chest');upper=sleeve.vertex_groups['upperarm_'+side]
  for v in sleeve.data.vertices:
   oldweight=next((a.weight for a in v.groups if chest and a.group==chest.index),0);t=1-oldweight/.35 if oldweight else 1;t=max(0,min(1,t));new=.12*(1-t)**2
   if chest:chest.add([v.index],new,'REPLACE')
   upper.add([v.index],1-new,'REPLACE')
   if t<.35:v.co.x*=1+.12*(1-t/.35);v.co.y*=1+.10*(1-t/.35)
  # Preserve digit pivots; taper palm/distal digits and flatten the oversized knuckle bulbs.
  for i in range(5):
   o=bpy.data.objects['AnatomicalDigit_'+side+str(i)];c=centroid(o)
   for v in o.data.vertices:
    v.co.y=c.y+(v.co.y-c.y)*.82
    if i==0:v.co.y-=.003;v.co.x-=sign*.002
  arm=bpy.data.objects['ContinuousArmHand_'+side]
  for v in arm.data.vertices:
   if v.co.z<.79:v.co.y=-.023+(v.co.y+.023)*.88
 # Sash gets controlled spine-follow weights, leaving hip motion available and no collision scale change.
 sash=bpy.data.objects['FittedWovenSash'];
 for group in list(sash.vertex_groups):sash.vertex_groups.remove(group)
 groups={n:sash.vertex_groups.get(n)or sash.vertex_groups.new(name=n)for n in ['pelvis','spine_01','chest']}
 for v in sash.data.vertices:
  t=max(0,min(1,(v.co.z-.83)/.32));w={'pelvis':(1-t)**2,'spine_01':2*t*(1-t),'chest':t*t};total=sum(w.values())
  for n,a in w.items():groups[n].add([v.index],a/total,'REPLACE')
 # Source neutral eyelid/eye size is refined; the shape key targets close the actual new globe.
 changed=['Removed duplicate/jagged neck overlap','Reduced eye projection/spacing and rebuilt almond orbital topology','Refined cheek/nose planes and eyebrow placement','Sleeve weight transition and shoulder circumference corrected','Digit thickness/thumb/palm refinements','Sash spine/hip weighting']
else:
 skin=bpy.data.materials['Fur_Gold_Rosettes'];head=bpy.data.objects['Feline_CheeksMuzzle_Continuous']
 for v in head.data.vertices:
  x,y,z=v.co;front=max(0,min(1,(-y-.02)/.09));v.co.x*=.89-.20*math.exp(-((z-1.80)/.045)**2);v.co.y-=front*(.029*math.exp(-(x/.085)**2-((z-1.845)/.037)**2)+.014*math.exp(-(x/.030)**2-((z-1.90)/.06)**2)+.010*math.exp(-((abs(x)-.063)/.028)**2-((z-1.95)/.018)**2));v.co.z+=.008*math.exp(-((z-1.785)/.03)**2)
 # Remove the jagged per-face cream assignment; bake a smooth muzzle mask below.
 for p in head.data.polygons:p.material_index=0
 for side,sign in [('L',-1),('R',1)]:
  for n in ['Ear_'+side,'EarInner_'+side]:
   o=bpy.data.objects[n];c=centroid(o);target=Vector((sign*.113,c.y,1.997))
   for v in o.data.vertices:v.co=target+Vector(((v.co.x-c.x)*.72,(v.co.y-c.y)*.8,(v.co.z-c.z)*.72))
  # True three-dimensional eyes and conforming eyelids replace floating flat discs.
  cx=sign*.063;cz=1.925
  tree=BVHTree.FromPolygons([v.co for v in head.data.vertices],[list(p.vertices)for p in head.data.polygons]);hit=tree.ray_cast(Vector((cx,-1,cz)),Vector((0,1,0)),2);cy=hit[0].y+.010;centre=Vector((cx,cy,cz));rx,ry,rz=.023,.019,.015
  for name,radii,offset in [('Eye',(rx,ry,rz),(0,0,0)),('Iris',(.012,.0018,.011),(0,-.018,0)),('Pupil',(.0027,.001,.010),(0,-.020,0))]:
   o=bpy.data.objects[name+'_'+side];c=centroid(o);bounds=[max(abs(v.co[i]-c[i])for v in o.data.vertices)for i in range(3)]
   for v in o.data.vertices:v.co=centre+Vector(offset)+Vector(tuple((v.co[i]-c[i])*radii[i]/bounds[i]for i in range(3)))
  ellipse_lid(side,centre,(rx,ry,rz),skin,tree)
  # Armhole/shoulder volume is expanded locally, preserving forearm/paw pivots.
  o=bpy.data.objects['ContinuousArmPaw_'+side]
  for v in o.data.vertices:
   if v.co.z>1.43:
    t=max(0,min(1,(v.co.z-1.43)/.15));v.co.x+=sign*.012*t;v.co.y*=1+.12*t
 # Replace nearest-surface transferred arm weights with bounded axial joint blends.
 for side in ['L','R']:
  o=bpy.data.objects['ContinuousArmPaw_'+side];upper=rig.data.bones['upperarm_'+side];lower=rig.data.bones['lowerarm_'+side];hand=rig.data.bones['hand_'+side];segments=[(upper.head_local,upper.tail_local),(lower.head_local,lower.tail_local),(hand.head_local,hand.tail_local)];lengths=[(b-a).length for a,b in segments];j1=lengths[0];j2=j1+lengths[1]
  for group in list(o.vertex_groups):o.vertex_groups.remove(group)
  groups={n:o.vertex_groups.new(name=n)for n in ['upperarm_'+side,'lowerarm_'+side,'hand_'+side]+[f'digit_{side}_{i}_{seg}'for i in range(4)for seg in ['01','02']]}
  for v in o.data.vertices:
   candidates=[];offset=0
   for a,b in segments:
    d=b-a;t=max(0,min(1,(v.co-a).dot(d)/d.length_squared));p=a+d*t;candidates.append(((v.co-p).length,offset+t*d.length));offset+=d.length
   _,distance=min(candidates);t=max(0,min(1,(distance-j1+.035)/.070));t=t*t*(3-2*t);h=max(0,min(1,(distance-j2+.025)/.050));h=h*h*(3-2*h);row={'upperarm_'+side:(1-t)*(1-h),'lowerarm_'+side:t*(1-h),'hand_'+side:h}
   if distance>j2+lengths[2]*.35:
    ds=[]
    for i in range(4):
     for seg in ['01','02']:
      bone=rig.data.bones[f'digit_{side}_{i}_{seg}'];d=bone.tail_local-bone.head_local;q=max(0,min(1,(v.co-bone.head_local).dot(d)/d.length_squared));ds.append(((v.co-bone.head_local-q*d).length,bone.name))
    error,n=min(ds)
    if error<.019:row={n:.85,'hand_'+side:.15}
   total=sum(row.values())
   for n,w in row.items():
    if w>0:groups[n].add([v.index],w/total,'REPLACE')
 if 'Throat_Cream'in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects['Throat_Cream'],do_unlink=True)
 neck=bpy.data.objects['Neck_Fur'];neck.data.materials.clear();neck.data.materials.append(skin)
 for polygon in neck.data.polygons:polygon.material_index=0
 for v in neck.data.vertices:
  t=max(0,min(1,(1.78-v.co.z)/.19));v.co.x*=1+.36*t;v.co.y*=1+.15*t
 nose=bpy.data.objects['Nose_Triangular']
 for v in nose.data.vertices:v.co.x*=.79;v.co.y-=.024;v.co.z+=.002
 jaw=bpy.data.objects['LowerJaw']
 for v in jaw.data.vertices:v.co.x*=.9;v.co.y-=.004
 # Add the missing attachment bridge; not a change to tail collision/root authority.
 root=rig.data.bones['tail_01'].head_local;bridge=g.oval('TailRoot_Transition',root+Vector((-.015,-.02,.02)),(.065,.075,.065),skin,None);bind(bridge,'pelvis')
 for n in ['Cape_TailoredPleats','Cape_WovenHem','Cape_Edge_L','Cape_Edge_R']:
  o=bpy.data.objects[n]
  for v in o.data.vertices:
   back=max(0,min(1,(v.co.y+.02)/.12));v.co.y+=.035*back*max(0,min(1,(1.55-v.co.z)/.4))
 # Bake head vertex tones into a real UV texture so native import sees the same smooth muzzle boundary.
 import numpy as np
 base=bpy.data.images.get('OseboRosetteTile_v003');W=base.size[0];pixels=np.array(base.pixels[:],dtype=np.float32).reshape(W,W,4);old_uv=[tuple(x.uv)for x in head.data.uv_layers.active.data]
 mat=skin.copy();mat.name='FelineFaceSurface';head.data.materials.clear();head.data.materials.append(mat)
 bpy.ops.object.select_all(action='DESELECT');head.select_set(True);bpy.context.view_layer.objects.active=head;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.012);bpy.ops.object.mode_set(mode='OBJECT');head.data.calc_loop_triangles();N=1024;paint=np.zeros((N,N,4),dtype=np.float32);paint[:]=(.30,.13,.025,1)
 for tri in head.data.loop_triangles:
  uv=np.array([head.data.uv_layers.active.data[i].uv[:]for i in tri.loops])*(N-1);lo=np.maximum(0,np.floor(uv.min(axis=0)).astype(int));hi=np.minimum(N-1,np.ceil(uv.max(axis=0)).astype(int));yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];den=(uv[1,1]-uv[2,1])*(uv[0,0]-uv[2,0])+(uv[2,0]-uv[1,0])*(uv[0,1]-uv[2,1])
  if abs(den)<1e-9:continue
  a=((uv[1,1]-uv[2,1])*(xx-uv[2,0])+(uv[2,0]-uv[1,0])*(yy-uv[2,1]))/den;b=((uv[2,1]-uv[0,1])*(xx-uv[2,0])+(uv[0,0]-uv[2,0])*(yy-uv[2,1]))/den;c=1-a-b;inside=(a>=-.03)&(b>=-.03)&(c>=-.03);pos=np.array([head.data.vertices[i].co[:]for i in tri.vertices]);xyz=a[...,None]*pos[0]+b[...,None]*pos[1]+c[...,None]*pos[2];prior=np.array([old_uv[i]for i in tri.loops]);tex=a[...,None]*prior[0]+b[...,None]*prior[1]+c[...,None]*prior[2];tx=(np.mod(tex[...,0],1)*W).astype(int)%W;ty=(np.mod(tex[...,1],1)*W).astype(int)%W;rgb=pixels[ty,tx,:3];mask=np.exp(-(xyz[...,0]/.094)**4-((xyz[...,2]-1.834)/.039)**4)*np.clip((-xyz[...,1]-.14)/.04,0,1);rgb=rgb*(1-mask[...,None])+np.array([.72,.61,.43])*mask[...,None];region=paint[lo[1]:hi[1]+1,lo[0]:hi[0]+1];region[inside,:3]=rgb[inside]
 # Small island padding avoids dark seams without changing original reference pixels.
 for _ in range(3):
  blank=(paint[...,0]==.30)&(paint[...,1]==.13)
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
   neighbor=np.roll(paint,(dy,dx),(0,1));valid=blank&((neighbor[...,0]!=.30)|(neighbor[...,1]!=.13));paint[valid]=neighbor[valid]
 image=bpy.data.images.new('FelineFaceSurface',width=N,height=N,alpha=True);image.colorspace_settings.name=base.colorspace_settings.name;image.pixels.foreach_set(paint.ravel());image.filepath_raw=str(out/'FelineFaceSurface.png');image.file_format='PNG';image.save();image.pack();nodes=mat.node_tree.nodes;nodes.clear();output=nodes.new('ShaderNodeOutputMaterial');p=nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Roughness'].default_value=.78;tex=nodes.new('ShaderNodeTexImage');tex.image=image;mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);mat.node_tree.links.new(p.outputs[0],output.inputs['Surface'])
 changed=['Feline skull/muzzle and smaller ears','True eyeball volume and conforming almond lids','Smooth UV-baked muzzle surface instead of jagged polygon mask','Neck flare/shoulder volume','Tail-root bridge','Cape back clearance']
# Re-author the defective interaction only, on existing bone lengths and pivots.
from mathutils import Matrix
clip_name='InspectLedger'if key=='Kwaku'else'CaptureReach';bpy.data.actions.remove(bpy.data.actions[clip_name]);action=bpy.data.actions.new(clip_name);action.use_fake_user=True;rig.animation_data.action=action
for b in rig.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
def key_pose(frame):
 for b in rig.pose.bones:b.keyframe_insert('rotation_euler',frame=frame)
def aim(name,a,b):
 d=(b-a).normalized();up=Vector((0,1,0));x=d.cross(up).normalized();z=x.cross(d).normalized();m=Matrix(((x.x,d.x,z.x),(x.y,d.y,z.y),(x.z,d.z,z.z))).to_4x4();m.translation=a;rig.pose.bones[name].matrix=m;bpy.context.view_layer.update()
key_pose(1 if key=='Kwaku'else 0)
for side,sign in [('L',-1),('R',1)]:
 upper=rig.data.bones['upperarm_'+side];lower=rig.data.bones['lowerarm_'+side];S=upper.head_local.copy();T=Vector((sign*.097,-.235,1.107))if key=='Kwaku'else Vector((sign*.225,-.385,1.39));a=upper.length;b=lower.length;d=(T-S).length;u=(T-S).normalized();along=(a*a-b*b+d*d)/(2*d);height=math.sqrt(max(0,a*a-along*along));pole=Vector((sign,0,-.35));pole=(pole-u*pole.dot(u)).normalized();E=S+along*u+height*pole;aim('upperarm_'+side,S,E);aim('lowerarm_'+side,E,T);aim('hand_'+side,T,T+Vector((-sign*.004,.003,-.060))if key=='Kwaku'else T+Vector((0,-.085,-.025)))
 for i in range(5 if key=='Kwaku'else 4):
  for seg in ['01','02']:rig.pose.bones[f'digit_{side}_{i}_{seg}'].rotation_euler.x=(-.35 if i==0 else .78)if key=='Kwaku'else .28
key_pose(14);key_pose(67 if key=='Kwaku'else 45)
for b in rig.pose.bones:b.rotation_euler=(0,0,0)
key_pose(82 if key=='Kwaku'else 60);s.frame_set(35);bpy.context.view_layer.update()
if key=='Kwaku':
 prop=bpy.data.objects['Ledger_SeparateProp'];world=Matrix.Identity(4);world.translation=Vector((0,-.248,1.045));prop.matrix_world=world;bpy.context.view_layer.update()
rig.animation_data.action=None;s.frame_set(0)

# Rebuild export mesh from actual editable parts. Preserve old rest skeleton/actions.
parts=[o for o in s.objects if o.type=='MESH'and o.name!='Ledger_SeparateProp'];copies=[];blink_targets={}
for o in parts:
 if o.data.uv_layers:
  chosen=o.data.uv_layers.active;coords=[tuple(x.uv)for x in chosen.data]
  for layer in list(o.data.uv_layers):o.data.uv_layers.remove(layer)
  layer=o.data.uv_layers.new(name='UVMap')
  for a,uv in zip(layer.data,coords):a.uv=uv
  layer.active_render=True

for side,(o,closed)in blink.items():
 kd=kdtree.KDTree(len(o.data.vertices))
 for i,v in enumerate(o.data.vertices):kd.insert(v.co,i)
 kd.balance();blink_targets[side]=(kd,closed)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:
 o.hide_set(False);o.hide_render=False;c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='SK_'+key;mesh.shape_key_add(name='Basis')
for side,(kd,closed)in blink_targets.items():
 keyblock=mesh.shape_key_add(name='Blink_'+side);group=mesh.vertex_groups['lid_'+side]
 for v in mesh.data.vertices:
  if any(a.group==group.index and a.weight>.5 for a in v.groups):co,i,d=kd.find(v.co);assert d<1e-5;keyblock.data[v.index].co=closed[i]
# Honest partial facial controls: brow and concern/suspicion/determination exist; speech remains an open gate.
for label in ['BrowUp','BrowDown','Concern','Suspicion','Determination']:
 shape=mesh.shape_key_add(name=label);faceZ=1.405 if key=='Kwaku'else 1.95
 for v in mesh.data.vertices:
  x,y,z=v.co;front=max(0,min(1,-y/.06));region=math.exp(-((z-faceZ)/.018)**2)*math.exp(-((abs(x)-(.036 if key=='Kwaku'else .063))/.032)**2)*front
  if label=='BrowUp':delta=.006*region
  elif label=='BrowDown':delta=-.004*region
  elif label=='Concern':delta=.005*region*max(0,1-abs(x)/.08)
  elif label=='Suspicion':delta=.006*region*(1 if x<0 else -.5)
  else:delta=-.004*region*max(0,1-abs(x)/.12)
  shape.data[v.index].co.z+=delta
for o in parts:o.hide_set(True);o.hide_render=True
mesh.hide_render=False;mesh.hide_set(False);rig.animation_data.action=None;s.frame_set(0)
assert rest==[(b.name,b.parent.name if b.parent else None,[list(r)for r in b.matrix_local])for b in rig.data.bones];assert old_actions==sorted(a.name for a in bpy.data.actions)
bpy.ops.wm.save_as_mainfile(filepath=str(out/(key+'.blend')));bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(out/(key+'.glb')),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
p=out/(key+'.glb');raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
if key=='Kwaku':
 import shutil;shutil.copyfile(src.parent/'Ledger.glb',out/'Ledger.glb')
(out/'visual-corrections.json').write_text(json.dumps({'source_previous_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'scene_sha256':hashlib.sha256((out/(key+'.blend')).read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rest_bones_unchanged':True,'actions_retained':old_actions,'changes':changed,'facial_shapes':[k.name for k in mesh.data.shape_keys.key_blocks],'speech_animation_complete':False,'creative_approved':False,'acceptance':'REVIEW_REQUIRED'},indent=2)+'\n');print('CORRECTED_SOURCE_SAVED',key,revision)
