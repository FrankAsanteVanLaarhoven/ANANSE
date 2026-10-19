"""Add upper branching/canopy continuity to the three new editable tree assets."""
import bpy,math,sys,json,struct,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];OUT=R/'SourceArt/Environments/MarketSanctuary/HeroCells_v002';backup=R/'.local/verification/hero-cells-pass2-20261017/source-before-crown.blend';assert not backup.exists();shutil.copy2(OUT/'HeroCellsPass2.blend',backup);bpy.ops.wm.open_mainfile(filepath=str(OUT/'HeroCellsPass2.blend'));sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g
g.scene=bpy.context.scene;g.parts=[];g.binds={};g.joints={};contract=json.loads((OUT/'source-status.json').read_text())
for name,lean,phase in [('SentinelTree',(-1.7,.3),.2),('LeaningTree',(2.7,-1.4),1.4),('ForkedTree',(-.3,2.4),2.8)]:
 col=bpy.data.collections[name]
 def put(o):
  for c in list(o.users_collection):c.objects.unlink(o)
  col.objects.link(o);return o
 for k in range(6):
  a=k*math.tau/6+phase;dx,dy=math.cos(a),math.sin(a);z=8.9+(k%3)*.7;start=(lean[0]*.65,lean[1]*.65,z);end=(lean[0]+dx*(1.8+(k%2)*.5),lean[1]+dy*(1.8+(k%2)*.5),12.3+(k%3)*.35)
  put(g.tube('Upper crown continuation',[start,(lean[0]*.8+dx*.6,lean[1]*.8+dy*.6,z+1.3),end],[.20,.12,.025],bpy.data.materials['Bark'],segments=10))
  for q in range(18):
   aa=q*math.tau/18;p=(end[0]+.45*math.cos(aa),end[1]+.45*math.sin(aa),end[2]-.1+q%3*.09);length=1.05+(q%3)*.14;width=.3;vs=[]
   for i in range(9):
    t=i/8;w=width*math.sin(math.pi*t)**.8
    for side in [-1,0,1]:
     x=t*length;y=side*w;zz=.16*math.sin(math.pi*t)*length+.025*(1-abs(side));vs.append((p[0]+x*math.cos(aa)-y*math.sin(aa),p[1]+x*math.sin(aa)+y*math.cos(aa),p[2]+zz))
   fs=[]
   for i in range(8):
    for j in range(2):v=i*3+j;fs.append((v,v+1,v+4,v+3))
   put(g.mesh('Upper layered leaf',vs,fs,bpy.data.materials['Leaf']))
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for o in list(col.objects):
  c=o.copy();c.data=o.data.copy();g.scene.collection.objects.link(c);c.select_set(True);copies.append(c)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');path=OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_animations=False)
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);j['asset'].pop('generator',None);s=json.dumps(j,separators=(',',':')).encode();s+=b' '*(-len(s)%4);tail=b[20+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(s)+len(tail))+struct.pack('<II',len(s),0x4e4f534a)+s+tail)
 row=next(r for r in contract['exports']if r['name']==name);row['triangles']=sum(len(p.vertices)-2 for p in o.data.polygons);row['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();bpy.data.objects.remove(o,do_unlink=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'HeroCellsPass2.blend'));contract['scene_sha256']=hashlib.sha256((OUT/'HeroCellsPass2.blend').read_bytes()).hexdigest();contract['crown_refinement']='Upper branches and canopy continuity added; earlier scene preserved locally';(OUT/'source-status.json').write_text(json.dumps(contract,indent=2))
