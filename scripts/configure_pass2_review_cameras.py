"""Disable defocus in the new diagnostic maps without touching original worlds."""
import unreal,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];b=R/'.local/verification/art-pass2-20261016';levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[]
for name in ['L_CharacterArtReview','L_LeopardArtContact','L_LeopardCinematicReview']:
 path='/Game/Ananse/Maps/ArtPass2_v002/'+name;assert levels.load_level(path);volume=next(a for a in actors.get_all_level_actors()if a.get_actor_label()=='ArtReview_FixedExposure_NoBlur');settings=volume.get_editor_property('settings')
 for prop,value in [('depth_of_field_fstop',32.),('depth_of_field_focal_distance',0.)]:settings.set_editor_property('override_'+prop,True);settings.set_editor_property(prop,value)
 volume.set_editor_property('settings',settings);assert levels.save_current_level();rows.append({'map':path,'fstop':32,'focal_distance_cm':0,'motion_blur_amount':settings.get_editor_property('motion_blur_amount'),'exposure_min':settings.get_editor_property('auto_exposure_min_brightness'),'exposure_max':settings.get_editor_property('auto_exposure_max_brightness')})
(b/'camera-settings.json').write_text(json.dumps(rows,indent=2)+'\n')
