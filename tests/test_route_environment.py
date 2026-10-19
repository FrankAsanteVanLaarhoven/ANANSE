import copy,pytest
from scripts.validate_route_environment import validate,summarize_samples

def fixture():
    return {'status':'reopened','meshes':[{'lod_vertices':[100,50,25],'nanite_enabled':False}for _ in range(8)],'maps':[{'anchor_differences':[],'instances':12,'simple_collision_boxes':12,'unexpected_visual_collision':[]}for _ in range(2)]}
def test_reopened_environment():assert validate(fixture())
def test_rejects_moved_gameplay_anchor():
    r=fixture();r['maps'][0]['anchor_differences']=['archive']
    with pytest.raises(ValueError):validate(r)
def test_rejects_missing_lod():
    r=fixture();r['meshes'][0]['lod_vertices']=[100]
    with pytest.raises(ValueError):validate(r)
def test_rejects_visual_collision():
    r=fixture();r['maps'][1]['unexpected_visual_collision']=['tree']
    with pytest.raises(ValueError):validate(r)
def test_rejects_missing_runtime_measurements():
    with pytest.raises(ValueError):summarize_samples([])
def test_rejects_nonfinite_runtime_measurement():
    with pytest.raises(ValueError):summarize_samples([{'active_seconds':float('nan')}])

from scripts.native_runtime_smoke import verify_aso_expose_evidence

def reaction(route):return {'mission_state':{'route':route},'aso_video_frames':[{'event':'aso_broken_promise_visual_only'}]}
def test_negotiation_expose_requires_reaction_and_capture(tmp_path):
    r=reaction('negotiation');assert not verify_aso_expose_evidence(r,tmp_path,'negotiation')
    (tmp_path/'cinematic_broken_promise.png').write_bytes(b'actual-capture-fixture');assert verify_aso_expose_evidence(r,tmp_path,'negotiation')
def test_negotiation_expose_rejects_capture_without_event(tmp_path):
    (tmp_path/'cinematic_broken_promise.png').write_bytes(b'capture-fixture');assert not verify_aso_expose_evidence({'mission_state':{'route':'negotiation'}},tmp_path,'negotiation')
def test_other_routes_do_not_make_witness_promise(tmp_path):
    assert verify_aso_expose_evidence({'mission_state':{'route':'social'}},tmp_path,'social')
def test_other_routes_reject_invented_promise_reaction(tmp_path):
    assert not verify_aso_expose_evidence(reaction('social'),tmp_path,'social')
def test_promise_checker_rejects_wrong_route(tmp_path):
    assert not verify_aso_expose_evidence(reaction('negotiation'),tmp_path,'rooftop')
