"""Qualify the real morph vertex-factory permutation on project-owned materials."""
import unreal,json,hashlib,os,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=True);report=out/'materials.json';assert not report.exists();mesh=unreal.load_asset('/Game/Ananse/Characters/Kwaku/Refined_v001/Kwaku');records=[];result={'status':'failed'}
try:
 seen=set()
 for slot in mesh.get_editor_property('materials'):
  material=slot.get_editor_property('material_interface');assert isinstance(material,unreal.Material);path=material.get_path_name();assert path.startswith('/Game/Ananse/Characters/Kwaku/Refined_v001/')
  if path in seen:continue
  seen.add(path);source=ROOT/'Unreal/Content'/(path.split('.')[0].removeprefix('/Game/')+'.uasset');before=hashlib.sha256(source.read_bytes()).hexdigest();unreal.MaterialEditingLibrary.set_material_usage(material,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH);unreal.MaterialEditingLibrary.set_material_usage(material,unreal.MaterialUsage.MATUSAGE_MORPH_TARGETS);assert material.get_editor_property('used_with_morph_targets');unreal.MaterialEditingLibrary.recompile_material(material);assert unreal.EditorAssetLibrary.save_loaded_asset(material);records.append({'path':path,'before_sha256':before,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'morph_usage':True,'skeletal_usage':True})
 result.update(status='saved_real_morph_material_permutations_pending_reopen_cook_render',materials=records,original_kwaku_changed=False)
except Exception:result['exception']=traceback.format_exc();raise
finally:report.write_text(json.dumps(result,indent=2)+'\n')
