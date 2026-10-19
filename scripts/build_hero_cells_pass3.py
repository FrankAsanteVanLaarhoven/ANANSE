"""Import benchmark scenery; retain original gameplay and collision anchors exactly."""
import unreal,json,os,math,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);src=R/'SourceArt/Environments/MarketSanctuary/HeroCells_v003';contract=json.loads((src/'source-status.json').read_text());dest='/Game/Ananse/Environments/HeroCells_v003'
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
  name=row['name'];m=unreal.EditorAssetLibrary.duplicate_asset('/Game/Ananse/Environments/HeroCells_v002/Surface/M_'+name,dest+'/Surface/M_'+name);assert m;mats[name]=m
 # Water uses an intentionally quiet opaque mobile baseline, no faceted highlight geometry.
 M=unreal.MaterialEditingLibrary;m=mats['Water'];M.delete_all_material_expressions(m)
 world=M.create_material_expression(m,unreal.MaterialExpressionWorldPosition,-1000,0);xy=M.create_material_expression(m,unreal.MaterialExpressionComponentMask,-850,0)
 for key,val in [('r',True),('g',True),('b',False),('a',False)]:xy.set_editor_property(key,val)
 assert M.connect_material_expressions(world,M.get_material_expression_output_names(world)[0],xy,M.get_material_expression_input_names(xy)[0])
 scale=M.create_material_expression(m,unreal.MaterialExpressionDivide,-700,0);scale.set_editor_property('const_b',900.);assert M.connect_material_expressions(xy,'',scale,'A')
 tex=M.create_material_expression(m,unreal.MaterialExpressionTextureSample,-550,0);tex.set_editor_property('texture',unreal.load_asset('/Game/Ananse/Environments/HeroCells_v002/Surface/SurfaceBreakup'));tex.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR);assert M.connect_material_expressions(scale,'',tex,'UVs')
 lerp=M.create_material_expression(m,unreal.MaterialExpressionLinearInterpolate,-200,0)
 for pin,col in [('A',(.018,.065,.075,1)),('B',(.045,.14,.15,1))]:
  c=M.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-400,-150);c.set_editor_property('constant',unreal.LinearColor(*col));assert M.connect_material_expressions(c,'',lerp,pin)
 assert M.connect_material_expressions(tex,'R',lerp,'Alpha');assert M.connect_material_property(lerp,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for prop,val in [(unreal.MaterialProperty.MP_ROUGHNESS,.26),(unreal.MaterialProperty.MP_SPECULAR,.35)]:
  c=M.create_material_expression(m,unreal.MaterialExpressionConstant,-150,250);c.set_editor_property('r',val);assert M.connect_material_property(c,'',prop)
 for m in mats.values():M.recompile_material(m);save(m)
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
  for a in original:
   label=a.get_actor_label()
   if market and label in ['Pass2 RiverBend','Pass2 RiverQuay','Pass2 FarBank','Pass2 SettlementDepth']:hide(a)
   if not market and label in ['Pass2 SentinelTree','Pass2 LeaningTree','Pass2 ForkedTree','Pass2 RemainingGrove','Pass2 ForestDepth','Pass2 StreamReach','Pass2 SanctuaryFrame']:hide(a)
  def add(key,places,scale=(1,1,1)):
   a=actors.spawn_actor_from_class(unreal.AnanseEnvironmentCluster,unreal.Vector());a.set_actor_label('Pass3 '+key);c=a.get_editor_property('instances');c.set_static_mesh(meshes[key]);c.set_mobility(unreal.ComponentMobility.STATIC);c.set_collision_profile_name('NoCollision')
   for x,y,z,yaw in places:c.add_instance(unreal.Transform(unreal.Vector(x,y,z),unreal.Rotator(pitch=0,yaw=yaw,roll=0),unreal.Vector(*scale)))
   placements.append({'key':key,'positions_cm':places,'scale':scale,'mesh':meshes[key].get_path_name(),'collision':'NoCollision'})
  if market:
   add('RiverMargin',[(3630,0,-35,90)],(2.4,1,1))
   # Separate quarter forms, different height/width/depth and spacing, no contiguous repeated wall.
   for k in range(3):add('SkylineQuarter'+str(k),[(5650+k*170,-2400+k*1800,-10,90+k*5)],(1.1+k*.12,1,1.05+k*.12))
   add('DyersCourt',[(-1200,-850,0,20),(-650,1050,0,180),(-1550,600,0,70)])
   add('ArchiveCrown',[(650,390,0,0)])
  else:
   add('CrownGuardian',[(760,0,0,35)])
   add('RiverFig',[(-760,0,0,190)])
   add('TwinnedElder',[(380,658,0,90)])
   add('CrownGuardian',[(-650,670,-5,120)],(.9,.9,1.05))
   add('RiverFig',[(600,-800,-5,15)],(.8,.8,.95))
   for k in range(3):
    add('DepthGrove'+str(k),[(1550*math.cos((i*3+k)*math.tau/12),1550*math.sin((i*3+k)*math.tau/12),-30,(i*3+k)*30+85)for i in range(4)],(1,1,.95+k*.09))
    add('DepthGrove'+str(k),[(2600*math.cos((i*3+k+.4)*math.tau/12),2600*math.sin((i*3+k+.4)*math.tau/12),-60,(i*3+k+.4)*30+95)for i in range(4)],(1.4,1.2,1.1))
   add('LivingStream',[(350,-200,0,0)])
   add('RootTheatre',[(-120,430,0,180)])
   add('FernEcology',[(-600,170,0,25),(-500,480,0,70),(-350,640,0,130),(100,640,0,10),(600,350,0,160),(650,-420,0,50),(-550,-420,0,70),(100,-420,0,30)],(1.2,1.2,1))
  assert before=={a.get_name():snapshot(a)for a in original},'Original transform/collision/action changed';assert levels.save_current_level();result['maps'].append({'path':path,'anchors_unchanged':True,'snapshot':before,'hidden_visuals':hidden,'placements':placements});original=[];a=c=None
 result['status']='saved_pending_reopen_visual_and_packaged_checks';result['lighting']='Existing fallback/exposure unchanged; no light/fog changes. Opaque material baseline.'
except Exception:result['exception']=traceback.format_exc();raise
finally:(out/'pass3-native.json').write_text(json.dumps(result,indent=2)+'\n')
