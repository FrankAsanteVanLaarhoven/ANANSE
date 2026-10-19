"""Inspect materialised GLB accessors, actual weights, scene hashes and distinct actions."""
import json,hashlib,struct,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def inspect(key):
 folder=ROOT/'SourceArt/Characters'/key/('Authored_v002'if key=='Kwaku'else'Authored_v001');status=json.loads((folder/'rig-map.json').read_text());raw=(folder/(key+'.glb')).read_bytes();assert hashlib.sha256(raw).hexdigest()==status['glb_sha256'];assert hashlib.sha256((folder/(key+'.blend')).read_bytes()).hexdigest()==status['scene_sha256'];assert raw[:4]==b'glTF';n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);binary=raw[28+n:];assert 'generator'not in doc['asset'];assert len(doc['skins'])==1 and len(doc['skins'][0]['joints'])==len(status['bones']);assert len(doc.get('animations',[]))==len(status['actions']);assert len({a['name']for a in doc['animations']})==len(status['actions'])
 def acc(index):
  a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];size={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];fmt={5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']];bytes=struct.calcsize(fmt);stride=v.get('byteStride',size*bytes);offset=v.get('byteOffset',0)+a.get('byteOffset',0)
  return [struct.unpack_from('<'+fmt*size,binary,offset+i*stride)for i in range(a['count'])]
 vertices=0;max_influences=0;triangles=0
 for mesh in doc['meshes']:
  for primitive in mesh['primitives']:
   attrs=primitive['attributes'];positions=acc(attrs['POSITION']);weights=acc(attrs['WEIGHTS_0']);joints=acc(attrs['JOINTS_0']);assert len(weights)==len(positions)==len(joints)
   for position,row,indices in zip(positions,weights,joints):
    assert all(math.isfinite(v)for v in position+row);assert all(w>=0 for w in row);assert abs(sum(row)-1)<.0001;assert all(j<len(status['bones'])for j,w in zip(indices,row)if w>0);max_influences=max(max_influences,sum(w>0 for w in row))
   vertices+=len(positions);triangles+=len(acc(primitive['indices']))//3
 assert 0<max_influences<=4
 views=folder/'Technical_v001';view=json.loads((views/'view-provenance.json').read_text());assert view['source_scene_sha256']==status['scene_sha256'];assert (views/'turntable.mp4').stat().st_size>0
 return {'key':key,'scene_sha256':status['scene_sha256'],'glb_sha256':status['glb_sha256'],'render_vertices_including_material_splits':vertices,'triangles':triangles,'bones':len(status['bones']),'actual_distinct_actions':len(status['actions']),'maximum_positive_influences':max_influences,'unweighted_vertices':0,'finite_normalised_weights':True,'model_derived_technical_views':True,'creative_approved':False}
if __name__=='__main__':
 out=Path(sys.argv[1]);assert not out.exists();results=[inspect(k)for k in ['Kwaku','AsoYaa','EsiHuman','OseboHuman','KojoTortoise','KofiHornbill','EsiMoth']];out.write_text(json.dumps({'status':'passed_source_integrity_not_art_acceptance','designs':results},indent=2)+'\n');print('7 actual source mesh/skin/action/view checks passed')
