#!/usr/bin/env python3
"""Real loopback HTTP workflow with a server restart, isolated database and role tokens."""
import argparse,json,os,secrets,socket,subprocess,sys,tempfile,time
from pathlib import Path
from datetime import datetime,timezone
import httpx
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'.local/verification'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')/'http_smoke'
def main():
    global OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=OUT,help='Fresh evidence directory; existing reports are never overwritten.')
    OUT=parser.parse_args().out.resolve()
    OUT.mkdir(parents=True,exist_ok=True)
    if any(OUT.glob('*smoke.json')):
        raise RuntimeError('Evidence directory already contains smoke reports. Select a fresh --out directory.')
    checks=[]
    with tempfile.TemporaryDirectory(prefix='ananse-http-') as tmp:
        temp=Path(tmp);tokens={r:secrets.token_urlsafe(32) for r in ('editor','reviewer','publisher')};(temp/'tokens.json').write_text(json.dumps(tokens))
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        base=f'http://127.0.0.1:{port}'
        code="import os,json; from pathlib import Path; from studio.app import create_app; import uvicorn; p=Path(os.environ['ANANSE_SMOKE_DIR']); uvicorn.run(create_app(p/'db.sqlite3',json.loads((p/'tokens.json').read_text()),Path('content/seed.json')),host='127.0.0.1',port=int(os.environ['ANANSE_SMOKE_PORT']),access_log=False)"
        def start(log):
            process=subprocess.Popen([sys.executable,'-c',code],cwd=ROOT,env=os.environ|{'ANANSE_SMOKE_DIR':str(temp),'ANANSE_SMOKE_PORT':str(port)},stdout=log,stderr=subprocess.STDOUT)
            for _ in range(100):
                try:
                    if httpx.get(base+'/health',timeout=.3).status_code==200:return process
                except httpx.HTTPError:pass
                time.sleep(.1)
            process.terminate();process.wait();raise RuntimeError('HTTP smoke server startup failed.')
        def stop(process):
            process.terminate()
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:process.kill();process.wait()
        with (OUT/'http-server.log').open('w') as log,httpx.Client(base_url=base,timeout=10) as client:
            process=start(log)
            def req(method,path,role='editor',body=None,version=None,status=200):
                h={'Authorization':'Bearer '+tokens[role]}
                if version is not None:h['If-Match']=str(version)
                response=client.request(method,path,headers=h,json=body)
                assert response.status_code==status,(path,response.status_code,response.text)
                return response.json()
            try:
                assert client.get('/api/characters').status_code==401;checks.append('unauthenticated-read-rejected')
                assert req('GET','/api/characters')['total']==16;checks.append('seed-roster-loaded-over-http')
                for resource in ['/','/static/app.js','/static/style.css']:assert client.get(resource).status_code==200
                checks.append('html-javascript-css-served')
                character=req('GET','/api/characters/kwaku');character['data']['variants'][0]['cloth_colour']='#234567'
                changed=req('PATCH','/api/characters/kwaku',body={'data':character['data']},version=1);assert changed['version']==2
                req('PATCH','/api/characters/kwaku',body={'data':character['data']},version=1,status=412);checks.append('appearance-update-and-conflict-rejection')
                req('POST','/api/characters/kwaku/review','reviewer',{'version':2,'decision':'approved','note':'HTTP test approval; not cultural certification.'});checks.append('independent-role-review')
                published=req('POST','/api/publish','publisher',{'channel':'prototype'},status=201);assert req('GET','/api/publications/'+published['id'])==published['manifest'];checks.append('immutable-manifest-publication')
                req('POST','/api/publish','publisher',{'channel':'production'},status=409);checks.append('production-publish-blocked')
                session=req('POST','/api/lab/sessions',status=201)
                for action in ['inspect-evidence','negotiate','enter-archive','take-ledger','protect']:
                    session=req('POST',f'/api/lab/sessions/{session["id"]}/actions',body={'expected_version':session['version'],'action':action})
                assert session['state']['outcome']=='witnesses-protected';checks.append('complete-negotiated-lab-route')
                stop(process);process=start(log)
                assert req('GET','/api/characters/kwaku')['data']['variants'][0]['cloth_colour']=='#234567';checks.append('character-survives-real-server-restart')
                assert req('GET',f'/api/lab/sessions/{session["id"]}')==session;checks.append('lab-state-survives-real-server-restart')
                assert req('GET','/api/audit')['integrity']['valid'];checks.append('audit-integrity-after-restart')
            finally:stop(process)
    report={'status':'passed','check_count':len(checks),'checks':checks,'scope':'Real HTTP and fresh-process persistence. No browser interaction or Unreal runtime verification.'}
    (OUT/'http-smoke.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
