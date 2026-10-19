"""Review/publish a bounded visual revision through the existing local studio.
Technical role checks are not creative, cultural, rights or device approval.
"""
import os,sys,json,sqlite3,hashlib,secrets,socket,threading,time,shutil,re
from pathlib import Path
import httpx,uvicorn
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from studio.app import create_app
from scripts.export_content import verify_manifest
out=Path(sys.argv[1]).resolve();mode=sys.argv[2]if len(sys.argv)>2 else'refined';assert mode in ['refined','restore-original','repaired','interactions'];out.mkdir(parents=True,exist_ok=False);private=out/'private-backup';private.mkdir(mode=0o700);db=ROOT/'.local/studio.sqlite3';catalogue=ROOT/'Unreal/Content/Data/catalogue.json'
with sqlite3.connect(db)as live,sqlite3.connect(private/'studio.sqlite3')as backup:
 live.backup(backup);oldpub=dict(live.execute('SELECT id,manifest FROM publications'));oldchars=list(live.execute("SELECT id,version,document FROM records WHERE kind='characters'ORDER BY id"));history=list(live.execute("SELECT version,document FROM revisions WHERE kind='characters'AND id='kwaku'ORDER BY version"))
(private/'studio.sqlite3').chmod(0o600);shutil.copy2(catalogue,private/'catalogue.json');tokens={role:secrets.token_urlsafe(32)for role in ['editor','reviewer','publisher']};app=create_app(db,tokens);sock=socket.socket();sock.bind(('127.0.0.1',0));base='http://127.0.0.1:'+str(sock.getsockname()[1]);server=uvicorn.Server(uvicorn.Config(app,log_level='error',access_log=False));thread=threading.Thread(target=server.run,kwargs={'sockets':[sock]},daemon=True);thread.start()
try:
 with httpx.Client(base_url=base,timeout=60)as client:
  for _ in range(100):
   if server.started:break
   time.sleep(.05)
  def req(method,path,data=None,role='editor',status=200,version=None):
   headers={'Authorization':'Bearer '+tokens[role]}
   if version is not None:headers['If-Match']=str(version)
   response=client.request(method,path,headers=headers,json=data);assert response.status_code==status,(path,response.status_code,response.text[:250]);return response.json()
  identifier='kwaku-human-v1-design';current=req('GET','/api/assets/'+identifier);data=current['data'];interactions=mode=='interactions';repaired=mode in ['repaired','interactions'];refined=mode!='restore-original';folder='Authored_v016'if interactions else'Authored_v008'if repaired else'Authored_v006'if refined else'Authored_v002';nativefolder='Interactions_v005'if interactions else'Refined_v002'if repaired else'Refined_v001'if refined else'Story_v001';prefix='/Game/Ananse/Characters/Kwaku/'+nativefolder;scene=ROOT/'SourceArt/Characters/Kwaku'/folder;native=ROOT/'Unreal/Content/Ananse/Characters/Kwaku'/nativefolder/'Kwaku.uasset';assert native.is_file()
  data.update(name='Kwaku visual refinement WIP'if refined else'Kwaku original visual restored WIP',unreal_path=prefix+'/Kwaku.Kwaku',source_reference=str(scene.relative_to(ROOT)),sha256=hashlib.sha256(native.read_bytes()).hexdigest(),status='review',mobile_review_passed=False)
  measured=json.loads((ROOT/'.local/verification/forms-scenery-20261015/native-01/native.json'if repaired else ROOT/'.local/verification/art-refinement-20261015/native-02/native.json'if refined else ROOT/'SourceArt/Characters/Kwaku/NATIVE_RIG_MAP_20261015_v001.json').read_text())['native'];data['triangles_lod0']=measured['lods'][0]['triangles'];data['material_slots']=len(measured['material_slots'])
  if interactions:measured=json.loads((ROOT/'.local/verification/character-interactions-20261016/native-05/native.json').read_text())['characters']['Kwaku']['native'];data['triangles_lod0']=measured['lods'][0]['triangles'];data['material_slots']=len(measured['material_slots'])
  data['visual_design'].update(definition_path=prefix+'/DA_Kwaku.DA_Kwaku',source_revision='authored-v016'if interactions else'authored-v008'if repaired else'authored-v006'if refined else'authored-v002',source_glb_sha256=hashlib.sha256((scene/'Kwaku.glb').read_bytes()).hexdigest());changed=[req('PATCH','/api/assets/'+identifier,{'data':data},version=current['version'])]
  if refined:
   for key in ['MarketEarth','ForestEarth','WarmPlaster','WeatheredWood']:
    aid='surface-'+re.sub(r'(?<!^)(?=[A-Z])','-',key).lower()+'-v2';native=ROOT/'Unreal/Content/Ananse/Environments/Refinement_v002'/('M_'+key+'.uasset');assert native.is_file();asset={'name':key+' original textured surface WIP','category':'material','unreal_path':'/Game/Ananse/Environments/Refinement_v002/M_'+key+'.M_'+key,'source_creator':'Frank Asante Van Laarhoven','source_reference':'SourceArt/Environments/MarketSanctuary/Refinement_v002/'+key+'_Albedo.png','licence':'UNVERIFIED','sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'mobile_review_passed':False,'status':'review'}
    existing=client.get('/api/assets/'+aid,headers={'Authorization':'Bearer '+tokens['editor']})
    if existing.status_code==404:changed.append(req('POST','/api/assets',{'id':aid,'data':asset},status=201))
    else:assert existing.status_code==200;assert existing.json()['data']['sha256']==asset['sha256']
  if refined:
   fix=json.loads((ROOT/'.local/verification/art-refinement-20261015/morph-material-fix-01/materials.json').read_text());assert fix['status'].startswith('saved_real_morph')
   if repaired:fix={'materials':[{'path':v['material'],'sha256':hashlib.sha256((ROOT/'Unreal/Content'/(v['material'].split('.')[0].removeprefix('/Game/')+'.uasset')).read_bytes()).hexdigest()}for v in measured['material_slots']]}
   for material in fix['materials']:
    path=material['path'];assert path.startswith(prefix+'/');native=ROOT/'Unreal/Content'/(path.split('.')[0].removeprefix('/Game/')+'.uasset');digest=hashlib.sha256(native.read_bytes()).hexdigest();assert digest==material['sha256'];name=path.rsplit('.',1)[1];aid='kwaku-'+re.sub('[^a-z0-9-]','-',name.lower())+('-morph-material-v4'if interactions else'-morph-material-v2'if repaired else'-morph-material-v1');asset={'name':name+' Kwaku morph material WIP','category':'material','unreal_path':path,'source_creator':'Frank Asante Van Laarhoven','source_reference':'scripts/fix_refined_morph_materials.py','licence':'UNVERIFIED','sha256':digest,'mobile_review_passed':False,'status':'review'};existing=client.get('/api/assets/'+aid,headers={'Authorization':'Bearer '+tokens['editor']})
    if existing.status_code==404:changed.append(req('POST','/api/assets',{'id':aid,'data':asset},status=201))
    else:assert existing.status_code==200 and existing.json()['data']['sha256']==digest
  if repaired:
   scenery=json.loads((ROOT/'.local/verification/forms-scenery-20261015/market-episode-04/scenery.json').read_text());assert scenery['status']=='saved_pending_rendered_gameplay_review'
   for key,path in scenery['meshes'].items():
    aid='forms-scenery-'+key.lower().replace('_','-')+'-v2';native=ROOT/'Unreal/Content'/(path.split('.')[0].removeprefix('/Game/')+'.uasset');assert native.is_file();asset={'name':key+' authored scenery WIP','category':'static-mesh','unreal_path':path,'source_creator':'Frank Asante Van Laarhoven','source_reference':'SourceArt/Environments/MarketSanctuary/Forms_v002/'+key+'.glb','licence':'UNVERIFIED','sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'mobile_review_passed':False,'status':'review'}
    existing=client.get('/api/assets/'+aid,headers={'Authorization':'Bearer '+tokens['editor']})
    if existing.status_code==404:changed.append(req('POST','/api/assets',{'id':aid,'data':asset},status=201))
    else:assert existing.status_code==200 and existing.json()['data']['sha256']==asset['sha256']
  if interactions:
   imported=json.loads((ROOT/'.local/verification/character-interactions-20261016/native-05/native.json').read_text())['characters']
   for aid,key,path,reference,category in [('osebo-leopard-interaction-surface-v1','OseboLeopard',imported['OseboLeopard']['mesh'],'SourceArt/Characters/OseboLeopard/Authored_v005','skeletal-mesh'),('kwaku-ledger-prop-v1','Kwaku',imported['Kwaku']['props'][0],'SourceArt/Characters/Kwaku/Authored_v016/Ledger.glb','static-mesh')]:
    native=ROOT/'Unreal/Content'/(path.split('.')[0].removeprefix('/Game/')+'.uasset');asset={'name':aid+' WIP','category':category,'unreal_path':path,'source_creator':'Frank Asante Van Laarhoven','source_reference':reference,'licence':'UNVERIFIED','sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'mobile_review_passed':False,'status':'review'};existing=client.get('/api/assets/'+aid,headers={'Authorization':'Bearer '+tokens['editor']})
    if existing.status_code==404:changed.append(req('POST','/api/assets',{'id':aid,'data':asset},status=201))
    else:
     assert existing.status_code==200
     if existing.json()['data']!=asset:changed.append(req('PATCH','/api/assets/'+aid,{'data':asset},version=existing.json()['version']))
  # Review is blocked until exact revisions are checked; old approvals cannot authorise edits.
  req('POST','/api/publish',{'channel':'prototype'},role='publisher',status=409)
  browser_result={}
  if refined:
   from playwright.sync_api import sync_playwright,expect
   errors=[]
   with sync_playwright()as pw:
    browser=pw.chromium.launch(executable_path=shutil.which('chromium'),headless=True);page=browser.new_page(viewport={'width':1400,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base);page.locator('#token').fill(tokens['editor']);page.locator('#connect').click();expect(page.locator('#identity')).to_have_text('Connected as editor');page.locator('[data-kind="assets"]').click();page.get_by_role('button',name=data['name'],exact=False).click();page.locator('#design-preview').click();expect(page.locator('#design-status')).to_contain_text('46 joints, 11 clips, 2 eyelid targets',timeout=60000);canvas=page.locator('#design-canvas');expect(canvas).to_have_attribute('data-morph-targets','2');page.locator('#design-turn').uncheck();page.locator('#design-clip').select_option('-1');page.wait_for_timeout(250);before=canvas.screenshot(path=str(out/'kwaku-eyes-open.png'));again=canvas.screenshot();assert hashlib.sha256(before).hexdigest()==hashlib.sha256(again).hexdigest(),'Rest pose must be stable before morph comparison';page.locator('#design-blink').check();expect(canvas).to_have_attribute('data-morph-weight','1');page.wait_for_timeout(100);closed=canvas.screenshot(path=str(out/'kwaku-eyelids-closed.png'));assert hashlib.sha256(before).hexdigest()!=hashlib.sha256(closed).hexdigest(),'Actual GPU morph pixels must differ';page.locator('#design-blink').uncheck();page.locator('#design-clip').select_option('10');signature=canvas.get_attribute('data-pose-signature');page.wait_for_timeout(350);assert signature!=canvas.get_attribute('data-pose-signature');page.locator('#design-wire').check();canvas.screenshot(path=str(out/'kwaku-actual-topology.png'));assert not errors,errors;browser.close();browser_result={'actual_gpu_morph_pixels_changed':True,'rest_pose_stable':True,'actual_skin_pose_changes':True,'sparse_targets_loaded':2,'browser_errors':errors}
  for record in changed:req('POST','/api/assets/'+record['id']+'/review',{'version':record['version'],'decision':'approved','note':'Local technical prototype review only: exact source/native references, existing skeleton compatibility and material/morph bytes. Final creative/deformation/cultural/rights/device acceptance remains open.'},role='reviewer')
  publication=req('POST','/api/publish',{'channel':'prototype'},role='publisher',status=201);manifest=req('GET','/api/publications/'+publication['id']);verify_manifest(manifest);(out/'publication.json').write_text(json.dumps(manifest,indent=2)+'\n');temp=catalogue.with_suffix('.json.tmp');temp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');temp.replace(catalogue)
 with sqlite3.connect(db)as live:
  assert all(live.execute('SELECT manifest FROM publications WHERE id=?',(key,)).fetchone()[0]==value for key,value in oldpub.items());assert oldchars==list(live.execute("SELECT id,version,document FROM records WHERE kind='characters'ORDER BY id"));assert history==list(live.execute("SELECT version,document FROM revisions WHERE kind='characters'AND id='kwaku'ORDER BY version"))
 (out/'result.json').write_text(json.dumps({'status':'technical_publication_exported','mode':mode,'asset_revision':changed[0]['version'],'publication_id':publication['id'],'payload_sha256':manifest['sha256'],'browser':browser_result,'canonical_characters_and_kwaku_history_unchanged':True,'prior_publications_preserved':len(oldpub),'creative_approved':False},indent=2)+'\n');print('Technical visual publication exported',publication['id'])
finally:server.should_exit=True;thread.join(timeout=10);sock.close()
