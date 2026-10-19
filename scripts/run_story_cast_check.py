"""Supervise real rendered all-cast qualification; reject partial/stale/empty evidence."""
import argparse,json,os,subprocess,time,hashlib,sys,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.native_runtime_smoke import build_input_identity
from scripts.aso_yaa_contract import validate_ledger_observation
KEYS={'kwaku-human-v1':'Kwaku','aso-yaa-human-v1':'AsoYaa','esi-human-v1':'EsiHuman','osebo-human-v1':'OseboHuman','kojo-tortoise-v1':'KojoTortoise','kofi-hornbill-v1':'KofiHornbill','esi-moth-v1':'EsiMoth'}
def finite_at_least(value, minimum):
 return type(value) in (int,float) and math.isfinite(value) and value>=minimum

def validate_neutral_lighting(report):
 lights=report.get('neutral_review_lights',[])
 return (report.get('neutral_review_enabled')is True and len(lights)==2
  and all(l.get('intensity_lumens')==3000 and l.get('uses_lumens_units')is True and l.get('channel0')is True and l.get('channel1')is False for l in lights)
  and bool(report.get('designs')) and all(d.get('character_review_light_components')==0 for d in report['designs']))

def validate(report,code,art_refinement=False,expected_publication=None,forms_scenery=False,interaction_refinement=False,visual_review=False,art_pass2=False,aso_contact=False,neutral_lighting=False):
 art_refinement=art_refinement or forms_scenery or interaction_refinement
 if neutral_lighting and not validate_neutral_lighting(report):return False
 if expected_publication and report.get('loaded_publication_hash')!=expected_publication:return False
 if report.get('material_fallback_warnings'):return False
 if code!=0 or report.get('passed') is not True or not finite_at_least(report.get('seconds'),60):return False
 designs=report.get('designs',[])
 if len(designs)!=7 or {d.get('design') for d in designs}!=set(KEYS):return False
 for d in designs:
  key=KEYS[d['design']];base='/Game/Ananse/Characters/'+key+'/Story_v001/'
  visual='/Game/Ananse/Characters/Kwaku/ArtPass2_v003/'if art_pass2 and key=='Kwaku'else'/Game/Ananse/Characters/Kwaku/Visual_v003/'if visual_review and key=='Kwaku'else'/Game/Ananse/Characters/Kwaku/Interactions_v005/'if interaction_refinement and key=='Kwaku'else'/Game/Ananse/Characters/Kwaku/Refined_v002/'if forms_scenery and key=='Kwaku'else'/Game/Ananse/Characters/Kwaku/Refined_v001/'if art_refinement and key=='Kwaku'else base
  if aso_contact and key=='AsoYaa':
   base=visual='/Game/Ananse/Characters/AsoYaa/Contact_v002/'
   if d.get('definition_revision')!=5 or d.get('skeleton')!=base+'AsoYaa_Skeleton.AsoYaa_Skeleton' or not validate_ledger_observation(d) or d.get('refined_face_bindings')is not True or not finite_at_least(d.get('applied_blink_peak'),.75):return False
   if len(d.get('clips',[]))!=16 or any(not c.get('clip','').startswith(base)for c in d.get('clips',[])):return False
  if d.get('mesh')!=visual+key+'.'+key or d.get('pawn_class')!=visual+'BP_'+key+'.BP_'+key+'_C' or d.get('animation_instance')!=base+'ABP_'+key+'.ABP_'+key+'_C':return False
  if art_refinement and key=='Kwaku'and(d.get('refined_face_bindings')is not True or d.get('applied_blink_peak',0)<.75 or d.get('definition_revision')!=(11 if art_pass2 else 8 if visual_review else 5 if interaction_refinement else 3 if forms_scenery else 2) or d.get('published_visual_revision')!=(5 if interaction_refinement else 3 if forms_scenery else 2)):return False
  if interaction_refinement and key=='Kwaku'and(d.get('separate_ledger_attached_observed')is not True or d.get('ledger_reset_cleared')is not True or not any(c.get('separate_ledger_attached_observed')is True and c.get('ledger_reset_cleared')is True and c.get('clip','').startswith('/Game/Ananse/Characters/Kwaku/Visual_v003/'if visual_review else'/Game/Ananse/Characters/Kwaku/Interactions_v003/')for c in d.get('clips',[]))):return False
  if d.get('complete_round_trips')!=20 or not finite_at_least(d.get('movement_cm'),10) or not finite_at_least(d.get('bones'),40):return False
  if key!='EsiMoth':
   try:metrics=json.loads(d['flat_contact_metrics'])
   except (KeyError,ValueError,TypeError):return False
   legs=metrics.get('legs',[])
   if len(legs)!=2 or metrics.get('invalid_transforms')!=0 or metrics.get('solved_chains')!=2:return False
   for leg in legs:
    if not finite_at_least(leg.get('samples'),50) or not 0<=leg.get('p95_stance_drift_cm',-1)<=2 or not 0<=leg.get('max_penetration_cm',-1)<=.5 or not finite_at_least(leg.get('max_segment_length_error_cm'),0) or leg.get('max_segment_length_error_cm',1)>.1:return False
  clips=d.get('clips',[])
  if len(clips)<8 or len({c.get('clip')for c in clips})!=len(clips) or any(c.get('graph_and_pose_observed')is not True for c in clips):return False
 return True
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--neutral-lighting',action='store_true');p.add_argument('--aso-contact',action='store_true');p.add_argument('--art-pass2',action='store_true');p.add_argument('--visual-review',action='store_true');p.add_argument('--interaction-refinement',action='store_true');p.add_argument('--out',type=Path,required=True);p.add_argument('--executable',type=Path);p.add_argument('--map',default='/Game/Characters/AnanseSpider/Lab_v001/L_AnanseCharacterLab');p.add_argument('--build-identity',type=Path);p.add_argument('--full-clips',action='store_true');p.add_argument('--forms-scenery',action='store_true');p.add_argument('--art-refinement',action='store_true');p.add_argument('--restore-original',action='store_true');p.add_argument('--portrait',action='store_true');a=p.parse_args();
 if a.aso_contact and not a.full_clips:p.error('--aso-contact requires --full-clips for complete ledger phases')
 out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
 exe=a.executable.resolve() if a.executable else Path('/home/favl/Unreal/UE_5.8.3-58210709/Engine/Binaries/Linux/UnrealEditor');file=out/'result.json'
 cmd=[str(exe)]+([]if a.executable else[str(ROOT/'Unreal/Ananse.uproject'),'-game'])+[a.map,'-ansimalloc','-windowed','-ResX=1280','-ResY=720','-unattended','-nosplash','-NoScreenMessages',f'-UserDir={out/"profile"}',f'-AnanseStoryCastVerify={file}','-trace=frame',f'-tracefile={out/"frames.utrace"}']
 if a.neutral_lighting:cmd.append('-AnanseNeutralLabLighting')
 if a.aso_contact:cmd+=['-AnanseAsoContact','-AnanseAsoReview']
 if a.art_pass2:cmd.append('-AnanseArtPass2')
 if a.visual_review:cmd.append('-AnanseVisualReview')
 if a.full_clips:cmd.append('-AnanseStoryFullClips')
 if a.art_refinement or a.forms_scenery or a.interaction_refinement:cmd.append('-AnanseArtRefinement')
 if a.forms_scenery:cmd.append('-AnanseFormsScenery')
 if a.interaction_refinement:cmd.append('-AnanseInteractionRefinement')
 if a.portrait:cmd.append('-AnanseArtPortrait')
 inputs=json.loads(a.build_identity.read_text())if a.build_identity else build_input_identity();catalogue=ROOT/'Unreal/Content/Data/catalogue.json';assert hashlib.sha256(catalogue.read_bytes()).hexdigest()==inputs['files']['Unreal/Content/Data/catalogue.json'],'Cook identity/catalogue mismatch';publication=json.loads(catalogue.read_text())['sha256'];digest=hashlib.file_digest(exe.open('rb'),'sha256').hexdigest();(out/'command.json').write_text(json.dumps({'command':cmd,'inputs':inputs,'executable_sha256':digest,'expected_publication_hash':publication},indent=2)+'\n')
 env=os.environ.copy();env.pop('PYTHONPATH',None);env.pop('LD_LIBRARY_PATH',None);forced=False;started=time.monotonic()
 with(out/'runtime.log').open('w')as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT);(out/'launch.json').write_text(json.dumps({'pid':proc.pid,'command':cmd},indent=2)+'\n')
  try:code=proc.wait(timeout=660 if a.full_clips else 240)
  except subprocess.TimeoutExpired:
   forced=True;proc.terminate()
   try:code=proc.wait(timeout=15)
   except subprocess.TimeoutExpired:proc.kill();code=proc.wait()
 d=json.loads(file.read_text(encoding='utf-8-sig'))if file.exists()else{};d['material_fallback_warnings']=[line for line in (out/'runtime.log').read_text(errors='replace').splitlines()if 'missing usage flag'in line.lower()or'Failed to find shader map for default material'in line];(out/'material-audit.json').write_text(json.dumps({'warnings':d['material_fallback_warnings'],'passed':not d['material_fallback_warnings']},indent=2)+'\n');ok=not forced and validate(d,code,(a.art_refinement or a.forms_scenery or a.interaction_refinement) and not a.restore_original,publication,a.forms_scenery,a.interaction_refinement,a.visual_review,a.art_pass2,a.aso_contact,a.neutral_lighting)and (not a.full_clips or d.get('complete_clip_cycles')is True)and d.get('world')==a.map+'.'+a.map.rsplit('/',1)[-1]and all((out/f'cast_{i}.png').is_file()for i in range(7))and(out/'frames.utrace').is_file()
 result={'accepted':ok,'exit_code':code,'forced':forced,'wall_seconds':time.monotonic()-started,'scope':'rendered technical cast/selection/pose; not final art,terrain,mobile or campaign mapping approval'};(out/'process.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));sys.exit(0 if ok else 1)
