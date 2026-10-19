"""Original tileable earth/plaster/wood maps; no downloaded imagery."""
import bpy,numpy as np,json,hashlib,sys
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'SourceArt/Environments/MarketSanctuary/Refinement_v002'
assert not out.exists();out.mkdir(parents=True);size=512;rng=np.random.default_rng(20261015);yy,xx=np.mgrid[0:size,0:size];u=xx/size;v=yy/size

def noise(cells):
 grid=rng.random((cells,cells));x=u*cells;y=v*cells;ix=x.astype(int);iy=y.astype(int);fx=x-ix;fy=y-iy;fx=fx*fx*(3-2*fx);fy=fy*fy*(3-2*fy)
 return (grid[iy%cells,ix%cells]*(1-fx)+grid[iy%cells,(ix+1)%cells]*fx)*(1-fy)+(grid[(iy+1)%cells,ix%cells]*(1-fx)+grid[(iy+1)%cells,(ix+1)%cells]*fx)*fy
records=[]
for name,base in [('MarketEarth',(.27,.135,.055)),('ForestEarth',(.062,.085,.033)),('WarmPlaster',(.54,.37,.21)),('WeatheredWood',(.15,.063,.023))]:
 n=.5*noise(8)+.25*noise(32)+.15*noise(64)+.10*noise(128)
 if name=='WeatheredWood':n=.35*n+.65*(.5+.5*np.sin(2*np.pi*(u*32+.25*np.sin(v*2*np.pi)+n*.8)))
 height=n;grain=rng.uniform(.92,1.08,(size,size));rgb=np.clip((.68+.50*n)[...,None]*grain[...,None]*np.array(base),0,1);dx=(np.roll(height,-1,1)-np.roll(height,1,1))*1.8;dy=(np.roll(height,-1,0)-np.roll(height,1,0))*1.8;normal=np.stack((-dx,-dy,np.ones_like(dx)),2);normal/=np.linalg.norm(normal,axis=2)[...,None];normal=normal*.5+.5
 for suffix,pixels,linear in [('Albedo',rgb,False),('Normal',normal,True)]:
  image=bpy.data.images.new(name+suffix,width=size,height=size,alpha=True);image.colorspace_settings.name='Non-Color'if linear else'sRGB';image.pixels.foreach_set(np.dstack((pixels,np.ones((size,size)))).astype(np.float32).ravel());path=out/(name+'_'+suffix+'.png');image.filepath_raw=str(path);image.file_format='PNG';image.save();records.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'colour_space':'linear'if linear else'sRGB'})
(out/'surface-status.json').write_text(json.dumps({'source_creator':'Frank Asante Van Laarhoven','method':'Original deterministic periodic noise/wood grain and height-derived normals','seed':20261015,'pixels':[size,size],'maps':records,'creative_approved':False,'licence':'Original locally authored texture maps; project rights review pending'},indent=2)+'\n')
