"""Final art bindings after direct native fixed-camera inspection."""
import unreal,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];M=unreal.MaterialEditingLibrary;dest='/Game/Ananse/Environments/HeroCells_v004';tools=unreal.AssetToolsHelpers.get_asset_tools()
t=unreal.AssetImportTask()
for k,v in dict(filename=str(R/'SourceArt/Environments/MarketSanctuary/HeroCells_v004/WaterFlowNormal.png'),destination_path=dest+'/Surface',automated=True,replace_existing=False,save=True,async_=False).items():t.set_editor_property(k,v)
tools.import_asset_tasks([t]);normal=next(unreal.load_asset(p)for p in t.get_editor_property('imported_object_paths')if isinstance(unreal.load_asset(p),unreal.Texture2D));normal.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP);normal.set_editor_property('srgb',False);assert unreal.EditorAssetLibrary.save_loaded_asset(normal)
m=unreal.load_asset(dest+'/Surface/M_Water');seen=set()
def visit(node):
 if not node or node.get_path_name()in seen:return
 seen.add(node.get_path_name())
 if isinstance(node,unreal.MaterialExpressionTextureSample)and node.get_editor_property('sampler_type')==unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL:node.set_editor_property('texture',normal)
 if isinstance(node,unreal.MaterialExpressionConstant3Vector):
  col=node.get_editor_property('constant')
  if abs(col.r-.28)<.001 and abs(col.g-.28)<.001:node.set_editor_property('constant',unreal.LinearColor(.6,.6,1,1))
 for n in M.get_inputs_for_material_expression(m,node):visit(n)
visit(M.get_material_property_input_node(m,unreal.MaterialProperty.MP_NORMAL));M.recompile_material(m);assert unreal.EditorAssetLibrary.save_loaded_asset(m)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);d=[];cache={}
for market,name in [(True,'L_RiverMarket_Route'),(False,'L_StoryForest_Route')]:
 assert levels.load_level('/Game/Ananse/Maps/EnvironmentRoute_v002/'+name)
 for a in actors.get_all_level_actors():
  if not market and isinstance(a,unreal.DirectionalLight):
   c=a.get_component_by_class(unreal.DirectionalLightComponent);c.set_intensity(4.0);c.set_light_color(unreal.LinearColor(.82,.9,1,1))
  if not isinstance(a,unreal.AnanseEnvironmentCluster):continue
  c=a.get_editor_property('instances');label=a.get_actor_label()
  if market and label=='Pass4 RiverReach':
   c.clear_instances();c.add_instance(unreal.Transform(unreal.Vector(3630,3000,-35),unreal.Rotator(pitch=0,yaw=90,roll=0),unreal.Vector(1,1,1)))
  if market and label.startswith('Pass3 SkylineQuarter'):
   mesh=c.get_editor_property('static_mesh')
   for i in range(c.get_num_materials()):
    old=mesh.get_material(i);key=old.get_path_name()
    if key not in cache:
     mat=unreal.EditorAssetLibrary.duplicate_asset(key,dest+'/Surface/M_Perspective_'+old.get_name());assert isinstance(mat,unreal.Material);node=M.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR);assert node;lerp=M.create_material_expression(mat,unreal.MaterialExpressionLinearInterpolate,200,0);lerp.set_editor_property('const_alpha',.4);assert M.connect_material_expressions(node,M.get_material_expression_output_names(node)[0],lerp,'A');col=M.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,0,300);col.set_editor_property('constant',unreal.LinearColor(.12,.18,.19,1));assert M.connect_material_expressions(col,'',lerp,'B');assert M.connect_material_property(lerp,'',unreal.MaterialProperty.MP_BASE_COLOR);M.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat);cache[key]=mat
    c.set_material(i,cache[key])
  if not market and label in ['Pass4 SanctuaryReliquary','Pass4 SanctuaryGarden']:
   yaw=34 if label.endswith('Reliquary')else 180;c.update_instance_transform(0,unreal.Transform(unreal.Vector(-120,430,0),unreal.Rotator(pitch=0,yaw=yaw,roll=0),unreal.Vector(1,1,1)),False,True,True)
 assert levels.save_current_level();d.append({'map':name,'water':'one continuous sheet over original extent; authored512px two-layer moving normal, opaque','perspective_materials':len(cache),'forest':'new visual marker yaw34/garden yaw180; existing directional4.0/cool-white; no new lights/exposure change'})
Path(os.environ['ANANSE_EVIDENCE_DIR']).write_text(json.dumps(d,indent=2))
