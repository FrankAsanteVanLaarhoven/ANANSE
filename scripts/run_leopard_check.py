"""Supervise real isolated feline playback/movement, preserving failed results."""
import argparse,hashlib,json,os,subprocess,time
from pathlib import Path
from scripts.native_runtime_smoke import build_input_identity
ROOT=Path(__file__).resolve().parents[1]
MAP='/Game/Ananse/Maps/CharacterLabs/L_OseboLeopardCharacterLab'

def verify(report,code,art_pass2=False):
    map_path='/Game/Ananse/Maps/ArtPass2_v003/L_LeopardArtContact' if art_pass2 else MAP
    pawn_base='/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/' if art_pass2 else '/Game/Ananse/Characters/OseboLeopard/Runtime_v001/'
    mesh_base='/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/' if art_pass2 else '/Game/Ananse/Characters/OseboLeopard/Authored_v001/'
    expected={"IdleGuard","Patrol","RunPursuit","TurnStop","Investigate","CaptureReach","StaggerRecover","Command","LimbIsolation"}
    clips=report.get('clips',[])
    current_paths={'/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard'+name+'.OseboLeopard'+name for name in expected if name!='CaptureReach'}
    current_paths.add('/Game/Ananse/Characters/OseboLeopard/Visual_v003/Capture_v002/OseboCapture.OseboCapture')
    return (type(code) is int and code==0 and report.get('passed') is True
      and report.get('normal_lit_rendering') is True and 60<=report.get('seconds',0)<95
      and report.get('world')==map_path+'.'+map_path.rsplit('/',1)[-1]
      and report.get('pawn_class')==pawn_base+'BP_OseboLeopard.BP_OseboLeopard_C'
      and report.get('mesh')==mesh_base+'OseboLeopard.OseboLeopard'
      and report.get('bones')==64 and report.get('ability_grants')==0 and report.get('movement_cm',0)>100
      and report.get('face_forward_alignment',-1)>.95
      and report.get('animation_instance')=='/Game/Ananse/Characters/OseboLeopard/Animations/ABP_OseboLeopard.ABP_OseboLeopard_C'
      and len(clips)==9 and all(c.get('evaluated_bone_motion') is True and c.get('graph_clip_observed') is True for c in clips)
      and ({c['clip'] for c in clips}==current_paths if art_pass2 else {c['clip'].rsplit('.',1)[-1].removeprefix('OseboLeopard') for c in clips}==expected))

def main():
    p=argparse.ArgumentParser();p.add_argument('--art-pass2',action='store_true');p.add_argument('--out',type=Path,required=True);p.add_argument('--executable',type=Path);p.add_argument('--save-profile',action='store_true');p.add_argument('--build-identity',type=Path);p.add_argument('--lod',type=int,choices=[0,1,2]);p.add_argument('--profile-dir',type=Path);a=p.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    exe=a.executable.resolve() if a.executable else Path('/home/favl/Unreal/UE_5.8.3-58210709/Engine/Binaries/Linux/UnrealEditor')
    result=out/'result.json'
    cmd=[str(exe)]+([] if a.executable else [str(ROOT/'Unreal/Ananse.uproject'),'-game'])+[MAP,'-ansimalloc','-windowed','-ResX=1280','-ResY=720','-unattended','-nosplash','-NoScreenMessages',f'-AnanseLeopardVerify={result}','-trace=frame',f'-tracefile={out/"frames.utrace"}']
    if a.art_pass2:
        cmd=[v.replace(MAP,'/Game/Ananse/Maps/ArtPass2_v003/L_LeopardArtContact')for v in cmd]
        cmd+=['-AnanseArtPass2','-AnanseVisualReview','-AnanseInteractionRefinement','-AnanseArtRefinement']
    if a.profile_dir:cmd+=[f'-UserDir={a.profile_dir.resolve()}']
    if a.save_profile:cmd+=['-AnanseLeopardSaveProfile']
    if a.lod is not None:cmd+=[f'-AnanseLeopardForcedLOD={a.lod}']
    inputs=json.loads(a.build_identity.read_text()) if a.build_identity else build_input_identity()
    with exe.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    record=dict(command=cmd,inputs=inputs,context='package' if a.executable else 'editor-game',executable_sha256=digest,
                identity_scope='preserved cook inputs' if a.build_identity else 'current tree; not independent package provenance')
    (out/'command.json').write_text(json.dumps(record,indent=2)+'\n')
    env=os.environ.copy()
    for k in ['PYTHONPATH','LD_LIBRARY_PATH']:env.pop(k,None)
    forced=False;started=time.monotonic()
    with (out/'runtime.log').open('w') as stream:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
        try:code=proc.wait(timeout=150)
        except subprocess.TimeoutExpired:
            forced=True;proc.terminate()
            try:code=proc.wait(timeout=20)
            except subprocess.TimeoutExpired:proc.kill();code=proc.wait()
    r=json.loads(result.read_text(encoding='utf-8-sig')) if result.exists() else {}
    accepted=not forced and verify(r,code,a.art_pass2) and result.with_suffix('.png').is_file() and (out/'frames.utrace').is_file()
    if a.lod is not None:accepted &= r.get('evaluated_lod')==a.lod and r.get('available_lods')==3
    (out/'process.json').write_text(json.dumps(dict(accepted=accepted,exit_code=code,forced_termination=forced,wall_seconds=time.monotonic()-started),indent=2)+'\n')
    print(json.dumps(dict(accepted=accepted,exit_code=code,forced_termination=forced)))
    return 0 if accepted else 1
if __name__=='__main__':raise SystemExit(main())
