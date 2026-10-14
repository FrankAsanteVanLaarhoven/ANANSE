import pytest
from studio import lab
from studio.store import DomainError
SOCIAL=['inspect-evidence','listen-captain','borrowed-voice','enter-archive','take-ledger','expose']
NEGOTIATED=['inspect-evidence','negotiate','enter-archive','take-ledger','protect']
ROOFTOP=['web-step','trick-mirror','enter-archive','take-ledger','protect']
@pytest.mark.parametrize('actions,route,outcome',[(SOCIAL,'social','truth-exposed'),(NEGOTIATED,'negotiation','witnesses-protected'),(ROOFTOP,'rooftop','witnesses-protected')])
def test_three_routes(actions,route,outcome):
    s=lab.replay(actions);assert s['route']==route and s['outcome']==outcome
    assert 0<=s['thread']<=3 and 0<=s['suspicion']<=100

def test_deterministic_replay():assert lab.replay(SOCIAL)==lab.replay(SOCIAL)
def test_guard_not_omniscient():
    s=lab.replay(['inspect-evidence']);assert s['kojo_beliefs']['edict-forged']==1;assert 'edict-forged' not in s['guard_beliefs']
def test_identity_can_be_contradicted():
    s=lab.replay(['listen-captain','borrowed-voice','challenge-identity','enter-archive']);assert s['location']=='market' and s['suspicion']>=30

def test_disguise_expires():
    s=lab.replay(['listen-captain','borrowed-voice','wait','wait','enter-archive']);assert s['location']=='market'
def test_truth_costs_if_promise_broken():
    s=lab.replay(NEGOTIATED[:-1]+['expose']);assert s['outcome']=='truth-exposed' and s['reputation']['market']==-1

def test_no_farming():
    s=lab.replay(['inspect-evidence'])
    with pytest.raises(DomainError):lab.step(s,'inspect-evidence')
    s=lab.replay(NEGOTIATED[:-1])
    with pytest.raises(DomainError):lab.step(s,'take-ledger')

def test_invalid_action_does_not_mutate():
    s=lab.initial()
    with pytest.raises(DomainError):lab.step(s,'borrowed-voice')
    assert s==lab.initial()
def test_unknown_action():
    with pytest.raises(DomainError):lab.step(lab.initial(),'grant-all-rewards')
def test_thread_budget_and_cooldown():
    s=lab.replay(['trick-mirror'])
    with pytest.raises(DomainError):lab.step(s,'trick-mirror')
    s=lab.replay(['trick-mirror','wait','trick-mirror','wait','trick-mirror','wait'])
    with pytest.raises(DomainError):lab.step(s,'trick-mirror')
def test_detention_bounds():
    s=lab.replay(['enter-archive']*4);assert s['suspicion']==100 and s['outcome']=='detained'
    with pytest.raises(DomainError):lab.step(s,'wait')

def test_lab_api_flow_and_conflict(client,headers):
    r=client.post('/api/lab/sessions',headers=headers).json()
    for action in NEGOTIATED:
        response=client.post(f'/api/lab/sessions/{r["id"]}/actions',headers=headers,json={'action':action,'expected_version':r['version']});assert response.status_code==200,response.text;r=response.json()
    assert r['state']['outcome']=='witnesses-protected'
    assert client.post(f'/api/lab/sessions/{r["id"]}/actions',headers=headers,json={'action':'wait','expected_version':1}).status_code==412
    assert client.get(f'/api/lab/sessions/{r["id"]}',headers=headers).json()==r
