"""Add authored environments/characters to NEW episode staging maps.
Original campaign levels, identities and published character revisions are preserved.
"""
import unreal,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=Path(os.environ['ANANSE_EVIDENCE_DIR']);OUT.mkdir(parents=True,exist_ok=True);report=OUT/'episode-staging.json'
if report.exists():raise RuntimeError('Preserve earlier staging')
tools=unreal.AssetToolsHelpers.get_asset_tools();dest='/Game/Ananse/Characters/Kwaku/Story_v001';source=json.loads((ROOT/'.local/verification/story-cast-20261015/native-Kwaku/Kwaku-native.json').read_text())
dest='/Game/Ananse/Characters/Kwaku/Story_v001'
storyclass=unreal.EditorAssetLibrary.load_blueprint_class(dest+'/BP_KwakuEpisodeStaging')
modeclass=unreal.EditorAssetLibrary.load_blueprint_class(dest+'/BP_StoryEpisodeStagingMode')
assert storyclass and modeclass
assert unreal.get_default_object(storyclass).get_editor_property('story_campaign_presentation')
env=json.loads((ROOT/'.local/verification/story-cast-20261015/environment-native/environments-native.json').read_text());collidable=set(json.loads((ROOT/'.local/verification/story-cast-20261015/environment-refine-01/result.json').read_text())['static_complex_collision']);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);maps=[]
for market,old in [(os.environ['ANANSE_STAGE_SECTION']=='market','/Game/Maps/L_Market_Greybox' if os.environ['ANANSE_STAGE_SECTION']=='market' else '/Game/Production/Sanctuary/Technical_v001/L_StorySanctuary_Technical')]:
 path='/Game/Ananse/Maps/Story_v001/'+('L_Market_EpisodeStaging'if market else'L_Sanctuary_EpisodeStaging');assert not unreal.EditorAssetLibrary.does_asset_exist(path);assert levels.new_level_from_template(path,old)
 for a in actors.get_all_level_actors():
  label=a.get_actor_label()
  if market and label.startswith(('Stall base','Stall canopy','Canopy post')):actors.destroy_actor(a);continue
  if isinstance(a,unreal.StaticMeshActor)and('floor'in label.lower()):a.static_mesh_component.set_material(0,unreal.load_asset('/Game/Ananse/Environments/Story_v001/Surface/M_'+('MarketEarth'if market else'ForestEarth')))
 for group,p in env['meshes'].items():
  if market==group.startswith('Sanctuary'):continue
  mesh=unreal.load_asset(p);a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.set_actor_label('Authored '+group+' WIP');a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_profile_name('BlockAll'if p in collidable else'NoCollision')
 if market:
  # Static conversational performance actors are visuals, never extra mission/AI owners.
  for key,pos in [('AsoYaa',(50,-80,0)),('EsiHuman',(-900,-530,0))]:
   native=json.loads((ROOT/'.local/verification/story-cast-20261015'/('native-'+key)/(key+'-native.json')).read_text());mesh=unreal.load_asset(native['mesh']);clip=unreal.load_asset(next(iter(native['clips'].values())));a=actors.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector(*pos));a.set_actor_label(key+' visual WIP; existing interaction remains authoritative');c=a.skeletal_mesh_component;c.set_skeletal_mesh_asset(mesh);c.set_collision_profile_name('NoCollision');data=unreal.SingleAnimationPlayData();data.set_editor_property('anim_to_play',clip);data.set_editor_property('saved_looping',True);data.set_editor_property('saved_playing',True);c.set_editor_property('animation_mode',unreal.AnimationMode.ANIMATION_SINGLE_NODE);c.set_editor_property('animation_data',data)
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',modeclass);assert levels.save_current_level();maps.append(path)
report.write_text(json.dumps({'status':'saved_pending_played_episode_verification','maps':maps,'continuation':'Create one map per editor using installed NewLevelFromTemplate API; original failed duplicate-world evidence retained','kwaku_pawn_class':storyclass.get_path_name(),'required_command_flag':'-AnanseStoryPresentation','canonical_records_changed':False,'original_maps_changed':False,'creative_approved':False,'missing':'Final facial/cloth performance,recordings,environment quality review; species mappings unchanged'},indent=2)+'\n')
