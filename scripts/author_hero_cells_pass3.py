"""Bounded third visual revision: continuous organic forms and composed shoreline/depth."""
from pathlib import Path
p=Path(__file__).resolve().parent/'author_hero_cells.py';prefix=p.read_text().split('# Layered market frontages')[0].replace('HeroCells_v001','HeroCells_v003').replace('171026','173026');exec(compile(prefix,str(p),'exec'))
from mathutils import Vector
# Smooth cubic branches with continuous transported cross-sections, not straight polyline elbows.
def sweep(name,points,radii,mat='Bark',sides=14,steps=8,flute=0):
 ps=[Vector(v) for v in points];vs=[];fs=[];rings=[];rs=[]
 for k in range(len(ps)-1):
  a,b,c,d=ps[max(0,k-1)],ps[k],ps[k+1],ps[min(len(ps)-1,k+2)]
  for q in range(steps):
   t=q/steps;rings.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t));rs.append(radii[k]*(1-t)+radii[k+1]*t)
 rings.append(ps[-1]);rs.append(radii[-1]);prev=Vector((1,0,0))
 for k,(v,r) in enumerate(zip(rings,rs)):
  tangent=(rings[min(k+1,len(rings)-1)]-rings[max(k-1,0)]).normalized();axis=prev-tangent*prev.dot(tangent)
  if axis.length<.01:axis=tangent.cross(Vector((0,1,0)))
  axis.normalize();prev=axis;other=tangent.cross(axis).normalized()
  for j in range(sides):
   ang=j*math.tau/sides;rr=r*(1+flute*math.sin(ang*5+k*.035)+flute*.5*math.sin(ang*9));vs.append(tuple(v+rr*(math.cos(ang)*axis+math.sin(ang)*other)))
 for k in range(len(rings)-1):
  for j in range(sides):a=k*sides+j;b=k*sides+(j+1)%sides;fs.append((a,b,b+sides,a+sides))
 fs.extend([tuple(reversed(range(sides))),tuple(range(len(vs)-sides,len(vs)))]);return put(g.mesh(name,vs,fs,mats[mat]))
# Three independently composed ancient trees: recurved boughs, broad basal mass, soft roots.
for name,lean,phase in [('CrownGuardian',(-2.7,.6),.2),('RiverFig',(3.2,-1.9),1.8),('TwinnedElder',(-.7,2.9),3.7)]:
 cur=name;lx,ly=lean
 sweep('Continuous fluted ancient bole',[(0,0,-.12),(-.15,.1,.8),(.2,-.2,2.4),(lx*.2,ly*.1,4.4),(lx*.48,ly*.55,7.1),(lx,ly,10.5),(lx*1.1,ly*1.1,12.4)],[1.12,.97,.76,.63,.47,.24,.055],sides=28,flute=.11)
 for k in range(8):
  a=phase+k*math.tau/8;dx,dy=math.cos(a),math.sin(a);length=2.4+.9*math.sin(k*2+phase)
  sweep('Recurved buttress root',[(.1*dx,.1*dy,2.5),(dx*.65,dy*.65,1.35),(dx*1.2,dy*1.2,.42),(dx*length,dy*length,.1),(dx*(length+.7),dy*(length+.7),.015)],[.30,.40,.30,.15,.018],sides=14,steps=7,flute=.05)
  z=4.3+(k%3)*1.1;start=(lx*.2,ly*.2,z);tip=(lx*.6+dx*4.1,ly*.6+dy*4.1,z+3.3)
  sweep('Curved rising primary bough',[start,(start[0]+dx*.65,start[1]+dy*.65,z+.7),(dx*2.7,dy*2.7,z+1.15),tip],[.4,.34,.22,.035],flute=.06)
  for side in [-1,1]:
   aa=a+side*.7;end=(tip[0]+math.cos(aa)*1.5,tip[1]+math.sin(aa)*1.5,tip[2]+1.0)
   sweep('Crown fork',[(dx*2.3,dy*2.3,z+1.0),tip,end],[.17,.08,.015],sides=10,steps=6)
   # Layered leaf fans follow crown branches; no faceted sphere canopy.
   for q in range(16):
    ang=q*2.399+phase;rr=.18+.085*q;leaf((end[0]+math.cos(ang)*rr,end[1]+math.sin(ang)*rr,end[2]-.25+.055*(q%5)),ang,.72+.12*(q%4),.20)
 if name=='TwinnedElder':sweep('Companion bole',[(.5,.2,0),(.9,.3,2.1),(1.3,.1,4.2),(1.9,-.4,6.8),(2.5,-1,9.2)],[.65,.53,.4,.23,.025],sides=20,flute=.1)
 for q in range(16):
  a=q*2.399;rock('Root moss mantle',(.8*math.cos(a),.8*math.sin(a),.12),(.35,.22,.1),'Leaf',2)
# Unique backdrop groves have irregular spacing/lean/height, staggered crowns and asymmetric understory.
for variant in range(3):
 cur='DepthGrove'+str(variant)
 for k in range(7):
  x=-7+k*2.2+rng.uniform(-.5,.5);y=rng.uniform(-1.9,1.9);h=rng.uniform(7,14);lean=rng.uniform(-1.8,1.8)
  sweep('Distant curved trunk',[(x,y,-.5),(x+.3,y+.2,h*.3),(x+lean*.6,y-.4,h*.7),(x+lean,y+.7,h)],[.55,.38,.23,.035],sides=10,steps=5)
  for q in range(3):
   a=q*2.4+variant;end=(x+lean+math.cos(a)*2.5,y+math.sin(a)*2.2,h-.8)
   sweep('Distant canopy branch',[(x+lean*.6,y,h*.65),(x+lean,y+.3,h*.85),end],[.16,.1,.01],sides=8,steps=4)
   for j in range(10):leaf((end[0]+rng.uniform(-.8,.8),end[1]+rng.uniform(-.8,.8),end[2]+rng.uniform(-.3,.3)),j*2.4,1.8,.48)
# Wet banks and stream: varying channel width, continuous earth lip, pebbles/reeds in moisture bands.
for river in [False,True]:
 cur='RiverMargin' if river else 'LivingStream';vs=[];fs=[];length=30 if river else 8;count=81;half=10 if river else .52
 for j in range(9):
  t=j/8
  for i in range(count):
   x=-length/2+i*length/(count-1);centre=(.20 if river else .25)*math.sin(x*.8)+.1*math.sin(x*1.9);width=half*(1+.16*math.sin(x*.9)+.07*math.sin(x*2.8));y=centre+(t*2-1)*width;vs.append((x,y,-.03+.006*math.sin(x*3+t*4)))
 for j in range(8):
  for i in range(count-1):a=j*count+i;fs.append((a,a+1,a+count+1,a+count))
 water=put(g.mesh('Quiet continuous river skin' if river else 'Meandering stream skin',vs,fs,mats['Water']))
 # Bank mesh is smooth continuous earth-to-water cross-section, avoiding stacked rock wall.
 for side in [-1,1]:
  vs=[];fs=[]
  for i in range(count):
   x=-length/2+i*length/(count-1);centre=(.20 if river else .25)*math.sin(x*.8)+.1*math.sin(x*1.9);w=half*(1+.16*math.sin(x*.9)+.07*math.sin(x*2.8))
   for d,z in [(0,-.05),(.22,.03),(.55,.12),(1.1,.11)]:vs.append((x,centre+side*(w+d),z+.035*math.sin(x*2)*d))
  for i in range(count-1):
   for j in range(3):a=i*4+j;fs.append((a,a+1,a+5,a+4))
  put(g.mesh('Silt bank rounded transition',vs,fs,mats['Stone' if river else 'Bark']))
  for k in range(28 if river else 16):
   x=-length/2+(k+.4)*length/(28 if river else 16);w=half*(1+.16*math.sin(x*.9)+.07*math.sin(x*2.8));y=.2*math.sin(x*.8)+side*(w+.32)
   rock('Waterworn margin pebble',(x,y,.055),(.14+rng.random()*.14,.12,.06),'Stone',3)
   if k%3:
    for q in range(5):sweep('Reed at wet margin',[(x,y,.04),(x+.04*q,y+.03,.25),(x+.05*q,y+.03,.45+rng.random()*.2)],[.015,.012,.003],'Leaf',sides=5,steps=3)
# Non-periodic far-river skyline: each module has a different authored plan and roof silhouette.
for variant in range(3):
 cur='SkylineQuarter'+str(variant)
 for j in range(6):
  x=-8+j*3+rng.uniform(-.45,.45);y=rng.uniform(-2,2);h=rng.uniform(2.2,6.0);w=rng.uniform(1.5,2.7);d=rng.uniform(1.5,3.1)
  box('Stepped settlement mass',(x,y,h/2),(w,d,h),'Lime',.09)
  if (j+variant)%3==0:
   # Hip roof differs from flat parapets.
   put(g.mesh('Hipped clay skyline roof',[(x-w*.6,y-d*.6,h),(x+w*.6,y-d*.6,h),(x+w*.6,y+d*.6,h),(x-w*.6,y+d*.6,h),(x-.3,y,h+.8),(x+.3,y,h+.8)],[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)],mats['Clay']))
  else:box('Deep parapet',(x,y,h+.12),(w+.15,d+.15,.24),'Stone')
  if j%2:box('Recessed side wing',(x+w*.7,y+.2,h*.32),(w*.6,d*.75,h*.64),'Lime')
  for q in range(2):box('Shadow opening',(x+(q-.5)*w*.48,y-d*.51,h*.65),(.32,.045,.65),'Timber')
  if j%2==0:
   for q in range(4):leaf((x+.1*q,y,h+.15),q*1.7,1.6,.4)
# New market activity cluster: covered basket goods, rolled mats, hanging dye cloth, pottery.
cur='DyersCourt'
for x in [-1.0,1.0]:sweep('Dyer shade upright',[(x,.5,0),(x+.03,.5,1),(x,.5,2.5)],[.05,.05,.04],'Timber',8,3)
put(g.mesh('Draped indigo shade',[(-1.3,-.9,2.3),(0,-.9,2.15),(1.3,-.9,2.4),(-1.3,.8,2.5),(0,.8,2.4),(1.3,.8,2.5)],[(0,1,4,3),(1,2,5,4)],mats['Indigo']))
for k in range(4):
 x=-.9+k*.6;put(g.loft('Open dye vessel',[(x,0,.02,.18,.18),(x,0,.15,.3,.3),(x,0,.45,.29,.29),(x,0,.52,.22,.22),(x,0,.52,.17,.17),(x,0,.1,.1,.1)],mats['Clay'],segments=24))
 for q in range(5):box('Folded dyed textile',(x,.5,.05+q*.04),(.5,.35,.035),'Indigo' if k%2 else 'Jade',.008)
for k in range(3):sweep('Rolled woven floor mat',[(-1+k*.4,-.65,.14),(-1+k*.4,-.15,.14),(-1+k*.4,.3,.14)],[.12,.12,.12],'Timber',sides=12,steps=3)
cur='ArchiveCrown'
for side in [-1,1]:
 for j in range(3):box('Archive layered side wing',(side*(2.4+j*.18),.2,1.7-j*.15),(.42,.85,3.4-j*.3),'Lime',.06)
 for j in range(9):
  z=.4+j*.3;box('Brass record inset',(side*2.35,-.25,z),(.14,.06,.12),'Brass',.01)
box('Archive shaded canopy',(0,.05,4.3),(5.8,1.4,.22),'Clay')
for k in range(13):box('Canopy tooth',(-2.7+k*.45,-.65,4.12),(.13,.3,.26),'Timber')
# Foliage deliberately composed by moisture and edges, with leaf litter and fern rosettes.
cur='FernEcology'
for centre in [(-.7,.3),(.5,.5),(.9,-.2)]:
 x,y=centre
 for k in range(7):
  a=k*math.tau/7;length=.6+.16*math.sin(k);sweep('Fern rachis',[(x,y,.03),(x+math.cos(a)*.3,y+math.sin(a)*.3,.35),(x+math.cos(a)*length,y+math.sin(a)*length,.20)],[.012,.009,.002],'Leaf',sides=5,steps=4)
  for q in range(1,6):
   t=q/6
   for side in [-1,1]:leaf((x+math.cos(a)*length*t,y+math.sin(a)*length*t,.30*math.sin(math.pi*t)),a+side*.75,.20*(1-t)+.09,.045)
for k in range(35):
 x=rng.uniform(-1.3,1.3);y=rng.uniform(-.8,.8);leaf((x,y,.008),rng.random()*math.tau,rng.uniform(.12,.27),.055,'Clay' if k%4==0 else 'Timber')
cur='RootTheatre'
for side in [-1,1]:
 sweep('Soft embracing root frame',[(side*3,.8,0),(side*2.2,.7,.2),(side*1.9,.6,1.3),(side*1.4,.6,2.5),(side*.6,.6,3.1)],[.16,.38,.31,.18,.02],steps=10,flute=.06)
 for q in range(4):sweep('Sanctuary thread tracing',[(side*2,.3,.5+q*.3),(side*1.5,.4,1+q*.3),(side*.8,.5,1.2+q*.25)],[.009,.008,.003],'GoldThread',sides=6,steps=6)
for k in range(8):rock('Timeworn sanctuary stones',((k-3.5)*.4,.8,.05),(.3,.38,.15),'Stone',3)
# Reuse the qualified consolidation/UV/export path, with a separate scene/version.
p=ROOT/'scripts/author_hero_cells_pass2.py';tail=p.read_text().split('# Export consolidated modules and keep editable parts in separate named collections.')[1];tail=tail.replace('HeroCellsPass2','HeroCellsPass3').replace('172026','173026').replace('HERO_PASS2_SAVED','HERO_PASS3_SAVED');exec(compile(tail,str(p),'exec'))
