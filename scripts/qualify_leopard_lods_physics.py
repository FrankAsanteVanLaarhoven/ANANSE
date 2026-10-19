"""Back up the prior native revision, then generate bounded LODs and physics policy."""
import hashlib,json,os,shutil
from pathlib import Path
import unreal
root=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);report=out/'quality.json'
backup=out/'native-before-quality';source=root/'Unreal/Content/Ananse/Characters/OseboLeopard'
if report.exists() or backup.exists():raise RuntimeError('Prior evidence/backup preserved')
shutil.copytree(source,backup)
hashes={str(p.relative_to(backup)):hashlib.sha256(p.read_bytes()).hexdigest() for p in backup.rglob('*') if p.is_file()}
(out/'backup-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
mesh=unreal.load_asset('/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard');assert isinstance(mesh,unreal.SkeletalMesh)
before=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(mesh));assert before['lod_count']==1
error=unreal.AnanseAnimationAuthoring.prepare_leopard_quality(mesh)
if error is None or (isinstance(error,str) and error):raise RuntimeError('Quality preparation failed: '+str(error))
sub=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
assert sub.regenerate_lod(mesh,3,True,False),'Installed mesh-reduction provider did not generate the requested LODs'
after=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(mesh));lods=after['lods']
assert len(lods)==3 and lods[0]['triangles']==before['lods'][0]['triangles']
assert 0<lods[2]['triangles']<lods[1]['triangles']<lods[0]['triangles']
assert all(0<x['max_influences']<=4 for x in lods)
bodies=after['physics_bodies'];assert len(bodies)==23 and all(b['kinematic'] for b in bodies)
assert all(b['collision_disabled']==b['bone'].startswith(('cape_','tail_')) for b in bodies)
assert unreal.EditorAssetLibrary.save_loaded_asset(mesh.get_editor_property('physics_asset'))
assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
report.write_text(json.dumps(dict(status='generated_saved_pending_reopen_and_visual_review',before=before,after=after,
 policy='Normal movement uses capsule; all23 skeletal bodies kinematic. Cape/tail bodies disabled. Dynamic ragdoll not approved.',
 creative_review_approved=False,deformation_review_approved=False,backup_files=len(hashes)),indent=2)+'\n')
