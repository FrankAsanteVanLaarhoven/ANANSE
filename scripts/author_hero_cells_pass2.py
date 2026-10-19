"""Second bounded art revision. Original editable scenery, metres, opaque conventional meshes."""
from pathlib import Path
# Reuse the qualified local geometry/export helpers, not previous generated assets.
p=Path(__file__).resolve().parent/'author_hero_cells.py';prefix=p.read_text().split('# Layered market frontages')[0];prefix=prefix.replace('HeroCells_v001','HeroCells_v002').replace('171026','172026');exec(compile(prefix,str(p),'exec'))
# Additional shared surfaces for depth and organic ground; still 512px, no opacity cards.
for name,base,rough in [('Moss',(.12,.19,.06),.95),('Litter',(.29,.19,.08),.98),('DistantBark',(.075,.13,.16),.96),('DistantLeaf',(.10,.18,.19),.96),('HazeStone',(.27,.34,.34),.94),('PlasterPale',(.60,.57,.42),.9),('ThreadDim',(.31,.20,.055),.6)]:
 m=g.material(name,base,rough=rough);mats[name]=m;image=bpy.data.images.new(name+'_Albedo',width=N,height=N,alpha=True);n=.5*noise(6)+.3*noise(24)+.2*noise(96);rgb=np.clip(np.array(base)[None,None,:]*(.8+.35*n[...,None]),0,1);image.pixels.foreach_set(np.dstack([rgb,np.ones((N,N))]).astype('float32').ravel());image.filepath_raw=str(OUT/(name+'_Albedo.png'));image.file_format='PNG';image.save();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=image;m.node_tree.links.new(t.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);surfaces.append({'name':name,'roughness':rough,'metallic':0,'texture':name+'_Albedo.png'})
# Linear shared macro/roughness map and subtle tangent-space grain, independently authored.
n=.55*noise(5)+.3*noise(16)+.15*noise(128);micro=noise(128);dx=(np.roll(micro,-1,1)-np.roll(micro,1,1))*.18;dy=(np.roll(micro,-1,0)-np.roll(micro,1,0))*.18
for name,rgb in [('SurfaceBreakup',np.stack([n,micro,.65+.3*n],2)),('SurfaceNormal',np.stack([.5-dx,.5-dy,np.full_like(n,.99)],2))]:
 im=bpy.data.images.new(name,width=N,height=N,alpha=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.dstack([rgb,np.ones((N,N))]).astype('float32').ravel());im.filepath_raw=str(OUT/(name+'.png'));im.file_format='PNG';im.save()
# Riverbank: articulated stone quay, low coping, irregular rubble/toe and rope rail.
cur='RiverQuay'
for j in range(24):
 y=(j-11.5)*.65
 for row in range(3):
  x=-.1+row*.12;box('Uneven quay masonry',(x,y+(row%2)*.14,-.2-row*.28),(.55,.62,.25),'Stone',.045)
 box('Worn coping',(-.2,y,.04),(.72,.63,.18),'Stone',.05)
 if j%4==0:
  tube('Quay bollard',[(-.45,y,.05),(-.45,y,.85)],[.095,.07]);tube('Barrier rope',[(-.45,y,.73),(-.45,y+1.3,.56),(-.45,y+2.6,.73)],[.025]*3,'Timber',8)
 rock('Bank rubble',(rng.uniform(.25,.8),y,-.55),(rng.uniform(.3,.65),.4,.30),'Stone',2)
cur='RiverBend';verts=[];faces=[]
for j in range(97):
 for i in range(49):
  x=(i-24)*.5;y=(j-48)*.75;z=.023*math.sin(x*3+y*.8)+.013*math.sin(y*3.5-x*.7);verts.append((x,y,z))
for j in range(96):
 for i in range(48):a=j*49+i;faces.append((a,a+1,a+50,a+49))
o=put(g.mesh('Continuous river surface',verts,faces,mats['Water']))
for f in o.data.polygons:f.use_smooth=True
# Low crest highlights rather than a grid of hard square waves.
for j in range(22):
 y=-30+j*2.8;pts=[(-10+i*.4,y+.12*math.sin(i*.4+j),.03)for i in range(50)];tube('Broken current glint',pts,[.006+.003*math.sin(i*.3)**2 for i in range(50)],'Jade',4)
cur='FarBank'
for j in range(22):
 y=(j-10.5)*1.2;rock('Distant bank',(0,y,-.45),(1.5,1.1,.8),'HazeStone',2)
 for k in range(3):leaf((rng.uniform(-.2,1.2),y+rng.uniform(-.4,.4),.15),rng.uniform(0,math.tau),1.5,.25,'DistantLeaf')
cur='SettlementDepth'
for j in range(7):
 x=(j-3)*2.9;h=[3.1,4.3,2.7,5.0,3.5,4.1,2.8][j];d=2+rng.random()
 box('Across river residence',(x,rng.uniform(-.3,.3),h*.5),(2.65,d,h),'HazeStone',.09)
 box('Layered roof coping',(x,0,h+.08),(2.9,d+.25,.16),'PlasterPale')
 for xx in [-.68,.68]:
  box('Shadow window',(x+xx,-d*.51,h*.65),(.45,.07,.75),'DistantBark')
 for z in [h*.35,h*.78]:box('Distant string course',(x,-d*.53,z),(2.7,.08,.08),'PlasterPale')
 if j%2==0:box('Parapet shoulder',(x+.8,0,h+.35),(.3,d,.65),'HazeStone')
cur='CargoBoat'
# Distinct upswept canoe with closed outer hull and readable raised prow/stern.
verts=[]
for z,rad in [(0,.45),(.42,.88),(.65,1),(.65,.87),(.17,.4)]:
 for i in range(48):
  a=i*math.tau/48;verts.append((3.6*math.cos(a),rad*math.sin(a),z+.55*abs(math.cos(a))**7))
faces=[]
for k in range(4):
 for i in range(48):faces.append((k*48+i,k*48+(i+1)%48,(k+1)*48+(i+1)%48,(k+1)*48+i))
put(g.mesh('Raised prow canoe',verts,faces,mats['Timber']))
for x in [-1.6,0,1.6]:box('Boat thwart',(x,0,.67),(.23,1.5,.10),'Timber')
for x in [-.8,.8]:
 for y in [-.6,.6]:tube('Boat shade upright',[(x,y,.55),(x,y,1.8)],[.035,.03])
put(g.mesh('Indigo shade', [(-1,-.85,1.85),(-1,0,2.05),(-1,.85,1.85),(1,-.85,1.85),(1,0,2.05),(1,.85,1.85)],[(0,3,4,1),(1,4,5,2)],mats['Indigo']))
for x in [-2.4,2.4]:rock('Boat cargo bundle',(x,0,.65),(.4,.4,.3),'Litter',2)
tube('Taut mooring',[(3.4,0,1),(3.9,.3,.9),(4.4,.8,1.1)],[.025]*3,'Timber',8)
cur='VendorCluster'
# Activity cluster: handcart, stacked woven baskets, cloth and produce, not random scatter.
for x in [-.7,.7]:
 bpy.ops.mesh.primitive_torus_add(major_radius=.36,minor_radius=.055,major_segments=20,minor_segments=6,location=(x,0,.38),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='Cart wheel';o.data.materials.append(mats['Timber']);put(o)
 tube('Cart axle',[(x,-.5,.38),(x,.5,.38)],[.06,.06])
box('Handcart bed',(0,0,.75),(1.7,1.1,.14),'Timber')
for y in [-.58,.58]:
 box('Cart side',(0,y,1),(1.8,.09,.4),'Timber')
for x in [-.65,.65]:tube('Cart shaft',[(x,0,.70),(x,-2,.40)],[.045,.035])
for x,y,z,rr in [(-.6,0,.88,.25),(0,0,.88,.3),(.6,0,.88,.23),(-.8,.9,.05,.32),(-.8,.9,.55,.27)]:
 for h in range(9):
  zz=z+h*.055;r=rr*(.65+.35*math.sin((h/9)*math.pi/2));tube('Basket wicker',[(x+r*math.cos(i*math.tau/24),y+r*math.sin(i*math.tau/24),zz)for i in range(25)],[.012]*25,'Litter',5)
 for q in range(5):rock('Market produce',(x+rng.uniform(-rr*.55,rr*.55),y+rng.uniform(-rr*.55,rr*.55),z+.52),(.075,.09,.075),'Clay'if q%2 else'Moss',1)
for i in range(5):box('Folded cloth stack',(.4,.85,.08+i*.04),(.8,.4,.035),'Indigo',.007)
cur='FacadeWing'
box('Offset rendered wing',(0,0,1.6),(2.2,1.5,3.2),'PlasterPale',.06)
for x in [-1.05,1.05]:box('Timber upright',(x,-.8,1.6),(.10,.13,3.1),'Timber')
box('Deep shade entrance',(0,-.78,1.0),(1.15,.07,1.9),'Timber')
for x in [-.65,.65]:box('Carved threshold jamb',(x,-.87,1.05),(.16,.2,2.1),'Stone')
box('Shallow sloping roof',(0,0,3.32),(2.65,2.0,.16),'Clay');box('Entry step',(0,-1.0,.07),(1.55,.6,.14),'Stone')
for i in range(8):box('Roof exposed end',(-1.15+i*.33,-.9,3.23),(.08,.36,.10),'Timber')
cur='ArchiveThreshold'
for side in [-1,1]:
 for step in range(3):box('Flanking carved plinth',(side*(1.95+.1*step),0,.14+step*.16),(.8-step*.14,1.5-step*.2,.28),'Stone')
 tube('Archive standard',[(side*2.4,0,0),(side*2.4,0,3.1)],[.04,.035],'Timber')
 put(g.mesh('Restricted archive hanging',[(side*2.4,0,3),(side*1.9,0,3),(side*1.9,0,1.1),(side*2.4,0,1.3)],[(0,1,2,3)],mats['Indigo']))
for k in range(4):
 z=3.0+k*.10;tube('Archive woven insignia',[(-.35,-.25,z),(-.15,-.25,z+.12),(0,-.25,z),(.15,-.25,z+.12),(.35,-.25,z)],[.018]*5,'GoldThread',7)
# Three independently shaped ancient hero trees. Root plates replace simple radial tubes.
def sculpt_tree(name,lean,fork,phase):
 global cur
 cur=name;verts=[];faces=[];rings=19;segments=28
 for j in range(rings):
  t=j/(rings-1);z=t*12.5;r=(.76*(1-t)**.65+.09)*(1+.1*math.sin(t*15+phase));cx=lean[0]*t*t+.14*math.sin(t*6+phase);cy=lean[1]*t*t+.15*math.sin(t*9+phase)
  for i in range(segments):
   a=i*math.tau/segments;flute=1+.13*math.sin(a*7+t*2)+.07*math.sin(a*11-t*3);verts.append((cx+math.cos(a)*r*flute,cy+math.sin(a)*r*flute,z))
 for j in range(rings-1):
  for i in range(segments):a=j*segments+i;b=j*segments+(i+1)%segments;faces.append((a,b,b+segments,a+segments))
 o=put(g.mesh('Ancient irregular fluted bole',verts,faces,mats['Bark']))
 for f in o.data.polygons:f.use_smooth=True
 for k in range(7):
  a=k*math.tau/7+phase;length=1.3+1.4*(.5+.5*math.sin(k*2.7+phase));dx,dy=math.cos(a),math.sin(a)
  # Solid tapered buttress wedge, off-centre and asymmetric.
  vs=[(dx*.4-dy*.18,dy*.4+dx*.18,2.5),(dx*.4+dy*.18,dy*.4-dx*.18,2.5),(dx*length+dy*.10,dy*length-dx*.10,.01),(dx*length-dy*.1,dy*length+dx*.1,.01),(dx*.5-dy*.30,dy*.5+dx*.30,.01),(dx*.5+dy*.30,dy*.5-dx*.30,.01)];put(g.mesh('Sculpted buttress plate',vs,[(0,1,2,3),(0,3,4),(1,5,2),(0,4,5,1),(4,3,2,5)],mats['Bark']))
  start=4+(k%3)*.8;end=(dx*(3.3+(k%2)),dy*(3.3+(k%2)),7.5+(k%3)*.9)
  pts=[(.1,0,start),(dx*.8,dy*.8,start+.9),(dx*2,dy*2,start+1.2),end];tube('Angular ancient bough',pts,[.32,.27,.18,.035],'Bark',12)
  for s in [-1,1]:
   aa=a+s*.65;ep=(end[0]+math.cos(aa)*1.5,end[1]+math.sin(aa)*1.5,end[2]+.7);tube('Secondary fork',[pts[2],(end[0],end[1],end[2]-.1),ep],[.15,.08,.02],'Bark',9)
   for q in range(14):
    ang=q*math.tau/14;leaf((ep[0]+math.cos(ang)*.6,ep[1]+math.sin(ang)*.6,ep[2]+.2*math.sin(q)),ang,.9+.3*math.sin(q)**2,.3)
 if fork:
  tube('Separate leaning fork',[(.4,0,1),(.8,-.1,3.6),(1.7,-.1,6.4),(3.1,.2,9.3)],[.55,.4,.25,.055],'Bark',16)
 # Root arch opens toward the outer grove, not across the gameplay approach.
 tube('Raised root arch',[(0,.5,.4),(.8,1.7,1.6),(1.9,2.4,1.3),(2.6,2.8,.05)],[.24,.27,.2,.07],'Bark',12)
 for i in range(8):
  a=i*.78;rock('Moss at root seam',(.7*math.cos(a),.7*math.sin(a),.15),(.25,.14,.1),'Moss',1)
sculpt_tree('SentinelTree',(-1.7,.3),True,.2);sculpt_tree('LeaningTree',(2.7,-1.4),False,1.4);sculpt_tree('ForkedTree',(-.3,2.4),True,2.8)
cur='ForestDepth'
for k in range(5):
 x=(k-2)*2.2;h=9+(k%3)*2;tube('Distant irregular trunk',[(x,0,-1),(x+.3,.1,h*.5),(x-.4,.3,h)],[.5,.3,.06],'DistantBark',8)
 for j in range(4):rock('Opaque canopy silhouette',(x+rng.uniform(-1,1),rng.uniform(-1,1),h-1+j*.4),(2.0,1.6,.6),'DistantLeaf',1)
cur='GroveFloor'
# Patch composition, lower central path deliberately absent from this mesh.
for i in range(9):
 x=rng.uniform(-1.2,1.2);y=rng.uniform(-.6,.6);rock('Low moss cushion',(x,y,.015),(rng.uniform(.22,.5),.25,.035),'Moss',2)
for j in range(30):
 a=rng.uniform(0,math.tau);x=rng.uniform(-1.4,1.4);y=rng.uniform(-.8,.8);leaf((x,y,.025),a,rng.uniform(.1,.26),.06,'Litter')
for a in [.2,1.1,2.2,3.5,5.2]:
 for k in range(5):leaf((math.cos(a)*.6,math.sin(a)*.6,.05+k*.018),a+(k-2)*.2,.65,.14,'Leaf')
cur='FallenWood';tube('Fallen irregular bole',[(-1.8,0,.25),(-.8,.1,.3),(.3,0,.2),(1.7,.2,.18)],[.26,.28,.22,.11],'Bark',14)
tube('Broken branch',[(.1,0,.3),(.4,.5,.6),(.9,.9,.65)],[.13,.08,.02],'Bark',9)
for k in range(8):rock('Moss on log',(-1.5+k*.4,.1,.48),(.2,.18,.04),'Moss',1)
cur='SanctuaryFrame'
for side in [-1,1]:
 tube('Embracing sanctuary root',[(side*2.8,.7,.02),(side*1.8,.5,.25),(side*1.6,.35,1.4),(side*.9,.3,2.7),(side*.5,.2,3.0)],[.12,.3,.26,.16,.04],'Bark',14)
 for k in range(5):
  tube('Subtle story thread',[(side*1.8,.3,.6+k*.35),(side*1.25,-.1,1.1+k*.22),(side*.7,-.2,1.0+k*.25)],[.007,.009,.006],'ThreadDim',5)
for i in range(7):rock('Framed sanctuary foundation',((i-3)*.36,.1,-.05),(.26,.32,.09),'Stone',2)
cur='StreamReach';vs=[];fs=[]
for j in range(3):
 for i in range(65):
  x=-4+i*.125;centre=.18*math.sin(x*.8);y=centre+(j-1)*(.63+.1*math.cos(x*1.6));vs.append((x,y,-.025+.006*math.sin(i*1.5+j)))
for j in range(2):
 for i in range(64):a=j*65+i;fs.append((a,a+1,a+66,a+65))
o=put(g.mesh('Curving opaque stream skin',vs,fs,mats['Water']))
for p in o.data.polygons:p.use_smooth=True
for side in [-1,1]:
 for i in range(18):
  x=-4+i*.47;y=.18*math.sin(x*.8)+side*(.72+.12*math.sin(i*1.7));rock('Irregular moist bank',(x,y,-.035),(.30,.25,.10),'Stone',2)
  if i%3==0:
   for q in range(4):leaf((x,y,.04),side*(1+q*.17),.45,.11)
cur='SilkHierarchy'
for side in [-1,1]:
 for x in [-1,1]:
  rock('Thread attachment node',(x,side*.62,.83),(.06,.06,.07),'GoldThread',2)
  for q in range(5):tube('Filament attachment fan',[(x,side*.62,.83),(x+q*.035,side*.78,.62),(x+q*.06,side*1.0,.03)],[.012-.0015*q,.007,.004],'GoldThread',5)
 for q in range(4):tube('Fine layered catenary',[(-1+i*.1,side*(.60+q*.014),.85-.16*math.sin(i*math.pi/20)+q*.014)for i in range(21)],[.004]*21,'ThreadDim',5)
# Export consolidated modules and keep editable parts in separate named collections.
exports=[]
for name,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for o in objects:
  c=o.copy();c.data=o.data.copy();scene.collection.objects.link(c);c.select_set(True);copies.append(c)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');path=OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_animations=False)
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);j['asset'].pop('generator',None);s=json.dumps(j,separators=(',',':')).encode();s+=b' '*(-len(s)%4);tail=b[20+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(s)+len(tail))+struct.pack('<II',len(s),0x4e4f534a)+s+tail);exports.append({'name':name,'file':path.name,'triangles':sum(len(f.vertices)-2 for f in o.data.polygons),'materials':len(o.data.materials),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});bpy.data.objects.remove(o,do_unlink=True)
for name,objects in groups.items():
 col=bpy.data.collections.new(name);scene.collection.children.link(col)
 for o in objects:
  for c in list(o.users_collection):c.objects.unlink(o)
  col.objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'HeroCellsPass2.blend'));(OUT/'source-status.json').write_text(json.dumps({'creator':'Frank Asante Van Laarhoven','units':'metres','scene':'HeroCellsPass2.blend','scene_sha256':hashlib.sha256((OUT/'HeroCellsPass2.blend').read_bytes()).hexdigest(),'exports':exports,'surfaces':surfaces,'seed':172026,'creative_approved':False},indent=2));print('HERO_PASS2_SAVED',len(exports))
