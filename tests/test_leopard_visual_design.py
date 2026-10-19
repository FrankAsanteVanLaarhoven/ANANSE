import copy,hashlib
import pytest
from pydantic import ValidationError
from studio.models import Asset
from studio.visuals import preview_source
from studio.store import DomainError
from .conftest import auth

def draft():
 return dict(name='Leopard technical visual',category='skeletal-mesh',unreal_path='/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard',visual_design=dict(design_id='osebo-leopard-v1',skeleton_key='osebo-feline-biped-v001',definition_path='/Game/Ananse/Characters/OseboLeopard/Data/DA_OseboLeopard.DA_OseboLeopard',source_revision='authored-v002',source_glb_sha256='a'*64,cape_colour='#752433',accent_colour='#C29848'))

@pytest.mark.parametrize('change',[{'design_id':'osebo'},{'skeleton_key':'ananse-eight-limb-v002'},{'definition_path':'/Game/Arbitrary.Evil'},{'body_scale':2},{'cape_colour':'javascript:bad'},{'source_glb_sha256':'bad'}])
def test_design_rejects_identity_rig_scale_and_untrusted_inputs(change):
 d=draft();d['visual_design'].update(change)
 with pytest.raises(ValidationError):Asset.model_validate(d)

@pytest.mark.parametrize('change',[{'category':'static-mesh'},{'unreal_path':'/Game/Other.Mesh'}])
def test_design_must_bind_actual_feline_skeletal_mesh(change):
 d=draft();d.update(change)
 with pytest.raises(ValidationError):Asset.model_validate(d)

def test_preview_materialisation_and_integrity(tmp_path):
 d=draft();p=tmp_path/'SourceArt/Characters/OseboLeopard/Authored_v002/OseboLeopard.glb'
 with pytest.raises(DomainError):preview_source(tmp_path,dict(data=d))
 p.parent.mkdir(parents=True);p.write_bytes(b'qualified source bytes')
 with pytest.raises(DomainError):preview_source(tmp_path,dict(data=d))
 d['visual_design']['source_glb_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 assert preview_source(tmp_path,dict(data=d))[0]==p
 p.write_bytes(b'changed source')
 with pytest.raises(DomainError):preview_source(tmp_path,dict(data=d))

def test_exact_revision_review_required_and_publications_immutable(client,headers):
 body=draft();made=client.post('/api/assets',headers=headers,json={'id':'leopard-design','data':body});assert made.status_code==201
 r=client.post('/api/publish',headers=auth('publisher'),json={'channel':'prototype'});assert r.status_code==409
 def review(version):
  r=client.post('/api/assets/leopard-design/review',headers=auth('reviewer'),json={'version':version,'decision':'approved','note':'Technical prototype binding only; final art/rights remain open.'});assert r.status_code==200
 def publish():
  r=client.post('/api/publish',headers=auth('publisher'),json={'channel':'prototype'});assert r.status_code==201;return r.json()
 review(1);first=publish();old=client.get('/api/publications/'+first['id'],headers=headers).json()
 body['visual_design']['cape_colour']='#224E70'
 r=client.patch('/api/assets/leopard-design',headers=headers|{'If-Match':'1'},json={'data':body});assert r.status_code==200
 assert client.post('/api/publish',headers=auth('publisher'),json={'channel':'prototype'}).status_code==409
 review(2);second=publish();assert second['id']!=first['id']
 assert client.get('/api/publications/'+first['id'],headers=headers).json()==old
 # Restore via a new revision and publication, never mutate the first two.
 original=draft();r=client.patch('/api/assets/leopard-design',headers=headers|{'If-Match':'2'},json={'data':original});assert r.status_code==200
 review(3);third=publish();assert len({first['id'],second['id'],third['id']})==3
