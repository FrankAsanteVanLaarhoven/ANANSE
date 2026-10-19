"""Explicit instance usage on new environment materials; legacy surfaces cloned."""
import unreal,json,os
from pathlib import Path
out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);tools=unreal.AssetToolsHelpers.get_asset_tools();sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);rows=[];clones={}
for prefix in ['/Game/Ananse/Environments/Route_v001','/Game/Ananse/Environments/Crossing_v001']:
 for path in unreal.EditorAssetLibrary.list_assets(prefix,recursive=True,include_folder=False):
  mesh=unreal.load_asset(path)
  if not isinstance(mesh,unreal.StaticMesh):continue
  for i,slot in enumerate(mesh.get_editor_property('static_materials')):
   m=mesh.get_material(i);old=m.get_path_name()if m else None
   if not isinstance(m,unreal.Material):continue
   if not m.get_path_name().startswith(('/Game/Ananse/Environments/Route','/Game/Ananse/Environments/Crossing')):
    if old not in clones:clones[old]=tools.duplicate_asset(m.get_name(),'/Game/Ananse/Environments/RouteSurface_v002',m)
    m=clones[old];assert m;mesh.set_material(i,m)
   m.set_editor_property('used_with_instanced_static_meshes',True);unreal.MaterialEditingLibrary.recompile_material(m);assert unreal.EditorAssetLibrary.save_loaded_asset(m);rows.append({'mesh':mesh.get_path_name(),'slot':i,'prior':old,'material':m.get_path_name(),'instanced_usage':m.get_editor_property('used_with_instanced_static_meshes'),'two_sided':m.get_editor_property('two_sided')})
  assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
(out/'materials.json').write_text(json.dumps(rows,indent=2)+'\n')
