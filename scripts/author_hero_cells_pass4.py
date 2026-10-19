"""Bounded fourth visual revision: composed shore, stream, sanctuary and varied depth silhouettes."""
from pathlib import Path
p=Path(__file__).resolve().parent/'author_hero_cells.py';prefix=p.read_text().split('# Layered market frontages')[0].replace('HeroCells_v001','HeroCells_v004').replace('171026','184026');exec(compile(prefix,str(p),'exec'))
from mathutils import Vector
p=ROOT/'scripts/author_hero_cells_pass3.py';s=p.read_text();exec(s[s.index('def sweep('):s.index('# Three independently')])
# Additional quiet earthen surfaces; source and native reuse the same albedos where bound.
for name,base,rough in [('WetEarth',(.16,.13,.08),.75),('Moss',(.12,.20,.075),.95),('DistantBark',(.11,.18,.20),.95),('DistantLeaf',(.16,.25,.25),.93),('Sand',(.32,.28,.17),.9),('Shallows',(.065,.18,.17),.38)]:
 m=g.material(name,base,rough=rough);mats[name]=m;im=bpy.data.images.new(name+'_Albedo',width=N,height=N,alpha=True);n=.6*noise(7)+.4*noise(42);im.pixels.foreach_set(np.dstack([np.clip(np.array(base)[None,None,:]*(.8+.35*n[...,None]),0,1),np.ones((N,N))]).astype('float32').ravel());im.filepath_raw=str(OUT/(name+'_Albedo.png'));im.file_format='PNG';im.save();node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;m.node_tree.links.new(node.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);surfaces.append({'name':name,'roughness':rough,'metallic':0,'texture':name+'_Albedo.png'})
# Analytic gentle shore cross-sections instead of subdivision of a dense rippled plane.
def channel(name,length,width,river):
 global cur
 cur=name;count=161 if river else 65;vs=[];fs=[]
 def profile(x):return (.16*math.sin(x*.27)+.08*math.sin(x*.73),width*(1+.045*math.sin(x*.32)+.025*math.sin(x*.89))) if river else(.18*math.sin(x*.9)+.045*math.sin(x*2.1),width*(1+.15*math.sin(x*1.2)))
 for j in range(5):
  for i in range(count):
   x=-length/2+i*length/(count-1);centre,w=profile(x);vs.append((x,centre+(j/4*2-1)*w,.015+.004*math.sin(x*1.6+j)))
 for j in range(4):
  for i in range(count-1):a=j*count+i;fs.append((a,a+1,a+count+1,a+count))
 put(g.mesh('Upward water surface',vs,fs,mats['Water']))
 for side in [-1,1]:
  vs=[];fs=[]
  for i in range(count):
   x=-length/2+i*length/(count-1);c,w=profile(x)
   for d,z in [(-.2,.016),(.04,.018),(.25,.035),(.6,.07),(1.2,.10)]:vs.append((x,c+side*(w+d),z+.012*math.sin(x*.8)*max(0,d)))
  for i in range(count-1):
   for j in range(4):a=i*5+j;fs.append((a,a+1,a+6,a+5))
  put(g.mesh('Rounded wet sediment lip',vs,fs,mats['Sand'if river else'WetEarth']))
  for k in range(26 if river else 15):
   x=-length/2+(k+.3)*length/(26 if river else 15);c,w=profile(x);y=c+side*(w+.45)
   rock('Waterworn bank stone',(x,y,.06),(.18+rng.random()*.22,.13+rng.random()*.12,.08),'Stone',2)
   if k%3!=0:
    for q in range(4):leaf((x,y,.08),q*1.9+.3*k,.35+.1*q,.08)
channel('RiverReach',72,10,True);channel('StreamPools',8,.58,False)
cur='QuayApron'
# Rough bank/rubble-to-boardwalk transition behind retained dock collision, not a new route.
vs=[];fs=[]
for i in range(81):
 y=-15+i*.375;edge=.12*math.sin(y*.5)+.05*math.sin(y*1.3)
 for x,z in [(-.9,.05),(-.4,.04),(.05,.01),(.45,-.10),(.8,-.3)]:vs.append((x+edge,y,z))
for i in range(80):
 for j in range(4):a=i*5+j;fs.append((a,a+1,a+6,a+5))
put(g.mesh('Rounded riverbank apron',vs,fs,mats['WetEarth']))
for k in range(32):rock('Quay erosion stones',(.25+rng.uniform(-.2,.2),-14.5+k*.9,-.05),(.25,.22,.14),'Stone',2)
cur='DockLife'
for x in [-.6,.3]:
 put(g.loft('Staved dock barrel',[(x,0,.02,.24,.24),(x,0,.12,.30,.30),(x,0,.55,.32,.32),(x,0,.85,.26,.26)],mats['Timber'],segments=16))
 for z in [.15,.68]:tube('Barrel hoop',[(x+.305*math.cos(i*math.tau/24),.305*math.sin(i*math.tau/24),z)for i in range(25)],[.015]*25,'Brass',6)
for k in range(4):
 x=.7+k*.10;tube('Coiled mooring rope',[(x+.28*math.cos(i*math.tau/36),.7+.28*math.sin(i*math.tau/36),.04+k*.03)for i in range(37)],[.016]*37,'Timber',6)
box('Folded sail cloth',(-.3,.8,.12),(.7,.45,.18),'Indigo')
cur='VerandaCorner'
# An asymmetrical recessed stall frontage with warped awning and a basket-pottery display.
for x,h in [(-1.5,2.5),(1.2,2.8)]:sweep('Veranda shaped support',[(x,0,0),(x-.03,0,1.4),(x+.05,0,h)],[.06,.065,.05],'Timber',8,4)
put(g.mesh('Unequal woven awning',[(-1.7,-.8,2.3),(0,-.8,2.2),(1.5,-.8,2.5),(-1.7,.8,2.7),(0,.8,2.6),(1.5,.8,2.85)],[(0,1,4,3),(1,2,5,4)],mats['Jade']))
box('Goods bench',(-.2,.35,.55),(2.2,.65,.12),'Timber')
for x in [-1,.6]:box('Bench trestle',(x,.35,.27),(.12,.5,.55),'Timber')
for i in range(7):
 x=-1+i*.29;put(g.loft('Display pottery',[(x,.35,.63,.08,.08),(x,.35,.75,.13,.13),(x,.35,.90,.10,.10),(x,.35,.94,.065,.065)],mats['Clay'],segments=14))
for x in [-1.2,.9]:
 for k in range(6):box('Folded fabric stack',(x,-.1,.04+k*.035),(.55,.35,.03),'Indigo',.005)
# Three broad asymmetrical silhouettes: fewer visible vertical columns, deeper canopy overlap.
for variant in range(3):
 cur='LayeredGrove'+str(variant)
 for k in range(3):
  x=-6+k*5+rng.uniform(-1,1);y=rng.uniform(-2,2);h=9+rng.uniform(-1.5,3);lean=(-1 if k%2 else 1)*(1.5+variant*.4)
  sweep('Leaning distant bole',[(x,y,-.3),(x+.3,y,2.5),(x+lean*.7,y+.3,h*.6),(x+lean,y+.8,h)],[.5,.38,.22,.015],'DistantBark',sides=8,steps=5)
  for q in range(3):
   aa=q*2.3+variant;end=(x+lean+math.cos(aa)*3,y+math.sin(aa)*2.5,h-.7)
   sweep('Lateral distant bough',[(x+lean*.5,y,h*.5),(x+lean,y,h*.8),end],[.20,.12,.008],'DistantBark',sides=7,steps=4)
   # Broad opaque lobed crown formed from overlapping bent leaf silhouettes.
   for j in range(12):leaf((end[0]+rng.uniform(-1.4,1.4),end[1]+rng.uniform(-1,1),end[2]+rng.uniform(-.5,.5)),j*2.399+variant,2.2,.7,'DistantLeaf')
 for k in range(8):
  x=-7+k*1.8;y=rng.uniform(-1,1)
  for q in range(7):leaf((x,y,.05),q*2.4+variant,1.4,.45,'DistantLeaf')
cur='EcologyIsland'
for k in range(5):
 x,y=[(-.8,.2),(.1,.45),(.85,-.1),(-.3,-.45),(.7,.5)][k]
 for q in range(6):leaf((x,y,.03),q*math.tau/6+.2*k,.6+.1*(q%3),.20)
for k in range(25):leaf((rng.uniform(-1.2,1.2),rng.uniform(-.8,.8),.012),rng.random()*math.tau,.16,.065,'Timber'if k%2 else'Clay')
for k in range(5):rock('Soft moss bed',(rng.uniform(-1,1),rng.uniform(-.5,.5),.015),(.45,.3,.025),'Moss',2)
cur='SanctuaryReliquary'
# Proposed visual story marker: fractured stone, real relief bands and thread inlays, no new mechanic.
put(g.loft('Worn tilted story stone',[(0,0,0,.45,.22),(-.04,.02,.35,.42,.25),(.02,.05,1.1,.37,.24),(-.10,.02,1.9,.33,.22),(-.16,.04,2.6,.25,.18),(-.05,.02,2.8,.18,.13)],mats['Stone'],segments=10))
for k in range(7):
 z=.4+k*.28;sweep('Inlaid story thread',[(-.26,-.255,z),(-.14,-.27,z+.08),(0,-.27,z-.01),(.13,-.265,z+.09),(.25,-.25,z+.01)],[.012]*5,'GoldThread',6,3)
for k in range(6):rock('Marker basal stones',((k-2.5)*.34,.15,.04),(.29,.38,.10),'Stone',2)
cur='SanctuaryGarden'
for side in [-1,1]:
 sweep('Embracing old root',[(side*3,.9,0),(side*2.4,1,.15),(side*1.8,1,.45),(side*1.3,1.1,1.25),(side*.75,1.2,1.7)],[.14,.36,.4,.26,.035],sides=14,steps=7,flute=.05)
 for k in range(4):
  x=side*(1.4+k*.45);y=.4+k*.15
  for q in range(8):leaf((x,y,.03),q*2.4,.8+.1*(q%3),.25)
 for q in range(3):sweep('Golden root tracery',[(side*2.4,.7,.16+q*.07),(side*1.9,.8,.4+q*.06),(side*1.4,.9,1+q*.04)],[.007,.006,.002],'GoldThread',6,6)
# Ground litter ribbons along, not across, the approach. Author mesh orientation explicitly.
import bmesh
for name,objects in groups.items():
 for o in objects:
  if 'water surface' in o.name or'lip' in o.name or'apron' in o.name:
   avg=sum(p.normal.z*p.area for p in o.data.polygons)/sum(p.area for p in o.data.polygons)
   if avg<0:
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
   assert sum(p.normal.z*p.area for p in o.data.polygons)>0
p=ROOT/'scripts/author_hero_cells_pass2.py';tail=p.read_text().split('# Export consolidated modules and keep editable parts in separate named collections.')[1].replace('HeroCellsPass2','HeroCellsPass4').replace('172026','184026').replace('HERO_PASS2_SAVED','HERO_PASS4_SAVED');exec(compile(tail,str(p),'exec'))
