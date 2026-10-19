"""Strict supervisor for evaluated feline contact fixtures, not art approval."""
import argparse,hashlib,json,math,os,subprocess,time
from pathlib import Path
from scripts.native_runtime_smoke import build_input_identity
ROOT=Path(__file__).resolve().parents[1]
MAP='/Game/Ananse/Maps/CharacterLabs/LeopardContact_v001/L_LeopardContactLab'
def verify(r,exit_code,interaction_refinement=False,visual_review=False,art_pass2=False):
 try:
  if type(exit_code) is not int or exit_code!=0 or r['passed'] is not True or not 160<=r['seconds']<190:return False
  if r['world']!=('/Game/Ananse/Maps/ArtPass2_v003/L_LeopardArtContact'if art_pass2 else'/Game/Ananse/Maps/Visual_v003/L_LeopardVisualContact'if visual_review else'/Game/Ananse/Maps/Interactions_v003/L_LeopardContactInteractions'if interaction_refinement else MAP) or r['mesh']!=('/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/OseboLeopard.OseboLeopard'if art_pass2 else'/Game/Ananse/Characters/OseboLeopard/Visual_v003/OseboLeopard.OseboLeopard'if visual_review else'/Game/Ananse/Characters/OseboLeopard/Interactions_v003/OseboLeopard.OseboLeopard'if interaction_refinement else'/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard'):return False
  if (interaction_refinement or visual_review or art_pass2) and (r.get('fixture_binding_valid') is not True or r.get('expected_fixture_map')!=r['world'] or r.get('expected_fixture_mesh')!=r['mesh']):return False
  if any(r[k] is not True for k in ['normal_lit_rendering','jump_started','web_transition_started','upper_body_graph_active']):return False
  m=r['metrics']
  if m['invalid_transforms']!=0 or m['solved_chains']!=2 or m['resets']<8:return False
  if len(m['legs'])!=2 or {l['leg'] for l in m['legs']}!={'L','R'}:return False
  for leg in m['legs']:
   if type(leg['samples']) is not int or leg['samples']<100:return False
   for key,limit in [('p95_stance_drift_cm',2),('max_penetration_cm',.5),('max_segment_length_error_cm',.1)]:
    v=leg[key]
    if type(v) not in (float,int) or not math.isfinite(v) or not 0<=v<=limit:return False
   for role in ['flat','ramp','steps','uneven','moving','disappearing']:
    n=leg['support_sample_coverage'].get('AnanseFixture:'+role)
    if type(n) is not int or n<100:return False
  return True
 except (KeyError,TypeError,ValueError):return False
def main():
 p=argparse.ArgumentParser();p.add_argument('--art-pass2',action='store_true');p.add_argument('--visual-review',action='store_true');p.add_argument('--interaction-refinement',action='store_true');p.add_argument('--out',type=Path,required=True);p.add_argument('--executable',type=Path);p.add_argument('--build-identity',type=Path);p.add_argument('--lod',type=int,choices=[0,1,2]);a=p.parse_args()
 out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
 exe=a.executable.resolve() if a.executable else Path('/home/favl/Unreal/UE_5.8.3-58210709/Engine/Binaries/Linux/UnrealEditor')
 cmd=[str(exe)]+([] if a.executable else [str(ROOT/'Unreal/Ananse.uproject'),'-game'])+[('/Game/Ananse/Maps/ArtPass2_v003/L_LeopardArtContact'if a.art_pass2 else'/Game/Ananse/Maps/Visual_v003/L_LeopardVisualContact'if a.visual_review else'/Game/Ananse/Maps/Interactions_v003/L_LeopardContactInteractions'if a.interaction_refinement else MAP),'-ansimalloc','-windowed','-ResX=1280','-ResY=720','-unattended','-NoScreenMessages',f'-AnanseLeopardContactVerify={out/"result.json"}','-trace=frame',f'-tracefile={out/"frames.utrace"}']
 if a.art_pass2:cmd.append('-AnanseArtPass2')
 if a.visual_review:cmd.append('-AnanseVisualReview')
 if a.interaction_refinement:cmd.append('-AnanseInteractionRefinement')
 inputs=json.loads(a.build_identity.read_text()) if a.build_identity else build_input_identity()
 if a.lod is not None:cmd+=[f'-AnanseLeopardForcedLOD={a.lod}']
 with exe.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 (out/'command.json').write_text(json.dumps(dict(command=cmd,inputs=inputs,executable_sha256=digest,identity_scope='preserved cook inputs' if a.build_identity else 'current tree'),indent=2)+'\n')
 env=os.environ.copy()
 for k in ['PYTHONPATH','LD_LIBRARY_PATH']:env.pop(k,None)
 start=time.monotonic();forced=False
 with (out/'runtime.log').open('w') as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
  try:code=proc.wait(timeout=240)
  except subprocess.TimeoutExpired:
   forced=True;proc.terminate()
   try:code=proc.wait(timeout=15)
   except subprocess.TimeoutExpired:proc.kill();code=proc.wait()
 r=json.loads((out/'result.json').read_text(encoding='utf-8-sig')) if (out/'result.json').exists() else {}
 passed=not forced and verify(r,code,a.interaction_refinement,a.visual_review,a.art_pass2) and all((out/n).is_file() and (out/n).stat().st_size>1000 for n in ['result.png','frames.utrace'])
 if a.lod is not None:passed &= r.get('evaluated_lod')==a.lod and r.get('available_lods')==3
 (out/'process.json').write_text(json.dumps(dict(accepted=passed,exit_code=code,forced_termination=forced,wall_seconds=time.monotonic()-start),indent=2)+'\n');print(json.dumps(dict(accepted=passed,exit_code=code)));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
