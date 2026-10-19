"""Original static sanctuary crossing and opaque shallow stream, no mission powers."""
import bpy,sys,math,json,struct,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=R/'SourceArt/Environments/MarketSanctuary/Crossing_v001';assert not out.exists();out.mkdir(parents=True);sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g
bpy.ops.wm.read_factory_settings(use_empty=True);g.scene=bpy.context.scene;g.parts=[];g.binds={};g.joints={};g.scene.unit_settings.system='METRIC';gold=g.material('GoldenFiber',(.50,.30,.075),rough=.68,metal=.15);water=g.material('ShallowStream',(.025,.10,.12),rough=.34);groups={}
def mesh(n,v,f,m):o=g.mesh(n,v,f,m);groups.setdefault(cur,[]).append(o)
def tube(n,p,r):o=g.tube(n,p,[r]*len(p),gold,segments=6);groups.setdefault(cur,[]).append(o)
cur='GoldenWebCrossing'
for y in [-.55+i*.11 for i in range(11)]:tube('Woven load line',[(-1+i*.1,y,.08+.08*math.sin(i/20*math.pi))for i in range(21)],.018)
for x in [-1+i*.1 for i in range(21)]:tube('Cross weave',[(x,-.6,.08+.08*math.sin((x+1)/2*math.pi)),(x,.6,.08+.08*math.sin((x+1)/2*math.pi))],.014)
for y in [-.62,.62]:
 for x in [-1.,1.]:tube('Anchor stanchion',[(x,y,0),(x,y,1.05)],.035)
 tube('Upper rail',[(-1+i*.1,y,.95-.15*math.sin(i/20*math.pi))for i in range(21)],.025)
 for x in [-1+i*.2 for i in range(11)]:tube('Safety web',[(x,y,.10),(x,y,.95-.15*math.sin((x+1)/2*math.pi))],.012)
cur='SanctuaryStream';mesh('Opaque shallow stream',[(-.72,-5,.012),(.72,-5,.012),(.72,5,.012),(-.72,5,.012)],[(0,1,2,3)],water)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'SanctuaryCrossing.blend'));exports=[]
for name,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
 p=out/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(p),use_selection=True,export_format='GLB',export_animations=False);raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);d['asset'].pop('generator',None);b=json.dumps(d,separators=(',',':')).encode();b+=b' '*((-len(b))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(b)+len(tail))+struct.pack('<II',len(b),0x4e4f534a)+b+tail);exports.append({'name':name,'file':p.name,'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(out/'source-status.json').write_text(json.dumps({'exports':exports,'scene_sha256':hashlib.sha256((out/'SanctuaryCrossing.blend').read_bytes()).hexdigest(),'units':'metres','state':'Always visible static crossing; collision enabled with static deck. No mission unlock/flight/world bypass. Stream is shallow opaque surface over retained ground.','creative_approved':False},indent=2)+'\n')
