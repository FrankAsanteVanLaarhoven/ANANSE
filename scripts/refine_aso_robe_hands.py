"""One versioned robe/hand art refinement; retain v027 geometry/weights as rollback."""
import bpy,json,math,hashlib,struct,bisect
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1];old=R/'SourceArt/Characters/AsoYaa/Authored_v027';out=R/'SourceArt/Characters/AsoYaa/Authored_v028';assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(old/'AsoYaa.blend'));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');rig.animation_data.action=None
for b in rig.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0)
s.frame_set(0);bpy.context.view_layer.update();rest=[(b.name,b.parent.name if b.parent else None,[list(r)for r in b.matrix_local])for b in rig.data.bones];bpy.data.objects.remove(bpy.data.objects['SK_AsoYaa'],do_unlink=True)
parts=[o for o in s.objects if o.type=='MESH'and o.name!='Ledger_SeparateProp'];before_counts=(sum(len(o.data.vertices)for o in parts),sum(len(p.vertices)-2 for o in parts for p in o.data.polygons));before_materials={m.name for o in parts for m in o.data.materials};leg_state={o.name:[(tuple(v.co),[(g.group,g.weight)for g in v.groups])for v in o.data.vertices]for o in parts if o.name in ['Leg_L','Leg_R']}
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def interp(points,z):
 i=max(0,min(len(points)-2,bisect.bisect_right([p[0]for p in points],z)-1));a,b=points[i:i+2];t=max(0,min(1,(z-a[0])/(b[0]-a[0])));result=[]
 for k in range(1,len(a)):
  m0=(b[k]-points[max(0,i-1)][k])/(b[0]-points[max(0,i-1)][0]);m1=(points[min(len(points)-1,i+2)][k]-a[k])/(points[min(len(points)-1,i+2)][0]-a[0]);d=b[0]-a[0];v=(2*t**3-3*t*t+1)*a[k]+(t**3-2*t*t+t)*d*m0+(-2*t**3+3*t*t)*b[k]+(t**3-t*t)*d*m1;result.append(max(min(a[k],b[k]),min(max(a[k],b[k]),v)))
 return result
# Measured v027 final-pose knee reaches30cm forward; retain targeted front ease,
# redistribute rear/hem volume rather than globally scaling the garment.
target=[(.08,.285,.275,.235),(.17,.295,.285,.24),(.30,.30,.335,.26),(.48,.305,.36,.265),(.62,.30,.325,.245),(.80,.275,.28,.215),(1.00,.225,.215,.175),(1.13,.205,.18,.14),(1.26,.20,.15,.12)]
references={}
for name in ['ContinuousTailoredRobe','CreamUnderlayers']:
 o=bpy.data.objects[name];bands={}
 for v in o.data.vertices:
  if v.co.z>1.27:continue
  if any('upperarm'in o.vertex_groups[g.group].name and g.weight>.05 for g in v.groups):continue
  band=round(v.co.z/.012);r=bands.setdefault(band,[0,0,0]);r[0]=max(r[0],abs(v.co.x));r[1]=max(r[1],-v.co.y);r[2]=max(r[2],v.co.y)
 references[name]=[(k*.012,*r)for k,r in sorted(bands.items())if min(r)>.02]
changes=[]
for name in ['ContinuousTailoredRobe','CreamUnderlayers','RobeWovenEdge-1','RobeWovenEdge1']:
 o=bpy.data.objects[name];inside=name=='CreamUnderlayers';ref=references['CreamUnderlayers'if inside else'ContinuousTailoredRobe'];changed=0;max_move=0
 for v in o.data.vertices:
  z=v.co.z
  if z>1.26 or any('upperarm'in o.vertex_groups[g.group].name and g.weight>.05 for g in v.groups):continue
  oldp=v.co.copy();rx,front,back=interp(ref,z);nx=v.co.x/max(rx,.01);ny=v.co.y/max(front if v.co.y<0 else back,.01);theta=math.atan2(ny,nx);rho=(abs(nx)**4+abs(ny)**4)**.25;side,fore,aft=interp(target,z)
  if inside:side-=.014;fore-=.012;aft-=.012
  power=3.5 if z<.80 else 3.0;cx=math.copysign(abs(math.cos(theta))**(2/power),math.cos(theta));cy=math.copysign(abs(math.sin(theta))**(2/power),math.sin(theta));fold=.004+.008*(1-smooth((z-.22)/.9));ridge=(.5+.5*math.cos(theta*8+.18*math.sin(theta*3)))**5;ease=fold*ridge
  new=Vector(((side+ease)*cx*rho,((fore if cy<0 else aft)+ease)*cy*rho,z));blend=1-smooth((z-1.10)/.16);v.co=oldp.lerp(new,blend)
  hem=smooth((.23-z)/.08);v.co.z+=hem*.004*math.sin(theta*8+.2)
  delta=v.co-oldp
  if o.data.shape_keys:
   for key in o.data.shape_keys.key_blocks:
    if key.name!='Basis':key.data[v.index].co+=delta
  changed+=1;max_move=max(max_move,delta.length)
 changes.append({'part':name,'changed_vertices':changed,'maximum_rest_displacement_m':max_move,'construction':'height-varying asymmetric front/rear loft and shallow longitudinal folds; same editable topology/UVs/weights','hidden_construction':'PROPOSED; not reference-established'})
# Use the actual protected final evaluated grip only as an authoring clearance
# reference. Future full-cycle native checks remain independent requirements.
F=R/'.local/verification/aso-motion-correction-20261018/packaged-evaluated-clearance/surfaces';meta_path=next(p for p in F.glob('*InspectEvidence*.json')if 3<float(json.loads(p.read_text())['evaluated_time'])<3.3);meta=json.loads(meta_path.read_text());raw=meta_path.with_suffix('.bin').read_bytes();pairs=list(struct.iter_unpack('<6f',raw[4:]));kd=KDTree(len(pairs))
for i,p in enumerate(pairs):kd.insert(Vector(p[:3]),i)
kd.balance();book=meta['LedgerPresentation'];origin=Vector(book['translation']);lo=Vector(book['bounds_min']);hi=Vector(book['bounds_max']);matrices={n:Matrix(rows).transposed()for n,flat in meta['final_ref_to_local_skin_matrices_row_major'].items()for rows in [[flat[k:k+4]for k in range(0,16,4)]]}
def native(v):return Vector((-100*v.y,-100*v.x,100*v.z))
def source(v):return Vector((-v.y/100,-v.x/100,v.z/100))
anchors=[Vector(p)for p in [(4.658439755,28.029343486,86.241745949),(3.766359761,26.566737890,81.295883656),(4.088330641,27.719998360,80.498969555),(4.658439755,-28.029343486,86.241745949),(3.766359761,-26.566737890,81.295883656),(4.088330641,-27.719998360,80.498969555)]]
hand_changes=[]
for o in parts:
 if not(o.name.startswith('Palm_')or o.name.startswith('ArticulatedDigit_')or o.name.startswith('ArticulatedThumb_')):continue
 bounds=[(min(v.co[k]for v in o.data.vertices),max(v.co[k]for v in o.data.vertices))for k in range(3)];cx=sum(bounds[0])/2;cy=sum(bounds[1])/2;zlo,zhi=bounds[2];maxmove=0;protected=0
 for v in o.data.vertices:
  original=v.co.copy();nr=native(original);near,i,error=kd.find(nr);assert error<.01,(o.name,error);posed=Vector(pairs[i][3:]);u=max(0,min(1,(zhi-original.z)/max(.001,zhi-zlo)));weighted=Matrix(((0,0,0),(0,0,0),(0,0,0)));total=0
  for g in v.groups:
   w=g.weight;n=o.vertex_groups[g.group].name
   if w>0:weighted+=matrices[n].to_3x3()*w;total+=w
  assert total>.99
  protect=smooth(min((nr-a).length for a in anchors)/.8);protected+=protect<.001
  wrist=smooth(u/.2);delta=Vector((0,0,0))
  if o.name.startswith('Palm_'):
   delta.x=-(original.x-cx)*.12*math.sin(math.pi*u)*wrist
   # Add dorsal volume away from the book, preserving the palmar contact surface.
   away=smooth((origin.z+lo.z-posed.z)/1.8);delta+=source(weighted.inverted()@Vector((0,0,-.55*away*math.sin(math.pi*u)*wrist)))
  else:
   taper=.86+.10*math.exp(-((u-.5)/.17)**2)-.06*u**3;delta.x=(original.x-cx)*(taper-1)*wrist;delta.y=(original.y-cy)*(.04*math.exp(-((u-.5)/.16)**2)-.08*u*u)*wrist;curl=.40*u*u*wrist
   if o.name.startswith('ArticulatedThumb_'):curl=-.22*math.sin(math.pi*u)
   delta+=source(weighted.inverted()@Vector((0,0,-curl)))
  delta*=protect;candidate=posed+weighted@native(delta);local=candidate-origin
  if all(lo[k]-.02<local[k]<hi[k]+.02 for k in range(3)):
   # Keep authored surface outside the conservative protected book bound.
   axis=min(range(3),key=lambda k:min(abs(local[k]-lo[k]),abs(local[k]-hi[k])));safe=lo[axis]-.025 if abs(local[axis]-lo[axis])<abs(local[axis]-hi[axis])else hi[axis]+.025;correction=Vector((0,0,0));correction[axis]=safe-local[axis];delta+=source(weighted.inverted()@correction)
  v.co+=delta;maxmove=max(maxmove,delta.length)
 hand_changes.append({'part':o.name,'maximum_rest_displacement_m':maxmove,'protected_contact_anchor_vertices':protected,'changes':'narrower separated/tapered fingers, rounded knuckles, cupped dorsal palm and thumb pad; wrist roots and six prior support anchors retained','reference':'one recorded v027 final held pose; not a new all-frame penetration result'})
assert leg_state=={o.name:[(tuple(v.co),[(g.group,g.weight)for g in v.groups])for v in o.data.vertices]for o in parts if o.name in ['Leg_L','Leg_R']};assert rest==[(b.name,b.parent.name if b.parent else None,[list(r)for r in b.matrix_local])for b in rig.data.bones]
assert before_counts==(sum(len(o.data.vertices)for o in parts),sum(len(p.vertices)-2 for o in parts for p in o.data.polygons));assert before_materials=={m.name for o in parts for m in o.data.materials}
ledger=bpy.data.objects['Ledger_SeparateProp'];bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in parts:
 c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.hide_render=False;c.hide_set(False);c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='SK_AsoYaa'
for o in parts:o.hide_render=True;o.hide_set(True)
for key in mesh.data.shape_keys.key_blocks:key.value=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'AsoYaa.blend'));bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);rig.select_set(True);p=out/'AsoYaa.glb';bpy.ops.export_scene.gltf(filepath=str(p),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
report=json.loads((old/'rig-map.json').read_text());report.update(scene_sha256=hashlib.sha256((out/'AsoYaa.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),art_revision='Authored_v028',previous_corrected_revision='Authored_v027',robe_art_changes=changes,hand_art_changes=hand_changes,triangles_and_materials_unchanged=True,animation_clips_and_timings_unchanged=True,leg_geometry_and_weights_unchanged=True,rest_skeleton_unchanged=True,creative_approved=False,correction='One robe-drape and hand-shape art refinement; new final-pose validation pending. Previous correction history retained.');(out/'rig-map.json').write_text(json.dumps(report,indent=2)+'\n');print('ASO_ART_SOURCE',report['scene_sha256'],before_counts)
