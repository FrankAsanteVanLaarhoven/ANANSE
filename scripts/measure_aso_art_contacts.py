"""Actual final hand triangles against recorded native ledger render triangles."""
import json,struct,os
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
folder=Path(os.environ['ASO_SURFACES']);labels=json.loads((folder/'vertex-part-map.json').read_text())['parts'];geometry=json.loads((folder/'ledger-static-geometry.json').read_text());assert geometry['mesh']=='/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/Props/Ledger.Ledger';indices=[x[0]for x in struct.iter_unpack('<I',(folder/'indices.bin').read_bytes())];hand=lambda n:n.startswith(('Palm_','ArticulatedDigit_','ArticulatedThumb_'));faces=[tuple(indices[k:k+3])for k in range(0,len(indices),3)if all(hand(labels[j])for j in indices[k:k+3])];ids=sorted({j for f in faces for j in f});bf=[tuple(geometry['indices'][i:i+3])for i in range(0,len(geometry['indices']),3)];rows=[]
# Verify closed convex components using welded native positions, not a box proxy.
weld={};vertex_id=[]
for v in geometry['vertices']:
 key=tuple(round(x,5)for x in v);vertex_id.append(weld.setdefault(key,len(weld)))
adj={i:set()for i in range(len(bf))};owners={}
for i,t in enumerate(bf):
 for j in t:
  for other in owners.get(vertex_id[j],[]):adj[i].add(other);adj[other].add(i)
  owners.setdefault(vertex_id[j],[]).append(i)
remaining=set(adj);components=[]
while remaining:
 todo=[remaining.pop()];part=[]
 while todo:
  i=todo.pop();part.append(i)
  for j in adj[i]&remaining:remaining.remove(j);todo.append(j)
 edges={}
 for i in part:
  t=[vertex_id[j]for j in bf[i]]
  for a,c in zip(t,t[1:]+t[:1]):edge=tuple(sorted((a,c)));edges[edge]=edges.get(edge,0)+1
 assert all(n==2 for n in edges.values()),'Ledger component is not closed'
 components.append(part)
for meta in sorted(folder.glob('*.json')):
 if not meta.with_suffix('.bin').exists():continue
 d=json.loads(meta.read_text())
 if 'InspectEvidence'not in d['clip']:continue
 prop=d['LedgerPresentation'];assert prop['visible'];raw=meta.with_suffix('.bin').read_bytes();points=[Vector(v[3:])for v in struct.iter_unpack('<6f',raw[4:])];q=prop['quaternion_xyzw'];rotation=Quaternion((q[3],q[0],q[1],q[2]));origin=Vector(prop['translation']);scale=prop['scale'];bp=[origin+rotation@Vector(tuple(v[k]*scale[k]for k in range(3)))for v in geometry['vertices']];a=BVHTree.FromPolygons(points,faces,all_triangles=True);b=BVHTree.FromPolygons(bp,bf,all_triangles=True);overlap=a.overlap(b);inside=[];minimum=1e9
 planes=[]
 for component in components:
  vids={j for i in component for j in bf[i]};centre=sum((bp[j]for j in vids),Vector())/len(vids);partplanes=[]
  for i in component:
   v0,v1,v2=[bp[j]for j in bf[i]];normal=(v1-v0).cross(v2-v0).normalized()
   if normal.dot(centre-v0)>0:normal=-normal
   assert all(normal.dot(bp[j]-v0)<=.0001 for j in vids),'Ledger component is not convex'
   partplanes.append((v0,normal))
  assert all(normal.dot(centre-v0)<-.0001 for v0,normal in partplanes),'Degenerate ledger component fails inside self-check'
  assert not all(normal.dot(centre+Vector((1000,1000,1000))-v0)<-.0001 for v0,normal in partplanes),'Outside self-check failed'
  planes.append(partplanes)
 for j in ids:
  p=points[j];nearest=b.find_nearest(p);distance=nearest[3];minimum=min(minimum,distance)
  if any(all(normal.dot(p-v0)<-.0001 for v0,normal in part)for part in planes):inside.append(j)
 rows.append({'pose':meta.stem,'clip':d['clip'],'evaluated_time':d['evaluated_time'],'intended_support':d['intended_support'],'triangle_intersection_pairs':len(overlap),'inside_hand_vertices':len(inside),'minimum_unsigned_hand_ledger_surface_gap_cm':minimum})
assert rows
result={'status':'FAIL'if any(r['triangle_intersection_pairs']or r['inside_hand_vertices']for r in rows)else'assertions_passed','samples':len(rows),'hand_vertices':len(ids),'hand_triangles':len(faces),'ledger_vertices':len(geometry['vertices']),'ledger_triangles':len(bf),'verified_closed_convex_components':len(components),'containment_positive_negative_self_checks':2*len(components),'ledger_mesh':geometry['mesh'],'maximum_triangle_intersection_pairs':max(r['triangle_intersection_pairs']for r in rows),'maximum_inside_vertices':max(r['inside_hand_vertices']for r in rows),'minimum_unsigned_surface_gap_cm':min(r['minimum_unsigned_hand_ledger_surface_gap_cm']for r in rows),'coverage':'All mapped palm/digit/thumb final LOD0 vertices/triangles vs exact recorded native static ledger triangles, including reach/hold/placement/withdrawal4Hz snapshots. BVH triangle overlaps plus exact triangle-derived convex halfspaces after verifying each welded ledger component is closed and convex. Numerical boundary exclusion0.0001cm; intersections still required zero. Not an all-frame/all-LOD or natural-grip certificate.','samples_detail':rows};(folder/'hand-ledger-triangles.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items()if k!='samples_detail'});assert result['status']=='assertions_passed',result['status']
