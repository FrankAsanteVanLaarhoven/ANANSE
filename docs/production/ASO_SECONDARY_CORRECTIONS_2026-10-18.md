# Aso secondary-motion corrections — 18 October 2026

Bounded engineering correction checkpoint. Human clearance/contact/naturalness review remains required. No creative approval, publication, commit or deployment.

## Repository and protected baseline

Branch `feature/local-milestone-verification`; HEAD `ec7bf0bcf16634a13c12e92433e9731064890e80`. Existing dirty work preserved. Frozen candidate `Builds/Linux/20261018T043700.710245Z/` and original review ZIP are unchanged. All1,686 prior native files and1,139 prior authored-model entries match the baseline; all39 frozen package payload files match. Catalogue/publication bytes are unchanged. New tests use isolated selection profiles and newly named mission slots, without campaign-save migration.

## Reproduction and root causes

Frozen revision5 Aso, exact `Contact_v002` mesh/ABP, `InspectEvidence`/`WalkControlled`/`Turn`, was replayed with the spring on/off. Both old technical checks passed despite visible clipping; final CPU-skinned geometry intersected in both modes. The spring was not established as the original cause. Raw baseline reports, trial scenes19..26, failed probes/builds and rejected broad fitting proposals remain in `.local/verification/aso-motion-correction-20261018/`.

Upper thigh weighting had substantial shin influence well above the real knee; calf skin had foot influence well above the ankle. Corrected those Aso-only weights with unchanged leg rest vertices,48-bone rest hierarchy and gait. The old Turn pelvis localZ angle was sideways roll, corrected to actual localY yaw, same duration/root movement. Lower garment drape/underlayer clearance was authored, including a small inner-layer ease for the one remaining disabled-spring failure in v026. Original source v018 remains unchanged.

Aso-only `Dress_L`/`Dress_R` base-pose correction preserves parent yaw, gravity-aligns the lower garment and bounds its authored relative rotation to4 degrees. It executes before the existing spring and contact solve in the single final deformation path. No root/collision/contact solver/hand deformation authority changed. The existing `-AnanseDisableSecondaryMotion` rollback remains; `-AnanseDisableAsoGarmentClearance` is a separate diagnostic bypass of this base-pose correction. No other rig is selected by its exact-mesh guard.

## Actual saved assets

- Editable final scene: `SourceArt/Characters/AsoYaa/Authored_v027/AsoYaa.blend`.
- Interchange and complete source rig map: sibling `AsoYaa.glb`, `rig-map.json`.
- Support scene/export: `SourceArt/Characters/AsoYaa/Props_v003/LedgerStand.blend` / `.glb`.
- Native mesh/skeleton/BP/ABP/DA/IK/CR and16 clips: `/Game/Ananse/Characters/AsoYaa/Clearance_v001/`.
- Lab: `/Game/Ananse/Maps/Clearance_v001/L_AsoYaaCharacterLab`.
- Actual active physics is reused `/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa_PhysicsAsset.AsoYaa_PhysicsAsset`, not the unused generated new-folder physics target.
- Exact saved/generated classes, native parent indices/axes/rest transforms, sockets, clip paths and runtime observations: `resolved-native-bindings.json`. This corrects a stale bootstrap top-level physics field retained in raw `finalize-05/native.json`; its newly described `rig.physics` and actual packaged transitions agree on Contact_v002.

DCC4.5.14 LTS; Unreal5.8.3 CL58210709. Source metres, native centimetres, qualified existing axis/handedness conversion retained.48 bones,149,023 source vertices,296,532 source triangles; finite normalized source weights, maximum4 influences. Native LOD0/1/2 triangles296,532/74,132/37,065; maximum3 native influences;9 material slots. These are engineering inventories, not a mobile or final-art pass. No COLOR_0/material-override or old input-mask changes.

## Ledger support contract

`InspectEvidence` remains8 seconds. Before1.6s the ledger is on the visible receiving fixture;1.6..6.8s it is supported by both hands via `socket_ledger_R` and existing authored/contact pose. At6.8s the placement pose coincides with the receiving surface; the hands then withdraw until8s. The prop is no longer left suspended in the withdrawn-hand interval. Cancellation/presentation cuts explicitly stow both ledger and fixture; this is a labelled presentation cut, not a claimed physical handoff.

The fixture is nonblocking lab presentation geometry, with a cantilever/counterweight base avoiding straight table legs through the skirt. Its vertical extent is fitted from the sole plane to the actual placement plane; it does not support or move gameplay collision. Campaign Aso single-node playback remains unchanged, spring migration PENDING. Legacy clip paths retain their existing helper branch. No campaign NPC migration or new state machine.

Ten full evaluated cycles passed, plus cancellation, pause/resume, cut/skip presentation and final re-entry.53,722 support samples; zero unsupported under the defined proxy. Max nearest selected-hand-to-book solid-bounds gap: left0.0207116cm/right0.0089134cm; rest mapping error0.0000049725cm. Table bounds gap ~1.42e-14cm (alignment by construction, not a physics result). The independent21 held-pose all-hand box diagnostic found no vertices inside the book bounds and maximum nearest box-surface gap0.0201062cm. These bounded geometric checks do not approve finger anatomy, all penetrations, natural grip or every blend.

## Evaluated robe coverage

80 actual final-pose samples per editor spring mode and80 from the final cooked package: WalkControlled12, Turn12, InspectEvidence32, LimbIsolation24. All observed triangle-intersection counts zero. Minimum unsigned separation: enabled editor2.4372844696cm; disabled2.6324627399cm; packaged2.9978957176cm. Different sampled timing prevents treating these minima as a controlled spring-effect comparison.

Part mapping is from actual imported rest vertices to source parts, max error0.0000137541cm. Native final skin matrices include the contact/garment/spring evaluation. Body restZ18..90cm, garment restZ16..110cm; feet/upper torso/facial morph-only regions excluded. No active morph targets on inspected leg/garment parts. LOD0,4Hz snapshots, not all intermediate frames/LODs. Unsigned distances are not penetration depth or general inside/outside proof. Earlier baseline used a smaller documented region; no percentage improvement claimed.

## Fresh checks, separate from historical results

- 382 Python tests passed; JavaScript syntax passed.
- 38 native tests executed:4 clean success,34 success with retained warnings,0 failed/not-run. New `Ananse.Animation.AsoSupportedPlacement` passed. Historical382/37/ten packaged results are not relabelled fresh.
- Aso16 clips/flat contacts/20 round trips passed; separate-process profile restoration passed.
- Aso ↔ Ananse20 full round trips/40 committed transitions and existing negative cases passed; exact new mesh/skeleton/ABP and reused physics recorded. Synthetic input only.
- Ten ledger cycles and defined negative cases passed; same package final evaluated geometry passed.
- Negotiation protect/expose, cinematic normal finish/skip/cancel/pause/retry, and before-choice/after-outcome restarts passed in the existing campaign path. Not a rerun of all six route/outcome cases or proof of campaign spring migration.
- Unchanged Osebo nine-motion regression passed. Other terrain suites were not relabelled as freshly rerun.

## Three continuous diagnostic recordings

| Clip | Real reads | Capture fps | Interval p95/max ms | Estimated missed30Hz slots |
|---|---:|---:|---:|---:|
| Aso walk/turn | 451 | 30.0028 | 34.547 / 35.872 | 0 |
| Aso ledger | 449 | 29.8689 | 34.452 / 129.119 | 3 |
| Unchanged Osebo start/turn/stop/settle | 451 | 30.0017 | 34.648 / 40.030 | 0 |

Each source capture spans ~15 real seconds. One encoded frame per actual read at30fps, no held-frame upconversion/interpolation/audio. Ledger encoded14.9667s vs15.0042s captured; use original capture timestamps. All1,351 selected encoded frames decoded through the installed movie sequencer. First readback attempt cropped the centre instead of scaling and failed a nonblack check; raw failure retained. Corrected explicit source-dimension scaling passed every frame; decoder process also used a nonzero Python-error exit and required output artifacts.

Aso walk/turn uses runtime-only FOV100 for complete hem framing; component camera stays unchanged. Osebo uses the unchanged rear camera/old assets at45cm/s lab speed; no high-speed cape qualification. Earlier cropped widescreen/square captures remain available but are not the selected full-body evidence. Videos and capture manifests: `diagnostic-aso-wide/video/`, `diagnostic-ledger/video/`, `diagnostic-fullbody-leopard/video/` under the evidence root.

## Fresh package and hashes

Package: `Builds/Linux/20261018T075353.595447Z/`

- Executable SHA256 `944fd22611bab079dab2978c13fbe2be6f71dc0ed1a500dd0617304f60df3913`
- 39-file payload manifest SHA256 `3c62a17fc70cae14f75421efc335fd5432fe65fd05e89a73c9cc0ce4873da060`
- 38 new native files canonical SHA256 `81b5a6d35805ff11fca4260e9d7cb8fb13081ce4712748a1e3f0eca7c6eea380`
- Final scene SHA256 `f299508844de48d229f15420badc221952aa18544c7e912e50a26c2b9838cfcd`
- Final GLB SHA256 `e3952fa2ca6bcaca055a2cdab6eff78debf264c2673e89fa9bfef0e77a71a40d`

Full per-file source/content/package hashes and canonical hashing recipe are in `final-identity.json` / `payload-final.json`. Raw commands, statuses and frame traces retained locally. CPU skin-buffer retention was process-only for probes, not performance/memory qualification. Allocator workaround retained; detailed CPU-tracing shutdown limitation remains.

Verified launch form (native executable, isolated profile):

```bash
cd /home/favl/Downloads/ANANSE_Production_Starter
task_profile=$(mktemp -d /tmp/ananse-aso-review.XXXXXX)
./Builds/Linux/20261018T075353.595447Z/Ananse/Binaries/Linux/Ananse /Game/Ananse/Maps/Clearance_v001/L_AsoYaaCharacterLab -ansimalloc -windowed -ResX=960 -ResY=960 -AnanseAsoReview -AnanseAsoContact -AnanseAsoClearance -AnanseArtPass2 -AnanseVisualReview -AnanseInteractionRefinement -AnanseArtRefinement -AnanseNeutralLabLighting -AnanseMotionReviewClean -AnanseAsoDiagnosticCamera '-ExecCmds=fov 100' "-UserDir=$task_profile"
```

0 automatic locomotion;3 authored Turn;5 ledger;P pause. Close normally. Exact recorded launch/input timelines are in the diagnostic launch/process files.

## Changed runtime/config inputs relative to frozen motion checkpoint

- `Unreal/Config/DefaultGame.ini`
- `Unreal/Source/Ananse/AnanseAsoClearanceTests.cpp`
- `Unreal/Source/Ananse/AnanseAsoLedger.cpp`
- `Unreal/Source/Ananse/AnanseAsoSurfaceProbe.cpp`
- `Unreal/Source/Ananse/AnanseAsoSurfaceProbe.h`
- `Unreal/Source/Ananse/AnanseAuthoredAnimation.cpp`
- `Unreal/Source/Ananse/AnanseCastLab.cpp`
- `Unreal/Source/Ananse/AnanseCastLab.h`
- `Unreal/Source/Ananse/AnanseLabSelection.cpp`
- `Unreal/Source/Ananse/AnanseWorld.cpp`

Exact touched runtime/config/authoring/import/final-pose/capture/check source paths and hashes are recorded in `task-source-files.json` in the review bundle and remain uncommitted. Source trials and evidence are local artifacts, not staged repository content.

## Remaining gates and stop boundary

SM-P0-01/02 retain FAIL_PENDING_REVIEW with new correction evidence; no human decision is inferred. All ten creative/readability fields in the12-gate Aso matrix remain REVIEW_REQUIRED; source/package verified separately. The fuller/structured robe silhouette, hands, face, fixture presentation and cloth naturalness still require human judgement. Other rigs' naturalness, Kwaku/hornbill loose-cloth authoring, campaign spring binding, interactive water/boats, final audio and full environmental motion remain outside this correction.

Baked lighting BLOCKED; mobile UNQUALIFIED; long-session memory/uncovered navigation remain open. No geometry propagation, maps/cast expansion, publication, commit/push/merge/deploy or system-tool changes. Stop here for human review of the three recordings and scoped metrics.

Skill note: task-observer informed final-pose/anatomical-weight validation. Skill-retrieval was unavailable; no retrieved skill materially influenced implementation. No skill installation or policy override.
