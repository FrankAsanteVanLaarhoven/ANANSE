"""Editable original route scenery, conventional geometry; no downloaded assets."""
import bpy,math,random,json,hashlib,struct,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'SourceArt/Environments/MarketSanctuary/Route_v001';assert not OUT.exists();OUT.mkdir(parents=True)
sys.path.insert(0,str(ROOT/'scripts'));import character_mesh_tools as g
bpy.ops.wm.read_factory_settings(use_empty=True);s=g.scene=bpy.context.scene;g.parts=[];g.binds={};g.joints={};s.unit_settings.system='METRIC';s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=32
s.world=bpy.data.worlds.new('NeutralDay');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
mats={n:g.material(n,c,rough=r,metal=m)for n,c,r,m in [('Plaster',(.48,.28,.13),.93,0),('Wood',(.14,.062,.027),.88,0),('Indigo',(.025,.06,.14),.9,0),('Ochre',(.55,.26,.07),.9,0),('Clay',(.34,.11,.045),.9,0),('Brass',(.44,.25,.08),.45,.65),('Bark',(.085,.053,.027),.98,0),('Stone',(.18,.20,.15),.96,0),('Leaf',(.055,.16,.038),.94,0),('Water',(.028,.095,.11),.32,0)]}
groups={};cur=None

def put(o):
 groups.setdefault(cur,[]).append(o);o['module']=cur;return o

def box(n,p,d,mat='Wood',b=.015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.scale=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[mat])
 if b:
  mod=o.modifiers.new('Worn arris','BEVEL');mod.width=min(b,min(d)*.2);mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
 return put(o)
def tube(n,pts,rs,mat='Wood'):return put(g.tube(n,pts,rs,mats[mat],segments=10))
def loft(n,rings,mat='Clay',segments=24):return put(g.loft(n,rings,mats[mat],segments=segments))
# Six-metre facade with recessed timber panels, arch relief, coping and projecting rafters.
cur='MarketFacade'
box('Lime rendered wall',(0,0,2.25),(6,1.8,4.5),'Plaster',.055)
for z in [.24,.52]:box('Stone plinth',(0,-.925,z),(6.08,.12,.23),'Stone',.025)
for x in [-2.6,2.6]:box('Corner pilaster',(x,-.97,2.25),(.24,.18,4.5),'Plaster',.025)
box('Recessed door',(0,-.925,1.35),(1.5,.06,2.6),'Wood')
for x in [-.84,.84]:box('Door jamb',(x,-1.0,1.4),(.15,.18,2.8))
box('Door lintel',(0,-1.0,2.83),(1.9,.2,.2))
for i in range(12):
 a=i*math.pi/11;p=(.85*math.cos(a),-1.04,2.8+.5*math.sin(a));o=box('Arch voussoir',p,(.25,.18,.22),'Stone');o.rotation_euler.y=-a
for x in [-1.9,1.9]:
 box('Window surround',(x,-.99,2.6),(1.0,.18,1.35),'Stone')
 for j in range(5):box('Window louvre',(x,-1.10,2.1+j*.23),(.8,.06,.12))
for x in [-2.8+i*.56 for i in range(11)]:box('Exposed rafter',(x,0,4.55),(.15,2.2,.17))
box('Raised parapet',(0,0,4.78),(6.12,1.96,.25),'Plaster',.035)
for x in [-.55,.55]:box('Door brass hinge',(x,-1.05,1.45),(.04,.03,.28),'Brass',.003)
# Standalone stall: solid cloth surfaces, no transparency, bounded sag topology.
cur='MarketStall'
for x in [-1.2,1.2]:
 for y in [-.7,.7]:tube('Carved upright',[(x,y,0),(x,y,2.7)],[.055,.045])
for j in range(8):box('Counter board',(-1.15+j*.33,0,1.0),(.30,1.48,.09))
for x in [-1.2,1.2]:box('Cross brace',(x,0,.75),(.1,1.5,.12))
for z in [.2,.4,.6,.8]:box('Front counter panel',(0,-.74,z),(2.48,.06,.16))
v=[];f=[];nx=17;ny=9
for j in range(ny):
 for i in range(nx):
  u=i/(nx-1);w=j/(ny-1);v.append(((u-.5)*2.85,(w-.5)*1.9,2.7-.14*math.sin(math.pi*u)+.035*math.cos(w*math.pi*8)))
for j in range(ny-1):
 for i in range(nx-1):k=j*nx+i;f.append((k,k+1,k+nx+1,k+nx))
put(g.mesh('Woven canopy',v,f,mats['Indigo']))
for y in [-.96,.96]:
 for i in range(12):box('Canopy edge stitch',(-1.29+i*.235,y,2.63),(.12,.014,.035),'Ochre',.002)
# Distinct editable hollow pots: actual inner wall, rolled rim, foot.
cur='PotterySet'
for x,h in [(-.43,.44),(0,.66),(.43,.35)]:
 rings=[(x,0,0,.14,.14),(x,0,.04,.18,.18),(x,0,h*.4,.23,.23),(x,0,h*.78,.19,.19),(x,0,h,.12,.12),(x,0,h+.018,.125,.125),(x,0,h+.018,.098,.098),(x,0,h*.85,.095,.095),(x,0,h*.5,.16,.16),(x,0,.07,.12,.12)]
 loft('Coiled earthenware',rings)
 for z in [.1,h*.65]:
  rr=.18 if z==.1 else .20
  pts=[(x+rr*math.cos(i*math.tau/32),rr*math.sin(i*math.tau/32),z)for i in range(33)];tube('Incised rim',pts,[.008]*33,'Ochre')
cur='DockSection'
for i in range(10):box('Dock plank',(-1.4+i*.31,0,.08),(.29,2,.16))
for x in [-1.25,1.25]:
 for y in [-.85,.85]:tube('Driven pile',[(x,y,-1),(x,y,.62)],[.13,.105]);tube('Rope wrap',[(x+.12*math.cos(i*.5),y+.12*math.sin(i*.5),.3+i*.007)for i in range(38)],[.015]*38,'Ochre')
cur='RiverSurface';box('Opaque river',(0,0,-.04),(10,40,.06),'Water',0)
# Larger root silhouette, branch collars and leaves authored as separate instances in engine.
cur='SanctuaryTree'
tube('Ancient bole',[(0,0,0),(.12,0,1.2),(-.1,.05,3.1),(.20,0,5.1),(.3,.1,7.3)],[.68,.54,.42,.3,.12],'Bark')
for j in range(7):
 a=j*math.tau/7;dx,dy=math.cos(a),math.sin(a)
 tube('Buttress root',[(dx*2,dy*2,.02),(dx*1.0,dy*1.0,.22),(0,0,1.8)],[.06,.20,.32],'Bark')
 tube('Crown branch',[(0,0,4.3),(dx*1.1,dy*1.1,5.8),(dx*2.3,dy*2.3,6.7)],[.25,.15,.035],'Bark')
 for k in range(5):
  x=dx*(1.2+k*.3);y=dy*(1.2+k*.3);z=6.0+k*.14
  # Actual broad leaf surfaces; solid geometry, not translucent overdraw cards.
  put(g.mesh('Crown leaves',[(x-.6,y,z),(x,y-.5,z+.18),(x+.7,y,z),(x,y+.5,z+.10),(x,y,z+.28)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],mats['Leaf']))
cur='SanctuaryRock'
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1);o=bpy.context.object;o.name='Weathered river boulder';o.scale=(.65,.45,.3);o.location.z=.20;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats['Stone']);put(o)
cur='ForestFern'
for j in range(7):
 a=j*math.tau/7;dx,dy=math.cos(a),math.sin(a);tube('Fern rachis',[(0,0,0),(dx*.25,dy*.25,.6),(dx*.65,dy*.65,.4)],[.012,.01,.002],'Leaf')
 for k in range(5):
  t=.15+k*.15;x,y=dx*t,dy*t;z=.5*math.sin(t/.8*math.pi);w=.18*(1-t)
  put(g.mesh('Fern pinnae',[(x,y,z),(x-dy*w,y+dx*w,z+.06),(x+dx*.10,y+dy*.10,z+.01),(x+dy*w,y-dx*w,z+.06)],[(0,1,2),(0,2,3)],mats['Leaf']))
# Export each module with an origin at zero, UV0 and separate nonoverlap UV1 target for native bake.
for objects in groups.values():
 for o in objects:
  bpy.context.view_layer.objects.active=o;o.select_set(True)
  if not o.data.uv_layers:
   bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
  o.select_set(False)
exports=[]
for name,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for o in objects:
  c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.select_set(True);copies.append(c)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 # Combined lightmap UVs are packed after joining, not overlapping per-part islands.
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
 path=OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_animations=False)
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);d['asset'].pop('generator',None);payload=json.dumps(d,separators=(',',':')).encode();payload+=b' '*((-len(payload))%4);tail=raw[20+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(tail))+struct.pack('<II',len(payload),0x4e4f534a)+payload+tail)
 exports.append(dict(name=name,file=path.name,triangles=sum(len(p.vertices)-2 for p in o.data.polygons),materials=len(o.data.materials),sha256=hashlib.sha256(path.read_bytes()).hexdigest()));bpy.data.objects.remove(o,do_unlink=True)
# Review scene: copies arranged without modifying module export origins.
for objects in groups.values():
 for o in objects:o.hide_render=True
for name,offset in [('MarketFacade',(0,2,0)),('MarketStall',(0,-1,0)),('PotterySet',(0,-1,1.05))]:
 for o in groups[name]:
  c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.location+=Vector(offset);c.hide_render=False
for name,loc,power in [('Key',(2,-6,8),2200),('Fill',(-4,-3,5),1500)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.size=7;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;g.aim(o,(0,0,1.5))
d=bpy.data.cameras.new('Module review');cam=bpy.data.objects.new('Module review',d);s.collection.objects.link(cam);cam.location=(8,-12,8);g.aim(cam,(0,0,2));s.camera=cam;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'RouteEnvironment.blend'));s.render.filepath=str(OUT/'market_modules.png');bpy.ops.render.render(write_still=True)
(OUT/'source-status.json').write_text(json.dumps(dict(status='AUTHORED_PENDING_NATIVE_AND_CREATIVE_REVIEW',scene_sha256=hashlib.sha256((OUT/'RouteEnvironment.blend').read_bytes()).hexdigest(),units='metres; native cm probe required',exports=exports,creative_approved=False,mobile_qualified=False),indent=2)+'\n');print('ROUTE_ENVIRONMENT_SAVED',len(exports))
