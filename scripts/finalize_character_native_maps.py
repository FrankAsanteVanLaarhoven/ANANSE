"""Author real feline sockets and export exact native rest/axis/socket maps."""
import json,os,hashlib
from pathlib import Path
import unreal
root=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR'])/'native-maps.json'
if out.exists():raise RuntimeError('Preserve previous map evidence')
jobs=[('AnanseSpider','/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY'),
      ('OseboLeopard','/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard')]
paths=[root/'SourceArt/Characters'/key/'NATIVE_RIG_MAP_20261015.json' for key,_ in jobs]
if any(p.exists() for p in paths):raise RuntimeError('Existing native maps preserved')
leopard=unreal.load_asset(jobs[1][1]);assert isinstance(leopard,unreal.SkeletalMesh)
response=unreal.AnanseAnimationAuthoring.add_leopard_sockets(leopard)
if response is None or (isinstance(response,str) and response):raise RuntimeError('Socket creation failed: '+str(response))
assert unreal.EditorAssetLibrary.save_loaded_asset(leopard.get_editor_property('skeleton'))
records=[]
for (key,path),output in zip(jobs,paths):
    mesh=unreal.load_asset(path);assert isinstance(mesh,unreal.SkeletalMesh)
    record=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(mesh))
    assert len(record['bones'])==(102 if key=='AnanseSpider' else 64)
    record['socket_named_bones']=[b['name'] for b in record['bones'] if b['name'].startswith('socket_')]
    record['socket_calibration']='Imported spider marker bones retained' if key=='AnanseSpider' else 'Paw midpoint and voice/cape offsets authored in native rest frame; final art/interaction review pending'
    if key=='OseboLeopard':
        assert {s['name'] for s in record['socket_objects']}=={'socket_capture_L','socket_capture_R','socket_cape','socket_voice'}
    output.write_text(json.dumps(record,indent=2)+'\n')
    records.append(dict(character=key,path=str(output),sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
        bones=len(record['bones']),socket_objects=len(record['socket_objects']),socket_named_bones=len(record['socket_named_bones']),
        lod_count=record['lod_count'],material_slots=len(record['material_slots']),physics_bodies=len(record['physics_bodies'])))
out.write_text(json.dumps(dict(status='native_maps_written',maps=records,original_spider_modified=False),indent=2)+'\n')
