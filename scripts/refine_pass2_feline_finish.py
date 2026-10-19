"""Feline contour, anatomical pads, physical armour edges and painted throat."""
import bpy,bmesh,json,hashlib,struct,shutil,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];src=R/'SourceArt/Characters/OseboLeopard/Authored_v019';out=src.parent/'Authored_v021';assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(src/'OseboLeopard.blend'));s=bpy.context.scene;old=bpy.data.objects['SK_OseboLeopard'];m=old.data;rig=next(o for o in s.objects if o.type=='ARMATURE');rig.animation_data.action=None;s.frame_set(0);names={g.index:g.name for g in old.vertex_groups};weights=[{names[g.group]:g.weight for g in p.groups}for p in m.vertices];v=[p.co.copy()for p in m.vertices];faces=[list(p.vertices)for p in m.polygons];mats=[p.material_index for p in m.polygons];uvs=[[tuple(m.uv_layers.active.data[i].uv)for i in p.loop_indices]for p in m.polygons];shapes={k.name:[p.co.copy()for p in k.data]for k in m.shape_keys.key_blocks if k.name!='Basis'};slots={mat.name:i for i,mat in enumerate(m.materials)};original_count=len(v);removed=set();changes=[]
def warp(p):
 x,y,z=p;front=max(0,min(1,(-y-.03)/.10));head=max(0,min(1,(z-1.77)/.12));top=max(0,min(1,(z-1.90)/.11));p.x*=1-.10*top
 if z>1.79:p.y-=.004*math.exp(-((z-1.875)/.035)**2-((abs(x)-.075)/.035)**2)*front
 # Lift outer canthus slightly, preserving both lid and eye surfaces through the same field.
 for sign in [-1,1]:p.z+=sign*(x-sign*.059)*.12*math.exp(-((x-sign*.059)/.044)**4-((z-1.925)/.035)**4)*front
 return p
for i,p in enumerate(v):
 if sum(w for n,w in weights[i].items()if n in ['head','jaw','eye_L','eye_R','ear_L','ear_R'])>.9 and p.z>1.76:
  v[i]=warp(p.copy())
  for q in shapes.values():q[i]=warp(q[i].copy())
 # Taper actual tail root rings, never the authoritative pawn root.
 if weights[i].get('tail_01',0)>.8:
  base=rig.data.bones['tail_01'].head_local;axis=(rig.data.bones['tail_01'].tail_local-base).normalized();t=(p-base).dot(axis);radial=p-base-axis*t;delta=radial*.10*max(0,1-t/.10);v[i]+=delta
  for q in shapes.values():q[i]+=delta
# Connected armour shells receive actual edge thickness/bevel, retaining their rigid bone weights.
parent=list(range(original_count))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for e in m.edges:
 a,b=map(find,e.vertices)
 if a!=b:parent[a]=b
comps={}
for i in range(original_count):comps.setdefault(find(i),[]).append(i)
neck_ids=next(set(ids)for ids in comps.values()if len(ids)==962 and min(v[i].z for i in ids)>1.5 and max(v[i].z for i in ids)<1.82)
armour=[]
for ids in comps.values():
 group=set(ids);polys=[p for p in m.polygons if set(p.vertices).issubset(group)]
 if not polys or not all(m.materials[p.material_index].name=='Armour_Brown_Leather'for p in polys):continue
 index={i:j for j,i in enumerate(ids)};data=bpy.data.meshes.new('Armour_Bevel');data.from_pydata([v[i]for i in ids],[],[[index[i]for i in p.vertices]for p in polys]);data.update();obj=bpy.data.objects.new('Armour_Bevel',data);s.collection.objects.link(obj);groups={n:obj.vertex_groups.new(name=n)for n in {n for i in ids for n in weights[i]if n in rig.data.bones}}
 for i in ids:
  for n,w in weights[i].items():
   if n in groups:groups[n].add([index[i]],w,'REPLACE')
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bm=bmesh.new();bm.from_mesh(data);boundary=any(e.is_boundary for e in bm.edges);bm.free()
 if boundary:solid=obj.modifiers.new('PlateThickness','SOLIDIFY');solid.thickness=.004;solid.offset=0;bpy.ops.object.modifier_apply(modifier=solid.name)
 bevel=obj.modifiers.new('WorkedLeatherEdge','BEVEL');bevel.width=.003;bevel.segments=2;bevel.limit_method='ANGLE';bpy.ops.object.modifier_apply(modifier=bevel.name);offset=len(v);groupnames={g.index:g.name for g in obj.vertex_groups}
 for p in obj.data.vertices:
  v.append(p.co.copy());d={groupnames[g.group]:g.weight for g in p.groups if g.weight>1e-6};total=sum(d.values());assert total>0;weights.append({n:w/total for n,w in d.items()})
  for q in shapes.values():q.append(p.co.copy())
 for p in obj.data.polygons:faces.append([offset+i for i in p.vertices]);mats.append(slots['Armour_Brown_Leather']);uvs.append([(obj.data.vertices[i].co.x*.2+.5,obj.data.vertices[i].co.z*.45)for i in p.vertices])
 removed|=group;armour.append({'old_vertices':len(ids),'new_vertices':len(obj.data.vertices),'thickness_m':.004 if boundary else 0,'bevel_m':.003});bpy.data.objects.remove(obj,do_unlink=True)
# Four existing articulated digits, with proposed ventral pad placement on actual skin hits.
tree=BVHTree.FromPolygons(v,faces);pads=[]
for side in ['L','R']:
 for digit in [-1,0,1,2,3]:
  bone=rig.data.bones['hand_'+side if digit==-1 else f'digit_{side}_{digit}_02'];c=bone.head_local.lerp(bone.tail_local,.70);hit=tree.ray_cast(Vector((c.x,-1,c.z)),Vector((0,1,0)),2);assert hit and hit[0]is not None;c=hit[0]+Vector((0,-.0007,0));rx,ry,rz=(.021,.0018,.023)if digit==-1 else(.0065,.0012,.008);offset=len(v);N=16;M=8
  for j in range(M+1):
   theta=math.pi*j/M
   for k in range(N):
    a=math.tau*k/N;p=c+Vector((rx*math.sin(theta)*math.cos(a),ry*math.sin(theta)*math.sin(a),rz*math.cos(theta)));v.append(p);weights.append({bone.name:1})
    for q in shapes.values():q.append(p.copy())
  for j in range(M):
   for k in range(N):f=[offset+j*N+k,offset+j*N+(k+1)%N,offset+(j+1)*N+(k+1)%N,offset+(j+1)*N+k];faces.append(f);mats.append(slots['Nose_Lips_Claws']);uvs.append([(k/N,j/M),((k+1)/N,j/M),((k+1)/N,(j+1)/M),(k/N,(j+1)/M)])
  pads.append({'side':side,'digit':digit,'bone':bone.name,'source_contact':list(hit[0]),'proposal':'Ventral pad; human anatomy approval required'})
keep=[j for j,f in enumerate(faces)if not any(i in removed for i in f)];faces=[faces[j]for j in keep];mats=[mats[j]for j in keep];uvs=[uvs[j]for j in keep];used=sorted({i for f in faces for i in f});index={i:j for j,i in enumerate(used)};data=bpy.data.meshes.new('Feline_Pass2_Finish');data.from_pydata([v[i]for i in used],[],[[index[i]for i in f]for f in faces]);data.update();obj=bpy.data.objects.new('Feline_Pass2_Finish',data);s.collection.objects.link(obj)
for mat in m.materials:data.materials.append(mat)
layer=data.uv_layers.new(name='UVMap')
for p,mat,uv in zip(data.polygons,mats,uvs):
 p.material_index=mat;p.use_smooth=True;centre=sum((data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices);boneweights=[weights[used[i]]for i in p.vertices];neck=all(used[i]in neck_ids for i in p.vertices)
 if neck and centre.y<-.025:p.material_index=slots['FelineFaceSurface']
 if data.materials[p.material_index].name=='FelineFaceSurface'and centre.y>0:p.material_index=slots['Fur_Gold_Rosettes']
 for li,co in zip(p.loop_indices,uv):
  q=data.vertices[data.loops[li].vertex_index].co
  if neck and centre.y<-.025:co=(.52+.46*(q.x/.30+.5),.02+.96*(q.z-1.53)/.28)
  layer.data[li].uv=co
allnames={n for i in used for n in weights[i]};groups={n:obj.vertex_groups.new(name=n)for n in allnames}
for i in used:
 for n,w in weights[i].items():
  if w>0:groups[n].add([index[i]],w,'REPLACE')
obj.parent=rig;obj.modifiers.new('Skin','ARMATURE').object=rig;obj.shape_key_add(name='Basis')
for name,q in shapes.items():
 shape=obj.shape_key_add(name=name)
 for i in used:shape.data[index[i]].co=q[i]
bpy.data.objects.remove(old,do_unlink=True);obj.name='SK_OseboLeopard';obj.hide_render=False;obj.hide_set(False)
# Reuse the right atlas half for the actual throat surface; no floating cream insert.
material=bpy.data.materials['FelineFaceSurface'];tex=next(n for n in material.node_tree.nodes if n.type=='TEX_IMAGE');image=tex.image;W,H=image.size;paint=np.array(image.pixels[:],dtype=np.float32).reshape(H,W,4);Y,X=np.mgrid[0:H,0:W];u=X/(W-1);z=(Y/(H-1)-.02)/.96*.28+1.53;x=((u-.52)/.46-.5)*.30;mask=np.exp(-(x/.072)**4)*np.clip((z-1.57)/.08,0,1);gold=np.array((.43,.235,.067));cream=np.array((.65,.55,.39));region=u>=.5;rgb=gold[None,None,:]*(1-mask[:,:,None])+cream[None,None,:]*mask[:,:,None];paint[:,:,:3][region]=rgb[region];image=image.copy();image.pixels.foreach_set(paint.ravel());image.filepath_raw=str(out/'FelineFaceSurface_BaseColor.png');image.file_format='PNG';image.save();image.pack();tex.image=image
for img in bpy.data.images:
 if img.filepath and Path(img.filepath).is_file()and Path(img.filepath).parent==src:
  target=out/Path(img.filepath).name
  if not target.exists():shutil.copyfile(img.filepath,target);img.filepath=str(target);img.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'OseboLeopard.blend'));bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(out/'OseboLeopard.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
p=out/'OseboLeopard.glb';raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);d['asset'].pop('generator',None);head=json.dumps(d,separators=(',',':')).encode();head+=b' '*((-len(head))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(head)+len(tail))+struct.pack('<II',len(head),0x4e4f534a)+head+tail);r=json.loads((src/'art-pass2.json').read_text());r.update(scene_sha256=hashlib.sha256((out/'OseboLeopard.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),armour_parts=armour,pads_proposed=pads,source_vertices=len(data.vertices),finish_parent_scene_sha256=hashlib.sha256((src/'OseboLeopard.blend').read_bytes()).hexdigest(),finish='Tapered cranium/outer-canthus angle, physical armour edge bevel, painted connected throat, pads on actual paw surfaces, tail-root flare');(out/'art-pass2.json').write_text(json.dumps(r,indent=2)+'\n');print('FELINE_ART_FINISH_AUTHORED',len(armour),len(pads))
