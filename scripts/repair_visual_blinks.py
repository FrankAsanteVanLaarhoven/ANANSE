"""Cover the actual globe through the whole closed lid; preserve original surfaces/rigs."""
import bpy,json,hashlib,struct,shutil,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for key,old,new in [('Kwaku','Authored_v022','Authored_v023'),('OseboLeopard','Authored_v010','Authored_v011')]:
 root=R/'SourceArt/Characters'/key;src=root/old;out=root/new;assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(src/(key+'.blend')));mesh=bpy.data.objects['SK_'+key];rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data.action=None
 for side in ['L','R']:
  eye=bpy.data.objects['Eye_'+side];centre=sum((v.co for v in eye.data.vertices),Vector())/len(eye.data.vertices);rx,ry,rz=[max(abs(v.co[i]-centre[i])for v in eye.data.vertices)for i in range(3)];shape=mesh.data.shape_keys.key_blocks['Blink_'+side];group=mesh.vertex_groups['lid_'+side]
  for v in mesh.data.vertices:
   if any(a.group==group.index and a.weight>.5 for a in v.groups):
    p=shape.data[v.index].co;alpha=((p.x-centre.x)/rx)**2+((p.z-centre.z)/rz)**2
    if alpha<1:p.y=min(p.y,centre.y-ry*math.sqrt(1-alpha)-.003)
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(key+'.blend')));bpy.ops.object.select_all(action='DESELECT');mesh.hide_set(False);mesh.select_set(True);rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(out/(key+'.glb')),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
 p=out/(key+'.glb');raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);d['asset'].pop('generator',None);data=json.dumps(d,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
 for filename in ['Ledger.glb','FelineFaceSurface.png']:
  if(src/filename).exists():shutil.copyfile(src/filename,out/filename)
 report=json.loads((src/'visual-corrections.json').read_text());report.update(scene_sha256=hashlib.sha256((out/(key+'.blend')).read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),blink_fix='All closed-lid vertices inside actual eye ellipse are placed in front of the globe; whole-eye occlusion still measured separately');(out/'visual-corrections.json').write_text(json.dumps(report,indent=2)+'\n');print('CLOSED_LID_SURFACE_REPAIRED',key,new)
