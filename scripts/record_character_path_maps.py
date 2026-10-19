"""Reopen the nine actual asset roles and record their classes and byte hashes."""
import hashlib,json,os,re
from pathlib import Path
import unreal

root=Path(__file__).resolve().parents[1]
report=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'path-maps.json'
if report.exists():raise RuntimeError('Preserve previous evidence')
spider='/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY'
leopard='/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard'
jobs={
 'AnanseSpider':dict(mesh=spider,skeleton=spider+'_Skeleton',physics=spider+'_PhysicsAsset',
   ik='/Game/Production/Characters/SpiderRig_v001/IK_AnanseSpider',control_rig='/Game/Production/Characters/SpiderRig_v001/CR_AnanseSpider',
   animation_blueprint='/Game/Production/Characters/SpiderRig_v001/ABP_AnanseSpider',
   blueprint='/Game/Production/Characters/SpiderSelection_v001/BP_AnanseSpider',definition='/Game/Production/Characters/SpiderSelection_v001/DA_AnanseSpider',
   lab_map='/Game/Characters/AnanseSpider/Lab_v001/L_AnanseCharacterLab'),
 'OseboLeopard':dict(mesh=leopard,skeleton=leopard+'_Skeleton',physics=leopard+'_PhysicsAsset',
   ik='/Game/Ananse/Characters/OseboLeopard/Rig/IK_OseboLeopard',control_rig='/Game/Ananse/Characters/OseboLeopard/Rig/CR_OseboLeopard',
   animation_blueprint='/Game/Ananse/Characters/OseboLeopard/Animations/ABP_OseboLeopard',
   blueprint='/Game/Ananse/Characters/OseboLeopard/Runtime_v001/BP_OseboLeopard',definition='/Game/Ananse/Characters/OseboLeopard/Data/DA_OseboLeopard',
   lab_map='/Game/Ananse/Maps/CharacterLabs/L_OseboLeopardCharacterLab')}
types=dict(mesh='SkeletalMesh',skeleton='Skeleton',physics='PhysicsAsset',ik='IKRigDefinition',control_rig='ControlRigBlueprint',
 animation_blueprint='AnimBlueprint',blueprint='Blueprint',definition='AnanseCharacterDefinition',lab_map='World')
revision=os.environ.get('ANANSE_PATH_MAP_REVISION','20261015');assert re.fullmatch(r'[A-Za-z0-9_]+',revision)
outputs=[]
for key,paths in jobs.items():
 output=root/'SourceArt/Characters'/key/('INTEGRATION_PATH_MAP_'+revision+'.json')
 if output.exists():raise RuntimeError('Preserve existing map '+str(output))
 assets={}
 for role,path in paths.items():
  asset=unreal.load_asset(path);assert asset and asset.get_class().get_name()==types[role],(role,path)
  file=root/'Unreal/Content'/path.removeprefix('/Game/')
  file=file.with_suffix('.umap' if role=='lab_map' else '.uasset');assert file.is_file()
  entry=dict(path=asset.get_path_name(),native_class=asset.get_class().get_name(),file=str(file.relative_to(root)),sha256=hashlib.sha256(file.read_bytes()).hexdigest())
  if role in ['blueprint','animation_blueprint']:
   cls=unreal.EditorAssetLibrary.load_blueprint_class(path);assert cls
   entry['generated_class']=cls.get_path_name()
  assets[role]=entry
 result=dict(design_id='ananse-spider-existing' if key=='AnanseSpider' else 'osebo-leopard-v1',assets=assets,
  authoring_only_roles=['ik','control_rig'],runtime_pose_path='Animation Blueprint clip graph; family-specific native contact solve once; no competing authoring FK runtime solve',
  full_character_accepted=False,creative_approved=False,campaign_mapping_changed=False,
  limitations=['Creative/cultural/rights and full deformation review remain open','Kinematic physics policy; dynamic ragdoll unapproved','Physical controller and mobile untested'])
 output.write_text(json.dumps(result,indent=2)+'\n');outputs.append(str(output))
report.write_text(json.dumps(dict(status='reopened',outputs=outputs,assets_per_design=9),indent=2)+'\n')
