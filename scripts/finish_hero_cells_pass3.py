"""Correct visible placement and quiet-water shading after fixed-camera native review."""
import unreal,json,os
from pathlib import Path
M=unreal.MaterialEditingLibrary;m=unreal.load_asset('/Game/Ananse/Environments/HeroCells_v003/Surface/M_Water')
# A subtle normal response makes actual surface lighting readable without added lights/transparency.
n=M.create_material_expression(m,unreal.MaterialExpressionTextureSample,-600,-400);n.set_editor_property('texture',unreal.load_asset('/Game/Ananse/Environments/HeroCells_v002/Surface/SurfaceNormal'));n.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
s=M.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-400,-500);s.set_editor_property('constant',unreal.LinearColor(.2,.2,1,1));mul=M.create_material_expression(m,unreal.MaterialExpressionMultiply,-200,-400);assert M.connect_material_expressions(n,'RGB',mul,'A');assert M.connect_material_expressions(s,'',mul,'B');assert M.connect_material_property(mul,'',unreal.MaterialProperty.MP_NORMAL)
colour=M.get_material_property_input_node(m,unreal.MaterialProperty.MP_BASE_COLOR)
for node in M.get_inputs_for_material_expression(m,colour):
 if isinstance(node,unreal.MaterialExpressionConstant3Vector):
  old=node.get_editor_property('constant');node.set_editor_property('constant',unreal.LinearColor(.035,.12,.13,1) if old.r<.03 else unreal.LinearColor(.10,.25,.23,1))
M.recompile_material(m);assert unreal.EditorAssetLibrary.save_loaded_asset(m)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert levels.load_level('/Game/Ananse/Maps/EnvironmentRoute_v002/L_RiverMarket_Route');original=list(actors.get_all_level_actors())
def snap(a):
 p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();return[p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z,a.get_actor_enable_collision()]
before={a.get_name():snap(a)for a in original}
for a in original:
 if not isinstance(a,unreal.AnanseEnvironmentCluster):continue
 c=a.get_editor_property('instances');label=a.get_actor_label()
 if label=='Pass3 DyersCourt':
  for x,y,yaw in [(-350,650,15),(100,-700,30),(-1000,80,55)]:c.add_instance(unreal.Transform(unreal.Vector(x,y,0),unreal.Rotator(pitch=0,yaw=yaw,roll=0),unreal.Vector(1,1,1)))
 if label=='Pass3 RiverMargin':c.add_instance(unreal.Transform(unreal.Vector(3630,6000,-35),unreal.Rotator(pitch=0,yaw=90,roll=0),unreal.Vector(2.4,1,1)))
 if label=='Pass3 SkylineQuarter2':c.add_instance(unreal.Transform(unreal.Vector(5700,3900,0),unreal.Rotator(pitch=0,yaw=82,roll=0),unreal.Vector(1.1,1,.95)))
 if label=='Pass3 ArchiveCrown':c.update_instance_transform(0,unreal.Transform(unreal.Vector(650,390,-35),unreal.Rotator(),unreal.Vector(1,1,1)),False,True,True)
assert before=={a.get_name():snap(a)for a in original};assert levels.save_current_level();Path(os.environ['ANANSE_EVIDENCE_DIR']).write_text(json.dumps({'actor_roots_unchanged':True,'lighting_changes':False,'water':'subtle normal XY scale0.2; opaque macro colour','plaza':'three additional functional dye-work clusters, NoCollision','river_extent':'matches existing Pass2 non-playable backdrop extent','archive':'new canopy lowered35cm to meet existing crown; existing portal untouched'},indent=2))
