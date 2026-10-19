"""Saved-scene integrity, full-action pose sampling and held-prop defect measurements."""
import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];out=Path(sys.argv[sys.argv.index('--')+1]);assert not out.exists();result={}
for key,revision,old in [('Kwaku','Authored_v028','Authored_v016'),('OseboLeopard','Authored_v013','Authored_v005')]:
 src=R/'SourceArt/Characters'/key/old/(key+'.blend');bpy.ops.wm.open_mainfile(filepath=str(src));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rest=[(b.name,b.parent.name if b.parent else None,[list(row)for row in b.matrix_local])for b in rig.data.bones];actions=sorted(a.name for a in bpy.data.actions)
 path=src.parent.parent/revision/(key+'.blend');bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');mesh=bpy.data.objects['SK_'+key];assert rest==[(b.name,b.parent.name if b.parent else None,[list(row)for row in b.matrix_local])for b in rig.data.bones];assert actions==sorted(a.name for a in bpy.data.actions);groups={g.index:g.name for g in mesh.vertex_groups};maxinf=0;bad=[]
 for v in mesh.data.vertices:
  weights=[a.weight for a in v.groups if groups[a.group]in rig.data.bones and a.weight>0];maxinf=max(maxinf,len(weights))
  if not weights or any(not math.isfinite(x)or x<0 for x in weights)or abs(sum(weights)-1)>1e-4:bad.append(v.index)
 assert not bad,(key,'weights',bad[:10]);assert maxinf<=4
 samples=[]
 for name in actions:
  rig.animation_data.action=bpy.data.actions[name];a,b=rig.animation_data.action.frame_range;frames=sorted(set([int(a),int(b)]+list(range(int(a),int(b)+1,5))));positions=[]
  for frame in frames:
   s.frame_set(frame);bpy.context.view_layer.update();ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();assert all(math.isfinite(c)for v in m.vertices for c in v.co);positions.append([list((rig.matrix_world@p.head))for p in rig.pose.bones]);ev.to_mesh_clear()
  displacement=max(math.dist(x,y)for pose in positions for x,y in zip(positions[0],pose));assert displacement>1e-5,(key,name);samples.append({'action':name,'sampled_frames':frames,'max_joint_displacement_m':displacement})
 contact=None
 if key=='Kwaku':
  rig.animation_data.action=bpy.data.actions['InspectLedger'];prop=bpy.data.objects['Ledger_SeparateProp'];contact={'socket':'socket_ledger -> hand_R','bone':'hand_R','surface':'Actual saved Ledger_SeparateProp evaluated triangles','visible_runtime_frames':list(range(23,81,3)),'excluded_not_visible_frames':[1,4,7,10,13,16,19,22,81,82],'per_part':{}}
  for frame in contact['visible_runtime_frames']:
   s.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();pe=prop.evaluated_get(deps);pm=pe.to_mesh();tree=BVHTree.FromPolygons([pe.matrix_world@v.co for v in pm.vertices],[list(p.vertices)for p in pm.polygons]);pe.to_mesh_clear();ev=mesh.evaluated_get(deps);m=ev.to_mesh()
   for side in ['L','R']:
    for digit in ['palm',0,1,2,3,4]:
     names={'hand_'+side}if digit=='palm'else{f'digit_{side}_{digit}_01',f'digit_{side}_{digit}_02'};ids={g.index for g in mesh.vertex_groups if g.name in names};values=[]
     for v in mesh.data.vertices:
      if any(a.group in ids and a.weight>.5 for a in v.groups):
       p=ev.matrix_world@m.vertices[v.index].co;hit=tree.find_nearest(p)
       if hit:values.append(hit[3]*100)
     if values:contact['per_part'].setdefault(side+'_'+str(digit),[]).append({'frame':frame,'minimum_distance_cm':min(values),'median_distance_cm':sorted(values)[len(values)//2],'sampled_vertices':len(values)})
   ev.to_mesh_clear()
  contact['acceptance']='REVIEW_REQUIRED';contact['limitations']=['Distance distribution does not establish a natural grasp or exclude palm penetration','Pickup/release visibility uses runtime timing; source-held samples are separate','Grip shape and full blend/native cinematic review remain required']
 keys=mesh.data.shape_keys.key_blocks;morphs={k.name:sum((a.co-b.co).length>1e-8 for a,b in zip(k.data,keys['Basis'].data))for k in keys if k.name!='Basis'};assert all(v>0 for v in morphs.values())
 result[key]={'scene':str(path.relative_to(R)),'scene_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rest_bones_unchanged':True,'bones':len(rest),'vertices':len(mesh.data.vertices),'max_influences':maxinf,'bad_weight_vertices':len(bad),'actions':samples,'morph_nonzero_vertices':morphs,'prop_review':contact,'creative_approved':False,'speech_shapes_complete':False}
out.write_text(json.dumps(result,indent=2)+'\n');print('VISUAL_SOURCE_CHECKS_PASSED',[(k,v['vertices'],len(v['actions']))for k,v in result.items()])
