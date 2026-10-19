"""Additive route environment revision; protected gameplay and character roots retained."""
import unreal,json,os,traceback,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);report=out/'environment.json';src=R/'SourceArt/Environments/MarketSanctuary/Route_v001';contract=json.loads((src/'source-status.json').read_text());dest='/Game/Ananse/Environments/Route_v001';# Meshes imported by the preserved first attempt may be reused at their exact paths.
tools=unreal.AssetToolsHelpers.get_asset_tools();sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);meshes={};result={'status':'failed','creative_approved':False,'mobile_qualified':False,'meshes':{},'maps':[]}
try:
 for item in contract['exports']:
  name=item['name']
  if unreal.EditorAssetLibrary.does_asset_exist(dest+'/'+name+'/'+name):
   mesh=meshes[name]=unreal.load_asset(dest+'/'+name+'/'+name);b=mesh.get_bounds();result['meshes'][name]={'path':mesh.get_path_name(),'lod_vertices':[sm.get_number_verts(mesh,i)for i in range(3)],'materials':len(mesh.get_editor_property('static_materials')),'source_triangles':item['triangles'],'bounds_extent_cm':[b.box_extent.x,b.box_extent.y,b.box_extent.z],'lightmap_resolution':128};continue
  task=unreal.AssetImportTask()
  for k,v in dict(filename=str(src/item['file']),destination_path=dest+'/'+name,automated=True,replace_existing=False,save=True,async_=False).items():task.set_editor_property(k,v)
  pipeline=unreal.InterchangeGenericAssetsPipeline();pipeline.set_editor_property('import_offset_rotation',unreal.Rotator());opt=unreal.InterchangePipelineStackOverride();opt.set_editor_property('override_pipelines',[unreal.SoftObjectPath(pipeline.get_path_name())]);task.set_editor_property('options',opt);tools.import_asset_tasks([task]);found=[unreal.load_asset(p)for p in task.get_editor_property('imported_object_paths')];found=[a for a in found if isinstance(a,unreal.StaticMesh)];assert len(found)==1;mesh=meshes[name]=found[0]
  opts=unreal.StaticMeshReductionOptions();opts.set_editor_property('auto_compute_lod_screen_size',False);settings=[]
  for percent,screen in [(1.,1.),(.5,.4),(.25,.15)]:
   setting=unreal.StaticMeshReductionSettings();setting.set_editor_property('percent_triangles',percent);setting.set_editor_property('screen_size',screen);settings.append(setting)
  opts.set_editor_property('reduction_settings',settings);sm.set_lods(mesh,opts);assert sm.get_lod_count(mesh)==3;sm.set_generate_lightmap_uv(mesh,True);mesh.set_editor_property('light_map_resolution',128)
  for i in range(mesh.get_num_sections(0)):
   mat=mesh.get_material(i)
   if mat and isinstance(mat,unreal.Material):mat.set_editor_property('two_sided',name in ['MarketStall','SanctuaryTree','ForestFern']);unreal.MaterialEditingLibrary.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
  # Reuse the project's original authored textures without modifying them.
  for i in range(len(mesh.get_editor_property('static_materials'))):
   mat=mesh.get_material(i);alias='WeatheredWood'if mat and mat.get_name().endswith('Wood')else'WarmPlaster'if mat and mat.get_name().endswith('Plaster')else None
   if alias:mesh.set_material(i,unreal.load_asset('/Game/Ananse/Environments/Refinement_v002/M_'+alias))
  assert unreal.EditorAssetLibrary.save_loaded_asset(mesh);bounds=mesh.get_bounds();result['meshes'][name]={'path':mesh.get_path_name(),'lod_vertices':[sm.get_number_verts(mesh,i)for i in range(3)],'materials':len(mesh.get_editor_property('static_materials')),'source_triangles':item['triangles'],'bounds_extent_cm':[bounds.box_extent.x,bounds.box_extent.y,bounds.box_extent.z],'lightmap_resolution':128}
 # metres -> centimetres verified against the 6m facade width
 assert abs(result['meshes']['MarketFacade']['bounds_extent_cm'][0]-306)<2
 def transform(a):
  p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();return[p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]
 for market,old,new in [(True,'/Game/Ananse/Maps/Contact_v002/L_Market_AsoNegotiation','L_RiverMarket_Route'),(False,'/Game/Ananse/Maps/EpisodeAccepted_v001/L_Sanctuary_AcceptedVisuals','L_StoryForest_Route')]:
  path='/Game/Ananse/Maps/EnvironmentRoute_v002/'+new;assert levels.new_level_from_template(path,old);original=list(actors.get_all_level_actors());anchors={a.get_name():{'transform':transform(a),'action':str(a.get_editor_property('action'))if isinstance(a,unreal.AnanseInteractable)else None,'identity':str(a.get_editor_property('character_id'))if isinstance(a,unreal.AnanseInteractable)else None}for a in original};hidden=[];new_instances=[]
  for a in original:
   label=a.get_actor_label()
   if isinstance(a,unreal.StaticMeshActor)and(label in ['Authored MarketArchitecture WIP','Authored MarketStalls WIP','Authored MarketWares WIP','Authored RiverDock WIP','Authored SanctuaryTrees WIP','Authored SanctuaryGround WIP','Authored replacement SanctuaryLeaves WIP']):a.static_mesh_component.set_visibility(False,False);a.set_actor_hidden_in_game(True);hidden.append(label)
   if isinstance(a,unreal.RectLight):a.set_actor_hidden_in_game(True);a.get_component_by_class(unreal.RectLightComponent).set_visibility(False,False)
   # Existing Aso-specific light components and character components remain unchanged.
  def instances(name,places,scale=(1,1,1)):
   a=actors.spawn_actor_from_class(unreal.AnanseEnvironmentCluster,unreal.Vector());a.set_actor_label('Route '+name);c=a.get_editor_property('instances');c.set_static_mesh(meshes[name]);c.set_mobility(unreal.ComponentMobility.STATIC);c.set_collision_profile_name('NoCollision');c.set_editor_property('cast_shadow',True)
   for x,y,z,yaw in places:c.add_instance(unreal.Transform(unreal.Vector(x,y,z),unreal.Rotator(pitch=0,yaw=yaw,roll=0),unreal.Vector(*scale)))
   new_instances.append({'mesh':name,'instances':len(places),'collision':'NoCollision; original authority retained','material_slots':result['meshes'][name]['materials']});return a
  if market:
   instances('MarketFacade',[(x,y,0,yaw)for y,yaw in [(-1500,180),(1500,0)]for x in [-1700,-1000,-300,400,1100]])
   instances('MarketStall',[(x,y,0,0)for y in [-800,1050]for x in [-1050,-650,-250,150]])
   instances('PotterySet',[(x,y,105,0)for y in [-800,1050]for x in [-1050,-650,-250,150]])
   instances('DockSection',[(1880,y,0,90)for y in [-650,-350,-50]])
   instances('RiverSurface',[(2600,0,-15,0)])
  else:
   instances('SanctuaryTree',[(760*math.cos(i*math.tau/12),760*math.sin(i*math.tau/12),0,i*30)for i in range(12)])
   instances('SanctuaryRock',[(600*math.cos(i*math.tau/24),600*math.sin(i*math.tau/24),0,i*45)for i in range(24)])
   instances('ForestFern',[(650*math.cos(i*math.tau/32),650*math.sin(i*math.tau/32),0,i*45)for i in range(32)])
  # Numeric root equality: no interaction, checkpoint, character, camera or navigation anchor moves.
  for a in original:
   b=anchors[a.get_name()];assert transform(a)==b['transform']
   if isinstance(a,unreal.AnanseInteractable):assert str(a.get_editor_property('action'))==b['action']and str(a.get_editor_property('character_id'))==b['identity']
  assert levels.save_current_level();result['maps'].append({'path':path,'template':old,'anchors':anchors,'old_modules_hidden':hidden,'instances':new_instances,'original_roots_unchanged':True,'collision_policy':'All original colliders retained. Added scenery NoCollision. No trigger/checkpoint edits.'})
  a=c=None;original=[]
 result['status']='saved_pending_reopen_render_route_qualification';result['lighting']='Existing environment lighting inherited; non-mobile rect fills hidden. Baked lightmap build separately pending.'
except Exception:result['exception']=traceback.format_exc();raise
finally:report.write_text(json.dumps(result,indent=2)+'\n')
