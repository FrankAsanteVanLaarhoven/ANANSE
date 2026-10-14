import copy,json,sqlite3
from concurrent.futures import ThreadPoolExecutor
import pytest
from studio.store import Store,DomainError,digest
from studio.app import create_app
from fastapi.testclient import TestClient
from scripts.export_content import verify_manifest
from .conftest import auth,TOKENS


def get(client,h,kind='characters',id='kwaku'):
    r=client.get(f'/api/{kind}/{id}',headers=h);assert r.status_code==200,r.text;return r.json()
def patch(client,h,r,data=None):return client.patch(f'/api/{r["kind"]}/{r["id"]}',headers=h|{'If-Match':str(r['version'])},json={'data':data or r['data']})

def test_seed_roster(client,headers):
    r=client.get('/api/characters',headers=headers).json();assert r['total']==16;assert len(r['items'])==16
    assert all(x['data']['stage']=='concept' for x in r['items'])
def test_auth_required(client):assert client.get('/api/characters').status_code==401
def test_bad_token(client):assert client.get('/api/characters',headers=auth('editor')|{'Authorization':'Bearer bad'}).status_code==401
def test_health_reports_unverified_unreal(client):assert client.get('/health').json()['unreal_verified'] is False
def test_role_separation(client,headers):
    r=get(client,headers);assert patch(client,auth('publisher'),r).status_code==403
    assert client.post('/api/publish',headers=headers,json={'channel':'prototype'}).status_code==403
    assert client.post('/api/characters/kwaku/review',headers=headers,json={'version':1,'decision':'approved','note':'Not independently reviewed'}).status_code==403
@pytest.mark.parametrize('kind,data',[('characters',{'name':'New','role':'Rival','source_note':'Original draft','variants':[{'id':'base','label':'Base'}]}),('factions',{'name':'New'}),('missions',{'name':'New','supported_routes':['social'],'endings':['one','two']}),('assets',{'name':'Mesh','category':'skeletal-mesh'})])
def test_full_crud_all_entity_types(client,headers,kind,data):
    r=client.post(f'/api/{kind}',headers=headers,json={'id':'new-record','data':data});assert r.status_code==201,r.text
    doc=r.json();assert r.headers['etag']=='"1"';doc['data']['name']='Revised'
    r=patch(client,headers,doc);assert r.status_code==200;r=r.json();assert r['version']==2
    deleted=client.delete(f'/api/{kind}/new-record',headers=headers|{'If-Match':'2'});assert deleted.status_code==200
    assert client.get(f'/api/{kind}/new-record',headers=headers).status_code==404
    assert client.post(f'/api/{kind}/new-record/restore',headers=headers|{'If-Match':'3'}).json()['version']==4
    assert get(client,headers,kind,'new-record')['data']['name']=='Revised'
def test_no_id_reuse(client,headers):
    client.post('/api/factions',headers=headers,json={'id':'temp-faction','data':{'name':'Temp'}})
    client.delete('/api/factions/temp-faction',headers=headers|{'If-Match':'1'})
    assert client.post('/api/factions',headers=headers,json={'id':'temp-faction','data':{'name':'New'}}).status_code==409
@pytest.mark.parametrize('id',['UPPER','../escape','a','has spaces'])
def test_invalid_ids(client,headers,id):assert client.post('/api/factions',headers=headers,json={'id':id,'data':{'name':'New'}}).status_code==422
def test_if_match_required(client,headers):
    r=get(client,headers);assert client.patch('/api/characters/kwaku',headers=headers,json={'data':r['data']}).status_code==428
    assert client.delete('/api/characters/kwaku',headers=headers).status_code==428
def test_stale_write(client,headers):
    r=get(client,headers);assert patch(client,headers,r).status_code==200;assert patch(client,headers,r).status_code==412
    assert get(client,headers)['version']==2

def test_references_prevent_delete(client,headers):
    assert client.delete('/api/characters/kwaku',headers=headers|{'If-Match':'1'}).status_code==409
    assert client.delete('/api/factions/story-road',headers=headers|{'If-Match':'1'}).status_code==409

def test_missing_reference_rejected(client,headers):
    r=get(client,headers);r['data']['faction_ids']=['missing-faction'];assert patch(client,headers,r).status_code==409

def test_asset_type_checked(client,headers):
    r=get(client,headers);r['data']['variants'][0]['body_asset_id']='market-kit';assert patch(client,headers,r).status_code==409

def test_referenced_asset_cannot_change_category(client,headers):
    r=get(client,headers);r['data']['variants'][0]['body_asset_id']='kwaku-body';assert patch(client,headers,r).status_code==200
    a=get(client,headers,'assets','kwaku-body');a['data']['category']='audio';assert patch(client,headers,a).status_code==409
    assert client.delete('/api/assets/kwaku-body',headers=headers|{'If-Match':'1'}).status_code==409

@pytest.mark.parametrize('mutation',[lambda d:d.update(execute='rm -rf'),lambda d:d['variants'].append(copy.deepcopy(d['variants'][0])),lambda d:d['variants'][0].update(body_scale=8),lambda d:d['variants'][0].update(cloth_colour='javascript:evil'),lambda d:d['variants'][0].update(morph_targets={'Bad Name':.3}),lambda d:d['variants'][0].update(morph_targets={'Smile':2})])
def test_strict_character_schema(client,headers,mutation):
    r=get(client,headers);mutation(r['data']);assert patch(client,headers,r).status_code==422

def test_asset_path_injection(client,headers):
    r=get(client,headers,'assets','kwaku-body');r['data']['unreal_path']='../../etc/passwd';assert patch(client,headers,r).status_code==422

def test_revision_history_and_revert(client,headers):
    r=get(client,headers);r['data']['name']='Changed';assert patch(client,headers,r).status_code==200
    old=client.get('/api/characters/kwaku/history',headers=headers).json()['items'];assert len(old)==2
    r=client.post('/api/characters/kwaku/revert',headers=headers|{'If-Match':'2'},json={'revision':1});assert r.status_code==200
    assert r.json()['version']==3 and r.json()['data']['name']=='Kwaku, the Story-Binder'

def test_reviews_revision_bound(client,headers):
    r=client.post('/api/characters/kwaku/review',headers=auth('reviewer'),json={'version':1,'decision':'approved','note':'Cultural and narrative review for this test only.'});assert r.status_code==200
    issues=client.get('/api/validation',headers=headers).json()['issues'];assert not any(i['record']=='characters/kwaku' and i['code']=='REVIEW_REQUIRED' for i in issues)
    patch(client,headers,get(client,headers));issues=client.get('/api/validation',headers=headers).json()['issues'];assert any(i['record']=='characters/kwaku' and i['code']=='REVIEW_REQUIRED' for i in issues)
    assert client.post('/api/characters/kwaku/review',headers=auth('reviewer'),json={'version':1,'decision':'approved','note':'Stale review should fail'}).status_code==412

def test_snapshot_immutable_and_hash_verified(client,headers):
    p=client.post('/api/publish',headers=auth('publisher'),json={'channel':'prototype'});assert p.status_code==201
    published=p.json();m=published['manifest'];assert verify_manifest(m)
    r=get(client,headers);r['data']['name']='Newer';patch(client,headers,r)
    assert client.get('/api/publications/'+published['id'],headers=headers).json()==m
    modified=copy.deepcopy(m);modified['payload']['entities']['characters'][0]['data']['name']='Tamper'
    with pytest.raises(ValueError):verify_manifest(modified)

def test_production_fail_closed(client,headers):
    r=client.post('/api/publish',headers=auth('publisher'),json={'channel':'production'});assert r.status_code==409
    assert client.get('/api/validation',headers=headers).json()['production_export_allowed'] is False

def test_audit_hash_and_triggers(client,headers):
    patch(client,headers,get(client,headers));a=client.get('/api/audit',headers=headers).json();assert a['integrity']['valid']
    with client.app.state.store.connect(True) as c:
        with pytest.raises(sqlite3.IntegrityError):c.execute("DELETE FROM audit")
        with pytest.raises(sqlite3.IntegrityError):c.execute("UPDATE revisions SET version=999")

def test_tokens_unique_and_long(tmp_path):
    with pytest.raises(ValueError):create_app(tmp_path/'db',{'editor':'x'*40,'reviewer':'x'*40,'publisher':'y'*40})

def test_self_review_rejected_at_storage_boundary(client,headers):
    store=client.app.state.store;store.create('factions','self-review',{'name':'Self'},'same-actor')
    with pytest.raises(DomainError) as e:store.review('factions','self-review',1,'same-actor','approved','Should not be accepted')
    assert e.value.status==403

def test_persistence_after_new_app_instance(client,headers):
    r=get(client,headers);r['data']['name']='Survives Restart';patch(client,headers,r)
    with TestClient(create_app(client.app.state.store.path,TOKENS)) as restarted:
        assert get(restarted,headers)['data']['name']=='Survives Restart'

def test_concurrent_compare_and_swap(client,headers):
    store=client.app.state.store;r=store.get('characters','kwaku')
    def write(n):
        try:store.update('characters','kwaku',r['data']|{'name':f'Writer {n}'},1,f'writer-{n}');return 200
        except DomainError as e:return e.status
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(write,[1,2]))
    assert sorted(results)==[200,412]

def test_cross_origin_blocked(client,headers):assert client.get('/api/characters',headers=headers|{'Origin':'https://attacker.invalid'}).status_code==403

def test_host_blocked(client,headers):assert client.get('/api/characters',headers=headers|{'Host':'attacker.invalid'}).status_code==400

def test_payload_limit(client,headers):assert client.post('/api/factions',headers=headers|{'Content-Type':'application/json'},content='x'*262145).status_code==413

def test_pagination(client,headers):
    a=client.get('/api/characters?limit=5&offset=0',headers=headers).json();b=client.get('/api/characters?limit=5&offset=5',headers=headers).json();assert len(a['items'])==5 and not({r['id'] for r in a['items']}&{r['id'] for r in b['items']})

def test_static_no_secret_disclosure(client):
    assert client.get('/').status_code==200
    assert 'object-src' in client.get('/').headers['content-security-policy']
    assert client.get('/static/credentials.json').status_code==404
    assert client.get('/api/openapi').status_code==401
