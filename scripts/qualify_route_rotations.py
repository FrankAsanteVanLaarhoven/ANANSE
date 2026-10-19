"""Named rotation axes plus numeric native instance checks; no gameplay-root changes."""
import unreal,json,os,math
from pathlib import Path
out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[]
# Independent convention probe: a90deg yaw rotates +X toward +Y, without vertical motion.
probe=unreal.Transform(rotation=unreal.Rotator(pitch=0,yaw=90,roll=0));p=unreal.MathLibrary.transform_location(probe,unreal.Vector(100,0,0));assert abs(p.x)<.001 and abs(p.y-100)<.001 and abs(p.z)<.001
for name in ['L_RiverMarket_Route','L_StoryForest_Route']:
 path='/Game/Ananse/Maps/EnvironmentRoute_v002/'+name;assert levels.load_level(path)
 for a in actors.get_all_level_actors():
  if isinstance(a,unreal.AnanseEnvironmentCluster):
   key=a.get_actor_label().removeprefix('Route ');c=a.get_editor_property('instances')
   for i in range(c.get_instance_count()):
    t=c.get_instance_transform(i,False)
    if isinstance(t,tuple):t=next(x for x in t if isinstance(x,unreal.Transform))
    pos=t.translation;old=t.rotation.rotator();yaw=(180 if pos.y>0 else 0)if key=='MarketFacade'else 90 if key=='DockSection'else i*30 if key=='SanctuaryTree'else i*45 if key in ['SanctuaryRock','ForestFern']else 0
    new=unreal.Transform(location=pos,rotation=unreal.Rotator(pitch=0,yaw=yaw,roll=0),scale=t.scale3d);assert c.update_instance_transform(i,new,False,True,True);check=c.get_instance_transform(i,False)
    if isinstance(check,tuple):check=next(x for x in check if isinstance(x,unreal.Transform))
    actual=check.rotation.rotator();assert abs(actual.pitch)<.001 and abs(actual.roll)<.001 and abs(math.remainder(actual.yaw-yaw,360))<.001
    rows.append({'map':path,'module':key,'index':i,'location_cm':[pos.x,pos.y,pos.z],'before_pitch_yaw_roll':[old.pitch,old.yaw,old.roll],'after_pitch_yaw_roll':[actual.pitch,actual.yaw,actual.roll]})
  if isinstance(a,unreal.StaticMeshActor)and a.get_actor_label()=='Route collision rock':
   # Match each saved rock's intended azimuth without tilting its collision box.
   pos=a.get_actor_location();i=round((math.atan2(pos.y,pos.x)%(math.tau))/(math.tau/24))%24;a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=i*45,roll=0),False)
 assert levels.save_current_level();a=c=None
(out/'rotations.json').write_text(json.dumps({'probe_cm':[p.x,p.y,p.z],'instances':rows,'status':'NAMED_YAW_AXES_VERIFIED'},indent=2)+'\n')
