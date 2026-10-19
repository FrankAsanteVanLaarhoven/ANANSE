"""Opaque two-sided cloth/leaf surfaces, original local 512px woven map."""
import unreal,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);tools=unreal.AssetToolsHelpers.get_asset_tools();dest='/Game/Ananse/Environments/RouteSurface_v001';rows=[]
for name,color,rough in [('Leaf',(.055,.16,.038),.94),('Indigo',(.025,.06,.14),.9)]:
 m=tools.create_asset('M_'+name,dest,unreal.Material,unreal.MaterialFactoryNew());assert m;m.set_editor_property('two_sided',True)
 if name=='Indigo':
  task=unreal.AssetImportTask()
  for k,v in dict(filename=str(R/'SourceArt/Environments/MarketSanctuary/Surface_v003/IndigoWeave.png'),destination_path=dest,automated=True,save=True,replace_existing=False).items():task.set_editor_property(k,v)
  tools.import_asset_tasks([task]);tex=next(unreal.load_asset(p)for p in task.get_editor_property('imported_object_paths')if isinstance(unreal.load_asset(p),unreal.Texture2D));e=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionTextureSample,-300,0);e.set_editor_property('texture',tex)
 else:e=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-300,0);e.set_editor_property('constant',unreal.LinearColor(*color,1))
 unreal.MaterialEditingLibrary.connect_material_property(e,'',unreal.MaterialProperty.MP_BASE_COLOR);r=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-300,150);r.set_editor_property('r',rough);unreal.MaterialEditingLibrary.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS);unreal.MaterialEditingLibrary.recompile_material(m);assert unreal.EditorAssetLibrary.save_loaded_asset(m)
 for meshname in (['SanctuaryTree','ForestFern']if name=='Leaf'else['MarketStall']):
  mesh=unreal.load_asset('/Game/Ananse/Environments/Route_v001/'+meshname+'/'+meshname)
  for i,slot in enumerate(mesh.get_editor_property('static_materials')):
   old=mesh.get_material(i)
   if old and old.get_name()==name:
    row={'mesh':mesh.get_path_name(),'slot':i,'old':old.get_path_name(),'old_class':old.get_class().get_name(),'new':m.get_path_name(),'two_sided':True};rows.append(row);mesh.set_material(i,m)
  assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
(out/'materials.json').write_text(json.dumps(rows,indent=2)+'\n')
