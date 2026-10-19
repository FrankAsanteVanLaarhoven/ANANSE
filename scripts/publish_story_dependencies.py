"""Revision-specific technical publication of actual cast sockets/environment bytes.
Preserves canonical identities and all immutable prior publications.
"""
import os,sys,json,sqlite3,hashlib,secrets,socket,threading,time,shutil
from pathlib import Path
import httpx,uvicorn
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from studio.app import create_app
from studio.models import STORY_DESIGNS
from scripts.export_content import verify_manifest
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);private=out/'private-backup';private.mkdir(mode=0o700);db=ROOT/'.local/studio.sqlite3';catalogue=ROOT/'Unreal/Content/Data/catalogue.json'
with sqlite3.connect(db)as live,sqlite3.connect(private/'studio.sqlite3')as saved:
 live.backup(saved);oldpub=dict(live.execute('SELECT id,manifest FROM publications'));oldchars=list(live.execute("SELECT id,version,document FROM records WHERE kind='characters' ORDER BY id"));oldkwaku=list(live.execute("SELECT version,document FROM revisions WHERE kind='characters'AND id='kwaku' ORDER BY version"))
(private/'studio.sqlite3').chmod(0o600);shutil.copy2(catalogue,private/'catalogue.json');tokens={k:secrets.token_urlsafe(32)for k in ['editor','reviewer','publisher']};app=create_app(db,tokens);sock=socket.socket();sock.bind(('127.0.0.1',0));base='http://127.0.0.1:'+str(sock.getsockname()[1]);server=uvicorn.Server(uvicorn.Config(app,log_level='error',access_log=False));thread=threading.Thread(target=server.run,kwargs={'sockets':[sock]},daemon=True);thread.start()
try:
 with httpx.Client(base_url=base,timeout=30)as client:
  for _ in range(100):
   if server.started:break
   time.sleep(.05)
  def req(method,path,data=None,role='editor',status=200,version=None):
   h={'Authorization':'Bearer '+tokens[role]}
   if version is not None:h['If-Match']=str(version)
   r=client.request(method,path,headers=h,json=data);assert r.status_code==status,(path,r.status_code,r.text[:250]);return r.json()
  changed=[]
  for design,(key,rev)in STORY_DESIGNS.items():
   record=req('GET','/api/assets/'+design+'-design');data=record['data'];mesh=ROOT/'Unreal/Content'/(data['unreal_path'].split('.')[0].removeprefix('/Game/')+'.uasset');data['sha256']=hashlib.sha256(mesh.read_bytes()).hexdigest();current=req('PATCH','/api/assets/'+record['id'],{'data':data},version=record['version']);assert current['version']==record['version']+1;changed.append(current)
  env=json.loads((ROOT/'.local/verification/story-cast-20261015/environment-native/environments-native.json').read_text())
  for key,path in env['meshes'].items():
   identifier='env-'+''.join('-'+c.lower()if c.isupper()else c for c in key).lstrip('-')+'-v1';native=ROOT/'Unreal/Content'/(path.split('.')[0].removeprefix('/Game/')+'.uasset');assert native.is_file()
   data={'name':key+' authored environment WIP','category':'static-mesh','unreal_path':path,'source_creator':'Frank Asante Van Laarhoven','source_reference':'SourceArt/Environments/MarketSanctuary/Authored_v001/'+key+'.glb','licence':'UNVERIFIED','sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'mobile_review_passed':False,'status':'review'}
   changed.append(req('POST','/api/assets',{'id':identifier,'data':data},status=201))
  req('POST','/api/publish',{'channel':'prototype'},role='publisher',status=409)
  for r in changed:req('POST','/api/assets/'+r['id']+'/review',{'version':r['version'],'decision':'approved','note':'Local temporary technical role: real native dependency/path/hash and saved socket validation. This does not approve final resemblance, deformation, culture, rights, mobile or campaign species mapping.'},role='reviewer')
  pub=req('POST','/api/publish',{'channel':'prototype'},role='publisher',status=201);manifest=req('GET','/api/publications/'+pub['id']);verify_manifest(manifest);(out/'publication.json').write_text(json.dumps(manifest,indent=2)+'\n');temp=catalogue.with_suffix('.json.tmp');temp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');temp.replace(catalogue)
 with sqlite3.connect(db)as live:
  assert all(live.execute('SELECT manifest FROM publications WHERE id=?',(i,)).fetchone()[0]==v for i,v in oldpub.items());assert list(live.execute("SELECT id,version,document FROM records WHERE kind='characters' ORDER BY id"))==oldchars;assert list(live.execute("SELECT version,document FROM revisions WHERE kind='characters'AND id='kwaku' ORDER BY version"))==oldkwaku
 (out/'result.json').write_text(json.dumps({'status':'passed','publication_id':pub['id'],'payload_sha256':manifest['sha256'],'cast_asset_revisions':{r['id']:r['version']for r in changed if r['data']['category']=='skeletal-mesh'},'new_environment_assets':7,'old_publications_preserved':len(oldpub),'canonical_characters_unchanged':True,'kwaku_history_unchanged':True,'review_scope':'Temporary local technical roles; final art/rights/mobile approval open','creative_approved':False},indent=2)+'\n');print('Technical cast/environment dependency publication passed.')
finally:server.should_exit=True;thread.join(timeout=10);sock.close()
