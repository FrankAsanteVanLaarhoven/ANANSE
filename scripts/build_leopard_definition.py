"""Create a typed lab-only definition from actual reopened native assets."""
import json,os
from pathlib import Path
import unreal
root=Path(__file__).resolve().parents[1];report=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'leopard-definition.json'
dest='/Game/Ananse/Characters/OseboLeopard/Data'
if report.exists() or unreal.EditorAssetLibrary.does_asset_exist(dest+'/DA_OseboLeopard'):raise RuntimeError('Preserve previous definition')
source=json.loads((root/'.local/verification/osebo-family-20261015/native-import-v002/leopard-import.json').read_text())
cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Ananse/Characters/OseboLeopard/Runtime_v001/BP_OseboLeopard')
cdo=unreal.get_default_object(cls)
factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.AnanseCharacterDefinition)
da=unreal.AssetToolsHelpers.get_asset_tools().create_asset('DA_OseboLeopard',dest,unreal.AnanseCharacterDefinition,factory)
for key,value in dict(design_id='osebo-leopard-v1',character_identity='osebo',skeleton_key='osebo-feline-biped-v001',revision=1,
    engineering_fixture=True,pawn_class=cls,mesh=cdo.get_editor_property('leopard_mesh'),clips=cdo.get_editor_property('leopard_clips')).items():da.set_editor_property(key,value)
assert unreal.EditorAssetLibrary.save_loaded_asset(da)
report.write_text(json.dumps(dict(path=da.get_path_name(),native_class=da.get_class().get_name(),
    lab_only=True,campaign_mapping_approved=False,creative_approved=False,
    full_character_gate_closed=False,mesh=source['mesh']),indent=2)+'\n')
