"""Bind actual imported feline assets to one isolated lab Blueprint/map."""
import json,os
from pathlib import Path
import unreal

root=Path(__file__).resolve().parents[1]
report=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'leopard-lab.json'
source=json.loads((root/'.local/verification/osebo-family-20261015/native-import-v002/leopard-import.json').read_text())
dest='/Game/Ananse/Characters/OseboLeopard/Runtime_v001'
map_path='/Game/Ananse/Maps/CharacterLabs/L_OseboLeopardCharacterLab'
if report.exists() or unreal.EditorAssetLibrary.does_directory_exist(dest) or unreal.EditorAssetLibrary.does_asset_exist(map_path):
    raise RuntimeError('Preserve existing authored revisions and maps')
mesh=unreal.load_asset(source['mesh']);skeleton=unreal.load_asset(source['skeleton'])
names=['IdleGuard','Patrol','RunPursuit','TurnStop','Investigate','CaptureReach','StaggerRecover','Command','LimbIsolation']
clips=[unreal.load_asset(source['clips'][n]) for n in names]
assert isinstance(mesh,unreal.SkeletalMesh) and mesh.get_editor_property('skeleton')==skeleton
assert all(isinstance(c,unreal.AnimSequence) and c.get_editor_property('skeleton')==skeleton for c in clips)
tools=unreal.AssetToolsHelpers.get_asset_tools()
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.AnanseLeopardLabPlayer)
bp=tools.create_asset('BP_OseboLeopard',dest,unreal.Blueprint,factory)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cls=unreal.EditorAssetLibrary.load_blueprint_class(dest+'/BP_OseboLeopard')
cdo=unreal.get_default_object(cls);cdo.set_editor_property('leopard_mesh',mesh);cdo.set_editor_property('leopard_clips',clips)
assert unreal.EditorAssetLibrary.save_loaded_asset(bp)
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.AnanseLeopardLabMode)
mode=tools.create_asset('BP_OseboLeopardLabMode',dest,unreal.Blueprint,factory)
unreal.BlueprintEditorLibrary.compile_blueprint(mode)
mode_class=unreal.EditorAssetLibrary.load_blueprint_class(dest+'/BP_OseboLeopardLabMode')
unreal.get_default_object(mode_class).set_editor_property('default_pawn_class',cls)
assert unreal.EditorAssetLibrary.save_loaded_asset(mode)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.new_level(map_path)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);cube=unreal.load_asset('/Engine/BasicShapes/Cube.Cube')
floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-50))
floor.set_actor_label('Leopard isolated qualification floor');floor.static_mesh_component.set_static_mesh(cube)
floor.set_actor_scale3d(unreal.Vector(40,40,1))
actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(0,0,110))
light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,1000),unreal.Rotator(-45,-30,0))
light.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
actors.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,900)).light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode',mode_class)
assert levels.save_current_level()
report.write_text(json.dumps(dict(status='SAVED_PENDING_REOPEN_AND_PLAY',blueprint=bp.get_path_name(),
    generated_class=cls.get_path_name(),mode=mode.get_path_name(),map=map_path,
    mesh=source['mesh'],skeleton=source['skeleton'],physics=source['physics'],clips=source['clips'],
    animation_path='native single-node authored clip playback; ABP/CR and contacts pending',
    campaign_binding_changed=False,art_approved=False),indent=2)+'\n')
