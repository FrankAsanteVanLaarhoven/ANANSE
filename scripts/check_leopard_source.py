"""Inspect saved source weights, UVs and evaluated deformations, without editing it."""
import bpy,sys,json,math,hashlib
from pathlib import Path

source=Path(sys.argv[sys.argv.index('--')+1]).resolve()
report=Path(sys.argv[sys.argv.index('--')+2]).resolve()
if report.exists():raise RuntimeError('Preserve previous source evidence')
bpy.ops.wm.open_mainfile(filepath=str(source))
rig=bpy.data.objects['SKEL_OseboLeopard'];meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len([b for b in rig.data.bones if not b.parent])==1
names=['IdleGuard','Patrol','RunPursuit','TurnStop','Investigate','CaptureReach','StaggerRecover','Command','LimbIsolation']
assert {a.name for a in bpy.data.actions}==set(names)
maximum=0;vertices=0;triangles=0
for o in meshes:
    assert len(o.data.uv_layers)>0 and len(o.data.materials)>0
    for v in o.data.vertices:
        w=[g.weight for g in v.groups if g.weight>0]
        assert w and all(math.isfinite(x) and x>=0 for x in w) and abs(sum(w)-1)<1e-5
        assert all(o.vertex_groups[g.group].name in rig.data.bones for g in v.groups)
        maximum=max(maximum,len(w))
    o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles);vertices+=len(o.data.vertices)
assert maximum<=4
samples=0
for name in names:
    rig.animation_data.action=bpy.data.actions[name]
    for factor in [0,.25,.5,.75,1]:
        bpy.context.scene.frame_set(int(rig.animation_data.action.frame_range[1]*factor))
        graph=bpy.context.evaluated_depsgraph_get()
        for obj in meshes:
            evaluated=obj.evaluated_get(graph);data=evaluated.to_mesh()
            assert all(all(math.isfinite(x) for x in v.co) for v in data.vertices)
            evaluated.to_mesh_clear()
        samples+=1
report.write_text(json.dumps(dict(status='source_structural_checks_passed',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    parts=len(meshes),vertices=vertices,triangles=triangles,bones=len(rig.data.bones),
    maximum_positive_influences=maximum,normalised_weights=True,unweighted_vertices=0,
    actions=names,evaluated_action_pose_samples=samples,invalid_evaluated_vertices=0,
    uv_layers_present=True,lod_count=1,creative_approval=False,
    limitations=['No runtime contact measurement','Finite deformation is not visual joint-limit acceptance','Reduced LODs not authored']),indent=2)+'\n')
