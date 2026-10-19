"""Observe ordinary selector RSS across real commits and default GC intervals.

No forced collection, time-dilation change or verification metric accumulation.
This reports an observed window, not a statistical absence-of-leaks guarantee.
"""
import argparse,json,os,re,subprocess,time
from pathlib import Path
from native_episode_ui_smoke import request_close
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--executable',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--profile-dir',type=Path,required=True);p.add_argument('--round-trips',type=int,default=100);a=p.parse_args()
 if not 60<=a.round_trips<=200:p.error('Use60..200 complete ordinary round trips.')
 out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);session=out/'session.log'
 cmd=[str(a.executable.resolve()),'/Game/Characters/AnanseSpider/Lab_v001/L_AnanseCharacterLab','-ansimalloc','-windowed','-ResX=1280','-ResY=720',f'-UserDir={a.profile_dir.resolve()}',f'-abslog={session}']
 env=os.environ.copy()
 for k in ['PYTHONPATH','LD_LIBRARY_PATH']:env.pop(k,None)
 result=dict(command=cmd,accepted=False,scope='Owned-window synthetic keyboard; process RSS. Ordinary play, no verifier flags, no forced GC or changed GC interval.',samples=[])
 def xd(*args):return subprocess.check_output(['xdotool',*map(str,args)],text=True).strip()
 start=time.monotonic();proc=None
 try:
  with (out/'process.log').open('x') as stream:
   proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT);result['pid']=proc.pid
   window=None
   for _ in range(120):
    if proc.poll() is not None:raise RuntimeError('Native process exited before owned window')
    try:
     for candidate in xd('search','--onlyvisible','--pid',proc.pid).splitlines():
      if xd('getwindowpid',candidate)==str(proc.pid) and 'ANANSE' in xd('getwindowname',candidate).upper():window=candidate;break
    except subprocess.CalledProcessError:pass
    if window:break
    time.sleep(.5)
   if not window:raise RuntimeError('Owned game window unavailable')
   time.sleep(8);committed=[]
   for i in range(a.round_trips*2):
    expected='osebo-leopard-v1' if i%2==0 else 'ananse-spider-existing'
    if proc.poll() is not None:raise RuntimeError('Game exited during ordinary swapping')
    if xd('getwindowpid',window)!=str(proc.pid):raise RuntimeError('Window ownership changed')
    xd('windowfocus','--sync',window)
    if xd('getwindowpid',xd('getwindowfocus'))!=str(proc.pid):raise RuntimeError('Focus not on owned native window')
    xd('key','--window',window,'--clearmodifiers','End' if i%2==0 else 'Home')
    deadline=time.monotonic()+10
    while True:
     text=session.read_text(errors='replace') if session.exists() else ''
     commits=re.findall(r'ANANSE lab selection committed design=(ananse-spider-existing|osebo-leopard-v1)',text)
     if len(commits)>i:
      if len(commits)!=i+1 or commits[-1]!=expected:raise RuntimeError('Duplicate or wrong family commit')
      committed=commits;break
     if proc.poll() is not None or time.monotonic()>deadline:raise RuntimeError('Actual family commit timeout')
     time.sleep(.05)
    time.sleep(.55)
    status=Path(f'/proc/{proc.pid}/status').read_text();rss=int(re.search(r'^VmRSS:\s+(\d+) kB',status,re.M).group(1))*1024
    result['samples'].append(dict(transition=i+1,design=expected,seconds=time.monotonic()-start,resident_bytes=rss))
   request_close(int(window));code=proc.wait(timeout=45)
   result.update(exit_code=code,accepted=code==0 and len(committed)==a.round_trips*2,round_trips=a.round_trips,committed_transitions=len(committed),wall_seconds=time.monotonic()-start)
   tail=result['samples'][-40:];values=[x['resident_bytes']/1048576 for x in tail]
   result['last40_transition_rss_mib']=dict(first=values[0],last=values[-1],minimum=min(values),maximum=max(values),delta=values[-1]-values[0])
 except Exception as e:
  result['error']=str(e)
  if proc and proc.poll() is None:proc.terminate();proc.wait(timeout=20);result['forced_termination']=True
 finally:(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result.get(k) for k in ['accepted','exit_code','committed_transitions','last40_transition_rss_mib','error']}));return 0 if result['accepted'] else 1
if __name__=='__main__':raise SystemExit(main())
