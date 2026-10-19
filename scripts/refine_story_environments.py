"""Refine only new draft environment maps: lit floors, static mesh collisions and cameras."""
import unreal,json,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=True)
if(out/'result.json').exists():raise RuntimeError('Preserve earlier evidence')
r=json.loads((ROOT/'.local/verification/story-cast-20261015/environment-native/environments-native.json').read_text());backup=out/'before-refinement';shutil.copytree(ROOT/'Unreal/Content/Ananse/Maps/Story_v001',backup)
tools=unreal.AssetToolsHelpers.get_asset_tools();dest='/Game/Ananse/Environments/Story_v001/Surface';mats={}
for name,color in [('MarketEarth',(.24,.12,.045)),('ForestEarth',(.052,.065,.027))]:
 path=dest+'/M_'+name;assert not unreal.EditorAssetLibrary.does_asset_exist(path);m=tools.create_asset('M_'+name,dest,unreal.Material,unreal.MaterialFactoryNew());c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-300,0);c.set_editor_property('constant',unreal.LinearColor(*color,1));unreal.MaterialEditingLibrary.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR);rough=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-300,100);rough.set_editor_property('r',.92);unreal.MaterialEditingLibrary.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);unreal.MaterialEditingLibrary.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m);mats[name]=m
collisions=[]
for key,path in r['meshes'].items():
 if key not in ['MarketArchitecture','MarketStalls','RiverDock','SanctuaryTrees','SanctuaryGround']:continue
 mesh=unreal.load_asset(path);body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh);collisions.append(path)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for path in r['maps']:
 assert levels.load_level(path)
 for a in actors.get_all_level_actors():
  if isinstance(a,unreal.StaticMeshActor):
   c=a.static_mesh_component
   if 'Stable gameplay floor' in a.get_actor_label():c.set_material(0,mats['MarketEarth' if 'Market' in path else 'ForestEarth'])
   elif c.get_editor_property('static_mesh') and c.get_editor_property('static_mesh').get_path_name()in collisions:c.set_collision_profile_name('BlockAll')
 assert levels.save_current_level()
(out/'result.json').write_text(json.dumps({'status':'saved_pending_render_and_movement_check','static_complex_collision':collisions,'maps':r['maps'],'creative_approved':False,'mobile_qualified':False,'original_campaign_maps_changed':False},indent=2)+'\n')
