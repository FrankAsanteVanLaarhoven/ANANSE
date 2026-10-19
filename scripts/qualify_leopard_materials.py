"""Persist required skeletal shader usage on this character's own materials."""
import json,os
from pathlib import Path
import unreal
root=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'materials.json'
if out.exists():raise RuntimeError('Preserve previous material evidence')
record=json.loads((root/'SourceArt/Characters/OseboLeopard/NATIVE_RIG_MAP_20261015.json').read_text())
paths=sorted({m['material'] for m in record['material_slots']});assert len(paths)==10
results=[]
for path in paths:
    assert path.startswith('/Game/Ananse/Characters/OseboLeopard/Authored_v001/')
    material=unreal.load_asset(path);assert isinstance(material,unreal.Material)
    before=bool(material.get_editor_property('used_with_skeletal_mesh'))
    unreal.MaterialEditingLibrary.set_material_usage(material,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
    assert material.get_editor_property('used_with_skeletal_mesh')
    unreal.MaterialEditingLibrary.recompile_material(material)
    assert unreal.EditorAssetLibrary.save_loaded_asset(material)
    results.append(dict(path=path,before=before,after=True))
out.write_text(json.dumps(dict(status='skeletal_usage_saved',materials=results,original_spider_materials_modified=False),indent=2)+'\n')
