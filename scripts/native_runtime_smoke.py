#!/usr/bin/env python3
"""Launch native Development acceptance scenarios; Python only supervises processes."""
import argparse,json,os,subprocess,time,hashlib,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.export_content import verify_manifest

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--engine-root',type=Path,required=True)
    parser.add_argument('--mode',choices=['r2','baseline','reload'],required=True)
    parser.add_argument('--context',choices=['pie','game','package'],default='pie')
    parser.add_argument('--executable',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--slot')
    parser.add_argument('--offscreen',action='store_true')
    parser.add_argument('--allocator',choices=['default','ansi'],default='default')
    args=parser.parse_args()
    engine=args.engine_root.resolve()
    version=json.loads((engine/'Engine/Build/Build.version').read_text())
    if version!=json.loads((ROOT/'toolchain.lock.json').read_text())['build_version']:raise RuntimeError('Engine pin mismatch.')
    if args.mode=='reload' and not args.slot:parser.error('Reload requires the previous dedicated --slot.')
    if args.context=='package' and not args.executable:parser.error('Package requires --executable.')
    manifest=json.loads((ROOT/'Unreal/Content/Data/catalogue.json').read_text());verify_manifest(manifest)
    kwaku=next(r for r in manifest['payload']['entities']['characters'] if r['id']=='kwaku')
    if args.mode=='r2' and (kwaku['version']!=2 or 'trick-mirror' in kwaku['data']['powers']):raise RuntimeError('r2 check requires the preserved restricted revision2.')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    slot=args.slot or ('AnanseVerify_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'))
    executable=args.executable.resolve() if args.executable else engine/'Engine/Binaries/Linux/UnrealEditor'
    command=[str(executable)]
    if args.context!='package':command.append(str(ROOT/'Unreal/Ananse.uproject'))
    if args.context=='pie':command.append('-ExecutePythonScript='+str(ROOT/'scripts/start_native_pie.py'))
    elif args.context=='game':command.append('-game')
    command+=['-windowed','-ResX=1280','-ResY=720','-unattended','-nop4','-nosplash','-stdout','-FullStdOutLogOutput','-abslog='+str(out/'runtime-session.log'),
        '-AnanseVerifyMode='+args.mode,'-AnanseVerifyReport='+str(out/'native-runtime.json'),
        '-AnanseExpectedHash='+manifest['sha256'],'-AnanseExpectedColour='+kwaku['data']['variants'][0]['cloth_colour'],
        '-AnanseExpectedMirror='+str(int('trick-mirror' in kwaku['data']['powers'])),'-AnanseVerifySlot='+slot]
    if args.offscreen:command.append('-RenderOffscreen')
    if args.allocator=='ansi':command.append('-ansimalloc')
    env=os.environ.copy()
    for key in ['PYTHONPATH','LD_LIBRARY_PATH']:env.pop(key,None)
    env['UE-LocalDataCachePath']=str(ROOT/'Unreal/DerivedDataCache')
    record={'command':command,'cwd':str(ROOT),'slot':slot,'mode':args.mode,'context':args.context,'revision':kwaku['version'],'publication_hash':manifest['sha256'],'engine_version':version,'removed_environment':['PYTHONPATH','LD_LIBRARY_PATH'],'offscreen':args.offscreen,'forced_termination':False,'timeout_seconds':210}
    start=time.monotonic()
    with (out/'process.log').open('x') as log:
        proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        record['pid']=proc.pid;(out/'launch.json').write_text(json.dumps(record,indent=2)+'\n')
        try:rc=proc.wait(timeout=210)
        except subprocess.TimeoutExpired:
            record['forced_termination']=True;record['termination_steps']=['SIGTERM to recorded PID'];proc.terminate()
            try:proc.wait(timeout=15)
            except subprocess.TimeoutExpired:record['termination_steps'].append('SIGKILL to recorded PID');proc.kill();proc.wait()
            rc=124
    record.update(exit_status=rc,process_returncode=proc.returncode,elapsed_seconds=time.monotonic()-start)
    log=out/'runtime-session.log'
    if args.context!='package' and log.exists():shutil.copy2(log,out/'session.log')
    (out/'command.json').write_text(json.dumps(record,indent=2)+'\n')
    path=out/'native-runtime.json';report=json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {'status':'missing'}
    passed=rc==0 and not record['forced_termination'] and report.get('status')=='assertions_passed' and report.get('play_stopped') and report.get('active_play_seconds',0)>=60 and bool(report.get('checks'))
    report['acceptance']='passed' if passed else 'failed';report['process_exit_status']=rc
    report['screenshots']=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in out.glob('*.png')]
    path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(record,indent=2));print(json.dumps(report,indent=2));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
