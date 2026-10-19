"""Editable replacement wall, interaction-prop and leaf geometry for existing maps."""
import bpy, math, random, json, hashlib, struct, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'SourceArt/Environments/MarketSanctuary/Forms_v002'
assert not OUT.exists();OUT.mkdir(parents=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'SourceArt/Environments/MarketSanctuary/Authored_v001/MarketAndSanctuary.blend'))
# Read actual branch tips from the saved original scene before starting the new one.
tips=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith('TreeBranch'):
  tips.append(sum((o.matrix_world@v.co for v in list(o.data.vertices)[-12:]),Vector())/12)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
sys.path.insert(0,str(ROOT/'scripts'));import character_mesh_tools as g
g.scene=s;g.parts=[];g.binds={};g.joints={};groups={}
s.unit_settings.system='METRIC';s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=48
s.world=bpy.data.worlds.new('Daylight');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
wood=g.material('WeatheredWood',(.13,.052,.020),rough=.86);plaster=g.material('WarmPlaster',(.46,.28,.13),rough=.94);stone=g.material('CarvedStone',(.16,.18,.15),rough=.94);page=g.material('Paper',(.60,.47,.28),rough=.95);leather=g.material('LedgerLeather',(.065,.025,.012),rough=.8);brass=g.material('SealBrass',(.48,.25,.07),metal=.65,rough=.48);leaf=[g.material('Leaf_'+str(i),c,rough=.86)for i,c in enumerate([(.026,.10,.019),(.048,.14,.025),(.085,.19,.034)])]

def add(o,group):
 collection=bpy.data.collections.get(group)
 if not collection:collection=bpy.data.collections.new(group);s.collection.children.link(collection)
 for old in list(o.users_collection):old.objects.unlink(o)
 collection.objects.link(o);o['module']=group;groups.setdefault(group,[]).append(o);return o
def box(name,loc,size,mat,group,bevel=.012):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:
  m=o.modifiers.new('WornEdges','BEVEL');m.width=min(bevel,min(size)*.16);m.segments=3;bpy.ops.object.modifier_apply(modifier=m.name)
 return add(o,group)
inventory=json.loads((ROOT/'.local/verification/forms-scenery-20261015/primitive-inventory.json').read_text())
wall_map={}
for item in inventory['L_Market_EpisodeRefined']:
 label=item['label']
 if item['class']!='StaticMeshActor' or label in ['Greybox floor','Web anchor visible marker']:continue
 group='Wall_'+''.join(c if c.isalnum()else'_'for c in label);wall_map[label]=group;x,y,z=[v*.02 for v in item['bounds_extent']]
 box('PlasteredMasonry',(0,0,0),(x,y,z),plaster,group,.025)
 # Low relief masonry joints and coping follow each wall's actual dimensions.
 long=x>=y;length=x if long else y;depth=y if long else x
 for i in range(max(2,int(length/.8))):
  a=-length*.5+(i+.5)*length/max(2,int(length/.8));pos=(a,0,z*.5-.045)if long else(0,a,z*.5-.045);size=(min(.78,length*.45),depth+.018,.09)if long else(depth+.018,min(.78,length*.45),.09);box('HandCutCoping',pos,size,stone,group,.015)
 # Recessed plank facade details on archive walls; route surfaces are unchanged.
 if 'Archive' in label:
  for i in range(9):
   a=-1.0+i*.25;pos=(a,-depth*.5-.018,-.15)if long else(-depth*.5-.018,a,-.15);size=(.22,.025,1.5)if long else(.025,.22,1.5);box('AgedTimberPanel',pos,size,wood,group,.006)
 if 'roof deck' in label:
  # Top is exactly the original walking plane; visual detail stays below it.
  for i in range(14):box('RoofEdgeBeam',(-x*.5+(i+.5)*x/14,0,z*.5-.055),(x/14-.012,y,.11),wood,group,.007)

add(g.loft('WebAnchorFinial',[(0,0,-.20,.13,.13),(0,0,-.14,.15,.15),(0,0,.10,.06,.06),(0,0,.18,.13,.13),(0,0,.20,.12,.12)],brass,segments=32),'WebAnchor')

# Collision-fit writing stands; book, paper leaves and clasp are editable parts.
for group in ['LedgerStand','NoticeStand']:
 box('Foot',(0,0,-.555),(.98,.94,.09),wood,group,.025)
 for x in [-.37,.37]:
  for y in [-.34,.34]:box('TurnedStandLeg',(x,y,-.10),(.14,.14,.89),wood,group,.018)
 box('WritingTable',(0,0,.37),(.98,.96,.10),wood,group,.025)
 box('LowerBrace',(0,.31,-.38),(.85,.10,.12),wood,group)
 if group=='LedgerStand':
  box('BoundLedger',(0,-.04,.455),(.63,.57,.07),leather,group,.018)
  for i in range(12):box('PaperLeaf',(0,-.055,.46+i*.0016),(.575,.51,.0014),page,group,0)
  box('LedgerSpine',(-.32,-.04,.48),(.055,.59,.10),leather,group)
  box('BrassClasp',(.22,-.04,.496),(.06,.12,.018),brass,group,.006)
 else:
  box('SlopingNotice',(0,.04,.49),(.72,.58,.045),wood,group)
  box('EdictSheet',(0,.03,.519),(.63,.49,.006),page,group,.002)
  add(g.oval('RaisedSeal',(.19,-.08,.534),(.055,.055,.016),brass,None),group)
group='StoryStone';rng=random.Random(61015)
add(g.loft('StoryAltar',[(0,0,-.60,.48,.45),(0,0,-.45,.52,.46),(0,0,.25,.39,.35),(0,0,.45,.52,.48),(0,0,.50,.50,.46)],stone,segments=36),group)
for i in range(12):
 a=i*math.tau/12;add(g.tube('CarvedMemoryGroove',[(.405*math.cos(a),.365*math.sin(a),-.30),(.41*math.cos(a),.37*math.sin(a),.15)],[.009,.009],brass),group)

# Actual leaf surfaces replace the old ellipsoidal canopy clusters.
group='SanctuaryLeaves'
for tip in tips:
 for j in range(55):
  angle=rng.random()*math.tau;radius=rng.uniform(.05,1.5);base=tip+Vector((math.cos(angle)*radius,math.sin(angle)*radius,rng.uniform(-.25,.65)));d=Vector((math.cos(angle),math.sin(angle),rng.uniform(-.2,.45))).normalized();across=Vector((-d.y,d.x,0)).normalized();length=rng.uniform(.28,.62);width=length*.30
  v=[base,base+d*length*.45+across*width,base+d*length,base+d*length*.45-across*width,base+d*length*.45+Vector((0,0,.055))];add(g.mesh('BentLeaf',[tuple(p)for p in v],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],rng.choice(leaf)),group)

for name,pos,energy in [('Key',(4,-6,8),1800),('Fill',(-4,-3,5),1000)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.size=5;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;g.aim(o,(0,0,.5))
d=bpy.data.cameras.new('ReviewCamera');camera=bpy.data.objects.new('ReviewCamera',d);s.collection.objects.link(camera);s.camera=camera;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
for o in [p for objects in groups.values()for p in objects]:o.hide_render=True
for o in groups['LedgerStand']+groups['NoticeStand']:o.hide_render=False
# Offset only review copies; export/authoring origins remain fixed.
review=[]
for group,dx in [('LedgerStand',-.9),('NoticeStand',.9)]:
 for o in groups[group]:c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.location.x+=dx;c.hide_render=False;review.append(c);o.hide_render=True
camera.location=(2.4,-3.5,2);g.aim(camera,(0,0,0));s.render.filepath=str(OUT/'writing_props.png');bpy.ops.render.render(write_still=True)
for o in review:bpy.data.objects.remove(o,do_unlink=True)
for o in [p for objects in groups.values()for p in objects]:o.hide_render=True
for o in groups['SanctuaryLeaves']:o.hide_render=False
camera.location=(11,-14,8);g.aim(camera,(0,0,5));s.render.filepath=str(OUT/'leaf_geometry.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ReplacementScenery.blend'))
exports=[]
for group,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for o in objects:
  c=o.copy();c.data=o.data.copy();s.collection.objects.link(c);c.hide_render=False;c.select_set(True);copies.append(c)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name='SM_'+group
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 if not o.data.uv_layers:
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
 path=OUT/(group+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_animations=False)
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
 exports.append({'group':group,'file':path.name,'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});bpy.data.objects.remove(o,do_unlink=True)
(OUT/'source-status.json').write_text(json.dumps({'status':'AUTHORED_REPLACEMENTS_PENDING_NATIVE_REVIEW','wall_map':wall_map,'exports':exports,'scene_sha256':hashlib.sha256((OUT/'ReplacementScenery.blend').read_bytes()).hexdigest(),'units':'metres; existing collision retained separately','leaf_branch_tips':len(tips),'creative_approved':False,'mobile_qualified':False},indent=2)+'\n')
print('REPLACEMENT_SCENERY_SAVED',len(exports))
