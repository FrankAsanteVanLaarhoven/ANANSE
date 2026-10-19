"""Matched native comparison stills and two continuous owned-window recordings."""
import argparse,json,os,subprocess,time,sys,threading,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from scripts.capture_motion_diagnostic import capture
from scripts.native_episode_ui_smoke import request_close
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--executable',type=Path,required=True);p.add_argument('--before',action='store_true');p.add_argument('--view',choices=['front','profile','threequarter','gripfront','gripoblique'],default='front');p.add_argument('--video',choices=['walk','ledger']);p.add_argument('--comparison-fov',type=float);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);exe=a.executable.resolve();editor=exe.name=='UnrealEditor';base='Clearance_v001'if a.before else'ArtRefine_v002';map_path='/Game/Ananse/Maps/'+base+'/L_AsoYaaCharacterLab';view=('gripoblique'if a.video=='ledger'else'front')if a.video else a.view
cmd=[str(exe)]+([str(R/'Unreal/Ananse.uproject'),'-game']if editor else[])+[map_path,'-ansimalloc','-windowed','-ResX=1280','-ResY=720','-NoScreenMessages','-AnanseAsoReview','-AnanseAsoContact','-AnanseAsoClearance','-AnanseArtPass2','-AnanseVisualReview','-AnanseInteractionRefinement','-AnanseArtRefinement','-AnanseNeutralLabLighting','-AnanseMotionReviewClean','-AnanseAsoComparisonCamera='+view,'-ExecCmds=t.MaxFPS 60','-UserDir='+str(out/'profile')]
if a.comparison_fov is not None:
 assert 30<=a.comparison_fov<=100
 cmd=[v if not v.startswith('-ExecCmds=')else f'-ExecCmds=t.MaxFPS 60,fov {a.comparison_fov}'for v in cmd]
if not a.before:cmd.append('-AnanseAsoArtRefine')
env=os.environ.copy();env.pop('LD_LIBRARY_PATH',None);env.pop('PYTHONPATH',None);events=[]
def xd(*args):return subprocess.check_output(['xdotool',*map(str,args)],text=True,stderr=subprocess.DEVNULL).strip()
with(out/'runtime.log').open('x')as log:
 proc=subprocess.Popen(cmd,cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT);(out/'launch.json').write_text(json.dumps({'command':cmd,'pid':proc.pid,'executable_sha256':__import__('hashlib').file_digest(exe.open('rb'),'sha256').hexdigest()},indent=2));window=None;deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  assert proc.poll()is None,'Process exited before owned window'
  try:
   for w in xd('search','--onlyvisible','--pid',proc.pid).splitlines():
    if xd('getwindowpid',w)==str(proc.pid)and'ANANSE'in xd('getwindowname',w).upper():window=int(w);break
  except subprocess.CalledProcessError:pass
  if window:break
  time.sleep(.1)
 assert window;time.sleep(6);xd('windowfocus','--sync',window)
 def key(k,kind='key'):
  assert Path(f'/proc/{proc.pid}/exe').resolve()==exe and xd('getwindowpid',window)==str(proc.pid);xd(kind,'--window',window,k);events.append({'event':kind,'key':k,'monotonic_seconds':time.monotonic()})
 try:
  if a.video:
   result={}
   def record():result.update(capture(proc.pid,exe,window,out/'video',15,30))
   thread=threading.Thread(target=record);thread.start();time.sleep(.4)
   if a.video=='ledger':key('5');time.sleep(8.4);key('1')
   else:
    key('0');time.sleep(1.3);key('s','keydown');time.sleep(3);key('s','keyup');key('d','keydown');time.sleep(2);key('d','keyup');time.sleep(.7);key('s','keydown');time.sleep(1.3);key('s','keyup');time.sleep(.5);key('3');time.sleep(2.5);key('0')
   thread.join();assert result['captured_frames']>10
  else:
   key('5'if view.startswith('grip')else'1');time.sleep(3.25 if view.startswith('grip')else .25);key('p');time.sleep(.2);result=capture(proc.pid,exe,window,out/'capture',.25,30);shutil.copy2(out/'capture/frames'/result['frames'][0]['png'],out/'image.png')
  request_close(window);code=proc.wait(timeout=30);assert code==0
 except BaseException as error:
  if proc.poll()is None:
   request_close(window)
   try:proc.wait(timeout=30)
   except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=15)
  (out/'capture-failure.json').write_text(json.dumps({'error':repr(error),'exit_code':proc.returncode,'owned_window_closed':True},indent=2))
  raise
(out/'process.json').write_text(json.dumps({'exit_code':code,'forced':False,'before_assets':a.before,'view':view,'map':map_path,'events':events,'scope':'Native live rendering; synthetic owned-window inputs, diagnostic fixed camera only. Before uses protected v027 assets under the same executable, not a claim of rerunning frozen executable.','camera':{'projection':'perspective','control_pitch_yaw_roll':[-12 if view.startswith('grip')else 0,90 if view=='profile'else 135 if view in ['threequarter','gripoblique']else 180,0],'arm_cm':110 if view.startswith('grip')else 450,'fov_degrees':a.comparison_fov if a.comparison_fov is not None else 40 if view.startswith('grip')else 45,'target':'ledger centre+3cm for grip; skeletal bounds centre Z for full body; actor XY pivot','exposure':'existing neutral-lab lighting configuration unchanged','dof':'unchanged existing disabled review setup'}},indent=2)+'\n')
