"""Join palm/digit skin, preserving the established rest rig and clip identities."""
import bpy,bmesh,json,hashlib,struct,shutil,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];src=R/'SourceArt/Characters/Kwaku/Authored_v032';out=src.parent/'Authored_v035';assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(src/'Kwaku.blend'));s=bpy.context.scene;old=bpy.data.objects['SK_Kwaku'];m=old.data;rig=next(o for o in s.objects if o.type=='ARMATURE');rig.animation_data.action=None
for p in rig.pose.bones:p.rotation_euler=(0,0,0);p.location=(0,0,0);p.scale=(1,1,1)
s.frame_set(0);names={g.index:g.name for g in old.vertex_groups};weights=[{names[g.group]:g.weight for g in v.groups}for v in m.vertices];coords=[v.co.copy()for v in m.vertices];faces=[list(p.vertices)for p in m.polygons];mats=[p.material_index for p in m.polygons];uvs=[[tuple(m.uv_layers.active.data[i].uv)for i in p.loop_indices]for p in m.polygons];shapes={k.name:[p.co.copy()for p in k.data]for k in m.shape_keys.key_blocks if k.name!='Basis'};removed=set();added=[];reports=[];skin=next(i for i,mat in enumerate(m.materials)if mat.name=='Skin')
for side in ['L','R']:
 ids={i for i,w in enumerate(weights)if sum(v for n,v in w.items()if n.startswith(('upperarm_'+side,'lowerarm_'+side,'hand_'+side,'digit_'+side)))>.95};assert len(ids)>1000;selected=[f for f in faces if set(f).issubset(ids)];used=sorted({i for f in selected for i in f});remap={i:j for j,i in enumerate(used)};data=bpy.data.meshes.new('ConnectedArmHand_'+side);data.from_pydata([coords[i]for i in used],[],[[remap[i]for i in f]for f in selected]);data.update();data.calc_loop_triangles();originalverts=[v.co.copy()for v in data.vertices];triangles=[tuple(t.vertices)for t in data.loop_triangles];tree=BVHTree.FromPolygons(originalverts,triangles);obj=bpy.data.objects.new(data.name,data);s.collection.objects.link(obj);bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new('PalmDigitUnion','REMESH');mod.mode='VOXEL';mod.voxel_size=.0017;mod.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=mod.name);smooth=obj.modifiers.new('AnatomicalSurfaceRelax','SMOOTH');smooth.factor=.35;smooth.iterations=3;bpy.ops.object.modifier_apply(modifier=smooth.name);reduce=obj.modifiers.new('BoundedSurfaceReduction','DECIMATE');reduce.ratio=.25;reduce.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=reduce.name)
 # Actual original surface triangles provide barycentric established skin weights.
 v0=len(coords);trimmed=0;maxdist=0
 for vertex in obj.data.vertices:
  point=vertex.co.copy();hit=tree.find_nearest(point);assert hit;maxdist=max(maxdist,hit[3]);a,b,c=triangles[hit[2]];A,B,C=[originalverts[i]for i in [a,b,c]];e0=B-A;e1=C-A;e2=hit[0]-A;den=e0.dot(e0)*e1.dot(e1)-e0.dot(e1)**2
  if abs(den)>1e-18:beta=(e1.dot(e1)*e2.dot(e0)-e0.dot(e1)*e2.dot(e1))/den;gamma=(e0.dot(e0)*e2.dot(e1)-e0.dot(e1)*e2.dot(e0))/den;alpha=1-beta-gamma
  else:alpha,beta,gamma=1,0,0
  combined={}
  for original,factor in zip([used[a],used[b],used[c]],[alpha,beta,gamma]):
   for n,w in weights[original].items():
    if n in rig.data.bones:combined[n]=combined.get(n,0)+max(0,factor)*w
  keep=sorted(combined.items(),key=lambda x:x[1],reverse=True)[:4];trimmed+=len(combined)>4;total=sum(w for n,w in keep);assert total>0;coords.append(point);weights.append({n:w/total for n,w in keep})
  for values in shapes.values():values.append(point.copy())
 for p in obj.data.polygons:faces.append([v0+i for i in p.vertices]);mats.append(skin);uvs.append([(obj.data.vertices[i].co.x*.2+.5,obj.data.vertices[i].co.z*.45)for i in p.vertices])
 removed|=ids;reports.append({'side':side,'old_arm_digit_vertices':len(used),'joined_vertices':len(obj.data.vertices),'voxel_m':.0017,'surface_reduction_ratio':.25,'weight_transfer':'Nearest actual original triangle barycentric interpolation; top4normalised','vertices_with_more_than4_interpolated_groups':trimmed,'maximum_source_surface_distance_m':maxdist});bpy.data.objects.remove(obj,do_unlink=True)
keep=[j for j,f in enumerate(faces)if not any(i in removed for i in f)];faces=[faces[j]for j in keep];mats=[mats[j]for j in keep];uvs=[uvs[j]for j in keep];used=sorted({i for f in faces for i in f});remap={i:j for j,i in enumerate(used)};data=bpy.data.meshes.new('Kwaku_ConnectedHandsSurface');data.from_pydata([coords[i]for i in used],[],[[remap[i]for i in f]for f in faces]);data.update();obj=bpy.data.objects.new('Kwaku_Pass2_Hands',data);s.collection.objects.link(obj)
for mat in m.materials:data.materials.append(mat)
layer=data.uv_layers.new(name='UVMap')
for p,mat,uv in zip(data.polygons,mats,uvs):
 p.material_index=mat;p.use_smooth=True
 for li,co in zip(p.loop_indices,uv):layer.data[li].uv=co
allnames={n for i in used for n in weights[i]};groups={n:obj.vertex_groups.new(name=n)for n in allnames}
for i in used:
 for name,w in weights[i].items():
  if w>0:groups[name].add([remap[i]],w,'REPLACE')
obj.parent=rig;obj.modifiers.new('Skin','ARMATURE').object=rig;obj.shape_key_add(name='Basis')
for name,values in shapes.items():
 k=obj.shape_key_add(name=name)
 for i in used:k.data[remap[i]].co=values[i]
bpy.data.objects.remove(old,do_unlink=True);obj.name='SK_Kwaku';obj.hide_render=False;obj.hide_set(False)
for image in bpy.data.images:
 if image.filepath and Path(image.filepath).is_file()and Path(image.filepath).parent==src:target=out/Path(image.filepath).name;shutil.copyfile(image.filepath,target);image.filepath=str(target);image.pack()
shutil.copyfile(src/'Ledger.glb',out/'Ledger.glb');bpy.ops.wm.save_as_mainfile(filepath=str(out/'Kwaku.blend'));bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(out/'Kwaku.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
p=out/'Kwaku.glb';raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);d['asset'].pop('generator',None);head=json.dumps(d,separators=(',',':')).encode();head+=b' '*((-len(head))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(head)+len(tail))+struct.pack('<II',len(head),0x4e4f534a)+head+tail)
r=json.loads((src/'art-pass2.json').read_text());r.update(scene_sha256=hashlib.sha256((out/'Kwaku.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),connected_hand_reports=reports,source_vertices=len(data.vertices));(out/'art-pass2.json').write_text(json.dumps(r,indent=2)+'\n');print('PALM_DIGIT_SURFACES_CONNECTED',reports)
