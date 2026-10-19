"""Read-only native binding audit; does not save, compile or alter assets."""
import json
import os
from pathlib import Path
import traceback
import unreal

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ['ANANSE_EVIDENCE_DIR']).resolve()
OUT.mkdir(parents=True, exist_ok=False)
report = {'status': 'failed', 'characters': [], 'environments': [],
          'creative_acceptance': 'REVIEW_REQUIRED', 'mobile': 'UNQUALIFIED',
          'scope': 'Saved native types and bindings only; runtime evidence is separate.'}

def checked(path, expected):
    asset = unreal.load_asset(path)
    assert isinstance(asset, expected), (path, expected, type(asset))
    return asset

try:
    for key in ['Kwaku', 'AsoYaa', 'EsiHuman', 'OseboHuman', 'KojoTortoise', 'KofiHornbill', 'EsiMoth', 'OseboLeopard', 'AnanseSpider']:
        if key == 'AnanseSpider':
            base = '/Game/Production/Characters/SpiderSelection_v001/'
            rigbase = '/Game/Production/Characters/SpiderRig_v001/'
        else:
            revision = 'ArtPass2_v003' if key in ['Kwaku', 'OseboLeopard'] else 'Contact_v002' if key == 'AsoYaa' else 'Story_v001'
            base = '/Game/Ananse/Characters/' + key + '/' + revision + '/'
            rigbase = '/Game/Ananse/Characters/OseboLeopard/Rig/' if key == 'OseboLeopard' else '/Game/Ananse/Characters/Kwaku/Story_v001/' if key == 'Kwaku' else base
        definition = checked(base + 'DA_' + key, unreal.AnanseCharacterDefinition)
        cls = unreal.EditorAssetLibrary.load_blueprint_class(base + 'BP_' + key)
        assert cls, (key, 'missing generated pawn class')
        defaults = unreal.get_default_object(cls)
        assert isinstance(defaults, unreal.AnansePlayer), (key, 'wrong pawn parent')
        if key == 'AnanseSpider':
            mesh = defaults.get_editor_property('mesh').get_editor_property('skeletal_mesh_asset')
        else:
            mesh = defaults.get_editor_property('leopard_mesh' if key == 'OseboLeopard' else 'authored_mesh')
        assert isinstance(mesh, unreal.SkeletalMesh), (key, 'missing skeletal mesh')
        skeleton = mesh.get_editor_property('skeleton')
        physics = mesh.get_editor_property('physics_asset')
        assert isinstance(skeleton, unreal.Skeleton) and isinstance(physics, unreal.PhysicsAsset)
        ik = checked(rigbase + 'IK_' + key, unreal.IKRigDefinition)
        control = checked(rigbase + 'CR_' + key, unreal.ControlRigBlueprint)
        animbase = '/Game/Ananse/Characters/OseboLeopard/Animations/' if key == 'OseboLeopard' else rigbase
        animation = checked(animbase + 'ABP_' + key, unreal.AnimBlueprint)
        generated_animation = unreal.load_class(None, animation.get_path_name() + '_C')
        assert animation.get_editor_property('target_skeleton') == skeleton, (key, 'animation skeleton mismatch')
        assert generated_animation, (key, 'missing generated animation class')
        description = json.loads(unreal.AnanseAnimationAuthoring.describe_rig(mesh))
        assert description['bones'] and description['lod_count'] > 0
        report['characters'].append({'key': key, 'definition': definition.get_path_name(),
            'revision': definition.get_editor_property('revision'), 'pawn_class': cls.get_path_name(),
            'mesh': mesh.get_path_name(), 'skeleton': skeleton.get_path_name(), 'physics': physics.get_path_name(),
            'ik': ik.get_path_name(), 'control_rig': control.get_path_name(),
            'animation_blueprint': animation.get_path_name(), 'animation_class': generated_animation.get_path_name(),
            'bones': len(description['bones']), 'lod_count': description['lod_count'], 'passed': True})
    for name in ['L_RiverMarket_Route', 'L_StoryForest_Route']:
        world = checked('/Game/Ananse/Maps/EnvironmentRoute_v002/' + name, unreal.World)
        report['environments'].append({'map': world.get_path_name(), 'passed': True})
    report['status'] = 'native_bindings_reopened'
except Exception:
    report['exception'] = traceback.format_exc()
    raise
finally:
    (OUT / 'native-wiring.json').write_text(json.dumps(report, indent=2) + '\n')
