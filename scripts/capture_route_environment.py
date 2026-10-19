"""Fixed-camera native diagnostic views; actual saved map geometry, no map edits."""
import unreal,json,os
from pathlib import Path
out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);worlds=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);rows=[]
market=[('overview',(-1900,-1750,1550),(0,0,100),65),('arrival',(-1000,-580,220),(-500,-200,100),65),('rooftop',(-400,1000,700),(400,600,170),60),('archive_approach',(250,100,200),(1000,400,150),60),('pursuit',(800,-600,240),(1500,0,140),65),('consequence',(1150,-500,200),(1500,200,100),65),('river',(1750,-850,300),(2400,-100,50),65)]
forest=[('forest_entry',(-500,-600,260),(0,100,100),65),('sanctuary_clearing',(650,-900,650),(-100,100,150),65)]
jobs=[]
for label,path,shots in [('market_before','/Game/Ananse/Maps/Contact_v002/L_Market_AsoNegotiation',market),('market_after','/Game/Ananse/Maps/EnvironmentRoute_v002/L_RiverMarket_Route',market),('forest_before','/Game/Ananse/Maps/EpisodeAccepted_v001/L_Sanctuary_AcceptedVisuals',forest),('forest_after','/Game/Ananse/Maps/EnvironmentRoute_v002/L_StoryForest_Route',forest+[('web_bridge',(600,-650,280),(350,-200,65),60)])]:
 for shot in shots:jobs.append((label,path,shot))
state={'index':0,'phase':0,'wait':0,'map':None};capture=None;target_texture=None

def tick(delta):
 global capture,target_texture
 try:
  if state['wait']>0:state['wait']-=delta;return
  if state['index']>=len(jobs):
   (out/'cameras.json').write_text(json.dumps(rows,indent=2)+'\n');unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor();return
  label,path,(name,loc,target,fov)=jobs[state['index']]
  if state['phase']==0:
   if state['map']!=path:
    assert levels.load_level(path);state['map']=path;state['wait']=4.;return
   world=worlds.get_editor_world();capture=actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(*loc));capture.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc),unreal.Vector(*target)),False);c=capture.get_component_by_class(unreal.SceneCaptureComponent2D);target_texture=unreal.RenderingLibrary.create_render_target2d(world,1280,720,unreal.TextureRenderTargetFormat.RTF_RGBA8);c.set_editor_property('texture_target',target_texture);c.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR);c.set_editor_property('fov_angle',fov);state['phase']=1;state['wait']=2.;return
  if state['phase']==1:
   capture.get_component_by_class(unreal.SceneCaptureComponent2D).capture_scene();state['phase']=2;state['wait']=.5;return
  file=label+'_'+name+'.png';unreal.RenderingLibrary.export_render_target(worlds.get_editor_world(),target_texture,str(out),file);rows.append({'file':file,'map':path,'location_cm':loc,'target_cm':target,'fov_degrees':fov,'method':'Native SceneCapture2D, final-color LDR, 1280x720 after scene settle; editor diagnostic, not packaged framebuffer'});actors.destroy_actor(capture);capture=target_texture=None;state['phase']=0;state['index']+=1;state['wait']=.2
 except Exception:
  import traceback
  (out/'failure.txt').write_text(traceback.format_exc());unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
