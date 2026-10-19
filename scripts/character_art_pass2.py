"""Versioned sculpt/weight/material edits on the two qualified character surfaces.
No rest-bone, clip-identity, gameplay, collision or publication changes.
"""
import bpy,bmesh,math,json,hashlib,struct,sys,shutil,random
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];key=sys.argv[sys.argv.index('--')+1];old,new=('Authored_v028','Authored_v031')if key=='Kwaku'else('Authored_v013','Authored_v016');root=R/'SourceArt/Characters'/key;src=root/old;out=root/new;assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(src/(key+'.blend')));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');o=bpy.data.objects['SK_'+key];m=o.data;rest=[(b.name,b.parent.name if b.parent else None,[list(r)for r in b.matrix_local])for b in rig.data.bones];actions=sorted(a.name for a in bpy.data.actions);rig.animation_data.action=None
for p in rig.pose.bones:p.location=(0,0,0);p.rotation_euler=(0,0,0);p.scale=(1,1,1)
s.frame_set(0);changes=[];groups={g.index:g.name for g in o.vertex_groups};weights=[{groups[g.group]:g.weight for g in v.groups}for v in m.vertices];v=[x.co.copy()for x in m.vertices];faces=[list(p.vertices)for p in m.polygons];mat=[p.material_index for p in m.polygons];uv=[[tuple(m.uv_layers.active.data[i].uv)for i in p.loop_indices]for p in m.polygons];materials=list(m.materials);shapes={k.name:[p.co.copy()for p in k.data]for k in m.shape_keys.key_blocks if k.name!='Basis'}
# Connected components identify real saved surfaces; hidden authoring parts may be stale.
parent=list(range(len(v)))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for e in m.edges:
 a,b=map(find,e.vertices)
 if a!=b:parent[a]=b
components={}
for i in range(len(v)):components.setdefault(find(i),[]).append(i)
comps=sorted(components.values(),key=lambda q:q[0]);byfirst={ids[0]:ids for ids in comps}
def warp(ids,fn):
 for i in ids:
  v[i]=fn(v[i].copy())
  for coords in shapes.values():coords[i]=fn(coords[i].copy())
def gauss(x,c,r):return math.exp(-((x-c)/r)**2)
def smooth(a):a=max(0,min(1,a));return a*a*(3-2*a)
def assign(i,d):
 marker={n:w for n,w in weights[i].items()if n not in rig.data.bones};d={n:w for n,w in d.items()if w>1e-6};total=sum(d.values());assert total>0;weights[i]={**marker,**{n:w/total for n,w in d.items()}}
def dominant(ids):
 d={}
 for i in ids:
  for n,w in weights[i].items():d[n]=d.get(n,0)+w
 return max(d,key=d.get)
# Smooth anatomy changes are applied to the actual Basis and all retained targets.
if key=='Kwaku':
 core=byfirst[28171]
 def headwarp(p):
  x,y,z=p;front=smooth((-y-.01)/.055);jaw=gauss(z,1.294,.028);p.x*=1+.12*jaw-.055*smooth((z-1.412)/.065);p.y-=front*(.003*gauss(x,0,.018)*gauss(z,1.36,.032)+.0025*gauss(abs(x),.045,.027)*gauss(z,1.345,.035));p.y+=front*.002*gauss(x,0,.006)*gauss(z,1.327,.008);p.z-=.22*max(0,z-1.402);return p
 warp(core,headwarp)
 # More natural lip width/volume, without painting a mouth onto an unchanging face.
 for first in [39891,40056]:
  ids=byfirst[first];c=sum((v[i]for i in ids),Vector())/len(ids)
  def lipwarp(p):
   p.x*=1.18;p.y=c.y+(p.y-c.y)*1.30-.0004;p.z=c.z+(p.z-c.z)*1.18+.001*min(1,abs(p.x)/.026);return p
  warp(ids,lipwarp)
 for first in [36547,36739]:
  ids=byfirst[first];c=sum((v[i]for i in ids),Vector())/len(ids);warp(ids,lambda p:c+Vector(((p.x-c.x)*1.08,(p.y-c.y)*1.4-.002,(p.z-c.z)*1.08)))
 # Break the perfect button-row crop into a denser, irregular coiled silhouette.
 rng=random.Random(2251)
 for ids in comps:
  if len(ids)==448 and min(v[i].z for i in ids)>1.405 and dominant(ids)=='head':
   c=sum((v[i]for i in ids),Vector())/len(ids)
   if c.z>1.44:
    dz=.009+.016*rng.random();scale=.9+.4*rng.random();warp(ids,lambda p:c+Vector(((p.x-c.x)*scale,(p.y-c.y)*scale,(p.z-c.z)*1.25+dz)))
 # Anatomical finger taper, knuckle swell and rounded terminal form; no extra digit.
 for side in ['L','R']:
  for digit in range(5):
   b=rig.data.bones[f'digit_{side}_{digit}_01'];end=rig.data.bones[f'digit_{side}_{digit}_02'].tail_local;axis=(end-b.head_local).normalized();length=(end-b.head_local).length
   ids=[i for i,w in enumerate(weights)if sum(x for n,x in w.items()if n.startswith(f'digit_{side}_{digit}_'))>.8]
   def digitwarp(p):
    t=max(0,min(1,(p-b.head_local).dot(axis)/length));c=b.head_local+axis*(p-b.head_local).dot(axis);rad=.94-.22*smooth((t-.56)/.44)+.10*gauss(t,.46,.13);return c+(p-c)*rad
   warp(ids,digitwarp)
  wrist=rig.data.bones['hand_'+side].head_local
  for i,w in enumerate(weights):
   if v[i].x*wrist.x>0 and (v[i]-wrist).length<.040 and sum(a for n,a in w.items()if n in ['lowerarm_'+side,'hand_'+side])>.8:
    a=smooth((wrist.z+.019-v[i].z)/.042);assign(i,{'lowerarm_'+side:1-a,'hand_'+side:a})
 # Sew proximal sleeve ring to the shirt surface; match boundary weights so it stays attached in reach.
 shirtids=byfirst[119965]if 119965 in byfirst else None
 shirtparts=[ids for ids in comps if len(ids)==8448];assert len(shirtparts)==1;shirtids=shirtparts[0];shirtset=set(shirtids);tree=BVHTree.FromPolygons(v,[f for f in faces if set(f).issubset(shirtset)])
 for ids in comps:
  if len(ids)!=360:continue
  side='L'if sum(v[i].x for i in ids)<0 else'R';a=rig.data.bones['upperarm_'+side].head_local;b=rig.data.bones['upperarm_'+side].tail_local;axis=(b-a).normalized();projs=[(v[i]-a).dot(axis)for i in ids];lo,hi=min(projs),max(projs)
  for i,t0 in zip(ids,projs):
   t=(t0-lo)/(hi-lo)
   if t<.14:
    hit=tree.find_nearest(v[i]);assert hit;delta=(hit[0]+hit[1]*.0003-v[i])*(1-t/.14);v[i]+=delta
    for q in shapes.values():q[i]+=delta
   chest=(1-smooth(t/.6))*.94;assign(i,{'chest':chest,'upperarm_'+side:1-chest})
 changes+=['Reshaped youthful jaw/cheek/forehead and nasal/philtrum planes','Fuller shaped lips and dimensional ears','Irregular coiled crop silhouette','Tapered five digit chains and smoother wrist weights','Sleeve seam fitted to actual shirt surface with chest-matched proximal weights']
else:
 core=byfirst[1130]
 def headwarp(p):
  x,y,z=p;front=smooth((-y-.025)/.09);upper=smooth((z-1.94)/.07);p.x*=1-.12*upper+.025*gauss(z,1.875,.035);p.z-=.10*max(0,z-1.94);p.y-=front*(.020*gauss(z,1.85,.045)+.006*gauss(z,1.9,.028)*gauss(x,0,.035));return p
 warp(core,headwarp)
 for first in [12579,13027,27340,27788]:
  ids=byfirst[first];c=sum((v[i]for i in ids),Vector())/len(ids)
  def earwarp(p):
   z=p.z;h=(z-c.z)/.034;p.x=c.x+(p.x-c.x)*(.82-.17*max(0,h))+(.004 if c.x>0 else-.004)*max(0,h);p.z=c.z+(z-c.z)*1.12-.002;p.y=c.y+(p.y-c.y)*.8;return p
  warp(ids,earwarp)
 ids=byfirst[168]
 def neckwarp(p):
  t=(p.z-1.592)/.186;scale=.66+.30*(1-smooth(t));p.x*=scale;p.y*=.86;p.z=1.535+t*.266;return p
 warp(ids,neckwarp)
 for i in ids:
  t=smooth((v[i].z-1.56)/.10);assign(i,{'chest':1-t,'neck':t})
 jaw=byfirst[12131];c=sum((v[i]for i in jaw),Vector())/len(jaw);warp(jaw,lambda p:c+Vector(((p.x-c.x)*.98,(p.y-c.y)*1.04-.012,(p.z-c.z)*.70+.004)))
 # Nose/mouth follow the longer feline muzzle, not a human lower face.
 for ids in comps:
  if len(ids)in [6,24] and min(v[i].z for i in ids)>1.77:
   warp(ids,lambda p:p+Vector((0,-.015,.002)))
 # Pin cape shoulder attachment to chest; blend secondary bones below the attachment.
 for ids in comps:
  if ids[0]not in [50139,50907,51099,51243]:continue
  for i in ids:
   pin=smooth((v[i].z-1.44)/.12);bone={n:w for n,w in weights[i].items()if n in rig.data.bones};assign(i,{**{n:w*(1-pin)for n,w in bone.items()if n!='chest'},'chest':pin+(1-pin)*bone.get('chest',0)})
 # Sculpt the paw mass about the existing articulated four-digit rig.
 for side in ['L','R']:
  ids=byfirst[14819 if side=='L'else 29580];hand=rig.data.bones['hand_'+side];axis=(hand.tail_local-hand.head_local).normalized()
  def pawwarp(p):
   t=smooth((1.105-p.z)/.13);c=hand.head_local+axis*(p-hand.head_local).dot(axis);d=p-c;return p+Vector((d.x*.10*t,d.y*.10*t,0))
  warp(ids,pawwarp)
 changes+=['Longer feline muzzle, tapered cranium, angular smaller pinnae','Tapered chest-to-neck contour replaces rounded floating-neck silhouette','Lower jaw narrowed vertically and aligned to muzzle','Chest-pinned cape shoulder region with retained secondary bones below','Paw volume refined around the existing four digit chains; no new claws/limbs']
# Replace overlapping orbital patches by a topology-joined annulus on the actual face boundary.
removed={i for i,w in enumerate(weights)if any(w.get('lid_'+side,0)>.5 for side in ['L','R'])};keep=[j for j,f in enumerate(faces)if not any(i in removed for i in f)];faces=[faces[j]for j in keep];mat=[mat[j]for j in keep];uv=[uv[j]for j in keep];coreids=set(core);edges={}
for f in faces:
 if not set(f).issubset(coreids):continue
 for a,b in zip(f,f[1:]+f[:1]):edge=tuple(sorted([a,b]));edges[edge]=edges.get(edge,0)+1
if key=='OseboLeopard':
 # This older surface had no actual apertures: cut two bounded eye openings in the front skin.
 keep=[]
 for j,f in enumerate(faces):
  c=sum((v[i]for i in f),Vector())/len(f);cut=set(f).issubset(coreids)and c.y<-.08 and any(((c.x-sign*.063)/.030)**2+((c.z-1.925)/.020)**2<1 for sign in [-1,1])
  if not cut:keep.append(j)
 faces=[faces[j]for j in keep];mat=[mat[j]for j in keep];uv=[uv[j]for j in keep];edges={}
 for f in faces:
  if not set(f).issubset(coreids):continue
  for a,b in zip(f,f[1:]+f[:1]):edge=tuple(sorted([a,b]));edges[edge]=edges.get(edge,0)+1
boundary={a for e,n in edges.items()if n==1 for a in e};skinmat=next(mat[j]for j,f in enumerate(faces)if set(f).issubset(coreids));coretree=BVHTree.FromPolygons(v,[f for f in faces if set(f).issubset(coreids)]);newblink={}
for side,sign in [('L',-1),('R',1)]:
 oldcx=sign*(.039 if key=='Kwaku'else .063);cz=1.381 if key=='Kwaku'else 1.925;cx=sign*(.0355 if key=='Kwaku'else .059);rx,ry,rz=(.019,.015,.013)if key=='Kwaku'else(.022,.018,.014)
 ring=[i for i in boundary if abs(v[i].x-oldcx)<(.034 if key=='Kwaku'else .046)and abs(v[i].z-cz)<(.026 if key=='Kwaku'else .034)and v[i].y<-.03];assert len(ring)>12,(key,side,len(ring));ring.sort(key=lambda i:math.atan2((v[i].z-cz)/rz,(v[i].x-oldcx)/rx));N=len(ring);shift=cx-oldcx
 # Move the actual aperture boundary consistently with eye spacing; it is shared, not overlaid.
 for i in ring:
  v[i].x+=shift
  for q in shapes.values():q[i].x+=shift
 # Keep the actual eye/pupil bones, but inset the visible surface and conform iris to globe.
 eyeids=[i for ids in comps if dominant(ids)=='eye_'+side for i in ids];oldcentre=Vector((oldcx,-.0635 if key=='Kwaku'else-.129,cz));cy=(-.071 if key=='Kwaku'else-.132);centre=Vector((cx,cy,cz));eyecomps=[ids for ids in comps if dominant(ids)=='eye_'+side];eyecomps.sort(key=lambda q:q[0])
 for number,ids in enumerate(eyecomps):
  c=sum((v[i]for i in ids),Vector())/len(ids);bounds=[max(abs(v[i][a]-c[a])for i in ids)for a in range(3)];radii=(rx,ry,rz)if number==0 else((rx*(.54 if key=='Kwaku'else .48),.0012,rz*.84)if number==1 else(rx*(.24 if key=='Kwaku'else .12),.0007,rz*(.40 if key=='Kwaku'else .67)))
  for i in ids:
   p=v[i];q=centre+Vector(tuple((p[a]-c[a])*radii[a]/max(bounds[a],1e-8)for a in range(3)))
   if number>0:q.y=cy-ry*math.sqrt(max(.04,1-((q.x-cx)/rx)**2-((q.z-cz)/rz)**2))-.0003-number*.0001
   delta=q-v[i];v[i]=q
   for coords in shapes.values():coords[i]+=delta
 outer=[v[i].copy()for i in ring];inner=[]
 for p in outer:
  angle=math.atan2((p.z-cz)/rz,(p.x-cx)/rx);x=.91*rx*math.cos(angle);zz=rz*.48*math.sin(angle)*(.65+.35*abs(math.sin(angle)));y=cy-ry*math.sqrt(max(.04,1-(x/rx)**2-(zz/rz)**2))-.0004;inner.append(Vector((cx+x,y,cz+zz)))
 rings=[]
 for k in range(6):
  t=k/6;ids=[]
  for j,(a,z)in enumerate(zip(inner,outer)):
   point=a.lerp(z,t);alpha=((point.x-cx)/rx)**2+((point.z-cz)/rz)**2
   if alpha<1:point.y=min(point.y,cy-ry*math.sqrt(1-alpha)-.0005)
   index=len(v);v.append(point);weights.append({'head':1,'lid_'+side:1});ids.append(index)
   for coords in shapes.values():coords.append(point.copy())
   closed=point.copy();closed.z-=((a.z-cz)+.0015)*(1-t)**1.1;alpha=((closed.x-cx)/rx)**2+((closed.z-cz)/rz)**2
   if alpha<1:closed.y=min(closed.y,cy-ry*math.sqrt(1-alpha)-.001)
   newblink[index]=('Blink_'+side,closed)
  rings.append(ids)
 rings.append(ring)
 for a,z in zip(rings,rings[1:]):
  for j in range(N):f=[a[j],z[j],z[(j+1)%N],a[(j+1)%N]];faces.append(f);mat.append(skinmat);uv.append([(v[i].x*.2+.5,v[i].z*.45)for i in f])
# Remove the lower half of the old cap that read as a plastic helmet band.
if key=='Kwaku':
 cap=set(byfirst[41117]);keep=[j for j,f in enumerate(faces)if not(set(f).issubset(cap)and sum(v[i].z for i in f)/len(f)<(1.449 if sum(v[i].y for i in f)<0 else 1.435))];faces=[faces[j]for j in keep];mat=[mat[j]for j in keep];uv=[uv[j]for j in keep]
 for ids in comps:
  if len(ids)==448 and dominant(ids)=='head':
   c=sum((v[i]for i in ids),Vector())/len(ids)
   if c.z>1.46 and c.y<0 and math.sqrt(c.x*c.x+c.y*c.y)>.061:
    warp(ids,lambda p:p+Vector((0,0,-.012)))
# Delete unused old lid vertices, preserving all other positions/weights/UVs.
used=sorted({i for f in faces for i in f});remap={a:i for i,a in enumerate(used)};data=bpy.data.meshes.new(key+'_Pass2Surface');data.from_pydata([v[i]for i in used],[],[[remap[i]for i in f]for f in faces]);data.update();newobj=bpy.data.objects.new('Pass2_ActiveSurface',data);s.collection.objects.link(newobj)
for material in materials:data.materials.append(material)
for polygon,material in zip(data.polygons,mat):polygon.material_index=material;polygon.use_smooth=True
layer=data.uv_layers.new(name='UVMap')
for polygon,coords in zip(data.polygons,uv):
 for li,point in zip(polygon.loop_indices,coords):layer.data[li].uv=point
names={n for i in used for n in weights[i]};gs={n:newobj.vertex_groups.new(name=n)for n in names}
for oldindex in used:
 for name,w in weights[oldindex].items():
  if w>1e-8:gs[name].add([remap[oldindex]],w,'REPLACE')
newobj.parent=rig;newobj.modifiers.new('Skin','ARMATURE').object=rig;newobj.shape_key_add(name='Basis')
for name,coords in shapes.items():
 shape=newobj.shape_key_add(name=name)
 for oldindex in used:shape.data[remap[oldindex]].co=coords[oldindex]
for oldindex,(name,closed)in newblink.items():newobj.data.shape_keys.key_blocks[name].data[remap[oldindex]].co=closed
# Real mesh targets for mouth opening/phoneme range and startle, distinct from a single jaw pose.
for name in ['MouthOpen','Speech_A','Speech_O','Speech_M','FearStartle']:
 shape=newobj.shape_key_add(name=name);mouth=1.313 if key=='Kwaku'else 1.812;fw=.037 if key=='Kwaku'else.080
 for p in data.vertices:
  x,y,z=p.co;front=smooth((-y-.035)/(.06 if key=='Kwaku'else.10));region=gauss(x,0,fw)*gauss(z,mouth,.022 if key=='Kwaku'else.035)*front;delta=.004 if key=='Kwaku'else.007
  if name in ['MouthOpen','Speech_A']:shape.data[p.index].co.z+=delta*region*(1 if z>mouth else-1)
  elif name=='Speech_O':shape.data[p.index].co.x*=1-.13*region;shape.data[p.index].co.y-=delta*region
  elif name=='Speech_M':shape.data[p.index].co.z+=(mouth-z)*.30*region
  else:shape.data[p.index].co.z+=.004*gauss(z,(1.407 if key=='Kwaku'else 1.95),.018)*front;shape.data[p.index].co.z-=delta*region
# Remove obsolete visible mesh, retain original part sources hidden for provenance.
bpy.data.objects.remove(o,do_unlink=True);newobj.name='SK_'+key
for ob in s.objects:
 if ob.type=='MESH':ob.hide_render=ob!=newobj;ob.hide_set(ob!=newobj)
# Restrained mobile-friendly PBR variation, baked base colour; no new material slots.
rng=np.random.default_rng(407 if key=='Kwaku'else 905);W=1024;Y,X=np.mgrid[0:W,0:W];noise=rng.normal(0,1,(W,W));texpaths=[]
def image_texture(material_name,base,roughness,pattern=False):
 material=bpy.data.materials[material_name];node=material.node_tree.nodes.get('Principled BSDF');node.inputs['Roughness'].default_value=roughness;node.inputs['Metallic'].default_value=0 if 'Brass'not in material_name else .65
 if'Specular IOR Level'in node.inputs:node.inputs['Specular IOR Level'].default_value=.28
 arr=np.zeros((W,W,4),dtype=np.float32);arr[:,:,:3]=base;arr[:,:,:3]*=(1+noise[:,:,None]*.014);arr[:,:,3]=1
 if pattern:
  band=((X//52)%4);chev=np.abs(((X%104)-52)*.52+(Y%66)-33)<2;gold=(.48,.29,.085);arr[chev,:3]=gold;arr[(X%52<2),:3]=gold;arr[(Y%132<3),:3]=(.25,.14,.045);weave=((X%4==0)|(Y%4==0));arr[weave,:3]*=.84
 image=bpy.data.images.new(material_name+'_Pass2_Baked',W,W);image.pixels.foreach_set(arr.ravel());image.filepath_raw=str(out/(material_name+'_BaseColor.png'));image.file_format='PNG';image.save();image.pack();tex=material.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;tex.label='Editable baked base colour';material.node_tree.links.new(tex.outputs['Color'],node.inputs['Base Color']);texpaths.append(image.filepath_raw)
if key=='Kwaku':
 image_texture('Skin',(.135,.065,.035),.57);image_texture('Cream_Linen',(.56,.44,.29),.84);image_texture('IndigoWoven_v007',(.018,.035,.075),.82,True);image_texture('Indigo_Woven',(.018,.035,.075),.82,True)
 for name in ['Eyes','Amber','Hair_Pupil','Leather','LedgerPaper','LedgerClasp']:
  node=bpy.data.materials[name].node_tree.nodes.get('Principled BSDF');node.inputs['Roughness'].default_value=.25 if name in ['Eyes','Amber']else .7
 bpy.data.materials['Eyes'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.64,.59,.48,1)
else:
 # Irregular broken rosettes, not evenly repeated flower shapes.
 arr=np.zeros((W,W,4),dtype=np.float32);arr[:,:,:3]=(.55,.29,.075);arr[:,:,:3]*=(1+noise[:,:,None]*.035);arr[:,:,3]=1
 for i in range(2300):
  x,y=rng.uniform(0,W,2);rx=rng.uniform(5,12);ry=rx*rng.uniform(.65,1.35);x0,x1=max(0,int(x-rx*1.4)),min(W,int(x+rx*1.4+1));y0,y1=max(0,int(y-ry*1.4)),min(W,int(y+ry*1.4+1));dx=(X[y0:y1,x0:x1]-x)/rx;dy=(Y[y0:y1,x0:x1]-y)/ry;a=np.arctan2(dy,dx);rr=np.sqrt(dx*dx+dy*dy);edge=1+.12*np.sin(a*3+i)+.09*np.cos(a*5+i*.7);mask=(rr>edge*.65)&(rr<edge)&(np.sin(a*2.2+i)>-.72);arr[y0:y1,x0:x1,:3][mask]=(.055,.025,.010)
 image=bpy.data.images.new('Fur_Rosettes_Pass2',W,W);image.pixels.foreach_set(arr.ravel());image.filepath_raw=str(out/'Fur_Rosettes_BaseColor.png');image.file_format='PNG';image.save();image.pack();material=bpy.data.materials['Fur_Gold_Rosettes'];node=material.node_tree.nodes['Principled BSDF'];node.inputs['Roughness'].default_value=.78;tex=material.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;material.node_tree.links.new(tex.outputs['Color'],node.inputs['Base Color']);texpaths.append(image.filepath_raw)
 image_texture('Armour_Brown_Leather',(.105,.042,.018),.66);image_texture('Cape_Burgundy',(.105,.012,.022),.86)
 # Preserve the authored face cream mask while softening old high-contrast spot values.
 material=bpy.data.materials['FelineFaceSurface'];node=material.node_tree.nodes['Principled BSDF'];node.inputs['Roughness'].default_value=.76
 for n in material.node_tree.nodes:
  if n.type=='TEX_IMAGE'and n.image:
   img=n.image.copy();img.name='FelineFace_Pass2';pixels=np.array(img.pixels[:],dtype=np.float32).reshape((-1,4));raw=pixels[:,:3].copy();H,F=img.size[1],img.size[0];gold=np.array((.55,.29,.075));cream=np.array((.68,.56,.38));ratio=raw[:,2]/np.maximum(raw[:,0],.001);mask=np.clip((ratio-.31)/.23,0,1);pixels[:,:3]=gold[None,:]*(1-mask[:,None])+cream[None,:]*mask[:,None];yy,xx=np.mgrid[0:H,0:F];rngface=np.random.default_rng(702)
   for spot in range(110):
    sx,sy=rngface.uniform(0,F),rngface.uniform(0,H);rr=rngface.uniform(F*.009,F*.023);dy=(yy-sy)/rr;dx=(xx-sx)/(rr*.8);angle=np.arctan2(dy,dx);r=np.sqrt(dx*dx+dy*dy);spotmask=(r>.58)&(r<1+.10*np.sin(angle*3+spot))&(np.sin(angle*2+spot)>-.6);ids=np.flatnonzero(spotmask.ravel()&(mask<.45));pixels[ids,:3]=(.06,.025,.008)
   img.pixels.foreach_set(pixels.ravel());img.filepath_raw=str(out/'FelineFaceSurface.png');img.file_format='PNG';img.save();img.pack();n.image=img;texpaths.append(img.filepath_raw)
 for name in ['Eye_Sclera','Iris_Amber']:
  node=bpy.data.materials[name].node_tree.nodes['Principled BSDF'];node.inputs['Roughness'].default_value=.24
 bpy.data.materials['Eye_Sclera'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.46,.39,.24,1)
changes+=['Topology-joined eyelid annuli sharing actual face boundary vertices; inset conforming globe/iris','Five distinct mouth/startle targets added; not a complete speech performance','Baked original PBR colour/roughness separation, retained slot discipline']
assert rest==[(b.name,b.parent.name if b.parent else None,[list(r)for r in b.matrix_local])for b in rig.data.bones];assert actions==sorted(a.name for a in bpy.data.actions)
rig.animation_data.action=None;s.frame_set(0);bpy.ops.wm.save_as_mainfile(filepath=str(out/(key+'.blend')));bpy.ops.object.select_all(action='DESELECT');newobj.hide_set(False);newobj.select_set(True);rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(out/(key+'.glb')),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
p=out/(key+'.glb');raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);encoded=json.dumps(doc,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(encoded)+len(tail))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+tail)
if key=='Kwaku':shutil.copyfile(src/'Ledger.glb',out/'Ledger.glb')
(out/'art-pass2.json').write_text(json.dumps({'source_previous':str(src.relative_to(R)),'source_previous_sha256':hashlib.sha256((src/(key+'.blend')).read_bytes()).hexdigest(),'scene_sha256':hashlib.sha256((out/(key+'.blend')).read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'changes':changes,'rest_bones_unchanged':True,'actions_unchanged':actions,'source_vertices':len(data.vertices),'joined_lid_boundary':True,'textures':texpaths,'creative_approved':False,'proposed_decisions':['Subtle neutral lip fullness and coil irregularity','Four leopard digit chains retained; prior five-digit report was inaccurate']},indent=2)+'\n');print('ART_PASS2_AUTHORED',key,new,len(data.vertices))
