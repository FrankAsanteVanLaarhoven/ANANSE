"""Save an editable inspection scene from the unchanged existing spider GLB.

No geometry generation, native reimport, joint renaming or runtime replacement.
"""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix

root=Path(__file__).resolve().parents[1]
source=root/'SourceArt/ANANSE_Spider_Character_Kit/assets/proxy-v001/AnanseSpider_PROXY.glb'
expected='1e94f6493d1c974c69722c9d5ca839bc3fcf87bd62e03225e1e6be8fa55e249e'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
native_reference='--native-reference' in sys.argv
if native_reference:
    reference=json.loads((root/'.local/verification/osebo-family-20261015/spider-native-export/spider-native-export.json').read_text())
    source=Path(reference['fbx_path']);expected=reference['fbx_sha256']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
out=root/'SourceArt/Characters/AnanseSpider'/('NativeReference_v001/EditableScene_v002' if native_reference else 'ImportedSource_v002');out.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30
if native_reference:bpy.ops.import_scene.fbx(filepath=str(source),automatic_bone_orientation=False,ignore_leaf_bones=False)
else:bpy.ops.import_scene.gltf(filepath=str(source))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
native_bones={b['name'] for b in json.loads((root/'SourceArt/Characters/AnanseSpider/NATIVE_RIG_MAP_20261015.json').read_text())['bones']}
source_bones=set(rig.data.bones.keys())
if native_reference:
    assert native_bones-source_bones=={'root'} and not source_bones-native_bones and len(source_bones)==101
else:assert len(rig.data.bones)==102
if rig.animation_data:
    rig.animation_data.action=None
    for track in rig.animation_data.nla_tracks:track.mute=True
if not native_reference:
    for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
scene=bpy.context.scene;scene.frame_set(0);scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['design_id']='ananse-spider-existing';scene['source_reference_sha256']=expected
if native_reference:scene['native_root_representation']='Native root is represented by the imported armature object; 101 remaining bones retain exact native names. Native reimport not qualified.'
scene['art_status']='Existing engineering proxy, not final reference-faithful art'
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=900;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.fps=30
scene.world=bpy.data.worlds.new('InspectionWorld');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.11,.13,.17,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size in [('Key',(-3,-4,5),650,4),('Fill',(3,-2,3),400,3),('Rim',(1,3,4),900,3)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,1.1))
cameras={}
face=(rig.matrix_world@rig.pose.bones['jaw'].head)-(rig.matrix_world@rig.pose.bones['head'].head);face.z=0;face.normalize()
left=(rig.matrix_world@rig.pose.bones['hand_upper_l'].head)-(rig.matrix_world@rig.pose.bones['hand_upper_r'].head);left.z=0;left.normalize()
locations=[('front',face*5),('left',left*5),('right',-left*5),('back',-face*5),('beauty',face*5+left*3)]
for name,delta in locations:
    loc=(delta.x,delta.y,2.5 if name=='beauty' else 1.1)
    data=bpy.data.cameras.new(name);data.type='ORTHO';data.ortho_scale=2.7
    o=bpy.data.objects.new('Camera_'+name,data);scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,1.05));cameras[name]=o
scene.camera=cameras['beauty'];bpy.ops.wm.save_as_mainfile(filepath=str(out/'AnanseSpider_Existing.blend'))
meshes=[o for o in scene.objects if o.type=='MESH'];coords=[];graph=bpy.context.evaluated_depsgraph_get()
for obj in meshes:
    evaluated=obj.evaluated_get(graph);data=evaluated.to_mesh()
    coords.extend(evaluated.matrix_world@v.co for v in data.vertices);evaluated.to_mesh_clear()
dimensions=[max(v[i] for v in coords)-min(v[i] for v in coords) for i in range(3)]
native=json.loads((root/'SourceArt/Characters/AnanseSpider/NATIVE_RIG_MAP_20261015.json').read_text())['imported_bounds_extent_cm']
assert abs(dimensions[2]-native[2]*.02)<.001 and all(abs(a-b)<.001 for a,b in zip(sorted(dimensions[:2]),sorted([native[0]*.02,native[1]*.02]))),'Evaluated source bounds differ from native reference'
for name,camera in cameras.items():scene.camera=camera;scene.render.filepath=str(out/(name+'_solid.png'));bpy.ops.render.render(write_still=True)
(out/'source-conversion.json').write_text(json.dumps(dict(source=str(source),source_reference_sha256=expected,source_format='native FBX export' if native_reference else 'original GLB',
    scene_sha256=hashlib.sha256((out/'AnanseSpider_Existing.blend').read_bytes()).hexdigest(),
    status='EXISTING_SOURCE_CONVERTED_FOR_INSPECTION',native_reimported=False,new_proxy_generated=False,
    bone_count=len(rig.data.bones),bone_names=[b.name for b in rig.data.bones],
    native_bone_count=102,native_root_representation='armature object' if native_reference else 'bone',native_reimport_qualified=False,
    evaluated_dimensions_metres=dimensions,measurement='evaluated skinned vertices, not raw mesh buffer',
    fps=scene.render.fps,actions=[dict(name=a.name,seconds=(a.frame_range[1]-a.frame_range[0])/scene.render.fps) for a in bpy.data.actions],
    cameras={n:dict(matrix_world=[list(row) for row in o.matrix_world],ortho_scale=o.data.ortho_scale) for n,o in cameras.items()},
    art_approved=False),indent=2)+'\n')
