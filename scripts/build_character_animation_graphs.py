"""Create two functional, independently bound clip Animation Blueprints."""
import json,os,traceback
from pathlib import Path
import unreal

out=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'animation-graphs.json'
if out.exists():raise RuntimeError('Preserve prior authoring evidence')
root=Path(__file__).resolve().parents[1]
leopard=json.loads((root/'.local/verification/osebo-family-20261015/native-import-v002/leopard-import.json').read_text())
jobs=[dict(name='ABP_AnanseSpider',dest='/Game/Production/Characters/SpiderRig_v001',
    mesh='/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY',
    clip='/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXYA_Idle_Proxy',
    parent=unreal.AnanseContactAnimInstance,contact=True),
 dict(name='ABP_OseboLeopard',dest='/Game/Ananse/Characters/OseboLeopard/Animations',mesh=leopard['mesh'],
    clip=leopard['clips']['IdleGuard'],parent=unreal.AnanseLeopardAnimInstance,contact=False)]
result=dict(status='failed',assets=[])
try:
    for job in jobs:
        path=job['dest']+'/'+job['name']
        if unreal.EditorAssetLibrary.does_asset_exist(path):raise RuntimeError('Existing graph preserved: '+path)
        mesh=unreal.load_asset(job['mesh']);clip=unreal.load_asset(job['clip'])
        assert isinstance(mesh,unreal.SkeletalMesh) and isinstance(clip,unreal.AnimSequence)
        factory=unreal.AnimBlueprintFactory();factory.set_editor_property('parent_class',job['parent'])
        factory.set_editor_property('target_skeleton',mesh.get_editor_property('skeleton'))
        bp=unreal.AssetToolsHelpers.get_asset_tools().create_asset(job['name'],job['dest'],unreal.AnimBlueprint,factory)
        response=unreal.AnanseAnimationAuthoring.populate_clip_graph(bp,clip)
        # Installed Python binding treats bool+out as success/failure and returns
        # just the out string on success, rather than a two-element tuple.
        if response is None or (isinstance(response,str) and response) or (isinstance(response,tuple) and not response[0]):
            raise RuntimeError('Native graph authoring failed: '+str(response))
        cls=unreal.EditorAssetLibrary.load_blueprint_class(path);assert cls
        cdo=unreal.get_default_object(cls)
        if job['contact']:cdo.set_editor_property('use_authored_graph',True)
        assert unreal.EditorAssetLibrary.save_loaded_asset(bp)
        result['assets'].append(dict(path=bp.get_path_name(),native_class=bp.get_class().get_name(),
            generated_class=cls.get_path_name(),skeleton=mesh.get_editor_property('skeleton').get_path_name(),
            graph='Clip variable -> Sequence Player -> Output Pose',
            final_solve='Existing native four-leg solve after source graph' if job['contact'] else 'Feline graph; foot contacts still pending',
            runtime_evaluation_tested=False))
    result['status']='compiled_saved_pending_reopen_and_runtime'
except Exception:
    result['exception']=traceback.format_exc();raise
finally:out.write_text(json.dumps(result,indent=2)+'\n')
