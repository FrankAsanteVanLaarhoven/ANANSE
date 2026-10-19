"""Actual saved-scene pose grids and three lighting modes with recorded cameras."""
import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];key=sys.argv[sys.argv.index('--')+1];rev='Authored_v035'if key=='Kwaku'else'Authored_v021';out=R/'.local/verification/art-pass2-20261016'/(key+'-art-review-final');out.mkdir(exist_ok=False);src=R/'SourceArt/Characters'/key/rev/(key+'.blend');bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');mesh=bpy.data.objects['SK_'+key];height=1.5 if key=='Kwaku'else 2.03;face=1.375 if key=='Kwaku'else 1.91
for ob in s.objects:
 if ob.type=='LIGHT':ob.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.device='CPU';s.render.resolution_x=640;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1;s.world.color=(.07,.07,.07);lights=[]
for name,loc,power,size in [('key',(-2,-3,3),350,3),('fill',(2,-2,2),260,3),('rim',(0,2,3),300,2)]:
 d=bpy.data.lights.new('Pass2_'+name,'AREA');d.energy=power;d.size=size;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,height*.6))-o.location).to_track_quat('-Z','Y').to_euler();lights.append(o)
cam=bpy.data.objects.new('Pass2_Camera',bpy.data.cameras.new('Pass2_Camera'));s.collection.objects.link(cam);s.camera=cam;rows=[]
def camera(loc,target,lens=70,ortho=None):
 globals()['camera_target']=Vector(target);cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO'if ortho else'PERSP';cam.data.lens=lens
 if ortho:cam.data.ortho_scale=ortho
 bpy.context.view_layer.update()
def reset(action=None,frame=0):
 rig.animation_data.action=None
 for p in rig.pose.bones:p.location=(0,0,0);p.rotation_euler=(0,0,0);p.scale=(1,1,1)
 for shape in mesh.data.shape_keys.key_blocks:shape.value=0
 if action:rig.animation_data.action=bpy.data.actions[action]
 s.frame_set(frame);bpy.context.view_layer.update()
 if key=='Kwaku':bpy.data.objects['Ledger_SeparateProp'].hide_render=action!='InspectLedger'
def render(name,wire=False):
 modifier=None
 if wire:
  modifier=mesh.modifiers.new('ActualTopology','WIREFRAME');modifier.thickness=.00035;modifier.use_replace=False
 p=out/(name+'.png');s.render.filepath=str(p);bpy.ops.render.render(write_still=True);rows.append({'name':name,'image_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'camera_matrix':[list(r)for r in cam.matrix_world],'lens_mm':cam.data.lens,'type':cam.data.type,'distance_m':(cam.location-camera_target).length,'target_m':list(camera_target),'exposure':0,'lights':[{'name':o.name,'position':list(o.location),'power_W':o.data.energy,'size_m':o.data.size}for o in lights],'pose':{p.name:list(p.rotation_euler)for p in rig.pose.bones if sum(abs(x)for x in p.rotation_euler)>1e-5},'morph_values':{k.name:k.value for k in mesh.data.shape_keys.key_blocks if k.value>0}})
 if modifier:mesh.modifiers.remove(modifier)
def arms(raised):
 from mathutils import Matrix
 def aim(name,a,b):
  direction=(b-a).normalized();x=direction.cross(Vector((0,1,0))).normalized();z=x.cross(direction).normalized();mat=Matrix(((x.x,direction.x,z.x),(x.y,direction.y,z.y),(x.z,direction.z,z.z))).to_4x4();mat.translation=a;rig.pose.bones[name].matrix=mat;bpy.context.view_layer.update()
 for side,sign in [('L',-1),('R',1)]:
  upper=rig.data.bones['upperarm_'+side];lower=rig.data.bones['lowerarm_'+side];a=upper.head_local;T=Vector((sign*(.18 if key=='Kwaku'else.27),-.03 if raised else-.30 if key=='Kwaku'else-.39,(1.47 if key=='Kwaku'else 1.97)if raised else(1.14 if key=='Kwaku'else 1.44)));d=(T-a).length;u=(T-a).normalized();q=(upper.length**2-lower.length**2+d*d)/(2*d);h=math.sqrt(max(0,upper.length**2-q*q));pole=Vector((sign,0,-.3));pole=(pole-u*pole.dot(u)).normalized();E=a+q*u+h*pole;aim(upper.name,a,E);aim(lower.name,E,T)
poses=[('NEUTRAL',None,0),('A_pose_rest',None,0),('walk_contact','Walk'if key=='Kwaku'else'Patrol',18),('run_contact','Run'if key=='Kwaku'else'RunPursuit',18),('left_turn','Turn'if key=='Kwaku'else'TurnStop',18),('right_turn','Turn'if key=='Kwaku'else'TurnStop',42),('arms_forward',None,0),('arms_raised',None,0),('maximum_elbow_bend',None,0),('maximum_wrist_bend',None,0),('prop_interaction','InspectLedger'if key=='Kwaku'else'CaptureReach',35),('dialogue_gesture','BorrowedVoice'if key=='Kwaku'else'Command',22),('capture_reaction','CapturedRetry'if key=='Kwaku'else'StaggerRecover',20),('deep_ankle_flexion',None,0)]
# Resolve actual existing action IDs explicitly; missing categories are visible failures.
actions={a.name for a in bpy.data.actions};aliases={'Walk':'WalkRun','Run':'WalkRun','CapturedRetry':'CaptureReact'}
for name,action,frame in poses:
 if action not in actions and action is not None:action=aliases.get(action,action)
 assert action is None or action in actions,(key,name,action,sorted(actions));reset(action,frame)
 if name=='arms_forward':arms(False)
 if name=='arms_raised':arms(True)
 if name=='maximum_elbow_bend':
  for side in ['L','R']:rig.pose.bones['lowerarm_'+side].rotation_euler.x=2.25
 if name=='maximum_wrist_bend':
  for side in ['L','R']:rig.pose.bones['hand_'+side].rotation_euler.x=1.13
 if name=='deep_ankle_flexion':
  for side in ['L','R']:rig.pose.bones['foot_'+side].rotation_euler.x=.85
 camera((-2.4,-3.7,height*.78),(0,0,height*.53),60);render('pose_'+name);render('pose_'+name+'_wire',True)
# Hero hand/paw views, not proxy contact markers.
for name in ['neutral','partial_curl','fist','point']:
 reset()
 for side in ['L','R']:
  for i in range(5 if key=='Kwaku'else 4):
   for seg in ['01','02']:rig.pose.bones[f'digit_{side}_{i}_{seg}'].rotation_euler.x=(.55 if name=='partial_curl'else 1.05 if name=='fist'else.95 if name=='point'and i!=1 else 0)
 target=rig.data.bones['hand_L'].head_local.lerp(rig.data.bones['hand_L'].tail_local,.75);camera(target+Vector((-.12,-.30,.025)),target,70);render(('hands_'if key=='Kwaku'else'paw_')+name)
for mode in ['neutral_diagnostic','gameplay','cinematic']:
 reset();powers=(350,260,300)if mode=='neutral_diagnostic'else(450,300,350)if mode=='gameplay'else(400,280,400)
 for light,power in zip(lights,powers):light.data.energy=power
 camera((0,-1.35,face),(0,-.04,face),70);render('face_'+mode)
 camera((-1.4,-3.4,height*.77),(0,0,height*.53),60);render(mode)
reset('InspectLedger'if key=='Kwaku'else'CaptureReach',35);camera((-.45,-1.2,1.08 if key=='Kwaku'else 1.60),(0,-.20,1.05 if key=='Kwaku'else 1.58),70);render('ledger_grip_closeup'if key=='Kwaku'else'capture_reach');render('clothing_deformation'if key=='Kwaku'else'cape_deformation')
for expression in ['Neutral','Blink','Concern','Suspicion','Determination','FearStartle','MouthOpen','Speech_A','Speech_O','Speech_M']:
 reset()
 if expression=='Blink':
  for side in ['L','R']:mesh.data.shape_keys.key_blocks['Blink_'+side].value=1
 elif expression!='Neutral':mesh.data.shape_keys.key_blocks[expression].value=1
 camera((0,-1.35,face),(0,-.04,face),70);render('expression_'+expression)
if key=='OseboLeopard':
 for label,action,frame in [('pursuit','RunPursuit',18),('command','Command',22),('tail_extreme','TurnStop',42)]:reset(action,frame);camera((-2,-3.6,height*.7),(0,0,height*.53),60);render(label)
(out/'review.json').write_text(json.dumps({'source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'views':rows,'creative_status':'REVIEW_REQUIRED','speech_performance_complete':False,'limitations':['Pose angles are declared diagnostic samples, not full approved joint limits','No source image can approve hidden anatomy','Source views are not native package captures']},indent=2)+'\n');print('ART_POSE_GRID_RENDERED',key,len(rows))
