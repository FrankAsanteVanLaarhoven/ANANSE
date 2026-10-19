"""Reject superficially successful lab reports that lack measured acceptance."""
import copy,json
import pytest
from scripts.run_lab_selection_check import verify_report

def valid():
    legs=[{'leg':name,'samples':10,'p95_stance_drift_cm':0.01,'max_penetration_cm':0.01,'max_segment_length_error_cm':0.0,'joint_limit_violations':0} for name in ['front_l','front_r','rear_l','rear_r']]
    return {'passed':True,'rendered_rhi':True,'seconds':60.1,'selection_transactions':40,'restored_profile':True,'post_swap_contact_metrics':json.dumps({'invalid_transforms':0,'last_solved_chains':4,'legs':legs})}

def test_complete_report_and_normal_exit_required():
    r=valid();assert verify_report(r,0,True)
    assert not verify_report(r,139,True)
    assert not verify_report({},0)

@pytest.mark.parametrize('field,value',[('passed',False),('seconds',59.9),('selection_transactions',39),('rendered_rhi',False),('restored_profile',False)])
def test_incomplete_runtime_rejected(field,value):
    r=valid();r[field]=value;assert not verify_report(r,0,True)

@pytest.mark.parametrize('field,value',[('samples',0),('p95_stance_drift_cm',2.01),('max_penetration_cm',.51),('max_segment_length_error_cm',.11),('joint_limit_violations',1),('p95_stance_drift_cm',float('nan'))])
def test_actual_contact_failure_rejected(field,value):
    r=valid();m=json.loads(r['post_swap_contact_metrics']);m['legs'][0][field]=value;r['post_swap_contact_metrics']=json.dumps(m);assert not verify_report(r,0)

def test_missing_leg_or_metrics_rejected():
    r=valid();m=json.loads(r['post_swap_contact_metrics']);m['legs'].pop();r['post_swap_contact_metrics']=json.dumps(m);assert not verify_report(r,0)
    r['post_swap_contact_metrics']='{}';assert not verify_report(r,0)
