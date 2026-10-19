# Character form and scenery repair — overnight 15–16 October 2026

Engineering repair checkpoint executed; creative acceptance remains OPEN. Branch `feature/local-milestone-verification`, HEAD `ec7bf0bcf16634a13c12e92433e9731064890e80`. Existing dirty work remains; no commit, push, deployment, installation or campaign remapping.

## Authored source

- `SourceArt/Characters/Kwaku/Authored_v008/`: editable scene/GLB, fixed-camera neutral/closed-lid/deformation views and woven ribbon texture.46 original bones/rest matrices and eleven actions retained.72,114 source vertices; repaired wrist/hand and ankle/foot surfaces each have one connected component and no degenerate faces. Inspected arm-bend volume ratios:0.9746138238077761 left /0.9738187399625937 right. These are limited source measurements, not final deformation approval.
- Closed-lid geometry passed eighteen actual evaluated mesh ray samples. The first v007 attempt failed a slit/seam sample and remains under `Authored_v007_FailedLidSeam01/`; the high-density v007 is retained but inactive. v008 reduces limb topology before native import. Sleeves, skin surface, face proportions, digits, prop contacts and final resemblance still need art review/refinement.
- Native `/Game/Ananse/Characters/Kwaku/Refined_v002/`: exact existing Skeleton, original graph and clips, new mesh/physics/definition/BP/modes. Native visual revision3, source revision`authored-v008`; these differ from studio record version. LOD triangles143192/35796/17897, maximum4influences. Actual bone/socket/material/LOD map is `SourceArt/Characters/Kwaku/NATIVE_FORM_REPAIR_MAP_20261016_v001.json`. No new spider/leopard rig or locomotion framework.
- `SourceArt/Environments/MarketSanctuary/Forms_v002/`: editable replacement scene and12GLBs for actual-sized masonry, writing/notice stands, ledger/pages/clasp, inlaid story pedestal, web-anchor finial and leaf surfaces derived from saved branch locations. Technical/source renders are not final art acceptance. First source revision's poor review layout remains inactive.

## Native scene integration

`AAnanseInteractable` has optional no-collision prop/character presentation components. The original root retains interaction/collision; components cannot own progression or move the root. New authored human idle presentations use existing approved identity families in an opt-in development map, with no species/role rewrite.

Active intended maps: `/Game/Ananse/Maps/Refinement_v007/L_Market_PresentationForms`, `L_Market_EpisodeForms`, `L_Sanctuary_EpisodeForms`. Market episode has16presentation replacements; sanctuary has2. Numeric actor position/rotation/scale, action and identity are unchanged from template v003. Failed map revisions v004(signature),v005(transform string comparison) and unselected v006 are preserved. The corrected guard compares numeric values rather than temporary Transform-object text representations.

**Osebo ownership correction:** v006 would show a static Osebo at the listening marker and another body during pursuit. It is rejected for presentation. v007 uses the authored notice stand at the existing listening interaction; only the existing pursuer owns Osebo's body. Two static human NPC presentations remain(Aso Yaa/Esi), plus six props. The anonymous watcher remains a labelled blockout; the spider remains the existing proxy. Native regression checks enforce eight interaction roots, no visual collision and no Osebo body on the listener.

Runtime opt-in:`-AnanseFormsScenery -AnanseArtRefinement`; episode additionally requires`-AnanseEpisode`. A separate profile`AnanseLabSelection_Forms_v1` preserves prior art/campaign profiles. Actual source/native definition paths are allowlisted; old revisions remain valid, metadata is not executable.

## Publication

Existing studio technical review/publication/browser preview succeeded once: publication`98c392beaf9b49f1bbdd4fa0b23cd959`, payload SHA256`3cae39dbcbd849ef244d5774738ef303c49890c32edb744fb3f6f84f919d8718`. Existing canonical records/Kwaku history and old immutable publications retained. Actual new morph/material bytes and12scenery meshes registered. Technical approval does not establish creative/cultural/rights/mobile approval. No account/resource deployment.

## Executed and pending verification

Evidence:`.local/verification/forms-scenery-20261015/`.

- Actual GLB integrity passed:46joints/11unique clips, finite normalized weights≤4, real nonzero morphs and valid triangles/UVs.
- Python277passed with process-local environment isolation; the initial inherited ROS plugin path failed before collection. No ROS/system Python changes. JavaScript syntax passed.
- Build03 and23native tests passed before the Osebo ownership correction. The original editor-game60second run passed8ready visual roots/3idle characters,10capture/retry, negotiation/protect, sanctuary completion and normal exit. This proves technical integration only; it is not selected after the duplication finding.
- First cooked candidate`Builds/Linux/20261015T225205.770119Z/` is preserved but not selected (static Osebo duplication). Its fingerprint`inputs-01.json` is historical. No failed evidence was erased.
- Build04 failed in the added test because `TestNotNull` requires raw pointers rather than `TObjectPtr`. Build05 corrected this and passed. All24native tests were discovered/executed/passed, including the new ownership regression. Final Python04:277passed in12.25seconds; no skipped/zero-test pass is inferred.

Current: `inputs-02.json` frozen after final source/model updates; candidate02 cooked to `Builds/Linux/20261015T230344.553176Z/`. Executable SHA256 `2f91f97944c12a235dff73a520b58eb49088ac41c0c4f4e1e16c3a2552026e0e`. Three rendered cast sessions passed (full eleven-clip cycle in the first); ordinary 90-second play capture passed with normal exit. Route/outcome, restart, terrain and profile regressions continue; inspect `package-02/execution.json` for executed status. Record ordinary90second WASD/mouse/interaction play without verifier hooks or temporary occlusion cube; this is synthetic input, not physical-device acceptance. Keep output directories and save slots unique.

## Protected artifacts and open gates

Rollback`Builds/Linux/20261015T094630.814642Z/`, original kits/references, source revisions, publications, profiles/saves and failed runs are preserved. Baseline`baseline.json` hashes366original source/content entries; catalogue is intentionally updated through publication and must be audited separately. Do not reset/clean/stage/commit. Archive only explicit immutable payload files, excluding runtime Saved directories/private studio backups.

The tall checkerboard object in the scripted chase captures is a temporary occlusion-test fixture, not a persisted production prop; ordinary-play capture will distinguish it. WIP overlays/anonymous guard/proxy spider and significant asset/composition/audio work remain. Broader character terrain and pursuit navigation, long-session memory, creative/cultural/rights review, campaign mapping, clean-checkout hydration/services and physical Android/iPhone qualification stay open. No final cast/episode/SOTA claim. Keep `-ansimalloc`; detailed CPU-trace shutdown defect remains unresolved. Do not infer device performance from desktop traces.

## Launch and review

From the project root:

```bash
Builds/Linux/20261015T230344.553176Z/Ananse/Binaries/Linux/Ananse /Game/Ananse/Maps/Refinement_v007/L_Market_EpisodeForms -ansimalloc -AnanseEpisode -AnanseArtRefinement -AnanseFormsScenery -windowed -ResX=1280 -ResY=720
```

For cast selection, replace the map with `/Game/Ananse/Maps/Refinement_v007/L_Market_PresentationForms` and omit `-AnanseEpisode`. Forms selection uses its dedicated profile. Ordinary play uses N/New Game, Escape/skip, WASD/mouse, E/interact, 1–3/powers, P/pause and F5/F9/save/load. Synthetic-input evidence is separate from physical keyboard/controller/touch qualification.

The actual ordinary-play frames show remaining crude faces, shoulder/sleeve clearance, sparse architecture and floating interaction labels. The repaired surfaces and replacement prop geometry are substantive editable changes, but these images do not meet final production art quality. Existing ground/dock/trunk drafts, the anonymous watcher and spider proxy remain. No recording, music or final ambient mix was authored in this repair.

## Frozen identities

- `native_source_sha256`: `7264b0646270b26f4ac8912733633ed39a1ce033dbec022f36b07515aae2b5eb`
- `source_asset_sha256`: `2b5389142ea1c65408e63d3e0121dfb20b584d36ea375db59c0b1c84370bc1f2`
- `authoring_source_sha256`: `bfab0454f2ed0b716aa7b6f4ddb90599a4601b4478ad07b8a918339d839af99e`
- `authored_model_sha256`: `72f5f03c501e3d6748cd3a4d48437e8f09ad9c56fd44d726c48200cc5e2c7918`

These identify the actual dirty source/content tree. Inactive preserved revisions are included in the input fingerprint; selected delivery archives are narrower. Engine UE5.8.3 CL58210709, bundled clang20.1.8/.NET10.0.203; Blender4.5.14. Original rollback ELF hash remains `7e2bca3934e08e6e0cbfdfa19946c63cf95f9f0d4af864b6878bab5dab196c17`.

## Corrected-candidate execution checkpoint

Three rendered cast sessions, ordinary90-second synthetic-control gameplay, all six actual route/outcome cases and both separate-process episode checkpoint restarts passed. The normal scripted route tests include10capture/retry cycles each and check8ready presentations/2staticNPCidles. Terrain/cross-family/profile results subsequently passed; final execution ledger is `package-02/execution.json`. The ordinary capture contains180actual frames, without native verification hooks.

## Spider evaluated-contact regression

240-second explicit ContactLab_v006 passed. Measurement stage: OnBoneTransformsFinalized evaluated tarsus + imported tip offset; drift uses latched stance, penetration independently queries actual collision for stance/swing/airborne; no requested-target measurement. Thresholds unchanged: p95stance drift≤2cm, maximum penetration≤0.5cm.

- front_l: drift `3.477239033600199e-06 cm` (`0.000003477239033600`); penetration `3.7946892916806974e-06 cm` (`0.000003794689291681`); stance samples 88462, swing/airborne/invalid exclusions 41532, reach failures 32, support-loss events 13881.
- front_r: drift `3.4832535220630234e-06 cm` (`0.000003483253522063`); penetration `3.5404032132646535e-06 cm` (`0.000003540403213265`); stance samples 85138, swing/airborne/invalid exclusions 44856, reach failures 32, support-loss events 17282.
- rear_l: drift `3.4920647067337995e-06 cm` (`0.000003492064706734`); penetration `3.7641050312231528e-06 cm` (`0.000003764105031223`); stance samples 80766, swing/airborne/invalid exclusions 49228, reach failures 103, support-loss events 24176.
- rear_r: drift `3.4434640383551596e-06 cm` (`0.000003443464038355`); penetration `3.5415714592090808e-06 cm` (`0.000003541571459209`); stance samples 73802, swing/airborne/invalid exclusions 56192, reach failures 85, support-loss events 29993.

Full per-fixture coverage, transitions and exclusions: `.local/verification/forms-scenery-20261015/contact-metrics-final.json`. One former-interior-probe sample rejected. Support-loss counters include declared support-loss fixtures; they are disclosed, not silently removed. No invalid transforms or segment-length error. Native p95query 10.403338432312012µs/solve 28.30335807800293µs; p95frame interval 2.5463621616363525ms. These are native counters/frame intervals, not complete CPU/GPU traces or mobile performance.

## Leopard evaluated-contact regression

160-second LOD2 regression passed. Contact point: Actual finalized foot transform with authored rest ball XY projected onto source sole Z=0cm; offset per actual bone. No requested-target-only samples.. Full sample coverage, pose-exclusion context and penetration contexts remain in `contact-metrics-final.json`.

- L: drift `4.105107291252352e-05 cm` (`0.000041051072912524`); penetration `2.95734189421637e-05 cm` (`0.000029573418942164`); stance samples 65014, swing/airborne/invalid exclusions 21780, support-loss events 42, segment-length error0cm.
- R: drift `0.6851367354393005 cm` (`0.685136735439300537`); penetration `2.95734189421637e-05 cm` (`0.000029573418942164`); stance samples 65236, swing/airborne/invalid exclusions 21558, support-loss events 26, segment-length error0cm.

Native p95query 7.655937194824219µs/solve 13.071112632751465µs; p95frame interval 2.515821695327759ms. Not a long-session memory, general navigation or mobile qualification.

## Final executed result and safety

All19serial verification stages exited0: three cast sessions(first196.32seconds/full clips; other two≥60seconds), ordinary90-second play, six route/outcomes, two episode restarts,240-second spider fixture,160-second leopardLOD2fixture, existing cross-family negative cases, keyboard create/two fresh-process profile restores and review encoding. Each cast session completed20round trips per seven additional designs. These are simulated/native inputs, not physical-controller evidence. Python277passed; native24discovered/executed/passed. Results from separate suites are not combined into a misleading test total.

Actual review video: `.local/verification/forms-scenery-20261015/ordinary-play-01/actual_gameplay_review.mp4` (1280×720,90seconds,720decoded frames at8fps; actual180captured frames held to their recorded times, no interpolated gameplay/audio). SHA256 `f65c82142e82266442acacc91ea305db463f4094cc9470f4577df793121049de`. It demonstrates ordinary controls and remaining visible defects, not a full novice playthrough or final presentation.

Final source audit:59runtime/config,397native-content,111authoring and549model files match frozen inputs02.365protected original source/content files and rollback ELF unchanged. The narrow nonempty AuthenticationToken/SecurityToken assignment scan found0matches across69tracked working files and69index files; index has0staged paths. This does not establish comprehensive history/log/artifact secret absence. Failed reports/revisions remain preserved. No credentials printed, no history rewritten.

Delivery archives are local-only under `.local/deliveries/20261016-form-scenery/`: the Linux tar contains exactly39immutable package entries; runtime Saved/log/profile files are excluded. The additive source zip contains selected editable/native repair files plus input/entry manifests; it requires the existing project's skeletons/graphs/clips and is not a clean-checkout asset-hydration solution. Exact archive hashes are in `.local/verification/forms-scenery-20261015/delivery-archives.json`. No privateDB/reference-image uploads, commits, pushes, deployments, installations or licence/signing changes.

Next bounded work: sculpt/refine Kwaku's face, sleeve/shoulder clearance, digits and skin surface; replace remaining watcher/scenery drafts and floating labels, then review deformation/prop contacts in actual gameplay before extending equivalent repairs to the other cast. Final audio remains missing. Creative/cultural/rights review, broad terrain/navigation, long-session memory, campaign mapping and physical-device gates stay open.
