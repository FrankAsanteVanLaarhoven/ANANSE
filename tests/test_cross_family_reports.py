"""Cross-family reports must prove committed live families, not UI requests."""
import json
import pytest
from scripts.run_cross_family_check import verify,FAMILIES,NEGATIVES,MAP,SPIDER,LEOPARD

def valid():
    transitions=[]
    for i in range(1,41):
        design=LEOPARD if i%2 else SPIDER
        transitions.append(dict(FAMILIES[design],transition=i,passed=True,requested_design=design,
            committed_design=design,possessed_pawn_id=100+i,input_mapping_active=True,camera_bound=True,
            evaluated_gesture_motion=True,movement_cm=10.,physics='/Game/Qualified/Physics.Physics',spider_contacts_rebuilt=design==SPIDER))
        transitions[-1].update(graph_evaluations=100,graph_clip_observed=True,finite_pose=True)
    legs=[dict(leg=s,samples=10,p95_stance_drift_cm=.01,max_penetration_cm=.01,
               max_segment_length_error_cm=0,joint_limit_violations=0) for s in ['front_l','front_r','rear_l','rear_r']]
    return dict(passed=True,normal_lit_rendering=True,seconds=60.1,world=MAP+'.L_AnanseCharacterLab',
        committed_cross_family_transitions=40,complete_round_trips=20,transitions=transitions,
        negative_checks=[dict(check=n,passed=True) for n in sorted(NEGATIVES)],
        rejected_stale_completions=1,restored_profile_committed=True,restored_design=LEOPARD,
        post_return_contact_metrics=json.dumps(dict(invalid_transforms=0,last_solved_chains=4,legs=legs)))

def test_complete_commits_and_restore():
    r=valid();assert verify(r,0,LEOPARD)
    assert not verify(r,139,LEOPARD)
    assert not verify(r,0,SPIDER)
    assert not verify({},0)

@pytest.mark.parametrize('field,value', [('committed_cross_family_transitions',39),('complete_round_trips',19),
    ('seconds',59),('negative_checks',[]),('restored_profile_committed',False),('normal_lit_rendering',False)])
def test_incomplete_scenario_rejected(field,value):
    r=valid();r[field]=value;assert not verify(r,0,LEOPARD)

@pytest.mark.parametrize('field,value',[('committed_design',SPIDER),('requested_design',SPIDER),
    ('pawn_class',FAMILIES[SPIDER]['pawn_class']),('mesh',FAMILIES[SPIDER]['mesh']),
    ('skeleton',FAMILIES[SPIDER]['skeleton']),('animation_instance',FAMILIES[SPIDER]['animation_instance']),
    ('movement_cm',0),('movement_cm',float('nan')),('evaluated_gesture_motion',False),
    ('camera_bound',False),('input_mapping_active',False),('physics','missing'),('passed',False),('graph_evaluations',0),('graph_clip_observed',False),('finite_pose',False)])
def test_requested_or_wrong_family_not_a_commit(field,value):
    r=valid();r['transitions'][0][field]=value;assert not verify(r,0)

def test_same_pawn_failed_negative_and_stale_contacts_rejected():
    r=valid();r['transitions'][1]['possessed_pawn_id']=r['transitions'][0]['possessed_pawn_id'];assert not verify(r,0)
    r=valid();r['negative_checks'][0]['passed']=False;assert not verify(r,0)
    r=valid();r['transitions'][1]['spider_contacts_rebuilt']=False;assert not verify(r,0)
    r=valid();m=json.loads(r['post_return_contact_metrics']);m['legs'][0]['max_penetration_cm']=.51
    r['post_return_contact_metrics']=json.dumps(m);assert not verify(r,0)

def test_visual_review_requires_new_feline_runtime_binding():
 r=valid()
 for t in r['transitions']:
  if t['committed_design']==LEOPARD:t.update(pawn_class='/Game/Ananse/Characters/OseboLeopard/Visual_v003/BP_OseboLeopard.BP_OseboLeopard_C',mesh='/Game/Ananse/Characters/OseboLeopard/Visual_v003/OseboLeopard.OseboLeopard')
 assert verify(r,0,visual_review=True)
 assert not verify(r,0)
 r['transitions'][0]['mesh']=FAMILIES[LEOPARD]['mesh'];assert not verify(r,0,visual_review=True)


def test_art_pass2_rejects_old_family_and_requires_new_exact_binding():
 r=valid();assert not verify(r,0,art_pass2=True)
 for t in r['transitions']:
  if t['committed_design']==LEOPARD:t.update(pawn_class='/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/BP_OseboLeopard.BP_OseboLeopard_C',mesh='/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/OseboLeopard.OseboLeopard')
 assert verify(r,0,art_pass2=True);assert not verify(r,0,visual_review=True)

def aso_report():
 r=valid();other='aso-yaa-human-v1';base='/Game/Ananse/Characters/AsoYaa/Negotiation_v002/';r['other_design']=other
 for t in r['transitions']:
  if t['committed_design']==LEOPARD:
   t.update(requested_design=other,committed_design=other,pawn_class=base+'BP_AsoYaa.BP_AsoYaa_C',mesh=base+'AsoYaa.AsoYaa',skeleton=base+'AsoYaa_Skeleton.AsoYaa_Skeleton',animation_instance=base+'ABP_AsoYaa.ABP_AsoYaa_C',physics=base+'AsoYaa_PhysicsAsset.AsoYaa_PhysicsAsset',aso_contacts_rebuilt=True)
 return r

def test_aso_mode_rejects_feline_or_wrong_rig_evidence():
 assert not verify(valid(),0,aso_yaa=True)
 r=aso_report();assert verify(r,0,aso_yaa=True);assert not verify(r,0)
 r['transitions'][0]['skeleton']=FAMILIES[SPIDER]['skeleton'];assert not verify(r,0,aso_yaa=True)

def test_aso_mode_requires_contacts_and_every_negative_case():
 r=aso_report();r['transitions'][0]['aso_contacts_rebuilt']=False;assert not verify(r,0,aso_yaa=True)
 r=aso_report();r['negative_checks'][0]['passed']=False;assert not verify(r,0,aso_yaa=True)

def aso_art_report():
 r=aso_report();base='/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/';shared='/Game/Ananse/Characters/AsoYaa/Clearance_v001/'
 for t in r['transitions']:
  if t['committed_design']=='aso-yaa-human-v1':t.update(pawn_class=base+'BP_AsoYaa.BP_AsoYaa_C',mesh=base+'AsoYaa.AsoYaa',skeleton=shared+'AsoYaa_Skeleton.AsoYaa_Skeleton',animation_instance=shared+'ABP_AsoYaa.ABP_AsoYaa_C',physics='/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa_PhysicsAsset.AsoYaa_PhysicsAsset')
 return r

def test_aso_art_reuses_exact_qualified_bindings_on_new_mesh():
 assert verify(aso_art_report(),0,aso_yaa=True,aso_contact=True,aso_clearance=True,aso_art_refine=True)
 assert not verify(aso_art_report(),0,aso_yaa=True,aso_contact=True,aso_clearance=True)

@pytest.mark.parametrize('field,value',[
 ('mesh','/Game/Ananse/Characters/AsoYaa/Clearance_v001/AsoYaa.AsoYaa'),
 ('skeleton','/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/AsoYaa_Skeleton.AsoYaa_Skeleton'),
 ('animation_instance','/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/ABP_AsoYaa.ABP_AsoYaa_C'),
 ('physics','/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/AsoYaa_PhysicsAsset.AsoYaa_PhysicsAsset')])
def test_aso_art_rejects_old_mesh_and_unqualified_replacements(field,value):
 r=aso_art_report();r['transitions'][0][field]=value
 assert not verify(r,0,aso_yaa=True,aso_contact=True,aso_clearance=True,aso_art_refine=True)
