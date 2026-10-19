"""Capture fixed-camera motion evidence from a real packaged environment."""
import argparse,hashlib,json,os,subprocess,time,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate(report,code,forest,disabled):
 expected='/Game/Ananse/Maps/EnvironmentRoute_v002/L_'+('StoryForest'if forest else'RiverMarket')+'_Route'
 rows=report.get('motion_clusters',[])
 cameras=report.get('cameras',[])
 camera_ok=len(cameras)==3 and all(c.get('horizontal_fov_degrees')==50 and bool(c.get('location_cm'))and bool(c.get('target_cm'))for c in cameras)
 expected_names={'CrownGuardian','RiverFig','TwinnedElder','StreamPools','EcologyIsland'}if forest else{'CanopySwag','RiverReach','VerandaCorner'}
 loaded={r.get('mesh','').rsplit('.',1)[-1]for r in rows}
 return (code==0 and report.get('passed')is True and report.get('world')==expected and report.get('secondary_disabled')is disabled and type(report.get('seconds'))in(int,float)and math.isfinite(report['seconds'])and 11<=report['seconds']<45 and camera_ok and (not rows if disabled else expected_names<=loaded) and all(r.get('mesh','').startswith('/Game/Ananse/Environments/Motion_v001/')and r.get('actor_tick')is False and r.get('collision')is False and type(r.get('instances'))is int and r['instances']>0 and any(m.startswith(('/Game/Ananse/Environments/Motion_v001/Surface/','/Game/Ananse/Environments/Motion_v001/Overrides/Ananse/Environments/'))for m in r.get('materials',[])) for r in rows))
def main():
 p=argparse.ArgumentParser();p.add_argument('--executable',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--forest',action='store_true');p.add_argument('--disabled',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);exe=a.executable.resolve();file=a.out.resolve()/'result.json';map='/Game/Ananse/Maps/EnvironmentRoute_v002/L_'+('StoryForest'if a.forest else'RiverMarket')+'_Route'
 cmd=[str(exe),map,'-ansimalloc','-windowed','-ResX=1280','-ResY=720','-unattended','-nosplash','-NoScreenMessages','-AnanseEnvironmentRoute','-AnanseAsoContact','-AnanseAcceptedVisuals','-AnanseStoryPresentation','-AnanseArtRefinement','-AnanseFormsScenery','-AnanseInteractionRefinement','-UserDir='+str(a.out.resolve()/'profile'),'-AnanseMotionReview='+str(file),'-trace=frame','-tracefile='+str(a.out.resolve()/'frames.utrace')]
 if a.disabled:cmd.append('-AnanseDisableSecondaryMotion')
 (a.out/'command.json').write_text(json.dumps({'command':cmd,'executable_sha256':hashlib.sha256(exe.read_bytes()).hexdigest()},indent=2));env=os.environ.copy();env.pop('PYTHONPATH',None);env.pop('LD_LIBRARY_PATH',None);start=time.monotonic();forced=False
 with(a.out/'runtime.log').open('w')as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
  try:code=proc.wait(timeout=90)
  except subprocess.TimeoutExpired:forced=True;proc.terminate();code=proc.wait(timeout=15)
 d=json.loads(file.read_text(encoding='utf-8-sig'))if file.exists()else{};ok=not forced and validate(d,code,a.forest,a.disabled);frames=[]
 for i in range(6):
  path=a.out/f'motion_{i}.png';ok &= path.is_file()
  if path.is_file():
   size=subprocess.check_output(['identify','-format','%w %h',str(path)],text=True).strip();ok &= size=='1280 720';frames.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 differences=[]
 if len(frames)==6:
  for i in [0,2,4]:
   comparison=subprocess.run(['compare','-metric','MAE',str(a.out/f'motion_{i}.png'),str(a.out/f'motion_{i+1}.png'),'null:'],capture_output=True,text=True);assert comparison.returncode in(0,1);differences.append(comparison.stderr.strip())
 warnings=[l for l in(a.out/'runtime.log').read_text(errors='replace').splitlines()if'Failed to find shader map'in l or'Failed to compile Material'in l or'Secondary motion dependency missing'in l];ok &= not warnings and(a.out/'frames.utrace').is_file()
 (a.out/'process.json').write_text(json.dumps({'accepted':bool(ok),'exit_code':code,'forced':forced,'wall_seconds':time.monotonic()-start,'frames':frames,'pair_mean_absolute_pixel_difference':differences,'material_warnings':warnings,'scope':'Binding/capture qualification only; temporal pixel difference includes normal flow, antialiasing and animation and does not establish naturalness or performance.'},indent=2));print('Secondary review capture:',ok);return 0 if ok else 1
if __name__=='__main__':raise SystemExit(main())
