"""Owned-window synthetic keyboard coverage; screenshots require visual review."""
import argparse,json,os,re,subprocess,time
from pathlib import Path
from native_episode_ui_smoke import request_close
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--executable',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--profile-dir',type=Path);a=p.parse_args()
out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
cmd=[str(a.executable.resolve()),'/Game/Characters/AnanseSpider/Lab_v001/L_AnanseCharacterLab','-ansimalloc','-windowed','-ResX=1280','-ResY=720','-abslog='+str(out/'session.log')]
if a.profile_dir:cmd+=[f'-UserDir={a.profile_dir.resolve()}']
env=os.environ.copy()
for n in ('PYTHONPATH','LD_LIBRARY_PATH'):env.pop(n,None)
def xd(*args):return subprocess.check_output(['xdotool',*map(str,args)],text=True).strip()
with (out/'process.log').open('x') as log:
 proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 report={'command':cmd,'pid':proc.pid,'input':'synthetic X11 keyboard; no physical controller/touch claim','accepted':False}
 (out/'launch.json').write_text(json.dumps(report,indent=2))
 try:
  window=None
  for _ in range(120):
   if proc.poll() is not None:raise RuntimeError('Exited before owned window')
   try:
    for candidate in xd('search','--onlyvisible','--pid',proc.pid).splitlines():
     if xd('getwindowpid',candidate)==str(proc.pid) and 'ANANSE' in xd('getwindowname',candidate).upper():window=int(candidate);break
   except subprocess.CalledProcessError:pass
   if window:break
   time.sleep(.5)
  if not window:raise RuntimeError('No verified owned window')
  report['window']=window;time.sleep(8)
  def key(name):
   if xd('getwindowpid',window)!=str(proc.pid):raise RuntimeError('Ownership changed')
   xd('windowfocus','--sync',window)
   if xd('getwindowpid',xd('getwindowfocus'))!=str(proc.pid):raise RuntimeError('Owned window did not receive focus')
   xd('key','--window',window,'--clearmodifiers',name);time.sleep(1)
  def capture(name):
   raw=out/(name+'.xwd');subprocess.run(['xwd','-silent','-id',str(window),'-out',str(raw)],check=True)
   subprocess.run(['convert',str(raw),str(out/(name+'.png'))],check=True)
  key('End');capture('baseline-selected');key('8');capture('leopard-command')
  for lod in ['lod0','lod1','lod2','automatic']:
   key('F10');capture('leopard-'+lod)
  xd('keydown','--window',window,'w');time.sleep(1);xd('keyup','--window',window,'w');capture('leopard-moved')
  key('Home');capture('spider-selected')
  key('v');capture('actual-wireframe');key('v');key('F2');capture('limb-clip')
  key('p');capture('paused');key('p');key('F6');key('F8');capture('profile-restored')
  xd('keydown','--window',window,'w');time.sleep(1);xd('keyup','--window',window,'w');capture('moved-after-restore')
  request_close(window);code=proc.wait(timeout=45)
  text=(out/'session.log').read_text(errors='replace')
  pauses=re.findall(r'ANANSE lab paused=(\d) world_time=([0-9.]+)',text)
  checks={'keyboard_baseline_commit':'ANANSE lab selection committed design=osebo-leopard-v1' in text,'keyboard_spider_commit':'ANANSE lab selection committed design=ananse-spider-existing' in text,'wireframe_bound':'ANANSE lab wireframe=on bound=1' in text,'materials_restored':'ANANSE lab wireframe=off' in text,'profile_committed':'ANANSE lab profile restored=1' in text,'pause_clock_frozen':len(pauses)==2 and pauses[0][0]=='1' and pauses[1][0]=='0' and abs(float(pauses[0][1])-float(pauses[1][1]))<.05}
  report['baseline_design']='osebo-leopard-v1'
  report.update(exit_code=code,accepted=code==0 and all(checks.values()),checks=checks,screenshots_require_review=True)
 except BaseException as exc:
  report['error']=str(exc)
  if proc.poll() is None:proc.terminate();proc.wait(timeout=20);report['forced_termination']=True
 finally:(out/'result.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'accepted':report['accepted'],'exit_code':report.get('exit_code')}))
raise SystemExit(0 if report['accepted'] else 1)
