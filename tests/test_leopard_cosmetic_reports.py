import pytest
from scripts.check_leopard_cosmetic_report import check
from scripts.run_leopard_check import MAP

def fixture():
 names=['IdleGuard','Patrol','RunPursuit','TurnStop','Investigate','CaptureReach','StaggerRecover','Command','LimbIsolation']
 base='/Game/Ananse/Characters/OseboLeopard/'
 report=dict(passed=True,normal_lit_rendering=True,seconds=60.01,world=MAP+'.L_OseboLeopardCharacterLab',pawn_class=base+'Runtime_v001/BP_OseboLeopard.BP_OseboLeopard_C',mesh=base+'Authored_v001/OseboLeopard.OseboLeopard',bones=64,ability_grants=0,movement_cm=175,face_forward_alignment=1,animation_instance=base+'Animations/ABP_OseboLeopard.ABP_OseboLeopard_C',clips=[dict(clip=base+'Authored_v001/OseboLeopard'+n+'.OseboLeopard'+n,evaluated_bone_motion=True,graph_clip_observed=True) for n in names],published_visual_revision=2,actual_cape_linear='(R=0.015996,G=0.076185,B=0.162029,A=1.000000)',actual_accent_linear='(R=0.539479,G=0.313989,B=0.064803,A=1.000000)')
 manifest=dict(payload=dict(entities=dict(assets=[dict(id='osebo-leopard-design',version=2,data=dict(visual_design=dict(cape_colour='#224E70',accent_colour='#C29848')))])))
 return report,dict(accepted=True,exit_code=0),manifest
def test_actual_material_values_and_publication_revision():assert check(*fixture())
@pytest.mark.parametrize('field,value',[('published_visual_revision',1),('actual_cape_linear','unbound'),('actual_cape_linear','(R=0.9,G=0.076185,B=0.162029,A=1)'),('actual_accent_linear','(R=NaN,G=0.313989,B=0.064803,A=1)'),('actual_cape_linear','(R=0.015996,G=0.076185,B=0.162029,A=0)'),('mesh','/Game/Other.Mesh')])
def test_material_report_rejects_wrong_or_unobserved_values(field,value):
 r,p,m=fixture();r[field]=value;assert not check(r,p,m)
def test_success_word_does_not_replace_execution():
 r,p,m=fixture();p['exit_code']=139;assert not check(r,p,m)
 r,p,m=fixture();r['clips'].pop();assert not check(r,p,m)
