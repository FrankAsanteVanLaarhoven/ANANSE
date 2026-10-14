"""Run INSIDE Unreal Editor after compiling the Ananse module.
Only creates a named generated map/material. It never installs plugins or imports external models.
Set ANANSE_REGENERATE_GREYBOX=1 explicitly to replace this generated level.
"""
import json,os
from pathlib import Path
import unreal
PROJECT=Path(unreal.Paths.project_dir())
ROOT=PROJECT.parent
MAP='/Game/Maps/L_Market_Greybox'
MATERIAL='/Game/Art/Prototype/M_AnansePrototype'
report={'status':'started','generated_only':True,'map':MAP}
try:
    if unreal.EditorAssetLibrary.does_asset_exist(MAP) and os.environ.get('ANANSE_REGENERATE_GREYBOX')!='1':
        raise RuntimeError('Generated map exists. Preserve any edits. Explicitly set ANANSE_REGENERATE_GREYBOX=1 only to replace it.')
    unreal.EditorAssetLibrary.make_directory('/Game/Art/Prototype')
    unreal.EditorAssetLibrary.make_directory('/Game/Maps')
    material=unreal.load_asset(MATERIAL)
    if not material:
        material=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_AnansePrototype','/Game/Art/Prototype',unreal.Material,unreal.MaterialFactoryNew())
        colour=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionVectorParameter,-320,0)
        colour.set_editor_property('parameter_name','ClothColor');colour.set_editor_property('default_value',unreal.LinearColor(0.5,0.3,0.1,1))
        unreal.MaterialEditingLibrary.connect_material_property(colour,'',unreal.MaterialProperty.MP_BASE_COLOR)
        rough=unreal.MaterialEditingLibrary.create_material_expression(material,unreal.MaterialExpressionConstant,-320,150)
        rough.set_editor_property('r',0.85);unreal.MaterialEditingLibrary.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
        unreal.MaterialEditingLibrary.recompile_material(material);unreal.EditorAssetLibrary.save_loaded_asset(material)
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not levels.new_level(MAP):raise RuntimeError('Unreal refused to create the greybox level.')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    cube=unreal.load_asset('/Engine/BasicShapes/Cube.Cube')
    if not cube:raise RuntimeError('Engine BasicShapes cube is unavailable.')
    def block(label,position,scale):
        a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*position))
        a.set_actor_label(label);a.set_actor_scale3d(unreal.Vector(*scale));c=a.static_mesh_component;c.set_static_mesh(cube);c.set_material(0,material);return a
    block('Greybox floor',(0,0,-50),(50,40,1))
    block('North boundary',(0,1900,200),(50,1,5));block('South boundary',(0,-1900,200),(50,1,5))
    block('West boundary',(-2400,0,200),(1,40,5));block('East boundary',(2400,0,200),(1,40,5))
    for x in [-1050,-650,-250,150]:
        for y in [-800,1050]:
            block(f'Stall base {x} {y}',(x,y,60),(2.4,1.4,1.2))
            block(f'Stall canopy {x} {y}',(x,y,260),(2.9,1.9,0.15))
            for dx in [-125,125]:block('Canopy post',(x+dx,y,140),(0.12,0.12,2.8))
    block('Web Step roof deck',(50,650,120),(8,5,2.4))
    block('Archive rear wall',(1150,650,150),(0.3,6,3))
    block('Archive side wall',(870,950,150),(6,0.3,3))
    start=actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(-900,-350,110),unreal.Rotator(0,0,0));start.set_actor_label('Start Story Road')
    anchor=actors.spawn_actor_from_class(unreal.TargetPoint,unreal.Vector(-150,650,340));anchor.set_actor_label('Validated Web Step anchor');anchor.set_editor_property('tags',[unreal.Name('WebAnchor')])
    block('Web anchor visible marker',(-150,650,265),(0.3,0.3,0.4))
    specs=[('evidence','Inspect altered edict',(-650,-350,60),''),('listen','Learn captain call',(-500,150,60),'osebo'),('negotiate','Negotiate witness protection',(50,-200,60),'aso-yaa'),('archive','Request archive access',(650,250,60),''),('archive','Rooftop archive opening',(250,700,300),''),('ledger','Recover stolen names',(1000,250,60),''),('expose','Expose forged history',(1450,-150,60),'esi'),('protect','Protect named witnesses',(1450,350,60),'kojo')]
    for action,label,pos,character in specs:
        a=actors.spawn_actor_from_class(unreal.AnanseInteractable,unreal.Vector(*pos));a.set_actor_label(label)
        a.set_editor_property('action',unreal.Name(action));a.set_editor_property('character_id',unreal.Name(character))
        a.get_editor_property('label').set_text(unreal.Text(label));a.get_editor_property('mesh').set_material(0,material)
    guard=actors.spawn_actor_from_class(unreal.AnanseWatchman,unreal.Vector(800,480,90),unreal.Rotator(0,180,0));guard.set_actor_label('Local archive watcher (not Osebo chase AI)')
    light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,1000),unreal.Rotator(-45,-30,0))
    light.light_component.set_editor_property('intensity',3.0);light.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    sky=actors.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,900));sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE);sky.light_component.set_editor_property('intensity',0.8)
    # Greybox lighting is dynamic. The production mobile slice requires authored/baked lighting.
    if not levels.save_current_level():raise RuntimeError('Level save failed.')
    unreal.EditorAssetLibrary.save_directory('/Game/Art/Prototype')
    if not unreal.EditorAssetLibrary.does_asset_exist(MAP):raise RuntimeError('Saved map cannot be resolved.')
    report.update(status='created',actor_count=len(actors.get_all_level_actors()),material=MATERIAL)
except Exception as exc:
    report.update(status='failed',error=str(exc));unreal.log_error(str(exc))
finally:
    out=Path(os.environ.get('ANANSE_EVIDENCE_DIR',str(ROOT/'evidence')))/'unreal-bootstrap.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2))
    unreal.SystemLibrary.quit_editor()
