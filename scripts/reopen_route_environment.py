"""Read-only native/map audit, including exact original anchor transforms."""
import unreal,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=False);base=json.loads((R/'.local/verification/environment-production-20261017/native-03/environment.json').read_text());sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);r={'status':'reopened','meshes':[],'maps':[]}
for name,row in base['meshes'].items():
 m=unreal.load_asset(row['path']);assert isinstance(m,unreal.StaticMesh);r['meshes'].append({'name':name,'path':m.get_path_name(),'lod_vertices':[sm.get_number_verts(m,i)for i in range(sm.get_lod_count(m))],'nanite_enabled':m.get_editor_property('nanite_settings').get_editor_property('enabled'),'materials':[x.material_interface.get_path_name()if x.material_interface else None for x in m.get_editor_property('static_materials')],'lod_triangles':[m.get_num_triangles(i)for i in range(sm.get_lod_count(m))]})
def frame(a):
 p=a.get_actor_location();q=a.get_actor_rotation();s=a.get_actor_scale3d();return[p.x,p.y,p.z,q.pitch,q.yaw,q.roll,s.x,s.y,s.z]
for row in base['maps']:
 assert levels.load_level(row['path']);allactors=list(actors.get_all_level_actors());byname={a.get_name():a for a in allactors};diff=[];instances=0;bad=[];boxes=0;components=[]
 for name,prior in row['anchors'].items():
  a=byname.get(name)
  if not a or frame(a)!=prior['transform']:diff.append(name)
  elif isinstance(a,unreal.AnanseInteractable)and(str(a.get_editor_property('action'))!=prior['action']or str(a.get_editor_property('character_id'))!=prior['identity']):diff.append(name)
 for a in allactors:
  if isinstance(a,unreal.AnanseEnvironmentCluster):
   c=a.get_editor_property('instances');instances+=c.get_instance_count();components.append({'label':a.get_actor_label(),'instances':c.get_instance_count(),'collision':str(c.get_collision_enabled())})
   if c.get_collision_enabled()!=unreal.CollisionEnabled.NO_COLLISION or a.get_actor_enable_collision():bad.append(a.get_actor_label())
  if a.get_actor_label().startswith('Route collision '):boxes+=1
 r['maps'].append({'path':row['path'],'anchor_differences':diff,'instances':instances,'simple_collision_boxes':boxes,'unexpected_visual_collision':bad,'components':components})
 a=c=m=None;allactors=[];byname={}
(out/'reopen.json').write_text(json.dumps(r,indent=2)+'\n')
