"""Export the authoritative native mesh for inspection, preserving its bytes."""
import unreal,os,json,hashlib,struct
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'spider-native-export.json'
dest=root/'SourceArt/Characters/AnanseSpider/NativeReference_v001';dest.mkdir(parents=True,exist_ok=False)
native=root/'Unreal/Content/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY.uasset'
before=hashlib.sha256(native.read_bytes()).hexdigest();filename=dest/'AnanseSpider_NativeReference.fbx'
mesh=unreal.load_asset('/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY');assert isinstance(mesh,unreal.SkeletalMesh)
task=unreal.AssetExportTask()
for k,v in dict(object=mesh,filename=str(filename),automated=True,prompt=False,replace_identical=False,
    exporter=unreal.SkeletalMeshExporterFBX(),options=unreal.FbxExportOption()).items():task.set_editor_property(k,v)
assert unreal.Exporter.run_asset_export_task(task) and filename.is_file() and filename.stat().st_size>1000
assert hashlib.sha256(native.read_bytes()).hexdigest()==before
raw=filename.read_bytes()
out.write_text(json.dumps(dict(status='native_mesh_exported_read_only',source_mesh=mesh.get_path_name(),
    native_mesh_sha256=before,fbx_path=str(filename),fbx_sha256=hashlib.sha256(raw).hexdigest(),
    observed_binary_fbx_version=struct.unpack_from('<I',raw,23)[0] if raw.startswith(b'Kaydara FBX Binary') else None,
    export_version_forced=False,native_reimported=False),indent=2)+'\n')
