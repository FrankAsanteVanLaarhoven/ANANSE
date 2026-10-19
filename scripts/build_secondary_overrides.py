"""Preserve current per-component art overrides while adding masked motion graphs."""
import unreal,json,os,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from secondary_material_authoring import build_motion_material
out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);names={'CanopySwag','Understory','CrownGuardian','RiverFig','TwinnedElder','RiverReach','StreamPools','LayeredGrove0','LayeredGrove1','LayeredGrove2','EcologyIsland','VerandaCorner'};cache={};rows=[]
for map in ['L_RiverMarket_Route','L_StoryForest_Route']:
 assert levels.load_level('/Game/Ananse/Maps/EnvironmentRoute_v002/'+map)
 for actor in actors.get_all_level_actors():
  if not isinstance(actor,unreal.AnanseEnvironmentCluster):continue
  c=actor.get_editor_property('instances');mesh=c.get_editor_property('static_mesh')
  if not mesh or mesh.get_name()not in names:continue
  for i in range(c.get_num_materials()):
   old=c.get_material(i)
   if not old or not any(s in old.get_name().lower()for s in ['bark','leaf','water','indigo','jade']):continue
   key=old.get_path_name()
   if key not in cache:
    folder='/Game/Ananse/Environments/Motion_v001/Overrides/'+key.split('.')[0].removeprefix('/Game/').rsplit('/',1)[0];cache[key]=build_motion_material(old,folder,old.get_name())
   rows.append({'map':map,'actor':actor.get_actor_label(),'slot':i,'source':key,'motion':cache[key].get_path_name()})
(out/'bindings.json').write_text(json.dumps({'status':'saved_new_materials_only_maps_not_modified','bindings':rows},indent=2))
