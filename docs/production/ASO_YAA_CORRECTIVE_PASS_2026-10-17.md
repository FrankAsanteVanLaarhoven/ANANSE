# Aso Yaa corrective art/animation checkpoint — 17 October 2026

Branch `feature/local-milestone-verification`; HEAD `ec7bf0bcf16634a13c12e92433e9731064890e80`. Work is uncommitted. This is a bounded engineering/art-review candidate, not final character acceptance. Only Aso Yaa was authored.

## Result

A complete eight-second ledger reach/contact/secure-hold/inspection/presentation/return/release performance, sewn robe/yoke and fitted sleeves, distinct hand poses, mission-driven facial responses and seven negotiation shots are integrated. A short broken-promise reaction uses the existing cinematic controller in visual-only mode: it preserves mission dialogue and never awards a durable event. Evidence ownership now produces attentive listening until actual E negotiation begins the full inspection; no quest rule or outcome state machine was replaced.

The visible forearm poke-through was corrected by reducing only the complete hidden arm surface's radial volume to fit the sleeve. Rest bones, all 16 motion curves and authoritative root/collision remain unchanged by that correction. Hero hand/face quality still requires human review.

## Actual source and native assets

- Editable scene: `SourceArt/Characters/AsoYaa/Authored_v018/AsoYaa.blend`; SHA-256 `fcd3f295863bf8ddb43cc155facd7c6e61b7fb3c367c4be90f8d127657de2521`.
- Character GLB: `SourceArt/Characters/AsoYaa/Authored_v018/AsoYaa.glb`; SHA-256 `b48d260dcdeb866a9d29613ca77e1e353fcb8ec1e7211ff9f11e904913c9d291`.
- Editable separate book remains in the scene; static export `SourceArt/Characters/AsoYaa/Authored_v017/Ledger.glb`.
- Evidence stand: `SourceArt/Characters/AsoYaa/Props_v002/LedgerStand.blend` and `.glb`. Its top aligns with the book's actual underside; decorative collision is disabled and the canonical interaction root retained.
- Exact native paths, 48 bone parent indices/rest quaternions/axes, socket transforms, physics/LOD counts: `SourceArt/Characters/AsoYaa/NATIVE_RIG_MAP_20261017_v002.json`; re-open evidence `.local/verification/aso-corrective-20261016/reopen-final-03/native.json`.
- Final source/asset deltas: `.local/verification/aso-corrective-20261016/candidate-03/changed-paths.json`. Old rejected/intermediate scenes and native revisions remain preserved.

- mesh: `/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa.AsoYaa`
- skeleton: `/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa_Skeleton.AsoYaa_Skeleton`
- physics: `/Game/Ananse/Characters/AsoYaa/Contact_v002/AsoYaa_PhysicsAsset.AsoYaa_PhysicsAsset`
- ik: `/Game/Ananse/Characters/AsoYaa/Contact_v002/IK_AsoYaa.IK_AsoYaa`
- control_rig: `/Game/Ananse/Characters/AsoYaa/Contact_v002/CR_AsoYaa.CR_AsoYaa`
- animation_blueprint: `/Game/Ananse/Characters/AsoYaa/Contact_v002/ABP_AsoYaa.ABP_AsoYaa`
- blueprint: `/Game/Ananse/Characters/AsoYaa/Contact_v002/BP_AsoYaa.BP_AsoYaa`
- generated_class: `/Game/Ananse/Characters/AsoYaa/Contact_v002/BP_AsoYaa.BP_AsoYaa_C`
- definition: `/Game/Ananse/Characters/AsoYaa/Contact_v002/DA_AsoYaa.DA_AsoYaa`
- map: `/Game/Ananse/Maps/Contact_v002/L_AsoYaaCharacterLab`

The Blueprint derives from the existing cast player class; the data asset uses the allowlisted native character-definition schema. IK/Control Rig are functional authoring assets; the existing ABP/contact proxy remains the single runtime pose path. Props update on the game thread after final bone evaluation. They never drive root movement or supply pawn support.

The current mesh has 3 materialised native LODs: 281,172 / 140,585 / 70,291 triangles, with max 3 native influences (source max 4). These are unapproved mobile budgets. Physics is kinematic normal-play policy with render-mesh/prop collision disabled, not ragdoll or joint-limit approval. Native revision 5 is an unpublished development-review override. Published Aso revision 3 and publication `f024326dc79048c7aec7055c6d6dc7b6` remain unchanged. No studio publication was made in this pass.

Mapped motion identities (16 actual distinct actions; InspectEvidence is now 8 seconds):

IdleStrategist, WalkControlled, Turn, Listen, InspectEvidence, Consider, NegotiateOpen, NegotiateFirm, Agreement, Refusal, ProtectWitnesses, ReactBrokenPromise, DialogueNeutral, DialogueConcern, DialogueResolve, LimbIsolation.

## Qualification and retained failures

The GLB importer exposed a 90-degree mesh/skeleton frame mismatch. Six rest-marker probes established the raw frame; the existing one-time geometry correction rotated positions, normals and all morph deltas +90 degrees, leaving the skeleton unchanged. Corresponding lab/NPC facing corrections maintain the intended viewing direction. A fresh raw-geometry proof precedes correction after mesh reimport, preventing a double conversion. The imported bone poses match all 48 source bones at 8 sampled times within 0.00009 cm. Thirty actual native LOD0 skinned markers match the source within 0.00073 cm; see `native-source-skin-final.json`.

The source test sampled all 133 held frames from 1.6–6.0 seconds, without exclusions: no measured hand/book OBB penetration. Worst nearest palm/ thumb gaps are below 0.8 mm; index/middle fingers below 0.6 mm; relaxed ring/little fingers up to 4.94 mm. This is a surface-correspondence/contact engineering result, not approval of human anatomy. Source018's 16 motion-curve hashes equal source017's; native clip bytes remained unchanged during the final hidden-arm mesh correction.

The final packaged lab observed 715 held-prop samples, all 5 phase captures, and maximum socket/prop binding error 1.0658141036401503e-14 cm. Correct normal release returns the book to its non-blocking stand. Skip/cancel safely restores the presentation; it does not preserve an unfinished grip indefinitely.

Preserved failures include: rejected early garment unions that tore during arm raises; initial penetrating/floating grip measurements; editor LODInfo/render-LOD mismatch (actual regeneration fixed it); reimports that left old animation bytes; raw mesh/skeleton frame mismatch; old-path-only observation checker (all original required pose identities retained); visual reaction clearing mission-owned subtitles (cleanup guarded); decorative mesh replacement restoring blocking collision (decoration disabled, canonical collider untouched); failed relative-path/enum/API invocations. Details and original files/logs remain in `.local/verification/aso-corrective-20261016/`. The earlier packages `222815` and `223439` are not final acceptance candidates and were not overwritten. No crash or threshold was suppressed.

## Final executed tests

- Python: **317 passed**, final log copied into the evidence root; no overlapping input-package tests added into that count.
- Native: **32 passed**, `candidate-03/native-tests-final-02/unreal-automation/index.json`.
- Native build 21 and final cook exited 0. JavaScript syntax checks for both existing studio scripts exited 0; no JS changes.
- All **12 packaged stages** exited normally on the same final ELF. Three rendered >=60-second sessions each completed 20 Aso round trips (40 committed transitions) with Ananse, Kwaku and Osebo respectively; a fourth fresh process restored the saved Aso profile and repeated checks.
- Aso/Ananse and retained Ananse/Osebo selection suites each completed 40 transitions and 7 exact negative cases, including missing assets, wrong rig, obstructed spawn, cancellation and stale completion. Previous usable pawns were retained on failure. New Aso readiness also rejects a missing book dependency.
- Negotiation protect and expose/broken-promise routes passed evidence/permit, played pursuit/ten capture-retries/escape, actual choice, consequence, sanctuary and completion. No development outcome setter was used as choice evidence.
- The new sequence passed normal finish, Escape skip, P pause/resume, interruption/cancel/retry and camera/input/movement/possession restoration. Reaction shots do not add the visual-only event to save state.
- Fresh-process before-choice and sanctuary restarts passed, plus the existing Kwaku ledger interaction regression.
- Spider/leopard terrain was not rerun: its movement/contact solver/assets were not modified. Current Aso measures below cover the lab's declared flat `StaticMeshActor_0` fixture only; thresholds remain per-foot p95 <=2 cm, maximum penetration <=0.5 cm. Exclusions are published below and in each full report.

| Foot | Samples | Excluded swing/airborne/invalid | p95 stance drift cm | Maximum penetration cm |
|---|---:|---:|---:|---:|
| L | 5193 | 2967 | 1.6253197827609256e-05 (0.000016253198) | 9.6406765806023031e-06 (0.000009640677) |
| R | 5175 | 2985 | 1.6234369468293153e-05 (0.000016234369) | 1.0287475561199244e-05 (0.000010287476) |

Raw commands/assertion identities/results are in `candidate-03/final-cast-stages.json`, `final-episode-stages.json`, `final-results.json` and each stage's command/process/native JSON. Simulated native input does not establish physical keyboard/controller/touch qualification. Frame traces/native contact timing remain bounded to the measurements supported; the detailed CPU-trace shutdown limitation is preserved.

## Package and launch

- Fresh package: `Builds/Linux/20261016T232829.030413Z/`.
- ELF SHA-256: `812dfa37b9e1743ae11b1a86f18641dddb3905f273b4116c79701c39ab3750b1`.
- Payload manifest SHA-256: `a829acd7ee12d7db60fb52f1dce73d526acb15f947f7cbc1927f2607a3ce1f52` (SHA-256 of canonical sorted compact JSON of the 39 relative-path/file-hash entries).
- Frozen dirty-tree identities: `.local/verification/aso-corrective-20261016/candidate-03/inputs-final.json`. Current hashes matched after qualification.

The executable/map/flags were exercised by supervisors. The interactive command below omits automation and uses a dedicated user directory; physical/manual hardware input remains unqualified.

```bash
"/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261016T232829.030413Z/Ananse/Binaries/Linux/Ananse" /Game/Ananse/Maps/Contact_v002/L_Market_AsoNegotiation -AnanseAsoContact -AnanseAsoReview -AnanseAcceptedVisuals -AnanseEpisode -AnanseStoryPresentation -AnanseArtRefinement -AnanseFormsScenery -AnanseInteractionRefinement -ansimalloc -windowed -ResX=1280 -ResY=720 -UserDir="/home/favl/Downloads/ANANSE_Production_Starter/.local/aso-corrective-player-review-03"
```

## Visual review and safety

Current saved-scene face/hand/robe/pose captures are in `source-review-05/`; actual topology, orthographic and skeleton sheets in `technical-views-02/`. They derive from source018, not illustration-style wireframes. Camera matrices/scale/exposure and source hashes accompany them. Source solid sheets are visual technical views, not manufacturing CAD.

The final review bundle contains those images, reference/before/after comparison, genuine packaged ledger phases, two-shot/reaction/insert/agreement/broken-promise frames, an 18-second negotiation video and a 3-second reaction video. Videos are silent, 10-fps sampled native viewport images held to recorded request times, without generated/interpolated poses; screenshot readback delay applies. This is not performance profiling footage.

The separate technical/creative matrix is `aso-yaa-corrective-review-20261017/AsoYaa.json` and `.md`. Every creative gate remains REVIEW_REQUIRED. Specific remaining limitations:

- Creative likeness, face, hand anatomy, robe/fold quality, prop credibility and cinematic composition await human approval.
- Hands remain stylised with blunt forms and two-segment finger chains; a numerical contact pass is not hero-hand art approval.
- Robe material detail, cuff fit and deformation away from the declared pose set require visual review.
- Source hand-to-book measurements cover 133 held frames (1.6–6.0 s), not every possible gesture, terrain or interaction. Ring/little fingers are relaxed support digits and do not all press the book.
- No approved voice recordings, speech visemes or lip-sync. Both review videos are silent.
- LOD0 281172 triangles / LOD2 70291 triangles remain heavy, unapproved mobile budgets; physical controller/touch, Android/iOS, long-session memory and broad terrain/navigation remain unqualified.
- Normal-play physics is kinematic with non-blocking render mesh/prop; ragdoll and detailed joint/physics art review remain open.
- Corrective appearance is unpublished. Existing studio publication remains unchanged; the new native revision is selected only by the explicit development-review flag.
- Source/environment blockouts, world debug labels and other cast drafts remain. No other character was authored in this pass.

Preservation audit: all 958 prior Aso-checkpoint asset files, 912 prior model files, and the 39-file prior Aso and accepted-episode payloads are unchanged. All final frozen inputs and 39 final payload entries match. Original references, all earlier publications/canonical characters/Kwaku history (including revision 2), profiles, saves and failure evidence were preserved. Test-specific save slots/profile directories were used. No commit, push, merge, external upload, publication, deployment, acquisition, driver/toolchain/global-Python or unrelated-project change occurred. Source scenes/native working bytes have incremental local safety snapshots; these require the retained existing project, not a new starter.

No external skill-retrieval endpoint was available; implementation used the project's existing qualified DCC/import/rig/cinematic/verification workflows and installed engine source. Stop for human Aso Yaa review. Do not begin Esi, Kojo, Kofi or another family.
