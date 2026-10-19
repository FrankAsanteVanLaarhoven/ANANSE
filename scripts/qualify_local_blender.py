"""Qualify portable DCC scene persistence and metre-to-glTF dimension export."""
import bpy, json, sys, hashlib
from pathlib import Path
from mathutils import Vector

out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
out.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=1
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,1))
obj=bpy.context.object;obj.name='TwoMetreDimensionProbe';obj.dimensions=(.5,.75,2)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'dimension-probe.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'dimension-probe.blend'))
obj=bpy.data.objects['TwoMetreDimensionProbe']
assert all(abs(a-b)<1e-6 for a,b in zip(obj.dimensions,(.5,.75,2)))
bpy.ops.export_scene.gltf(filepath=str(out/'dimension-probe.glb'),export_format='GLB',export_yup=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(out/'dimension-probe.glb'))
obj=next(o for o in bpy.context.scene.objects if o.type=='MESH')
coords=[obj.matrix_world@Vector(v) for v in obj.bound_box]
dims=[max(v[i] for v in coords)-min(v[i] for v in coords) for i in range(3)]
assert all(abs(a-b)<1e-5 for a,b in zip(dims,(.5,.75,2)))
(out/'qualification.json').write_text(json.dumps(dict(status='passed',version=bpy.app.version_string,
    scene_saved_reopened=True,glb_saved_reimported=True,dimensions_metres=dims,
    native_centimetres_expected=[50,75,200],native_import_tested=False,
    scene_sha256=hashlib.sha256((out/'dimension-probe.blend').read_bytes()).hexdigest(),
    glb_sha256=hashlib.sha256((out/'dimension-probe.glb').read_bytes()).hexdigest()),indent=2)+'\n')
