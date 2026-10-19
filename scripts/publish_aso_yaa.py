"""Scoped local prototype publication through the existing studio role/review API.
Technical review never supplies creative, rights, cultural or mobile approval.
"""
import json,sys,hashlib,secrets,sqlite3,shutil
from pathlib import Path
from fastapi.testclient import TestClient
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from studio.app import create_app
from scripts.export_content import verify_manifest
mode=sys.argv[1];assert mode in ['refined','restore'];out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=False);private=out/'private-backup';private.mkdir(mode=0o700);db=R/'.local/studio.sqlite3';catalogue=R/'Unreal/Content/Data/catalogue.json'
with sqlite3.connect(db)as live,sqlite3.connect(private/'studio.sqlite3')as backup:
 live.backup(backup);pubs=dict(live.execute('SELECT id,manifest FROM publications'));chars=list(live.execute("SELECT id,version,document FROM records WHERE kind='characters'ORDER BY id"));history=list(live.execute("SELECT version,document FROM revisions WHERE kind='characters'AND id='kwaku'ORDER BY version"))
(private/'studio.sqlite3').chmod(0o600);shutil.copy2(catalogue,private/'catalogue.json');tokens={r:secrets.token_urlsafe(32)for r in ['editor','reviewer','publisher']}
with TestClient(create_app(db,tokens))as client:
 def req(method,path,data=None,role='editor',status=200,version=None):
  headers={'Authorization':'Bearer '+tokens[role]}
  if version is not None:headers['If-Match']=str(version)
  response=client.request(method,path,json=data,headers=headers);assert response.status_code==status,(path,response.status_code,response.text[:250]);return response.json()
 aid='aso-yaa-human-v1-design';current=req('GET','/api/assets/'+aid);data=current['data'];prefix='/Game/Ananse/Characters/AsoYaa/'+('Negotiation_v002'if mode=='refined'else'Story_v001');folder='Authored_v007'if mode=='refined'else'Authored_v001';source=R/'SourceArt/Characters/AsoYaa'/folder;native=R/'Unreal/Content'/(prefix.removeprefix('/Game/')+'/AsoYaa.uasset');quality=json.loads((R/'.local/verification/aso-yaa-20261016/quality-03/quality.json').read_text())['rig']if mode=='refined'else json.loads((R/'SourceArt/Characters/AsoYaa/NATIVE_RIG_MAP_20261015_v001.json').read_text())['native']
 data.update(name='Aso Yaa negotiation appearance WIP'if mode=='refined'else'Aso Yaa previous appearance restored WIP',unreal_path=prefix+'/AsoYaa.AsoYaa',source_reference=str(source.relative_to(R)),sha256=hashlib.sha256(native.read_bytes()).hexdigest(),triangles_lod0=quality['lods'][0]['triangles'],material_slots=len(quality['material_slots']),status='review',mobile_review_passed=False)
 data['visual_design'].update(definition_path=prefix+'/DA_AsoYaa.DA_AsoYaa',source_revision=folder.lower().replace('_','-'),source_glb_sha256=hashlib.sha256((source/'AsoYaa.glb').read_bytes()).hexdigest())
 changed=req('PATCH','/api/assets/'+aid,{'data':data},version=current['version']);req('PATCH','/api/assets/'+aid,{'data':data},version=current['version'],status=412)
 req('POST','/api/publish',{'channel':'prototype'},role='publisher',status=409)
 req('POST','/api/assets/'+aid+'/review',{'version':changed['version'],'decision':'approved','note':'Technical local prototype review: materialised source/native bytes and isolated rig binding. Creative likeness, deformation, rights, cultural and physical-device approval remain REVIEW_REQUIRED.'},role='reviewer')
 pub=req('POST','/api/publish',{'channel':'prototype'},role='publisher',status=201);manifest=req('GET','/api/publications/'+pub['id']);verify_manifest(manifest);(out/'publication.json').write_text(json.dumps(manifest,indent=2)+'\n');temp=catalogue.with_suffix('.json.tmp');temp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');temp.replace(catalogue)
with sqlite3.connect(db)as live:
 assert all(live.execute('SELECT manifest FROM publications WHERE id=?',(key,)).fetchone()[0]==v for key,v in pubs.items());assert chars==list(live.execute("SELECT id,version,document FROM records WHERE kind='characters'ORDER BY id"));assert history==list(live.execute("SELECT version,document FROM revisions WHERE kind='characters'AND id='kwaku'ORDER BY version"))
(out/'result.json').write_text(json.dumps({'status':'prototype_technical_publication_exported','mode':mode,'publication_id':pub['id'],'payload_sha256':manifest['sha256'],'asset_revision':changed['version'],'prior_publications_unchanged':len(pubs),'canonical_characters_and_kwaku_history_unchanged':True,'creative_approved':False,'stale_write_rejected':True,'unreviewed_publication_rejected':True},indent=2)+'\n');print(pub['id'],manifest['sha256'])
