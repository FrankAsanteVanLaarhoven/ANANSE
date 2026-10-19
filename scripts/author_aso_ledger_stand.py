"""Editable small evidence table; separate non-blocking presentation prop."""
import bpy,sys,json,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=R/'SourceArt/Characters/AsoYaa/Props_v002';assert not out.exists();out.mkdir();bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g;g.scene=s
wood=g.material('EvidenceStand_Wood',(.12,.055,.024),rough=.7);gold=g.material('EvidenceStand_Brass',(.42,.24,.065),metal=.6,rough=.4)
for x in [-.135,.135]:
 for y in [-.09,.09]:g.loft('TaperedLeg',[(x,y,.02,.018,.018),(x,y,.1,.016,.016),(x,y,.84,.012,.012),(x,y,.9885,.022,.022)],wood,'None',segments=12)
for name,z,dims,mat in [('TableTop',.9995,(.36,.26,.034),wood),('BrassEdge',1.0125,(.365,.265,.006),gold)]:
 bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.name=name;o.scale=dims;o.location.z=z;o.data.materials.append(mat);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bevel=o.modifiers.new('CarvedEdge','BEVEL');bevel.width=.008;bevel.segments=3;bpy.ops.object.modifier_apply(modifier=bevel.name)
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=next(o for o in s.objects if o.type=='MESH');bpy.ops.object.join();obj=bpy.context.object;obj.name='LedgerStand';bpy.ops.wm.save_as_mainfile(filepath=str(out/'LedgerStand.blend'));p=out/'LedgerStand.glb';bpy.ops.export_scene.gltf(filepath=str(p),use_selection=True,export_format='GLB',export_animations=False);raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);d['asset'].pop('generator',None);data=json.dumps(d,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
