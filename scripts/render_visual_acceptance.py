"""Controlled views of exact saved character scenes; no creative pass inference."""
import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];key,revision,destination=args;source=R/'SourceArt/Characters'/key/revision/(key+'.blend');out=Path(destination);assert not out.exists();out.mkdir(parents=True);digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');parts=[o for o in s.objects if o.type=='MESH'and not o.hide_render];height=1.5 if key=='Kwaku'else 2.03;face=1.38 if key=='Kwaku'else 1.87
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=768;s.render.resolution_y=960;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1;s.world.color=(.055,.055,.055)
# CPU rendering is deliberate: no external services or pipeline acquisition.
s.cycles.device='CPU'
lights=[]
for name,loc,power,size in [('Review_Key',(-3,-4,4),450,4),('Review_Fill',(3,-2,2),250,3),('Review_Rim',(0,3,3),350,3)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,height*.55))-o.location).to_track_quat('-Z','Y').to_euler();lights.append({'name':name,'location':loc,'energy':power,'size':size})
cam=bpy.data.objects.new('Review_Camera',bpy.data.cameras.new('Review_Camera'));s.collection.objects.link(cam);s.camera=cam
wire=bpy.data.materials.new('Review_ActualEdges');wire.diffuse_color=(.005,.008,.012,1);wire.use_nodes=True;wire.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.005,.008,.012,1)
cyan=bpy.data.materials.new('Review_ActualBones');cyan.diffuse_color=(0,.85,.8,1);cyan.use_nodes=True;p=cyan.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(0,.85,.8,1);p.inputs['Emission Color'].default_value=(0,.4,.35,1);p.inputs['Emission Strength'].default_value=.6
sys.path.insert(0,str(R/'scripts'));import character_mesh_tools as g;g.scene=s;g.parts=[];g.binds={}
def pose(action=None,frame=0):
 rig.animation_data.action=None
 for b in rig.pose.bones:
  b.location=(0,0,0);b.scale=(1,1,1)
  if b.rotation_mode=='QUATERNION':b.rotation_quaternion=(1,0,0,0)
  else:b.rotation_euler=(0,0,0)
 for o in parts:
  if o.data.shape_keys:
   for k in o.data.shape_keys.key_blocks:k.value=0
 if action:rig.animation_data.action=bpy.data.actions[action]
 s.frame_set(frame);bpy.context.view_layer.update()
def prop_visibility(active):
 if key=='Kwaku'and 'Ledger_SeparateProp'in bpy.data.objects:bpy.data.objects['Ledger_SeparateProp'].hide_render=not active
views=[('front',(0,-4,height*.5),(0,0,height*.5),'ORTHO',height*1.22,None,0),('rear',(0,4,height*.5),(0,0,height*.5),'ORTHO',height*1.22,None,0),('left',(-4,0,height*.5),(0,0,height*.5),'ORTHO',height*1.22,None,0),('right',(4,0,height*.5),(0,0,height*.5),'ORTHO',height*1.22,None,0),('three_quarter',(-2.8,-4,height*.75),(0,0,height*.52),'PERSP',50,None,0),('dialogue',(0,-1.3,face),(0,-.02,face),'PERSP',85,None,0),('gameplay',(0,-3.4,height*.75),(0,0,height*.52),'PERSP',50,None,0),('movement',(-2.8,-4,height*.75),(0,0,height*.52),'PERSP',50,'Run'if key=='Kwaku'else'RunPursuit',18),('interaction',(-1.2,-2.8,height*.65),(0,-.1,height*.65),'PERSP',70,'InspectLedger'if key=='Kwaku'else'CaptureReach',35)]
manifest={'source':str(source.relative_to(R)),'source_sha256':digest,'reference':'Generated_Human_Cast_Lineup.png'if key=='Kwaku'else'Original_Four_Creatures.png','exposure':0,'view_transform':'AgX','look':s.view_settings.look,'lighting':lights,'resolution':[768,960],'views':{},'creative_approved':False}
for name,loc,target,typ,parameter,action,frame in views:
 pose(action,frame);prop_visibility(name=='interaction');cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type=typ
 if typ=='ORTHO':cam.data.ortho_scale=parameter
 else:cam.data.lens=parameter
 bpy.context.view_layer.update();manifest['views'][name]={'camera_world_matrix':[list(row)for row in cam.matrix_world],'type':typ,'parameter':parameter,'action':action,'frame':frame,'files':[]}
 def render(suffix):
  path=out/(name+'_'+suffix+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);manifest['views'][name]['files'].append({'path':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 render('solid')
 if name in ['front','rear','left','right','interaction','movement','dialogue']:
  mods=[]
  for o in parts:
   o.data.materials.append(wire);m=o.modifiers.new('ActualTopologyReview','WIREFRAME');m.thickness=.00035;m.use_replace=False;m.material_offset=len(o.data.materials)-1;mods.append((o,m))
  render('topology')
  for o,m in mods:o.modifiers.remove(m);o.data.materials.pop(index=len(o.data.materials)-1)
 if name in ['front','left','movement','interaction']:
  bones=[]
  for b in rig.pose.bones:
   a=rig.matrix_world@b.head;c=rig.matrix_world@b.tail;o=g.tube('ActualBone_'+b.name,[a,c],[.002,.0014],cyan,segments=6);bones.append(o)
  # Actual projected bones over translucent source are not an inferred skeleton.
  for o in parts:o.hide_render=True
  render('skeleton')
  for o in parts:o.hide_render=False
  for o in bones:bpy.data.objects.remove(o,do_unlink=True)
(out/'review-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');assert hashlib.sha256(source.read_bytes()).hexdigest()==digest;print('CONTROLLED_REVIEW_COMPLETE',key,revision)
