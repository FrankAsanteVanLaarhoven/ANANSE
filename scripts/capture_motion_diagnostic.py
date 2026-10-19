"""Continuous owned-window X11 captures; one PNG per actual read, no interpolation."""
import argparse,ctypes as C,hashlib,json,os,queue,struct,subprocess,threading,time,zlib
from pathlib import Path

def capture(pid,executable,window,out,seconds=15,fps=30):
 out=Path(out);out.mkdir(parents=True,exist_ok=False);frames=out/'frames';frames.mkdir();exe=Path(executable).resolve();assert Path(f'/proc/{pid}/exe').resolve()==exe
 owner=subprocess.check_output(['xdotool','getwindowpid',str(window)],text=True).strip();assert owner==str(pid)
 x=C.CDLL('libX11.so.6');x.XOpenDisplay.restype=C.c_void_p;display=x.XOpenDisplay(None);assert display
 class Image(C.Structure):
  _fields_=[('width',C.c_int),('height',C.c_int),('xoffset',C.c_int),('format',C.c_int),('data',C.c_void_p),('byte_order',C.c_int),('bitmap_unit',C.c_int),('bitmap_bit_order',C.c_int),('bitmap_pad',C.c_int),('depth',C.c_int),('bytes_per_line',C.c_int),('bits_per_pixel',C.c_int),('red_mask',C.c_ulong),('green_mask',C.c_ulong),('blue_mask',C.c_ulong)]
 x.XGetImage.argtypes=[C.c_void_p,C.c_ulong,C.c_int,C.c_int,C.c_uint,C.c_uint,C.c_ulong,C.c_int];x.XGetImage.restype=C.POINTER(Image);x.XDestroyImage.argtypes=[C.POINTER(Image)]
 geom=subprocess.check_output(['xdotool','getwindowgeometry','--shell',str(window)],text=True);g=dict(line.split('=',1)for line in geom.splitlines());w=int(g['WIDTH']);h=int(g['HEIGHT']);rows=[];jobs=queue.Queue(4);errors=[]
 def chunk(name,data):return struct.pack('!I',len(data))+name+data+struct.pack('!I',zlib.crc32(name+data)&0xffffffff)
 def writer():
  while True:
   item=jobs.get()
   if item is None:jobs.task_done();break
   row,bgra=item
   try:
    rgb=bytearray(w*h*3);rgb[0::3]=bgra[2::4];rgb[1::3]=bgra[1::4];rgb[2::3]=bgra[0::4];filtered=b''.join(b'\0'+rgb[y*w*3:(y+1)*w*3]for y in range(h));data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(filtered,1))+chunk(b'IEND',b'');(frames/row['png']).write_bytes(data);row['sha256']=hashlib.sha256(data).hexdigest()
   except Exception as e:errors.append(str(e))
   finally:jobs.task_done()
 thread=threading.Thread(target=writer);thread.start();start=time.monotonic();next_due=start
 while time.monotonic()-start<seconds:
  if time.monotonic()<next_due:time.sleep(next_due-time.monotonic())
  assert Path(f'/proc/{pid}/exe').resolve()==exe
  begin=time.monotonic();image=x.XGetImage(display,window,0,0,w,h,0xffffffff,2);assert image
  try:
   im=image.contents;assert im.bits_per_pixel==32 and im.bytes_per_line==w*4 and(im.red_mask,im.green_mask,im.blue_mask)==(0xff0000,0xff00,0xff)
   data=C.string_at(im.data,im.bytes_per_line*h)
  finally:x.XDestroyImage(image)
  finish=time.monotonic();row={'frame':len(rows),'png':f'frame_{len(rows):05d}.png','elapsed_seconds':finish-start,'read_start_seconds':begin-start,'read_duration_ms':1000*(finish-begin)};rows.append(row);jobs.put((row,data));next_due+=1/fps
  if next_due<time.monotonic()-1/fps:next_due=time.monotonic()
 duration=time.monotonic()-start;jobs.put(None);jobs.join();thread.join();assert not errors,errors;x.XCloseDisplay.argtypes=[C.c_void_p];x.XCloseDisplay(display)
 intervals=[b['elapsed_seconds']-a['elapsed_seconds']for a,b in zip(rows,rows[1:])];sorted_dt=sorted(intervals);result={'status':'actual_owned_window_reads','pid':pid,'window':window,'executable':str(exe),'executable_sha256':hashlib.file_digest(exe.open('rb'),'sha256').hexdigest(),'duration_seconds':duration,'target_capture_fps':fps,'captured_frames':len(rows),'distinct_pixel_hashes':len({r['sha256']for r in rows}),'achieved_capture_fps':(len(rows)-1)/(rows[-1]['elapsed_seconds']-rows[0]['elapsed_seconds']),'interval_p95_ms':1000*sorted_dt[int(.95*(len(sorted_dt)-1))],'interval_max_ms':1000*max(intervals),'intervals_over_50ms':sum(dt>.05 for dt in intervals),'estimated_missed_30hz_slots':sum(max(0,round(dt*fps)-1)for dt in intervals),'width':w,'height':h,'frames':rows,'interpolated_frames':0,'held_frame_upconversion':False,'audio':False,'scope':'Capture sampling only, not game frame rate, GPU timing or physical-device qualification.'};(out/'capture.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--executable',type=Path,required=True);p.add_argument('--window',type=int,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--seconds',type=float,default=15);a=p.parse_args();r=capture(a.pid,a.executable,a.window,a.out,a.seconds);print({k:v for k,v in r.items()if k!='frames'})
