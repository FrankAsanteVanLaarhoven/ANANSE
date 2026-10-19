"""Correct first-view visual failures without replacing preserved Pass3 source."""
import bpy,math,random,struct,json,hashlib,sys,shutil,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];ROOT=R;OUT=R/'SourceArt/Environments/MarketSanctuary/HeroCells_v004';E=R/'.local/verification/hero-cells-pass4-20261018';shutil.copy2(OUT/'HeroCellsPass4.blend',E/'source-before-presentation.blend');bpy.ops.wm.open_mainfile(filepath=str(OUT/'HeroCellsPass4.blend'));sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g
g.scene=bpy.context.scene;g.parts=[];g.binds={};g.joints={};scene=bpy.context.scene;mats={m.name:m for m in bpy.data.materials};rng=random.Random(184027)
s=(R/'scripts/author_hero_cells.py').read_text();exec(s[s.index('groups={};'):s.index('# Layered market frontages')]);s=(R/'scripts/author_hero_cells_pass3.py').read_text();exec(s[s.index('def sweep('):s.index('# Three independently')])
col=bpy.data.collections['RiverReach']
for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(col)
s=(R/'scripts/author_hero_cells_pass4.py').read_text();exec(s[s.index('def channel('):s.index("channel('RiverReach'")].replace('161 if river else 65','281 if river else 65'));channel('RiverReach',132,10,True)
for o in groups['RiverReach']:
 if 'surface' in o.name or'lip'in o.name:
  import bmesh
  if sum(p.normal.z*p.area for p in o.data.polygons)<0:
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
col=bpy.data.collections.new('RiverReach');scene.collection.children.link(col)
for o in groups['RiverReach']:
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o)
for o in bpy.data.collections['SanctuaryReliquary'].objects:
 for v in o.data.vertices:v.co.x*=1.35
N=512;y,x=np.mgrid[:N,:N];u=x/N;v=y/N;nx=.25*np.sin(math.tau*(u*11+v*3))+.08*np.sin(math.tau*(u*23-v*9));ny=.15*np.cos(math.tau*(v*9-u*2))+.06*np.cos(math.tau*(v*21+u*7));nz=np.sqrt(1-nx*nx-ny*ny);rgb=np.stack([nx*.5+.5,ny*.5+.5,nz*.5+.5],2);im=bpy.data.images.new('WaterFlowNormal',width=N,height=N,alpha=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.dstack([rgb,np.ones((N,N))]).astype('float32').ravel());im.filepath_raw=str(OUT/'WaterFlowNormal.png');im.file_format='PNG';im.save();m=mats['Water'];tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;normal=m.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.6;m.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],m.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
d=json.loads((OUT/'source-status.json').read_text())
for name in ['RiverReach','SanctuaryReliquary']:
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for original in bpy.data.collections[name].objects:
  o=original.copy();o.data=original.data.copy();scene.collection.objects.link(o);o.select_set(True);copies.append(o)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');path=OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_animations=False)
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);j['asset'].pop('generator',None);ss=json.dumps(j,separators=(',',':')).encode();ss+=b' '*(-len(ss)%4);tail=b[20+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(ss)+len(tail))+struct.pack('<II',len(ss),0x4e4f534a)+ss+tail);row=next(r for r in d['exports']if r['name']==name);row['triangles']=sum(len(p.vertices)-2 for p in o.data.polygons);row['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();bpy.data.objects.remove(o,do_unlink=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'HeroCellsPass4.blend'));d['scene_sha256']=hashlib.sha256((OUT/'HeroCellsPass4.blend').read_bytes()).hexdigest();d['water_normal']={'file':'WaterFlowNormal.png','sha256':hashlib.sha256((OUT/'WaterFlowNormal.png').read_bytes()).hexdigest()};d['presentation']='Single132m river sheet over former[-3600,9600]cmextent; marker width+35%; authored wave normal';(OUT/'source-status.json').write_text(json.dumps(d,indent=2))
