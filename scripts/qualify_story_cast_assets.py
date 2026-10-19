"""Reopen every new family's real assets and apply bounded engineering LOD/physics policy."""
import unreal,json,os,shutil,hashlib,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=Path(os.environ['ANANSE_EVIDENCE_DIR']);OUT.mkdir(parents=True,exist_ok=True);report=OUT/'cast-quality.json'
if report.exists():raise RuntimeError('Preserve earlier results')
results=[]
try:
 for key in ['Kwaku','AsoYaa','EsiHuman','OseboHuman','KojoTortoise','KofiHornbill','EsiMoth']:
  source=ROOT/'.local/verification/story-cast-20261015'/('native-'+key)/(key+'-native.json');r=json.loads(source.read_text());mesh=unreal.load_asset(r['mesh']);assert isinstance(mesh,unreal.SkeletalMesh)
  backup=OUT/'before-quality'/key;shutil.copytree(ROOT/'Unreal/Content/Ananse/Characters'/key/'Story_v001',backup)
  before=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(mesh));assert before['lod_count']==1
  error=unreal.AnanseAnimationAuthoring.prepare_leopard_quality(mesh);assert error is not None and not error,str(error)
  assert unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem).regenerate_lod(mesh,3,True,False)
  after=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(mesh));assert len(after['lods'])==3;assert after['lods'][0]['triangles']>after['lods'][1]['triangles']>after['lods'][2]['triangles']>0;assert all(0<lod['max_influences']<=4 for lod in after['lods']);assert all(b['kinematic']for b in after['physics_bodies'])
  assert unreal.EditorAssetLibrary.save_loaded_asset(mesh.get_editor_property('physics_asset'));assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
  bp=unreal.load_asset(r['animation_blueprint']);unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp)
  cls=unreal.EditorAssetLibrary.load_blueprint_class(r['blueprint']);assert cls;unreal.BlueprintEditorLibrary.compile_blueprint(unreal.load_asset(r['blueprint']));assert unreal.EditorAssetLibrary.save_asset(r['blueprint'])
  rig=unreal.load_asset(r['control_rig']);assert isinstance(rig,unreal.ControlRigBlueprint) and rig.create_control_rig().execute('Forwards Solve')
  ik=unreal.load_asset(r['ik']);assert isinstance(ik,unreal.IKRigDefinition) and unreal.IKRigController.get_controller(ik).get_num_solvers()==2
  da=unreal.load_asset(r['definition']);assert isinstance(da,unreal.AnanseCharacterDefinition)
  results.append({'key':key,'after':after,'native_reopened':True,'fk_executed':True,'ik_solvers':2,'creative_approved':False,'joint_limits_reviewed':False,'physics_policy':'Kinematic, mesh collision off; capsule authoritative. Dynamic ragdoll unapproved.','runtime_contact_qualified':False})
 report.write_text(json.dumps({'status':'reopened_engineering_quality_passed','designs':results},indent=2)+'\n')
except Exception:report.write_text(json.dumps({'status':'failed','designs':results,'exception':traceback.format_exc()},indent=2)+'\n');raise
