"""Fixed, readable review lighting on new Aso maps only; not device qualification."""
import unreal,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);reports=[]
for name in ['L_AsoYaaCharacterLab','L_Market_AsoNegotiation']:
 path='/Game/Ananse/Maps/Contact_v002/'+name;assert levels.load_level(path);allactors=actors.get_all_level_actors();assert not any(a.get_actor_label().startswith('AsoContact_')for a in allactors);row={'map':path,'lights':[]}
 if name=='L_Market_AsoNegotiation':
  a=next(a for a in allactors if isinstance(a,unreal.AnanseInteractable)and str(a.get_editor_property('character_id'))=='aso-yaa');origin=a.get_actor_location()
  for label,offset,power,radius in [('AsoContact_Key',(-180,-120,180),1800.,80.),('AsoContact_Fill',(-140,160,100),900.,100.),('AsoContact_Rim',(130,-120,200),1200.,70.)]:
   light=actors.spawn_actor_from_class(unreal.PointLight,origin+unreal.Vector(*offset));light.set_actor_label(label);c=light.get_component_by_class(unreal.PointLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);c.set_intensity(power);c.set_editor_property('attenuation_radius',500.);c.set_editor_property('source_radius',radius);c.set_editor_property('cast_shadows',label=='AsoContact_Key');row['lights'].append({'name':label,'relative_cm':offset,'lumens':power,'radius_cm':radius})
 volume=actors.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector());volume.set_actor_label('AsoContact_FixedExposure');volume.set_editor_property('unbound',True);volume.set_editor_property('priority',150.);settings=volume.get_editor_property('settings');settings.set_editor_property('override_auto_exposure_method',True);settings.set_editor_property('auto_exposure_method',unreal.AutoExposureMethod.AEM_MANUAL);settings.set_editor_property('override_auto_exposure_apply_physical_camera_exposure',True);settings.set_editor_property('auto_exposure_apply_physical_camera_exposure',False)
 for prop,value in [('auto_exposure_bias',-2.),('motion_blur_amount',0.),('bloom_intensity',0.)]:settings.set_editor_property('override_'+prop,True);settings.set_editor_property(prop,value)
 volume.set_editor_property('settings',settings);row.update(exposure='manual',physical_camera_exposure=False,exposure_bias_stops=-2.,bloom=0.,motion_blur=0.,note='Lab adds two pawn-attached neutral fills; cinematic camera depth of field remains disabled');assert levels.save_current_level();reports.append(row)
(out/'lighting.json').write_text(json.dumps(reports,indent=2)+'\n')
