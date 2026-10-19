"""Fresh technical chase-introduction camera; no final performance/audio claims."""
from pathlib import Path
import os,json
import unreal
report=Path(os.environ['ANANSE_PURSUIT_SEQUENCE_REPORT']);dest='/Game/Production/Market/Technical_v002'
if report.exists() or unreal.EditorAssetLibrary.does_directory_exist(dest):raise RuntimeError('Fresh destination required')
seq=unreal.AssetToolsHelpers.get_asset_tools().create_asset('LS_PursuitIntro_Technical',dest,unreal.LevelSequence,unreal.LevelSequenceFactoryNew());assert seq
seq.set_display_rate(unreal.FrameRate(30,1));seq.set_playback_start(0);seq.set_playback_end(150)
camera=seq.add_spawnable_from_class(unreal.CineCameraActor);camera.set_name('Osebo approach / TECHNICAL PROXY')
s=camera.add_track(unreal.MovieScene3DTransformTrack).add_section();s.set_range(0,150)
for channel,value in zip(s.get_all_channels(),[500,0,380,0,-15,35,1,1,1]):channel.set_default(value)
s=seq.add_track(unreal.MovieSceneCameraCutTrack).add_section();s.set_range(0,150);s.set_camera_binding_id(seq.get_binding_id(camera))
assert unreal.EditorAssetLibrary.save_loaded_asset(seq);report.write_text(json.dumps({'asset':seq.get_path_name(),'seconds':5,'status':'TECHNICAL_CAMERA_NOT_FINAL_ART_AUDIO'},indent=2)+'\n')
