"""Encode actual captured game frames using the already qualified local codec."""
import bpy,json,sys,hashlib
from pathlib import Path
folder=Path(sys.argv[sys.argv.index('--')+1]).resolve();d=json.loads((folder/'capture.json').read_text());assert d['status']=='captured_actual_owned_game_window';frames=d['frames'];assert len(frames)>10;dest=folder/'actual_gameplay_review.mp4';assert not dest.exists();duration=d['duration_seconds'];fps=8;count=int(duration*fps);mapped=[];source=0
for i in range(count):
 while source+1<len(frames)and frames[source+1]['elapsed_seconds']<=i/fps:source+=1
 mapped.append(frames[source]['png'])
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.fps=fps;s.frame_start=1;s.frame_end=len(mapped);seq=s.sequence_editor_create();strip=seq.strips.new_image('ActualGameWindow',str(folder/'frames'/mapped[0]),channel=1,frame_start=1)
for name in mapped[1:]:strip.elements.append(name)
strip.frame_final_duration=len(mapped);s.render.use_sequencer=True;s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.filepath=str(dest);bpy.ops.render.render(animation=True);assert dest.stat().st_size>0;(folder/'video-provenance.json').write_text(json.dumps({'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'native_capture_manifest_sha256':hashlib.sha256((folder/'capture.json').read_bytes()).hexdigest(),'duration_seconds':len(mapped)/fps,'fps':fps,'mapping':mapped,'scope':'Actual captured frames held to recorded times; no interpolated/generated gameplay frames; silent review video'},indent=2)+'\n')
