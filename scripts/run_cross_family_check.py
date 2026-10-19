"""Supervise forty real cross-family commits, negative cases and normal exit."""
import argparse,json,math,os,subprocess,time,hashlib
from pathlib import Path
from scripts.native_runtime_smoke import build_input_identity
ROOT=Path(__file__).resolve().parents[1]
MAP='/Game/Characters/AnanseSpider/Lab_v001/L_AnanseCharacterLab'
SPIDER='ananse-spider-existing';LEOPARD='osebo-leopard-v1'
FAMILIES={
 SPIDER:dict(pawn_class='/Game/Production/Characters/SpiderSelection_v001/BP_AnanseSpider.BP_AnanseSpider_C',
  mesh='/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY.AnanseSpider_PROXY',
  skeleton='/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY_Skeleton.AnanseSpider_PROXY_Skeleton',
  animation_instance='/Game/Production/Characters/SpiderRig_v001/ABP_AnanseSpider.ABP_AnanseSpider_C'),
 LEOPARD:dict(pawn_class='/Game/Ananse/Characters/OseboLeopard/Runtime_v001/BP_OseboLeopard.BP_OseboLeopard_C',
  mesh='/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard',
  skeleton='/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard_Skeleton.OseboLeopard_Skeleton',
  animation_instance='/Game/Ananse/Characters/OseboLeopard/Animations/ABP_OseboLeopard.ABP_OseboLeopard_C')}
NEGATIVES={'unknown_design_retained','missing_asset_retained','incompatible_rig_retained','blocked_spawn_retained','cancel_retained','latest_request_won','late_completion_rejected'}

def verify(report,code,restore=None,publication=None,interaction_refinement=False,visual_review=False,art_pass2=False,aso_yaa=False,aso_contact=False,aso_clearance=False,aso_art_refine=False):
    families={k:dict(v)for k,v in FAMILIES.items()}
    if interaction_refinement:families[LEOPARD].update(pawn_class='/Game/Ananse/Characters/OseboLeopard/Interactions_v003/BP_OseboLeopard.BP_OseboLeopard_C',mesh='/Game/Ananse/Characters/OseboLeopard/Interactions_v003/OseboLeopard.OseboLeopard')
    if visual_review:families[LEOPARD].update(pawn_class='/Game/Ananse/Characters/OseboLeopard/Visual_v003/BP_OseboLeopard.BP_OseboLeopard_C',mesh='/Game/Ananse/Characters/OseboLeopard/Visual_v003/OseboLeopard.OseboLeopard')
    if art_pass2:families[LEOPARD].update(pawn_class='/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/BP_OseboLeopard.BP_OseboLeopard_C',mesh='/Game/Ananse/Characters/OseboLeopard/ArtPass2_v003/OseboLeopard.OseboLeopard')
    other="aso-yaa-human-v1"if aso_yaa else LEOPARD
    if aso_yaa:
        prefix="/Game/Ananse/Characters/AsoYaa/ArtRefine_v002/"if aso_art_refine else"/Game/Ananse/Characters/AsoYaa/Clearance_v001/"if aso_clearance else"/Game/Ananse/Characters/AsoYaa/Contact_v002/"if aso_contact else"/Game/Ananse/Characters/AsoYaa/Negotiation_v002/"
        families[other]=dict(pawn_class=prefix+"BP_AsoYaa.BP_AsoYaa_C",mesh=prefix+"AsoYaa.AsoYaa",skeleton=("/Game/Ananse/Characters/AsoYaa/Clearance_v001/"if aso_art_refine else prefix)+"AsoYaa_Skeleton.AsoYaa_Skeleton",animation_instance=("/Game/Ananse/Characters/AsoYaa/Clearance_v001/"if aso_art_refine else prefix)+"ABP_AsoYaa.ABP_AsoYaa_C",physics=("/Game/Ananse/Characters/AsoYaa/Contact_v002/"if aso_clearance else prefix)+"AsoYaa_PhysicsAsset.AsoYaa_PhysicsAsset")
    try:
        if aso_yaa and report.get("other_design")!=other:return False
        if code!=0 or report['passed'] is not True or report['normal_lit_rendering'] is not True:return False
        if publication and report.get('loaded_publication_hash')!=publication:return False
        if not 60<=report['seconds']<115 or report['world']!=MAP+'.L_AnanseCharacterLab':return False
        if report['committed_cross_family_transitions']!=40 or report['complete_round_trips']!=20:return False
        transitions=report['transitions']
        if len(transitions)!=40:return False
        prior=None
        for i,t in enumerate(transitions,1):
            expected=other if i%2 else SPIDER
            if t['transition']!=i or t['requested_design']!=expected or t['committed_design']!=expected or t['passed'] is not True:return False
            if any(t.get(k)!=v for k,v in families[expected].items()):return False
            if aso_yaa and expected==other and t.get('aso_contacts_rebuilt')is not True:return False
            if t['input_mapping_active'] is not True or t['camera_bound'] is not True or t['evaluated_gesture_motion'] is not True:return False
            if t['graph_evaluations']<1 or t['graph_clip_observed'] is not True:return False
            if t['finite_pose'] is not True:return False
            if type(t['movement_cm']) not in (int,float) or not math.isfinite(t['movement_cm']) or t['movement_cm']<=.5:return False
            if type(t['possessed_pawn_id']) is not int or t['possessed_pawn_id']==prior:return False
            prior=t['possessed_pawn_id']
            if not t['physics'].startswith('/Game/') or (expected==SPIDER and t['spider_contacts_rebuilt'] is not True):return False
        checks=report['negative_checks']
        if len(checks)!=7 or {c['check'] for c in checks}!=NEGATIVES or any(c['passed'] is not True for c in checks):return False
        if report['rejected_stale_completions']<1:return False
        if restore and (report['restored_profile_committed'] is not True or report['restored_design']!=restore):return False
        m=json.loads(report['post_return_contact_metrics'])
        if m['invalid_transforms']!=0 or m['last_solved_chains']!=4:return False
        if len(m['legs'])!=4 or {l['leg'] for l in m['legs']}!={'front_l','front_r','rear_l','rear_r'}:return False
        for leg in m['legs']:
            if type(leg['samples']) is not int or leg['samples']<1:return False
            for field,limit in [('p95_stance_drift_cm',2),('max_penetration_cm',.5),('max_segment_length_error_cm',.1)]:
                value=leg[field]
                if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=limit:return False
            if leg['joint_limit_violations']!=0:return False
    except (KeyError,TypeError,ValueError):return False
    return True

def main():
    p=argparse.ArgumentParser();p.add_argument('--aso-art-refine',action='store_true');p.add_argument('--aso-clearance',action='store_true');p.add_argument('--neutral-lighting',action='store_true');p.add_argument('--aso-contact',action='store_true');p.add_argument('--aso-yaa',action='store_true');p.add_argument('--art-pass2',action='store_true');p.add_argument('--visual-review',action='store_true');p.add_argument('--interaction-refinement',action='store_true');p.add_argument('--out',type=Path,required=True);p.add_argument('--executable',type=Path)
    p.add_argument('--restore',choices=[SPIDER,LEOPARD]);p.add_argument('--build-identity',type=Path);p.add_argument('--profile-dir',type=Path);a=p.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    exe=a.executable.resolve() if a.executable else Path('/home/favl/Unreal/UE_5.8.3-58210709/Engine/Binaries/Linux/UnrealEditor')
    cmd=[str(exe)]+([] if a.executable else [str(ROOT/'Unreal/Ananse.uproject'),'-game'])+[MAP,'-ansimalloc','-windowed','-ResX=1280','-ResY=720','-unattended','-nosplash','-NoScreenMessages',f'-AnanseCrossFamilyVerify={out/"result.json"}',f'-AnanseVerifyReport={out/"contact-samples.json"}','-trace=frame',f'-tracefile={out/"frames.utrace"}']
    if a.neutral_lighting:cmd.append('-AnanseNeutralLabLighting')
    if a.aso_art_refine:
        assert a.aso_clearance
        cmd.append('-AnanseAsoArtRefine')
    if a.aso_clearance:
        assert a.aso_yaa and a.aso_contact
        cmd.append('-AnanseAsoClearance')
    if a.aso_contact:cmd.append('-AnanseAsoContact')
    if a.aso_yaa:cmd+=['-AnanseCrossAso','-AnanseAsoReview']
    if a.art_pass2:cmd.append('-AnanseArtPass2')
    if a.visual_review:cmd+=['-AnanseVisualReview']
    if a.interaction_refinement:cmd+=['-AnanseInteractionRefinement','-AnanseArtRefinement']
    if a.profile_dir:cmd+=[f'-UserDir={a.profile_dir.resolve()}']
    if a.restore:cmd+=['-AnanseCrossRestoreCheck',f'-AnanseCrossExpectedRestore={a.restore}']
    with exe.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    inputs=json.loads(a.build_identity.read_text()) if a.build_identity else build_input_identity()
    catalogue=ROOT/'Unreal/Content/Data/catalogue.json'
    if hashlib.sha256(catalogue.read_bytes()).hexdigest()!=inputs['files']['Unreal/Content/Data/catalogue.json']:
        raise RuntimeError('Selected cook identity and catalogue bytes differ; do not launch with guessed content identity')
    publication=json.loads(catalogue.read_text())['sha256']
    (out/'command.json').write_text(json.dumps(dict(command=cmd,context='package' if a.executable else 'editor-game',inputs=inputs,
        identity_scope='preserved cook inputs' if a.build_identity else 'current tree; not independent package provenance',
        executable_sha256=digest,expected_restore=a.restore),indent=2)+'\n')
    env=os.environ.copy()
    for k in ['PYTHONPATH','LD_LIBRARY_PATH']:env.pop(k,None)
    forced=False;started=time.monotonic()
    with (out/'runtime.log').open('w') as stream:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
        try:code=proc.wait(timeout=180)
        except subprocess.TimeoutExpired:
            forced=True;proc.terminate()
            try:code=proc.wait(timeout=20)
            except subprocess.TimeoutExpired:proc.kill();code=proc.wait()
    r=json.loads((out/'result.json').read_text(encoding='utf-8-sig')) if (out/'result.json').is_file() else {}
    accepted=not forced and verify(r,code,a.restore,publication,a.interaction_refinement,a.visual_review,a.art_pass2,a.aso_yaa,a.aso_contact,a.aso_clearance,a.aso_art_refine)
    for name in ['result.png','aso.png'if a.aso_yaa else'leopard.png','frames.utrace']:
        accepted &= (out/name).is_file() and (out/name).stat().st_size>1000
    (out/'process.json').write_text(json.dumps(dict(accepted=bool(accepted),exit_code=code,forced_termination=forced,wall_seconds=time.monotonic()-started),indent=2)+'\n')
    print(json.dumps(dict(accepted=bool(accepted),exit_code=code,round_trips=r.get('complete_round_trips'),transitions=r.get('committed_cross_family_transitions'))))
    return 0 if accepted else 1
if __name__=='__main__':raise SystemExit(main())
