"""Reopen Aso native assets and clone the accepted market without editing its bytes."""
import unreal,json,os,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False)
r=json.loads((R/'.local/verification/aso-yaa-20261016/native-01/AsoYaa-native.json').read_text());tools=unreal.AssetToolsHelpers.get_asset_tools()
mesh=unreal.load_asset(r['mesh']);rig=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(mesh));assert len(rig['bones'])==48;assert len(rig['morph_targets'])>=11
cls=unreal.load_class(None,r['generated_class']);assert cls;bp=unreal.load_asset(r['blueprint']);unreal.get_default_object(cls).set_editor_property('refined_face',True);unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp)
clips=[unreal.load_asset(path)for path in r['clips'].values()];assert len(clips)==16 and all(c.get_editor_property('skeleton')==mesh.get_editor_property('skeleton')for c in clips)
for key,typ in [('mesh',unreal.SkeletalMesh),('skeleton',unreal.Skeleton),('physics',unreal.PhysicsAsset),('animation_blueprint',unreal.AnimBlueprint),('ik',unreal.IKRigDefinition),('control_rig',unreal.ControlRigBlueprint),('definition',unreal.AnanseCharacterDefinition)]:assert isinstance(unreal.load_asset(r[key]),typ),(key,r[key])
source='/Game/Ananse/Maps/EpisodeAccepted_v001/L_Market_AcceptedVisuals';dest='/Game/Ananse/Maps/Negotiation_v001/L_Market_AsoNegotiation';file=R/'Unreal/Content'/(source.removeprefix('/Game/')+'.umap');before=hashlib.sha256(file.read_bytes()).hexdigest();levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not unreal.EditorAssetLibrary.does_asset_exist(dest);assert levels.new_level_from_template(dest,source);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);changed=[]
for actor in actors.get_all_level_actors():
 if isinstance(actor,unreal.AnanseInteractable)and str(actor.get_editor_property('character_id'))=='aso-yaa':
  component=actor.get_editor_property('character_visual');component.set_skeletal_mesh_asset(mesh);actor.set_editor_property('presentation_idle',clips[0]);actor.set_editor_property('negotiation_presentation',True);actor.set_editor_property('negotiation_clips',clips);changed.append(actor.get_path_name())
assert changed;assert levels.save_current_level();assert levels.load_level(dest);assert hashlib.sha256(file.read_bytes()).hexdigest()==before
(out/'native.json').write_text(json.dumps({'status':'saved_reopened_pending_rendered_runtime','map':dest,'source_map_unchanged':True,'changed_actors':changed,'native_asset_map':r,'rig':rig,'creative_approved':False},indent=2)+'\n')
