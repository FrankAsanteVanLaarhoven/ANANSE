"""Continuous non-playable far-bank terrain behind the market hero waterfront."""
import bpy,sys,json,math,struct,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];OUT=R/'SourceArt/Environments/MarketSanctuary/HeroCells_v002';backup=R/'.local/verification/hero-cells-pass2-20261017/source-before-backshore.blend';assert not backup.exists();shutil.copy2(OUT/'HeroCellsPass2.blend',backup);bpy.ops.wm.open_mainfile(filepath=str(OUT/'HeroCellsPass2.blend'));sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g
g.scene=bpy.context.scene;g.parts=[];g.binds={};g.joints={};v=[];f=[]
for j in range(65):
 y=(j-32)*1.4
 for i in range(17):
  t=i/16;x=-12+t*24+.6*math.sin(y*.2)*(1-t);z=.05+1.2*t+.18*math.sin(y*.37+x*.2)*t;v.append((x,y,z))
for j in range(64):
 for i in range(16):a=j*17+i;f.append((a,a+1,a+18,a+17))
o=g.mesh('BackshoreTerrain',v,f,bpy.data.materials['HazeStone']);col=bpy.data.collections.new('BackshoreTerrain');g.scene.collection.children.link(col)
for c in list(o.users_collection):c.objects.unlink(o)
col.objects.link(o)
for p in o.data.polygons:p.use_smooth=True
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');path=OUT/'BackshoreTerrain.glb';bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_animations=False)
b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);j['asset'].pop('generator',None);s=json.dumps(j,separators=(',',':')).encode();s+=b' '*(-len(s)%4);tail=b[20+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(s)+len(tail))+struct.pack('<II',len(s),0x4e4f534a)+s+tail);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'HeroCellsPass2.blend'));d=json.loads((OUT/'source-status.json').read_text());d['exports'].append({'name':'BackshoreTerrain','file':path.name,'triangles':2048,'materials':1,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});d['scene_sha256']=hashlib.sha256((OUT/'HeroCellsPass2.blend').read_bytes()).hexdigest();(OUT/'source-status.json').write_text(json.dumps(d,indent=2))
