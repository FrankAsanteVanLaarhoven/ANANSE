"""Technical views from the pinned saved refined scene; never rewrite that scene."""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];revision=sys.argv[sys.argv.index('--')+1]if'--'in sys.argv else'Authored_v006';assert revision in {'Authored_v006','Authored_v008'};folder=root/'SourceArt/Characters/Kwaku'/revision;scene=folder/'Kwaku.blend';digest=hashlib.sha256(scene.read_bytes()).hexdigest();out=folder/('Technical_v001'if revision=='Authored_v008'else'Technical_v002');assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');mesh=next(o for o in s.objects if o.name=='SK_Kwaku');parts=[o for o in s.objects if o.type=='MESH'and o!=mesh];s.render.resolution_percentage=65;s.eevee.taa_render_samples=24;s.render.image_settings.file_format='PNG'
views={}
for name in ['front','left','right','back']:
 s.camera=bpy.data.objects[name];m=mesh.modifiers.new('ActualTriangleEdges','WIREFRAME');m.thickness=.00065;m.use_replace=True;s.render.filepath=str(out/(name+'_topology.png'));bpy.ops.render.render(write_still=True);views[name+'_topology']={'camera':[list(r)for r in s.camera.matrix_world]};mesh.modifiers.remove(m)
# Bone rods use only the source armature's actual rest head/tail values.
material=bpy.data.materials.new('BoneInspection');material.diffuse_color=(1,.2,.015,1);rods=[]
for bone in rig.data.bones:
 a=rig.matrix_world@bone.head_local;b=rig.matrix_world@bone.tail_local;d=b-a
 if d.length<.00001:continue
 bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.003,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name='ActualBone_'+bone.name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(material);rods.append(o)
mesh.hide_render=True;s.camera=bpy.data.objects['front'];s.render.filepath=str(out/'actual_skeleton.png');bpy.ops.render.render(write_still=True)
for o in rods:bpy.data.objects.remove(o,do_unlink=True)
# Exploded inspection uses actual saved accessory meshes, not a drawn overlay.
accessories=[o for o in parts if o.name.startswith(('Pouch_','DiagonalSash','FittedWovenSash','Tabard','Sandal'))];positions={o.name:o.location.copy()for o in accessories}
for i,o in enumerate(accessories):o.hide_render=False;o.location.x+=(-.35 if i%2 else .35)
s.render.filepath=str(out/'actual_accessories_exploded.png');bpy.ops.render.render(write_still=True)
for o in accessories:o.hide_render=True;o.location=positions[o.name]
mesh.hide_render=False;camera=bpy.data.objects['beauty'];s.camera=camera;s.render.resolution_percentage=50;s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.fps=12;s.frame_start=1;s.frame_end=24;matrices=[]
for frame in range(1,25):
 angle=(frame-1)*2*math.pi/24;camera.location=(3*math.sin(angle),-3*math.cos(angle),1.08);camera.rotation_euler=(Vector((0,0,.77))-camera.location).to_track_quat('-Z','Y').to_euler();camera.keyframe_insert('location',frame=frame);camera.keyframe_insert('rotation_euler',frame=frame);bpy.context.view_layer.update();matrices.append({'frame':frame,'camera':[list(r)for r in camera.matrix_world]})
s.render.filepath=str(out/'actual_turntable.mp4');bpy.ops.render.render(animation=True);assert hashlib.sha256(scene.read_bytes()).hexdigest()==digest
(out/'view-provenance.json').write_text(json.dumps({'source_scene_sha256':digest,'geometry_source':'Actual saved refined mesh/armature/accessories','source_units':'metres','source_bones':len(rig.data.bones),'source_vertices':len(mesh.data.vertices),'views':views,'turntable':matrices,'creative_approved':False,'technical_sheets_are_manufacturing_cad':False},indent=2)+'\n')
