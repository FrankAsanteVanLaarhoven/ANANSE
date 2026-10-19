"""Correct source-to-native facade facing, keeping all anchors and collisions fixed."""
import unreal,json,os
from pathlib import Path
out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);path='/Game/Ananse/Maps/EnvironmentRoute_v002/L_RiverMarket_Route';assert levels.load_level(path);rows=[]
for a in actors.get_all_level_actors():
 if not isinstance(a,unreal.AnanseEnvironmentCluster)or a.get_actor_label()!='Route MarketFacade':continue
 c=a.get_editor_property('instances')
 for i in range(c.get_instance_count()):
  t=c.get_instance_transform(i,False)
  if isinstance(t,tuple):t=next(x for x in t if isinstance(x,unreal.Transform))
  p=t.translation;yaw=180. if p.y>0 else 0.;new=unreal.Transform(unreal.Vector(p.x,p.y,p.z),unreal.Rotator(pitch=0,yaw=yaw,roll=0),unreal.Vector(1,1,1));assert c.update_instance_transform(i,new,False,True,True);rows.append({'index':i,'location_cm':[p.x,p.y,p.z],'yaw':yaw,'reason':'Native glTF Y handedness reverses source facade front; doors face route. Collision boxes symmetric and unchanged.'})
assert len(rows)==10;assert levels.save_current_level();(out/'orientation.json').write_text(json.dumps(rows,indent=2)+'\n')
