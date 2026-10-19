"""Use true aperture boundary connectivity; angle sorting can cross a triangulated rim."""
import bpy,json,math,hashlib,struct,shutil,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];src=R/'SourceArt/Characters/OseboLeopard/Authored_v017';out=src.parent/'Authored_v019';assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(src/'OseboLeopard.blend'));s=bpy.context.scene;old=bpy.data.objects['SK_OseboLeopard'];m=old.data;rig=next(o for o in s.objects if o.type=='ARMATURE');rig.animation_data.action=None;s.frame_set(0);names={g.index:g.name for g in old.vertex_groups};v=[p.co.copy()for p in m.vertices];weights=[{names[g.group]:g.weight for g in p.groups}for p in m.vertices];shapes={k.name:[p.co.copy()for p in k.data]for k in m.shape_keys.key_blocks if k.name!='Basis'};lid={side:{i for i,w in enumerate(weights)if w.get('lid_'+side,0)>.5}for side in ['L','R']};removed=lid['L']|lid['R'];faces=[];materials=[];uvs=[];outer={}
for side,ids in lid.items():outer[side]={i for p in m.polygons if any(j in ids for j in p.vertices)for i in p.vertices if i not in removed}
for p in m.polygons:
 if any(i in removed for i in p.vertices):continue
 faces.append(list(p.vertices));materials.append(p.material_index);uvs.append([tuple(m.uv_layers.active.data[i].uv)for i in p.loop_indices])
closed={};reports=[];material=next(i for i,mat in enumerate(m.materials)if mat.name=='FelineFaceSurface')
for side,sign in [('L',-1),('R',1)]:
 ids=outer[side];edges={};directions={}
 for f in faces:
  for a,b in zip(f,f[1:]+f[:1]):
   if a in ids and b in ids:e=tuple(sorted([a,b]));edges[e]=edges.get(e,0)+1;directions[e]=(a,b)
 graph={i:[]for i in ids}
 for (a,b),count in edges.items():
  if count==1:graph[a].append(b);graph[b].append(a)
 assert all(len(n)==2 for n in graph.values()),{i:len(n)for i,n in graph.items()if len(n)!=2}
 remaining=set(ids);loops=[]
 while remaining:
  start=min(remaining);loop=[start];previous=None;current=start
  while True:
   nxt=next(n for n in graph[current]if n!=previous)
   if nxt==start:break
   assert nxt not in loop;loop.append(nxt);previous,current=current,nxt
  loops.append(loop);remaining-=set(loop)
 print('APERTURE_LOOPS',side,[(len(loop),sum(v[i].y for i in loop)/len(loop))for loop in loops])
 ring=min(loops,key=lambda loop:sum(v[i].y for i in loop)/len(loop));start=ring[0]
 # The secondary internal cut is not the visible rim. Close it without crossing the external annulus.
 for loop in loops:
  if loop is ring:continue
  if directions[tuple(sorted(loop[:2]))]==tuple(loop[:2]):loop=[loop[0]]+list(reversed(loop[1:]))
  point=sum((v[i]for i in loop),Vector())/len(loop);centre=len(v);v.append(point);weights.append({'head':1})
  for coords in shapes.values():coords.append(point.copy())
  for a,b in zip(loop,loop[1:]+loop[:1]):faces.append([a,b,centre]);materials.append(material);uvs.append([(.5,.5)]*3)
 if directions[tuple(sorted(ring[:2]))]==tuple(ring[:2]):ring=[ring[0]]+list(reversed(ring[1:]))
 cx=sign*.059;cz=1.925;cy=-.132;rx,ry,rz=.022,.018,.014;area=sum((v[a].x-cx)*(v[b].z-cz)-(v[b].x-cx)*(v[a].z-cz)for a,b in zip(ring,ring[1:]+ring[:1]));orientation=1 if area>0 else-1;a0=math.atan2((v[start].z-cz)/.021,(v[start].x-cx)/.031);N=len(ring);A=np.array([[1,p.x-cx,p.z-cz,(p.x-cx)**2,(p.z-cz)**2]for p in [v[i]for i in ring]]);q=np.linalg.lstsq(A,np.array([v[i].y for i in ring]),rcond=None)[0];angles=[a0+orientation*math.tau*j/N for j in range(N)]
 for i,a in zip(ring,angles):
  x=.031*math.cos(a);z=.021*math.sin(a);y=float(np.dot([1,x,z,x*x,z*z],q));point=Vector((cx+x,y,cz+z));delta=point-v[i];v[i]=point
  for coords in shapes.values():coords[i]+=delta
 rings=[]
 for k in range(6):
  t=k/6;row=[]
  for j,a in enumerate(angles):
   x=.91*rx*math.cos(a);z=rz*.48*math.sin(a)*(.65+.35*abs(math.sin(a)));y=cy-ry*math.sqrt(max(.04,1-(x/rx)**2-(z/rz)**2))-.0004;inner=Vector((cx+x,y,cz+z));p=inner.lerp(v[ring[j]],t);alpha=((p.x-cx)/rx)**2+((p.z-cz)/rz)**2
   if alpha<1:p.y=min(p.y,cy-ry*math.sqrt(1-alpha)-.0005)
   index=len(v);v.append(p);row.append(index);weights.append({'head':1,'lid_'+side:1})
   for coords in shapes.values():coords.append(p.copy())
   end=p.copy();end.z-=((inner.z-cz)+.0015)*(1-t)**1.1;alpha=((end.x-cx)/rx)**2+((end.z-cz)/rz)**2
   if alpha<1:end.y=min(end.y,cy-ry*math.sqrt(1-alpha)-.001)
   closed[index]=('Blink_'+side,end)
  rings.append(row)
 rings.append(ring)
 for inner,outerrow in zip(rings,rings[1:]):
  for j in range(N):f=[inner[j],outerrow[j],outerrow[(j+1)%N],inner[(j+1)%N]];faces.append(f);materials.append(material);uvs.append([(.02+.46*(v[i].x/.28+.5),.02+.96*(v[i].z-1.75)/.30)for i in f])
 reports.append({'side':side,'boundary_vertices':N,'degree_two':True,'one_external_closed_loop':True,'internal_loops_closed':len(loops)-1,'orientation_matches_adjacent_faces':True})
used=sorted({i for f in faces for i in f});index={i:j for j,i in enumerate(used)};data=bpy.data.meshes.new('Feline_JoinedOrbitalTopology');data.from_pydata([v[i]for i in used],[],[[index[i]for i in f]for f in faces]);data.update();obj=bpy.data.objects.new('SK_OseboLeopard_FinalLoop',data);s.collection.objects.link(obj)
for mat in m.materials:data.materials.append(mat)
layer=data.uv_layers.new(name='UVMap')
for p,mat,coords in zip(data.polygons,materials,uvs):
 p.material_index=mat;p.use_smooth=True
 for li,co in zip(p.loop_indices,coords):
  if data.materials[mat].name=='FelineFaceSurface':q=data.vertices[data.loops[li].vertex_index].co;co=((.02 if q.y<0 else .52)+.46*(q.x/.28+.5),.02+.96*(q.z-1.75)/.30)
  layer.data[li].uv=co
allnames={n for i in used for n in weights[i]};groups={n:obj.vertex_groups.new(name=n)for n in allnames}
for i in used:
 for n,w in weights[i].items():
  if w>0:groups[n].add([index[i]],w,'REPLACE')
obj.parent=rig;obj.modifiers.new('Skin','ARMATURE').object=rig;obj.shape_key_add(name='Basis')
for name,coords in shapes.items():
 shape=obj.shape_key_add(name=name)
 for i in used:shape.data[index[i]].co=coords[i]
for i,(name,co)in closed.items():obj.data.shape_keys.key_blocks[name].data[index[i]].co=co
bpy.data.objects.remove(old,do_unlink=True);obj.name='SK_OseboLeopard';obj.hide_render=False;obj.hide_set(False)
for image in bpy.data.images:
 if image.filepath and Path(image.filepath).is_file()and Path(image.filepath).parent==src:
  target=out/Path(image.filepath).name;shutil.copyfile(image.filepath,target);image.filepath=str(target);image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'OseboLeopard.blend'));bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(out/'OseboLeopard.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
p=out/'OseboLeopard.glb';raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);d['asset'].pop('generator',None);head=json.dumps(d,separators=(',',':')).encode();head+=b' '*((-len(head))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(head)+len(tail))+struct.pack('<II',len(head),0x4e4f534a)+head+tail);r=json.loads((src/'art-pass2.json').read_text());r.update(scene_sha256=hashlib.sha256((out/'OseboLeopard.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),orbital_boundary_reports=reports,orbital_correction='True edge adjacency, fitted surface depth and even boundary spacing; no angle-sorted crossing faces');(out/'art-pass2.json').write_text(json.dumps(r,indent=2)+'\n');print('ORBITAL_CONNECTIVITY_REPAIRED',reports)
