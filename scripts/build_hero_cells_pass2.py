"""Import benchmark scenery; retain original gameplay and collision anchors exactly."""
import unreal,json,os,math,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);src=R/'SourceArt/Environments/MarketSanctuary/HeroCells_v002';contract=json.loads((src/'source-status.json').read_text());dest='/Game/Ananse/Environments/HeroCells_v002'
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
 breakup=next(a for a in import_file(src/'SurfaceBreakup.png',dest+'/Surface')if isinstance(a,unreal.Texture2D));breakup.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_DEFAULT);breakup.set_editor_property('srgb',False);save(breakup)
 normal=next(a for a in import_file(src/'SurfaceNormal.png',dest+'/Surface')if isinstance(a,unreal.Texture2D));normal.set_editor_property('srgb',False);normal.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP);save(normal)
 for row in contract['surfaces']:
  name=row['name'];textures=[a for a in import_file(src/row['texture'],dest+'/Surface')if isinstance(a,unreal.Texture2D)];assert len(textures)==1
  m=tools.create_asset('M_'+name,dest+'/Surface',unreal.Material,unreal.MaterialFactoryNew());assert m
  tex=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionTextureSample,-400,0);tex.set_editor_property('texture',textures[0]);unreal.MaterialEditingLibrary.connect_material_property(tex,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
  for prop,value in [(unreal.MaterialProperty.MP_ROUGHNESS,row['roughness']),(unreal.MaterialProperty.MP_METALLIC,row['metallic'])]:
   c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-350,200);c.set_editor_property('r',value);unreal.MaterialEditingLibrary.connect_material_property(c,'',prop)
  if name not in ['DistantBark','DistantLeaf','HazeStone']:
   M=unreal.MaterialEditingLibrary
   mask=M.create_material_expression(m,unreal.MaterialExpressionTextureSample,-800,400);mask.set_editor_property('texture',breakup);mask.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
   world=M.create_material_expression(m,unreal.MaterialExpressionWorldPosition,-1200,400);xy=M.create_material_expression(m,unreal.MaterialExpressionComponentMask,-1050,400);xy.set_editor_property('r',True);xy.set_editor_property('g',True);xy.set_editor_property('b',False);xy.set_editor_property('a',False);M.connect_material_expressions(world,M.get_material_expression_output_names(world)[0],xy,M.get_material_expression_input_names(xy)[0])
   scale=M.create_material_expression(m,unreal.MaterialExpressionDivide,-900,400);scale.set_editor_property('const_b',350.0);M.connect_material_expressions(xy,'',scale,'A');M.connect_material_expressions(scale,'',mask,'UVs')
   factor=M.create_material_expression(m,unreal.MaterialExpressionMultiply,-650,450);factor.set_editor_property('const_b',.35);M.connect_material_expressions(mask,'R',factor,'A');bias=M.create_material_expression(m,unreal.MaterialExpressionAdd,-500,450);bias.set_editor_property('const_b',.78);M.connect_material_expressions(factor,'',bias,'A');colour=M.create_material_expression(m,unreal.MaterialExpressionMultiply,-250,0);M.connect_material_expressions(tex,'RGB',colour,'A');M.connect_material_expressions(bias,'',colour,'B');M.connect_material_property(colour,'',unreal.MaterialProperty.MP_BASE_COLOR)
   rough=M.create_material_expression(m,unreal.MaterialExpressionMultiply,-250,200);rough.set_editor_property('const_b',row['roughness']);M.connect_material_expressions(mask,'B',rough,'A');M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
   norm=M.create_material_expression(m,unreal.MaterialExpressionTextureSample,-600,-250);norm.set_editor_property('texture',normal);norm.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL);M.connect_material_property(norm,'RGB',unreal.MaterialProperty.MP_NORMAL)
  if name in ['GoldThread','ThreadDim']:
   c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-350,300);c.set_editor_property('constant',unreal.LinearColor(*((.28,.12,.015,1) if name=='GoldThread' else (.045,.018,.002,1))));unreal.MaterialEditingLibrary.connect_material_property(c,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
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
 for market,name in [(True,'L_RiverMarket_Route'),(False,'L_StoryForest_Route')]:
  path='/Game/Ananse/Maps/EnvironmentRoute_v002/'+name;assert levels.load_level(path);original=list(actors.get_all_level_actors());before={a.get_name():snapshot(a)for a in original};hidden=[];placements=[]
  def hide(a):
   a.set_actor_hidden_in_game(True)
   for c in a.get_components_by_class(unreal.PrimitiveComponent):c.set_visibility(False,False)
   hidden.append(a.get_actor_label())
  def override(c):
   m=c.get_editor_property('static_mesh')
   if m:
    for i in range(len(m.get_editor_property('static_materials'))):
     mat=m.get_material(i);key=mat.get_name().removeprefix('M_')if mat else ''
     if key in mats:c.set_material(i,mats[key])
  for a in original:
   label=a.get_actor_label()
   if isinstance(a,unreal.AnanseEnvironmentCluster):
    c=a.get_editor_property('instances')
    if label.startswith('Hero cell ')or label in ['Route MarketStall','Route PotterySet']:override(c)
    if market and label in ['Route RiverSurface','Hero cell RiverWater','Hero cell Boat']:hide(a)
    if not market and label in ['Hero cell HeroTree','Hero cell Understory','Hero cell RockCluster','Route SanctuaryRock','Route SanctuaryStream','Hero cell StreamBank','Hero cell RiverWater']:hide(a)
    if market and label=='Hero cell Frontage'and c.get_instance_count()==10:
     for i,(x,y,yaw)in enumerate([(x,y,yaw)for y,yaw in [(-1500,0),(1500,180)]for x in [-1700,-1000,-300,400,1100]]):
      scale=[1.02,1.13,1.0,1.2,1.07][i%5];c.update_instance_transform(i,unreal.Transform(unreal.Vector(x,y,0),unreal.Rotator(pitch=0,yaw=yaw,roll=0),unreal.Vector([.98,1.02,.96,1.05,1][i%5],1,scale)),False,True,True)
  def add(key,places,scale=(1,1,1),mesh=None):
   a=actors.spawn_actor_from_class(unreal.AnanseEnvironmentCluster,unreal.Vector());a.set_actor_label('Pass2 '+key);c=a.get_editor_property('instances');c.set_static_mesh(mesh or meshes[key]);c.set_mobility(unreal.ComponentMobility.STATIC);c.set_collision_profile_name('NoCollision');override(c)
   for x,y,z,yaw in places:c.add_instance(unreal.Transform(unreal.Vector(x,y,z),unreal.Rotator(pitch=0,yaw=yaw,roll=0),unreal.Vector(*scale)))
   placements.append({'key':key,'positions_cm':places,'scale':scale,'mesh':c.get_editor_property('static_mesh').get_path_name(),'collision':'NoCollision'})
  if market:
   add('RiverQuay',[(2490,-750,0,0),(2490,750,0,0)])
   add('RiverBend',[(3600,0,-35,0)])
   add('FarBank',[(4800,-1300,0,0),(4800,1300,0,0)])
   add('SettlementDepth',[(5350,-1800,0,90),(5500,0,0,90),(5300,1800,0,90)],(1.4,1,1.5))
   add('SettlementDepth',[(6500,-1500,0,90),(6600,1300,0,90)],(1.6,1,2.0))
   add('CargoBoat',[(2900,-500,-45,85),(3200,650,-45,105)])
   add('VendorCluster',[(-1050,-650,0,0),(-650,1000,0,180),(150,-1000,0,15),(-1500,250,0,80)])
   add('FacadeWing',[(-1350,-1340,0,0),(-650,1340,0,180),(700,1450,0,180)],(1,1,1))
   add('ArchiveThreshold',[(650,390,0,0)])
  else:
   add('SentinelTree',[(760,0,0,35)])
   add('LeaningTree',[(-760,0,0,190)])
   add('ForkedTree',[(380,658,0,90)])
   oldtree=unreal.load_asset('/Game/Ananse/Environments/HeroCells_v001/HeroTree/HeroTree');add('RemainingGrove',[(760*math.cos(i*math.tau/12),760*math.sin(i*math.tau/12),0,i*30)for i in range(12)if i not in [0,2,6]],mesh=oldtree)
   add('ForestDepth',[(1700*math.cos(i*math.tau/12),1700*math.sin(i*math.tau/12),-50,i*30+90)for i in range(12)])
   add('ForestDepth',[(2700*math.cos(i*math.tau/16),2700*math.sin(i*math.tau/16),-100,i*22.5+90)for i in range(16)],(1.4,1,1.3))
   add('GroveFloor',[(-650,350,0,35),(-450,650,0,80),(200,650,0,15),(650,250,0,150),(650,-450,0,40),(100,-350,0,-20),(-650,-450,0,80)],(1.2,1.2,1))
   add('FallenWood',[(-480,530,0,25),(640,350,0,75),(-600,-430,0,15)])
   add('SanctuaryFrame',[(-120,430,0,180)])
   add('StreamReach',[(350,-200,0,0)])
   add('SilkHierarchy',[(350,-200,0,0)])
  assert before=={a.get_name():snapshot(a)for a in original},'Original transform/collision/action changed';assert levels.save_current_level();result['maps'].append({'path':path,'anchors_unchanged':True,'snapshot':before,'hidden_visuals':hidden,'placements':placements});original=[];a=c=None
 result['status']='saved_pending_reopen_visual_and_packaged_checks';result['lighting']='Existing fallback unmodified; no fog/light additions; atmospheric perspective uses opaque distant geometry/palette.'
except Exception:result['exception']=traceback.format_exc();raise
finally:(out/'pass2-native.json').write_text(json.dumps(result,indent=2)+'\n')
