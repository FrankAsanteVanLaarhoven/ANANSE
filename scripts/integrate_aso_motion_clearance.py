"""Create only the bounded revision6 lab; original campaign and content preserved."""
import unreal,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);base='/Game/Ananse/Characters/AsoYaa/Clearance_v001';report=json.loads((R/'.local/verification/aso-motion-correction-20261018/import/AsoYaa-native.json').read_text());mesh=unreal.load_asset(report['mesh']);clips=[unreal.load_asset(p)for p in report['clips'].values()]
# Proven same importer and frame conversion, once on fresh bytes only.
frame=unreal.EditorAssetLibrary.get_metadata_tag(mesh,'AnanseImportFrame')
if not frame:assert unreal.AnanseAnimationAuthoring.correct_interaction_import_frame(mesh)=='ok'
assert unreal.EditorAssetLibrary.save_loaded_asset(mesh); assert unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem).regenerate_lod(mesh,3,True,False)
assert unreal.AnanseAnimationAuthoring.add_story_sockets(mesh)is not None;assert not unreal.AnanseAnimationAuthoring.author_aso_ledger_grip(mesh,clips[4]);assert not unreal.AnanseAnimationAuthoring.prepare_leopard_quality(mesh);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
old=unreal.load_asset('/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa');oldrig=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(old));rig=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(mesh));assert rig['bones']==oldrig['bones'];assert rig['lod_count']==3
bp=unreal.load_asset(report['blueprint']);cdo=unreal.get_default_object(unreal.load_class(None,report['generated_class']));cdo.set_editor_property('aso_ledger_presentation',True);cdo.set_editor_property('ledger_mesh',unreal.load_asset('/Game/Ananse/Characters/AsoYaa/Contact_v002/Props/Ledger'));unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);dest='/Game/Ananse/Maps/Clearance_v001/L_AsoYaaCharacterLab';assert levels.load_level(dest);mode=unreal.EditorAssetLibrary.load_blueprint_class(base+'/BP_AsoYaaLabMode');world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',mode)
# Imported neutral lab contains no campaign actors; review lighting is provided by existing flag.
assert levels.save_current_level();assert levels.load_level(dest)
report.update(rig=rig,source_revision='Authored_v019',rest_skeleton_matches_previous=True,creative='REVIEW_REQUIRED',campaign_spring='PENDING; unchanged single-node path',source_scene=str(R/'SourceArt/Characters/AsoYaa/Authored_v019/AsoYaa.blend'))
(out/'native.json').write_text(json.dumps(report,indent=2)+'\n')
