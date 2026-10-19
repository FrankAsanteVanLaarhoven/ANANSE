"""Authored parameter material for a bounded visual-publication revision."""
import json,os
from pathlib import Path
import unreal
out=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'cosmetic-material.json'
dest='/Game/Ananse/Characters/OseboLeopard/Presentation_v002';name='M_LeopardCosmetic'
if out.exists() or unreal.EditorAssetLibrary.does_asset_exist(dest+'/'+name):raise RuntimeError('Preserve existing revision')
m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,dest,unreal.Material,unreal.MaterialFactoryNew());assert m
for parameter,cls,value,property in [('BaseColour',unreal.MaterialExpressionVectorParameter,unreal.LinearColor(.18,.016,.033,1),unreal.MaterialProperty.MP_BASE_COLOR),('Roughness',unreal.MaterialExpressionScalarParameter,.84,unreal.MaterialProperty.MP_ROUGHNESS),('Metallic',unreal.MaterialExpressionScalarParameter,0.,unreal.MaterialProperty.MP_METALLIC)]:
 n=unreal.MaterialEditingLibrary.create_material_expression(m,cls,-300,0);n.set_editor_property('parameter_name',parameter);n.set_editor_property('default_value',value)
 assert unreal.MaterialEditingLibrary.connect_material_property(n,'',property)
unreal.MaterialEditingLibrary.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
unreal.MaterialEditingLibrary.recompile_material(m);assert m.get_editor_property('used_with_skeletal_mesh')
assert unreal.EditorAssetLibrary.save_loaded_asset(m)
out.write_text(json.dumps(dict(path=m.get_path_name(),role='Actual cape/accent shader parameters; no final textile or simulation approval',skeletal_usage=True),indent=2)+'\n')
