"""Close the hero-tree upper crowns after direct source-render inspection."""
import bpy,math,sys,json,struct,hashlib,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];OUT=R/'SourceArt/Environments/MarketSanctuary/HeroCells_v003';E=R/'.local/verification/hero-cells-pass3-20261017';shutil.copy2(OUT/'HeroCellsPass3.blend',E/'source-before-crown.blend');bpy.ops.wm.open_mainfile(filepath=str(OUT/'HeroCellsPass3.blend'));sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g
g.scene=bpy.context.scene;g.parts=[];g.binds={};g.joints={};mats={m.name:m for m in bpy.data.materials};groups={};cur='';rng=__import__('random').Random(173027)
def put(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 bpy.data.collections[cur].objects.link(o);return o
src=(R/'scripts/author_hero_cells_pass3.py').read_text();exec(src[src.index('def sweep('):src.index('# Three independently')])
leafsrc=(R/'scripts/author_hero_cells.py').read_text();exec(leafsrc[leafsrc.index('def leaf('):leafsrc.index('def arch(')])
contract=json.loads((OUT/'source-status.json').read_text())
for name,lean,phase in [('CrownGuardian',(-2.7,.6),.2),('RiverFig',(3.2,-1.9),1.8),('TwinnedElder',(-.7,2.9),3.7)]:
 cur=name;lx,ly=lean
 for k in range(7):
  a=phase+k*math.tau/7;dx,dy=math.cos(a),math.sin(a);z=8.8+(k%3)*.8;end=(lx*1.05+dx*2.2,ly*1.05+dy*2.2,12.0+(k%3)*.4)
  sweep('Upper continuous crown',[(lx*.8,ly*.8,z),(lx,ly,z+1.1),(lx+dx,ly+dy,11.5),end],[.23,.18,.11,.012],sides=12,steps=8)
  for q in range(28):
   aa=q*2.399+phase;rad=.2+.06*q;leaf((end[0]+rad*math.cos(aa),end[1]+rad*math.sin(aa),end[2]+.12*(q%4)-.3),aa,.95+(q%4)*.14,.28)
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for original in list(bpy.data.collections[name].objects):
  o=original.copy();o.data=original.data.copy();g.scene.collection.objects.link(o);o.select_set(True);copies.append(o)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');path=OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_animations=False)
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);j['asset'].pop('generator',None);s=json.dumps(j,separators=(',',':')).encode();s+=b' '*(-len(s)%4);tail=b[20+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(s)+len(tail))+struct.pack('<II',len(s),0x4e4f534a)+s+tail)
 row=next(r for r in contract['exports']if r['name']==name);row['triangles']=sum(len(p.vertices)-2 for p in o.data.polygons);row['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();bpy.data.objects.remove(o,do_unlink=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'HeroCellsPass3.blend'));contract['scene_sha256']=hashlib.sha256((OUT/'HeroCellsPass3.blend').read_bytes()).hexdigest();contract['crown_refinement']='Bare upper silhouettes corrected after direct source-render inspection';(OUT/'source-status.json').write_text(json.dumps(contract,indent=2))
