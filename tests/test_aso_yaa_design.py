"""Aso revisions remain scoped and cannot substitute another character's bindings."""
import pytest
from pydantic import ValidationError
from studio.models import StoryVisualDesign

def design():
 return dict(design_id='aso-yaa-human-v1',skeleton_key='AsoYaa-independent-v001',definition_path='/Game/Ananse/Characters/AsoYaa/Negotiation_v001/DA_AsoYaa.DA_AsoYaa',source_revision='authored-v004',source_glb_sha256='a'*64)

def test_new_aso_revision_is_allowlisted():
 assert StoryVisualDesign.model_validate(design()).source_revision=='authored-v004'

@pytest.mark.parametrize('field,value',[('skeleton_key','Kwaku-independent-v001'),('definition_path','/Game/Ananse/Characters/Kwaku/Story_v001/DA_Kwaku.DA_Kwaku'),('source_revision','authored-v005')])
def test_aso_revision_rejects_cross_character_and_unreviewed_binding(field,value):
 d=design();d[field]=value
 with pytest.raises(ValidationError):StoryVisualDesign.model_validate(d)

def test_original_aso_revision_is_still_resolvable():
 d=design();d.update(source_revision='authored-v001',definition_path='/Game/Ananse/Characters/AsoYaa/Story_v001/DA_AsoYaa.DA_AsoYaa');assert StoryVisualDesign.model_validate(d)

from scripts.aso_yaa_contract import validate_native_sockets

def socket_report():
 return {'socket_objects':[dict(name=n,bone=b,relative_location_cm=[0,0,0],relative_rotation_pitch_yaw_roll=[0,0,0],scale=[1,1,1])for n,b in [('socket_voice','jaw'),('socket_ledger_L','hand_L'),('socket_ledger_R','hand_R')]]}

def test_native_socket_object_schema_is_accepted():assert validate_native_sockets(socket_report())

def test_old_socket_name_schema_does_not_claim_success():
 with pytest.raises(ValueError):validate_native_sockets({'sockets':['socket_voice','socket_ledger_L','socket_ledger_R']})

@pytest.mark.parametrize('defect',['empty','wrong_bone','nonfinite','duplicate'])
def test_native_socket_report_rejects_incomplete_or_invalid_bindings(defect):
 d=socket_report()
 if defect=='empty':d['socket_objects']=[]
 if defect=='wrong_bone':d['socket_objects'][1]['bone']='hand_R'
 if defect=='nonfinite':d['socket_objects'][0]['relative_location_cm'][0]=float('nan')
 if defect=='duplicate':d['socket_objects'].append(d['socket_objects'][0])
 with pytest.raises(ValueError):validate_native_sockets(d)

def test_corrected_aso_source_uses_its_new_native_revision():
 d=design();d.update(source_revision='authored-v007',definition_path='/Game/Ananse/Characters/AsoYaa/Negotiation_v002/DA_AsoYaa.DA_AsoYaa');assert StoryVisualDesign.model_validate(d)
 d['definition_path']='/Game/Ananse/Characters/AsoYaa/Negotiation_v001/DA_AsoYaa.DA_AsoYaa'
 with pytest.raises(ValidationError):StoryVisualDesign.model_validate(d)

def test_unqualified_intermediate_lid_revision_cannot_be_published():
 d=design();d['source_revision']='authored-v006'
 with pytest.raises(ValidationError):StoryVisualDesign.model_validate(d)

from scripts.aso_yaa_contract import validate_ledger_observation
@pytest.mark.parametrize('change',[{'aso_ledger_phase_mask':15},{'aso_ledger_samples':0},{'aso_ledger_max_binding_error_cm':float('nan')},{'aso_ledger_max_binding_error_cm':float('inf')},{'aso_ledger_max_binding_error_cm':.11}])
def test_ledger_checker_rejects_missing_phases_and_invalid_contact(change):
 row=dict(aso_ledger_phase_mask=31,aso_ledger_samples=133,aso_ledger_max_binding_error_cm=0);row.update(change);assert not validate_ledger_observation(row)
def test_ledger_report_contract_requires_complete_observations():
 assert validate_ledger_observation(dict(aso_ledger_phase_mask=31,aso_ledger_samples=133,aso_ledger_max_binding_error_cm=.002))
