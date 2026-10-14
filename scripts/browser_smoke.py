#!/usr/bin/env python3
"""Optional real-browser smoke. Uses an isolated DB and kills its own server at exit."""
from __future__ import annotations
import argparse,json,os,re,secrets,shutil,socket,subprocess,sys,tempfile,time
from pathlib import Path
from datetime import datetime,timezone
import httpx
from playwright.sync_api import sync_playwright,expect
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'.local/verification'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')/'browser_smoke'
def main():
    global OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=OUT,help='Fresh evidence directory; existing reports are never overwritten.')
    OUT=parser.parse_args().out.resolve()
    OUT.mkdir(parents=True,exist_ok=True)
    if any(OUT.glob('*smoke.json')):
        raise RuntimeError('Evidence directory already contains smoke reports. Select a fresh --out directory.')
    checks=[];errors=[]
    with tempfile.TemporaryDirectory(prefix='ananse-browser-') as tmp:
        temp=Path(tmp);tokens={r:secrets.token_urlsafe(32) for r in ('editor','reviewer','publisher')}
        (temp/'tokens.json').write_text(json.dumps(tokens))
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        code="import os,json; from pathlib import Path; from studio.app import create_app; import uvicorn; p=Path(os.environ['ANANSE_SMOKE_DIR']); uvicorn.run(create_app(p/'db.sqlite3',json.loads((p/'tokens.json').read_text()),Path('content/seed.json')),host='127.0.0.1',port=int(os.environ['ANANSE_SMOKE_PORT']),access_log=False)"
        env=os.environ|{'ANANSE_SMOKE_DIR':str(temp),'ANANSE_SMOKE_PORT':str(port)}
        with (OUT/'browser-server.log').open('w') as log:
            proc=subprocess.Popen([sys.executable,'-c',code],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
            try:
                base=f'http://127.0.0.1:{port}'
                for _ in range(100):
                    try:
                        if httpx.get(base+'/health',timeout=.3).status_code==200:break
                    except httpx.HTTPError:pass
                    time.sleep(.1)
                else:raise RuntimeError('Test server did not become healthy.')
                with sync_playwright() as p:
                    browser=p.chromium.launch(executable_path=os.environ.get('ANANSE_CHROMIUM_PATH') or shutil.which('chromium'),headless=True);page=browser.new_page(viewport={'width':1440,'height':1050},device_scale_factor=1)
                    page.on('pageerror',lambda error:errors.append(str(error)))
                    page.goto(base)
                    def connect(role):
                        page.locator('#token').fill(tokens[role]);page.locator('#connect').click();expect(page.locator('#identity')).to_have_text(f'Connected as {role}')
                    connect('editor');expect(page.locator('#count')).to_have_text('16');checks.append('authenticated-roster-read')
                    page.get_by_role('button',name=re.compile('^Kwaku, the Story-Binder')).click()
                    data=json.loads(page.locator('#json').input_value());data['variants'][0]['cloth_colour']='#48766B';data['powers'].remove('trick-mirror');page.locator('#json').fill(json.dumps(data,indent=2));page.locator('#save').click();expect(page.locator('#revision')).to_have_text('REVISION 2');checks.append('appearance-edit-persists-as-new-revision')
                    page.reload();connect('editor');page.get_by_role('button',name=re.compile('^Kwaku, the Story-Binder')).click();assert json.loads(page.locator('#json').input_value())['variants'][0]['cloth_colour']=='#48766B';checks.append('browser-reload-persistence')
                    page.once('dialog',lambda d:d.accept('browser-character'));page.locator('#create').click();expect(page.locator('#record-id')).to_have_text('CHARACTERS / browser-character')
                    page.once('dialog',lambda d:d.accept('alternate'));page.locator('#add-variant').click();page.locator('#save').click();expect(page.locator('#revision')).to_have_text('REVISION 2');assert len(json.loads(page.locator('#json').input_value())['variants'])==2;checks.append('create-character-and-add-variant')
                    page.once('dialog',lambda d:d.accept());page.locator('#delete').click();expect(page.locator('#count')).to_have_text('16')
                    page.locator('#archived').check();expect(page.locator('#count')).to_have_text('17');page.get_by_role('button',name=re.compile('^New Story Road character')).click();expect(page.locator('#revision')).to_have_text('REVISION 3 · ARCHIVED');page.locator('#restore').click();expect(page.locator('#revision')).to_have_text('REVISION 4');checks.append('archive-and-restore-character')
                    connect('reviewer');page.get_by_role('button',name=re.compile('^Kwaku, the Story-Binder')).click()
                    page.once('dialog',lambda d:d.accept('Local UI revision review; not cultural certification.'));page.locator('#review').click();expect(page.locator('#dialog-title')).to_have_text('Revision review recorded');page.locator('#close-dialog').click();checks.append('revision-bound-review')
                    page.screenshot(path=str(OUT/'studio-overview.png'),full_page=True)
                    connect('publisher');page.locator('#publish').click();expect(page.locator('#dialog-title')).to_have_text('Immutable prototype publication');publication=json.loads(page.locator('#dialog-body').inner_text());assert len(publication['sha256'])==64;page.locator('#close-dialog').click();checks.append('immutable-prototype-publication')
                    subprocess.run([sys.executable,str(ROOT/'scripts/export_content.py'),'--db',str(temp/'db.sqlite3'),'--publication',publication['publication_id'],'--out',str(OUT/'catalogue.json')],check=True,cwd=ROOT)
                    from scripts.export_content import verify_manifest
                    manifest=json.loads((OUT/'catalogue.json').read_text());verify_manifest(manifest)
                    kwaku=next(r for r in manifest['payload']['entities']['characters'] if r['id']=='kwaku');assert kwaku['version']==2 and kwaku['data']['variants'][0]['cloth_colour']=='#48766B' and 'trick-mirror' not in kwaku['data']['powers'];checks.append('reviewed-character-cli-export')
                    page.locator('#validate').click();expect(page.locator('#dialog-title')).to_have_text('Production release blockers');assert json.loads(page.locator('#dialog-body').inner_text())['production_export_allowed'] is False;page.locator('#close-dialog').click();checks.append('production-blockers-visible')
                    connect('editor');page.locator('#open-lab').click();page.locator('#new-run').click();expect(page.locator('#lab-metrics')).to_contain_text('BEAT 0')
                    for i,label in enumerate(['Inspect the altered royal edict','Promise to protect the market witnesses','Enter the guarded archive','Recover the ledger of stolen names','Protect the witnesses; withhold the ledger']):
                        page.locator('#lab-actions').get_by_role('button',name=label,exact=True).click();expect(page.locator('#lab-metrics')).to_contain_text(f'BEAT {i+1}')
                    expect(page.locator('#lab-metrics')).to_contain_text('witnesses-protected');checks.append('negotiation-route-to-protection-ending')
                    page.locator('#lab').screenshot(path=str(OUT/'story-laboratory.png'));browser.close()
                if errors:raise RuntimeError('Browser console exceptions: '+repr(errors))
            finally:
                proc.terminate()
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
    report={'status':'passed','checks':checks,'check_count':len(checks),'javascript_exceptions':errors,'scope':'Local browser/API/persistence workflow only. Not Unreal compilation, gameplay, art or mobile performance.'}
    (OUT/'browser-smoke.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':
    try:main()
    except Exception as exc:
        message=str(exc)
        report={"status":"blocked" if "ERR_BLOCKED_BY_ADMINISTRATOR" in message or "Executable doesn't exist" in message else "failed", "error":message, "scope":"Browser verification did not complete. API tests do not establish UI correctness."}
        if not (OUT/'browser-smoke.json').exists():
            (OUT/'browser-smoke.json').write_text(json.dumps(report,indent=2)+'\n')
        raise
