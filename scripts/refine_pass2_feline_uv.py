"""Correct the actual joined face/lid atlas and consistent fur texel density."""
import bpy,json,struct,hashlib,numpy as np,math,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];src=R/'SourceArt/Characters/OseboLeopard/Authored_v016';out=src.parent/'Authored_v017';assert not out.exists();out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(src/'OseboLeopard.blend'));mesh=bpy.data.objects['SK_OseboLeopard'];rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data.action=None;bpy.context.scene.frame_set(0);data=mesh.data;uv=data.uv_layers.active;W=1024;Y,X=np.mgrid[0:W,0:W];rng=np.random.default_rng(661);gold=np.array((.43,.235,.067));cream=np.array((.65,.55,.39));face=np.zeros((W,W,4),dtype=np.float32);face[:,:,:3]=gold;face[:,:,3]=1;u=X/(W-1);vv=Y/(W-1);front=u<.5;xx=((u-.02)/.46-.5)*.28;zz=(vv-.02)/.96*.30+1.75;mask=np.exp(-(xx/.089)**4-((zz-1.832)/.037)**4)*front;face[:,:,:3]=gold[None,None,:]*(1-mask[:,:,None])+cream[None,None,:]*mask[:,:,None]
def spots(arr,count,low,high,mask=None):
 for n in range(count):
  a,b=rng.uniform(0,W,2);rx=rng.uniform(low,high);ry=rx*rng.uniform(.7,1.25);x0,x1=max(0,int(a-rx*1.2)),min(W,int(a+rx*1.2+1));y0,y1=max(0,int(b-ry*1.2)),min(W,int(b+ry*1.2+1));dx=(X[y0:y1,x0:x1]-a)/rx;dy=(Y[y0:y1,x0:x1]-b)/ry;angle=np.arctan2(dy,dx);r=np.sqrt(dx*dx+dy*dy);hit=(r>.56)&(r<1+.12*np.sin(angle*3+n))&(np.sin(angle*2.1+n)>-.6)
  if mask is not None:hit&=mask[y0:y1,x0:x1]<.3
  arr[y0:y1,x0:x1,:3][hit]=(.045,.021,.008)
spots(face,95,9,19,mask)
# Sparse original whisker-root dots on the pale muzzle.
for sign in [-1,1]:
 for n in range(3):
  px=sign*(.032+n*.015);pz=1.83+(n%2)*.009;cx=(.02+.46*(px/.28+.5))*(W-1);cy=(.02+.96*(pz-1.75)/.30)*(W-1);face[((X-cx)/3)**2+((Y-cy)/4)**2<1,:3]=(.075,.038,.015)
body=np.zeros((W,W,4),dtype=np.float32);body[:,:,:3]=gold;body[:,:,3]=1;body[:,:,:3]*=(1+rng.normal(0,.02,(W,W,1)));spots(body,720,9,18)
for name,arr in [('FelineFaceSurface',face),('Fur_Gold_Rosettes',body)]:
 image=bpy.data.images.new(name+'_Pass2_Atlas',W,W);image.pixels.foreach_set(arr.ravel());image.filepath_raw=str(out/(name+'_BaseColor.png'));image.file_format='PNG';image.save();image.pack();material=bpy.data.materials[name];nodes=material.node_tree.nodes;nodes.clear();output=nodes.new('ShaderNodeOutputMaterial');p=nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Roughness'].default_value=.76;p.inputs['Specular IOR Level'].default_value=.25;tex=nodes.new('ShaderNodeTexImage');tex.image=image;material.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);material.node_tree.links.new(p.outputs['BSDF'],output.inputs['Surface'])
for p in data.polygons:
 name=data.materials[p.material_index].name
 if name=='FelineFaceSurface':
  front=sum(data.vertices[i].co.y for i in p.vertices)<0
  for li in p.loop_indices:
   q=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=((.02 if front else .52)+.46*(q.x/.28+.5),.02+.96*(q.z-1.75)/.30)
 elif name=='Fur_Gold_Rosettes':
  normal=p.normal;axis=max(range(3),key=lambda i:abs(normal[i]));axes=[i for i in range(3)if i!=axis]
  for li in p.loop_indices:q=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]]*.8+.5,q[axes[1]]*.8)
for file in ['Armour_Brown_Leather_BaseColor.png','Cape_Burgundy_BaseColor.png']:
 if(src/file).exists():shutil.copyfile(src/file,out/file)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'OseboLeopard.blend'));bpy.ops.object.select_all(action='DESELECT');mesh.hide_set(False);mesh.select_set(True);rig.select_set(True);bpy.ops.export_scene.gltf(filepath=str(out/'OseboLeopard.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_yup=True,export_morph=True)
p=out/'OseboLeopard.glb';raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);d['asset'].pop('generator',None);head=json.dumps(d,separators=(',',':')).encode();head+=b' '*((-len(head))%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(head)+len(tail))+struct.pack('<II',len(head),0x4e4f534a)+head+tail);r=json.loads((src/'art-pass2.json').read_text());r.update(scene_sha256=hashlib.sha256((out/'OseboLeopard.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),uv_correction='Explicit front/rear face/lid atlas, position-matched cream mask/whisker roots; baked body world-scale box projection, no runtime triplanar shader',creative_approved=False);(out/'art-pass2.json').write_text(json.dumps(r,indent=2)+'\n');print('FELINE_ATLAS_REPAIRED')
