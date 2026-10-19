"""Render technical sheets and a turntable from an existing saved source scene."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector

args=sys.argv[sys.argv.index('--')+1:]
source=Path(args[0]).resolve()
out=source.parent/(args[1] if len(args)>1 else 'technical')
out.mkdir(exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
parts=[o for o in scene.objects if o.type=='MESH']
rig=next(o for o in scene.objects if o.type=='ARMATURE')
assert len(rig.data.bones) in [64,102] or (len(rig.data.bones)==101 and 'native_root_representation' in scene)
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=800;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.display.shading.light='FLAT';scene.display.shading.color_type='OBJECT'
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.display.shading.background_type='WORLD';scene.world.color=(.8,.8,.8)
for o in parts:o.color=(.015,.015,.015,1)
scene.render.image_settings.file_format='PNG'
records=[]
for view in ['front','left','right','back']:
    scene.camera=bpy.data.objects['Camera_'+view]
    # Real edges of the saved mesh, no illustrative wire-line synthesis.
    mods=[]
    for o in parts:
        m=o.modifiers.new('TopologyEdges','WIREFRAME')
        # FBX inspection meshes can retain centimetre object scale. Keep actual
        # rendered edge width in world metres rather than almost invisible local units.
        m.thickness=.0015/max(abs(v) for v in o.matrix_world.to_scale())
        m.use_replace=True;mods.append((o,m))
    scene.render.filepath=str(out/(view+'_topology.png'));bpy.ops.render.render(write_still=True)
    for o,m in mods:o.modifiers.remove(m)
    records.append(dict(view=view,type='actual saved base topology',camera=[list(row) for row in scene.camera.matrix_world]))
# Skeleton overlays use actual saved rest matrices/head/tail positions.
for o in parts:o.hide_render=True
for b in rig.data.bones:
    data=bpy.data.curves.new('Bone_'+b.name,'CURVE');data.dimensions='3D';data.bevel_depth=.004;data.bevel_resolution=1
    spline=data.splines.new('POLY');spline.points.add(1)
    for point,co in zip(spline.points,[rig.matrix_world@b.head_local,rig.matrix_world@b.tail_local]):point.co=(*co,1)
    obj=bpy.data.objects.new('Bone_'+b.name,data);scene.collection.objects.link(obj)
    obj.color=(.02,.02,.02,1)
scene.camera=bpy.data.objects['Camera_front'];scene.render.filepath=str(out/'skeleton_front.png');bpy.ops.render.render(write_still=True)
for o in list(scene.objects):
    if o.name.startswith('Bone_'):bpy.data.objects.remove(o,do_unlink=True)
for o in parts:o.hide_render=False
scene.render.engine='BLENDER_EEVEE_NEXT'
# Saved actions are rendered at known frames; these are authored pose samples,
# not a claim that anatomical joint limits or contacts were accepted.
poses=[('CaptureReach',30),('Command',45),('LimbIsolation',120)] if len(rig.data.bones)==64 else [(next(a.name for a in bpy.data.actions if token in a.name),30) for token in ['LimbROM','Weave','Crawl'] if any(token in a.name for a in bpy.data.actions)]
for name,frame in poses:
    rig.animation_data.action=bpy.data.actions[name];scene.frame_set(frame)
    scene.camera=bpy.data.objects['Camera_beauty'];scene.render.filepath=str(out/(name+'_pose.png'));bpy.ops.render.render(write_still=True)
if poses:
    rig.animation_data.action=None
    for b in rig.pose.bones:b.rotation_euler=(0,0,0)
scene.frame_set(0)
scene.render.resolution_x=640;scene.render.resolution_y=720
camera=bpy.data.objects['Camera_beauty'];scene.camera=camera
for frame in range(1,61):
    a=2*math.pi*(frame-1)/60;camera.location=(4*math.sin(a),-4*math.cos(a),1.65)
    camera.rotation_euler=(Vector((0,0,1.05))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.keyframe_insert('location',frame=frame);camera.keyframe_insert('rotation_euler',frame=frame)
scene.frame_start=1;scene.frame_end=60
scene.render.image_settings.file_format='FFMPEG';scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264'
scene.render.filepath=str(out/'turntable.mp4');bpy.ops.render.render(animation=True)
(out/'technical-views.json').write_text(json.dumps(dict(source_scene_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    views=records,bone_count=len(rig.data.bones),pose_samples='not joint-limit acceptance',
    sheet_type='visual technical sheets, not manufacturing CAD',pose_samples_included=len(poses),turntable_frames=60,source_modified=False),indent=2)+'\n')
