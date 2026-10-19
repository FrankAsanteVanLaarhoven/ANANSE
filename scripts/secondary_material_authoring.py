"""Author a bounded material variant while preserving the source graph."""
import unreal
def build_motion_material(old,folder,name):
 M=unreal.MaterialEditingLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools()
 key=old.get_path_name()
 path=folder+'/'+name;# Resume only this task-owned revision after a preserved failed import.
 if unreal.EditorAssetLibrary.does_asset_exist(path):
  mat=unreal.load_asset(path);return mat
 mat=tools.duplicate_asset(name,folder,old);assert isinstance(mat,unreal.Material),key
 custom=M.create_material_expression(mat,unreal.MaterialExpressionCustom,0,600);custom.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
 custom.set_editor_property('description','Bounded visual wind and water, anchored by authored RGBA masks; centimetres')
 custom.set_editor_property('code','''float slow=sin(T*1.4+P.x*.0017+P.y*.0011);
float fast=sin(T*5.3+P.x*.018+P.y*.011);
float gust=.7+.3*sin(T*.37+P.x*.0003);
float sway=(C.r*2.0*slow+C.g*.7*fast+A*1.2*slow)*gust;
return float3(sway,sway*.38,C.b*.6*(sin(T*1.8+P.x*.022+P.y*.014)+.25*sin(T*3.1+P.y*.04))+C.g*.22*fast);''')
 inputs=[]
 for name,cls,output in [('C',unreal.MaterialExpressionVertexColor,''),('T',unreal.MaterialExpressionTime,''),('P',unreal.MaterialExpressionWorldPosition,''),('A',unreal.MaterialExpressionVertexColor,'A')]:
  i=unreal.CustomInput();i.set_editor_property('input_name',name);inputs.append(i)
 custom.set_editor_property('inputs',inputs)
 for name,cls,output in [('C',unreal.MaterialExpressionVertexColor,''),('T',unreal.MaterialExpressionTime,''),('P',unreal.MaterialExpressionWorldPosition,''),('A',unreal.MaterialExpressionVertexColor,'A')]:
  node=M.create_material_expression(mat,cls,-300,600);assert M.connect_material_expressions(node,output,custom,name),(name,output)
 assert M.connect_material_property(custom,'',unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
 M.set_material_usage(mat,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);M.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat);return mat
