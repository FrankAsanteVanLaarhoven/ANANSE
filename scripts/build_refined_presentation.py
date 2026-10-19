"""Versioned lit maps and original PBR surface assets. Original levels unchanged."""
import unreal,json,os,hashlib,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=True);report=out/'presentation.json';assert not report.exists();section=os.environ['ANANSE_REFINEMENT_SECTION'];native=json.loads((ROOT/'.local/verification/art-refinement-20261015/native-02/native.json').read_text());dest='/Game/Ananse/Environments/Refinement_v002';tools=unreal.AssetToolsHelpers.get_asset_tools();surfaces=ROOT/'SourceArt/Environments/MarketSanctuary/Refinement_v002';mats={};result={'status':'failed','creative_approved':False}
try:
 for key in ['MarketEarth','ForestEarth','WarmPlaster','WeatheredWood']:
  path=dest+'/M_'+key
  if not unreal.EditorAssetLibrary.does_asset_exist(path):
   textures={}
   for suffix in ['Albedo','Normal']:
    task=unreal.AssetImportTask()
    for name,value in dict(filename=str(surfaces/(key+'_'+suffix+'.png')),destination_path=dest,automated=True,replace_existing=False,save=True).items():task.set_editor_property(name,value)
    tools.import_asset_tasks([task]);texture=unreal.load_asset(task.get_editor_property('imported_object_paths')[0]);assert isinstance(texture,unreal.Texture2D)
    if suffix=='Normal':texture.set_editor_property('srgb',False);texture.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP);assert unreal.EditorAssetLibrary.save_loaded_asset(texture)
    textures[suffix]=texture
   material=tools.create_asset('M_'+key,dest,unreal.Material,unreal.MaterialFactoryNew());coord=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionTextureCoordinate,-600,0);coord.set_editor_property('u_tiling',24. if key.endswith('Earth')else 1.);coord.set_editor_property('v_tiling',24. if key.endswith('Earth')else 1.)
   for suffix,prop in [('Albedo',unreal.MaterialProperty.MP_BASE_COLOR),('Normal',unreal.MaterialProperty.MP_NORMAL)]:
    sample=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionTextureSample,-350,0 if suffix=='Albedo'else 250);sample.set_editor_property('texture',textures[suffix]);sample.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if suffix=='Normal'else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR);unreal.MaterialEditingLibrary.connect_material_expressions(coord,'',sample,'UVs');assert unreal.MaterialEditingLibrary.connect_material_property(sample,'RGB',prop)
   rough=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionConstant,-350,400);rough.set_editor_property('r',.88);unreal.MaterialEditingLibrary.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);unreal.MaterialEditingLibrary.recompile_material(material);assert unreal.EditorAssetLibrary.save_loaded_asset(material)
  mats[key]=unreal.load_asset(path);assert isinstance(mats[key],unreal.Material)
 configs={'market-lab':('/Game/Ananse/Maps/Story_v001/L_Market_Authored','L_Market_PresentationRefined','Lab'),'market-episode':('/Game/Ananse/Maps/Story_v001/L_Market_EpisodeStaging','L_Market_EpisodeRefined','Episode'),'sanctuary-episode':('/Game/Ananse/Maps/Story_v001/L_Sanctuary_EpisodeStaging','L_Sanctuary_EpisodeRefined','Episode')};old,name,mode=configs[section];path='/Game/Ananse/Maps/Refinement_v003/'+name;assert not unreal.EditorAssetLibrary.does_asset_exist(path)
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert levels.new_level_from_template(path,old);changed=[]
 for actor in actors.get_all_level_actors():
  if isinstance(actor,unreal.DirectionalLight):
   actor.set_actor_rotation(unreal.Rotator(-28,-35,0),False);light=actor.light_component;light.set_mobility(unreal.ComponentMobility.MOVABLE);light.set_editor_property('intensity',30000.);light.set_editor_property('atmosphere_sun_light',True);light.set_editor_property('light_color',unreal.Color(255,227,195,255));light.set_editor_property('light_source_angle',1.5)
  if isinstance(actor,unreal.SkyLight):actor.light_component.set_mobility(unreal.ComponentMobility.MOVABLE);actor.light_component.set_editor_property('real_time_capture',True);actor.light_component.set_editor_property('intensity',8.);actor.light_component.recapture_sky()
  if isinstance(actor,unreal.StaticMeshActor):
   component=actor.static_mesh_component
   for i in range(component.get_num_materials()):
    current=component.get_material(i);materialname=current.get_name()if current else'';match=next((k for k in mats if k in materialname),None)
    if match:component.set_material(i,mats[match]);changed.append({'actor':actor.get_actor_label(),'slot':i,'material':mats[match].get_path_name()})
 volume=actors.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector());volume.set_actor_label('Refined daylight exposure EV100 approximately 11.94');volume.set_editor_property('unbound',True);settings=volume.get_editor_property('settings')
 for field,value in dict(auto_exposure_method=unreal.AutoExposureMethod.AEM_MANUAL,auto_exposure_apply_physical_camera_exposure=True,camera_iso=100.,camera_shutter_speed=125.,depth_of_field_fstop=5.6,auto_exposure_bias=0.,bloom_intensity=.15,vignette_intensity=.18).items():settings.set_editor_property('override_'+field,True);settings.set_editor_property(field,value)
 volume.set_editor_property('settings',settings)
 fog=actors.spawn_actor_from_class(unreal.ExponentialHeightFog,unreal.Vector(0,0,-50));fog.component.set_editor_property('fog_density',.001);fog.component.set_editor_property('fog_max_opacity',.3)
 import math
 centres=[(-900,-350),(0,0),(900,400),(1700,600)]if section!='sanctuary-episode'else[(-400,-350),(0,0)]
 for x,y in centres:
  position=unreal.Vector(x+500,y-250,550);target=unreal.Vector(x,y,100);delta=target-position;rotation=unreal.Rotator(math.degrees(math.atan2(delta.z,math.hypot(delta.x,delta.y))),math.degrees(math.atan2(delta.y,delta.x)),0);bounce=actors.spawn_actor_from_class(unreal.RectLight,position,rotation);bounce.set_actor_label('Courtyard bounce approximation; desktop');light=bounce.rect_light_component;light.set_mobility(unreal.ComponentMobility.MOVABLE);light.set_editor_property('intensity',300000.);light.set_editor_property('attenuation_radius',2200.);light.set_editor_property('source_width',800.);light.set_editor_property('source_height',600.);light.set_editor_property('cast_shadows',False);light.set_editor_property('light_color',unreal.Color(240,231,215,255))
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',unreal.load_class(None,native['modes'][mode]));assert levels.save_current_level()
 result.update(status='saved_pending_rendered_exposure_and_gameplay_check',map=path,template=old,materials=changed,sun_lux=30000,sky_intensity=8.,exposure={'method':'manual_physical','iso':100,'shutter':125,'fstop':5.6},geometry_and_collision_transforms_unchanged=True,mode=native['modes'][mode],mobile_qualified=False)
except Exception:result['exception']=traceback.format_exc();raise
finally:report.write_text(json.dumps(result,indent=2)+'\n')
