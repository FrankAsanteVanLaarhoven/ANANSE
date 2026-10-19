"""Bounded editable Aso clearance/return revision; preserves prior source bytes."""
import bpy,json,math,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];old=R/'SourceArt/Characters/AsoYaa/Authored_v018';out=R/'SourceArt/Characters/AsoYaa/Authored_v027';assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(old/'AsoYaa.blend'));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0)
s.frame_set(0);bpy.context.view_layer.update();rest=[(b.name,b.parent.name if b.parent else None,[list(row)for row in b.matrix_local])for b in rig.data.bones];bpy.data.objects.remove(bpy.data.objects['SK_AsoYaa'],do_unlink=True)
changes=[]
leg_weight_changes=[]
for side in ['L','R']:
 obj=bpy.data.objects['Leg_'+side];positions=[tuple(v.co)for v in obj.data.vertices];before=[]
 for v in obj.data.vertices:
  before.append({obj.vertex_groups[g.group].name:g.weight for g in v.groups})
  z=v.co.z
  shin=max(0,min(1,(.57-z)/.17));shin=shin*shin*(3-2*shin)
  foot=max(0,min(1,(.185-z)/(.185-.1037647)));foot=foot*foot*(3-2*foot)
  weights={'thigh_'+side:1-shin,'shin_'+side:shin*(1-foot),'foot_'+side:foot}
  for group in obj.vertex_groups:group.remove([v.index])
  total=sum(weights.values())
  for bone,w in weights.items():
   if w>0:(obj.vertex_groups.get(bone)or obj.vertex_groups.new(name=bone)).add([v.index],w/total,'REPLACE')
 assert positions==[tuple(v.co)for v in obj.data.vertices]
 leg_weight_changes.append({'part':obj.name,'vertices':len(obj.data.vertices),'rest_positions_unchanged':True,'before':before,'reason':'Upper-thigh ring was50%shin and mid-calf50%foot; concentrate blend fields near actual knee/ankle joints, preserving source surface and final contact bones.'})
for name in ['ContinuousTailoredRobe','CreamUnderlayers','RobeWovenEdge-1','RobeWovenEdge1']:
 obj=bpy.data.objects[name];changed=0
 if name=='CreamUnderlayers':
  # Sparse long waist quads bridged across the nonlinear ease profile and
  # crossed the outer robe. Add real editable rings, retaining UVs/weights.
  bpy.ops.object.select_all(action='DESELECT');obj.hide_set(False);obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.subdivide(number_cuts=3,smoothness=0);bpy.ops.object.mode_set(mode='OBJECT')
 for v in obj.data.vertices:
  z=v.co.z;t=max(0,min(1,(1.1-z)/.24));t=t*t*(3-2*t)
  if t<=0:continue
  # Three-dimensional tailoring ease for the evaluated turn/stance envelope.
  # Side and rear clearance matter too; a forward-only offset left flank contacts.
  before=v.co.copy()
  profile=[(.09,.25,.14),(.25,.24,.14),(.50,.22,.13),(.80,.18,.12),(1.02,.163,.116),(1.20,.18,.12),(1.31,.202,.125),(1.37,.17,.095),(1.40,.065,.058)]if name=='CreamUnderlayers'else[(.17,.285,.16),(.30,.275,.155),(.55,.245,.15),(.80,.205,.137),(1.02,.175,.13),(1.20,.19,.133),(1.32,.212,.14),(1.37,.18,.105),(1.40,.070,.065)]
  f=1.68/1.7
  lo=next((i for i in range(len(profile)-1)if profile[i][0]*f<=z<=profile[i+1][0]*f),0 if z<profile[0][0]*f else len(profile)-2);a,b=profile[lo:lo+2];u=max(0,min(1,(z/f-a[0])/(b[0]-a[0])));rx=(a[1]*(1-u)+b[1]*u)*f;ry=(a[2]*(1-u)+b[2]*u)*f;rho=math.hypot(v.co.x/rx,v.co.y/ry)
  if rho>1e-6:
   xn=min(1,abs(v.co.x/rx/rho));flat=math.copysign(ry*max(0,1-xn**4)**.25*rho,v.co.y);v.co.y=(v.co.y*(1-t)+flat*t)*(1+1.7*t)
  waist=max(0,min(1,(z-.78)/.08));waist=waist*waist*(3-2*waist);v.co.x*=1+(.45-.15*waist)*t;
  if name=='CreamUnderlayers':
   v.co.y+=math.copysign(.02*t,v.co.y);v.co.x+=math.copysign(.005*t,v.co.x)
  delta=v.co-before
  if obj.data.shape_keys:
   for key in obj.data.shape_keys.key_blocks:
    if key.name!='Basis':key.data[v.index].co+=delta
  changed+=1
 changes.append({'part':name,'vertices':changed,'radial_ease_scale_xy_max':[1.45,2.7],'upper_waist_width_scale_max':1.3,'weights':'original unchanged'})
# The prior Turn applied its large turn channel to local Z, which is a
# sideways lean for this vertical pelvis bone. Preserve duration and turn
# magnitude as local-Y yaw; gameplay turn rate/root and walk gait are unchanged.
for curve in bpy.data.actions['Turn'].fcurves:
 if curve.data_path=='pose.bones["pelvis"].rotation_euler' and curve.array_index in [1,2]:
  factor=2.2 if curve.array_index==1 else 0
  for key in curve.keyframe_points:
   key.co.y*=factor;key.handle_left.y*=factor;key.handle_right.y*=factor
# The old return keys withdrew the hands while the book moved to a fixed park.
# Keep the actual two-hand contact pose until placement, then withdraw.
action=bpy.data.actions['InspectEvidence']
for curve in action.fcurves:
 value=curve.evaluate(180);end=curve.evaluate(240)
 for i in reversed(range(len(curve.keyframe_points))):
  if curve.keyframe_points[i].co.x>180:curve.keyframe_points.remove(curve.keyframe_points[i],fast=True)
 curve.keyframe_points.insert(204,value);curve.keyframe_points.insert(240,end)
 for key in curve.keyframe_points:
  if key.co.x>=180:key.interpolation='BEZIER';key.handle_left_type='AUTO_CLAMPED';key.handle_right_type='AUTO_CLAMPED'
 action.update_tag()
ledger=bpy.data.objects['Ledger_SeparateProp'];parts=[o for o in s.objects if o.type=='MESH'and o!=ledger];bpy.ops.object.select_all(action='DESELECT');copies=[]
for obj in parts:
 c=obj.copy();c.data=obj.data.copy();s.collection.objects.link(c);c.hide_render=False;c.hide_set(False);c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='SK_AsoYaa'
for obj in parts:obj.hide_render=True;obj.hide_set(True)
for key in mesh.data.shape_keys.key_blocks:key.value=0
assert rest==[(b.name,b.parent.name if b.parent else None,[list(row)for row in b.matrix_local])for b in rig.data.bones]
bpy.ops.wm.save_as_mainfile(filepath=str(out/'AsoYaa.blend'));bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);rig.select_set(True);p=out/'AsoYaa.glb';bpy.ops.export_scene.gltf(filepath=str(p),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
report=json.loads((old/'rig-map.json').read_text());report.update(vertices=len(mesh.data.vertices),source_triangles=sum(len(poly.vertices)-2 for poly in mesh.data.polygons),animation_and_rest_skeleton_unchanged=False,changed_actions=['InspectEvidence','Turn'],underlayer_extra_clearance_m={'depth':.02,'lateral':.005},scene_sha256=hashlib.sha256((out/'AsoYaa.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),correction='Anatomical leg weight fields corrected around actual knee/ankle; original independent garment weights retained with3Drest clearance ease; hold contact through placement at6.8s then withdraw. Native/evaluated clearance pending.',lower_panel_changes=changes,leg_weight_changes=leg_weight_changes,body_rest_geometry_unchanged=True,turn_pose_correction='Local-Y pelvis yaw0.22rad instead of local-Z side lean0.22rad; duration and gameplay root/turn/gait unchanged.',rest_skeleton_unchanged=True,runtime_garment_correction='Clearance_v001 only: keep authored yaw, gravity-aligned lower-panel orientation,4degree authored garment bound before unchanged spring. Body/root/contact/hands untouched. DisableAsoGarmentClearance is diagnostic only.',creative_approved=False);report['ledger']['support']='Table before1.6s; hands1.6..6.8s; table after6.8s. Cancelled presentation returns to supported table with an explicit presentation cut; no physics drop.';(out/'rig-map.json').write_text(json.dumps(report,indent=2)+'\n');print('ASO_CLEARANCE_SOURCE',report['scene_sha256'])
