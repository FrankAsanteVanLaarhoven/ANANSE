"""Encode the already rendered actual-model frames with the qualified DCC codec."""
import bpy,sys,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for key in ['Kwaku','AsoYaa','EsiHuman','OseboHuman','KojoTortoise','KofiHornbill','EsiMoth']:
 folder=root/'SourceArt/Characters'/key/('Authored_v002'if key=='Kwaku'else'Authored_v001')/'Technical_v001';dest=folder/'turntable.mp4';assert not dest.exists();assert all((folder/f'turn_{i:03d}.png').is_file()for i in range(24))
 bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.resolution_x=720;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.fps=12;s.frame_start=1;s.frame_end=24
 seq=s.sequence_editor_create();strip=seq.strips.new_image('ActualModelTurntable',str(folder/'turn_000.png'),channel=1,frame_start=1)
 for i in range(1,24):strip.elements.append(f'turn_{i:03d}.png')
 strip.frame_final_duration=24;s.render.use_sequencer=True;s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.filepath=str(dest);bpy.ops.render.render(animation=True);assert dest.stat().st_size>0
print('Seven source-model turntables encoded')
