"""Add explicit wind/water masks to copies of editable scenery; original topology retained."""
import bpy,json,hashlib,math,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];base=R/'SourceArt/Environments/MarketSanctuary';out=base/'Motion_v001';out.mkdir(exist_ok='--resume-task-draft' in sys.argv)
jobs=[('HeroCells_v001','HeroCells.blend',['CanopySwag','Understory']),('HeroCells_v003','HeroCellsPass3.blend',['CrownGuardian','RiverFig','TwinnedElder']),('HeroCells_v004','HeroCellsPass4.blend',['RiverReach','StreamPools','LayeredGrove0','LayeredGrove1','LayeredGrove2','EcologyIsland','VerandaCorner'])];report=[]
for version,scene,names in jobs:
 source=base/version/scene;bpy.ops.wm.open_mainfile(filepath=str(source));records=[]
 for name in names:
  col=bpy.data.collections.get(name);assert col,name
  for o in col.objects:
   if o.type!='MESH':continue
   attr=o.data.color_attributes.new(name='MotionMask',type='FLOAT_COLOR',domain='POINT');mat=o.data.materials[0].name if o.data.materials else '';leaf='leaf' in o.name.lower()or'reed' in o.name.lower();branch=any(s in o.name.lower()for s in ['bough','branch','fork']);cloth='pennant'in o.name.lower()or'awning'in o.name.lower();water='water surface'in o.name.lower()
   n=len(o.data.vertices);zs=[v.co.z for v in o.data.vertices];lo=min(zs);hi=max(zs)
   for i,v in enumerate(o.data.vertices):
    r=g=b=a=0.
    if leaf:
     # Leaf is a nine-ring, three-vertex curved strip; base ring stays attached.
     g=(i//3)/8 if n==27 else max(0,min(1,(v.co.z-lo)/max(.001,hi-lo)))
     r=max(0,min(1,(v.co.z-.3)/10))**2
    if branch:r=max(0,min(1,(v.co.z-.3)/10))**2
    if cloth:a=max(0,min(1,(hi-v.co.z)/max(.001,hi-lo)))**2
    if water:
     assert n%5==0; b=math.sin(math.pi*(i//(n//5))/4)**2
    attr.data[i].color=(r,g,b,a)
   o.data.color_attributes.active_color=attr
   records.append({'object':o.name,'material':mat,'vertices':n,'mask_channels':['branch','leaf','water','cloth'],'moving_vertices':sum(any(x>0 for x in d.color)for d in attr.data)})
  bpy.ops.object.select_all(action='DESELECT');copies=[]
  for o in col.objects:
   if o.type=='MESH':
    c=o.copy();c.data=o.data.copy();bpy.context.scene.collection.objects.link(c);c.select_set(True);copies.append(c)
  bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
  path=out/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_animations=False,export_vertex_color='NAME',export_vertex_color_name='MotionMask',export_all_vertex_colors=False)
  data=path.read_bytes();n=struct.unpack_from('<I',data,12)[0];j=json.loads(data[20:20+n]);j['asset'].pop('generator',None);chunk=json.dumps(j,separators=(',',':')).encode();chunk+=b' '*(-len(chunk)%4);tail=data[20+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(chunk)+len(tail))+struct.pack('<II',len(chunk),0x4e4f534a)+chunk+tail)
  assert all('COLOR_0'in p['attributes']for m in j['meshes']for p in m['primitives']);bpy.data.objects.remove(o,do_unlink=True)
  report.append({'name':name,'source_version':version,'source_scene_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'parts':list(records)});records=[]
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/(version+'_Motion.blend')))
(out/'source-status.json').write_text(json.dumps({'creator':'Frank Asante Van Laarhoven','status':'masks_authored_pending_runtime_review','exports':report},indent=2))
