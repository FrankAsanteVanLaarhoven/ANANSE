#!/usr/bin/env python3
"""Non-destructive engine checks and native build commands. No signing or store publishing."""
from __future__ import annotations
import argparse,json,os,platform,shutil,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.export_content import verify_manifest
PROJECT=ROOT/'Unreal/Ananse.uproject'


def environment():
    system=platform.system();host={'Windows':'Win64','Linux':'Linux','Darwin':'Mac'}.get(system)
    raw=os.environ.get('UE_ROOT','');engine=Path(raw).expanduser().resolve() if raw else None
    info={'checked_at':datetime.now(timezone.utc).isoformat(),'host':host,'UE_ROOT':str(engine) if engine else None,'python':platform.python_version(),'engine_installed':False,'engine_compiled_here':False,'required_engine_family':'5.8','blockers':[],'warnings':[]}
    if not host:info['blockers'].append('Unsupported build host.')
    if engine and (engine/'Engine/Build/Build.version').is_file():
        info['engine_version']=json.loads((engine/'Engine/Build/Build.version').read_text());info['engine_installed']=True
        v=info['engine_version']
        if (v.get('MajorVersion'),v.get('MinorVersion'))!=(5,8):info['blockers'].append('This starter targets UE 5.8. Review and explicitly port for another engine family.')
    else:info['blockers'].append('UE_ROOT is unset or does not contain Engine/Build/Build.version. Install Epic-licensed UE 5.8 locally.')
    info['free_disk_gib']=round(shutil.disk_usage(ROOT).free/(1024**3),1)
    if info['free_disk_gib']<150:info['warnings'].append('Less than the proposed 150 GiB working-space reserve. Actual source builds may need substantially more.')
    for name in ['git','git-lfs','adb','java','xcodebuild']:info[name]=shutil.which(name)
    return info

def paths(engine,host):
    b=engine/'Engine/Build/BatchFiles'
    if host=='Win64':return b/'Build.bat',b/'RunUAT.bat',engine/'Engine/Binaries/Win64/UnrealEditor-Cmd.exe',engine/'Engine/Binaries/Win64/UnrealEditor.exe'
    if host=='Mac':
        editor=engine/'Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor';return b/'Mac/Build.sh',b/'RunUAT.sh',editor,editor
    editor=engine/'Engine/Binaries/Linux/UnrealEditor';return b/'Linux/Build.sh',b/'RunUAT.sh',editor,editor

def run(command,name,env=None,evidence_dir=None):
    output=(evidence_dir or ROOT/'evidence')/f'{name}.log';output.parent.mkdir(exist_ok=True)
    print('Running:',subprocess.list2cmdline([str(x) for x in command]))
    with output.open('w',encoding='utf-8') as log:
        result=subprocess.run([str(x) for x in command],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env=env,check=False)
    print(f'Exit {result.returncode}; full log: {output}')
    if result.returncode:raise RuntimeError(f'{name} failed. Inspect the log; no success is inferred.')


def verify_automation_report(index,not_before=None):
    if not_before is not None and Path(index).stat().st_mtime<not_before:
        raise RuntimeError('Stale automation report.')
    report=json.loads(Path(index).read_text(encoding='utf-8-sig'))
    if not isinstance(report,dict) or not isinstance(report.get('tests'),list):
        raise RuntimeError('Malformed automation report.')
    tests=report.get('tests',[])
    if any(not isinstance(t,dict) for t in tests):raise RuntimeError('Malformed test record.')
    for key in ['succeeded','succeededWithWarnings','failed','notRun','inProcess']:
        if key in report and (type(report[key]) is not int or report[key]<0):raise RuntimeError('Malformed automation summary.')
    if any(report.get(k,0) for k in ['failed','notRun','inProcess']):raise RuntimeError('Incomplete or failed automation summary.')
    if 'succeeded' in report and report['succeeded']+report.get('succeededWithWarnings',0)!=len(tests):raise RuntimeError('Inconsistent executed test count.')
    required={'Ananse.Mission.Negotiation','Ananse.Mission.PowerBudget'}
    identities=[t.get('fullTestPath') for t in tests]
    if any(not isinstance(name,str) or not name.startswith('Ananse.') for name in identities):
        raise RuntimeError('Unexpected or malformed ANANSE test identity.')
    if not required.issubset(identities) or len(set(identities))!=len(tests):
        raise RuntimeError('Missing required ANANSE tests or duplicate report identities.')
    if report.get('failed',0)>0 or any(str(t.get('state','')).lower()!='success' for t in tests):
        raise RuntimeError('Expected successful ANANSE automation tests and no failures.')
    return len(tests)

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['doctor','lock-engine','build','bootstrap','test','open','verify-android','package']);p.add_argument('--evidence-dir',type=Path,default=ROOT/'.local/verification'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')/'native');p.add_argument('--platform',choices=['Win64','Linux','Mac','Android','IOS']);p.add_argument('--replace-generated',action='store_true');p.add_argument('--variant',default='base');a=p.parse_args()
    a.evidence_dir=a.evidence_dir.resolve()
    info=environment();a.evidence_dir.mkdir(parents=True,exist_ok=True)
    doctor_report=a.evidence_dir/'unreal-doctor.json'
    if doctor_report.exists():raise RuntimeError('Doctor report exists. Select a fresh --evidence-dir to preserve evidence.')
    doctor_report.write_text(json.dumps(info,indent=2)+'\n')
    if a.command=='doctor':print(json.dumps(info,indent=2));return 2 if info['blockers'] else 0
    if info['blockers']:raise RuntimeError('; '.join(info['blockers']))
    engine=Path(info['UE_ROOT']);host=info['host'];build,uat,editor_cmd,editor=paths(engine,host)
    lockfile=ROOT/'toolchain.lock.json'
    if a.command=='lock-engine':
        if lockfile.exists():raise RuntimeError('toolchain.lock.json exists. Review its changes explicitly rather than overwriting a pin.')
        lockfile.write_text(json.dumps({'engine_family':'5.8','build_version':info['engine_version'],'locked_at':info['checked_at']},indent=2)+'\n');print('Engine exact Build.version recorded in toolchain.lock.json. Review and commit this file.');return 0
    if not lockfile.is_file():raise RuntimeError('Run python scripts/unreal.py lock-engine once and review the exact engine pin.')
    if json.loads(lockfile.read_text())['build_version']!=info['engine_version']:raise RuntimeError('Installed engine differs from toolchain.lock.json. Silent upgrades are blocked.')
    if a.command=='build':
        run([build,'AnanseEditor',host,'Development',f'-Project={PROJECT}','-WaitMutex','-NoHotReloadFromIDE'],'unreal-build',evidence_dir=a.evidence_dir);return 0
    if a.command=='bootstrap':
        previous=a.evidence_dir/'unreal-bootstrap.json'
        if previous.exists():raise RuntimeError('Bootstrap report exists. Select a fresh --evidence-dir.')
        env=os.environ.copy();env['ANANSE_EVIDENCE_DIR']=str(a.evidence_dir.resolve())
        if a.replace_generated:env['ANANSE_REGENERATE_GREYBOX']='1'
        run([editor_cmd,PROJECT,f'-ExecutePythonScript={ROOT/"scripts/build_greybox.py"}','-unattended','-nop4','-nosplash'],'unreal-bootstrap',env,evidence_dir=a.evidence_dir)
        if not previous.is_file() or json.loads(previous.read_text()).get('status')!='created':raise RuntimeError('No successful generated-map report. Engine exit code alone is insufficient.')
        return 0
    if a.command=='test':
        target=a.evidence_dir/'unreal-automation'
        if target.exists():raise RuntimeError('Archive or remove the old evidence/unreal-automation folder explicitly before a fresh test run.')
        started=time.time()
        run([editor_cmd,PROJECT,'-unattended','-nop4','-NullRHI','-nosound','-ExecCmds=Automation RunTests Ananse;SoftQuit',f'-ReportExportPath={target}'],'unreal-automation',evidence_dir=a.evidence_dir)
        index=target/'index.json'
        if not index.is_file():raise RuntimeError('No automation report. Tests are NOT verified.')
        count=verify_automation_report(index,not_before=started)
        print(f'Verified {count} Unreal automation results from a new report.');return 0
    if a.command=='open':
        if not (ROOT/'Unreal/Content/Maps/L_Market_Greybox.umap').is_file():raise RuntimeError('Run build and bootstrap before opening the intended greybox map.')
        run([editor,PROJECT,f'-AnanseVariant={a.variant}'],'unreal-editor',evidence_dir=a.evidence_dir);return 0
    if a.command=='verify-android':
        run([uat,'Turnkey','-command=VerifySdk','-platform=Android','-utf8output'],'android-sdk-verification',evidence_dir=a.evidence_dir);return 0
    if a.command=='package':
        target=a.platform or host
        if target=='IOS' and host!='Mac':raise RuntimeError('This starter requires a Mac for iOS. Remote-signing/build setup is not implemented.')
        if not (ROOT/'Unreal/Content/Maps/L_Market_Greybox.umap').is_file():raise RuntimeError('Generated greybox map is missing. Run build and bootstrap.')
        catalogue=ROOT/'Unreal/Content/Data/catalogue.json'
        if not catalogue.is_file():raise RuntimeError('Publish a prototype in the Studio and export its immutable catalogue before packaging.')
        verify_manifest(json.loads(catalogue.read_text()))
        archive=ROOT/'Builds'/target/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        archive.mkdir(parents=True,exist_ok=False)
        args=[uat,'BuildCookRun',f'-project={PROJECT}','-nop4',f'-platform={target}','-clientconfig=Development','-build','-cook','-stage','-pak','-iostore','-package','-archive',f'-archivedirectory={archive}','-map=/Game/Maps/L_Market_Greybox','-utf8output']
        if target=='Android':args.append('-cookflavor=ASTC')
        run(args,f'package-{target.lower()}',evidence_dir=a.evidence_dir)
        files=list(archive.rglob('*'))
        if not any(f.is_file() and f.stat().st_size>0 for f in files):raise RuntimeError('Packaging returned success but no non-empty output was found.')
        print('Development packaging completed. Installation, gameplay and real-device performance still require evidence; this is NOT a store submission.')
        return 0
    return 0
if __name__=='__main__':
    try:sys.exit(main())
    except (RuntimeError,KeyError,ValueError,OSError) as exc:print(f'BLOCKED: {exc}',file=sys.stderr);sys.exit(2)
