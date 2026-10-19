"""Lossless screenshots of one recorded, owned native game window.
No desktop-wide, microphone, system-audio or unrelated-window recording.
"""
import argparse,subprocess,json,time,hashlib,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--launch',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--seconds',type=float,default=80);p.add_argument('--fps',type=float,default=8);a=p.parse_args();assert 1<=a.seconds<=90 and 1<=a.fps<=12;out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);frames=out/'frames';frames.mkdir();deadline=time.monotonic()+90
while not a.launch.is_file():
 if time.monotonic()>deadline:raise RuntimeError('No recorded launch')
 time.sleep(.2)
launch=json.loads(a.launch.read_text());pid=int(launch['pid']);expected=Path(launch['command'][0]).resolve();assert Path('/proc/'+str(pid)+'/exe').resolve()==expected

def xd(*args):return subprocess.check_output(['xdotool',*map(str,args)],text=True,stderr=subprocess.DEVNULL).strip()
window=None
while time.monotonic()<deadline:
 assert Path('/proc/'+str(pid)+'/exe').resolve()==expected
 try:
  candidates=xd('search','--onlyvisible','--pid',pid).splitlines()
  for candidate in candidates:
   if xd('getwindowpid',candidate)==str(pid)and'ANANSE'in xd('getwindowname',candidate).upper():window=int(candidate);break
 except subprocess.CalledProcessError:pass
 report=a.launch.parent/'native-runtime.json'
 if window and report.is_file():
  try:
   if json.loads(report.read_text(encoding='utf-8-sig')).get('active_play_seconds',0)>=5:break
  except json.JSONDecodeError:pass
 time.sleep(.2)
else:raise RuntimeError('Owned game window/readiness not found')
rows=[];started=time.monotonic();index=0
while time.monotonic()-started<a.seconds:
 assert Path('/proc/'+str(pid)+'/exe').resolve()==expected and xd('getwindowpid',window)==str(pid)
 now=time.monotonic();raw=out/'current-frame.xwd';png=frames/f'frame_{index:05d}.png';subprocess.run(['xwd','-silent','-id',str(window),'-out',str(raw)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);subprocess.run(['convert',str(raw),str(png)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);rows.append({'frame':index,'elapsed_seconds':now-started,'png':png.name,'sha256':hashlib.sha256(png.read_bytes()).hexdigest()});raw.unlink();index+=1;delay=started+index/a.fps-time.monotonic()
 if delay>0:time.sleep(delay)
result={'status':'captured_actual_owned_game_window','pid':pid,'executable':str(expected),'window':window,'duration_seconds':time.monotonic()-started,'requested_fps':a.fps,'frames':rows,'audio_recorded':False,'scope':'Actual gameplay review capture with capture overhead; not physical input, audio or performance qualification'};(out/'capture.json').write_text(json.dumps(result,indent=2)+'\n');print('Captured native review frames',len(rows))
