# Aso Yaa negotiation engineering checkpoint — 16 October 2026

Branch `feature/local-milestone-verification`, HEAD `ec7bf0bcf16634a13c12e92433e9731064890e80`; all milestone work remains uncommitted. No other character was authored. This is a review candidate, not final art acceptance.

## Delivery and source

- Package: `Builds/Linux/20261016T204016.914795Z/`
- ELF SHA-256: `37f6d4a5f5cad1d75bc81cd5d6c7aa0c37f7bf7a5edb927b34491f73ae8eeec5`
- Exact frozen dirty-tree inputs: `.local/verification/aso-yaa-20261016/inputs-final.json` (source, content, authoring and model hashes).
- Editable source: `SourceArt/Characters/AsoYaa/Authored_v007/AsoYaa.blend`; SHA-256 `0fd31f7086e6458b9216d4de8f1c423fca7429da184606f29e38b632c9966298`.
- Interchange: `SourceArt/Characters/AsoYaa/Authored_v007/AsoYaa.glb`; SHA-256 `9e89afcc9efcb47e88b5d1b817d8518001081c000474a7565dee5d34800066ac`.
- Blender 4.5.14; engine 5.8.3-58210709. Existing qualified GLB import path retained. Native centimetres; exact rest transforms/axes, socket transforms and units are in `SourceArt/Characters/AsoYaa/NATIVE_RIG_MAP_20261016_v004.json`.
- 48 native rest bones; 16 distinct keyed animation drafts; no invalid/unweighted source vertices, max 3 influences. Native LOD0 43,847 vertices / 83,580 triangles; LOD1 22,461 / 41,788; LOD2 11,528 / 20,894. These counts do not approve art or mobile budgets.

## Actual native family

- mesh: `/Game/Ananse/Characters/AsoYaa/Negotiation_v002/AsoYaa.AsoYaa`
- skeleton: `/Game/Ananse/Characters/AsoYaa/Negotiation_v002/AsoYaa_Skeleton.AsoYaa_Skeleton`
- physics: `/Game/Ananse/Characters/AsoYaa/Negotiation_v002/AsoYaa_PhysicsAsset.AsoYaa_PhysicsAsset`
- ik: `/Game/Ananse/Characters/AsoYaa/Negotiation_v002/IK_AsoYaa.IK_AsoYaa`
- control_rig: `/Game/Ananse/Characters/AsoYaa/Negotiation_v002/CR_AsoYaa.CR_AsoYaa`
- animation_blueprint: `/Game/Ananse/Characters/AsoYaa/Negotiation_v002/ABP_AsoYaa.ABP_AsoYaa`
- blueprint: `/Game/Ananse/Characters/AsoYaa/Negotiation_v002/BP_AsoYaa.BP_AsoYaa`
- generated_class: `/Game/Ananse/Characters/AsoYaa/Negotiation_v002/BP_AsoYaa.BP_AsoYaa_C`
- definition: `/Game/Ananse/Characters/AsoYaa/Negotiation_v002/DA_AsoYaa.DA_AsoYaa`
- map: `/Game/Ananse/Maps/Negotiation_v002/L_AsoYaaCharacterLab`

IK and Control Rig are functional authoring assets; the compiled Animation Blueprint uses the established single runtime contact/deformation path. Gameplay retains authoritative root/capsule movement. Normal-play physics is kinematic; feather/cloth or secondary motion never owns movement. Three native sockets (voice/jaw, ledger L/hand_L, ledger R/hand_R) resolve, but zero-origin ledger sockets are not approved held-prop grips.

Motion identities:

IdleStrategist, WalkControlled, Turn, Listen, InspectEvidence, Consider, NegotiateOpen, NegotiateFirm, Agreement, Refusal, ProtectWitnesses, ReactBrokenPromise, DialogueNeutral, DialogueConcern, DialogueResolve, LimbIsolation.

## Negotiation and cinematic

The existing mission owns evidence, permits, promises, trust and outcomes. Aso presentation reads those states: refusal without evidence, inspection, agreement, protect reaction and broken-promise reaction on exposure. It never sets outcomes. One inherited visual-only staging duplicate was removed from the new map only.

The new map is `/Game/Ananse/Maps/Negotiation_v002/L_Market_AsoNegotiation`. The 18-second six-shot camera-only sequence is `/Game/Ananse/Characters/AsoYaa/Negotiation_v002/Cinematics_v004/LS_AsoNegotiation_v002`. Explicit 25/35/50 mm camera lenses, fixed review settings and disabled DOF are recorded in `reopen-final/native.json`. Camera-component orientation tracks actual speaker heads; pawns remain gameplay-owned. Tracks restore state and global restoration remains forced. Original MSN_NEG_010–050 draft dialogue is retained; subtitles exist, approved recordings do not.

## Executed validation

- Full Python suite: **311 passed**, `python-final-D.log`.
- Native engine automation: **31 passed**, `native-tests-D/unreal-automation/index.json`; native build and cook exited 0.
- Three rendered final lab sessions, each >=60 seconds, each exercising all 16 clips and **20 complete round trips / 40 committed transitions** with Aso: Ananse, Kwaku and Osebo respectively.
- Separate fresh process restores Aso profile and repeats motion/selection checks.
- Aso/Ananse and retained Ananse/Osebo suites each passed 40 committed transitions and seven negative checks, including missing content, incompatible rig, cancellation/stale completion and obstructed spawn.
- Negotiation protect and expose/broken-promise routes reached pursuit, ten capture/retries, escape, consequence, sanctuary/completion and save.
- Cinematic finish, skip, actual P pause/resume, cancel and retry passed; pause clock drift was zero. Camera/input/possession/UI restoration asserted.
- Fresh-process before-choice and sanctuary restart checks passed on their explicit correct fixture maps.
- Existing Kwaku ledger/interaction regression passed. Spider/leopard terrain was not rerun: their solver/assets were not changed. Prior terrain results remain historical.
- Exact commands, assertion identities, measured flat-fixture contacts, sample counts, runtime classes, publication/build identities and normal exits are retained per stage. See `final-results.json`, `final-cast-stages.json`, `final-episode-stages.json` and each stage's command/process/native JSON. Do not add overlapping suite counts.

## Studio prototype revision and rollback

Internal role-reviewed prototype publications were executed through the existing studio API, not direct database mutations or external deployment. They are technical reviews, not independent human art approval.

- A: `cf5290dcc72644d18afd6f760f88d81d`, first authored revision.
- B: `686d6f9936644042b6785c0d3df29749`, NEW publication restoring prior published draft. Cook `20261016T194911.482359Z` observed prior Story_v001 appearance and eight clips through 20 round trips.
- C current: `f024326dc79048c7aec7055c6d6dc7b6`, asset revision 5 / native definition revision 3; semantic SHA-256 `1faf44ca273fc87a0a90c8819d3d33b57f1669a71468bbdeae6029653d215990`.

All 21 prior publications, canonical character records and Kwaku revision history were preserved. Stale writes returned 412; unreviewed publishing returned 409. Licence/mobile flags remain unqualified; production publication is blocked. Browser GPU preview was not newly exercised.

## Review evidence and limitations

Current-source fixed views, real topology, skeleton, pose grid, weights and turntable are under `.local/verification/aso-yaa-20261016/source-review-02/`, `deformation-grid/` and `weight-review/`. The `ledger_interaction.png` is a pose, not held-ledger contact proof. Packaged screenshots are in `final-protect/` and the genuine sampled viewport video in `final-cast-spider/actual_gameplay_review.mp4`. Video samples approximately twice per second and holds frames at 8 fps; it is silent, not full-rate motion evidence. Provenance records readback/request timing.

Creative likeness/face/hands/acting/deformation/readability remain REVIEW_REQUIRED. Robe seam/clearance defects remain FAIL; held ledger grip remains FAIL. Eleven facial morphs and blink correction exist, but no speech viseme range/lip sync or final voice/music. Source facial form, digit anatomy, yoke/sleeve gaps, material response and cinematic lighting remain visibly draft. No physical controller, touch, Android/iOS device, long-session memory, broader terrain/navigation or rights/cultural approval is claimed. Existing environment blockouts remain.

## Safety and failures

`preservation-final.json` verifies the accepted package's 39 files, all 878 previous model files and 883 prior native/content files unchanged. The sole intentional old-content difference is the catalogue publication export. All final frozen source/content/model inputs and 39 final package payload files match after qualification. Failed imports, missing-cook-definition rejection, wrong-fixture restart rejection, checker/schema mismatch, lid iterations and camera/paused-input experiments are preserved; see `failure-reconciliation.json` and original stage logs. No reset, clean, commit, push, external publication, purchase or deployment occurred. Allocator workaround remains required; detailed CPU-trace shutdown failure remains unresolved. Frame/native timings do not establish GPU/thread/mobile performance.

## Launch

The executable/map/flags below were exercised by the packaged supervisors; the interactive command removes automation and uses a dedicated profile. Physical/manual input qualification is separate.

```bash
"/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261016T204016.914795Z/Ananse/Binaries/Linux/Ananse" /Game/Ananse/Maps/Negotiation_v002/L_Market_AsoNegotiation -AnanseAsoReview -AnanseAcceptedVisuals -AnanseEpisode -AnanseStoryPresentation -AnanseArtRefinement -AnanseFormsScenery -AnanseInteractionRefinement -ansimalloc -windowed -ResX=1280 -ResY=720 -UserDir="/home/favl/Downloads/ANANSE_Production_Starter/.local/aso-yaa-player-final"
```

Stop for human Aso Yaa visual/deformation review. Do not start Esi or another family. Consult `aso-yaa-review-20261016/AsoYaa.json` and `.md` for separate acceptance dimensions.
