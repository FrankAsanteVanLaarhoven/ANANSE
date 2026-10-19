# Kwaku and presentation refinement — 15 October 2026

Branch `feature/local-milestone-verification`, HEAD `ec7bf0bcf16634a13c12e92433e9731064890e80`; no commit/push/deployment. The whole cast and storyline are not production-ready. This milestone refines one existing character and presentation section; the other designs retain their previous open art/terrain/clearance gates.

## Active source and native assets

- `SourceArt/Characters/Kwaku/Authored_v006/`: refined saved scene, skinned GLB, original woven texture maps, neutral/deformed/eyelid views. All 46 source bones/rest matrices and eleven actions preserved; 47,676 source vertices / 94,570 triangles. Joined head/neck/torso skin, tapered short sleeves, reduced eye exposure, dark hair and leather gusset/flap pouches. Actual eyelid target deltas exist. This remains stylised WIP: face likeness, hand/wrist joins, sash-edge placement, prop grips, facial acting and final skin/cloth quality still need work.
- Source attempts v003/v004/v005 are retained but inactive. Bulbous sleeves, excessive density, ankle loss from broad remeshing and insufficient eyelid coverage were not promoted as accepted character work. The active scene preserves the original limb geometry and narrows remeshing to the upper body.
- `/Game/Ananse/Characters/Kwaku/Refined_v001/Kwaku`: imported onto the exact existing Skeleton. Original animation graph/clips are reused; native physics/LODs/sockets are separate saved assets. The new definition has visual revision2, original family key and identity. The source revision number, native visual revision and studio record revision are distinct.
- Original Kwaku source and native asset bytes were hashed/backed up before import; native import reported them unchanged. Prior packages, kits, references, publications and saves are protected. No species or power migration.

## Presentation assets

Original deterministic earth/plaster/wood albedo and height-derived normal maps are under `SourceArt/Environments/MarketSanctuary/Refinement_v002/`. Four native materials/eight textures live at `/Game/Ananse/Environments/Refinement_v002/`. No external imagery or reference upload.

New maps under `/Game/Ananse/Maps/Refinement_v003/` preserve the existing geometry/collision transforms. They use a 30,000-lux warm sun, explicit physical exposure and bounded courtyard bounce-light approximations. Dynamic desktop presentation is not baked/mobile acceptance. The first map revision v002 passed a technical run but left the character too dark; it is retained as failed art evidence, not the selected lighting revision.

## Publication and runtime boundary

`studio-refined-01`: technical publication `97b98715ac724d73bc1254f63385c89a`, payload SHA256 `bbf58c2c7c72fd442e694d7b86129e37eac811229ad184e7765e2b8fb9c50737`, Kwaku visual asset record revision3. Existing canonical character records, Kwaku history and nine earlier publications remain unchanged. Temporary local technical roles are not creative/cultural/rights/device approval.

The existing studio renderer now reads actual sparse morph accessors and applies eyelid deltas before skinning. Browser verification compared stable rest images against changed GPU morph pixels, exercised skin animation and actual topology, and reported no page errors. Historical original-source revisions remain allowlisted/readable; cross-revision/family substitutions are rejected.

`-AnanseArtRefinement` opts into versioned presentation and a separate lab profile. Native appearance selection resolves only the two exact published Kwaku bindings; metadata is not executable. Default campaign maps/identity and previous profiles remain separate. The original graph/contact system still owns the final bone pose; expressions do not move root/collision or advance mission state.

## Executed verification and final closeout

Corrected-material candidate D cooked successfully at `Builds/Linux/20261015T093644.028125Z/`. Build09 passed, with 272 Python tests and 22 native tests executed successfully. The source-integrity check verifies actual GLB weights, hierarchy, actions and nonzero sparse morphs. The corrected publication and route verification subsequently passed; final cast-session closeout is recorded below. This does not establish final art acceptance.

Earlier packages A and C exposed a real `MorphTargets` material-usage defect and fell back to Default Material on skin. Their previous pose assertions did not detect that rendering failure. The failed packages/reports remain preserved. All eight refined material usage flags and the import recipe are corrected; native and runtime checks now reject missing morph usage/default material warnings. The exact pre-fix native bytes are archived. The publication now includes exact material dependency hashes. No original Story_v001 material was modified.


Evidence root `.local/verification/art-refinement-20261015/`. Build09, 272 Python tests and all 22 discovered native tests passed. Corrected D rendered 196.31 seconds, all 59 existing clips across seven designs, and 20 spider round trips per design (140 total); no material fallback warnings. New E restoration publication and fresh cook/render passed; new F reapplication publication and fresh cook/render passed. These are technical pose/selection checks, not acceptance of resemblance, props, whole-body deformation or acting. All six route/outcome processes passed on F: negotiation, social and rooftop × protect/expose. Each executed ten capture/retry cycles, reached its distinct consequence dialogue, transitioned to the refined sanctuary, saved completion and exited normally after at least 120 seconds. Input is native simulated verification, not human/controller playtest. Both episode restarts, spider240-second terrain, leopard160-second LOD2 terrain, the seven selector negative cases and three keyboard/profile processes subsequently passed. All three final-candidate cast sessions passed with normal exits, no material fallback warnings, seven independent draft designs and twenty spider round trips per design per session. Full clip-length cycles are additionally covered by corrected D, using the same source/asset bytes except for publication revisions.

No final art, audio, memory-plateau, physical-controller/touch, Android/iOS or full episode acceptance is claimed. Missing voice recordings remain a real production dependency; this milestone does not provide new voice or finished audio assets. Existing allocator and detailed CPU-trace shutdown limitations remain in force.

## Corrected publication cycle and candidate identity

The three selected corrected-material cooks are independent outputs. D uses technical publication `f4f3c0d9be7442219e3e077fb8dbbdce`; E restores the original through NEW publication `e7fbd35e2868439a99b53da85a88d230`; F reapplies through NEW publication `4e885cb0cd4244d8a5b1e5f9c50b6c8b`. Existing canonical characters, Kwaku history and earlier publications were retained. No direct database edits. This is local prototype review, with rights and creative acceptance explicitly unverified.

Current F package: `Builds/Linux/20261015T094630.814642Z/`.

- ELF SHA256: `7e2bca3934e08e6e0cbfdfa19946c63cf95f9f0d4af864b6878bab5dab196c17`.
- Cooked publication payload SHA256: `e2d8a606a83b845d3dfabeab946524338d843be5241994619c421bfff01edd80`.
- Package payload manifest digest: `2d85737e12f0acd419c15ff726a3b8f83e78726a9dc961c9e1ad5401b06d039c` (39 files; includes file sizes and hashes; not an archive hash).
- Frozen dirty/untracked source/content/model/toolchain identity: `inputs-f.json` in the evidence root. Current input audit covers 59 runtime/config files, 325 content files, 108 authoring files and 480 source/model entries. All match. The 35 protected original files match their pre-import hashes; the catalogue intentionally changed through publication.
- Rollback `Builds/Linux/20261015T050301.033364Z/` remains; its recorded ELF hash is unchanged.

Launch the revised free-play presentation with ordinary controls:

```bash
cd /home/favl/Downloads/ANANSE_Production_Starter
Builds/Linux/20261015T094630.814642Z/Ananse/Binaries/Linux/Ananse /Game/Ananse/Maps/Refinement_v003/L_Market_PresentationRefined -AnanseArtRefinement -ansimalloc -windowed -ResX=1280 -ResY=720
```

PageDown selects the next design; Home returns to spider, End to leopard, 1–9 select existing clips, V toggles wireframe, P pauses. F6/F8 use the separate art-test profile `AnanseLabSelection_Art_v2`. Keyboard checks are synthetic owned-window input; physical controller/touch remain untested.

Episode staging launch uses `/Game/Ananse/Maps/Refinement_v003/L_Market_EpisodeRefined -AnanseEpisode -AnanseStoryPresentation -AnanseArtRefinement` with the same binary/allocator. The art flag is an explicit opt-in; campaign identity/species mapping and default maps have not been silently migrated.

The native-window review capture is actual rendered output, silent and recorded with capture overhead. It includes the scripted scenario's completion hold. It is not an uninterrupted human playthrough, finished audio or accepted 60–90-second production-art section.

### Capture supervisor correction

The first final-F negotiation/protect process passed normally, but its capture helper rejected the already-existing `gameplay-review/` output directory. That directory belongs to older candidate C (`20261015T092338.262025Z`), whose material rendering is rejected; it is not final-F visual evidence. The failed command and raw ledger remain intact. Remaining checks resume under `final-f/resumed-execution.json`, retaining the passed first process without pretending the helper passed. The fresh final-F capture target is `gameplay-review-f/` during social/protect. No game process was killed to hide a failure.

The capture log itself also collided on the first resume. The wrapper exited after launching social/protect, so that attempt has no supervised process-exit result and is not qualified. It was allowed to finish naturally. Both negotiation choices passed with observed normal exits. The remaining four route/outcome processes and dependent regressions use the wholly fresh `final-f2/` directory; its ledger incorporates the two passed negotiation results and records new runs separately. Only the waiting closeout supervisor was stopped; no native game was force-stopped to pass a check.

### Visual findings that remain failures of the production-art target

The corrected candidate F capture shows the new material/lighting path working, but the episode still contains visible primitive walls/markers and checkerboard development props. Kwaku's sash-edge placement, proportions, hands and facial construction remain rough. The forest composition and spider presentation also remain blockout/proxy level. These are unfinished assets, not merely approval paperwork. No continuous 60–90-second section is accepted as production-target art/audio in this checkpoint. All seven newer designs retain their draft status; this pass does not finish the cast or environments.

The final route ledger is `final-f3/execution.json`. It retains the two independently passed negotiation processes from `final-f/` and the four new social/rooftop processes under `final-f3/`. Fresh route-test slots use `AnanseArtF3_20261015_*`; existing test saves are preserved. The reused-slot preflight rejection is retained under `final-f2/`; it is not counted as a gameplay pass. The fresh F capture has 290 actual window frames across 80.13 seconds; timestamps govern held frames when encoding. Requested capture rate was eight frames/second, actual capture throughput was lower. No audio/performance/human-input claim.

## Current-candidate spider terrain regression

240.002 seconds, normal exit, zero invalid transforms and zero joint-limit violations. Fixture map `/Game/Characters/AnanseSpider/ContactLab_v006/L_AnanseContactLab`; flat, ramp, steps, landing, uneven, moving and disappearing support. Thresholds remain per-leg p95 drift ≤2 cm and maximum penetration ≤0.5 cm. The full `spider-final-contact-metrics.json` retains per-fixture coverage, reach/support-loss counters and exclusions; this is not a claim that unreachable support never occurs.

| Leg | p95 stance drift (cm; full numeric value) | Max penetration (cm) | Stance samples | Excluded swing/airborne/invalid | Reach failures |
|---|---|---|---:|---:|---:|
| front_l | 3.480523673715652e-06 (0.00000348052367372) | 3.7956892811052967e-06 | 88115 | 42440 | 33 |
| front_r | 3.4764220799843315e-06 (0.00000347642207998) | 3.559450306056533e-06 | 84690 | 45865 | 34 |
| rear_l | 3.473247943475144e-06 (0.00000347324794348) | 3.702759840962244e-06 | 81419 | 49136 | 109 |
| rear_r | 3.441233729972737e-06 (0.00000344123372997) | 3.5346715776540805e-06 | 74588 | 55967 | 90 |

Native p95 frame interval 2.5453739166259766 ms; query 10.618008613586426 μs; solve 27.91592788696289 μs. These are the counters actually recorded plus frame traces, not complete CPU/GPU profiling or mobile performance. The detailed CPU-trace shutdown defect and allocator workaround remain open.

## Current-candidate leopard regression

160.0005 seconds, LOD2 of three, normal exit. Protocol: 8x20s; explicit relocations across flat,15deg ramp,10cm steps,5/10/15cm uneven,moving,disappearing,jump,WebStep transition. Controlled45cm/s walking. Source sole-plane markers; no full mesh collision acceptance. Broader running gait and whole-mesh clearance acceptance remain separate.

| Leg | p95 drift (cm) | Maximum penetration (cm) | Samples |
|---|---|---|---:|
| L | 4.107089262106456e-05 | 2.9577222449006513e-05 | 64741 |
| R | 0.7091946601867676 | 2.9577222449006513e-05 | 64920 |

Invalid transforms: 0; p95 query 7.905997276306152 μs; solve 13.41104507446289 μs; frame interval 2.513356924057007 ms. Full per-leg support coverage/exclusions are preserved in `leopard-final-contact-metrics.json`; thresholds are unchanged.

## Profile, publication and review evidence

Keyboard create and two separate restore processes passed: seven designs selected, actual refined Kwaku binding observed, art profile materialized, movement/gesture exercised, pause time frozen, normal exits and no material fallback warnings. These are synthetic X11 keyboard events, not physical keyboard/controller/touch qualification. The original profile and campaign save schema/history remain separate.

The 60-second original spider/leopard selector regression committed forty transitions/twenty full round trips and seven negative cases, retaining the previous usable pawn on failure and rejecting a late completion. No touch/controller coverage is implied.

Fresh candidate-F review video: `.local/verification/art-refinement-20261015/gameplay-review-f3/actual_gameplay_review.mp4`. Actual window capture, 290 acquired frames held to their recorded times; encoded 641 frames at8fps/1280×720 (80.125 seconds). Decoder and SHA256 checks passed. SHA256 `4d597f44f80c8988033cd273479dccb29ae2094ba2a0ac21acba377e2d3dfd1f`. No recorded audio; includes scripted completion hold.

Narrow safety checks found zero nonempty AuthenticationToken/SecurityToken line assignments in tracked working files/index (59 files each) and the SHA1-verified cooked DefaultEngine.ini entry. This is not a comprehensive scan of all secrets, logs or history. No token rotation or history rewrite.

### Remaining episode-navigation limitation

All six reports record `pursuit_nav_available=false` at their sampled goal. That flag means the last-known position was not successfully projected to navigation; it alone does not prove whether the whole map lacks navigation data. The existing bounded steering/sweep fallback and obstruction-aware capture passed these scripted scenarios. Broad market pathfinding, stuck recovery and human-played pursuit coverage remain open; passing route interactions is not a finished pursuit-art/navigation acceptance.

## Final executed checkpoint

- Python:272 passed (`python-final-02.log`); native:22 discovered/executed/passed (`native-final-02/unreal-automation/index.json`). No overlapping-suite totals are invented.
- Final F rendered cast sessions:`package-f-refined/`, `package-f-refined-02/`, `package-f-refined-03/`, each≥60seconds and normal exit,7designs/59existing clip pose checks,20full spider round trips per design per session. Corrected D additionally completed every clip's full duration in196.31seconds.
- Six route/outcome processes:≥120seconds each,10capture/retry cycles each, actual route prerequisite interactions, distinct consequence dialogue, sanctuary arrival/completion and normal exits. `final-route-results.json` identifies exact reports and assertions; all are native simulated input.
- Separate episode restarts:before choice and sanctuary,≥60seconds each, normal exits. Spider240seconds and leopard160seconds/LOD2 terrain; selector60seconds/20round trips/7negative cases; keyboard create plus2profile-restoration processes passed.
- Current byte audit:59runtime/config,325native/content,108authoring and480model/source entries match the frozen F identity;35protected originals unchanged. Git index remains empty; no commit/push/deployment.

The final package's original39 immutable files remain byte-identical.37additional files are confined to `Ananse/Saved/` and `Engine/Saved/` (runtime configuration and dedicated test saves); these are preserved in the exercised directory and excluded from clean delivery. The strict whole-directory audit failure is retained; the separate payload audit explicitly verifies every original file and rejects any new non-Saved file. CrashReportClient configuration creation is not evidence of a crash; selected processes exited normally.

### Reproduction commands

Use fresh output paths and dedicated NEW save-slot names; existing output directories and slots are deliberately rejected.

```bash
.venv/bin/python -m pytest -q
UE_ROOT=/home/favl/Unreal/UE_5.8.3-58210709 .venv/bin/python scripts/unreal.py test --allocator ansi --evidence-dir .local/verification/NEW-native-art-check
.venv/bin/python scripts/check_refined_kwaku.py .local/verification/NEW-source-art-check.json
```

The exact executed native commands, package identity and process outcomes are in the evidence root. Detailed launch commands are preserved in each `command.json` or `launch.json`; do not reuse those dedicated save slots blindly.

### Next compact milestone

Repair Kwaku face/eyelids/hands and the mispositioned sash-edge geometry, refine prop contacts/deformation and replace visible market/forest blockout geometry/markers. Establish a genuinely continuous playable60–90-second audiovisual section before calling the presentation production-target. Other cast designs need their own substantial geometry/performance passes, broader terrain/clearance tests and reviewed campaign bindings. Final recordings/mix, environment composition/lighting, creative/cultural/rights acceptance, long-session memory stability, broad pursuit navigation, clean-checkout asset hydration, services and physical Android/iPhone qualification remain open. No production-ready cast/episode or SOTA claim is supported by this checkpoint.

### Frozen aggregate identities

- `native_source_sha256`: `b2e7e87beb3f5f156752918090809c98c1b05073c70ba722c9cfc68e84a04f0f`.
- `source_asset_sha256`: `a537af51785403d9076aabb7ef8e1c3457d06e8b46a13e447026bc6a975e8e72`.
- `authoring_source_sha256`: `9e15c579985ca770d12cbe2cccb7a9cc39507f410fd93ba21be3ee6680bfc3c3`.
- `authored_model_sha256`: `ae75705d88792f7e2ae040a15f08deb115fe7bea3c549bd9b0040978d3d23d07`.

Engine5.8.3/changelist58210709; Blender4.5.14LTS/build62c1db4208e8. The exact toolchain lock is included in the runtime fingerprint. Active scene SHA256 `36a5a69311a593787b2ba2f3a1970289f9617e19b5d93163328b8b775ff8edb8`; GLB `5c3c803c4e0f8d69c66b6c9a51252c0d6e4b8fc88a95aa228fdd05240a96d7cf`.

## Local delivery artifacts

- Clean tested payload: `.local/deliveries/20261015-art-refinement/ANANSE_Linux_Art_Refinement_20261015_v001.tar.gz`,425,451,951bytes,39verified entries, no runtime Saved files. SHA256 `a58d0b2b55121d1f26897c2f356572c1744257565bc5a27713b80d57320db4ba`. Extract into a NEW directory, retaining permissions; its relative `Ananse/Binaries/Linux/Ananse` is the same verified ELF. The original exercised directory remains preserved with test saves/evidence.
- Additive source/native WIP archive: `.local/deliveries/20261015-art-refinement/ANANSE_Art_Refinement_20261015_v002.zip`. Includes actual saved scene/GLB/textures/model-derived views, new native assets/maps, project source/tests and frozen build inputs. Requires the existing project/original Kwaku Skeleton, graph and clips. This is not another starter project or a production-ready art kit. Archive hash and per-entry validation are in `delivery-archive.json` in the evidence root.
- Actual silent game-window review: `gameplay-review-f3/actual_gameplay_review.mp4` in the evidence root; source/model technical views are under `SourceArt/Characters/Kwaku/Authored_v006/Technical_v002/`.

No assets/reference images were uploaded, no account/resource was created, no package submitted, no signing data changed and no Git commit/staging/push occurred. Failed attempts, original kits/publications/profiles and rollback packages remain. Local technical publication does not confer creative approval.

Source archive v002 corrects the episode launch note to include `-AnanseEpisode`, required to enable the episode lifecycle (and its pursuit). The v001 archive is retained but superseded for instructions; mesh/native/runtime payload bytes are unchanged.
