"""Reject incomplete/mismatched final-pose coverage and any observed intersection."""
import argparse,json,math
from pathlib import Path

def validate(folder,art_refine=False):
 d=json.loads((folder/'clearance-final.json').read_text());rows=d['samples'];expected={'WalkControlled':12,'Turn':12,'InspectEvidence':32,'LimbIsolation':24};coverage={k:sum(k in r['clip']for r in rows)for k in expected};assert coverage==expected,(coverage,expected);assert len(rows)==80
 for r in rows:
  m=json.loads((folder/Path(r['file']).with_suffix('.json')).read_text());base='/Game/Ananse/Characters/AsoYaa/Clearance_v001/'
  assert m['mesh']==('/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/'if art_refine else base)+'AsoYaa.AsoYaa'and m['skeleton']==base+'AsoYaa_Skeleton.AsoYaa_Skeleton'and m['animation_instance']==base+'ABP_AsoYaa.ABP_AsoYaa_C'
  assert r['body_triangles']>0 and r['garment_triangles']>0 and r['maximum_source_mapping_error_cm']<.01
  assert math.isfinite(r['minimum_unsigned_surface_distance_cm']) and r['minimum_unsigned_surface_distance_cm']>=0
 bad=[r for r in rows if r['triangle_intersection_pairs']!=0]
 result={'status':'FAIL'if bad else'assertions_passed','samples':len(rows),'coverage':coverage,'intersecting_samples':len(bad),'maximum_intersection_pairs':max(r['triangle_intersection_pairs']for r in rows),'minimum_unsigned_separation_cm':min(r['minimum_unsigned_surface_distance_cm']for r in rows),'maximum_source_correspondence_error_cm':max(r['maximum_source_mapping_error_cm']for r in rows),'predicted_render_lods':sorted({r['predicted_render_lod']for r in rows}),'exclusions':'Body surface restZ18..90cm, garment restZ16..110cm; no feet/upper torso/morph-only face coverage.4Hz captured poses, not every intermediate rendered frame. Unsigned separation is not penetration depth or an inside/outside certificate. Human visual review remains required.'};(folder/'clearance-validation.json').write_text(json.dumps(result,indent=2)+'\n');assert not bad,result;return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('--art-refine',action='store_true');a=p.parse_args();print(json.dumps(validate(a.folder,a.art_refine),indent=2))
