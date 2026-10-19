"""Explicitly cooked inspection material; does not modify the original mesh."""
import json,os
from pathlib import Path
import unreal
path='/Game/Production/Characters/SpiderSelection_v001';name='M_LabWireframe'
report=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'wireframe-material.json'
if report.exists() or unreal.EditorAssetLibrary.does_asset_exist(path+'/'+name):raise RuntimeError('Existing asset/report preserved')
m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,path,unreal.Material,unreal.MaterialFactoryNew())
m.set_editor_property('wireframe',True);m.set_editor_property('two_sided',True);m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
unreal.MaterialEditingLibrary.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-200,0);c.set_editor_property('constant',unreal.LinearColor(.9,.65,.15))
unreal.MaterialEditingLibrary.connect_material_property(c,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
unreal.MaterialEditingLibrary.recompile_material(m)
if not m.get_editor_property('wireframe') or not unreal.EditorAssetLibrary.save_loaded_asset(m):raise RuntimeError('Wireframe material not saved')
report.write_text(json.dumps({'asset':m.get_path_name(),'wireframe':True,'skeletal_usage':True,'scope':'Actual triangle-edge inspection shader; not illustrative topology or production art'},indent=2)+'\n')
