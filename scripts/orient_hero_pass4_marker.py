"""Face the new visual inscription toward the reviewed native approach camera."""
import unreal,json,os
from pathlib import Path
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert levels.load_level('/Game/Ananse/Maps/EnvironmentRoute_v002/L_StoryForest_Route');changed=[]
for a in actors.get_all_level_actors():
 if isinstance(a,unreal.AnanseEnvironmentCluster)and a.get_actor_label()=='Pass4 SanctuaryReliquary':
  c=a.get_editor_property('instances');assert c.get_instance_count()==1;c.update_instance_transform(0,unreal.Transform(unreal.Vector(-120,430,0),unreal.Rotator(pitch=0,yaw=214,roll=0),unreal.Vector(1,1,1)),False,True,True);changed.append(a.get_actor_label())
assert len(changed)==1;assert levels.save_current_level();Path(os.environ['ANANSE_EVIDENCE_DIR']).write_text(json.dumps({'new_visual_only':changed,'position_cm':[-120,430,0],'yaw':214,'reason':'native first-view facing was reversed; source/import front-axis correction','gameplay_changes':False},indent=2))
