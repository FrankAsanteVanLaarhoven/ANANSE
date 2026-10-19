"""Run the existing rendered cast harness in Aso-only mode and validate exact bindings."""
import argparse,json,hashlib,os,subprocess,time,sys,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from scripts.native_runtime_smoke import build_input_identity
from scripts.aso_yaa_contract import validate_ledger_observation
from scripts.run_story_cast_check import validate_neutral_lighting
BASE='/Game/Ananse/Characters/AsoYaa/Negotiation_v002/'
def validate(d,code,base,publication,restored=False,contact=False,neutral_lighting=False,clearance=False,art_refine=False):
 if neutral_lighting and not validate_neutral_lighting(d):return False
 expected_base="/Game/Ananse/Characters/AsoYaa/Story_v001/"if restored else '/Game/Ananse/Characters/AsoYaa/Contact_v002/'if contact else BASE
 if clearance:expected_base="/Game/Ananse/Characters/AsoYaa/Clearance_v001/"
 skeleton_base=expected_base
 if art_refine:expected_base="/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/"
 count=8 if restored else 16
 revision=8 if art_refine else 6 if clearance else 1 if restored else 5 if contact else 3
 try:
  if code!=0 or d['passed']is not True or d['seconds']<60 or d['loaded_publication_hash']!=publication or d['round_trip_base']!=base or d['complete_clip_cycles']is not True:return False
  rows=d['designs']
  if len(rows)!=1:return False
  a=rows[0]
  if a['design']!='aso-yaa-human-v1'or a['mesh']!=expected_base+'AsoYaa.AsoYaa'or a['pawn_class']!=expected_base+'BP_AsoYaa.BP_AsoYaa_C'or a['animation_instance']!=skeleton_base+'ABP_AsoYaa.ABP_AsoYaa_C'or a['skeleton']!=skeleton_base+'AsoYaa_Skeleton.AsoYaa_Skeleton'or a['definition_revision']!=revision or a['bones']!=48:return False
  if a['complete_round_trips']!=20 or a['movement_cm']<10 or(not restored and(a['refined_face_bindings']is not True or a['applied_blink_peak']<.75)):return False
  native=R/('.local/verification/aso-motion-correction-20261018/import/AsoYaa-native.json'if clearance else'.local/verification/aso-corrective-20261016/native-02/AsoYaa-native.json'if contact else'.local/verification/story-cast-20261015/native-AsoYaa/AsoYaa-native.json'if restored else'.local/verification/aso-yaa-20261016/native-02/AsoYaa-native.json');expected=set(json.loads(native.read_text())['clips'].values());clips=a['clips']
  if art_refine:expected.remove('/Game/Ananse/Characters/AsoYaa/Clearance_v001/AsoYaaInspectEvidence.AsoYaaInspectEvidence');expected.add('/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/AsoYaaInspectEvidence.AsoYaaInspectEvidence')
  if len(clips)!=count or{c['clip']for c in clips}!=expected or any(c['graph_and_pose_observed']is not True for c in clips):return False
  if contact and not validate_ledger_observation(a):return False
  m=json.loads(a['flat_contact_metrics'])
  if m['invalid_transforms']!=0 or m['solved_chains']!=2 or len(m['legs'])!=2:return False
  for leg in m['legs']:
   if leg['samples']<50:return False
   for field,limit in [('p95_stance_drift_cm',2),('max_penetration_cm',.5),('max_segment_length_error_cm',.1)]:
    value=leg[field]
    if not isinstance(value,(int,float))or not math.isfinite(value)or not 0<=value<=limit:return False
  return True
 except(KeyError,TypeError,ValueError):return False
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--surface-capture',type=Path);p.add_argument('--support-audit',type=Path);p.add_argument('--disable-secondary-motion',action='store_true');p.add_argument('--art-refine',action='store_true');p.add_argument('--clearance',action='store_true');p.add_argument('--neutral-lighting',action='store_true');p.add_argument('--contact',action='store_true');p.add_argument('--portrait',action='store_true');p.add_argument('--profile-dir',type=Path);p.add_argument('--restore-profile',action='store_true');p.add_argument('--restore-original',action='store_true');p.add_argument('--out',type=Path,required=True);p.add_argument('--executable',type=Path);p.add_argument('--base',choices=['spider','kwaku','leopard'],default='spider');p.add_argument('--build-identity',type=Path);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);file=out/'result.json';exe=a.executable or Path('/home/favl/Unreal/UE_5.8.3-58210709/Engine/Binaries/Linux/UnrealEditor');base={'spider':'ananse-spider-existing','kwaku':'kwaku-human-v1','leopard':'osebo-leopard-v1'}[a.base]
 cmd=[str(exe)]+([]if a.executable else[str(R/'Unreal/Ananse.uproject')])+['/Game/Ananse/Maps/Negotiation_v002/L_AsoYaaCharacterLab']+([]if a.executable else['-game'])+['-ansimalloc','-windowed','-ResX=1280','-ResY=720','-unattended','-nosplash','-NoScreenMessages','-AnanseAsoCapture','-AnanseAsoReview','-AnanseAsoOnly','-AnanseStoryFullClips','-AnanseArtPass2','-AnanseVisualReview','-AnanseArtRefinement',f'-AnanseStoryCastVerify={file}',f'-UserDir={a.profile_dir.resolve()if a.profile_dir else out/"profile"}','-trace=frame',f'-tracefile={out/"frames.utrace"}']
 if a.contact:
  cmd=[v.replace('/Game/Ananse/Maps/Negotiation_v002/','/Game/Ananse/Maps/Contact_v002/')for v in cmd];cmd.append('-AnanseAsoContact')
 if a.clearance:
  assert a.contact and not a.restore_original
  cmd=[v.replace('/Game/Ananse/Maps/Contact_v002/','/Game/Ananse/Maps/Clearance_v001/')for v in cmd];cmd.append('-AnanseAsoClearance')
 if a.art_refine:
  assert a.clearance
  cmd=[v.replace('/Game/Ananse/Maps/Clearance_v001/','/Game/Ananse/Maps/ArtRefine_v002/')for v in cmd];cmd.append('-AnanseAsoArtRefine')
 if a.surface_capture:
  assert not a.surface_capture.exists();cmd.append('-AnanseAsoSurfaceCapture='+str(a.surface_capture.resolve()))
 if a.support_audit:
  assert not a.support_audit.exists();cmd.append('-AnanseAsoSupportAudit='+str(a.support_audit.resolve()))
 if a.disable_secondary_motion:cmd.append('-AnanseDisableSecondaryMotion')
 if a.portrait:cmd.append('-AnanseArtPortrait')
 if a.neutral_lighting:cmd.append('-AnanseNeutralLabLighting')
 if a.restore_profile:cmd.append('-AnanseAsoRestoreProfile')
 if a.base=='kwaku':cmd.append('-AnanseAsoWithKwaku')
 if a.base=='leopard':cmd.append('-AnanseAsoWithLeopard')
 inputs=json.loads(a.build_identity.read_text())if a.build_identity else build_input_identity();publication=json.loads((R/'Unreal/Content/Data/catalogue.json').read_text())['sha256'];(out/'command.json').write_text(json.dumps({'command':cmd,'inputs':inputs,'executable_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'publication':publication},indent=2)+'\n');env=os.environ.copy();env.pop('PYTHONPATH',None);env.pop('LD_LIBRARY_PATH',None);start=time.monotonic();forced=False
 with(out/'runtime.log').open('w')as log:
  proc=subprocess.Popen(cmd,cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT)
  try:code=proc.wait(timeout=240)
  except subprocess.TimeoutExpired:forced=True;proc.terminate();code=proc.wait(timeout=15)
 d=json.loads(file.read_text(encoding='utf-8-sig'))if file.exists()else{};warnings=[line for line in(out/'runtime.log').read_text(errors='replace').splitlines()if'missing usage flag'in line.lower()or'Failed to find shader map for default material'in line];ok=(not a.restore_profile or d.get('aso_profile_restored')is True)and d.get('aso_profile_saved')is True and not forced and not warnings and validate(d,code,base,publication,a.restore_original,a.contact,a.neutral_lighting,a.clearance,a.art_refine)and(out/'cast_0.png').is_file()and(out/'frames.utrace').is_file();ok=ok and(not a.contact or all((out/(name+'.png')).is_file()for name in ['ledger_contact_start','ledger_stable_hold','ledger_inspection_closeup','ledger_gesture_closeup','ledger_release']));result={'accepted':ok,'exit_code':code,'forced':forced,'wall_seconds':time.monotonic()-start,'material_warnings':warnings,'scope':'Aso 16 evaluated clips, flat contacts and 20 round trips; no creative/device acceptance'};(out/'process.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));sys.exit(0 if ok else 1)
