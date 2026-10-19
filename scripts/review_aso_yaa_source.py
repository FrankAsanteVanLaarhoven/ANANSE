"""Measured source validation and model-derived review views; no creative approval."""
import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];source=R/'SourceArt/Characters/AsoYaa/Authored_v007';out=R/'.local/verification/aso-yaa-20261016/source-review-02';out.mkdir(exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(source/'AsoYaa.blend'));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');mesh=bpy.data.objects['SK_AsoYaa'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
weights=[];bad=[]
for v in mesh.data.vertices:
 row=[g.weight for g in v.groups if mesh.vertex_groups[g.group].name in rig.data.bones];weights.append(len(row))
 if not row or any(not math.isfinite(x)or x<0 for x in row)or abs(sum(row)-1)>.00001:bad.append(v.index)
assert not bad,bad[:10]
assert max(weights)<=4
motions={}
for a in bpy.data.actions:
 channels=[(c.data_path,c.array_index,[(round(k.co.x,5),round(k.co.y,7))for k in c.keyframe_points])for c in a.fcurves];motions[a.name]=hashlib.sha256(json.dumps(channels).encode()).hexdigest()
assert len(motions)==16 and len(set(motions.values()))==16
assert len(rig.data.bones)==48
sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g
cameras={}
def capture(name,camera,action=None,frame=0):
 rig.animation_data.action=bpy.data.actions[action]if action else None;s.frame_set(frame);s.camera=camera;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);cameras[name]={'camera_matrix':[list(row)for row in camera.matrix_world],'type':camera.data.type,'ortho_scale':camera.data.ortho_scale,'lens_mm':camera.data.lens,'exposure_stops':s.view_settings.exposure,'display_look':s.view_settings.look,'action':action,'frame':frame}
def cam(name,loc,target,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;g.aim(o,target);return o
for name in ['front','left','right','back','beauty']:capture(name+'_solid',bpy.data.objects[name])
face=cam('FaceReview',(0,-4,1.59),(0,0,1.59),.42);capture('face_closeup',face)
hands=cam('HandReview',(0,-3,.90),(0,0,.90),.86);capture('hands_sheet',hands)
capture('robe_neutral',bpy.data.objects['beauty']);capture('robe_extreme_pose',bpy.data.objects['beauty'],'NegotiateOpen',45)
for name,action in [('negotiation_pose','NegotiateFirm'),('ledger_interaction','InspectEvidence'),('agreement_pose','Agreement'),('refusal_pose','Refusal')]:capture(name,bpy.data.objects['beauty'],action,45)
# Actual joined mesh topology rendered through a wireframe modifier.
wire=mesh.modifiers.new('ActualTopology','WIREFRAME');wire.thickness=.0007;wire.use_replace=True
capture('topology_front',bpy.data.objects['front']);capture('topology_side',bpy.data.objects['left']);mesh.modifiers.remove(wire)
# Render real rest-bone endpoints as a separate technical overlay using saved hierarchy.
rig.animation_data.action=None;s.frame_set(0)
mat=g.material('RigInspection',(.8,.1,.04));g.scene=s
for b in rig.data.bones:
 o=g.tube('ActualBone_'+b.name,[rig.matrix_world@b.head_local,rig.matrix_world@b.tail_local],[.002,.001],mat,segments=6)
mesh.hide_render=True;capture('skeleton_overlay',bpy.data.objects['front']);mesh.hide_render=False
for o in list(s.objects):
 if o.name.startswith('ActualBone_'):bpy.data.objects.remove(o,do_unlink=True)
turn=cam('Turntable',(0,-5,.87),(0,0,.87),2.35)
for i in range(24):
 a=math.tau*i/24;turn.location=(5*math.sin(a),-5*math.cos(a),.87);g.aim(turn,(0,0,.87));capture('turn_%03d'%i,turn)
report={'source_scene':str(source/'AsoYaa.blend'),'source_scene_sha256':sha(source/'AsoYaa.blend'),'glb_sha256':sha(source/'AsoYaa.glb'),'vertices':len(mesh.data.vertices),'bone_count':48,'maximum_influences':max(weights),'invalid_weight_vertices':len(bad),'motion_curve_hashes':motions,'morph_targets':[k.name for k in mesh.data.shape_keys.key_blocks],'cameras':cameras,'creative':'REVIEW_REQUIRED','prop_contact':'REVIEW_REQUIRED','note':'InspectEvidence pose has no verified held ledger; image is a pose review, not contact acceptance'}
(out/'source-review.json').write_text(json.dumps(report,indent=2)+'\n');print('SOURCE_CHECKS_PASSED',len(motions),max(weights),len(bad))
