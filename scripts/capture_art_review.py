"""Capture one verified owned native game window, with no desktop/audio capture."""
import argparse,subprocess,json,time,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--launch',type=Path,required=True);p.add_argument('--ready',type=Path,required=True);p.add_argument('--stop-file',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--seconds',type=float,default=55);p.add_argument('--fps',type=float,default=6);a=p.parse_args();assert 1<=a.seconds<=90 and 1<=a.fps<=8;out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);frames=out/'frames';frames.mkdir();deadline=time.monotonic()+100
while not a.launch.exists():
 if time.monotonic()>deadline:raise RuntimeError('No recorded native launch')
 time.sleep(.1)
d=json.loads(a.launch.read_text());pid=int(d['pid']);exe=Path(d['command'][0]).resolve()
def xd(*args):return subprocess.check_output(['xdotool',*map(str,args)],text=True,stderr=subprocess.DEVNULL).strip()
window=None
while time.monotonic()<deadline:
 assert Path('/proc/'+str(pid)+'/exe').resolve()==exe
 try:
  for candidate in xd('search','--onlyvisible','--pid',pid).splitlines():
   if xd('getwindowpid',candidate)==str(pid)and'ANANSE'in xd('getwindowname',candidate).upper():window=int(candidate);break
 except subprocess.CalledProcessError:pass
 if window and a.ready.exists():break
 time.sleep(.1)
else:raise RuntimeError('Owned native viewport did not reach the recorded readiness image')
rows=[];started=time.monotonic();index=0
while time.monotonic()-started<a.seconds:
 if a.stop_file and a.stop_file.exists():break
 assert Path('/proc/'+str(pid)+'/exe').resolve()==exe and xd('getwindowpid',window)==str(pid)
 now=time.monotonic();raw=out/'current.xwd';png=frames/f'frame_{index:05d}.png';subprocess.run(['xwd','-silent','-id',str(window),'-out',str(raw)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);subprocess.run(['convert',str(raw),str(png)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);raw.unlink();rows.append({'frame':index,'elapsed_seconds':now-started,'png':png.name,'sha256':hashlib.sha256(png.read_bytes()).hexdigest()});index+=1;delay=started+index/a.fps-time.monotonic()
 if delay>0:time.sleep(delay)
assert len(rows)>10;result={'status':'captured_actual_owned_game_window','pid':pid,'executable':str(exe),'executable_sha256':hashlib.file_digest(exe.open('rb'),'sha256').hexdigest(),'command':d['command'],'window':window,'duration_seconds':time.monotonic()-started,'requested_fps':a.fps,'frames':rows,'audio_recorded':False,'stop_file':str(a.stop_file)if a.stop_file else None,'scope':'Actual native scripted review; capture overhead, no physical-input/audio/performance qualification'};(out/'capture.json').write_text(json.dumps(result,indent=2)+'\n');print('NATIVE_REVIEW_FRAMES_CAPTURED',len(rows),flush=True)
