# Kwaku and OseboLeopard visual/deformation review — 16 October 2026

**Both characters remain rejected for final art use.** Corrective editable assets and a fresh executable review candidate are delivered; this is not reference-likeness, natural-deformation, campaign-species or commercial-release approval. Frank must review likeness separately. No other family was started.

Branch `feature/local-milestone-verification`; HEAD `ec7bf0bcf16634a13c12e92433e9731064890e80`; uncommitted/unstaged. No commit, push, publication, deployment, purchase, tool installation or unrelated system changes.

## Character-by-character result

| Gate | Kwaku | OseboLeopard |
|---|---|---|
| reference_likeness | REVIEW_REQUIRED | REVIEW_REQUIRED |
| silhouette | FAIL | FAIL |
| face | FAIL | FAIL |
| hands_digits | FAIL | FAIL |
| prop_contact | FAIL | BLOCKED |
| clothing_deformation | FAIL | FAIL |
| limb_deformation | FAIL | FAIL |
| material_quality | FAIL | FAIL |
| cinematic_readability | FAIL | FAIL |
| gameplay_readability | REVIEW_REQUIRED | REVIEW_REQUIRED |
| source_scene_verified | PASS | PASS |
| package_verified | PASS | PASS |

[Kwaku findings](visual-review-20261016/Kwaku.md) · [Kwaku JSON](visual-review-20261016/Kwaku.json) · [Leopard findings](visual-review-20261016/OseboLeopard.md) · [Leopard JSON](visual-review-20261016/OseboLeopard.json). Each uses twelve independent gates; no REVIEW_REQUIRED was converted to PASS.

## Actual corrections and source identity

Kwaku: `SourceArt/Characters/Kwaku/Authored_v028/Kwaku.blend` and `Kwaku.glb`, separate `Ledger.glb`, and filtered `NativeImport/Kwaku.glb`. Removed the obsolete overlapping collar-neck geometry; revised face/eyes/lids and digit/palm proportions; repaired sleeve/sash weighting. Reauthored the real InspectLedger action with bounded original arm/thumb controls and a hold through frame80 before release. No bone scale/stretch or root/collision workaround. Original46-bone rest hierarchy and eleven action identities remain. Source133773vertices, max4normalized influences.

OseboLeopard: `SourceArt/Characters/OseboLeopard/Authored_v013/OseboLeopard.blend` and `.glb`, rosette texture and `NativeCapture/OseboCapture.glb`. Revised muzzle/skull/ears, neck/tail-root/cape surfaces, actual morphing eyelids, iris/pupil placement and axial arm weights. Added a readable two-paw CaptureReach through original arm controls. Original64-bone rest hierarchy and nine action identities remain; source60155vertices, max2normalized influences. Two arms, two legs, one tail. Native mesh imported from012; neutral geometry, polygons, weights, rest bones and morph coordinates are identical to013, independently hashed in `animation-only-geometry.json`. Only the013 CaptureReach was imported afterward. Do not claim the mesh was reimported from013.

Toolchain: installed Unreal5.8.3/changelist58210709 (compatible55116800), Blender4.5.14LTS/hash62c1db4208e8. Source metres -> native centimetres; measured native mapping(-Y,-X,Z)*100, qualified import yaw-90deg with one mesh-description+90deg correction, retained animation frame. Existing bone local matrices/parents are recorded in native review JSON; no blind retarget or scale change. Native LOD0/1/2: Kwaku142343/74577/40178vertices,265190/132593/66296triangles; leopard67100/36430/20613vertices,119596/59614/29716triangles. This remains unqualified for mobile. Both saved scenes contain seven real expression targets: Blink_L/R, BrowUp/Down, Concern, Suspicion, Determination. Eye-direction poses are reviewed through actual controls. Full jaw/lip/speech and fear/startle range remains incomplete. Both paired open-visible ray tests cover54/54samples on closure, with16open rays that did not hit eye explicitly excluded per character. Bulging lids/orbital seams still fail natural facial-art acceptance.

Kwaku page-core diagnostic checks every visible integer frame23..80:1728evaluated hand vertices per frame, zeroinside conservative pagecore,0cmdepth. It excludes cover/clasp/2mmedges and invisible pickup/stow samples. It is not full mesh penetration/grasp certification; no tolerance was relaxed. Earlier reports demonstrating206penetrating vertices and release-frame failures are retained. Actual native hand skin probes match saved posed source within0.1cm, rest within0.01cm. Five digit chains per hand/paw remain; natural anatomy/grip is still failed. Actual native LedgerPresentation attaches to bone hand_R with NoCollision (`AnanseCastLab.cpp:84`); no named socket_ledger was verified. The source checker socket_ledger text is a semantic work-order label, not socket evidence. Native versus source contact limitations remain explicit.

Remaining defects: generic Kwaku face/hair and proportions; sleeve openings/folds, wrist/ankle/palm volume, stiff/short fingers and simplified textile/costume; leopard round head/ears, segmented neck/shoulders, muzzle/jaw/eye seams, paw/cuff joins, tail-root/cape/armour integration and overly simple rosette/fur/leather. The reference comparison clearly fails final silhouette/material/cinematic quality. Do not hide these with framing or rename engineering art as final.

## Controlled and native evidence

Evidence root: `.local/verification/visual-acceptance-20261016/`. All technical views are rendered from the exact saved source, not illustrations. Before/after cameras, focal length, light placement/energy and exposure match. Reference illustration camera is unmeasured. Each source has20solid/topology/skeleton views;22face views and4actual arm-weight views across the pair;18reference/before/after sheets. Comparison manifests retain camera matrices and source/image hashes.

[Kwaku face comparison](../../.local/verification/visual-acceptance-20261016/comparisons-final/Kwaku-dialogue.png) · [Kwaku interaction](../../.local/verification/visual-acceptance-20261016/comparisons-final/Kwaku-interaction.png) · [Leopard silhouette](../../.local/verification/visual-acceptance-20261016/comparisons-final/OseboLeopard-front.png) · [Leopard reach](../../.local/verification/visual-acceptance-20261016/comparisons-final/OseboLeopard-interaction.png).

Final source manifests: `Kwaku-selected5/`, `OseboLeopard-selected5/`, facial review `*-face5/`, `arm-weight-views-final/`, `comparison-provenance-final.json`; source checks `source-checks-05.json`; blink `blink-occlusion-05.json`; full visible ledger diagnostic `ledger-volume-diagnostic-08.json`; native `native-07/native.json`; reopened skin probes `native-reopened-probes-04.json`. Native skin/LOD tests are technical checks, not deformation/likeness approval. Source action geometry is sampled every5frames; not a proof every surface is collision-free.

Native assets: `/Game/Ananse/Characters/Kwaku/Visual_v003/{Kwaku,BP_Kwaku,DA_Kwaku,Kwaku_Anim}` (definition8), `/Game/Ananse/Characters/OseboLeopard/Visual_v003/{OseboLeopard,BP_OseboLeopard,DA_OseboLeopard}` (definition5), plus `Capture_v002/OseboCapture`. Actual object/generated-class paths and retained skeleton/physics/clip bindings are in each review JSON. Reuse existing independent skeleton/ABP/contact architecture. One defined final pose path; gameplay root/collision unchanged. No campaign species substitution or competing AI. New visual definitions are unpublished opt-in review data.

Source changes: `scripts/{render_visual_acceptance,sculpt_visual_characters,check_visual_sources,finalize_visual_sources,repair_visual_blinks,correct_visual_contacts,refine_ledger_thumb_pose,refine_ledger_release,refine_leopard_capture_pose,render_face_review,visual_acceptance_contract,import_visual_review,import_visual_capture,build_visual_review_maps}.py`; opt-in existing `run_story_cast_check.py`, `run_cross_family_check.py`, `run_leopard_contact_check.py`, `unreal.py`; `refine_visual_review_lighting.py` changes only the isolated leopard fixture; `native_runtime_smoke.py` now fingerprints all authored leopard revisions instead of only002. C++ opt-in review bindings/inspection/description/tests in `Unreal/Source/Ananse/{AnanseAuthoredAnimation,AnanseLabSelection,AnanseCastLab,AnanseLeopardContactVerification,AnanseLeopardLab,AnanseRefinedArtTests}.cpp`, and `Unreal/Config/DefaultGame.ini`. Tests: `tests/test_visual_acceptance.py` and strict visual binding cases in existing cross/contact tests. No new gameplay framework.

## Executed verification

Python291passed (`python-06.log`, isolated project environment; initial unisolated pytest attempt hit unrelated ROS plugin import and is retained). Native27passed after final editor build10 (`native-tests-05/`);2clean/25pre-SDL Wayland warnings, no failed assertions. Input-package20 and prior280/26/24/six-routes/restarts remain historical; not added into invented totals. No final six-route sweep or spider240s rerun was needed because their progression/controller/contact implementation was unchanged. Cross-family verifies restored spider contacts; original013344 historical coverage remains protected.

| Fresh rendered stage | Exit | Wall seconds |
|---|---:|---:|
| cast-ledger-close | 0 | 203.011 |
| leopard-motion-close | 0 | 64.041 |
| cross-family | 0 | 64.302 |
| leopard-terrain | 0 | 164.240 |
| pursuit-regression | 0 | 65.938 |

These are native scripted scenarios, not physical keyboard/controller/touch or novice observations. Cross-family asserts20complete round trips/40committed transitions plus7negative cases. Leopard terrain uses actual evaluated feet atLOD2 on its declared fixture, unchanged2cm/0.5cm thresholds; full report retains exclusions. Nine-motion preview is not played leopard AI pursuit; original human Osebo pursuit regression preserves ten capture/retries/obstruction behavior. Actual leopard capture-target contact remains BLOCKED/unverified. Frame traces/native counters are retained; no detailed CPU/function/GPU/mobile inference. Long-session memory, broader terrain/navigation, campaign mapping and physical-device gates stay open.

## Fresh review package and launch

Package: `/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261016T145831.944219Z`

ELF SHA-256: `e5ff3840434688705f5c5167cd790b70972797f1c2eedc784b02c08556e8a312`

Frozen input hashes: native `94e4eea5f467b0e679686743f4fb33d1c6db44459f9629d50920a7106062862f`; native content `d12e67307edc59531fc9a4075320d44a78690b6491ab495a18ca9cbf4a2b667e`; authoring `6bcdda31582b9f099a2734bddec6c0dc809db7dbd6c8b13bda846d3c6242e20c`; source models `cf243738c1ab9c5eab99e8031d40c8cb9fc63f057f3508508437ab1afc926959`. Full untracked source/content/toolchain identity: `inputs-06.json`; prelaunch payload files/hash `package-manifest-06.json`. Geometry regression candidate05 has its separate exact inputs05 and payload manifest05. A Git SHA alone does not identify this build.

Verified invocation pattern (exact automated commands in `package-05/`):

```bash
"/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261016T145831.944219Z/Ananse/Binaries/Linux/Ananse" /Game/Ananse/Maps/Visual_v003/L_CharacterVisualReview -ansimalloc -AnanseVisualReview -AnanseArtRefinement -AnanseFormsScenery -AnanseInteractionRefinement -windowed -ResX=1280 -ResY=720
```

For leopard use `/Game/Ananse/Maps/Visual_v003/L_LeopardVisualContact` with the same flags. Review maps/default lab preserve Kwaku campaign identity. PageDown selects next design; Home spider/End leopard;1–9clips,0auto,Vwireframe,Ppause,F6/F8dedicated lab profile. Ordinary input launch is available; the fresh verification invoked additional scenario/report/trace flags recorded in its commands. Do not claim physical input tested. Genuine PNGs: `package-05/cast-ledger-close/kwaku-{ledger,eyes-open,eyelids-closed}.png`, `package-06/leopard-motion-close/leopard-stage-{0,2,5}.png` and `leopard-blink.png` (lighting06); dark05captures preserved; source fixed views are the controlled comparisons. Native Kwaku blink camera can be profile; do not treat native open/closed shots as a matched frontal comparison. Geometry-candidate05 leopard close/capture shots were severely backlit and retained as a rejected presentation. Candidate06 adds front fill to that isolated fixture, without hiding anatomy/clipping; final image review is separately recorded in lighting-visual-review.json: visibility improves, but harsh highlights and cropped close framing remain FAIL. Close framing/motion blur and underlying art still prevent final cinematic acceptance. No new final voiced cinematic or audio capture.

## Failures, preservation and next decision

All rejected source revisions and failed reports retained. Package135052 was rejected for exposed eyes;140237 lacked the intended map;144426 is rejected as exact-source evidence because a header-order correction occurred after freeze (UAT eventually completed; already-running game was allowed normal exit, only pipeline supervisors stopped). Animation-only attempts05/06 produced no acceptable new clip/target and were rejected before definition mutation;07uses installed engine import_only_animations and imports one actual clip. Geometry package144626 uses frozen corrected inputs and all five affected scenarios passed. Its dark leopard fixture remains rejected for cinematic presentation. Final06 changes only leopard review-map front fill and adds its authoring script, with identical binary/native gameplay/character models/maps otherwise; lighting-build-delta.json proves this. Only affected leopard nine-motion inspection is rerun in06. Do not call all five scenarios executed in06. Earlier checker/schema and map-preflight failures were not relabelled passes.

Original610native asset entries,650source model entries,87explicitly protected files,39rollback payload files and both reference hashes remain unchanged (`preservation-audit-final.json`). Rollback013344 ELF unchanged. Existing immutable cataloguepublication `ae9920682a7442f4850ca8fe8f2b127f`, SHA `edd86d324f4db0e0980ab55d248c8e6dd97df69277a1051a4670aa13faa82bab`, unchanged. All working data/saves/rejected evidence retained; index empty. `-ansimalloc` workaround and detailed CPU-trace shutdown defect unresolved. No attribution/signing/account/system-tool changes.

Materially used skills: enterprise-execution and task-observer. Skill-retrieval connector unavailable; repository contracts and installed engine APIs used. No external generation/reference upload.

**Next decision:** review the exact comparison/interaction images and keep both characters unaccepted. Next corrective milestone should rebuild integrated facial/shoulder/paw/costume surfaces on these retained skeletons, address natural whole-surface grip/capture contacts and complete facial range before another final-art review. Do not proceed to another family as if these passed.

Final lighting-only package06 independently reran the nine-motion leopard scenario with normal exit. Its exact process report is `package-06/leopard-motion-close/process.json`; full five-stage geometry regression belongs to candidate05. No unrelated tests were repeated for a non-colliding review-light change.

## Complete new leopard foot metrics — geometry candidate05

Unchanged limits: per-leg p95 drift≤2cm; max penetration≤0.5cm; segment error≤0.1cm. Actual finalized feet plus authored sole-plane offsets atLOD2, not full-mesh collision acceptance. Controlled45cm/s fixture coverage includes flat,ramp,steps,uneven,moving/disappearing support; all exclusions and actor coverage retained in `package-05/leopard-terrain/result.json`. No failing leg averaged away.

| Leg | Stance samples | Excluded swing/airborne/invalid | p95 drift cm (full / readable decimal) | Max penetration cm (full / readable decimal) |
|---|---:|---:|---|---|
| L | 65319 | 21845 | 4.10487518820446e-05 (0.00004104875188204) | 2.9575032385764644e-05 (0.00002957503238576) |
| R | 65523 | 21641 | 0.6721770167350769 (0.67217701673507690) | 2.9573770007118583e-05 (0.00002957377000712) |

Native p95 query8.190051078796387µs, solve13.391952514648438µs, frame interval2.5661540031433105ms. These are instrumented native counters in this scenario, not detailed CPU-thread/function, GPU, mobile or long-session profiling. Invalid transforms0; segment length error0. Contact measurements pass the numeric contract; natural deformation and art remain FAIL.
