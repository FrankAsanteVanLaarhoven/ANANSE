"""Complete dynamic sky/fill on the newly authored staging maps only."""
import unreal,json,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=True);report=out/'lighting.json';assert not report.exists();assert not(out/'before-lighting').exists();shutil.copytree(ROOT/'Unreal/Content/Ananse/Maps/Story_v001',out/'before-lighting')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);maps=[]
for name in ['L_Market_Authored','L_Sanctuary_Authored','L_Market_EpisodeStaging','L_Sanctuary_EpisodeStaging']:
 assert levels.load_level('/Game/Ananse/Maps/Story_v001/'+name)
 for a in actors.get_all_level_actors():
  if isinstance(a,unreal.DirectionalLight):
   a.light_component.set_editor_property('atmosphere_sun_light',True);a.light_component.set_editor_property('light_color',unreal.Color(255,224,192,255));a.light_component.set_editor_property('intensity',3.0)
  if isinstance(a,unreal.SkyLight):a.light_component.set_editor_property('real_time_capture',True);a.light_component.set_editor_property('intensity',.8)
 atmosphere=actors.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector());atmosphere.set_actor_label('Dynamic authored staging sky; desktop qualification only')
 assert levels.save_current_level();maps.append(name)
 # Release Python actor/component/world references before the next level's GC.
 a=None;atmosphere=None
report.write_text(json.dumps({'status':'saved_dynamic_sky_pending_render_review','maps':maps,'baked_lighting':False,'mobile_qualified':False,'creative_approved':False,'original_campaign_maps_changed':False},indent=2)+'\n')
