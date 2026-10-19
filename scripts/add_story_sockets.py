"""Create real mapped native sockets on the new story families; preserve backups."""
import unreal,json,os,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];out=Path(os.environ['ANANSE_EVIDENCE_DIR']);out.mkdir(parents=True,exist_ok=True);records=[]
assert not(out/'result.json').exists()
for key in ['Kwaku','AsoYaa','EsiHuman','OseboHuman','KojoTortoise','KofiHornbill','EsiMoth']:
 p='/Game/Ananse/Characters/'+key+'/Story_v001/'+key;mesh=unreal.load_asset(p);assert isinstance(mesh,unreal.SkeletalMesh)
 before=ROOT/'Unreal/Content/Ananse/Characters'/key/'Story_v001'/(key+'.uasset');backup=out/'before-sockets'/key;backup.mkdir(parents=True,exist_ok=False);shutil.copy2(before,backup/before.name)
 if key!='Kwaku':
  error=unreal.AnanseAnimationAuthoring.add_story_sockets(mesh);assert error is not None and not error,str(error);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
 description=json.loads(unreal.AnanseAnimationAuthoring.describe_rig(mesh));assert len(description['socket_objects'])>=3
 record={'key':key,'native':description,'status':'actual_native_sockets_saved','continuation':'Kwaku mesh sockets already saved by prior attempt; prior checker only described skeleton sockets and its failure is preserved','source_units':'metres','native_units':'centimetres','grip_offsets_reviewed':False,'socket_origin_policy':'At the named actual bone origin; final prop-specific grip offsets and deformation remain art review','mesh_sha256':hashlib.sha256(before.read_bytes()).hexdigest()};records.append(record)
 target=ROOT/'SourceArt/Characters'/key/'NATIVE_RIG_MAP_20261015_v001.json';assert not target.exists();target.write_text(json.dumps(record,indent=2)+'\n')
(out/'result.json').write_text(json.dumps({'status':'passed_saved_sockets','designs':records,'existing_spider_and_leopard_changed':False},indent=2)+'\n')
