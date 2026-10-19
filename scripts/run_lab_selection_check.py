"""Supervise rendered lab checks; require evaluated contacts and an orderly exit."""
import argparse,json,math,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def verify_report(report,exit_code,restart=False):
    if exit_code!=0 or report.get('passed') is not True or report.get('rendered_rhi') is not True:return False
    if not isinstance(report.get('seconds'),(float,int)) or not 60<=report['seconds']<=95:return False
    if report.get('selection_transactions')!=40 or (restart and report.get('restored_profile') is not True):return False
    try:
        metrics=json.loads(report['post_swap_contact_metrics']);legs=metrics['legs']
        if metrics['invalid_transforms']!=0 or metrics['last_solved_chains']!=4 or len(legs)!=4:return False
        if {leg['leg'] for leg in legs}!={'front_l','front_r','rear_l','rear_r'}:return False
        for leg in legs:
            if type(leg['samples']) is not int or leg['samples']<1:return False
            for key,limit in [('p95_stance_drift_cm',2),('max_penetration_cm',.5),('max_segment_length_error_cm',.1)]:
                value=leg[key]
                if not isinstance(value,(float,int)) or not math.isfinite(value) or not 0<=value<=limit:return False
            if leg['joint_limit_violations']!=0:return False
    except (KeyError,TypeError,ValueError):return False
    return True

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--executable',type=Path);p.add_argument('--restart',action='store_true');a=p.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    exe=a.executable.resolve() if a.executable else Path('/home/favl/Unreal/UE_5.8.3-58210709/Engine/Binaries/Linux/UnrealEditor')
    cmd=[str(exe)]+([] if a.executable else [str(ROOT/'Unreal/Ananse.uproject'),'-game'])+['/Game/Characters/AnanseSpider/Lab_v001/L_AnanseCharacterLab','-ansimalloc','-windowed','-ResX=1280','-ResY=720','-unattended','-nosplash','-NoScreenMessages',f'-AnanseLabVerify={out/"result.json"}','-trace=frame',f'-tracefile={out/"frames.utrace"}',f'-AnanseVerifyReport={out/"contact-samples.json"}']
    if a.restart:cmd+=['-AnanseLabRestoreCheck']
    env=os.environ.copy()
    for key in ['PYTHONPATH','LD_LIBRARY_PATH']:env.pop(key,None)
    (out/'command.json').write_text(json.dumps({'command':cmd,'restart':a.restart},indent=2))
    started=time.monotonic()
    with (out/'runtime.log').open('w') as log:
        process=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        try:code=process.wait(timeout=180)
        except subprocess.TimeoutExpired:
            process.terminate();process.wait(timeout=20)
            (out/'process.json').write_text(json.dumps({'accepted':False,'forced_termination':True,'reason':'Supervisor timeout; no normal-exit acceptance'},indent=2))
            return 1
    report=json.loads((out/'result.json').read_text()) if (out/'result.json').is_file() else {}
    ok=verify_report(report,code,a.restart)
    ok=ok and (out/'result.png').is_file() and (out/'result.png').stat().st_size>1000 and (out/'frames.utrace').is_file() and (out/'frames.utrace').stat().st_size>0
    (out/'process.json').write_text(json.dumps({'exit_code':code,'wall_seconds':time.monotonic()-started,'accepted':ok},indent=2))
    print(json.dumps({'exit_code':code,'accepted':ok,'seconds':report.get('seconds'),'swaps':report.get('selection_transactions')}))
    return 0 if ok else 1
if __name__=='__main__':raise SystemExit(main())
