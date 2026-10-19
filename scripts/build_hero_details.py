"""Import benchmark scenery; retain original gameplay and collision anchors exactly."""
import unreal,json,os,math,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);src=R/'SourceArt/Environments/MarketSanctuary/HeroCells_v001';contract=json.loads((src/'detail-status.json').read_text());dest='/Game/Ananse/Environments/HeroCells_v001'
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
 for n in ['Lime','Timber','Stone','Jade','GoldThread']:mats[n]=unreal.load_asset(dest+'/Surface/M_'+n)
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
  path='/Game/Ananse/Maps/EnvironmentRoute_v002/'+name;assert levels.load_level(path);original=list(actors.get_all_level_actors());before={a.get_name():snapshot(a)for a in original}
  if market:
   for a in original:
    if isinstance(a,unreal.StaticMeshActor) and 'Wall_Web_Step_roof_deck' in a.get_actor_label():a.set_actor_hidden_in_game(True);a.static_mesh_component.set_visibility(False,False)
  key='RoofGallery' if market else 'WovenDeck';pos=(50,650,0) if market else (350,-200,0)
  a=actors.spawn_actor_from_class(unreal.AnanseEnvironmentCluster,unreal.Vector());a.set_actor_label('Hero cell '+key);c=a.get_editor_property('instances');c.set_static_mesh(meshes[key]);c.set_mobility(unreal.ComponentMobility.STATIC);c.set_collision_profile_name('NoCollision');c.add_instance(unreal.Transform(unreal.Vector(*pos),unreal.Rotator(),unreal.Vector(1,1,1)))
  if not market:
   for a in original:
    if isinstance(a,unreal.SkyLight):a.get_component_by_class(unreal.SkyLightComponent).set_intensity(3.0)
    if isinstance(a,unreal.AnanseEnvironmentCluster) and a.get_actor_label()=='Hero cell SanctuaryMarker':
     c=a.get_editor_property('instances');c.update_instance_transform(0,unreal.Transform(unreal.Vector(-120,430,0),unreal.Rotator(pitch=0,yaw=180,roll=0),unreal.Vector(1,1,1)),False,True,True)
  assert before=={a.get_name():snapshot(a)for a in original};assert levels.save_current_level();result['maps'].append({'path':path,'protected_anchors_unchanged':True,'visual_module':key,'position_cm':pos})
 result['status']='saved_pending_reopen_render_and_package'
except Exception:result['exception']=traceback.format_exc();raise
finally:(out/'hero-details.json').write_text(json.dumps(result,indent=2)+'\n')
