"""Editable roof-platform cladding and woven crossing detail; no movement geometry."""
import bpy,sys,math,json,struct,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];OUT=R/'SourceArt/Environments/MarketSanctuary/HeroCells_v001';sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g
bpy.ops.wm.read_factory_settings(use_empty=True);g.scene=bpy.context.scene;g.parts=[];g.binds={};g.joints={};groups={};cur='RoofGallery';mats={n:g.material(n,c,rough=.8,metal=.2 if n=='GoldThread' else 0)for n,c in [('Lime',(.68,.51,.31)),('Timber',(.22,.105,.045)),('Stone',(.32,.35,.28)),('Jade',(.055,.24,.21)),('GoldThread',(.73,.46,.12))]}
def put(o):groups.setdefault(cur,[]).append(o);return o
def box(n,p,d,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.scale=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[m]);mod=o.modifiers.new('Worn edge','BEVEL');mod.width=min(.018,min(d)*.2);mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name);return put(o)
def tube(n,p,r,m):return put(g.tube(n,p,r,mats[m],segments=6))
# Same platform envelope as existing roof: 8 x 5 metres, walking top at 2.4m.
box('Roof walking surface visual',(0,0,2.36),(8,5,.08),'Stone')
for side in [-1,1]:
 y=side*2.51
 for z in [.15,2.18,2.36]:box('Gallery string course',(0,y,z),(8.15,.20,.14),'Lime')
 for x in [-3.8,-1.9,0,1.9,3.8]:
  box('Gallery pier',(x,y,1.13),(.23,.35,2.15),'Lime')
  box('Gallery stone foot',(x,y,.22),(.38,.46,.44),'Stone')
 for x in [-2.85,-.95,.95,2.85]:
  box('Gallery shadow shutter',(x,y,1.12),(1.55,.12,1.7),'Jade')
  for k in range(8):box('Gallery timber louvre',(x,y+side*.11,.47+k*.18),(1.48,.10,.065),'Timber')
  for dx in [-.8,.8]:box('Gallery jamb',(x+dx,y+side*.08,1.12),(.07,.12,1.8),'Timber')
for x in [-4.01,4.01]:
 box('Gallery side render',(x,0,1.15),(.1,5,2.3),'Lime')
 for y in [-2,-.7,.7,2]:box('Gallery side buttress',(x,y,1.1),(.35,.24,2.2),'Lime')
cur='WovenDeck'
for i in range(19):
 x=-.96+i*.106;tube('Cross woven silk',[(x+.012*math.sin(j+i),-.56+j*.07,.15+.015*math.sin(j*1.5+i))for j in range(17)],[.008]*17,'GoldThread')
for side in [-1,1]:
 for i in range(9):
  x=-.9+i*.225;tube('Diamond thread fan',[(x-.11,side*.61,.35),(x,side*.61,.55),(x+.11,side*.61,.35),(x,side*.61,.16),(x-.11,side*.61,.35)],[.006]*5,'GoldThread')
exports=[]
for name,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for o in objects:
  c=o.copy();c.data=o.data.copy();g.scene.collection.objects.link(c);c.select_set(True);copies.append(c)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');path=OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_animations=False)
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);j['asset'].pop('generator',None);s=json.dumps(j,separators=(',',':')).encode();s+=b' '*(-len(s)%4);tail=b[20+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(s)+len(tail))+struct.pack('<II',len(s),0x4e4f534a)+s+tail)
 exports.append({'name':name,'file':path.name,'triangles':sum(len(f.vertices)-2 for f in o.data.polygons),'materials':len(o.data.materials)});bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'HeroDetails.blend'));(OUT/'detail-status.json').write_text(json.dumps({'scene':'HeroDetails.blend','sha256':hashlib.sha256((OUT/'HeroDetails.blend').read_bytes()).hexdigest(),'exports':exports,'creative_approved':False},indent=2))
