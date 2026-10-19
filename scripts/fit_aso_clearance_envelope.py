"""Propose garment profiles from actual final native skin matrices and surfaces."""
import json,struct,hashlib
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];E=R/'.local/verification/aso-motion-correction-20261018';folder=E/'evaluated-skin-matrices/surfaces';old=E/'evaluated-weights-enabled/surfaces';labels=json.loads((old/'vertex-part-map.json').read_text())['parts'];files=sorted(p for p in folder.glob('*.bin')if p.name!='indices.bin'and p.with_suffix('.json').exists());assert len(files)>=75,'Wait for complete captured pose coverage';files=[p for p in files if 'LimbIsolation' not in p.name];clouds=[];f=1.68/1.7
profiles={'cream':[[.09,.25,.14],[.25,.24,.14],[.50,.22,.13],[.80,.18,.12],[1.02,.163,.116],[1.20,.18,.12],[1.31,.202,.125],[1.37,.17,.095],[1.40,.065,.058]],'blue':[[.17,.285,.16],[.30,.275,.155],[.55,.245,.15],[.80,.205,.137],[1.02,.175,.13],[1.20,.19,.133],[1.32,.212,.14],[1.37,.18,.105],[1.40,.070,.065]]}
for file in files:
 pairs=np.array(list(struct.iter_unpack('<6f',file.read_bytes()[4:])));meta=json.loads(file.with_suffix('.json').read_text());mats={k:np.array(v).reshape(4,4)for k,v in meta['final_ref_to_local_skin_matrices_row_major'].items()};assert all(np.isfinite(m).all()for m in mats.values())
 for side in ['L','R']:
  ii=np.array([i for i,label in enumerate(labels)if label=='Leg_'+side and 18<pairs[i,2]<90]);p=np.c_[pairs[ii,3:],np.ones(len(ii))]
  for rings in profiles.values():
   rings=np.array(rings);lower=np.clip((.98-rings[:,0])/.38,0,1);chest=np.clip((rings[:,0]-1.04)/.27,0,1);q=pairs[ii,:3].copy()
   for iteration in range(12):
    z=q[:,2]/100;lo=np.interp(z,rings[:,0]*f,lower);hi=np.interp(z,rings[:,0]*f,chest);w=(1-lo)*(1-hi);m=w[:,None,None]*mats['pelvis']+hi[:,None,None]*mats['chest']+lo[:,None,None]*mats['Dress_'+side];q=np.einsum('ni,nij->nj',p,np.linalg.inv(m))[:,:3]
   assert np.isfinite(q).all();clouds.extend(q.tolist())
points=np.array(clouds)/100;cream=np.array(profiles['cream'])*f;rows=[];margin=.03
for z in np.arange(.1,1.151,.025):
 width=float(np.interp(z,cream[:,0],cream[:,1]));depth=float(np.interp(z,cream[:,0],cream[:,2]));near=points[np.abs(points[:,2]-z)<.075];best=None
 if len(near):
  for a in np.arange(max(width,float(np.max(np.abs(near[:,1])))+margin+.001),.501,.0025):
   b=max(depth,float(np.max((np.abs(near[:,0])+margin)/np.sqrt(np.maximum(1e-8,1-((np.abs(near[:,1])+margin)/a)**2)))))
   if b>.5:continue
   cost=a*b*(1+.7*(a/width-1)**2)
   if best is None or cost<best[0]:best=(cost,a,b)
  assert best is not None,(z,'No bounded profile; retain failure')
  width,depth=best[1:]
 rows.append({'z_m':float(z),'width_radius_m':width,'depth_radius_m':depth,'surface_points_in_overlapping_band':len(near)})
for i in range(len(rows)-2,-1,-1):
 for key in ['width_radius_m','depth_radius_m']:rows[i][key]=max(rows[i][key],rows[i+1][key])
report={'status':'fitted_proposal_not_runtime_acceptance','native_pose_files':len(files),'sampled_native_surface_points':len(points),'source_mesh':'/Game/Ananse/Characters/AsoYaa/Clearance_v001/AsoYaa.AsoYaa','source_scene':'SourceArt/Characters/AsoYaa/Authored_v023/AsoYaa.blend','source_scene_sha256':hashlib.sha256((R/'SourceArt/Characters/AsoYaa/Authored_v023/AsoYaa.blend').read_bytes()).hexdigest(),'method':'Actual final native ref-to-local skin matrices and leg surface vertices. Iterative inverse mapping through each original garment ring-weight field. Minimum-area ellipses,3cm fitting margin, overlapping7.5cm height bands and monotone A-line. This proposal is not the acceptance measurement: direct native evaluated triangle tests remain mandatory.','profile':rows,'fit_exclusions':['Extreme LimbIsolation is not included in the proposal fit; it must still be measured and any failure retained. No family gate is waived.'],'creative':'REVIEW_REQUIRED'};(E/'fitted-clearance-envelope.json').write_text(json.dumps(report,indent=2)+'\n');print('FITTED_ENVELOPE',len(files),len(rows),max(r['width_radius_m']for r in rows),max(r['depth_radius_m']for r in rows))
