"""Explicit simple scenery collision and conventional precomputed-lighting attempt."""
import unreal,json,math,os,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[];sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
# Reject a known startup crash before changing meshes, collision or maps.
import sys
sys.path.insert(0,str(R))
from scripts.lightmass_preflight import probe_worker
engine_root=Path(os.environ.get('UE_ROOT','/home/favl/Unreal/UE_5.8.3-58210709'))
preflight=probe_worker(engine_root/'Engine/Binaries/Linux/UnrealLightmass',out/'worker-preflight')
if preflight['status']!='startup_probe_completed':
 raise RuntimeError('CPU Lightmass startup blocked; project assets untouched. See '+str(out/'worker-preflight/preflight.json'))
# A completed startup probe does not qualify a bake. Imported lightmaps still require verification.
# Conventional LODs are the actual baseline, Nanite disabled explicitly.
for name in ['MarketFacade','MarketStall','PotterySet','DockSection','RiverSurface','SanctuaryTree','SanctuaryRock','ForestFern']:
 mesh=unreal.load_asset('/Game/Ananse/Environments/Route_v001/'+name+'/'+name);n=mesh.get_editor_property('nanite_settings');n.set_editor_property('enabled',False);mesh.set_editor_property('nanite_settings',n);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
for market,name in [(True,'L_RiverMarket_Route'),(False,'L_StoryForest_Route')]:
 path='/Game/Ananse/Maps/EnvironmentRoute_v002/'+name;assert levels.load_level(path);original=list(actors.get_all_level_actors());r={'map':path,'retired_collision':[],'new_simple_colliders':[],'lighting':[],'baked':False}
 def collider(label,pos,size,yaw=0):
  a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos),unreal.Rotator(pitch=0,yaw=yaw,roll=0));a.set_actor_label('Route collision '+label);a.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));a.set_actor_scale3d(unreal.Vector(*[v/100 for v in size]));a.static_mesh_component.set_collision_profile_name('BlockAll');a.static_mesh_component.set_visibility(False,False);a.static_mesh_component.set_editor_property('cast_shadow',False);a.set_actor_hidden_in_game(True);r['new_simple_colliders'].append({'label':label,'location_cm':pos,'size_cm':size,'yaw':yaw})
 for a in original:
  if isinstance(a,unreal.StaticMeshActor)and a.get_actor_label()in ['Authored MarketArchitecture WIP','Authored MarketStalls WIP','Authored RiverDock WIP','Authored SanctuaryTrees WIP','Authored SanctuaryGround WIP']:
   a.set_actor_enable_collision(False);r['retired_collision'].append(a.get_actor_label())
  if isinstance(a,unreal.DirectionalLight):
   c=a.get_component_by_class(unreal.DirectionalLightComponent);c.set_mobility(unreal.ComponentMobility.STATIONARY);c.set_intensity(3.0 if market else 1.8);c.set_editor_property('dynamic_shadow_distance_stationary_light',1800.);r['lighting'].append({'class':'DirectionalLight','mobility':'Stationary','intensity':3.0 if market else 1.8,'dynamic_shadow_distance_cm':1800.})
  if isinstance(a,unreal.SkyLight):
   c=a.get_component_by_class(unreal.SkyLightComponent);c.set_editor_property('real_time_capture',False);c.set_mobility(unreal.ComponentMobility.STATIC);c.set_intensity(.85 if market else .65);r['lighting'].append({'class':'SkyLight','mobility':'Static','real_time_capture':False})
 if market:
  for y in [-1500,1500]:
   for x in [-1700,-1000,-300,400,1100]:collider('facade',(x,y,225),(600,180,450))
  for y in [-800,1050]:
   for x in [-1050,-650,-250,150]:collider('stall counter',(x,y,51),(248,148,102))
  for y in [-650,-350,-50]:collider('dock deck',(1880,y,8),(200,310,16))
 else:
  for i in range(12):
   a=i*math.tau/12;collider('trunk',(760*math.cos(a),760*math.sin(a),220),(90,90,440))
  for i in range(24):
   a=i*math.tau/24;collider('rock',(600*math.cos(a),600*math.sin(a),20),(100,65,38),i*45)
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('force_no_precomputed_lighting',False);assert levels.save_current_level();r['status']='saved_before_bake';rows.append(r);(out/'finish.json').write_text(json.dumps(rows,indent=2)+'\n')
 # Runs real installed CPU Lightmass; an exit0 alone will not establish a bake.
 try:r['build_api_return']=bool(levels.build_light_maps(unreal.LightingBuildQuality.QUALITY_PREVIEW,False));r['baked']=False;r['bake_validation']='API return alone insufficient; validate imported lightmap textures and worker exit'
 except Exception:r['bake_error']=traceback.format_exc()
 assert levels.save_current_level();r['status']='saved';(out/'finish.json').write_text(json.dumps(rows,indent=2)+'\n');a=c=world=None;original=[]
