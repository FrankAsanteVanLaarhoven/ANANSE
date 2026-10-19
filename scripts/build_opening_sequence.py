"""Create a real, explicitly technical opening sequence from reviewed draft shot timings."""
import json,os
from pathlib import Path
import unreal
root=Path(__file__).resolve().parents[1];report=Path(os.environ['ANANSE_SEQUENCE_REPORT']);dest=os.environ['ANANSE_SEQUENCE_DEST']
if report.exists() or unreal.EditorAssetLibrary.does_directory_exist(dest):raise RuntimeError('Use fresh sequence/report destinations.')
shots=[s for s in json.loads((root/'production/market/shots.json').read_text())['shots'] if s['sequence']=='opening']
seq=unreal.AssetToolsHelpers.get_asset_tools().create_asset('LS_MarketOpening_Technical',dest,unreal.LevelSequence,unreal.LevelSequenceFactoryNew())
assert seq is not None
seq.set_display_rate(unreal.FrameRate(30,1));seq.set_playback_start(0);seq.set_playback_end(round(max(s['out_seconds'] for s in shots)*30))
cut=seq.add_track(unreal.MovieSceneCameraCutTrack)
positions=[(-1400,-1100,650),(-1100,-650,320),(-1000,-450,240),(-900,-450,230),(-800,-400,220),(-900,-350,200)]
for i,shot in enumerate(shots):
 binding=seq.add_spawnable_from_class(unreal.CineCameraActor)
 binding.set_name(shot['id']+' TECHNICAL BLOCKING')
 section=binding.add_track(unreal.MovieScene3DTransformTrack).add_section();section.set_range(round(shot['in_seconds']*30),round(shot['out_seconds']*30))
 channels=section.get_all_channels();values=[*positions[i%len(positions)],0,-12,30,1,1,1]
 assert len(channels)==9
 for c,value in zip(channels,values):c.set_default(value)
 cs=cut.add_section();cs.set_range(round(shot['in_seconds']*30),round(shot['out_seconds']*30));cs.set_camera_binding_id(seq.get_binding_id(binding))
assert unreal.EditorAssetLibrary.save_loaded_asset(seq)
report.write_text(json.dumps({'status':'CREATED_TECHNICAL_BLOCKING_NOT_FINAL_CINEMATIC','asset':seq.get_path_name(),'shots':[s['id'] for s in shots],'duration_seconds':max(s['out_seconds'] for s in shots),'dialogue':'Draft IDs only; no recordings or final performances supplied.'},indent=2)+'\n')
