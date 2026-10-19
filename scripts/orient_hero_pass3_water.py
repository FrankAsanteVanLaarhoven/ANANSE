"""Qualify upward-facing open water/bank surfaces before one-sided native import."""
import bpy,bmesh,json,hashlib,struct,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];OUT=R/'SourceArt/Environments/MarketSanctuary/HeroCells_v003';E=R/'.local/verification/hero-cells-pass3-20261017';shutil.copy2(OUT/'HeroCellsPass3.blend',E/'source-before-normal-fix.blend');bpy.ops.wm.open_mainfile(filepath=str(OUT/'HeroCellsPass3.blend'));d=json.loads((OUT/'source-status.json').read_text());audit=[]
for name in ['RiverMargin','LivingStream']:
 for o in bpy.data.collections[name].objects:
  if 'skin'not in o.name and'transition'not in o.name:continue
  mean=sum(p.normal.z*p.area for p in o.data.polygons)/sum(p.area for p in o.data.polygons);before=mean
  if mean<0:
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
  mean=sum(p.normal.z*p.area for p in o.data.polygons)/sum(p.area for p in o.data.polygons);assert mean>.8;audit.append({'object':o.name,'area_weighted_normal_z_before':before,'after':mean})
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for original in bpy.data.collections[name].objects:
  o=original.copy();o.data=original.data.copy();bpy.context.scene.collection.objects.link(o);o.select_set(True);copies.append(o)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');path=OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_animations=False)
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);j['asset'].pop('generator',None);s=json.dumps(j,separators=(',',':')).encode();s+=b' '*(-len(s)%4);tail=b[20+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(s)+len(tail))+struct.pack('<II',len(s),0x4e4f534a)+s+tail);row=next(r for r in d['exports']if r['name']==name);row['triangles']=sum(len(p.vertices)-2 for p in o.data.polygons);row['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();bpy.data.objects.remove(o,do_unlink=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'HeroCellsPass3.blend'));d['scene_sha256']=hashlib.sha256((OUT/'HeroCellsPass3.blend').read_bytes()).hexdigest();d['normal_orientation']=audit;(OUT/'source-status.json').write_text(json.dumps(d,indent=2));(E/'water-normal-fix.json').write_text(json.dumps(audit,indent=2))
