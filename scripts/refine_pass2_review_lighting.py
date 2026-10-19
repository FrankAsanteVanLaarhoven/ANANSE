"""Distance-stable review illumination for the existing opt-in art maps only."""
import unreal,json,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];b=R/'.local/verification/art-pass2-20261016';out=b/'lighting-correction-03';out.mkdir(exist_ok=False);rows=[];levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for name in ['L_CharacterArtReview','L_LeopardArtContact','L_LeopardCinematicReview']:
 path='/Game/Ananse/Maps/ArtPass2_v003/'+name;file=R/'Unreal/Content/Ananse/Maps/ArtPass2_v003'/(name+'.umap');shutil.copy2(file,out/file.name);before=hashlib.sha256(file.read_bytes()).hexdigest();assert levels.load_level(path);lights=[]
 for label,rotation,lux in [('ArtReview_TravelStableKey',(-30,225,0),30),('ArtReview_TravelStableFill',(-25,45,0),12)]:
  light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,500),unreal.Rotator(*rotation));light.set_actor_label(label);component=light.get_component_by_class(unreal.DirectionalLightComponent);component.set_mobility(unreal.ComponentMobility.MOVABLE);component.set_intensity(lux);component.set_editor_property('cast_shadows',False);component.set_editor_property('light_source_angle',10.);lights.append({'label':label,'rotation_degrees':rotation,'intensity_lux':lux,'casts_shadows':False,'source_angle_degrees':10})
 assert levels.save_current_level();rows.append({'map':path,'before_sha256':before,'after_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'added_lights':lights,'preserved_failed_map_snapshot':str((out/file.name).relative_to(R))})
(out/'maps.json').write_text(json.dumps({'maps':rows,'reason':'Actual package Kwaku moved ~583cm from PlayerStart light cluster and became silhouetted. Distance-stable soft review key/fill keep travel/turn lighting readable; original world maps untouched. Not mobile lighting qualification.'},indent=2)+'\n')
