"""Editable individual story designs, using the qualified project mesh/export path.
Hidden views/anatomy are proposals. No creative acceptance is inferred.
"""
import bpy, math, json, hashlib, struct, sys, random
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import character_mesh_tools as g
KEY=sys.argv[sys.argv.index('--')+1];OUT=Path(sys.argv[sys.argv.index('--')+2]).resolve()
if OUT.exists():raise RuntimeError('Preserve existing source revision')
OUT.mkdir(parents=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=g.scene=bpy.context.scene;g.parts=[];g.binds={};g.joints={}
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
s.render.engine='BLENDER_EEVEE_NEXT';s.render.resolution_x=720;s.render.resolution_y=900;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.fps=30;s.eevee.taa_render_samples=32;s.view_settings.view_transform='AgX'
s.world=bpy.data.worlds.new('StoryStudio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
height={'Kwaku':1.45,'AsoYaa':1.68,'EsiHuman':1.70,'OseboHuman':1.98,'KojoTortoise':1.45,'KofiHornbill':1.75,'EsiMoth':1.55}[KEY]
ids={'Kwaku':'kwaku-human-v1','AsoYaa':'aso-yaa-human-v1','EsiHuman':'esi-human-v1','OseboHuman':'osebo-human-v1','KojoTortoise':'kojo-tortoise-v1','KofiHornbill':'kofi-hornbill-v1','EsiMoth':'esi-moth-v1'}
# Coordinates authored at 1.70 metres then uniformly scaled at export and source.
mat=g.material;oval=g.oval;loft=g.loft;tube=g.tube;bone=g.bone
skin=mat('Skin',(.105,.046,.025));cream=mat('Cream_Linen',(.65,.52,.32),rough=.9)
indigo=mat('Indigo_Woven',(.014,.037,.105),rough=.92);gold=mat('Woven_Gold',(.53,.28,.06),metal=.5,rough=.44)
dark=mat('Hair_Pupil',(.009,.006,.004));white=mat('Eyes',(.76,.68,.51),rough=.23)
leather=mat('Leather',(.065,.025,.012));red=mat('Burgundy',(.17,.012,.026));orange=mat('Ochre_Woven',(.50,.16,.025));green=mat('Tortoise_Skin',(.19,.25,.095));shell=mat('Shell',(.14,.065,.024));amber=mat('Amber',(.55,.26,.025),rough=.25)
if KEY=='KojoTortoise':skin=green
if KEY=='KofiHornbill':skin=mat('Feathers_Black',(.013,.018,.026))
if KEY=='EsiMoth':skin=indigo
bone('root',(0,0,0),(0,0,.1));bone('pelvis',(0,0,.84),(0,0,1),'root');bone('spine_01',(0,0,1),(0,0,1.15),'pelvis');bone('spine_02',(0,0,1.15),(0,0,1.30),'spine_01');bone('chest',(0,0,1.30),(0,0,1.40),'spine_02');bone('neck',(0,0,1.40),(0,0,1.48),'chest');bone('head',(0,0,1.48),(0,0,1.70),'neck');bone('jaw',(0,-.045,1.51),(0,-.13,1.49),'head')
wide=1.23 if KEY=='OseboHuman' else 1.12 if KEY=='KojoTortoise' else .90 if KEY in ['EsiHuman','AsoYaa'] else 1
loft('Torso_Anatomical',[(0,0,.83,.14*wide,.09),(0,0,.94,.17*wide,.105),(0,0,1.05,.135*wide,.09),(0,0,1.18,.16*wide,.105),(0,0,1.31,.20*wide,.115),(0,0,1.38,.17*wide,.09)],skin,chain=['pelvis','spine_01','spine_02','chest'])
loft('Neck',[(0,0,1.37,.063,.06),(0,0,1.46,.057,.056),(0,-.01,1.50,.065,.058)],skin,'neck')
# Shaped jaw, cheeks, brow, separate mouth, lips, nose and socketed eyes.
loft('Head_FacialContour',[(0,-.015,1.47,.045,.055),(0,-.025,1.50,.070,.070),(0,-.015,1.55,.097,.085),(0,-.005,1.61,.105,.084),(0,.005,1.67,.085,.075),(0,.01,1.70,.045,.04)],skin,'head',segments=32)
oval('Jaw',(0,-.042,1.51),(.067,.055,.032),skin,'jaw')
for sign,side in [(-1,'L'),(1,'R')]:
 bone('eye_'+side,(sign*.043,-.072,1.603),(sign*.043,-.10,1.603),'head')
 oval('Lid_'+side,(sign*.044,-.079,1.604),(.036,.018,.024),skin,'head')
 oval('Eye_'+side,(sign*.044,-.093,1.604),(.026,.012,.017),white,'eye_'+side)
 oval('Iris_'+side,(sign*.044,-.104,1.604),(.013,.003,.014),amber,'eye_'+side)
 oval('Pupil_'+side,(sign*.044,-.107,1.604),(.006,.002,.008),dark,'eye_'+side)
 tube('Brow_'+side,[(sign*.016,-.082,1.632),(sign*.044,-.09,1.636),(sign*.076,-.073,1.627)],[.005,.006,.003],dark,bone='head')
 oval('Ear_'+side,(sign*.10,0,1.59),(.020,.016,.033),skin,'head')
 shoulder=(sign*.185*wide,0,1.34);elbow=(sign*.28*wide,-.008,1.13);wrist=(sign*.32*wide,-.025,.935)
 bone('clavicle_'+side,(0,0,1.34),shoulder,'chest');bone('upperarm_'+side,shoulder,elbow,'clavicle_'+side);bone('lowerarm_'+side,elbow,wrist,'upperarm_'+side);bone('hand_'+side,wrist,(sign*.325*wide,-.03,.86),'lowerarm_'+side)
 loft('Arm_'+side,[(shoulder[0],0,1.37,.061,.062),(sign*.225*wide,0,1.26,.062,.058),(elbow[0],-.008,1.13,.035,.036),(sign*.30*wide,-.02,1.03,.042,.035),(wrist[0],-.025,.935,.026,.023)],skin,chain=['clavicle_'+side,'upperarm_'+side,'lowerarm_'+side,'hand_'+side])
 oval('Hand_'+side,(sign*.325*wide,-.03,.89),(.039,.025,.048),skin,'hand_'+side)
 for d in range(5):
  x=sign*(.295*wide+d*.015);z=.875;end=.805+abs(d-2)*.009
  a=f'digit_{side}_{d}_01';b=f'digit_{side}_{d}_02';bone(a,(x,-.03,z),(x,-.035,(z+end)/2),'hand_'+side);bone(b,(x,-.035,(z+end)/2),(x,-.04,end),a)
  tube('Finger_'+side+str(d),[(x,-.03,z),(x,-.035,(z+end)/2),(x,-.04,end)],[.008,.007,.005],skin,bones=[a,b])
 bone('thigh_'+side,(sign*.095,0,.87),(sign*.11,-.015,.49),'pelvis');bone('shin_'+side,(sign*.11,-.015,.49),(sign*.115,0,.105),'thigh_'+side);bone('foot_'+side,(sign*.115,0,.105),(sign*.115,-.13,.065),'shin_'+side);bone('ball_'+side,(sign*.115,-.13,.065),(sign*.115,-.20,.065),'foot_'+side)
 loft('Leg_'+side,[(sign*.095,0,.88,.085,.084),(sign*.105,.005,.73,.078,.073),(sign*.11,-.015,.50,.048,.048),(sign*.113,0,.35,.061,.055),(sign*.115,0,.105,.030,.033)],skin,chain=['thigh_'+side,'shin_'+side,'foot_'+side])
 oval('Foot_'+side,(sign*.115,-.075,.065),(.050,.115,.048),skin,'foot_'+side)
 for d in range(5):oval('Toe_'+side+str(d),(sign*(.079+d*.018),-.165,.05),(.009,.029,.015),skin,'ball_'+side)
 if KEY not in ['EsiMoth','KofiHornbill','KojoTortoise']:
  oval('SandalSole_'+side,(sign*.115,-.07,.025),(.056,.123,.017),leather,'foot_'+side)
  tube('SandalStrap_'+side,[(sign*.065,-.10,.062),(sign*.115,-.10,.105),(sign*.165,-.10,.062)],[.012]*3,leather,bone='foot_'+side)
oval('Nose',(0,-.096,1.568),(.025,.028,.026),skin,'head');tube('Mouth', [(-.033,-.087,1.532),(0,-.099,1.529),(.033,-.087,1.532)],[.004,.004,.004],dark,bone='jaw')
# Clothing uses continuous ring topology with woven borders and independent bones.
def robe(name,top,bottom,width,material):
 for side,sign in [('L',-1),('R',1)]:bone(name+'_'+side,(sign*.08,0,top),(sign*.12,0,bottom),'pelvis')
 rings=[(0,0,top-t*(top-bottom),.16+t*(width-.16),.11+t*.045) for t in [i/18 for i in range(19)]]
 o=loft(name,rings,material,chain=['pelvis',name+'_L',name+'_R'],segments=40)
 # Add real geometric hems/motifs, no poster plane.
 for t in [.04,.13,.92,.98]:
  z=top-t*(top-bottom);r=.16+t*(width-.16)
  tube(name+'_Hem'+str(t),[(r*math.cos(i*math.pi/32),(.11+t*.045)*math.sin(i*math.pi/32),z) for i in range(65)],[.004]*65,gold,bone='pelvis' if t<.2 else name+'_L')
 return o
if KEY=='Kwaku':
 loft('Linen_Shirt',[(0,0,.94,.166,.12),(0,0,1.12,.17,.12),(0,0,1.31,.215,.13),(0,0,1.38,.15,.10)],cream,chain=['pelvis','spine_01','chest'])
 for sign,side in [(-1,'L'),(1,'R')]:
  loft('CroppedTrousers_'+side,[(sign*.095,0,.88,.09,.095),(sign*.105,0,.70,.09,.09),(sign*.11,-.01,.51,.068,.063),(sign*.11,-.01,.46,.068,.063)],cream,chain=['pelvis','thigh_'+side,'shin_'+side])
  oval('BeltPouch_'+side,(sign*.16,-.12,.92),(.045,.027,.065),leather,'pelvis')
 # Separate front/back narrow tabard panels preserve cropped-trouser silhouette.
 for rear in [False,True]:
  y=.12 if rear else -.137
  g.panel('TabardBack' if rear else 'TabardFront',[(-.075,y,.96),(.075,y,.96),(.078,y,.48),(-.078,y,.48)],indigo,'pelvis')
 # Continuous diagonal woven cloth ribbon with proper quad surface.
 verts=[]
 for i in range(18):
  t=i/17;x=-.17+.30*t;z=1.35-.40*t
  for d in [-1,1]:verts.append((x+d*.038,-.139,z+d*.026))
 faces=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(17)]
 g.mesh('DiagonalSash',verts,faces,indigo,'chest')
 for sign in [-1,1]:tube('SashWovenEdge'+str(sign),[(x+sign*.038,y-.002,z+sign*.026) for x,y,z in verts[::2]],[.003]*18,gold,bone='chest')
if KEY in ['AsoYaa','EsiHuman']:
 robe('Dress',1.16,.08,.29,indigo if KEY=='AsoYaa' else orange)
 loft('Bodice',[(0,0,.98,.159,.115),(0,-.003,1.16,.17,.12),(0,0,1.31,.20,.125)],indigo if KEY=='AsoYaa' else orange,chain=['pelvis','spine_01','chest'])
 for sign,side in [(-1,'L'),(1,'R')]:
  oval('Earring_'+side,(sign*.115,-.005,1.55),(.014,.006,.033),gold,'head')
  for z in [1.00,1.02,1.04]:oval('Bracelet_'+side+str(z),(sign*.31,-.025,z),(.037,.029,.008),gold,'lowerarm_'+side)
 for i in range(24):
  a=i*math.pi/12;oval('Necklace'+str(i),(.105*math.cos(a),.08*math.sin(a)-.018,1.37-.02*math.cos(a)),(.009,.008,.012),gold,'chest')
if KEY=='AsoYaa':
 for i in range(7):
  a=i*.45;oval('HeadwrapFold'+str(i),(.018*math.cos(a),.012*math.sin(a),1.66+i*.008),(.112,.10,.047),indigo,'head')
 for side,sign in [('L',-1),('R',1)]:
  tube('RobeSleeve_'+side,[(sign*.18,0,1.33),(sign*.25,-.01,1.17),(sign*.30,-.02,1.02)],[.075,.075,.065],indigo,bones=['upperarm_'+side,'lowerarm_'+side])
if KEY in ['Kwaku','EsiHuman','OseboHuman']:
 rng=random.Random(518)
 for i in range(85 if KEY=='Kwaku' else 46):
  a=i*2.39996;r=.085*math.sqrt(i/(85 if KEY=='Kwaku' else 46));x=r*math.cos(a);y=r*math.sin(a)
  if KEY=='EsiHuman':
   tube('Loc'+str(i),[(x,y,1.70),(x*1.25,y*1.25,1.65),(x*1.3,y*1.3,1.48+rng.uniform(-.04,.08))],[.012,.011,.008],dark,bone='head')
  else:oval('HairCurl'+str(i),(x,y,1.688+.04*(1-r/.1)),(.015,.015,.017),dark,'head')
if KEY=='EsiHuman':
 bone('instrument',(0,-.20,1.12),(0,-.20,1.35),'chest')
 oval('Instrument_ProposedBody',(.03,-.23,1.07),(.115,.045,.16),leather,'instrument')
 tube('Instrument_Neck',[(.03,-.23,1.15),(.23,-.23,1.60)],[.027,.023],leather,bone='instrument')
 for i in range(5):tube('String'+str(i),[(.015+i*.005,-.279,.99),(.21+i*.005,-.258,1.58)],[.0008]*2,gold,bone='instrument')
if KEY=='OseboHuman':
 loft('FittedArmour',[(0,0,.91,.20,.12),(0,0,1.1,.19,.13),(0,0,1.32,.26,.15),(0,0,1.40,.21,.13)],leather,chain=['pelvis','spine_01','chest'])
 robe('ArmourSkirt',.94,.30,.23,leather)
 bone('cape',(0,.08,1.38),(0,.23,.35),'chest')
 loft('Cape',[(0,.08,1.38,.25,.08),(0,.16,1.14,.29,.09),(0,.22,.85,.33,.09),(0,.25,.48,.35,.08),(0,.25,.30,.36,.06)],red,'cape')
 oval('CapeClasp',(-.13,-.135,1.37),(.035,.015,.035),gold,'chest')
if KEY=='KojoTortoise':
 bone('shell_root',(0,.09,1.0),(0,.25,1.30),'pelvis')
 oval('RigidShell',(0,.17,1.10),(.30,.20,.39),shell,'shell_root')
 for i in range(7):
  z=.83+i*.085;r=.28*math.sin((i+1)*math.pi/9)
  tube('ShellScuteRidge'+str(i),[(r*math.cos(a),.18+.192*math.sin(a),z) for a in [j*math.pi/32 for j in range(65)]],[.006]*65,leather,bone='shell_root')
 oval('Plastron',(0,-.1,1.12),(.18,.035,.24),cream,'chest')
 robe('Apron',.96,.53,.20,indigo)
 bone('staff',( .36,-.08,.0),(.36,-.08,1.45),'hand_R')
 tube('Staff',[(.36,-.08,.02),(.36,-.08,.7),(.36,-.08,1.40),(.39,-.08,1.47)],[.018,.02,.025,.018],leather,bone='staff')
if KEY=='KofiHornbill':
 bone('beak_lower',(0,-.10,1.55),(0,-.37,1.53),'head')
 oval('Beak_Curved',(0,-.21,1.60),(.085,.21,.065),gold,'head');oval('LowerBeak',(0,-.22,1.55),(.065,.18,.025),gold,'beak_lower');oval('Casque',(0,-.16,1.67),(.058,.14,.047),gold,'head')
 oval('CreamBreast',(0,-.095,1.25),(.145,.035,.18),cream,'chest')
 for sign,side in [(-1,'L'),(1,'R')]:
  # Folded feather fans belong to the two existing arms, never extra arms.
  for i in range(11):oval('WingFeather_'+side+str(i),(sign*(.23+i*.009),.045,1.27-i*.027),(.025,.025,.15),skin,'lowerarm_'+side)
  for i in range(3):tube('BirdToe_'+side+str(i),[(sign*.115,0,.07),(sign*(.08+i*.035),-.22,.025)],[.012,.007],gold,bone='foot_'+side)
 bone('tail_01',(0,.07,.90),(0,.23,.75),'pelvis');bone('tail_02',(0,.23,.75),(0,.35,.62),'tail_01')
 for i in range(7):oval('TailFeather'+str(i),((i-3)*.025,.24,.75),(.025,.12,.13),skin,'tail_02')
 for i in range(5):oval('Crest'+str(i),((i-2)*.02,.04+i*.015,1.70+i*.005),(.018,.07,.025),skin,'head')
 oval('Satchel',(-.18,-.11,.93),(.075,.04,.10),indigo,'pelvis');oval('OpticalProp',(.32,-.06,.89),(.035,.025,.035),gold,'hand_R')
if KEY=='EsiMoth':
 oval('Collar',(0,0,1.42),(.18,.14,.075),cream,'chest');robe('Garment',.95,.05,.19,indigo)
 for side,sign in [('L',-1),('R',1)]:
  bone('antenna_'+side,(sign*.05,0,1.68),(sign*.13,-.02,1.86),'head');tube('Antenna_'+side,[(sign*.05,0,1.68),(sign*.09,-.01,1.80),(sign*.13,-.02,1.86)],[.008,.008,.004],gold,bone='antenna_'+side)
  for lower in [False,True]:
   name=('hindwing_' if lower else 'upperwing_')+side;z=1.02 if lower else 1.37
   bone(name,(sign*.08,.08,z),(sign*.58,.12,z+(.25 if not lower else -.24)),'pelvis' if lower else 'chest')
   coords=[(sign*.09,.10,z),(sign*.55,.12,z+.30),(sign*.67,.13,z+.12),(sign*.55,.14,z-.22),(sign*.13,.10,z-.30)]
   g.panel(name,coords,indigo,name)
   tube(name+'_Border',coords+[coords[0]],[.009]*6,gold,bone=name)
   for i in range(4):oval(name+'_Pattern'+str(i),(sign*(.25+i*.065),.085,z+.10-i*.045),(.032,.014,.065),cream,name)
# Fine original woven motifs in real geometry on front cloth, each stays editable.
if KEY in ['Kwaku','AsoYaa','EsiHuman','KojoTortoise']:
 for row in range(8):
  z=.58+row*.065
  for col in ([-.5,.5] if KEY=='Kwaku' else [-1,0,1]):
   x=col*.063
   tube('WovenChevron'+str(row)+'_'+str(col),[(x-.018,-.162,z+.018),(x,-.166,z),(x+.018,-.162,z+.018)],[.0028]*3,gold,bone='pelvis' if z<1 else 'spine_01')
# Bind full independent anatomy, preserve editable named pieces.
arm=bpy.data.armatures.new('SKEL_'+KEY);rig=bpy.data.objects.new('SKEL_'+KEY,arm);s.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for n,(h,t,p) in g.joints.items():
 b=arm.edit_bones.new(n);b.head=h;b.tail=t
 if p:b.parent=arm.edit_bones[p]
bpy.ops.object.mode_set(mode='OBJECT')
for o in g.parts:
 for n in {n for row in g.binds[o.name] for n,w in row.items() if w>0}:o.vertex_groups.new(name=n)
 for i,row in enumerate(g.binds[o.name]):
  total=sum(w for w in row.values() if w>0)
  for n,w in row.items():
   if w>0:o.vertex_groups[n].add([i],w/total,'REPLACE')
 mod=o.modifiers.new('Skin','ARMATURE');mod.object=rig;o.parent=rig
# Uniform scale is applied to geometry and bone data once, not left on object roots.
factor=height/1.70
for o in g.parts:
 for v in o.data.vertices:v.co*=factor
for b in arm.bones:pass
bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for b in arm.edit_bones:b.head*=factor;b.tail*=factor
bpy.ops.object.mode_set(mode='OBJECT')
rig['design_id']=ids[KEY];rig['creative_approval']='PENDING';rig['hidden_anatomy']='PROPOSED';rig['height_proposal_m']=height
categories={'Kwaku':['Idle','Walk','Run','Turn','JumpLand','WebStep','BorrowedVoice','TrickMirror','InspectLedger','CapturedRetry','LimbIsolation'],'AsoYaa':['Idle','WalkTurn','ListenSpeak','Negotiate','PresentLedger','Agree','Refuse','LimbIsolation'],'EsiHuman':['Idle','WalkTurn','ListenSpeak','Perform','AddressCrowd','PresentInstrument','React','LimbIsolation'],'OseboHuman':['IdleGuard','Patrol','RunPursuit','Search','CaptureReach','Command','Recover','LimbIsolation'],'KojoTortoise':['Idle','Walk','TurnInPlace','StaffPlant','InspectClue','PresentEvidence','ThinkReact','LimbIsolation'],'KofiHornbill':['Idle','Walk','Run','TurnInPlace','WingFoldSpread','InspectSatchel','ScoutLook','LimbIsolation'],'EsiMoth':['IdleHover','MoveHover','WingOpenFold','WeaveThread','PointGuide','React','SettleResume','LimbIsolation']}[KEY]
actions=[]
for category in categories:
 act=bpy.data.actions.new(category);rig.animation_data_create();rig.animation_data.action=act;frames=120 if category=='LimbIsolation' else 72
 for frame in range(0,frames+1,3):
  t=frame/30;phase=math.sin(t*2*math.pi/(frames/30));amount=math.sin(math.pi*frame/frames)
  for b in rig.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0);b.location=(0,0,0)
  def rot(n,x=0,y=0,z=0):
   if n in rig.pose.bones:rig.pose.bones[n].rotation_euler=(x,y,z)
  rot('chest',.015*math.sin(t*2));rot('head',0,.025*math.sin(t),.025*phase)
  if category in ['Walk','WalkTurn','Run','RunPursuit','Patrol','MoveHover','TurnInPlace','Turn']:
   for side,sign in [('L',1),('R',-1)]:
    a=.5 if category in ['Run','RunPursuit'] else .25
    rot('thigh_'+side,sign*a*phase);rot('shin_'+side,-max(0,-sign*phase)*a*1.3);rot('upperarm_'+side,-sign*a*.5*phase)
  elif category=='LimbIsolation':
   names=list(g.joints)[1:];idx=min(len(names)-1,int(frame/frames*len(names)));rot(names[idx],.22*math.sin((frame/frames*len(names)-idx)*math.pi))
  elif category in ['WingFoldSpread','WingOpenFold']:
   for side,sign in [('L',1),('R',-1)]:rot('upperarm_'+side,0,0,sign*.7*amount);rot('upperwing_'+side,0,0,sign*.5*amount);rot('hindwing_'+side,0,0,-sign*.3*amount)
  else:
   idx=categories.index(category);rot('upperarm_R',-(.35+idx*.045)*amount,0,-.12*amount);rot('lowerarm_R',-.4*amount);rot('upperarm_L',-.25*amount);rot('jaw',.08*max(0,phase));rot('head',.06*amount,0,.12*phase)
   if category in ['InspectLedger','InspectClue','InspectSatchel']:rot('spine_01',.18*amount)
   if category=='CapturedRetry':rot('spine_01',-.25*amount)
  for b in rig.pose.bones:b.keyframe_insert(data_path='rotation_euler',frame=frame)
 act.use_fake_user=True;actions.append({'name':category,'frames':frames+1,'seconds':frames/30,'status':'authored_draft_requires_contact_and_performance_review'})
rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_euler=(0,0,0)
s.frame_set(0)
for name,loc,power in [('Key',(-3,-4,5),650),('Fill',(3,-2,3),350),('Rim',(1,3,4),800)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.size=3;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;g.aim(o,(0,0,height*.6))
cameras={}
for name,loc in [('front',(0,-5,height*.5)),('left',(-5,0,height*.5)),('right',(5,0,height*.5)),('back',(0,5,height*.5)),('beauty',(3,-5,height*1.2))]:
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=height*1.40;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;g.aim(o,(0,0,height*.52));cameras[name]=o
s.camera=cameras['beauty'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(KEY+'.blend')))
bpy.ops.object.select_all(action='DESELECT')
copies=[]
for o in g.parts:
 c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);copies.append(c)
for o in copies:o.select_set(True)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();joined=bpy.context.object;joined.name='SK_'+KEY;rig.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/(KEY+'.glb')),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True)
p=OUT/(KEY+'.glb');raw=p.read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length]);doc['asset'].pop('generator',None);payload=json.dumps(doc,separators=(',',':')).encode();payload+=b' '*((-len(payload))%4);tail=raw[20+length:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(tail))+struct.pack('<II',len(payload),0x4e4f534a)+payload+tail)
bpy.data.objects.remove(joined,do_unlink=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'design_id':ids[KEY],'key':KEY,'dcc_version':bpy.app.version_string,'units':'metres','height_proposal_m':height,'scene_sha256':sha(OUT/(KEY+'.blend')),'glb_sha256':sha(p),'creative_approval':False,'native_import_executed':False,'status':'AUTHORED_DRAFT_NOT_FINAL','bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'tail':list(b.tail_local),'rest_matrix':[list(r) for r in b.matrix_local]} for b in arm.bones],'parts':[{'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)} for o in g.parts],'actions':actions,'cameras':{n:{'matrix':[list(r) for r in c.matrix_world],'ortho_scale':c.data.ortho_scale} for n,c in cameras.items()},'limitations':['Hidden anatomy and all proportions proposed pending review','Authored motion drafts are not contact-qualified performance','No final facial morph/cloth/rights/cultural approval','No campaign mapping change']}
(OUT/'rig-map.json').write_text(json.dumps(report,indent=2)+'\n')
for n in ['front','left','right','back','beauty']:
 s.camera=cameras[n];s.render.filepath=str(OUT/(n+'_solid.png'));bpy.ops.render.render(write_still=True)
for o in g.parts:
 mod=o.modifiers.new('ActualTopology','WIREFRAME');mod.thickness=.0007;mod.use_replace=True
s.camera=cameras['front'];s.render.filepath=str(OUT/'front_topology.png');bpy.ops.render.render(write_still=True)
(OUT/'source-status.json').write_text(json.dumps(report,indent=2)+'\n')
print('STORY_SOURCE_SAVED',KEY,len(g.parts),len(arm.bones),len(actions))
