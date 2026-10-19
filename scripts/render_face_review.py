"""Named facial targets from exact saved scenes; absent speech controls remain absent."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];key=sys.argv[sys.argv.index('--')+1];tag=sys.argv[sys.argv.index('--')+2]if len(sys.argv)>sys.argv.index('--')+2 else ''; b=R/'.local/verification/visual-acceptance-20261016';m=json.loads((b/(key+'-selected'+tag+'/review-manifest.json')).read_text());p=R/m['source'];assert hashlib.sha256(p.read_bytes()).hexdigest()==m['source_sha256'];out=b/(key+'-face'+tag);assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');mesh=bpy.data.objects['SK_'+key];rig.animation_data.action=None
for bone in rig.pose.bones:bone.rotation_euler=(0,0,0);bone.location=(0,0,0);bone.scale=(1,1,1)
s.frame_set(0)
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
for row in m['lighting']:
 light=bpy.data.lights.new('Review_'+row['name'],'AREA');light.energy=row['energy'];light.shape='DISK';light.size=row['size'];o=bpy.data.objects.new(light.name,light);s.collection.objects.link(o);o.location=row['location'];height=1.5 if key=='Kwaku'else 2.03;o.rotation_euler=(Vector((0,0,height*.55))-o.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=768;s.render.resolution_y=960;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look=m['look'];s.view_settings.exposure=0;s.view_settings.gamma=1;s.world.color=(.055,.055,.055);cam=bpy.data.objects.new('FaceReview',bpy.data.cameras.new('FaceReview'));s.collection.objects.link(cam);cam.matrix_world=Matrix(m['views']['dialogue']['camera_world_matrix']);cam.data.lens=85;s.camera=cam
cases=['Neutral','Blink','BrowUp','BrowDown','Concern','Suspicion','Determination','EyesLeft','EyesRight','EyesUp','EyesDown'];rows=[]
for case in cases:
 for shape in mesh.data.shape_keys.key_blocks:shape.value=0
 for side in ['L','R']:
  rig.pose.bones['eye_'+side].rotation_euler=(0,0,0)
 if case=='Blink':
  for side in ['L','R']:mesh.data.shape_keys.key_blocks['Blink_'+side].value=1
 elif case.startswith('Eyes'):
  direction=case[4:]
  for side in ['L','R']:rig.pose.bones['eye_'+side].rotation_euler=(.12 if direction=='Up'else -.12 if direction=='Down'else 0,0,.12 if direction=='Left'else -.12 if direction=='Right'else 0)
 else:
  shape=mesh.data.shape_keys.key_blocks.get(case)
  if shape:shape.value=1
 bpy.context.view_layer.update();s.render.filepath=str(out/(case+'.png'));bpy.ops.render.render(write_still=True);rows.append({'case':case,'path':case+'.png','sha256':hashlib.sha256((out/(case+'.png')).read_bytes()).hexdigest()})
(out/'face-review.json').write_text(json.dumps({'source_sha256':m['source_sha256'],'camera':m['views']['dialogue'],'cases':rows,'missing_required_controls':['MouthOpenClose','speech shape range','FearStartle'],'facial_animation_complete':False,'human_creative_approval':False},indent=2)+'\n')
