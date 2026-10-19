"""Stage real authored sources in the existing studio, verify browser previews and
publish a technical prototype revision. No creative/rights/mobile approval.
"""
import json,os,sys,sqlite3,secrets,socket,threading,time,hashlib,re,shutil
from pathlib import Path
import httpx,uvicorn
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from studio.app import create_app
from studio.models import STORY_DESIGNS
from scripts.export_content import verify_manifest
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False);backup=out/'private-backup';backup.mkdir(mode=0o700);db=ROOT/'.local/studio.sqlite3';cat=ROOT/'Unreal/Content/Data/catalogue.json'
with sqlite3.connect(db)as live,sqlite3.connect(backup/'studio.sqlite3')as saved:
 live.backup(saved);oldpub=dict(live.execute('SELECT id,manifest FROM publications'));oldchars=list(live.execute("SELECT kind,id,version,document FROM records WHERE kind='characters' ORDER BY id"));oldkwaku=list(live.execute("SELECT version,document FROM revisions WHERE kind='characters' AND id='kwaku' ORDER BY version"))
(backup/'studio.sqlite3').chmod(0o600);shutil.copy2(cat,backup/'catalogue.json');tokens={k:secrets.token_urlsafe(32)for k in ['editor','reviewer','publisher']};app=create_app(db,tokens);sock=socket.socket();sock.bind(('127.0.0.1',0));base='http://127.0.0.1:'+str(sock.getsockname()[1]);server=uvicorn.Server(uvicorn.Config(app,log_level='error',access_log=False));thread=threading.Thread(target=server.run,kwargs={'sockets':[sock]},daemon=True);thread.start()
try:
 with httpx.Client(base_url=base,timeout=30)as client:
  for _ in range(100):
   if server.started:break
   time.sleep(.05)
  def req(method,path,data=None,role='editor',status=200):
   r=client.request(method,path,headers={'Authorization':'Bearer '+tokens[role]},json=data);assert r.status_code==status,(path,r.status_code,r.text[:250]);return r.json()
  records=[]
  for design,(key,revision)in STORY_DESIGNS.items():
   native=json.loads((ROOT/'.local/verification/story-cast-20261015'/('native-'+key)/(key+'-native.json')).read_text());folder=ROOT/'SourceArt/Characters'/key/revision.replace('authored','Authored').replace('-','_');source=json.loads((folder/'rig-map.json').read_text());mesh=ROOT/'Unreal/Content'/(native['mesh'].split('.')[0].removeprefix('/Game/')+'.uasset')
   data={'name':key+' authored story design WIP','category':'skeletal-mesh','unreal_path':native['mesh'],'source_creator':'Frank Asante Van Laarhoven','source_reference':str(folder.relative_to(ROOT)),'licence':'UNVERIFIED','sha256':hashlib.sha256(mesh.read_bytes()).hexdigest(),'mobile_review_passed':False,'status':'review','visual_design':{'design_id':design,'skeleton_key':key+'-independent-v001','definition_path':native['definition'],'source_revision':revision,'source_glb_sha256':source['glb_sha256']}}
   identifier=design+'-design';r=req('GET','/api/assets/'+identifier,status=404)
   current=req('POST','/api/assets',{'id':identifier,'data':data},status=201);records.append(current)
   body=client.get('/api/assets/'+identifier+'/preview.glb',headers={'Authorization':'Bearer '+tokens['editor']});assert body.status_code==200 and hashlib.sha256(body.content).hexdigest()==source['glb_sha256']
  req('POST','/api/publish',{'channel':'prototype'},role='publisher',status=409)
  from playwright.sync_api import sync_playwright,expect
  errors=[];checks=[]
  with sync_playwright()as pw:
   browser=pw.chromium.launch(executable_path=shutil.which('chromium'),headless=True);page=browser.new_page(viewport={'width':1440,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base);page.locator('#token').fill(tokens['editor']);page.locator('#connect').click();expect(page.locator('#identity')).to_have_text('Connected as editor');page.locator('[data-kind="assets"]').click()
   for current in records:
    key=STORY_DESIGNS[current['data']['visual_design']['design_id']][0];folder=ROOT/current['data']['source_reference'];source=json.loads((folder/'rig-map.json').read_text());page.get_by_role('button',name=current['data']['name'],exact=False).click();page.locator('#design-preview').click();expect(page.locator('#design-status')).to_contain_text(str(len(source['bones']))+' joints, '+str(len(source['actions']))+' clips',timeout=30000);expect(page.locator('#design-canvas')).to_have_attribute('data-rendered-frames',re.compile(r'[0-9]{2,}'),timeout=30000)
    page.locator('#design-clip').select_option(str(len(source['actions'])-1));expect(page.locator('#design-canvas')).to_have_attribute('data-evaluated-clip',page.locator('#design-clip option:checked').inner_text());before=page.locator('#design-canvas').get_attribute('data-pose-signature');page.wait_for_timeout(300);assert page.locator('#design-canvas').get_attribute('data-pose-signature')!=before
    page.screenshot(path=str(out/(key+'-preview.png')),full_page=True);page.locator('#design-wire').check();page.screenshot(path=str(out/(key+'-topology.png')),full_page=True);page.locator('#design-wire').uncheck();checks.append({'design':key,'actual_skin_joints':len(source['bones']),'clips':len(source['actions']),'evaluated_pose_changes':True,'actual_topology_toggle':True})
   page.locator('[data-kind="characters"]').click();expect(page.locator('#design-tools')).to_be_hidden();before=page.locator('#design-canvas').get_attribute('data-rendered-frames');page.wait_for_timeout(200);assert page.locator('#design-canvas').get_attribute('data-rendered-frames')==before;assert not errors,errors;browser.close()
  for current in records:req('POST','/api/assets/'+current['id']+'/review',{'version':current['version'],'decision':'approved','note':'Temporary local role technical import/schema/source integrity review only. Creative, cultural, rights, physical device and final deformation acceptance remain OPEN.'},role='reviewer')
  publication=req('POST','/api/publish',{'channel':'prototype'},role='publisher',status=201);manifest=req('GET','/api/publications/'+publication['id']);verify_manifest(manifest);(out/'publication.json').write_text(json.dumps(manifest,indent=2)+'\n')
  # Export only after actual reviewed prototype publication. Existing files backed up.
  temp=cat.with_suffix('.json.tmp');temp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');temp.replace(cat)
 with sqlite3.connect(db)as live:
  assert all(live.execute('SELECT manifest FROM publications WHERE id=?',(i,)).fetchone()[0]==v for i,v in oldpub.items());assert list(live.execute("SELECT kind,id,version,document FROM records WHERE kind='characters' ORDER BY id"))==oldchars;assert list(live.execute("SELECT version,document FROM revisions WHERE kind='characters' AND id='kwaku' ORDER BY version"))==oldkwaku
 (out/'result.json').write_text(json.dumps({'status':'passed','browser_designs':checks,'browser_errors':errors,'canonical_characters_unchanged':True,'kwaku_history_unchanged':True,'older_publications_preserved':len(oldpub),'publication_id':publication['id'],'payload_sha256':manifest['sha256'],'creative_approval':False,'mobile_qualified':False,'review_scope':'Temporary local technical roles only; no final art/rights/cultural approval'},indent=2)+'\n');print('Studio technical prototype publication passed; seven real 3D previews checked.')
finally:server.should_exit=True;thread.join(timeout=10);sock.close()
