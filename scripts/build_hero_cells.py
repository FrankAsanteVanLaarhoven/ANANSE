"""Import benchmark scenery; retain original gameplay and collision anchors exactly."""
import unreal,json,os,math,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);src=R/'SourceArt/Environments/MarketSanctuary/HeroCells_v001';contract=json.loads((src/'source-status.json').read_text());dest='/Game/Ananse/Environments/HeroCells_v001'
tools=unreal.AssetToolsHelpers.get_asset_tools();sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);meshes={};mats={};result={'status':'failed','meshes':{},'maps':[],'creative':'REVIEW_REQUIRED','baked_lighting':'BLOCKED','mobile':'UNQUALIFIED'}
def save(a):assert unreal.EditorAssetLibrary.save_loaded_asset(a)
def import_file(file,folder):
 t=unreal.AssetImportTask()
 for k,v in dict(filename=str(file),destination_path=folder,automated=True,replace_existing=False,save=True,async_=False).items():t.set_editor_property(k,v)
 if file.suffix=='.glb':
  pipeline=unreal.InterchangeGenericAssetsPipeline();pipeline.set_editor_property('import_offset_rotation',unreal.Rotator());opt=unreal.InterchangePipelineStackOverride();opt.set_editor_property('override_pipelines',[unreal.SoftObjectPath(pipeline.get_path_name())]);t.set_editor_property('options',opt)
 tools.import_asset_tasks([t]);return[unreal.load_asset(p)for p in t.get_editor_property('imported_object_paths')]
def snapshot(a):
 p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();d={'transform':[p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z],'collision_enabled':a.get_actor_enable_collision()}
 if isinstance(a,unreal.StaticMeshActor):d['profile']=str(a.static_mesh_component.get_collision_profile_name());d['component_collision']=str(a.static_mesh_component.get_collision_enabled())
 if isinstance(a,unreal.AnanseInteractable):d['action']=str(a.get_editor_property('action'));d['identity']=str(a.get_editor_property('character_id'))
 return d
try:
 for row in contract['surfaces']:
  name=row['name'];textures=[a for a in import_file(src/row['texture'],dest+'/Surface')if isinstance(a,unreal.Texture2D)];assert len(textures)==1
  m=tools.create_asset('M_'+name,dest+'/Surface',unreal.Material,unreal.MaterialFactoryNew());assert m
  tex=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionTextureSample,-400,0);tex.set_editor_property('texture',textures[0]);unreal.MaterialEditingLibrary.connect_material_property(tex,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
  for prop,value in [(unreal.MaterialProperty.MP_ROUGHNESS,row['roughness']),(unreal.MaterialProperty.MP_METALLIC,row['metallic'])]:
   c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-350,200);c.set_editor_property('r',value);unreal.MaterialEditingLibrary.connect_material_property(c,'',prop)
  if name=='GoldThread':
   c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-350,300);c.set_editor_property('constant',unreal.LinearColor(.28,.12,.015,1));unreal.MaterialEditingLibrary.connect_material_property(c,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
  m.set_editor_property('two_sided',name in ['Leaf','Indigo','Jade']);unreal.MaterialEditingLibrary.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);unreal.MaterialEditingLibrary.recompile_material(m);save(m);mats[name]=m
 for row in contract['exports']:
  name=row['name'];found=[a for a in import_file(src/row['file'],dest+'/'+name)if isinstance(a,unreal.StaticMesh)];assert len(found)==1;mesh=meshes[name]=found[0]
  slots=mesh.get_editor_property('static_materials')
  for i,slot in enumerate(slots):
   old=mesh.get_material(i);mn=old.get_name() if old else '';match=next((n for n in mats if mn==n or mn.endswith('_'+n)),None);assert match,(name,mn);mesh.set_material(i,mats[match])
  opts=unreal.StaticMeshReductionOptions();opts.set_editor_property('auto_compute_lod_screen_size',False);settings=[]
  for percent,screen in [(1.,1.),(.5,.4),(.22,.15)]:
   s=unreal.StaticMeshReductionSettings();s.set_editor_property('percent_triangles',percent);s.set_editor_property('screen_size',screen);settings.append(s)
  opts.set_editor_property('reduction_settings',settings);sm.set_lods(mesh,opts);sm.set_generate_lightmap_uv(mesh,True);mesh.set_editor_property('light_map_resolution',128);n=mesh.get_editor_property('nanite_settings');n.set_editor_property('enabled',False);mesh.set_editor_property('nanite_settings',n);save(mesh)
  result['meshes'][name]={'path':mesh.get_path_name(),'lod_vertices':[sm.get_number_verts(mesh,i)for i in range(3)],'lod_triangles':[sum(mesh.get_num_triangles(i) for _ in [0])for i in range(3)],'material_slots':len(slots),'source_triangles':row['triangles']}
 crossing=unreal.EditorAssetLibrary.duplicate_asset(meshes['WebLace'].get_path_name(),dest+'/GoldenWebCrossing/GoldenWebCrossing');assert crossing;save(crossing)
 result['crossing_visual_binding']=crossing.get_path_name()
 for market,name in [(True,'L_RiverMarket_Route'),(False,'L_StoryForest_Route')]:
  path='/Game/Ananse/Maps/EnvironmentRoute_v002/'+name;assert levels.load_level(path);original=list(actors.get_all_level_actors());before={a.get_name():snapshot(a)for a in original};hidden=[];placements=[]
  def hide(a):
   a.set_actor_hidden_in_game(True)
   for c in a.get_components_by_class(unreal.PrimitiveComponent):c.set_visibility(False,False)
   hidden.append(a.get_actor_label())
  for a in original:
   label=a.get_actor_label()
   if market and isinstance(a,unreal.StaticMeshActor)and any('Wall_'+d+'_boundary' in label for d in ['East','West','North','South']):hide(a)
   if not market and label in ['Route SanctuaryTree','Route ForestFern']:hide(a)
   if not market and label=='Route GoldenWebCrossing':a.get_editor_property('instances').set_static_mesh(crossing)
  def instances(key,places,scale=(1,1,1)):
   a=actors.spawn_actor_from_class(unreal.AnanseEnvironmentCluster,unreal.Vector());a.set_actor_label('Hero cell '+key);c=a.get_editor_property('instances');c.set_static_mesh(meshes[key]);c.set_mobility(unreal.ComponentMobility.STATIC);c.set_collision_profile_name('NoCollision')
   for x,y,z,yaw in places:c.add_instance(unreal.Transform(unreal.Vector(x,y,z),unreal.Rotator(pitch=0,yaw=yaw,roll=0),unreal.Vector(*scale)))
   placements.append({'module':key,'instances':len(places),'transforms_cm':places,'scale':scale,'collision':'NoCollision'})
  if market:
   instances('Frontage',[(x,y,0,yaw)for y,yaw in [(-1500,0),(1500,180)]for x in [-1700,-1000,-300,400,1100]])
   instances('ArchivePortal',[(650,390,0,0)])
   instances('MarketDressing',[(-1100,-650,0,0),(-820,-650,0,0),(-250,-650,0,10),(-100,940,0,180),(370,1000,0,180),(-1700,300,0,90)])
   instances('GroundTreatment',[(x,y,-2.5,yaw)for x,y,yaw in [(-600,-300,0),(-100,-200,0),(400,200,0),(850,250,0),(-1200,-400,90)]])
   instances('CanopySwag',[(-1100,-500,0,0),(-350,-500,0,0),(650,390,40,0)])
   instances('Waterfront',[(2550,y,-5,90)for y in [-650,0,650]])
   instances('Boat',[(2850,-400,-55,90),(3050,520,-55,75)])
   instances('RiverWater',[(3000,0,-30,0)],(1.4,2.5,1))
   # Outside retained west/north collision boundaries: town backdrop, never new playable area.
   instances('Frontage',[(x,2100,0,180)for x in [-1900,-1200,-500,200,900]],(1.1,1,1.2))
  else:
   instances('HeroTree',[(760*math.cos(i*math.tau/12),760*math.sin(i*math.tau/12),0,i*30)for i in range(12)])
   instances('HeroTree',[(1400*math.cos(i*math.tau/18),1400*math.sin(i*math.tau/18),-50,i*20)for i in range(18)],(1.25,1.25,1.25))
   instances('Understory',[(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),0,i*27)for r,n in [(600,27),(920,32),(1200,36)]for i in range(n)])
   instances('RockCluster',[(520*math.cos(i*math.tau/11),520*math.sin(i*math.tau/11),0,i*40)for i in range(11)])
   instances('SanctuaryMarker',[(-120,430,0,0)])
   instances('StreamBank',[(350,-200,-8,0)])
   instances('RiverWater',[(350,-200,-3,0)],(.9,.09,.3))
  after={a.get_name():snapshot(a)for a in original};assert before==after,'Protected anchor/collision changed'
  assert levels.save_current_level();result['maps'].append({'path':path,'protected_anchors_unchanged':True,'anchor_snapshot':before,'hidden_visuals_only':hidden,'placements':placements})
  original=[];a=c=None
 result['status']='saved_pending_reopen_render_and_package';result['light_policy']='Existing bounded fallback unchanged. No light edits; bake remains BLOCKED.'
except Exception:result['exception']=traceback.format_exc();raise
finally:(out/'hero-cells.json').write_text(json.dumps(result,indent=2)+'\n')
