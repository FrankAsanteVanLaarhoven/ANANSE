"""Import benchmark scenery; retain original gameplay and collision anchors exactly."""
import unreal,json,os,math,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);src=R/'SourceArt/Environments/MarketSanctuary/HeroCells_v004';contract=json.loads((src/'source-status.json').read_text());dest='/Game/Ananse/Environments/HeroCells_v004'
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
 M=unreal.MaterialEditingLibrary
 for row in contract['surfaces']:
  name=row['name'];texture=next(a for a in import_file(src/row['texture'],dest+'/Surface')if isinstance(a,unreal.Texture2D));texture.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_DEFAULT);texture.set_editor_property('srgb',True);save(texture)
  m=tools.create_asset('M_'+name,dest+'/Surface',unreal.Material,unreal.MaterialFactoryNew());assert m;mats[name]=m
  tex=M.create_material_expression(m,unreal.MaterialExpressionTextureSample,-400,0);tex.set_editor_property('texture',texture);assert M.connect_material_property(tex,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
  for prop,val in [(unreal.MaterialProperty.MP_ROUGHNESS,row['roughness']),(unreal.MaterialProperty.MP_METALLIC,row['metallic'])]:
   c=M.create_material_expression(m,unreal.MaterialExpressionConstant,-200,200);c.set_editor_property('r',val);assert M.connect_material_property(c,'',prop)
  if name in ['GoldThread','DistantLeaf','DistantBark']:
   c=M.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-200,400);c.set_editor_property('constant',unreal.LinearColor(*({'GoldThread':(.24,.11,.012,1),'DistantLeaf':(.009,.018,.020,1),'DistantBark':(.005,.010,.013,1)}[name])));assert M.connect_material_property(c,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
  m.set_editor_property('two_sided',name in ['Leaf','DistantLeaf','Indigo','Jade']);M.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);M.recompile_material(m);save(m)
 # Opaque conventional water: opposing moving normals, angle-dependent colour, no screen refraction.
 m=mats['Water'];M.delete_all_material_expressions(m);normal=unreal.load_asset('/Game/Ananse/Environments/HeroCells_v002/Surface/SurfaceNormal');samples=[]
 for k,(sx,sy)in enumerate([(.018,.007),(-.009,.013)]):
  pan=M.create_material_expression(m,unreal.MaterialExpressionPanner,-800,k*200);pan.set_editor_property('speed_x',sx);pan.set_editor_property('speed_y',sy)
  n=M.create_material_expression(m,unreal.MaterialExpressionTextureSample,-600,k*200);n.set_editor_property('texture',normal);n.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL);assert M.connect_material_expressions(pan,'',n,'UVs');samples.append(n)
 blend=M.create_material_expression(m,unreal.MaterialExpressionLinearInterpolate,-400,-200);blend.set_editor_property('const_alpha',.5)
 for pin,n in zip(['A','B'],samples):assert M.connect_material_expressions(n,'RGB',blend,pin)
 strength=M.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-400,-400);strength.set_editor_property('constant',unreal.LinearColor(.28,.28,1,1));mul=M.create_material_expression(m,unreal.MaterialExpressionMultiply,-200,-200);assert M.connect_material_expressions(blend,'',mul,'A');assert M.connect_material_expressions(strength,'',mul,'B');assert M.connect_material_property(mul,'',unreal.MaterialProperty.MP_NORMAL)
 fresnel=M.create_material_expression(m,unreal.MaterialExpressionFresnel,-400,300);colour=M.create_material_expression(m,unreal.MaterialExpressionLinearInterpolate,-100,100)
 for pin,col in [('A',(.012,.065,.074,1)),('B',(.09,.19,.20,1))]:
  c=M.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-300,100);c.set_editor_property('constant',unreal.LinearColor(*col));assert M.connect_material_expressions(c,'',colour,pin)
 assert M.connect_material_expressions(fresnel,'',colour,'Alpha');assert M.connect_material_property(colour,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for prop,val in [(unreal.MaterialProperty.MP_ROUGHNESS,.32),(unreal.MaterialProperty.MP_SPECULAR,.4)]:
  c=M.create_material_expression(m,unreal.MaterialExpressionConstant,-200,500);c.set_editor_property('r',val);assert M.connect_material_property(c,'',prop)
 M.recompile_material(m);save(m)
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
  path='/Game/Ananse/Maps/EnvironmentRoute_v002/'+name;assert levels.load_level(path);original=list(actors.get_all_level_actors());before={a.get_name():snapshot(a)for a in original};hidden=[];placements=[];lights=[]
  def hide(a):
   a.set_actor_hidden_in_game(True)
   for c in a.get_components_by_class(unreal.PrimitiveComponent):c.set_visibility(False,False)
   hidden.append(a.get_actor_label())
  for a in original:
   label=a.get_actor_label()
   if market and label=='Pass3 RiverMargin':hide(a)
   if not market and(label.startswith('Pass3 DepthGrove')or label in ['Pass3 LivingStream','Pass3 FernEcology','Pass3 RootTheatre','Hero cell SanctuaryMarker']):hide(a)
   if market and isinstance(a,unreal.AnanseEnvironmentCluster)and label.startswith('Pass3 SkylineQuarter'):
    c=a.get_editor_property('instances')
    # Cool, muted distant material binds to existing silhouettes without changing geometry/anchors.
    for i in range(c.get_num_materials()):c.set_material(i,mats['DistantBark']if i%2==0 else mats['DistantLeaf'])
   if not market and isinstance(a,unreal.DirectionalLight):
    c=a.get_component_by_class(unreal.DirectionalLightComponent);old=c.get_editor_property('intensity');c.set_intensity(2.0);c.set_light_color(unreal.LinearColor(.65,.78,1,1));lights.append({'actor':label,'old_intensity':old,'new_intensity':2.0,'colour_linear':[.65,.78,1],'scope':'existing bounded fallback directional only; shipping bake still blocked'})
  def add(key,places,scale=(1,1,1)):
   a=actors.spawn_actor_from_class(unreal.AnanseEnvironmentCluster,unreal.Vector());a.set_actor_label('Pass4 '+key);c=a.get_editor_property('instances');c.set_static_mesh(meshes[key]);c.set_mobility(unreal.ComponentMobility.STATIC);c.set_collision_profile_name('NoCollision')
   for x,y,z,yaw in places:c.add_instance(unreal.Transform(unreal.Vector(x,y,z),unreal.Rotator(pitch=0,yaw=yaw,roll=0),unreal.Vector(*scale)))
   placements.append({'key':key,'positions_cm':places,'scale':scale,'mesh':meshes[key].get_path_name(),'collision':'NoCollision'})
  if market:
   add('RiverReach',[(3630,0,-35,90),(3630,6000,-35,90)])
   add('QuayApron',[(2550,-750,-3,0),(2550,2250,-3,0),(2550,5250,-3,0)])
   add('DockLife',[(2400,-650,0,20),(2410,650,0,-20),(2460,1250,0,35)])
   add('VerandaCorner',[(-900,250,0,15),(-150,900,0,180),(350,-850,0,10)])
  else:
   for k in range(3):
    add('LayeredGrove'+str(k),[(1750*math.cos((i*3+k)*math.tau/9),1750*math.sin((i*3+k)*math.tau/9),-20,(i*3+k)*40+88)for i in range(3)],(1.15,1,1))
    add('LayeredGrove'+str(k),[(2600*math.cos((i*3+k+.3)*math.tau/9),2600*math.sin((i*3+k+.3)*math.tau/9),-40,(i*3+k+.3)*40+90)for i in range(3)],(1.4,1.1,1.2))
   add('StreamPools',[(350,-200,3,0)])
   add('EcologyIsland',[(-600,200,0,20),(-400,500,0,60),(200,650,0,170),(600,350,0,110),(650,-400,0,25),(-600,-400,0,80),(-150,250,0,30),(150,450,0,70),(450,-500,0,130),(150,-450,0,30)],(1.5,1.5,1))
   add('SanctuaryReliquary',[(-120,430,0,0)])
   add('SanctuaryGarden',[(-120,430,0,0)])
  assert before=={a.get_name():snapshot(a)for a in original},'Protected actor root/collision/action changed';assert levels.save_current_level();result['maps'].append({'path':path,'anchors_unchanged':True,'snapshot':before,'hidden_visuals':hidden,'placements':placements,'existing_fallback_light_changes':lights});original=[];a=c=None
 result['status']='saved_pending_reopen_visual_and_packaged_checks';result['lighting']='Market/exposure unchanged. Forest existing directional fallback retuned; no new lights or shipping strategy changes. Before/after Forest images include this disclosed lighting difference.'
except Exception:result['exception']=traceback.format_exc();raise
finally:(out/'pass4-native.json').write_text(json.dumps(result,indent=2)+'\n')
