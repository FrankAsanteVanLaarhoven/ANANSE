"""Hide debug render geometry, retain collision/actions, apply coherent plaster in new maps."""
import unreal,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);tools=unreal.AssetToolsHelpers.get_asset_tools();dest='/Game/Ananse/Environments/RouteSurface_v003';task=unreal.AssetImportTask()
for k,v in dict(filename=str(R/'SourceArt/Environments/MarketSanctuary/Refinement_v002/WarmPlaster_Albedo.png'),destination_path=dest,automated=True,save=True,replace_existing=False).items():task.set_editor_property(k,v)
tools.import_asset_tasks([task]);tex=next(unreal.load_asset(p)for p in task.get_editor_property('imported_object_paths')if isinstance(unreal.load_asset(p),unreal.Texture2D));mat=tools.create_asset('M_OchrePlaster',dest,unreal.Material,unreal.MaterialFactoryNew());mat.set_editor_property('used_with_instanced_static_meshes',True)
e=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-300,0);e.set_editor_property('texture',tex);unreal.MaterialEditingLibrary.connect_material_property(e,'',unreal.MaterialProperty.MP_BASE_COLOR);rough=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,150);rough.set_editor_property('r',.94);unreal.MaterialEditingLibrary.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);unreal.MaterialEditingLibrary.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
# Only new mesh asset slots may be changed; legacy wall materials use per-map overrides.
mesh=unreal.load_asset('/Game/Ananse/Environments/Route_v001/MarketFacade/MarketFacade')
for i,slot in enumerate(mesh.get_editor_property('static_materials')):
 old=mesh.get_material(i)
 if old and 'WarmPlaster'in old.get_name():mesh.set_material(i,mat)
assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[]
for name in ['L_RiverMarket_Route','L_StoryForest_Route']:
 path='/Game/Ananse/Maps/EnvironmentRoute_v002/'+name;assert levels.load_level(path);row={'map':path,'debug_meshes_hidden':[],'wall_overrides':[]}
 for a in actors.get_all_level_actors():
  if isinstance(a,unreal.AnanseInteractable):
   root=a.get_editor_property('mesh');collision=root.get_collision_enabled();root.set_visibility(False,False);assert root.get_collision_enabled()==collision;a.get_editor_property('label').set_visibility(False,False);row['debug_meshes_hidden'].append({'action':str(a.get_editor_property('action')),'collision':str(collision),'note':'Rendered debug cube and floating label hidden; authored visual, interaction root and existing HUD prompt retained. CharacterVisual untouched.'})
  if isinstance(a,unreal.StaticMeshActor)and a.get_actor_label().startswith('Authored replacement Wall_'):
   c=a.static_mesh_component
   for i in range(c.get_num_materials()):
    old=c.get_material(i)
    if old and 'WarmPlaster'in old.get_name():c.set_material(i,mat);row['wall_overrides'].append({'label':a.get_actor_label(),'slot':i})
 assert levels.save_current_level();rows.append(row);a=root=c=None
(out/'presentation.json').write_text(json.dumps(rows,indent=2)+'\n')
