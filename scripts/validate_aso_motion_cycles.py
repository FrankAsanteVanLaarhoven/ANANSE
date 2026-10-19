"""Validate actual finalized support phases, not the number of input requests."""
import argparse,json,math
from pathlib import Path

def validate(folder,art_refine=False):
 p=json.loads((folder/'process.json').read_text());rows=[json.loads(line)for line in(folder/'support.jsonl').read_text().splitlines()];assert p['exit_code']==0 and not p['forced'] and p['mode']=='cycles';assert len(rows)>=100
 assert all(r['supported_sample']is True for r in rows),'Unsupported or invalid evaluated support sample'
 expected=('/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/'if art_refine else'/Game/Ananse/Characters/AsoYaa/Clearance_v001/')+'AsoYaaInspectEvidence.AsoYaaInspectEvidence';inspect=[r for r in rows if r['clip']==expected];groups={}
 for row in inspect:groups.setdefault((row['actor'],row['epoch']),[]).append(row)
 ordered=sorted(groups.values(),key=lambda g:g[0]['monotonic_seconds'])
 def complete(g):return min(r['evaluated_time']for r in g)<=.15 and max(r['evaluated_time']for r in g)>=7.90 and all(any(r['support_state']==phase for r in g)for phase in ['table','both_hands'])
 assert len(ordered)>=10 and all(complete(g)for g in ordered[:10]),'First ten actual interaction epochs must complete reach/hold/placement/release'
 events=p['events'];assert sum('cycle_requested'in e for e in events)==10
 cuts=[e for e in events if e.get('key')=='1'];assert len(cuts)==2
 cut_checks=[]
 for event in cuts:
  after=[r for r in rows if event['monotonic_seconds']+.05<=r['monotonic_seconds']<=event['monotonic_seconds']+.35];assert after and all(r['support_state']=='presentation_stowed'and not r['prop_visible']for r in after);cut_checks.append({'event_monotonic':event['monotonic_seconds'],'stowed_samples':len(after)})
 pauses=[e for e in events if e.get('key')=='p'];assert len(pauses)==2
 before=max((r for r in rows if r['monotonic_seconds']<pauses[0]['monotonic_seconds']),key=lambda r:r['monotonic_seconds']);after=min((r for r in rows if r['monotonic_seconds']>pauses[1]['monotonic_seconds']+.02),key=lambda r:r['monotonic_seconds']);clock_delta=after['evaluated_time']-before['evaluated_time'];assert before['epoch']==after['epoch'] and -.01<=clock_delta<=.15,'Pause advanced or reset the held clip clock'
 assert complete(ordered[-1]),'Final re-entry must finish'
 held=[r for r in rows if r['support_state']=='both_hands'];placed=[r for r in rows if r['support_state']=='table'];assert held and placed
 result={'status':'assertions_passed','executed_checks':8,'evaluated_support_samples':len(rows),'unsupported_samples':0,'first_ten_complete_cycles':10,'total_complete_epochs':sum(complete(g)for g in ordered),'cancel_and_presentation_cut_checks':cut_checks,'pause_resume_clip_clock_delta_seconds':clock_delta,'final_reentry_completed':True,'max_left_contact_vertex_distance_cm':max(r['left_contact_vertex_distance_cm']for r in held),'max_right_contact_vertex_distance_cm':max(r['right_contact_vertex_distance_cm']for r in held),'max_marker_rest_error_cm':max(r['marker_rest_error_cm']for r in held),'max_absolute_table_gap_cm':max(abs(r['table_vertical_gap_cm'])for r in placed),'thresholds':{'mapped_surface_vertex_correspondence_cm':.01,'held_contact_vertex_distance_cm':.5,'table_bbox_vertical_gap_cm':.2},'coverage':'Six actual finalized LOD0 hand/digit vertices, three per hand, independently mapped from source rest positions; distance to actual imported rectangular book bounds. Table bounds aligned to authored flat top. Does not approve all hand anatomy, all possible prop penetration, cinematic skip or creative naturalness.'};(folder/'support-validation.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('--art-refine',action='store_true');a=p.parse_args();print(json.dumps(validate(a.folder,a.art_refine),indent=2))
