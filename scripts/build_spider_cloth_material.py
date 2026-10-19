"""Create a new, skeletal-compatible proxy cloth material; preserve older materials."""
import json
import os
from pathlib import Path
import unreal

DEST = '/Game/Production/Characters/SpiderLook_v001'
NAME = 'M_ProxyClothVariant'
path = DEST + '/' + NAME
report = Path(os.environ['ANANSE_EVIDENCE_DIR']) / 'cloth-material.json'
if report.exists() or unreal.EditorAssetLibrary.does_asset_exist(path):
    raise RuntimeError('Existing material/report preserved. Use a reviewed new version instead.')
material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(NAME, DEST, unreal.Material, unreal.MaterialFactoryNew())
if not material:
    raise RuntimeError('Material creation failed.')
colour = unreal.MaterialEditingLibrary.create_material_expression(material, unreal.MaterialExpressionVectorParameter, -300, 0)
colour.set_editor_property('parameter_name', 'ClothColor')
colour.set_editor_property('default_value', unreal.LinearColor(.417885, .155926, .036889, 1))
unreal.MaterialEditingLibrary.connect_material_property(colour, '', unreal.MaterialProperty.MP_BASE_COLOR)
roughness = unreal.MaterialEditingLibrary.create_material_expression(material, unreal.MaterialExpressionConstant, -300, 150)
roughness.set_editor_property('r', .85)
unreal.MaterialEditingLibrary.connect_material_property(roughness, '', unreal.MaterialProperty.MP_ROUGHNESS)
unreal.MaterialEditingLibrary.set_material_usage(material, unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
unreal.MaterialEditingLibrary.recompile_material(material)
if not material.get_editor_property('used_with_skeletal_mesh'):
    raise RuntimeError('Actual skeletal usage flag was not set.')
node = unreal.MaterialEditingLibrary.get_material_property_input_node(material, unreal.MaterialProperty.MP_BASE_COLOR)
if node != colour or str(node.get_editor_property('parameter_name')) != 'ClothColor':
    raise RuntimeError('Actual base-colour shader input is not the published parameter.')
if not unreal.EditorAssetLibrary.save_loaded_asset(material):
    raise RuntimeError('Material save failed.')
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(json.dumps({'asset': material.get_path_name(), 'skeletal_usage': True,
                              'base_colour_parameter': 'ClothColor',
                              'scope': 'Flat proxy cosmetic material; no final textile/cloth-simulation approval'}, indent=2) + '\n')
