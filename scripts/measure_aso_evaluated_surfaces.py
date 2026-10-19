"""Read-only native evaluated-surface overlap measurements with disclosed coverage."""
import bpy,json,struct,sys,os
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[1];root=r/'.local/verification/aso-motion-correction-20261018';folder=Path(os.environ['ASO_SURFACES']);bpy.ops.wm.open_mainfile(filepath=str(r/'SourceArt/Characters/AsoYaa'/os.environ.get('ASO_SOURCE','Authored_v018')/'AsoYaa.blend'))
points=[]
for obj in bpy.context.scene.objects:
 if obj.type!='MESH' or obj.name in ['SK_AsoYaa','Ledger_SeparateProp']:continue
 for v in obj.data.vertices:
  p=obj.matrix_world@v.co;points.append((Vector((-100*p.y,-100*p.x,100*p.z)),obj.name))
kd=KDTree(len(points))
for i,(p,name) in enumerate(points):kd.insert(p,i)
kd.balance();files=sorted(folder.glob('*.bin'));files=[p for p in files if p.name!='indices.bin'and p.with_suffix('.json').exists()];indices=[x[0]for x in struct.iter_unpack('<I',(folder/'indices.bin').read_bytes())];rows=[]
for file in files:
 raw=file.read_bytes();n=struct.unpack_from('<I',raw)[0];pairs=list(struct.iter_unpack('<6f',raw[4:]));rest=[Vector(p[:3])for p in pairs];final=[Vector(p[3:])for p in pairs]
 if not rows:
  labels=[];errors=[]
  for p in rest:
   co,i,dist=kd.find(p);labels.append(points[i][1]);errors.append(dist)
  (folder/'vertex-part-map.json').write_text(json.dumps({'parts':labels,'maximum_rest_correspondence_error_cm':max(errors),'vertices':n,'mapping':'Nearest exact source part vertex after qualified native handedness/centimetre conversion; duplicate imported seam vertices retain part identity.'}))
 lower={i for i,p in enumerate(rest)if .18*100<p.z<.90*100}
 leg=[tuple(indices[i:i+3])for i in range(0,len(indices),3)if all(labels[j]in ['Leg_L','Leg_R'] and j in lower for j in indices[i:i+3])]
 cloth=[tuple(indices[i:i+3])for i in range(0,len(indices),3)if all(labels[j] in ['ContinuousTailoredRobe','CreamUnderlayers','RobeWovenEdge-1','RobeWovenEdge1']and 16<rest[j].z<110 for j in indices[i:i+3])]
 a=BVHTree.FromPolygons(final,leg,all_triangles=True);b=BVHTree.FromPolygons(final,cloth,all_triangles=True);hits=a.overlap(b)
 ids=set(j for t in leg for j in t);minnear=min((b.find_nearest(final[i])[3]for i in ids),default=None)
 meta=json.loads(file.with_suffix('.json').read_text());support={}
 book=meta.get('LedgerPresentation');stand=meta.get('AsoLedgerSupport')
 if book:
  q=book['quaternion_xyzw'];quat=Quaternion((q[3],q[0],q[1],q[2]));origin=Vector(book['translation']);scale=Vector(book['scale']);low=Vector(book['bounds_min']);high=Vector(book['bounds_max'])
  def book_distance(point):
   p=quat.inverted()@(point-origin);p=Vector(tuple(p[i]/scale[i]for i in range(3)));delta=Vector(tuple(max(low[i]-p[i],0,p[i]-high[i])for i in range(3)));return delta.length
  support={'visible':book['visible'],'intended_support':meta.get('intended_support'),'nearest_hand_surface_vertex_cm':{side:min((book_distance(final[i])for i,label in enumerate(labels)if label=='Palm_'+side or label.startswith('ArticulatedDigit_'+side)or label=='ArticulatedThumb_'+side),default=None)for side in ['L','R']}}
  if stand:
   sq=stand['quaternion_xyzw'];rotation=Quaternion((sq[3],sq[0],sq[1],sq[2]));so=Vector(stand['translation']);ss=Vector(stand['scale']);sl=Vector(stand['bounds_min']);sh=Vector(stand['bounds_max']);bc=[origin+quat@Vector(tuple(v[i]*scale[i]for i in range(3)))for v in [Vector((x,y,z))for x in [low.x,high.x]for y in [low.y,high.y]for z in [low.z,high.z]]];sc=[so+rotation@Vector(tuple(v[i]*ss[i]for i in range(3)))for v in [Vector((x,y,z))for x in [sl.x,sh.x]for y in [sl.y,sh.y]for z in [sl.z,sh.z]]];support.update(table_visible=stand['visible'],ledger_underside_to_table_top_cm=min(v.z for v in bc)-max(v.z for v in sc),table_bounds_overlap_xy=all(min(v[i]for v in bc)>=min(v[i]for v in sc)-.01 and max(v[i]for v in bc)<=max(v[i]for v in sc)+.01 for i in [0,1]))
 rows.append({'file':file.name,'support':support,'clip':meta['clip'],'seconds':meta['evaluated_time'],'predicted_render_lod':meta.get('predicted_render_lod'),'secondary_disabled':meta['secondary_disabled'],'body_triangles':len(leg),'garment_triangles':len(cloth),'triangle_intersection_pairs':len(hits),'intersections_by_garment':{name:sum(labels[cloth[b][0]]==name for a,b in hits)for name in ['ContinuousTailoredRobe','CreamUnderlayers','RobeWovenEdge-1','RobeWovenEdge1']},'intersected_body_z_range_cm':[min((final[j].z for a,b in hits for j in leg[a]),default=0),max((final[j].z for a,b in hits for j in leg[a]),default=0)],'minimum_unsigned_surface_distance_cm':minnear,'max_leg_front_cm':max(final[i].x for i in ids),'maximum_source_mapping_error_cm':max(errors)})
(folder/'clearance-final.json').write_text(json.dumps({'coverage':'Native LOD0 skin after final contact+secondary evaluation; body leg rest Z18..90cm, robe/underlayer rest Z16..110cm; excludes feet, upper torso and morph-only facial surfaces. Triangle intersection pairs are geometric intersection tests, unsigned distances are not signed clearance. No omitted captured samples.','samples':rows},indent=2))
print('EVALUATED_SURFACES',len(rows),'max_pairs',max(x['triangle_intersection_pairs']for x in rows),'max_rest_error_cm',max(errors))
