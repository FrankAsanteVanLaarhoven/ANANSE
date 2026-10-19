"""Bounded fallback fill and approach-facing new sanctuary marker; no gameplay edits."""
import unreal,json,os
from pathlib import Path
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels.load_level('/Game/Ananse/Maps/EnvironmentRoute_v002/L_StoryForest_Route');rows=[];alias='/Game/Ananse/Environments/HeroCells_v001/GoldenWebCrossing/GoldenWebCrossing';crossing=unreal.load_asset(alias) if unreal.EditorAssetLibrary.does_asset_exist(alias) else unreal.EditorAssetLibrary.duplicate_asset('/Game/Ananse/Environments/HeroCells_v001/WebLace/WebLace',alias);assert crossing;assert unreal.EditorAssetLibrary.save_loaded_asset(crossing)
for a in actors.get_all_level_actors():
 if isinstance(a,unreal.AnanseEnvironmentCluster):
  if a.get_actor_label()=='Route GoldenWebCrossing':a.get_editor_property('instances').set_static_mesh(crossing);a.get_editor_property('instances').set_visibility(True,False);a.set_actor_hidden_in_game(False)
  if a.get_actor_label()=='Hero cell WebLace':a.get_editor_property('instances').set_visibility(False,False);a.set_actor_hidden_in_game(True)
 if isinstance(a,unreal.SkyLight):
  c=a.get_component_by_class(unreal.SkyLightComponent);rows.append({'label':a.get_actor_label(),'previous_intensity':c.get_editor_property('intensity'),'new_intensity':3.0,'policy':'existing fixed cubemap fallback; no recapture/new light/shipping strategy change'});c.set_intensity(3.0)
 if isinstance(a,unreal.AnanseEnvironmentCluster)and a.get_actor_label()=='Hero cell SanctuaryMarker':
  c=a.get_editor_property('instances');assert c.update_instance_transform(0,unreal.Transform(unreal.Vector(-120,430,0),unreal.Rotator(pitch=0,yaw=180,roll=0),unreal.Vector(1,1,1)),False,True,True)
assert levels.save_current_level();Path(os.environ['ANANSE_EVIDENCE_DIR']).write_text(json.dumps({'changes':rows,'baked_lighting':'BLOCKED','mobile':'UNQUALIFIED'},indent=2))
