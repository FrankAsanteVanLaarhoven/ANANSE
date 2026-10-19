"""Original editable benchmark scenery. Metres; conventional opaque geometry."""
import bpy,math,random,json,hashlib,struct,sys,numpy as np
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'SourceArt/Environments/MarketSanctuary/HeroCells_v001';assert not OUT.exists();OUT.mkdir(parents=True)
sys.path.insert(0,str(ROOT/'scripts'));import character_mesh_tools as g
bpy.ops.wm.read_factory_settings(use_empty=True);g.scene=bpy.context.scene;g.parts=[];g.binds={};g.joints={};scene=bpy.context.scene;scene.unit_settings.system='METRIC';rng=random.Random(171026)
# Authored periodic grain maps: small shared atlases, no transparency or external imagery.
N=512;yy,xx=np.mgrid[:N,:N];u=xx/N;v=yy/N;nr=np.random.default_rng(171026)
def noise(k):
 a=nr.random((k,k));x=u*k;y=v*k;i=x.astype(int);j=y.astype(int);fx=x-i;fy=y-j;fx=fx*fx*(3-2*fx);fy=fy*fy*(3-2*fy)
 return (a[j%k,i%k]*(1-fx)+a[j%k,(i+1)%k]*fx)*(1-fy)+(a[(j+1)%k,i%k]*(1-fx)+a[(j+1)%k,(i+1)%k]*fx)*fy
mats={};surfaces=[]
spec=[('Lime',(.68,.51,.31),.91,0),('Timber',(.22,.105,.045),.79,0),('Indigo',(.035,.12,.25),.86,0),('Brass',(.58,.37,.12),.38,.72),('Stone',(.32,.35,.28),.96,0),('Bark',(.16,.10,.052),.98,0),('Leaf',(.09,.23,.065),.87,0),('Jade',(.055,.24,.21),.77,0),('Clay',(.56,.21,.10),.91,0),('Water',(.055,.19,.22),.29,.12),('GoldThread',(.73,.46,.12),.4,.25)]
for name,base,rough,metal in spec:
 n=.45*noise(5)+.3*noise(21)+.25*noise(96)
 if name in ['Timber','Bark']:n=.4*n+.6*(.5+.5*np.sin(u*math.tau*25+.9*np.sin(v*math.tau)+n*3))
 if name=='Indigo':n=.45*n+.3*(np.sin(u*math.tau*64)*np.sin(v*math.tau*64))+.25*(np.sin((u+v)*math.tau*8)>.7)
 if name=='Leaf':n=.5*n+.3*(1-np.abs(u-.5)*2)+.2*np.sin(v*math.tau*18)
 rgb=np.clip(np.array(base)[None,None,:]*(.65+.55*n[...,None]),0,1)
 image=bpy.data.images.new(name+'_Albedo',width=N,height=N,alpha=True);image.pixels.foreach_set(np.dstack([rgb,np.ones((N,N))]).astype('float32').ravel());image.filepath_raw=str(OUT/(name+'_Albedo.png'));image.file_format='PNG';image.save()
 m=g.material(name,base,rough=rough,metal=metal);node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;m.node_tree.links.new(node.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);mats[name]=m;surfaces.append({'name':name,'roughness':rough,'metallic':metal,'texture':name+'_Albedo.png'})
groups={};cur=''
def put(o):groups.setdefault(cur,[]).append(o);o['module']=cur;return o
def box(n,p,d,mat='Timber',bevel=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.scale=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[mat])
 if bevel:
  b=o.modifiers.new('Rounded worn arris','BEVEL');b.width=min(bevel,min(d)*.22);b.segments=2;bpy.ops.object.modifier_apply(modifier=b.name)
 return put(o)
def tube(n,pts,rs,mat='Timber',segments=10):return put(g.tube(n,pts,rs,mats[mat],segments=segments))
def rock(n,p,d,mat='Stone',sub=2):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=p);o=bpy.context.object;o.name=n
 for vert in o.data.vertices:vert.co*=rng.uniform(.88,1.13)
 o.scale=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[mat]);return put(o)
def leaf(p,ang,length,width,mat='Leaf'):
 # Curved ribbed leaf, true opaque surface with small silhouette serrations.
 verts=[]
 for i in range(9):
  t=i/8;w=width*math.sin(math.pi*t)**.8
  for side in [-1,0,1]:
   x=t*length;y=side*w;z=.18*math.sin(math.pi*t)*length+.035*(1-abs(side));verts.append((p[0]+x*math.cos(ang)-y*math.sin(ang),p[1]+x*math.sin(ang)+y*math.cos(ang),p[2]+z))
 faces=[]
 for i in range(8):
  for j in range(2):a=i*3+j;faces.append((a,a+1,a+4,a+3))
 return put(g.mesh('Curved vein leaf',verts,faces,mats[mat]))
def arch(n,x,y,z,w,h,mat='Stone'):
 for i in range(19):
  a=i*math.pi/18;o=box(n,(x+w*math.cos(a),y,z+h*math.sin(a)),(.16,.22,.20),mat,.025);o.rotation_euler.y=-a
# Layered market frontages, asymmetric upper volume and cool shutter relief.
cur='Frontage'
box('Warm lime upper storey',(0,0,3.9),(5.8,.38,1.8),'Lime',.05)
for x in [-2.85,2.85]:
 box('Stepped buttress',(x,-.12,1.6),(.42,.65,3.2),'Lime',.06);box('Stone buttress foot',(x,-.2,.25),(.60,.8,.5),'Stone')
for z in [.28,3.05,4.85]:box('Projecting string course',(0,-.22,z),(6,.5,.16),'Stone')
for x in [-1.75,1.75]:
 box('Recessed shutter',(x,-.25,3.9),(1.15,.12,1.1),'Jade')
 for zz in [3.55,3.72,3.89,4.06,4.23]:box('Window louvre',(x,-.34,zz),(1.06,.10,.08),'Timber',.01)
 for dx in [-.65,.65]:box('Window jamb',(x+dx,-.3,3.9),(.12,.16,1.35),'Lime')
 box('Deep window sill',(x,-.4,3.24),(1.5,.42,.15),'Stone')
box('Central balcony deck',(0,-.7,3.05),(2.3,1.5,.18),'Timber')
for x in [-1.1+i*.22 for i in range(11)]:box('Balcony baluster',(x,-1.35,3.48),(.055,.055,.7),'Timber',.008)
box('Balcony handrail',(0,-1.35,3.87),(2.4,.10,.09),'Timber')
for x in [-1,1]:tube('Angled balcony bracket',[(x,-.25,2.2),(x,-1.22,3.0)],[.09,.07])
for i in range(19):box('Roof cap tile',(-2.9+i*.32,0,5.04),(.30,.68,.14),'Clay')
for x in [-2.6,-1.3,0,1.3,2.6]:box('Roof eave rafter',(x,-.4,4.72),(.14,1.0,.15),'Timber')
# Original story-archive facade; no new solid doorway across existing interaction route.
cur='ArchivePortal'
for x in [-1.9,1.9]:
 box('Archive terraced pier',(x,0,1.8),(.65,.7,3.6),'Lime',.07)
 for z in [.15,.6,2.6,3.5]:box('Incised pier band',(x,-.4,z),(.79,.16,.14),'Stone')
 for k in range(5):rock('Story brass inset',(x,-.5,1+k*.28),(.07,.025,.09),'Brass',1)
arch('Archive carved arch',0,-.1,2.65,1.7,1.1)
box('Archive raised crown',(0,.06,3.9),(4.5,.85,.28),'Lime')
box('Archive indigo frieze',(0,-.44,3.88),(3.45,.055,.18),'Indigo',.005)
for x in [-1.4+i*.28 for i in range(11)]:o=box('Frieze woven diamond',(x,-.49,3.88),(.11,.035,.11),'Brass',.005);o.rotation_euler.y=math.pi/4
# Timber/cloth/pottery market kit. Count controlled by instancing.
cur='MarketDressing'
for x in [-.75,.75]:
 for y in [-.45,.45]:box('Basket crate frame',(x,y,.4),(.08,.08,.8))
for z in [.12,.29,.46,.63,.80]:
 for y in [-.48,.48]:box('Crate slat',(0,y,z),(1.6,.055,.12))
for x in [-.75,.75]:box('Crate end',(x,0,.45),(.07,.9,.68))
for x,h in [(-.5,.46),(0,.65),(.48,.4)]:
 put(g.loft('Earthen storage vessel',[(x,0,.84,.14,.14),(x,0,1.,.23,.23),(x,0,.84+h*.75,.24,.24),(x,0,.84+h,.11,.11),(x,0,.86+h,.12,.12),(x,0,.86+h,.085,.085),(x,0,.90,.10,.10)],mats['Clay'],segments=24))
for i in range(4):box('Folded indigo cloth',(.15,-.3,1+i*.035),(.8,.32,.03),'Indigo',.008)
cur='GroundTreatment'
for i in range(12):
 for j in range(5):
  if rng.random()<.12:continue
  box('Irregular worn paving',((i-5.5)*.33,(j-2)*.35,.012+rng.uniform(-.003,.003)),(.30+rng.uniform(-.025,.025),.32,.025),'Stone',.018)
cur='CanopySwag'
for offset in [0,.7]:
 pts=[(-2+i*.2,offset,3.1-.4*math.sin(i/20*math.pi))for i in range(21)];tube('Hanging cord',pts,[.014]*21,'Timber',6)
 for i in range(20):
  x=-2+i*.2;z=3.1-.4*math.sin(i/20*math.pi);put(g.mesh('Indigo pennant',[(x,offset,z),(x+.17,offset,z-.01),(x+.085,offset,z-.31)],[(0,1,2)],mats['Indigo']))
# River tableau behind the retained collision boundary, rendered as a visible dock scene.
cur='Waterfront'
for i in range(22):box('Boardwalk worn plank',((i-10.5)*.25,0,.12),(.23,2.3,.18))
for x in [-2.5,0,2.5]:
 for y in [-.9,.9]:
  tube('Dock pile',[(x,y,-1),(x,y,1.1)],[.14,.11]);tube('Mooring rope',[(x+.13*math.cos(i*.4),y+.13*math.sin(i*.4),.55+i*.005)for i in range(70)],[.016]*70,'Timber',6)
# Hollow dugout hull, frames, thwarts, independent mooring rope.
cur='Boat'
verts=[]
for z,r in [(0,.65),(.65,1),(.65,.88),(.14,.50)]:
 for i in range(40):a=i*math.tau/40;verts.append((2.9*math.cos(a),r*math.sin(a),z+.2*abs(math.cos(a))**4))
faces=[]
for k in range(3):
 for i in range(40):faces.append((k*40+i,k*40+(i+1)%40,(k+1)*40+(i+1)%40,(k+1)*40+i))
put(g.mesh('Carved hollow river hull',verts,faces,mats['Timber']))
for x in [-1.5,0,1.5]:box('Boat thwart',(x,0,.56),(.24,1.55,.10))
tube('Curved bow rope',[(2.8,0,.55),(3.3,0,.7),(3.6,.4,1.1),(4,.8,1.4)],[.025]*4,'Timber',8)
cur='RiverWater'
verts=[]
for j in range(33):
 for i in range(17):verts.append(((i-8)*.5,(j-16)*.5,.018*math.sin(i*2.3+j*.8)))
faces=[(j*17+i,j*17+i+1,(j+1)*17+i+1,(j+1)*17+i)for j in range(32)for i in range(16)];put(g.mesh('Rippled opaque river',verts,faces,mats['Water']))
for j in range(18):tube('Subtle reflected current',[(-3+i*.4,-7+j*.8,.03+.012*math.sin(i+j))for i in range(16)],[.008]*16,'Jade',4)
# Hero trees: asymmetric taper, fluted buttresses, twisting secondary branches.
cur='HeroTree'
tube('Fluted ancient trunk',[(0,0,-.15),(.08,.05,.8),(-.10,.12,2.4),(.22,.05,4.4),(.05,.25,6.6),(.45,.3,8.8)],[.72,.68,.52,.40,.26,.10],'Bark',20)
for k in range(9):
 a=k*math.tau/9;dx,dy=math.cos(a),math.sin(a)
 tube('Twisting buttress',[(dx*2.4,dy*2.4,.01),(dx*1.55,dy*1.55,.12),(dx*.8,dy*.8,.55),(dx*.35,dy*.35,2.2)],[.035,.16,.25,.25],'Bark',10)
 tube('Bark flute',[(dx*.67,dy*.67,.15),(dx*.62+.08,dy*.62,1.3),(dx*.48-.10,dy*.48,2.9),(dx*.36+.18,dy*.36,4.3)],[.055,.07,.05,.025],'Bark',7)
 a+=.2;dx,dy=math.cos(a),math.sin(a);start=4.0+(k%3)*.5
 tube('Asymmetric scaffold',[(.1,0,start),(dx*1.3,dy*1.3,start+.9),(dx*2.5,dy*2.5,start+1.4),(dx*3.2,dy*3.2,start+2.1)],[.23,.17,.09,.025],'Bark',10)
 for branch in [-1,1]:
  aa=a+branch*.5;end=(dx*2.4+math.cos(aa)*1.25,dy*2.4+math.sin(aa)*1.25,start+2.1)
  tube('Crown fork',[(dx*1.8,dy*1.8,start+1.1),end],[.09,.015],'Bark',8)
  for q in range(8):
   angle=aa+q*math.tau/8;leaf((end[0]+math.cos(angle)*rng.uniform(.1,.6),end[1]+math.sin(angle)*rng.uniform(.1,.6),end[2]+rng.uniform(-.1,.4)),angle,rng.uniform(.65,1.2),.22)
cur='Understory'
for stem in range(8):
 a=stem*math.tau/8;dx,dy=math.cos(a),math.sin(a)
 for k in range(7):
  t=.12+k*.1;p=(dx*t,dy*t,.6*math.sin(t*2.1));leaf(p,a+1.15,.22*(1-t)+.08,.045);leaf(p,a-1.15,.22*(1-t)+.08,.045)
for a in [.4,2.4,4.5]:leaf((0,0,.05),a,.85,.17,'Jade')
cur='SanctuaryMarker'
rock('Foundation stone',(0,0,.15),(1.35,.85,.25),'Stone',2)
box('Story upright',(0,0,1.25),(1.15,.38,2.1),'Stone',.15)
for x in [-.44,.44]:tube('Golden story border',[(x,-.23,.45),(x,-.23,2.08)],[.018,.018],'GoldThread',8)
for k in range(7):
 z=.65+k*.19;pts=[(-.3+i*.06,-.25,z+.05*math.sin(i*math.pi/2))for i in range(11)];tube('Woven story inscription',pts,[.016]*11,'GoldThread',6)
rock('Sanctuary crown',(0,0,2.38),(.48,.32,.34),'Stone',2)
for x in [-1,1]:tube('Root cradle',[(x*1.7,.1,.03),(x*.9,.1,.15),(x*.7,.1,1),(x*.48,.1,1.5)],[.07,.16,.12,.025],'Bark',10)
cur='WebLace'
# Deliberately organic web layers surrounding retained deck; no collision or new movement.
for k in range(9):
 y=-.56+k*.14;pts=[(-1+i*.1,y+.018*math.sin(i*.9+k),.13+.04*math.sin(i/20*math.pi)+.009*math.sin(k+i))for i in range(21)];tube('Tensioned golden warp',pts,[.008]*21,'GoldThread',5)
for side in [-1,1]:
 for h in [.3,.55,.9]:
  pts=[(-1+i*.1,side*.61,h-.12*math.sin(i/20*math.pi))for i in range(21)];tube('Catenary silk rail',pts,[.009]*21,'GoldThread',5)
 for i in range(13):
  x=-1+i/6;pts=[(x,side*.61,.13),(x+.07,side*.61,.40),(x-.05,side*.61,.70),(x,side*.61,.9)];tube('Irregular lattice silk',pts,[.007]*4,'GoldThread',5)
 for j in range(4):
  a=-1+j*.65;tube('Root attachment fan',[(a,side*.61,.7),(a+side*.3,side*.90,.9),(a+side*.45,side*1.1,.15)],[.012,.009,.005],'GoldThread',5)
cur='StreamBank'
for side in [-1,1]:
 for i in range(15):
  x=-3.5+i*.5;y=side*(.8+.13*math.sin(i*1.3));rock('Water-worn bank stone',(x,y,.06),(rng.uniform(.25,.4),.23,.12),'Stone',2)
  if i%2==0:leaf((x,y,.12),side*1.4,.5,.11)
cur='RockCluster'
for i in range(6):rock('Split mossy stone',(rng.uniform(-.8,.8),rng.uniform(-.5,.5),.08),(rng.uniform(.25,.6),rng.uniform(.25,.5),rng.uniform(.18,.35)),'Stone',2)
# Pack each module: material slots consolidated by name; conventional 3LOD in native import.
exports=[]
for name,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for o in objects:
  c=o.copy();c.data=o.data.copy();scene.collection.objects.link(c);c.select_set(True);copies.append(c)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
 path=OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_animations=False)
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);j['asset'].pop('generator',None);s=json.dumps(j,separators=(',',':')).encode();s+=b' '*(-len(s)%4);tail=b[20+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(s)+len(tail))+struct.pack('<II',len(s),0x4e4f534a)+s+tail)
 exports.append({'name':name,'file':path.name,'triangles':sum(len(f.vertices)-2 for f in o.data.polygons),'materials':len(o.data.materials),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});bpy.data.objects.remove(o,do_unlink=True)
# Editable original separate parts retained in named collections, not flattened source geometry.
for name,objects in groups.items():
 col=bpy.data.collections.new(name);scene.collection.children.link(col)
 for o in objects:
  for old in list(o.users_collection):old.objects.unlink(o)
  col.objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'HeroCells.blend'))
(OUT/'source-status.json').write_text(json.dumps({'creator':'Frank Asante Van Laarhoven','units':'metres','seed':171026,'source_scene':'HeroCells.blend','scene_sha256':hashlib.sha256((OUT/'HeroCells.blend').read_bytes()).hexdigest(),'exports':exports,'surfaces':surfaces,'creative_approved':False,'status':'AUTHORED_PENDING_NATIVE_REVIEW'},indent=2)+'\n')
print('HERO_CELLS_SAVED',len(exports))
