"""Repair explicit material pin/sampler bindings against installed editor APIs."""
import unreal,json,os
from pathlib import Path
M=unreal.MaterialEditingLibrary;rows=[];root='/Game/Ananse/Environments/HeroCells_v002/Surface'
breakup=unreal.load_asset(root+'/SurfaceBreakup');breakup.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_DEFAULT);breakup.set_editor_property('srgb',False);assert unreal.EditorAssetLibrary.save_loaded_asset(breakup)
for path in unreal.EditorAssetLibrary.list_assets(root,recursive=False,include_folder=False):
 m=unreal.load_asset(path)
 if not isinstance(m,unreal.Material):continue
 pending=[M.get_material_property_input_node(m,p)for p in [unreal.MaterialProperty.MP_BASE_COLOR,unreal.MaterialProperty.MP_ROUGHNESS,unreal.MaterialProperty.MP_NORMAL,unreal.MaterialProperty.MP_EMISSIVE_COLOR]];seen=set();fixed=[]
 while pending:
  node=pending.pop()
  if not node or node.get_path_name()in seen:continue
  seen.add(node.get_path_name());pending.extend(M.get_inputs_for_material_expression(m,node))
  if isinstance(node,unreal.MaterialExpressionComponentMask):
   world=M.create_material_expression(m,unreal.MaterialExpressionWorldPosition,-1200,400);outs=M.get_material_expression_output_names(world);ins=M.get_material_expression_input_names(node);assert M.connect_material_expressions(world,outs[0]if outs else'',node,ins[0]if ins else'');fixed.append({'world_outputs':list(outs),'mask_inputs':list(ins)})
  if isinstance(node,unreal.MaterialExpressionTextureSample):
   tex=node.get_editor_property('texture')
   if tex and tex.get_name()=='SurfaceBreakup':node.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
 M.recompile_material(m);assert unreal.EditorAssetLibrary.save_loaded_asset(m);rows.append({'material':m.get_path_name(),'pin_fixes':fixed})
Path(os.environ['ANANSE_EVIDENCE_DIR']).write_text(json.dumps(rows,indent=2))
