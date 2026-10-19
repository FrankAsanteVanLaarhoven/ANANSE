#!/usr/bin/env python3
"""Launch native Development acceptance scenarios; Python only supervises processes."""
import argparse,json,os,subprocess,time,hashlib,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.export_content import verify_manifest

def build_input_identity():
    # File bytes identify dirty/untracked native work; a Git SHA alone cannot.
    paths=set((ROOT/'Unreal/Source').rglob('*'))
    paths.update((ROOT/'Unreal/Config').glob('*.ini'))
    paths.update([ROOT/'Unreal/Ananse.uproject',ROOT/'toolchain.lock.json',ROOT/'Unreal/Content/Data/catalogue.json'])
    files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted(paths) if p.is_file() and p.suffix in {'.cpp','.h','.cs','.ini','.uproject','.json'}}
    assets={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'Unreal/Content').rglob('*')) if p.is_file() and p.suffix in {'.uasset','.umap','.ubulk','.uexp','.json'}}
    authoring={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
               for directory in ['scripts','studio','production','.github/workflows']
               for p in sorted((ROOT/directory).rglob('*')) if p.is_file() and p.suffix in {'.py','.js','.html','.css','.json','.yml','.yaml'}}
    model_paths=set()
    # Every locally authored leopard revision is input evidence, including untracked
    # scenes and animation-only derivatives. A fixed v002 folder misses later art.
    for revision in (ROOT/'SourceArt/Characters/OseboLeopard').glob('Authored_v*'):
        if revision.is_dir():model_paths.update(revision.rglob('*'))
    model_paths.update((ROOT/'SourceArt/Characters/AnanseSpider/NativeReference_v001').rglob('*'))
    for key in ['Kwaku','AsoYaa','EsiHuman','OseboHuman','KojoTortoise','KofiHornbill','EsiMoth']:
        model_paths.update((ROOT/'SourceArt/Characters'/key).rglob('*'))
    model_paths.update((ROOT/'SourceArt/Environments/MarketSanctuary').rglob('*'))
    model_paths.add(ROOT/'SourceArt/ANANSE_Spider_Character_Kit/assets/proxy-v001/AnanseSpider_PROXY.glb')
    for key in ['AnanseSpider','OseboLeopard']:
        model_paths.update((ROOT/'SourceArt/Characters'/key).glob('NATIVE*_MAP*.json'))
        model_paths.update((ROOT/'SourceArt/Characters'/key).glob('INTEGRATION_PATH_MAP*.json'))
    models={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(model_paths)
            if p.is_file() and p.suffix in {'.blend','.glb','.fbx','.obj','.mtl','.png','.mp4','.json','.py'}}
    return {'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
            'files':files,'source_asset_files':assets,'authoring_source_files':authoring,
            'authored_model_files':models,
            'authored_model_sha256':hashlib.sha256(json.dumps(models,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'authoring_source_sha256':hashlib.sha256(json.dumps(authoring,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'native_source_sha256':hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'source_asset_sha256':hashlib.sha256(json.dumps(assets,sort_keys=True,separators=(',',':')).encode()).hexdigest()}

def verify_aso_expose_evidence(report,out,route):
    # Only negotiation makes the witness promise. Other routes must not invent
    # its broken-promise movie merely to satisfy a presentation checker.
    if report.get('mission_state',{}).get('route')!=route:return False
    reaction=any(f.get('event')=='aso_broken_promise_visual_only' for f in report.get('aso_video_frames',[]))
    capture=(Path(out)/'cinematic_broken_promise.png').is_file()
    return reaction and capture if route=='negotiation' else not reaction and not capture

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--engine-root',type=Path,required=True)
    parser.add_argument('--mode',choices=['r2','baseline','reload','cinematic','spider','contact','pursuit','pursuit-reload','episode-reload'],required=True)
    parser.add_argument('--context',choices=['pie','game','package'],default='pie')
    parser.add_argument('--executable',type=Path)
    parser.add_argument('--catalogue',type=Path,default=ROOT/'Unreal/Content/Data/catalogue.json',help='Exact exported manifest that was cooked into the selected candidate.')
    parser.add_argument('--build-identity',type=Path,help='Preserved source/content fingerprint captured for the selected package cook.')
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--slot');parser.add_argument('--duration',type=int,default=60)
    parser.add_argument('--offscreen',action='store_true')
    parser.add_argument('--consequence-dialogue',action='store_true',help='Exercise authored consequence lines through real native E interactions.')
    parser.add_argument('--expose',action='store_true',help='Choose exposure through the real choice marker in pursuit verification.')
    parser.add_argument('--route',choices=['negotiation','social','rooftop'],default='negotiation',help='Actual infiltration interactions for pursuit verification.')
    parser.add_argument('--episode',action='store_true',help='Continue the actual route to the technical sanctuary and save completion.')
    parser.add_argument('--appearance-capture',action='store_true',help='Use a declared front inspection camera and diagnostic fill for proxy colour comparison.')
    parser.add_argument('--require-valid-materials',action='store_true',help='Reject actual skeletal-material fallback/shader warnings in the running candidate.')
    parser.add_argument('--environment-route',action='store_true');parser.add_argument('--aso-contact',action='store_true');parser.add_argument('--aso-yaa',action='store_true');parser.add_argument('--accepted-visuals',action='store_true');
    parser.add_argument('--interaction-refinement',action='store_true');parser.add_argument('--forms-scenery',action='store_true');parser.add_argument('--art-refinement',action='store_true',help='Use published Kwaku refinement and versioned art maps.');parser.add_argument('--story-presentation',action='store_true',help='Use isolated authored episode staging maps; older campaign profiles remain separate.')
    parser.add_argument('--map',dest='map_path')
    parser.add_argument('--allocator',choices=['default','ansi'],default='default')
    parser.add_argument('--trace-preset',choices=['full','frame'],default='full',help='Frame uses native per-frame contact timing CSV; full CPU capture currently has a reproduced shutdown blocker.')
    args=parser.parse_args()
    if not 60<=args.duration<=600:parser.error("Duration must be 60..600 seconds.")
    engine=args.engine_root.resolve()
    version=json.loads((engine/'Engine/Build/Build.version').read_text())
    if version!=json.loads((ROOT/'toolchain.lock.json').read_text())['build_version']:raise RuntimeError('Engine pin mismatch.')
    if args.mode in ['reload','pursuit-reload','episode-reload'] and not args.slot:parser.error('Reload requires the previous dedicated --slot.')
    if args.episode and not args.consequence_dialogue:parser.error('Episode verification requires --consequence-dialogue.')
    if args.context=='package' and not args.executable:parser.error('Package requires --executable.')
    manifest=json.loads(args.catalogue.read_text());verify_manifest(manifest)
    kwaku=next(r for r in manifest['payload']['entities']['characters'] if r['id']=='kwaku')
    if args.mode=='r2' and (kwaku['version']!=2 or 'trick-mirror' in kwaku['data']['powers']):raise RuntimeError('r2 check requires the preserved restricted revision2.')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    slot=args.slot or ('AnanseVerify_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'))
    executable=args.executable.resolve() if args.executable else engine/'Engine/Binaries/Linux/UnrealEditor'
    command=[str(executable)]
    if args.context!='package':command.append(str(ROOT/'Unreal/Ananse.uproject'))
    if args.map_path:command.append(args.map_path)
    if args.aso_yaa:command.append('-AnanseAsoReview')
    if args.aso_contact:command.append('-AnanseAsoContact')
    if args.environment_route:command.append('-AnanseEnvironmentRoute')
    if args.accepted_visuals:command.append('-AnanseAcceptedVisuals')
    if args.story_presentation:command.append('-AnanseStoryPresentation')
    if args.art_refinement or args.forms_scenery or args.interaction_refinement:command.append('-AnanseArtRefinement')
    if args.forms_scenery:command.append('-AnanseFormsScenery')
    if args.interaction_refinement:command.append('-AnanseInteractionRefinement')
    if args.context=='pie':command.append('-ExecutePythonScript='+str(ROOT/'scripts/start_native_pie.py'))
    elif args.context=='game':command.append('-game')
    command+=['-windowed','-ResX=1280','-ResY=720','-unattended','-nop4','-nosplash','-stdout','-FullStdOutLogOutput','-abslog='+str(out/'runtime-session.log'),
        '-AnanseVerifyMode='+args.mode,'-AnanseVerifySeconds='+str(args.duration),'-AnanseVerifyReport='+str(out/'native-runtime.json'),
        '-AnanseExpectedHash='+manifest['sha256'],'-AnanseExpectedColour='+kwaku['data']['variants'][0]['cloth_colour'],
        '-AnanseExpectedMirror='+str(int('trick-mirror' in kwaku['data']['powers'])),'-AnanseVerifySlot='+slot]
    if args.mode in ['pursuit','pursuit-reload']:command.append('-AnanseProductionPursuit')
    if args.consequence_dialogue:command.append('-AnanseVerifyConsequenceDialogue')
    if args.expose:command.append('-AnanseVerifyExpose')
    if args.episode or args.mode=='episode-reload':command.append('-AnanseEpisode')
    if args.episode:command.append('-AnanseVerifyEpisode')
    if args.appearance_capture:command.append('-AnanseAppearanceCapture')
    command.append('-AnanseVerifyRoute='+args.route)
    trace_channels='cpu,frame,animation' if args.trace_preset=='full' else 'frame'
    command+=['-trace='+trace_channels,'-tracefile='+str(out/'runtime.utrace')]
    if args.offscreen:command.append('-RenderOffscreen')
    if args.allocator=='ansi':command.append('-ansimalloc')
    env=os.environ.copy()
    for key in ['PYTHONPATH','LD_LIBRARY_PATH']:env.pop(key,None)
    env['UE-LocalDataCachePath']=str(ROOT/'Unreal/DerivedDataCache')
    record={'command':command,'cwd':str(ROOT),'slot':slot,'mode':args.mode,'context':args.context,'revision':kwaku['version'],'publication_hash':manifest['sha256'],'engine_version':version,'removed_environment':['PYTHONPATH','LD_LIBRARY_PATH'],'offscreen':args.offscreen,'forced_termination':False,'timeout_seconds':args.duration+180}
    record['validation_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    record['trace_channels']=trace_channels
    record['build_inputs']=json.loads(args.build_identity.read_text()) if args.build_identity else build_input_identity()
    record['build_identity_scope']='preserved cook inputs' if args.build_identity else 'current working tree; not independent package provenance'
    record['catalogue_path']=str(args.catalogue.resolve())
    if args.context=='package':record['executable_sha256']=hashlib.sha256(executable.read_bytes()).hexdigest()
    if args.context!='package':record['native_module_sha256']=hashlib.sha256((ROOT/'Unreal/Binaries/Linux/libUnrealEditor-Ananse.so').read_bytes()).hexdigest()
    start=time.monotonic()
    with (out/'process.log').open('x') as log:
        proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        record['pid']=proc.pid;(out/'launch.json').write_text(json.dumps(record,indent=2)+'\n')
        try:rc=proc.wait(timeout=args.duration+180)
        except subprocess.TimeoutExpired:
            record['forced_termination']=True;record['termination_steps']=['SIGTERM to recorded PID'];proc.terminate()
            try:proc.wait(timeout=15)
            except subprocess.TimeoutExpired:record['termination_steps'].append('SIGKILL to recorded PID');proc.kill();proc.wait()
            rc=124
    record.update(exit_status=rc,process_returncode=proc.returncode,elapsed_seconds=time.monotonic()-start)
    log=out/'runtime-session.log'
    if args.context!='package' and log.exists():shutil.copy2(log,out/'session.log')
    (out/'command.json').write_text(json.dumps(record,indent=2)+'\n')
    path=out/'native-runtime.json';report=json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {'status':'missing'}
    material_errors=[]
    if log.exists():
        for line in log.read_text(errors='replace').splitlines():
            if 'missing usage flag' in line.lower() or 'Please fix material usage flag SkeletalMesh' in line or 'Failed to find shader map for default material' in line:
                material_errors.append(line)
    report['material_fallback_warnings']=material_errors
    report['material_validation_required']=args.appearance_capture or args.require_valid_materials
    passed=rc==0 and not record['forced_termination'] and report.get('status')=='assertions_passed' and report.get('play_stopped') and report.get('active_play_seconds',0)>=args.duration and bool(report.get('checks')) and not (report['material_validation_required'] and material_errors)
    if args.accepted_visuals:passed=passed and report.get('accepted_campaign_appearance') is True and report.get('accepted_campaign_mesh')=='/Game/Ananse/Characters/Kwaku/ArtPass2_v003/Kwaku.Kwaku'
    if (args.forms_scenery or args.interaction_refinement) and args.mode=='pursuit':passed=passed and report.get('authored_interactable_count')==8 and report.get('authored_interactable_ready')==8 and report.get('authored_npc_idle_playing')==2
    if args.aso_contact and args.mode=='pursuit' and args.expose:passed=passed and verify_aso_expose_evidence(report,out,args.route)
    report['acceptance']='passed' if passed else 'failed';report['process_exit_status']=rc
    report['screenshots']=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in out.glob('*.png')]
    path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(record,indent=2));print(json.dumps(report,indent=2));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
