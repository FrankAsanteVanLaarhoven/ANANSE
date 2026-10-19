"""Owned-window ten-cycle contact evidence; synthetic input, isolated profile."""
import argparse,json,os,subprocess,time,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from scripts.native_episode_ui_smoke import request_close
from scripts.capture_motion_diagnostic import capture

def main():
 p=argparse.ArgumentParser();p.add_argument('--art-refine',action='store_true');p.add_argument('--executable',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--mode',choices=['cycles','walk','ledger','leopard'],required=True);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);exe=a.executable.resolve();editor=exe.name=='UnrealEditor';leopard=a.mode=='leopard';level='/Game/Ananse/Maps/ArtPass2_v003/L_LeopardArtContact'if leopard else'/Game/Ananse/Maps/Clearance_v001/L_AsoYaaCharacterLab';cmd=[str(exe)]+([str(R/'Unreal/Ananse.uproject'),'-game']if editor else[])+[level,'-ansimalloc','-windowed','-ResX=1280','-ResY=720','-NoScreenMessages','-AnanseArtPass2','-AnanseVisualReview','-AnanseInteractionRefinement','-AnanseArtRefinement','-AnanseNeutralLabLighting','-AnanseMotionReviewClean',f'-UserDir={out/"profile"}']
 if a.art_refine:
  assert not leopard
  cmd=[v.replace('/Game/Ananse/Maps/Clearance_v001/','/Game/Ananse/Maps/ArtRefine_v002/')for v in cmd];cmd.append('-AnanseAsoArtRefine')
 if not leopard:cmd+=['-AnanseAsoReview','-AnanseAsoContact','-AnanseAsoClearance','-AnanseAsoDiagnosticCamera']
 if a.mode in ['cycles','ledger']:cmd+=['-AnanseAsoLedgerClose']
 if a.mode=='cycles':cmd+=['-ini:Engine:[SystemSettings]:r.FreeSkeletalMeshBuffers=0','-AnanseAsoSurfaceCapture='+str(out/'surfaces'),'-AnanseAsoSupportAudit='+str(out/'support.jsonl')]
 env=os.environ.copy();env.pop('PYTHONPATH',None);env.pop('LD_LIBRARY_PATH',None);events=[]
 def xd(*args):return subprocess.check_output(['xdotool',*map(str,args)],text=True,stderr=subprocess.DEVNULL).strip()
 with(out/'runtime.log').open('w')as log:
  proc=subprocess.Popen(cmd,cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT);(out/'launch.json').write_text(json.dumps({'pid':proc.pid,'command':cmd},indent=2));deadline=time.monotonic()+90;window=None
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
  if a.mode=='cycles':
   for i in range(10):key('5');events.append({'cycle_requested':i+1,'monotonic_seconds':time.monotonic()});time.sleep(8.15)
   # Explicit cut cancellation, then complete re-entry; pause must preserve pose clock.
   key('5');time.sleep(3);key('1');time.sleep(.4);key('5');time.sleep(3);key('p');time.sleep(1);key('p');time.sleep(5.3);key('5');time.sleep(2);key('1');time.sleep(.4);key('5');time.sleep(8.15)
  else:
   import threading
   result={}
   def record():result.update(capture(proc.pid,exe,window,out/'video',15,30))
   thread=threading.Thread(target=record);thread.start();time.sleep(.4)
   if a.mode=='ledger':key('5');time.sleep(8.2);key('1');time.sleep(2);key('5')
   else:
    key('0');time.sleep(1.5);key('s'if not leopard else'w','keydown');time.sleep(3);key('s'if not leopard else'w','keyup');key('d','keydown');time.sleep(2);key('d','keyup');time.sleep(1);key('s'if not leopard else'w','keydown');time.sleep(1.5);key('s'if not leopard else'w','keyup')
   thread.join();assert result.get('captured_frames',0)>10
  request_close(window);code=proc.wait(timeout=30);assert code==0
 (out/'process.json').write_text(json.dumps({'exit_code':code,'forced':False,'mode':a.mode,'events':events,'input_scope':'Synthetic OS input to owned window. Cycles are requests until final evaluated phase records are checked; not physical controller/touch evidence.','camera':{'aso_control_pitch_yaw_roll':[-5,180,0],'arm_length_cm':130 if a.mode in ['cycles','ledger']else 277.2,'fov':55 if a.mode in ['cycles','ledger']else 70}if not leopard else'existing unchanged rear gameplay camera'},indent=2)+'\n')
if __name__=='__main__':main()
