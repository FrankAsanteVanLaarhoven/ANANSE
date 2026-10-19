"""Aso Yaa's versioned editable clothing, face and negotiation performance source."""
import bpy, math, json, hashlib, struct, sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
OUT=R/'SourceArt/Characters/AsoYaa/Authored_v004'
assert not OUT.exists(), 'Preserve prior revisions'
OUT.mkdir(parents=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceArt/Characters/AsoYaa/Authored_v001/AsoYaa.blend'))
s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE')
rest=[(b.name,b.parent.name if b.parent else None,tuple(v for row in b.matrix_local for v in row)) for b in rig.data.bones]
rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0);b.location=(0,0,0)
s.frame_set(0)
sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g
g.scene=s;g.parts=[];g.binds={};m={x.name:x for x in bpy.data.materials};skin=m['Skin'];indigo=m['Indigo_Woven'];cream=m.get('Cream_Linen') or g.material('Cream_Linen',(.65,.52,.32),rough=.9);gold=m['Woven_Gold']
def bind(o,rows):
 for mod in list(o.modifiers):o.modifiers.remove(mod)
 for group in list(o.vertex_groups):o.vertex_groups.remove(group)
 groups={}
 if isinstance(rows,str):rows=[{rows:1}for _ in o.data.vertices]
 for i,row in enumerate(rows):
  row={n:w for n,w in row.items()if w>0};total=sum(row.values());assert total>0
  for n,w in row.items():
   assert n in rig.data.bones,n
   if n not in groups:groups[n]=o.vertex_groups.new(name=n)
   groups[n].add([i],w/total,'REPLACE')
 o.parent=rig;o.modifiers.new('Deform','ARMATURE').object=rig
 return o
for o in list(s.objects):
 if o.type=='MESH' and o.name.startswith(('Head_Facial','Jaw','Nose','Mouth','Lid_','Eye_','Iris_','Pupil_','Brow_','Ear_','Bodice','Dress','RobeSleeve','Bracelet','WovenChevron','HeadwrapFold','Finger_','Hand_')):bpy.data.objects.remove(o,do_unlink=True)
# Continuous neck-to-head surface with cheek, muzzle, nose and brow planes.
f=1.68/1.70
rings=[(1.40,.061,.055),(1.46,.055,.054),(1.48,.048,.055),(1.50,.064,.065),(1.53,.080,.073),(1.57,.094,.079),(1.61,.098,.080),(1.65,.093,.079),(1.68,.075,.067),(1.71,.023,.024)]
def profile(z):
 for a,b in zip(rings,rings[1:]):
  if a[0]<=z<=b[0]:
   t=(z-a[0])/(b[0]-a[0]);return a[1]*(1-t)+b[1]*t,a[2]*(1-t)+b[2]*t
 return rings[0][1:]if z<rings[0][0]else rings[-1][1:]
def face(x,z):
 rx,ry=profile(z);y=-ry*math.sqrt(max(0,1-(x/rx)**2))
 y-=.014*math.exp(-(x/.014)**2-((z-1.585)/.035)**2)
 y-=.024*math.exp(-(x/.021)**2-((z-1.566)/.012)**2)
 y-=.009*math.exp(-((abs(x)-.021)/.012)**2-((z-1.559)/.010)**2)
 y-=.011*math.exp(-((abs(x)-.049)/.025)**2-((z-1.576)/.024)**2)
 y-=.012*math.exp(-(x/.036)**2-((z-1.526)/.018)**2)
 return y
vs=[];fs=[];uv=[];rows=[];N=80;M=90
for k in range(M):
 z=1.40+.31*k/(M-1);rx,ry=profile(z)
 for j in range(N):
  a=math.tau*j/N;x=rx*math.sin(a);y=-ry*math.cos(a)
  if math.cos(a)>0:y+=(face(x,z)+ry*abs(math.cos(a)))*math.cos(a)**.4
  vs.append((x*f,y*f,z*f));uv.append((j/N,k/(M-1)));neck=max(0,min(1,(1.49-z)/.06));jaw=max(0,min(.45,(1.546-z)/.04))if z>1.48 else 0;rows.append({'neck':neck,'head':(1-neck)*(1-jaw),'jaw':(1-neck)*jaw})
for k in range(M-1):
 for j in range(N):a=k*N+j;b=k*N+(j+1)%N;fs.append((a,b,b+N,a+N))
head=bind(g.mesh('AsoYaa_ContinuousFace',vs,fs,skin,uv=uv),rows)
head.shape_key_add(name='Basis')
# Localised face correctives; every target is actual editable geometry.
expressions={'Concern':(.004,-.002),'Suspicion':(-.003,.003),'Disapproval':(-.004,-.003),'Consideration':(.001,-.001),'Resolve':(-.002,.001),'Agreement':(.002,.004),'Refusal':(-.002,-.002),'QuietWarning':(-.003,0),'ControlledAnger':(-.005,-.003)}
for name,(brow,mouth)in expressions.items():
 key=head.shape_key_add(name=name)
 for v in key.data:
  x,y,z=v.co/f
  if y<-.025:
   v.co.z+=f*(brow*math.exp(-((abs(x)-.043)/.030)**2-((z-1.629)/.018)**2)+mouth*math.exp(-((abs(x)-.028)/.016)**2-((z-1.531)/.012)**2))
for side,sign in [('L',-1),('R',1)]:
 c=Vector((sign*.042,-.072,1.609))*f
 for name,off,scale,mat in [('Eye',(0,0,0),(.023,.018,.014),m['Eyes']),('Iris',(0,-.0175,0),(.009,.0016,.009),m['Amber']),('Pupil',(0,-.019,0),(.004,.0009,.005),m['Hair_Pupil'])]:bind(g.oval(name+'_'+side,c+Vector(off)*f,tuple(v*f for v in scale),mat,None),'eye_'+side)
 vs=[];fs=[];closed=[]
 for k in range(8):
  t=k/7
  for j in range(64):
   a=math.tau*j/64;x=(.021+.012*t)*math.cos(a);z=(.007+.017*t)*math.sin(a)
   inner=-.072-.018*math.sqrt(max(.02,1-(.021*math.cos(a)/.023)**2-(.007*math.sin(a)/.014)**2))-.0006
   y=inner*(1-t)+(face(sign*.042+x,1.609+z)-.0005)*t;vs.append(tuple(c+Vector((x,y+.072,z))*f))
   cz=z-.007*math.sin(a)*(1-t)**1.3;cy=-.072-.018*math.sqrt(max(.02,1-(x/.023)**2-(cz/.014)**2))-.001;closed.append(c+Vector((x,(y+(cy-y)*(1-t)**1.1)+.072,cz))*f)
 for k in range(7):
  for j in range(64):a=k*64+j;b=k*64+(j+1)%64;fs.append((a,b,b+64,a+64))
 lid=bind(g.mesh('AsoYaa_OrbicularLid_'+side,vs,fs,skin),'head');lid.shape_key_add(name='Basis');key=lid.shape_key_add(name='Blink_'+side)
 for v,p in zip(key.data,closed):v.co=p
 points=[(sign*.042+(i/16-.5)*.051,0,1.634+.003*math.sin(math.pi*i/16))for i in range(17)]
 points=[(x*f,(face(x,z)-.002)*f,z*f)for x,y,z in points];bind(g.tube('Brow_'+side,points,[.002*f]*17,m['Hair_Pupil'],segments=8),'head')
 bind(g.oval('Ear_'+side,(sign*.099*f,0,1.592*f),(.016*f,.014*f,.028*f),skin,None),'head')
# Layered cream underdress and indigo open overrobe, joined shoulders and real cuff seams.
def garment(name,rings,mat,open_front=False):
 vs=[];fs=[];uv=[];rows=[];count=64
 for k,(z,rx,ry)in enumerate(rings):
  for j in range(count+1):
   a=(.30+(math.tau-.60)*j/count)if open_front else math.tau*j/count
   x=rx*math.sin(a);y=-ry*math.cos(a);vs.append((x*f,y*f,z*f));uv.append((j/count,k/(len(rings)-1)))
   lower=max(0,min(1,(.98-z)/.38));chest=max(0,min(1,(z-1.04)/.27));side='L'if x<0 else'R';rows.append({'pelvis':(1-lower)*(1-chest),'chest':chest,'Dress_'+side:lower})
 for k in range(len(rings)-1):
  for j in range(count):a=k*(count+1)+j;fs.append((a,a+1,a+count+2,a+count+1))
 return bind(g.mesh(name,vs,fs,mat,uv=uv),rows)
garment('CreamUnderlayers',[(.09,.25,.14),(.25,.24,.14),(.50,.22,.13),(.80,.18,.12),(1.02,.163,.116),(1.20,.18,.12),(1.31,.202,.125),(1.37,.17,.095),(1.40,.065,.058)],cream)
robe=garment('IndigoOpenRobe',[(.17,.285,.16),(.30,.275,.155),(.55,.245,.15),(.80,.205,.137),(1.02,.175,.13),(1.20,.19,.133),(1.32,.212,.14),(1.37,.18,.105),(1.40,.070,.065)],indigo,True)
for side,sign in [('L',-1),('R',1)]:
 upper=rig.data.bones['upperarm_'+side];lower=rig.data.bones['lowerarm_'+side];points=[upper.head_local.lerp(upper.tail_local,i/6)for i in range(7)]+[lower.head_local.lerp(lower.tail_local,i/7)for i in range(1,8)]
 o=g.tube('TailoredSleeve_'+side,points,[.076*(1-i/13)+.048*i/13 for i in range(14)],indigo,segments=32);rows=[]
 for i in range(14):
  t=max(0,min(1,(i-4)/4));rows.extend([{'upperarm_'+side:1-t,'lowerarm_'+side:t}]*32)
 bind(o,rows)
 bind(g.oval('Cuff_'+side,lower.tail_local,(.037,.03,.012),cream,None),'lowerarm_'+side)
 # Digit surfaces follow retained pivots; thumb splay is proposed, explicitly not anatomy approval.
 for d in range(5):
  b1=rig.data.bones[f'digit_{side}_{d}_01'];b2=rig.data.bones[f'digit_{side}_{d}_02'];p0=b1.head_local.copy();p1=b1.tail_local.copy();p2=b2.tail_local.copy()
  if d==0:p0.z+=.008;p1.x-=sign*.01;p2.x-=sign*.018;p2.z+=.014
  points=[p0.lerp(p1,i/4)for i in range(5)]+[p1.lerp(p2,i/4)for i in range(1,5)];o=g.tube('ArticulatedDigit_'+side+str(d),points,[.0075,.0073,.007,.0072,.0068,.0063,.0059,.0051,.0035],skin,segments=12);rows=[]
  for i in range(9):t=max(0,min(1,(i-2)/4));rows.extend([{b1.name:1-t,b2.name:t}]*12)
  bind(o,rows)
 hand=rig.data.bones['hand_'+side];bind(g.oval('Palm_'+side,hand.head_local.lerp(hand.tail_local,.55),(.035,.022,.042),skin,None),'hand_'+side)
 # Bracelets now attach near the real wrist, not a fixed world-height ring.
 bind(g.oval('WristBangle_'+side,lower.tail_local,(.030,.027,.007),gold,None),'lowerarm_'+side)
# Sewn shoulder yoke bridges the garment neckline and the arm roots.
for side,sign in [('L',-1),('R',1)]:
 points=[Vector((sign*x*f,0,z*f))for x,z in [(.055,1.375),(.11,1.365),(.16,1.35),(.19,1.325)]]
 o=g.tube('ShoulderYoke_'+side,points,[.056*f,.060*f,.065*f,.072*f],indigo,segments=32);rows=[]
 for i in range(4):rows.extend([{'chest':1-i/3,'upperarm_'+side:i/3}]*32)
 bind(o,rows)
lip=g.material('AsoLip',(.12,.037,.027),rough=.6)
for upper in [True,False]:
 points=[]
 for i in range(25):
  x=(i/24-.5)*.052;z=1.533+(.002 if upper else -.003)*math.sin(math.pi*i/24);points.append((x*f,(face(x,z)-.002)*f,z*f))
 bind(g.tube('LipUpper'if upper else'LipLower',points,[.0025]*25,lip,segments=8),'jaw')
# Wrapped fabric with diagonal folded construction and a swept crown.
for i in range(6):
 o=g.oval('HeadwrapLayer_%02d'%i,(0,.006*f,(1.669+i*.011)*f),((.108-i*.004)*f,(.096-i*.003)*f,.027*f),indigo,None);
 for vertex in o.data.vertices:vertex.co.z+=(vertex.co.x)*(.16 if i%2 else -.12)
 bind(o,'head')
for j in range(11):
 a=math.tau*j/11;points=[((.109-t*.016)*math.sin(a+t*.35)*f,(.097-t*.014)*math.cos(a+t*.35)*f,(1.658+t*.07)*f)for t in [i/8 for i in range(9)]];bind(g.tube('HeadwrapWovenSeam'+str(j),points,[.0014]*9,gold,segments=6),'head')
# Embroidered open edges follow the same garment weights and keep the cream layer visible.
for sign in [-1,1]:
 points=[]
 for i in range(25):
  t=i/24;z=.18+1.21*t;rx=.285*(1-t)+.07*t;ry=.16*(1-t)+.065*t;points.append((sign*rx*math.sin(.30)*f,-ry*math.cos(.30)*f-.002,z*f))
 o=g.tube('RobeWovenEdge'+str(sign),points,[.003]*25,gold,segments=8);rows=[]
 for i in range(25):
  z=points[i][2]/f;lower=max(0,min(1,(.98-z)/.38));chest=max(0,min(1,(z-1.04)/.27));rows.extend([{'pelvis':(1-lower)*(1-chest),'chest':chest,'Dress_L'if sign<0 else'Dress_R':lower}]*8)
 bind(o,rows)
for mat in [skin,indigo,cream]:
 p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.65 if mat==skin else .88;p.inputs['Specular IOR Level'].default_value=.24
# Distinct controlled performances, not duplicate renamed clips. Every action starts/ends neutral.
categories=['IdleStrategist','WalkControlled','Turn','Listen','InspectEvidence','Consider','NegotiateOpen','NegotiateFirm','Agreement','Refusal','ProtectWitnesses','ReactBrokenPromise','DialogueNeutral','DialogueConcern','DialogueResolve','LimbIsolation']
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
actions=[]
for index,name in enumerate(categories):
 act=bpy.data.actions.new(name);rig.animation_data.action=act;frames=180 if name=='LimbIsolation'else 90
 for frame in range(0,frames+1,3):
  t=frame/frames;v=math.sin(math.pi*t)**2;p=math.sin(math.tau*t)
  for b in rig.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0)
  def rot(n,x=0,y=0,z=0):rig.pose.bones[n].rotation_euler=(x,y,z)
  rot('chest',.008*math.sin(math.tau*t));rot('head',.008*p)
  if name=='WalkControlled':
   for side,sgn in [('L',1),('R',-1)]:rot('thigh_'+side,.16*sgn*p);rot('shin_'+side,-.20*max(0,-sgn*p));rot('upperarm_'+side,-.07*sgn*p);rot('Dress_'+side,.07*sgn*p)
  elif name=='Turn':rot('pelvis',0,.10*v,.22*v);rot('head',0,0,.32*v);rot('foot_L',0,0,-.10*v)
  elif name=='LimbIsolation':
   names=[b.name for b in rig.pose.bones if b.name!='root'];phase=t*len(names);n=names[min(len(names)-1,int(phase))];rot(n,.18*math.sin(math.pi*(phase%1)))
  elif name=='IdleStrategist':rot('lowerarm_L',-.14*v);rot('lowerarm_R',-.12*v)
  else:
   # Each authored gesture has independent shoulder/elbow/wrist/head timing and amplitude.
   poses={'Listen':(.10,.18,.04,-.12),'InspectEvidence':(.44,.80,.18,.16),'Consider':(.25,.92,-.18,.10),'NegotiateOpen':(.32,.52,-.40,-.05),'NegotiateFirm':(.43,.60,.16,-.06),'Agreement':(.29,.48,-.12,.13),'Refusal':(.21,.38,.32,-.09),'ProtectWitnesses':(.48,.72,-.36,-.03),'ReactBrokenPromise':(.15,.32,.20,-.17),'DialogueNeutral':(.15,.22,-.08,.02),'DialogueConcern':(.22,.38,-.22,.09),'DialogueResolve':(.31,.44,.13,-.04)}
   shoulder,elbow,wrist,headtilt=poses[name];rot('upperarm_R',-shoulder*v,0,-.12*v);rot('lowerarm_R',-elbow*v);rot('hand_R',wrist*v,.08*p*v);rot('head',headtilt*v,0,(-.14 if name=='Refusal'else .04)*p*v)
   left=.80 if name in ['NegotiateOpen','ProtectWitnesses','InspectEvidence']else .32;rot('upperarm_L',-shoulder*left*v,0,.13*v);rot('lowerarm_L',-elbow*left*v);rot('hand_L',-wrist*.6*v)
   if name=='InspectEvidence':rot('spine_01',.055*v)
   if name.startswith('Dialogue'):rot('jaw',(.045+.025*p)*v)
   for side in ['L','R']:
    for d in range(5):rot(f'digit_{side}_{d}_01',(.08+.035*((index+d)%4))*v);rot(f'digit_{side}_{d}_02',.12*v)
  for b in rig.pose.bones:b.keyframe_insert(data_path='rotation_euler',frame=frame)
 act.use_fake_user=True;actions.append({'name':name,'frames':frames+1,'seconds':frames/30,'review':'REVIEW_REQUIRED'})
rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_euler=(0,0,0)
s.frame_set(0)
parts=[o for o in s.objects if o.type=='MESH'];assert all(o.parent==rig for o in parts)
# Export combined surface while retaining all separate authoring parts and morphs in the scene.
bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in parts:c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();export=bpy.context.object;export.name='SK_AsoYaa'
for o in parts:o.hide_render=True;o.hide_set(True)
assert [(b.name,b.parent.name if b.parent else None,tuple(v for row in b.matrix_local for v in row))for b in rig.data.bones]==rest
s.render.resolution_x=720;s.render.resolution_y=900;s.eevee.taa_render_samples=32
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'AsoYaa.blend'))
bpy.ops.object.select_all(action='DESELECT');export.select_set(True);rig.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'AsoYaa.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
p=OUT/'AsoYaa.glb';raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'key':'AsoYaa','design_id':'aso-yaa-human-v1','height_proposal_m':1.68,'dcc_version':bpy.app.version_string,'units':'metres','scene_sha256':sha(OUT/'AsoYaa.blend'),'glb_sha256':sha(p),'bone_rest_unchanged':True,'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'tail':list(b.tail_local)}for b in rig.data.bones],'actions':actions,'vertices':len(export.data.vertices),'parts':[o.name for o in parts],'creative_approved':False,'limitations':['Hidden construction and thumb splay proposed','Facial performance targets require native curve binding and visual review','Ledger contact not qualified','Clothing clearance and foot contact pending evaluated tests','No new native or packaged acceptance yet']}
(OUT/'rig-map.json').write_text(json.dumps(report,indent=2)+'\n')
for name in ['front','left','right','back','beauty']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(OUT/(name+'_solid.png'));bpy.ops.render.render(write_still=True)
print('ASO_SOURCE_COMPLETE',len(parts),len(rest),len(actions))
