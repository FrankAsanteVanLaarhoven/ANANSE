"""Check actual exported weights, indices, actions and sparse eyelid deltas."""
import json,math,struct,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'SourceArt/Characters/Kwaku'/(sys.argv[2] if len(sys.argv)>2 else 'Authored_v006');assert folder.parent==ROOT/'SourceArt/Characters/Kwaku' and folder.name in {'Authored_v006','Authored_v008','Authored_v015','Authored_v016'};raw=(folder/'Kwaku.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);at=20+n;size,kind=struct.unpack_from('<II',raw,at);assert kind==0x004E4942;binary=raw[at+8:at+8+size]
widths={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16};formats={5121:'B',5123:'H',5125:'I',5126:'f'}
def accessor(index):
 a=doc['accessors'][index];width=widths[a['type']];fmt=formats[a['componentType']];size=struct.calcsize(fmt);out=[[0]*width for _ in range(a['count'])]
 if 'bufferView'in a:
  v=doc['bufferViews'][a['bufferView']]
  for i in range(a['count']):out[i]=list(struct.unpack_from('<'+fmt*width,binary,v.get('byteOffset',0)+a.get('byteOffset',0)+i*v.get('byteStride',size*width)))
 if 'sparse'in a:
  q=a['sparse'];iv=doc['bufferViews'][q['indices']['bufferView']];vv=doc['bufferViews'][q['values']['bufferView']];iformat=formats[q['indices']['componentType']];last=-1
  for i in range(q['count']):
   j=struct.unpack_from('<'+iformat,binary,iv.get('byteOffset',0)+q['indices'].get('byteOffset',0)+i*struct.calcsize(iformat))[0];assert last<j<a['count'];last=j;out[j]=list(struct.unpack_from('<'+fmt*width,binary,vv.get('byteOffset',0)+q['values'].get('byteOffset',0)+i*width*size))
 if a.get('normalized')and fmt!='f':
  maximum={5121:255,5123:65535,5125:4294967295}[a['componentType']];out=[[v/maximum for v in row]for row in out]
 assert all(math.isfinite(v)for row in out for v in row);return out
assert len(doc['skins'])==1 and len(doc['skins'][0]['joints'])==46;assert len(doc['animations'])==11;assert len({a['name']for a in doc['animations']})==11;vertices=triangles=0;maximum=0;morphs={}
for mesh in doc['meshes']:
 for p in mesh['primitives']:
  attributes=p['attributes'];positions=accessor(attributes['POSITION']);normals=accessor(attributes['NORMAL']);weights=accessor(attributes['WEIGHTS_0']);joints=accessor(attributes['JOINTS_0']);uv=accessor(attributes['TEXCOORD_0']);assert len(positions)==len(normals)==len(weights)==len(joints)==len(uv)
  for w,j in zip(weights,joints):assert all(x>=0 for x in w)and abs(sum(w)-1)<1e-5 and all(0<=x<46 for x in j);maximum=max(maximum,sum(x>0 for x in w))
  indices=accessor(p['indices']);assert all(0<=i[0]<len(positions)for i in indices);vertices+=len(positions);triangles+=len(indices)//3
  for name,target in zip(mesh.get('extras',{}).get('targetNames',[]),p.get('targets',[])):
   delta=accessor(target['POSITION']);assert len(delta)==len(positions);morphs[name]=morphs.get(name,0)+sum(any(abs(v)>1e-7 for v in row)for row in delta)
assert maximum<=4 and set(morphs)=={'Blink_L','Blink_R'}and all(morphs.values());status=json.loads((folder/('Technical_v001/model-derived-evidence.json'if folder.name in {'Authored_v015','Authored_v016'}else'refinement-status.json')).read_text());assert status['rest_bones_unchanged']and hashlib.sha256((folder/'Kwaku.blend').read_bytes()).hexdigest()==status['scene_sha256'];out=Path(sys.argv[1]);assert not out.exists();out.write_text(json.dumps({'passed':True,'scene_sha256':status['scene_sha256'],'glb_sha256':hashlib.sha256(raw).hexdigest(),'rendered_export_vertices':vertices,'triangles':triangles,'maximum_positive_influences':maximum,'materialized_morph_deltas':morphs,'actions':len(doc['animations']),'joints':46,'creative_approved':False,'scope':'Actual binary data, not reference resemblance/limb clearance approval'},indent=2)+'\n');print('Actual GLB source integrity passed')
