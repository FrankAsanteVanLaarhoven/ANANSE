"""Read saved source scenes and render actual topology/bones/poses and turntable."""
import bpy,math,sys,json,hashlib,subprocess,shutil
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];key=sys.argv[sys.argv.index('--')+1];folder=root/'SourceArt/Characters'/key/('Authored_v002'if key=='Kwaku'else'Authored_v001');source=folder/(key+'.blend');out=folder/'Technical_v001'
if out.exists():raise RuntimeError('Preserve technical views')
out.mkdir();before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.eevee.taa_render_samples=16;s.render.resolution_percentage=65;s.render.image_settings.file_format='PNG';parts=[o for o in s.objects if o.type=='MESH'];rig=next(o for o in s.objects if o.type=='ARMATURE');cameras={n:next(o for o in s.objects if o.type=='CAMERA'and o.name==n)for n in ['front','left','right','back','beauty']}
for side in ['left','back']:
 mods=[]
 for o in parts:mod=o.modifiers.new('ActualMeshEdges','WIREFRAME');mod.thickness=.0008;mod.use_replace=True;mods.append((o,mod))
 s.camera=cameras[side];s.render.filepath=str(out/(side+'_topology.png'));bpy.ops.render.render(write_still=True)
 for o,mod in mods:o.modifiers.remove(mod)
# Render overlay rods directly from actual saved bone head/tail matrices.
bone_mat=bpy.data.materials.new('InspectionBone');bone_mat.diffuse_color=(1,.35,.01,1);rods=[]
for b in rig.data.bones:
 a=rig.matrix_world@b.head_local;c=rig.matrix_world@b.tail_local;direction=c-a
 if direction.length<.0001:continue
 bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.003,depth=direction.length,location=(a+c)/2);o=bpy.context.object;o.name='ActualBone_'+b.name;o.rotation_euler=direction.to_track_quat('Z','Y').to_euler();o.data.materials.append(bone_mat);rods.append(o)
for o in parts:o.hide_render=True
s.camera=cameras['front'];s.render.filepath=str(out/'skeleton_actual.png');bpy.ops.render.render(write_still=True)
for o in rods:bpy.data.objects.remove(o,do_unlink=True)
for o in parts:o.hide_render=False
for side in ['L','R']:
 rig.pose.bones['upperarm_'+side].rotation_mode='XYZ';rig.pose.bones['upperarm_'+side].rotation_euler.x=-.9;rig.pose.bones['lowerarm_'+side].rotation_euler.x=-.7
s.camera=cameras['beauty'];s.render.filepath=str(out/'joint_review_pose.png');bpy.ops.render.render(write_still=True)
for b in rig.pose.bones:b.rotation_euler=(0,0,0)
# Actual scene geometry rotating camera, exported with local ffmpeg only.
cam=cameras['beauty'];height=json.loads((folder/'rig-map.json').read_text())['height_proposal_m'];positions=[]
for i in range(24):
 a=i*2*math.pi/24;cam.location=(4*math.sin(a),-4*math.cos(a),height*.75);cam.rotation_euler=(Vector((0,0,height*.52))-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam;s.render.filepath=str(out/f'turn_{i:03d}.png');bpy.ops.render.render(write_still=True);positions.append([list(r)for r in cam.matrix_world])
if shutil.which('ffmpeg'):
 subprocess.run(['ffmpeg','-v','error','-framerate','12','-i',str(out/'turn_%03d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-metadata','encoder=','-metadata','artist=Frank Asante Van Laarhoven',str(out/'turntable.mp4')],check=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
(out/'view-provenance.json').write_text(json.dumps({'source_scene_sha256':before,'geometry_source':'Saved editable scene; no generated illustration','camera_matrices':positions,'creative_approved':False,'joint_limits_approved':False,'technical_sheets_are_manufacturing_cad':False},indent=2)+'\n')
