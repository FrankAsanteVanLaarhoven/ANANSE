"""Editor-only technical epilogue assembly. No final forest-art or bake claim."""
import json
import os
from pathlib import Path

import unreal

MAP = '/Game/Production/Sanctuary/Technical_v001/L_StorySanctuary_Technical'
report_path = Path(os.environ['ANANSE_EVIDENCE_DIR']) / 'sanctuary-assets.json'
if report_path.exists() or unreal.EditorAssetLibrary.does_asset_exist(MAP):
    raise RuntimeError('Existing map/report preserved. Select a new reviewed version, never overwrite.')
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not levels.new_level(MAP):
    raise RuntimeError('New technical epilogue level failed.')
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode', unreal.AnanseGameMode)
floor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, -50))
floor.set_actor_label('Technical sanctuary floor - production forest art missing')
floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube.Cube'))
floor.set_actor_scale3d(unreal.Vector(20, 20, 1))
start = actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-400, -350, 110))
start.set_actor_label('Campaign Kwaku start; Ananse remains a separate actor')
spider = actors.spawn_actor_from_class(unreal.AnanseSpiderLabPlayer, unreal.Vector(-100, 250, 110))
spider.set_actor_label('Ananse engineering proxy - final mesh, facial performance and cloth missing')
stone = actors.spawn_actor_from_class(unreal.AnanseInteractable, unreal.Vector(-100, 100, 60))
stone.set_editor_property('action', unreal.Name('epilogue'))
stone.set_editor_property('character_id', unreal.Name('ananse'))
stone.get_editor_property('label').set_text(unreal.Text('E: speak with Ananse / draft sanctuary epilogue'))
light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1000), unreal.Rotator(-45, -30, 0))
light.light_component.set_editor_property('intensity', 3.0)
light.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
sky = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 900))
sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
sky.light_component.set_editor_property('intensity', .8)
if not levels.save_current_level():
    raise RuntimeError('Sanctuary level save failed.')
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps({'map': MAP, 'saved': True, 'actors': len(actors.get_all_level_actors()),
                                  'art_status': 'technical blockout; no final forest, recording or bake',
                                  'player_identity': 'kwaku', 'spider_identity': 'ananse'}, indent=2) + '\n')
