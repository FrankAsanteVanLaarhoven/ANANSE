"""Editable Kwaku surface/interaction revision, retaining the qualified rest rig."""
import bpy,bmesh,math,json,hashlib,struct,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];OUT=R/'SourceArt/Characters/Kwaku/Authored_v011'
assert not OUT.exists();OUT.mkdir(parents=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceArt/Characters/Kwaku/Authored_v008/Kwaku.blend'))
s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE')
def rest():return [(b.name,b.parent.name if b.parent else None,list(v for row in b.matrix_local for v in row))for b in rig.data.bones]
original=rest();actions=sorted(a.name for a in bpy.data.actions);rig.animation_data.action=None;s.frame_set(0)
for b in rig.pose.bones:b.rotation_mode='QUATERNION';b.rotation_quaternion=(1,0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
bpy.data.objects.remove(bpy.data.objects['SK_Kwaku'],do_unlink=True)
for o in s.objects:
 if o.type=='MESH':o.hide_set(False);o.hide_render=False
sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g
g.scene=s;g.parts=[];g.binds={};mats={m.name:m for m in bpy.data.materials};skin=mats['Skin']
def bind(o,bone):
 for v in list(o.vertex_groups):o.vertex_groups.remove(v)
 o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE');o.parent=rig
 for m in list(o.modifiers):o.modifiers.remove(m)
 o.modifiers.new('Skin','ARMATURE').object=rig
 return o
def weights(o,rows):
 for v in list(o.vertex_groups):o.vertex_groups.remove(v)
 groups={}
 for i,row in enumerate(rows):
  total=sum(row.values());assert total>0
  for n,w in row.items():
   if w>0:
    if n not in groups:groups[n]=o.vertex_groups.new(name=n)
    groups[n].add([i],w/total,'REPLACE')
 o.parent=rig;o.modifiers.new('Skin','ARMATURE').object=rig;return o
def remove_prefix(prefixes):
 for o in list(s.objects):
  if o.type=='MESH'and o.name.startswith(tuple(prefixes)):bpy.data.objects.remove(o,do_unlink=True)
# Retain the original torso below the new sewn neck; replace the old fused bulb face.
body=bpy.data.objects['Kwaku_ContinuousSkin'];bm=bmesh.new();bm.from_mesh(body.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z>1.236],context='VERTS');bm.to_mesh(body.data);bm.free()
remove_prefix(['Eye_','Iris_','Pupil_','Brow_','UpperLid_','LowerLid_','UpperLip','LowerLip','HairCurl','SewnNeckOpening'])
profiles=[(1.200,.050,.048,.006),(1.249,.045,.043,.006),(1.265,.038,.044,-.005),(1.282,.052,.055,-.002),(1.305,.067,.062,.002),(1.335,.080,.071,.003),(1.365,.084,.074,.003),(1.390,.083,.075,.003),(1.420,.082,.077,.006),(1.447,.076,.072,.008),(1.465,.060,.058,.009),(1.477,.027,.029,.009),(1.480,.001,.001,.009)]
def profile(z):
 for a,b in zip(profiles,profiles[1:]):
  if a[0]<=z<=b[0]:
   t=(z-a[0])/(b[0]-a[0]);index=profiles.index(a);prev=profiles[max(0,index-1)];nxt=profiles[min(len(profiles)-1,index+2)];h=b[0]-a[0];return tuple((2*t**3-3*t*t+1)*a[i]+(t**3-2*t*t+t)*h*(b[i]-prev[i])/(b[0]-prev[0])+(-2*t**3+3*t*t)*b[i]+(t**3-t*t)*h*(nxt[i]-a[i])/(nxt[0]-a[0])for i in range(1,4))
 return profiles[0][1:]if z<profiles[0][0]else profiles[-1][1:]
def face_y(x,z):
 rx,ry,cy=profile(z);front=math.sqrt(max(0,1-(x/rx)**2));y=cy-ry*front
 # Continuous bridge, alae, cheek plane and mouth/chin plane, not separate nose balls.
 y-=.013*math.exp(-(x/.015)**2-((z-1.359)/.030)**2)
 y-=.019*math.exp(-(x/.019)**2-((z-1.345)/.010)**2)
 y-=.009*math.exp(-((abs(x)-.019)/.010)**2-((z-1.341)/.008)**2)
 y-=.010*math.exp(-((abs(x)-.044)/.023)**2-((z-1.354)/.020)**2)
 y-=.016*math.exp(-(x/.037)**2-((z-1.312)/.020)**2)
 y-=.011*math.exp(-((abs(x)-.041)/.027)**2-((z-1.381)/.026)**2)
 return y
verts=[];uv=[];faces=[];rows=[];N=96;M=88
for i in range(M):
 z=profiles[0][0]+(profiles[-1][0]-profiles[0][0])*i/(M-1);rx,ry,cy=profile(z)
 for j in range(N):
  a=j*math.tau/N;x=rx*math.sin(a);y=cy-ry*math.cos(a)
  if math.cos(a)>0:y+=(face_y(x,z)-(cy-ry*abs(math.cos(a))))*max(0,math.cos(a))**.35
  verts.append((x,y,z));uv.append((j/N,i/(M-1)));jaw=max(0,min(.55,(1.320-z)/.055))if z>1.26 else 0;neck=max(0,min(1,(1.268-z)/.028));rows.append({'head':(1-neck)*(1-jaw),'jaw':(1-neck)*jaw,'neck':neck})
for i in range(M-1):
 for j in range(N):a=i*N+j;b=i*N+(j+1)%N;faces.append((a,b,b+N,a+N))
faces.append(tuple(range((M-1)*N,M*N)));head=weights(g.mesh('Kwaku_FaceNeck_QuadSurface',verts,faces,skin,uv=uv),rows)
for side,sign in [('L',-1),('R',1)]:
 # Ear rim and recessed concha are actual editable curved surfaces.
 vs=[];fs=[]
 for k in range(6):
  t=k/5;rx=.011*(1-.72*t);rz=.024*(1-.72*t)
  for j in range(32):
   a=j*math.tau/32;vs.append((sign*(.081+rx*math.cos(a)),.001-.009*math.sin(math.pi*t),1.365+rz*math.sin(a)))
 for k in range(5):
  for j in range(32):a=k*32+j;b=k*32+(j+1)%32;fs.append((a,b,b+32,a+32))
 bind(g.mesh('EarConcha_'+side,vs,fs,skin),'head')
eye_centres={};lid_close={}
for side,sign in [('L',-1),('R',1)]:
 centre=Vector((sign*.041,-.062,1.3795));eye_centres[side]=centre
 for name,offset,scale,mat in [('Eye',(0,0,0),(.023,.020,.015),mats['Eyes']),('Iris',(0,-.0192,0),(.009,.002,.010),mats['Amber']),('Pupil',(0,-.021,0),(.004,.0011,.006),mats['Hair_Pupil'])]:bind(g.oval(name+'_'+side,centre+Vector(offset),scale,mat,None),'eye_'+side)
 vs=[];fs=[];closed=[]
 for k in range(9):
  t=k/8
  for j in range(64):
   a=j*math.tau/64;x=(.021*(1-t)+.032*t)*math.cos(a);z=(.0075*(1-t)+.022*t)*math.sin(a)
   inner_y=-.062-.020*math.sqrt(max(.02,1-(.021*math.cos(a)/.023)**2-(.0075*math.sin(a)/.015)**2))-.0007
   y=inner_y*(1-t)+(face_y(centre.x+x,centre.z+z)-.0005)*t;vs.append((centre.x+x,y,centre.z+z))
   cz=z-(.0075*math.sin(a))*(1-t)**1.25;cy=-.062-.020*math.sqrt(max(.02,1-(x/.023)**2-(cz/.015)**2))-.0012
   closed.append(Vector((centre.x+x,y+(cy-y)*(1-t)**1.1,centre.z+cz)))
 for k in range(8):
  for j in range(64):a=k*64+j;b=k*64+(j+1)%64;fs.append((a,b,b+64,a+64))
 o=bind(g.mesh('OrbicularLid_'+side,vs,fs,skin),'head');marker=o.vertex_groups.new(name='lid_'+side);marker.add(list(range(len(vs))),1,'REPLACE');lid_close[o.name]=closed
 points=[]
 for i in range(17):
  x=sign*.041+(i/16-.5)*.052;z=1.406+.004*math.sin(math.pi*i/16);points.append((x,face_y(x,z)-.0015,z))
 bind(g.tube('Brow_'+side,points,[.0015+.0015*math.sin(math.pi*i/16)for i in range(17)],mats['Hair_Pupil'],segments=8),'head')
lip=skin.copy();lip.name='Kwaku_LipSurface_v009';lip.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.105,.033,.025,1)
for upper in [True,False]:
 vs=[];fs=[]
 for k in range(5):
  t=k/4
  for j in range(33):
   x=(j/32-.5)*.048;shape=math.sin(math.pi*j/32);z=1.313+shape*((.0035+.0015*math.cos(x*160))if upper else-.005)*(1-t);y=face_y(x,z)-.001-.0025*shape*math.sin(math.pi*t);vs.append((x,y,z))
 for k in range(4):
  for j in range(32):a=k*33+j;fs.append((a,a+1,a+34,a+33))
 bind(g.mesh('VermilionUpper'if upper else'VermilionLower',vs,fs,lip),'jaw')
# Low-contrast nostril recesses follow the alar surface, without detached black beads.
for side,sign in [('L',-1),('R',1)]:bind(g.oval('Nostril_'+side,(sign*.014,face_y(sign*.014,1.339)-.0007,1.339),(.004,.0007,.0018),lip,None),'head')
# Short coiled crop: compact cap + small coiled clumps, not one broad button row.
bind(g.oval('HairCap',(0,.009,1.447),(.083,.073,.039),mats['Hair_Pupil'],None),'head')
for i in range(175):
 a=i*2.39996323;r=math.sqrt((i+.5)/175);x=.082*r*math.cos(a);y=.009+.071*r*math.sin(a);z=1.448+.038*math.sqrt(max(0,1-r*r))
 bind(g.oval('HairCoil_%03d'%i,(x,y,z),(.006,.006,.0065),mats['Hair_Pupil'],None),'head')
# Replace the collapsed/boxy shirt with an editable quad garment and sewn cuffs.
old=bpy.data.objects['Kwaku_TailoredShortSleeveShirt'];bpy.data.objects.remove(old,do_unlink=True);cream=mats['Cream_Linen']
shirt=g.loft('Kwaku_TailoredShortSleeveShirt',[(0,0,.805,.158,.100),(0,0,.85,.164,.102),(0,0,.94,.161,.102),(0,0,1.04,.165,.102),(0,0,1.12,.180,.100),(0,0,1.16,.183,.096),(0,0,1.185,.180,.094),(0,0,1.205,.115,.070),(0,0,1.225,.054,.049)],cream,segments=64)
bm=bmesh.new();bm.from_mesh(shirt.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if len(f.verts)>4],context='FACES');bm.to_mesh(shirt.data);bm.free()
bpy.context.view_layer.objects.active=shirt;modifier=shirt.modifiers.new('TailoringCurvature','SUBSURF');modifier.levels=2;bpy.ops.object.modifier_apply(modifier=modifier.name)
weights(shirt,[{'pelvis':max(0,1-(v.co.z-.81)/.18),'chest':min(1,max(0,(v.co.z-.81)/.18))}for v in shirt.data.vertices])
for side,sign in [('L',-1),('R',1)]:
 a=rig.data.bones['upperarm_'+side].head_local;b=rig.data.bones['upperarm_'+side].tail_local;direction=(b-a).normalized();u=Vector((0,1,0));v=direction.cross(u).normalized();vs=[];fs=[];rows=[]
 for k in range(9):
  t=k/8;c=a.lerp(b,-.18+t*.76);radius=.061*(1-t)+.051*t
  for j in range(40):
   angle=j*math.tau/40;vs.append(tuple(c+radius*(math.cos(angle)*u+math.sin(angle)*v)));rows.append({'upperarm_'+side:.65+.35*t,'chest':.35*(1-t)})
 for k in range(8):
  for j in range(40):a1=k*40+j;b1=k*40+(j+1)%40;fs.append((a1,b1,b1+40,a1+40))
 weights(g.mesh('SetInSleeve_'+side,vs,fs,cream),rows)
 # Refine existing digits around the exact original pivots; thumb splay is provisional.
 for i in range(5):
  old=bpy.data.objects['Finger_'+side+str(i)];bpy.data.objects.remove(old,do_unlink=True);b1=rig.data.bones[f'digit_{side}_{i}_01'];b2=rig.data.bones[f'digit_{side}_{i}_02'];p0=b1.head_local.copy();p1=b1.tail_local.copy();p2=b2.tail_local.copy()
  if i==0:p0.z+=.010;p1.x-=sign*.011;p1.z+=.012;p2.x-=sign*.019;p2.z+=.015
  points=[p0.lerp(p1,t/4)for t in range(5)]+[p1.lerp(p2,t/4)for t in range(1,5)];radii=[.0075,.0074,.007,.0072,.0071,.0064,.006,.0055,.0038]
  o=g.tube('AnatomicalDigit_'+side+str(i),points,radii,skin,segments=16);rows=[]
  for k in range(9):
   t=max(0,min(1,(k-2)/4));rows.extend([{b1.name:1-t,b2.name:t}]*16)
  weights(o,rows)
# Surface response avoids the previous plastic highlights; texture provenance unchanged.
p=skin.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.62;p.inputs['Specular IOR Level'].default_value=.25;p.inputs['Subsurface Weight'].default_value=.055
p=mats['Eyes'].node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.69,.61,.48,1);p.inputs['Roughness'].default_value=.24
# Export copy and eyelid morphs are derived from the editable surfaces above.
parts=[o for o in s.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT');copies=[];close_by_vertex={};offset=0
for o in parts:
 c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();export=bpy.context.object;export.name='SK_Kwaku';export.shape_key_add(name='Basis')
for side in ['L','R']:
 key=export.shape_key_add(name='Blink_'+side);group=export.vertex_groups['lid_'+side];ids=[v.index for v in export.data.vertices if any(a.group==group.index and a.weight>.5 for a in v.groups)];closed=lid_close['OrbicularLid_'+side];assert len(ids)==len(closed)
 for i,p in zip(ids,closed):key.data[i].co=p
for o in parts:o.hide_render=True;o.hide_set(True)
assert rest()==original and sorted(a.name for a in bpy.data.actions)==actions
s.render.resolution_x=900;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.eevee.taa_render_samples=48
for name in ['front','left','right','back','beauty']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(OUT/(name+'_solid.png'));bpy.ops.render.render(write_still=True)
for side in ['L','R']:export.data.shape_keys.key_blocks['Blink_'+side].value=1
s.camera=bpy.data.objects['front'];s.render.filepath=str(OUT/'blink_closed.png');bpy.ops.render.render(write_still=True)
for key in export.data.shape_keys.key_blocks:key.value=0
s.camera=bpy.data.objects['beauty'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kwaku.blend'))
bpy.ops.object.select_all(action='DESELECT');export.select_set(True);rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(OUT/'Kwaku.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
p=OUT/'Kwaku.glb';raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
(OUT/'refinement-status.json').write_text(json.dumps({'status':'WIP_SOURCE_PENDING_DEFORMATION_NATIVE_AND_CREATIVE_REVIEW','source_scene_sha256':hashlib.sha256((OUT/'Kwaku.blend').read_bytes()).hexdigest(),'source_glb_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bone_rest_unchanged':rest()==original,'bone_count':len(original),'actions':actions,'vertices':len(export.data.vertices),'creative_approved':False,'proposals':['Thumb surface splay uses retained pivots; reviewed grasp/retarget mapping still required','Hidden facial/garment construction authored proposal']},indent=2)+'\n')
