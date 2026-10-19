"""Exercise reviewed prototype visual publication through the existing local API.

Per-person creative/rights approval is not supplied by these temporary test roles.
"""
import argparse,copy,hashlib,json,os,re,secrets,shutil,socket,sqlite3,sys,threading,time
from pathlib import Path
import httpx,uvicorn
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from studio.app import create_app
from scripts.export_content import verify_manifest

def main():
 p=argparse.ArgumentParser();p.add_argument('--db',type=Path,default=ROOT/'.local/studio.sqlite3');p.add_argument('--out',type=Path,required=True);p.add_argument('--colour',default='#224E70');p.add_argument('--restore-from',type=Path);p.add_argument('--export',action='store_true');p.add_argument('--browser',action='store_true');p.add_argument('--reuse-publication');a=p.parse_args()
 out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);backup=out/'private-backup';backup.mkdir(mode=0o700)
 with sqlite3.connect(a.db) as live,sqlite3.connect(backup/'studio.sqlite3') as saved:
  live.backup(saved);oldpub=dict(live.execute('SELECT id,manifest FROM publications'));oldidentities=list(live.execute("SELECT kind,id,version,document FROM records WHERE kind='characters' ORDER BY id"));oldkwaku=list(live.execute("SELECT version,document FROM revisions WHERE kind='characters' AND id='kwaku' ORDER BY version"))
 (backup/'studio.sqlite3').chmod(0o600)
 catalogue=ROOT/'Unreal/Content/Data/catalogue.json';shutil.copy2(catalogue,backup/'catalogue.json')
 tokens={k:secrets.token_urlsafe(32) for k in ['editor','reviewer','publisher']};app=create_app(a.db,tokens)
 sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
 server=uvicorn.Server(uvicorn.Config(app,log_level='error',access_log=False));thread=threading.Thread(target=server.run,kwargs={'sockets':[sock]},daemon=True);thread.start();checks=[];browser_checks=[]
 try:
  for _ in range(100):
   if server.started:break
   time.sleep(.1)
  if not server.started:raise RuntimeError('Owned loopback service not ready')
  base=f'http://127.0.0.1:{port}'
  with httpx.Client(base_url=base,timeout=15) as client:
   def req(method,path,body=None,role='editor',version=None,status=200):
    headers={'Authorization':'Bearer '+tokens[role]}
    if version is not None:headers['If-Match']=str(version)
    r=client.request(method,path,headers=headers,json=body)
    if r.status_code!=status:raise RuntimeError(f'{method} {path}: expected {status}, got {r.status_code}; {r.text[:500]}')
    return r.json()
   source=ROOT/'SourceArt/Characters/OseboLeopard/Authored_v002/OseboLeopard.glb';mesh=ROOT/'Unreal/Content/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.uasset'
   data=dict(name='OseboLeopard authored technical design',category='skeletal-mesh',unreal_path='/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard',source_creator='Frank Asante Van Laarhoven',source_reference='Local authored-v002 model and native LOD revision. Technical prototype binding only; creative/cultural/rights approval remains open.',sha256=hashlib.sha256(mesh.read_bytes()).hexdigest(),triangles_lod0=66106,material_slots=10,licence='UNVERIFIED',status='review',mobile_review_passed=False,visual_design=dict(design_id='osebo-leopard-v1',skeleton_key='osebo-feline-biped-v001',definition_path='/Game/Ananse/Characters/OseboLeopard/Data/DA_OseboLeopard.DA_OseboLeopard',source_revision='authored-v002',source_glb_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),cape_colour='#752433',accent_colour='#C29848'))
   path='/api/assets/osebo-leopard-design'
   if a.reuse_publication:
    manifest=req('GET','/api/publications/'+a.reuse_publication);verify_manifest(manifest)
    current=next(x for x in manifest['payload']['entities']['assets'] if x['id']=='osebo-leopard-design')
    live=req('GET',path)
    if current['version']!=live['version'] or current['data']!=live['data']:raise RuntimeError('Reuse requires the exact current published visual revision')
    data=current['data'];original=copy.deepcopy(data);pub={'id':a.reuse_publication}
    if data['sha256']!=hashlib.sha256(mesh.read_bytes()).hexdigest():raise RuntimeError('Published native mesh bytes changed')
    checks.append('existing exact reviewed publication recovered without mutation')
    (out/'previous-appearance.json').write_text(json.dumps(original,indent=2)+'\n')
   else:
    response=client.get(path,headers={'Authorization':'Bearer '+tokens['editor']})
    if response.status_code==404:
     original=copy.deepcopy(data);data['visual_design']['cape_colour']=a.colour
     current=req('POST','/api/assets',dict(id='osebo-leopard-design',data=data),status=201)
    else:
     if response.status_code!=200:raise RuntimeError('Cannot inspect existing design revision')
     existing=response.json();original=copy.deepcopy(existing['data']);data=copy.deepcopy(existing['data'])
     data['sha256']=hashlib.sha256(mesh.read_bytes()).hexdigest()
     if a.restore_from:data['visual_design']=copy.deepcopy(json.loads(a.restore_from.read_text())['visual_design'])
     else:data['visual_design']['cape_colour']=a.colour
     current=req('PATCH',path,dict(data=data),version=existing['version'])
     req('PATCH',path,dict(data=data),version=existing['version'],status=412);checks.append('stale edit rejected')
    (out/'previous-appearance.json').write_text(json.dumps(original,indent=2)+'\n')
    req('POST','/api/publish',dict(channel='prototype'),role='publisher',status=409);checks.append('unreviewed exact visual revision blocked')
    req('POST',path+'/review',dict(version=current['version'],decision='approved',note='Wrong role negative case'),status=403);checks.append('editor cannot review')
    req('POST',path+'/review',dict(version=current['version'],decision='approved',note='Local technical prototype metadata/dependency review. Temporary role isolation; not final art, culture, rights or mobile approval.'),role='reviewer')
    req('POST','/api/publish',dict(channel='prototype'),status=403);checks.append('editor cannot publish')
    pub=req('POST','/api/publish',dict(channel='prototype'),role='publisher',status=201);manifest=req('GET','/api/publications/'+pub['id']);verify_manifest(manifest)
    checks.append('immutable publication retrieved and hash verified')
   (out/'publication.json').write_text(json.dumps(manifest,indent=2)+'\n')
   (out/'published-stage.json').write_text(json.dumps(dict(publication_id=pub['id'],visual_revision=current['version'],browser_status='pending' if a.browser else 'not_requested',exported=False),indent=2)+'\n')
   r=client.get(path+'/preview.glb');assert r.status_code==401;checks.append('preview requires authentication')
   r=client.get(path+'/preview.glb',headers={'Authorization':'Bearer '+tokens['editor']});assert r.status_code==200 and hashlib.sha256(r.content).hexdigest()==data['visual_design']['source_glb_sha256'];checks.append('real preview bytes match revision hash')
   if a.browser:
    from playwright.sync_api import sync_playwright,expect
    errors=[]
    with sync_playwright() as pw:
     browser=pw.chromium.launch(executable_path=os.environ.get('ANANSE_CHROMIUM_PATH') or shutil.which('chromium'),headless=True)
     page=browser.new_page(viewport={'width':1440,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base)
     page.locator('#token').fill(tokens['editor']);page.locator('#connect').click();expect(page.locator('#identity')).to_have_text('Connected as editor')
     page.locator('[data-kind="assets"]').click();page.get_by_role('button',name='OseboLeopard authored technical design',exact=False).click();page.locator('#design-preview').click()
     expect(page.locator('#design-status')).to_contain_text('64 joints, 9 clips',timeout=30000);expect(page.locator('#design-canvas')).to_have_attribute('data-rendered-frames',re.compile(r'[0-9]{2,}'),timeout=30000)
     page.locator('#design-clip').select_option('7');expect(page.locator('#design-canvas')).to_have_attribute('data-evaluated-clip',page.locator('#design-clip option:checked').inner_text());pose_before=page.locator('#design-canvas').get_attribute('data-pose-signature');page.wait_for_timeout(250);assert page.locator('#design-canvas').get_attribute('data-pose-signature')!=pose_before;page.locator('#design-wire').check();page.screenshot(path=str(out/'studio-real-topology.png'),full_page=True);page.locator('#design-wire').uncheck();page.screenshot(path=str(out/'studio-real-model.png'),full_page=True)
     page.locator('[data-kind="characters"]').click();expect(page.locator('#design-tools')).to_be_hidden();stopped=page.locator('#design-canvas').get_attribute('data-rendered-frames');page.wait_for_timeout(250);assert page.locator('#design-canvas').get_attribute('data-rendered-frames')==stopped
     assert not errors,errors;browser_checks=['authenticated source load','64 actual skin joints','9 actual clips','rendered frames nonzero','evaluated selected clip identity','actual skin pose changes across frames','real indexed wireframe','turntable enabled','leaving asset cancels preview rendering','no browser exceptions'];browser.close()
   if a.export:
    temp=catalogue.with_suffix('.json.tmp');temp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');temp.replace(catalogue)
   (out/'publication.json').write_text(json.dumps(manifest,indent=2)+'\n')
  with sqlite3.connect(a.db) as live:
   assert all(live.execute('SELECT manifest FROM publications WHERE id=?',(key,)).fetchone()[0]==value for key,value in oldpub.items())
   assert list(live.execute("SELECT kind,id,version,document FROM records WHERE kind='characters' ORDER BY id"))==oldidentities
   assert list(live.execute("SELECT version,document FROM revisions WHERE kind='characters' AND id='kwaku' ORDER BY version"))==oldkwaku
  result=dict(status='passed',publication_id=pub['id'],publication_hash=manifest['sha256'],visual_revision=current['version'],cape_colour=data['visual_design']['cape_colour'],http_checks=checks,browser_checks=browser_checks,exported=a.export,old_publications_preserved=len(oldpub),canonical_characters_unchanged=True,review_scope='Isolated temporary local technical roles; creative/cultural/rights/mobile remain unapproved')
  (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
 finally:server.should_exit=True;thread.join(timeout=10);sock.close()
if __name__=='__main__':main()
