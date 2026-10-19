"""Create only a definition and Blueprint around the existing qualified spider."""
import json, os
from pathlib import Path
import unreal

DEST='/Game/Production/Characters/SpiderSelection_v001'
report=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'selection-assets.json'
if report.exists() or unreal.EditorAssetLibrary.does_directory_exist(DEST):
    raise RuntimeError('Existing assets/evidence preserved; use a reviewed new revision.')
mesh=unreal.load_asset('/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY')
if not isinstance(mesh,unreal.SkeletalMesh):raise RuntimeError('Qualified skeletal mesh missing')
skeleton=mesh.get_editor_property('skeleton')
clips=[unreal.load_asset('/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY'+n) for n in ['A_Idle_Proxy','A_LimbROM_Proxy','A_WeaveGesture_Proxy','A_CrawlInPlace_Proxy']]
if any(not isinstance(c,unreal.AnimSequence) or c.get_editor_property('skeleton')!=skeleton for c in clips):raise RuntimeError('Actual clip/skeleton incompatibility')
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.AnanseSpiderLabPlayer)
bp=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_AnanseSpider',DEST,unreal.Blueprint,factory)
if not bp:raise RuntimeError('Blueprint creation failed')
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cls=unreal.EditorAssetLibrary.load_blueprint_class(DEST+'/BP_AnanseSpider')
if not cls:raise RuntimeError('Generated pawn class missing')
factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.AnanseCharacterDefinition)
da=unreal.AssetToolsHelpers.get_asset_tools().create_asset('DA_AnanseSpider',DEST,unreal.AnanseCharacterDefinition,factory)
for key,value in {'design_id':'ananse-spider-existing','character_identity':'ananse','skeleton_key':'ananse-eight-limb-v002','revision':1,'engineering_fixture':True,'pawn_class':cls,'mesh':mesh,'clips':clips}.items():
    da.set_editor_property(key,value)
for asset in [bp,da]:
    if not unreal.EditorAssetLibrary.save_loaded_asset(asset):raise RuntimeError('Native asset save failed')
paths={'mesh':mesh.get_path_name(),'skeleton':skeleton.get_path_name(),'physics':mesh.get_editor_property('physics_asset').get_path_name() if mesh.get_editor_property('physics_asset') else None,'blueprint':bp.get_path_name(),'generated_class':cls.get_path_name(),'definition':da.get_path_name(),'lab_map':'/Game/Characters/AnanseSpider/Lab_v001/L_AnanseCharacterLab','native_animation':'/Script/Ananse.AnanseContactAnimInstance','clips':[c.get_path_name() for c in clips]}
report.write_text(json.dumps({'paths':paths,'reused_mesh':True,'reimported':False,'native_ik_rig_asset':None,'control_rig_blueprint':None,'animation_blueprint':None,'art_status':'existing engineering proxy; final reference-faithful art missing'},indent=2)+'\n')
