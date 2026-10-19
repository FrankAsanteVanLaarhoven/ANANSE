"""Read-only source contact/deformation captures and geometric measurements."""
import bpy,json,hashlib,math,os,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];source=R/'SourceArt/Characters/AsoYaa/Authored_v018';out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(source/'AsoYaa.blend'));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');mesh=bpy.data.objects['SK_AsoYaa'];ledger=bpy.data.objects['Ledger_SeparateProp'];ledger.hide_set(False);ledger.hide_render=False;s.eevee.taa_render_samples=32
sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g
g.scene=s;grip=Matrix(json.loads((source/'rig-map.json').read_text())['ledger']['ledger_to_hand_R']);park=Matrix.Translation(Vector((0,-.30,1.018)));cameras={}
def camera(name,loc,target,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;g.aim(o,target);return o
close=camera('HandsContact',(.6,-1.5,1.18),(0,-.30,1.06),.58);face=camera('FaceExpression',(0,-3,1.59),(0,0,1.59),.42)
def pose(action=None,frame=0):
 rig.animation_data.action=bpy.data.actions[action]if action else None;s.frame_set(frame)
 if not action:
  for b in rig.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0)
 bpy.context.view_layer.update()
def prop(frame):
 held=rig.matrix_world@rig.pose.bones['hand_R'].matrix@grip
 if frame<48:ledger.matrix_world=park
 elif frame<=180:ledger.matrix_world=held
 else:
  alpha=max(0,min(1,(204-frame)/24));alpha=alpha*alpha*(3-2*alpha);ledger.matrix_world=Matrix.LocRotScale(park.translation.lerp(held.translation,alpha),park.to_quaternion().slerp(held.to_quaternion(),alpha),Vector((1,1,1)))
def snap(name,cam):
 s.camera=cam;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);cameras[name]={'matrix_world':[list(row)for row in cam.matrix_world],'orthographic_scale_m':cam.data.ortho_scale,'lens_mm':cam.data.lens,'exposure_stops':s.view_settings.exposure}
contact_ids={group:[v.index for v in mesh.data.vertices if any(mesh.vertex_groups[a.group].name==group and a.weight>.5 for a in v.groups)]for side in ['L','R']for group in ['hand_'+side,'digit_'+side+'_0_02','digit_'+side+'_1_02','digit_'+side+'_2_02','digit_'+side+'_3_02','digit_'+side+'_4_02']}
phases={'ledger_contact_start':48,'ledger_stable_hold':72,'ledger_inspection_closeup':108,'ledger_gesture_closeup':144,'ledger_release':204};metrics=[]
for frame in range(0,241):
 pose('InspectEvidence',frame);prop(frame)
 if 48<=frame<=180:
  evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());data=evaluated.to_mesh();inv=ledger.matrix_world.inverted();samples={}
  for side in ['L','R']:
   for group in ['hand_'+side,'digit_'+side+'_0_02','digit_'+side+'_1_02','digit_'+side+'_2_02','digit_'+side+'_3_02','digit_'+side+'_4_02']:
    ids=contact_ids[group];distance=[];penetration=[]
    for i in ids:
     p=inv@(mesh.matrix_world@data.vertices[i].co);q=Vector((abs(p.x)-.115,abs(p.y)-.085,abs(p.z)-.0145));distance.append(max(q,default=0)if max(q)<0 else Vector(tuple(max(0,v)for v in q)).length)
     if max(q)<0:penetration.append(-max(q))
    samples[group]={'rendered_vertices':len(ids),'nearest_surface_cm':100*min((abs(x)for x in distance),default=999),'max_penetration_cm':100*max(penetration,default=0)}
  metrics.append({'frame':frame,'seconds':frame/30,'book_world_m':[list(row)for row in ledger.matrix_world],'contacts':samples});evaluated.to_mesh_clear()
 for name,f in phases.items():
  if frame==f:snap(name,close)
for name,act in [('hands_relaxed','IdleStrategist'),('hands_explanation','NegotiateOpen'),('hands_point','NegotiateFirm'),('hands_agreement','Agreement'),('hands_refusal','Refusal'),('hands_warning','ProtectWitnesses')]:
 ledger.hide_render=True;pose(act,45);snap(name,camera(name,(.1,-3,.96),(0,-.07,.98),.9))
for name,act in [('robe_neutral',None),('robe_walk','WalkControlled'),('robe_turn','Turn'),('robe_negotiation','NegotiateOpen'),('robe_ledger','InspectEvidence')]:
 pose(act,108 if act=='InspectEvidence'else 45);ledger.hide_render=act!='InspectEvidence'
 if not ledger.hide_render:prop(108)
 snap(name,bpy.data.objects['beauty'])
pose();ledger.hide_render=True
for side in ['L','R']:rig.pose.bones['upperarm_'+side].rotation_euler.x=-1.15;rig.pose.bones['lowerarm_'+side].rotation_euler.x=-.8
bpy.context.view_layer.update();snap('robe_max_reach',bpy.data.objects['beauty'])
pose()
for name,key in [('face_neutral',None),('face_attention','Concern'),('face_recognition','Consideration'),('face_consideration','Consideration'),('face_suspicion','Suspicion'),('face_agreement','Agreement'),('face_refusal','Refusal'),('face_controlled_anger','ControlledAnger'),('face_broken_promise','Disapproval'),('face_resolve','Resolve'),('face_blink','Blink')]:
 for k in mesh.data.shape_keys.key_blocks:k.value=0
 if key=='Blink':
  for side in ['L','R']:mesh.data.shape_keys.key_blocks['Blink_'+side].value=1
 elif key:mesh.data.shape_keys.key_blocks[key].value=.65
 snap(name,face)
weights=[];invalid=[]
for v in mesh.data.vertices:
 row=[a.weight for a in v.groups if mesh.vertex_groups[a.group].name in rig.data.bones];weights.append(len(row))
 if not row or abs(sum(row)-1)>1e-5 or any(not math.isfinite(x)or x<0 for x in row):invalid.append(v.index)
report={'source_scene_sha256':hashlib.sha256((source/'AsoYaa.blend').read_bytes()).hexdigest(),'source_glb_sha256':hashlib.sha256((source/'AsoYaa.glb').read_bytes()).hexdigest(),'editable_parts':[o.name for o in s.objects if o.type=='MESH'and o.name not in ['SK_AsoYaa','Ledger_SeparateProp']],'bones':len(rig.data.bones),'vertices':len(mesh.data.vertices),'maximum_influences':max(weights),'invalid_weight_vertices':len(invalid),'measured_frames':len(metrics),'sample_exclusions':[],'contact_samples':metrics,'camera_settings':cameras,'creative':'REVIEW_REQUIRED','contact_acceptance':'REVIEW_REQUIRED; geometric distances do not approve credible anatomy','audio':'INCOMPLETE'}
(out/'source-contact-review.json').write_text(json.dumps(report,indent=2)+'\n');assert not invalid and max(weights)<=4
print('SOURCE_CONTACT_REVIEW',len(metrics),len(invalid),max(weights))
