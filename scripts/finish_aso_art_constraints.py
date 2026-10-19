"""Local technical repairs within the one art pass; preserve rejected v028."""
import bpy,json,math,hashlib,struct
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];old=R/'SourceArt/Characters/AsoYaa/Authored_v027';prior=R/'SourceArt/Characters/AsoYaa/Authored_v028';out=R/'SourceArt/Characters/AsoYaa/Authored_v030';assert not out.exists()or not any(out.iterdir());out.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(old/'AsoYaa.blend'));original={o.name:[v.co.copy()for v in o.data.vertices]for o in bpy.context.scene.objects if o.type=='MESH'and o.name in ['ContinuousTailoredRobe','CreamUnderlayers','RobeWovenEdge-1','RobeWovenEdge1']};bpy.ops.wm.open_mainfile(filepath=str(prior/'AsoYaa.blend'));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0)
s.frame_set(0);bpy.data.objects.remove(bpy.data.objects['SK_AsoYaa'],do_unlink=True)
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
repairs=[]
for name,coords in original.items():
 o=bpy.data.objects[name];n=0
 for v,ref in zip(o.data.vertices,coords):
  # Native failures are localized to front/lateral cloth at restZ55..73cm.
  alpha=.87*smooth((v.co.z-.14)/.40)*(1-smooth((v.co.z-.78)/.42))*smooth((-ref.y-.02)/.10)
  if not alpha:continue
  delta=(ref-v.co)*alpha;delta.z=0;v.co+=delta;n+=1
 repairs.append({'part':name,'vertices':n,'method':'Restore only evidenced front knee-band ease toward protected v027, maximum87%; rear, hem and waist refinement retained','coverage_basis':'Native failures localized to front restZ55..73cm; smooth broad transition avoids an abrupt localized shelf, retaining same core ease; no region excluded'})
# Retain all original clips/timing except staged approach/withdrawal of the lab ledger.
module=(R/'scripts/correct_aso_yaa_contact.py').read_text();defs=module[module.index('def frame_matrix'):module.index('# New contact performance')];exec(defs,globals());action=bpy.data.actions['InspectEvidence'];rig.animation_data.action=action
rest_rotation={side:rig.data.bones['hand_'+side].matrix_local.to_quaternion()for side in ['L','R']};finger_contact={}
s.frame_set(48);bpy.context.view_layer.update()
for b in rig.pose.bones:
 if b.name.startswith('digit_'):finger_contact[b.name]=(b.rotation_euler.copy(),b.location.copy())
# The previous .8s wrist target was inside the book approach corridor. Route
# from the sides and below the fixed receiving plane; preserve contact at1.6,
# placement6.8, end8s and the whole held phase.
knots=[(0,.287,-.03,.925),(18,.245,-.24,.91),(30,.22,-.30,.94),(42,.178,-.30,.965),(48,.178,-.30,1.004),(204,.178,-.30,1.004),(216,.22,-.30,.94),(228,.245,-.24,.91),(240,.287,-.03,.925)]
def target(frame):
 i=next((i for i in range(len(knots)-1)if knots[i][0]<=frame<=knots[i+1][0]),len(knots)-2);a,b=knots[i:i+2];t=smooth((frame-a[0])/(b[0]-a[0]));return Vector(tuple(a[k]+(b[k]-a[k])*t for k in range(1,4)))
for frame in list(range(0,48))+list(range(205,241)):
 s.frame_set(frame);bpy.context.view_layer.update();w=target(frame)
 for side,sign in [('L',-1),('R',1)]:
  arm(side,Vector((sign*w.x,w.y,w.z)),Vector((-sign,0,0)))
  blend=smooth(frame/18)if frame<48 else 1-smooth((frame-228)/12);hand=rig.pose.bones['hand_'+side];q=rest_rotation[side].slerp(hand.matrix.to_quaternion(),blend);hand.matrix=Matrix.LocRotScale(hand.head.copy(),q,Vector((1,1,1)));bpy.context.view_layer.update()
  for name in ['upperarm_'+side,'lowerarm_'+side,'hand_'+side]:
   bone=rig.pose.bones[name];bone.keyframe_insert('rotation_euler',frame=frame);bone.keyframe_insert('location',frame=frame)
 for name,(rotation,location)in finger_contact.items():
  b=rig.pose.bones[name];b.rotation_euler=tuple(v*blend for v in rotation);b.location=location*blend;b.keyframe_insert('rotation_euler',frame=frame);b.keyframe_insert('location',frame=frame)
for curve in action.fcurves:
 if any(n in curve.data_path for n in ['upperarm_','lowerarm_','hand_','digit_']):
  for key in curve.keyframe_points:
   if key.co.x<48 or key.co.x>204:key.interpolation='LINEAR'
rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0)
s.frame_set(0);ledger=bpy.data.objects['Ledger_SeparateProp'];parts=[o for o in s.objects if o.type=='MESH'and o!=ledger];bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in parts:
 c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.hide_render=False;c.hide_set(False);c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='SK_AsoYaa'
for o in parts:o.hide_render=True;o.hide_set(True)
for key in mesh.data.shape_keys.key_blocks:key.value=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'AsoYaa.blend'))
def export(path,animations,mode):
 bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_animations=animations,export_animation_mode=mode,export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True);raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);d['asset'].pop('generator',None)
 if animations:assert len(d.get('animations',[]))==1;d['animations'][0]['name']='InspectEvidence'
 data=json.dumps(d,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
export(out/'AsoYaa.glb',False,'ACTIONS');rig.animation_data.action=action;export(out/'InspectEvidence.glb',True,'ACTIVE_ACTIONS');report=json.loads((prior/'rig-map.json').read_text());report.update(art_revision='Authored_v030',source_trial='Authored_v028 retained rejected native overlap coverage',scene_sha256=hashlib.sha256((out/'AsoYaa.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/'AsoYaa.glb').read_bytes()).hexdigest(),ledger_clip_glb_sha256=hashlib.sha256((out/'InspectEvidence.glb').read_bytes()).hexdigest(),localized_clearance_repairs=repairs,animation_clips_and_timings_unchanged=False,changed_actions=['InspectEvidence'],ledger_timing='Unchanged8seconds: table<1.6; hands1.6..6.8; table>=6.8. New staged approach/withdrawal only; held phase unchanged.',runtime_garment_correction='ArtRefine_v002 uses the same v027 gravity/yaw and4degree authored bound before existing spring; old baseline unchanged',creative_approved=False);(out/'rig-map.json').write_text(json.dumps(report,indent=2)+'\n');print('ASO_ART_CONSTRAINT_SOURCE',report['scene_sha256'])
