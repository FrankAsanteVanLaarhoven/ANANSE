"""Editable cantilevered receiving support; keeps the existing book/top height."""
import bpy,json,struct,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=R/'SourceArt/Characters/AsoYaa/Props_v003';assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(R/'SourceArt/Characters/AsoYaa/Props_v002/LedgerStand.blend'));s=bpy.context.scene;obj=next(o for o in s.objects if o.type=='MESH')
# Keep the tabletop exactly fixed. Move the receiving support legs ahead of the
# garment envelope; upper struts return to the existing tabletop attachment.
for v in obj.data.vertices:
 z=v.co.z
 if z<.99:
  a=max(0,min(1,(.99-z)/.30));a=a*a*(3-2*a);v.co.y-=.36*a
sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g;g.scene=s
bpy.ops.mesh.primitive_cube_add(size=1);base=bpy.context.object;base.name='CounterweightBase';base.location=(0,-.36,.03);base.scale=(.44,.40,.045);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);base.data.materials.append(bpy.data.materials['EvidenceStand_Wood']);bevel=base.modifiers.new('RoundedBase','BEVEL');bevel.width=.012;bevel.segments=3;bpy.ops.object.modifier_apply(modifier=bevel.name)
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);base.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.join();obj.name='LedgerStand';bpy.ops.wm.save_as_mainfile(filepath=str(out/'LedgerStand.blend'));p=out/'LedgerStand.glb';bpy.ops.export_scene.gltf(filepath=str(p),use_selection=True,export_format='GLB',export_animations=False);raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);doc['asset'].pop('generator',None);data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(raw[20+n:]))+struct.pack('<II',len(data),0x4e4f534a)+data+raw[20+n:]);(out/'support.json').write_text(json.dumps({'scene_sha256':hashlib.sha256((out/'LedgerStand.blend').read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'role':'Nonblocking lab receiving fixture; tabletop unchanged, cantilever legs and counterweight clear garment. Visual support, not load-bearing pawn physics.','creative':'REVIEW_REQUIRED'},indent=2)+'\n')
