"""Cross-family binding, local-source integrity and report failure regressions."""
import copy,hashlib,json
from pathlib import Path
import pytest
from pydantic import ValidationError
from studio.models import STORY_DESIGNS,Asset
from studio.visuals import preview_source
from studio.store import DomainError
from scripts.run_story_cast_check import validate

def record(design):
 key,rev=STORY_DESIGNS[design]
 return {'data':{'name':key,'category':'skeletal-mesh','unreal_path':f'/Game/Ananse/Characters/{key}/Story_v001/{key}.{key}','visual_design':{'design_id':design,'skeleton_key':key+'-independent-v001','definition_path':f'/Game/Ananse/Characters/{key}/Story_v001/DA_{key}.DA_{key}','source_revision':rev,'source_glb_sha256':hashlib.sha256(b'actual-local-bytes').hexdigest()}}}

@pytest.mark.parametrize('design',STORY_DESIGNS)
def test_allowlisted_design_rejects_cross_family_mesh(design):
 r=record(design);Asset.model_validate(r['data']);r['data']['unreal_path']='/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard'
 with pytest.raises(ValidationError):Asset.model_validate(r['data'])

@pytest.mark.parametrize('field,value',[('skeleton_key','ananse-eight-limb-v002'),('definition_path','/Game/Injected.BP_Injected'),('source_revision','../../escape')])
def test_family_source_and_definition_cannot_be_substituted(field,value):
 r=record('kwaku-human-v1');r['data']['visual_design'][field]=value
 with pytest.raises(ValidationError):Asset.model_validate(r['data'])

def test_preview_rejects_changed_bytes_and_escape(tmp_path):
 r=record('kwaku-human-v1');p=tmp_path/'SourceArt/Characters/Kwaku/Authored_v002/Kwaku.glb';p.parent.mkdir(parents=True);p.write_bytes(b'actual-local-bytes');assert preview_source(tmp_path,r)[0]==p
 p.write_bytes(b'changed')
 with pytest.raises(DomainError):preview_source(tmp_path,r)
 outside=tmp_path/'outside.glb';outside.write_bytes(b'actual-local-bytes');p.unlink();p.symlink_to(outside);assert preview_source(tmp_path,r)[0].is_relative_to(tmp_path)

def test_preview_forbids_escape_from_project(tmp_path):
 root=tmp_path/'project';root.mkdir();r=record('kwaku-human-v1');p=root/'SourceArt/Characters/Kwaku/Authored_v002/Kwaku.glb';p.parent.mkdir(parents=True);outside=tmp_path/'private.glb';outside.write_bytes(b'actual-local-bytes');p.symlink_to(outside)
 with pytest.raises(DomainError):preview_source(root,r)

@pytest.mark.parametrize('report,code',[({},0),({'passed':True,'seconds':60,'designs':[]},0),({'passed':True,'seconds':60,'designs':[]},2),({'passed':True,'seconds':0,'designs':[]},0)])
def test_report_rejects_empty_incomplete_or_failed_execution(report,code):assert not validate(report,code)

def complete_report():
 rows=[]
 for design,(key,rev)in STORY_DESIGNS.items():
  base=f'/Game/Ananse/Characters/{key}/Story_v001/'
  d={'character_review_light_components':0,'design':design,'mesh':base+key+'.'+key,'pawn_class':base+'BP_'+key+'.BP_'+key+'_C','animation_instance':base+'ABP_'+key+'.ABP_'+key+'_C','complete_round_trips':20,'movement_cm':100,'bones':48,'clips':[{'clip':base+str(i),'graph_and_pose_observed':True}for i in range(8)]}
  if key!='EsiMoth':d['flat_contact_metrics']=json.dumps({'invalid_transforms':0,'solved_chains':2,'legs':[{'samples':500,'p95_stance_drift_cm':1,'max_penetration_cm':.2,'max_segment_length_error_cm':0}for _ in range(2)]})
  rows.append(d)
 return {'passed':True,'seconds':60,'designs':rows}

def test_complete_synthetic_report_is_accepted():assert validate(complete_report(),0)

@pytest.mark.parametrize('field,value',[('p95_stance_drift_cm',2.01),('max_penetration_cm',.501),('samples',0),('max_segment_length_error_cm',.11)])
def test_report_rejects_one_failing_leg_without_averaging(field,value):
 r=complete_report();m=json.loads(r['designs'][0]['flat_contact_metrics']);m['legs'][1][field]=value;r['designs'][0]['flat_contact_metrics']=json.dumps(m);assert not validate(r,0)

def test_report_rejects_one_failed_evaluated_clip():
 r=complete_report();r['designs'][3]['clips'][2]['graph_and_pose_observed']=False;assert not validate(r,0)

def test_report_rejects_duplicate_design_and_missing_family():
 r=complete_report();r['designs'][-1]=copy.deepcopy(r['designs'][0]);assert not validate(r,0)


@pytest.mark.parametrize('value',[float('nan'),float('inf'),float('-inf'),None,'60',True])
def test_cast_report_rejects_invalid_duration(value):
 r=complete_report();r['seconds']=value;assert not validate(r,0)

@pytest.mark.parametrize('field',['movement_cm','bones'])
@pytest.mark.parametrize('value',[float('nan'),float('inf'),None,True])
def test_cast_report_rejects_invalid_runtime_measurement(field,value):
 r=complete_report();r['designs'][0][field]=value;assert not validate(r,0)

@pytest.mark.parametrize('field',['samples','max_segment_length_error_cm'])
@pytest.mark.parametrize('value',[float('nan'),float('inf'),None,True])
def test_cast_report_rejects_invalid_contact_measurement(field,value):
 r=complete_report();m=json.loads(r['designs'][0]['flat_contact_metrics']);m['legs'][0][field]=value;r['designs'][0]['flat_contact_metrics']=json.dumps(m);assert not validate(r,0)


def current_aso_report():
 r=complete_report();a=r['designs'][1];base='/Game/Ananse/Characters/AsoYaa/Contact_v002/'
 a.update(mesh=base+'AsoYaa.AsoYaa',pawn_class=base+'BP_AsoYaa.BP_AsoYaa_C',animation_instance=base+'ABP_AsoYaa.ABP_AsoYaa_C',skeleton=base+'AsoYaa_Skeleton.AsoYaa_Skeleton',definition_revision=5,refined_face_bindings=True,applied_blink_peak=1,aso_ledger_samples=60,aso_ledger_phase_mask=31,aso_ledger_max_binding_error_cm=.01)
 a['clips']=[{'clip':base+str(i),'graph_and_pose_observed':True}for i in range(16)]
 return r

def test_current_aso_cannot_be_replaced_by_historical_cast_binding():
 assert validate(current_aso_report(),0,aso_contact=True)
 assert not validate(complete_report(),0,aso_contact=True)

def test_current_aso_requires_full_contact_sequence():
 r=current_aso_report();r['designs'][1]['aso_ledger_phase_mask']=7
 assert not validate(r,0,aso_contact=True)

def test_current_aso_requires_all_sixteen_evaluated_clips():
 r=current_aso_report();r['designs'][1]['clips'].pop()
 assert not validate(r,0,aso_contact=True)


def test_neutral_review_requires_actual_light_component_evidence():
 r=complete_report();assert not validate(r,0,neutral_lighting=True)
 r.update(neutral_review_enabled=True,neutral_review_lights=[dict(intensity_lumens=3000,uses_lumens_units=True,channel0=True,channel1=False)for _ in range(2)])
 assert validate(r,0,neutral_lighting=True)

def test_neutral_review_rejects_wrong_channel_after_return():
 r=complete_report();r.update(neutral_review_enabled=True,neutral_review_lights=[dict(intensity_lumens=3000,uses_lumens_units=True,channel0=True,channel1=False)for _ in range(2)])
 r['neutral_review_lights'][1]['channel0']=False
 assert not validate(r,0,neutral_lighting=True)

def test_neutral_review_rejects_accumulating_preview_lights():
 r=complete_report();r.update(neutral_review_enabled=True,neutral_review_lights=[dict(intensity_lumens=3000,uses_lumens_units=True,channel0=True,channel1=False)for _ in range(3)])
 assert not validate(r,0,neutral_lighting=True)


def test_corrected_aso_cli_rejects_shortened_run_before_launch(tmp_path):
 import subprocess,sys
 out=tmp_path/'not-created'
 r=subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/'scripts/run_story_cast_check.py'),'--aso-contact','--out',str(out)],capture_output=True,text=True)
 assert r.returncode==2 and 'requires --full-clips'in r.stderr
 assert not out.exists()


def test_neutral_review_rejects_stacked_character_preview_fills():
 r=complete_report();r.update(neutral_review_enabled=True,neutral_review_lights=[dict(intensity_lumens=3000,uses_lumens_units=True,channel0=True,channel1=False)for _ in range(2)])
 r['designs'][1]['character_review_light_components']=2
 assert not validate(r,0,neutral_lighting=True)
