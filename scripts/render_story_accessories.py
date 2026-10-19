"""Model-derived exploded accessories and neutral static inspection geometry."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
for key in ['Kwaku','AsoYaa','EsiHuman','OseboHuman','KojoTortoise','KofiHornbill','EsiMoth']:
 folder=ROOT/'SourceArt/Characters'/key/('Authored_v002'if key=='Kwaku'else'Authored_v001');scene=folder/(key+'.blend');before=hashlib.sha256(scene.read_bytes()).hexdigest();out=folder/'Technical_v001';assert not(out/'accessories_exploded.png').exists();bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;s.eevee.taa_render_samples=16;s.render.resolution_percentage=70;parts=[o for o in s.objects if o.type=='MESH']
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];obj=out/(key+'_Inspection.obj');bpy.ops.wm.obj_export(filepath=str(obj),export_selected_objects=True)
 for p in [obj,obj.with_suffix('.mtl')]:
  if p.exists():p.write_text(''.join(l for l in p.read_text().splitlines(True)if not l.startswith('# Blender')))
 moved=[]
 for o in parts:
  name=o.name;delta=None
  if key=='KojoTortoise':
   if name.startswith(('RigidShell','ShellScute')):delta=(0,.65,0)
   elif name.startswith('Staff'):delta=(.55,0,0)
   elif name.startswith(('Apron','Woven')):delta=(-.45,0,0)
  elif key=='KofiHornbill':
   if name.startswith('WingFeather_'):delta=(-.30 if '_L'in name else .30,0,0)
   elif name.startswith('Satchel'):delta=(-.5,0,0)
   elif name.startswith('Optical'):delta=(.5,0,0)
   elif name.startswith('TailFeather'):delta=(0,.5,0)
  elif key=='EsiMoth':
   if name.startswith(('upperwing_','hindwing_')):delta=(-.3 if '_L'in name else .3,0,0)
   elif name.startswith('Garment'):delta=(.45,0,0)
  elif key=='OseboHuman':
   if name.startswith('Cape'):delta=(-.5,0,0)
   elif name.startswith(('FittedArmour','ArmourSkirt')):delta=(.5,0,0)
  else:
   if name.startswith('Instrument')or name.startswith('String'):delta=(.6,0,0)
   elif name.startswith('Headwrap'):delta=(0,0,.45)
   elif name.startswith(('Dress','Robe','Bodice','Tabard','DiagonalSash','SashWoven','BeltPouch','Linen_Shirt','CroppedTrousers')):delta=(-.5,0,0)
  if delta:o.location+=Vector(delta);moved.append({'part':name,'offset_metres':delta})
 camera=next(o for o in s.objects if o.type=='CAMERA'and o.name=='beauty');camera.data.ortho_scale*=1.8;s.camera=camera;s.render.filepath=str(out/'accessories_exploded.png');bpy.ops.render.render(write_still=True);assert hashlib.sha256(scene.read_bytes()).hexdigest()==before
 (out/'exploded-provenance.json').write_text(json.dumps({'source_scene_sha256':before,'camera_matrix':[list(r)for r in camera.matrix_world],'ortho_scale':camera.data.ortho_scale,'moved_actual_mesh_parts':moved,'source_modified':False,'manufacturing_cad':False,'creative_approved':False},indent=2)+'\n')
print('Seven actual-model accessory views and inspection meshes saved')
