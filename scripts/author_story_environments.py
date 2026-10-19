"""Original editable market and sanctuary modules; draft art, no asset downloads."""
import bpy,math,random,json,hashlib,sys,struct
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));import character_mesh_tools as g
OUT=Path(sys.argv[sys.argv.index('--')+1]).resolve()
if OUT.exists():raise RuntimeError('Preserve previous environment revision')
OUT.mkdir(parents=True);bpy.ops.wm.read_factory_settings(use_empty=True);s=g.scene=bpy.context.scene;g.parts=[];g.binds={};g.joints={}
s.unit_settings.system='METRIC';s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=32;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('Daylight');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
mat=g.material;wood=mat('WeatheredWood',(.15,.065,.025),rough=.93);earth=mat('OchreEarth',(.31,.16,.065),rough=.98);plaster=mat('WarmPlaster',(.52,.32,.15),rough=.95);indigo=mat('IndigoTextile',(.018,.047,.115),rough=.95);gold=mat('OchreTextile',(.49,.23,.055),rough=.95);green=mat('LeafGreen',(.045,.11,.027),rough=.95);bark=mat('TreeBark',(.065,.035,.017),rough=.98);stone=mat('RiverStone',(.17,.19,.15),rough=.98);water=mat('RiverWater',(.025,.10,.12),rough=.24);fruit=mat('Produce',(.52,.21,.035),rough=.8)
rng=random.Random(90512);groups={}
def box(name,c,d,m,group):
 x,y,z=c;a,b,h=[v*.5 for v in d];verts=[(x+i*a,y+j*b,z+k*h) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 o=g.mesh(name,verts,faces,m);o['module']=group;groups.setdefault(group,[]).append(o);return o
def oval(name,c,d,m,group):
 o=g.oval(name,c,d,m,None);o['module']=group;groups.setdefault(group,[]).append(o);return o
def tube(name,pts,r,m,group):
 o=g.tube(name,pts,r,m);o['module']=group;groups.setdefault(group,[]).append(o);return o
# Matches existing mission coordinate lanes; facades deliberately outside route corridor.
for side in [-1,1]:
 for i in range(5):
  x=-17+i*7;y=side*15
  box('AdobeFacade', (x,y,2.3),(6,3,4.6),plaster,'MarketArchitecture')
  box('TimberLintel',(x,y-side*1.55,3.25),(2,.15,.18),wood,'MarketArchitecture')
  for j in [-1,1]:box('Doorframe',(x+j*.85,y-side*1.55,1.55),(.12,.16,3.2),wood,'MarketArchitecture')
  box('DoorInset',(x,y-side*1.57,1.5),(1.5,.12,3),wood,'MarketArchitecture')
  for z in [.5,1.4,2.4,3.5]:
   for j in range(8):box('MudBrickLine',(x-2.8+j*.8,y-side*1.51,z),(.69,.025,.025),earth,'MarketArchitecture')
  for j in range(11):box('RoofBeam',(x-2.9+j*.58,y,4.65),(.13,3.7,.18),wood,'MarketArchitecture')
for row,y in enumerate([-8,10.5]):
 for i,x in enumerate([-10.5,-6.5,-2.5,1.5]):
  for dx in [-1.25,1.25]:
   for dy in [-.75,.75]:tube('StallPost',[(x+dx,y+dy,0),(x+dx,y+dy,2.65)],[.045,.045],wood,'MarketStalls')
  for j in range(7):box('CounterPlank',(x-1.18+j*.39,y,.95),(.36,1.4,.10),wood,'MarketStalls')
  # Real sagged textile canopy grid, source topology retained.
  verts=[];faces=[];cols=12;rows=8
  for a in range(rows):
   v=a/(rows-1)
   for b in range(cols):
    u=b/(cols-1);verts.append((x+(u-.5)*2.9,y+(v-.5)*1.9,2.65-.16*math.sin(u*math.pi)+.05*math.cos(v*math.pi*8)))
  for a in range(rows-1):
   for b in range(cols-1):k=a*cols+b;faces.append((k,k+1,k+cols+1,k+cols))
  o=g.mesh('WovenCanopy',verts,faces,indigo if (i+row)%2 else gold);o['module']='MarketStalls';groups.setdefault('MarketStalls',[]).append(o)
  for j in range(4):
   bx=x-.85+j*.55
   # Pottery is a lathed vessel with interior lip, not a primitive cube.
   rings=[(bx,y,.99,.16,.16),(bx,y,1.04,.20,.20),(bx,y,1.25,.22,.22),(bx,y,1.36,.13,.13),(bx,y,1.38,.12,.12),(bx,y,1.35,.10,.10)]
   o=g.loft('PotteryVessel',rings,earth,segments=20);o['module']='MarketWares';groups.setdefault('MarketWares',[]).append(o)
   for k in range(3):oval('Produce',(bx+rng.uniform(-.12,.12),y+rng.uniform(-.12,.12),1.43),(.065,.065,.065),fruit,'MarketWares')
for i in range(36):
 x=17.5+(i%6)*.45;y=-7+(i//6)*.95
 box('DockPlank',(x,y,.12),(.42,.92,.16),wood,'RiverDock')
for x in [17.5,20]:
 for y in [-7,-2]:tube('DockPile',[(x,y,-1),(x,y,.65)],[.12,.12],wood,'RiverDock')
box('RiverSurface',(26,0,-.15),(10,40,.05),water,'RiverDock')
# Separate sanctuary scene module anchored at origin for its own level.
for i in range(14):
 a=i*2*math.pi/14;r=7+rng.uniform(-1,1);x,y=r*math.cos(a),r*math.sin(a);h=rng.uniform(6,9)
 tube('AncientTrunk',[(x,y,0),(x+.2,y,.7),(x-.15,y+.1,h*.5),(x+.3,y,h)],[.60,.46,.30,.12],bark,'SanctuaryTrees')
 for j in range(5):
  b=a+j*math.pi*.4;dx,dy=math.cos(b),math.sin(b)
  tube('ButtressRoot',[(x+dx*1.8,y+dy*1.8,.05),(x+dx*.75,y+dy*.75,.22),(x,y,1.4)],[.06,.18,.25],bark,'SanctuaryTrees')
  tube('TreeBranch',[(x,y,h*.65),(x+dx*1.3,y+dy*1.3,h*.8),(x+dx*2,y+dy*2,h*.83)],[.20,.11,.025],bark,'SanctuaryTrees')
  oval('CanopyCluster',(x+dx*1.5,y+dy*1.5,h*.85),(1.7,1.4,.8),green,'SanctuaryFoliage')
for i in range(80):
 a=rng.uniform(0,2*math.pi);r=rng.uniform(4.5,9);x,y=r*math.cos(a),r*math.sin(a)
 oval('MossStone',(x,y,.10),(rng.uniform(.15,.5),rng.uniform(.12,.4),rng.uniform(.1,.25)),stone,'SanctuaryGround')
 for j in range(4):
  b=j*math.pi*.5
  tube('FernFrond',[(x,y,.05),(x+.18*math.cos(b),y+.18*math.sin(b),.38),(x+.45*math.cos(b),y+.45*math.sin(b),.28)],[.025,.04,.005],green,'SanctuaryFoliage')
# Ringed story stone/podium in clearing.
for i in range(10):
 a=i*math.pi/5;oval('StoryStone',(2*math.cos(a),2*math.sin(a),.14),(.38,.27,.15),stone,'SanctuaryGround')
for name,loc,power in [('Sun',(-10,-10,15),2500),('Fill',(5,-5,8),1300)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.size=8;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;g.aim(o,(0,0,1))
d=bpy.data.cameras.new('MarketCamera');cam=bpy.data.objects.new('MarketCamera',d);s.collection.objects.link(cam);cam.location=(22,-30,15);g.aim(cam,(0,0,1));s.camera=cam
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'MarketAndSanctuary.blend'))
exports=[]
for group,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for o in objects:
  c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.select_set(True);copies.append(c)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();joined=bpy.context.object;joined.name='SM_'+group
 path=OUT/(group+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_animations=False)
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);payload=json.dumps(doc,separators=(',',':')).encode();payload+=b' '*((-len(payload))%4);tail=raw[20+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(tail))+struct.pack('<II',len(payload),0x4e4f534a)+payload+tail)
 exports.append({'group':group,'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'vertices':len(joined.data.vertices),'parts':len(objects)})
 bpy.data.objects.remove(joined,do_unlink=True)
for o in g.parts:o.hide_render=o['module'].startswith('Sanctuary')
s.render.filepath=str(OUT/'Market_beauty.png');bpy.ops.render.render(write_still=True)
for o in g.parts:o.hide_render=not o['module'].startswith('Sanctuary')
cam.location=(11,-14,8);g.aim(cam,(0,0,2));s.render.filepath=str(OUT/'Sanctuary_beauty.png');bpy.ops.render.render(write_still=True)
(OUT/'source-status.json').write_text(json.dumps({'status':'AUTHORED_ENVIRONMENT_DRAFT','creative_approved':False,'collision_reviewed':False,'units':'metres','scene_sha256':hashlib.sha256((OUT/'MarketAndSanctuary.blend').read_bytes()).hexdigest(),'exports':exports,'layout':'Market module aligns original greybox streets; sanctuary independent clearing','limitations':['Dynamic lighting draft, no baked/mobile qualification','Individual source props editable; grouped native rendering modules','Gameplay collisions and routes require native qualification']},indent=2)+'\n')
