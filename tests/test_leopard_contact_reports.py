import copy,math
import pytest
from scripts.run_leopard_contact_check import verify,MAP

def report():
 return dict(passed=True,seconds=160.01,world=MAP,mesh='/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard',normal_lit_rendering=True,jump_started=True,web_transition_started=True,upper_body_graph_active=True,metrics=dict(invalid_transforms=0,solved_chains=2,resets=8,legs=[dict(leg=side,samples=1000,p95_stance_drift_cm=.2,max_penetration_cm=.1,max_segment_length_error_cm=0,support_sample_coverage={'AnanseFixture:'+k:500 for k in ['flat','ramp','steps','uneven','moving','disappearing']}) for side in ['L','R']]))

def test_complete_contact_report_required():assert verify(report(),0)
@pytest.mark.parametrize('field,value',[('world','/Game/Wrong'),('seconds',10),('passed',False),('normal_lit_rendering',False),('jump_started',False),('web_transition_started',False),('upper_body_graph_active',False),('mesh','/Game/Other.Mesh')])
def test_contact_rejects_wrong_execution(field,value):
 r=report();r[field]=value;assert not verify(r,0)
@pytest.mark.parametrize('field,value',[('p95_stance_drift_cm',2.01),('max_penetration_cm',.51),('max_segment_length_error_cm',.11),('p95_stance_drift_cm',float('nan')),('max_penetration_cm',-1),('samples',0)])
def test_contact_rejects_failing_leg_even_when_other_passes(field,value):
 r=report();r['metrics']['legs'][1][field]=value;assert not verify(r,0)
def test_contact_rejects_missing_surface_and_crash():
 r=report();del r['metrics']['legs'][0]['support_sample_coverage']['AnanseFixture:moving'];assert not verify(r,0);assert not verify(report(),139)

def test_interaction_fixture_requires_exact_native_pair_and_success():
 r=report();r.update(world='/Game/Ananse/Maps/Interactions_v003/L_LeopardContactInteractions',mesh='/Game/Ananse/Characters/OseboLeopard/Interactions_v003/OseboLeopard.OseboLeopard')
 assert not verify(r,0,True)
 r.update(fixture_binding_valid=True,expected_fixture_map=r['world'],expected_fixture_mesh=r['mesh'])
 assert verify(r,0,True)
 for field,value in [('fixture_binding_valid',False),('expected_fixture_map',MAP),('world',MAP),('expected_fixture_mesh','/Game/Wrong.Mesh'),('passed',False)]:
  bad=copy.deepcopy(r);bad[field]=value;assert not verify(bad,0,True)
 assert not verify(r,2,True)
 assert not verify(r,0,False)

def test_visual_contact_requires_exact_new_pair_and_native_binding():
 r=report();r.update(world='/Game/Ananse/Maps/Visual_v003/L_LeopardVisualContact',mesh='/Game/Ananse/Characters/OseboLeopard/Visual_v003/OseboLeopard.OseboLeopard',fixture_binding_valid=True);r.update(expected_fixture_map=r['world'],expected_fixture_mesh=r['mesh'])
 assert verify(r,0,False,True)
 assert not verify(r,0,True,False)
 r['fixture_binding_valid']=False;assert not verify(r,0,False,True)


def test_art_pass2_contact_requires_exact_revision_and_fixture():
 r=report();r.update(world='/Game/Ananse/Maps/ArtPass2_v003/L_LeopardArtContact',mesh='/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/OseboLeopard.OseboLeopard',fixture_binding_valid=True);r.update(expected_fixture_map=r['world'],expected_fixture_mesh=r['mesh'])
 assert verify(r,0,art_pass2=True);assert not verify(r,0,visual_review=True)
 r['expected_fixture_map']=MAP;assert not verify(r,0,art_pass2=True)
