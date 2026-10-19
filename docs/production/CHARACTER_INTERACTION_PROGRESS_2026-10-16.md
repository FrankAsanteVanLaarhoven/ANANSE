# Character surfaces and ledger interaction — 16 October 2026

Engineering checkpoint; **not final character acceptance**. Branch `feature/local-milestone-verification`; HEAD `ec7bf0bcf16634a13c12e92433e9731064890e80`; work remains uncommitted and unstaged. No push, deployment, installation, purchase, licence/signing or campaign-species change.

## Result and selected assets

Kwaku's face/neck, inset eyes/closing lids, crop, garment/sleeve surfaces, tapered digits and weighted arm topology were refined. A real two-hand InspectLedger action presents a separate non-colliding book. Leopard cheek/muzzle, arm/paw surfaces, digits and original rosette texture/UV density were refined. Genuine cooked captures show the corrected continuous arms/book; stiff fingers, simple face/cloth and environment art remain visible. This is a WIP improvement, not reference-likeness or natural-grasp approval.

- Editable Kwaku: `SourceArt/Characters/Kwaku/Authored_v016/` (`Kwaku.blend`, skinnedGLB, separate`Ledger.glb`, technical views/turntable/probes). v016 preserves v015 geometry/actions byte-for-byte and adds calibrated native-frame binding metadata. Original46rest joints and eleven moving actions retained; only this revision's InspectLedger was reauthored. Source134531visible/export vertices, maximum4influences.
- Editable leopard: `SourceArt/Characters/OseboLeopard/Authored_v005/`; same64rest joints and nine moving actions,59003visible/export vertices, maximum4influences. Model-derived `Technical_v002/` and `Turntable_v001/` retained. It remains lab/free-play only; human campaign Osebo is unchanged.
- Native Kwaku: `/Game/Ananse/Characters/Kwaku/Interactions_v005/`, definition visual revision5. Own mesh/physics/materials/BP/typed definition/threeLODs; original Skeleton/Animation Blueprint/ten clips reused. Qualified InspectLedger sequence remains `/Game/Ananse/Characters/Kwaku/Interactions_v003/KwakuInspectLedger.KwakuInspectLedger`; its earlier mesh binding was rejected, its clip was correct. Separate ledger is under new Props.
- Native leopard: `/Game/Ananse/Characters/OseboLeopard/Interactions_v003/`, definition revision2; original feline Skeleton/Animation Blueprint/nine clips reused. Actual class, bone/parent/rest/socket/clip/LOD maps are `SourceArt/Characters/<Kwaku|OseboLeopard>/NATIVE_INTERACTION_MAP_20261016_v001.json`.
- Three nativeLOD triangle counts: Kwaku266729/133363/66682; leopard117548/58773/29385. Five Kwaku mesh sockets/four retained feline sockets resolve. These large meshes and kinematic physics configurations still require visual physics/LOD review and mobile budget qualification.
- Four maps: `/Game/Ananse/Maps/Interactions_v003/` containing `L_Market_InteractionsLab`, `L_Market_EpisodeInteractions`, `L_Sanctuary_EpisodeInteractions`, `L_LeopardContactInteractions`. They reuse accepted environment templates; no new finished environment pass is claimed here.

## Binding repair and authority

Earlier editor graph assertions passed while detached skin was visibly wrong. Native joint/rest matrices matched source, but mesh vertices were yaw270 relative to the retained skeleton. Nativev004 yaw0 experiment failed. Selected imports keep qualified yaw-90 and apply a once-only native MeshDescription yaw90 correction to positions, normals, tangents and morph deltas. Actual rest vertex/weight and animated skin probes now match source within0.01cm/0.1cm; original joint frames, root/collision and animation bindings remain unchanged. This limited probe coverage does not approve the full surface.

Gameplay retains root/collision, powers, routes and durable-event authority. The separate no-collision ledger latches once relative to the evaluated hand during the actual held clip phase, including visual body-height adjustment. Reset/capture/switching clear transient prop/pose/contact state; resumed episode movement cancels cosmetic inspection. One final pose path remains. Arm gestures are retained with leg contacts. No extra gameplay timer or duplicate mission grant was introduced.

## Executed verification — this candidate

- Full Python suite: **280passed in12.37seconds** (`python-07.log`); JavaScript syntax checks passed. Build16passed.
- Native: **26discovered/executed/passed**,0failed/unrun;2clean and24with the retained “Wayland before SDL initialization” warning. Original24identities retained; two new tests cover real native mesh/clip/prop/socket/skin-probe bindings and protected-preparation rejection. Latest report: `native-tests-05/unreal-automation/index.json`.
- Reopened saved source: exact original rest matrices/parents, eleven/nine actually moving actions, finite nonnegative normalized weights/max4influences, Kwaku nonzero sparse eyelid targets and18closed-lid rays passed. Bent-arm volume ratios: Kwaku0.9516772147264816/0.9509738459343628; leopard0.9663103940036829/0.9666118469782103. Two source hand vertices meet the solid ledger within0.0005cm; minimum distance is not whole-hand grasp/penetration acceptance.
- Three rendered cast sessions passed; first includes every clip/portrait/ledger/reset cycle. Each exceeded60seconds. Six route/outcome cases passed through actual mission scenario prerequisites with ten capture/retry cycles; two separate restarts passed before consequence and after sanctuary arrival. These are native scenario assertions, separate from ordinary controls.
- Spider240second and new leopard160secondLOD2 terrain sessions passed, normal exits, actual evaluated-contact measurements. Cross-family passed20complete round trips/40committed transitions and7negative cases (unknown/missing/wrong rig/blocked spawn/cancellation/latest request/late completion), with0failed transitions and rebuilt contacts. Dedicated spider/leopard fresh-process profiles and three keyboard/profile processes passed; exact bindings remain in `package-02/` reports. Physical controller/touch remains untested.
- Two separate90second ordinary-controls captures each contain180owned-game-window frames, orderly exits, no material fallback: `ordinary-play-02/` and `interaction-controls-02/`. Encoded silent720p review videos retain capture timestamps/provenance. Synthetic keyboard/mouse only; the ordinary lab recording is largely rear-facing, so front-hand contact is evidenced by the separate packaged portrait, not that video. No full novice mission playthrough or finished cinematic/audio acceptance.

## Contact measurements and scope

Limits remain per-leg p95stance drift≤2cm and maximum penetration≤0.5cm. No averaging across legs or tolerance change. Full counts, fixture coverage, exclusions, reach/support-loss/transitions and timing are in local `complete-contact-metrics.json` and original reports.

| Family/leg | Stance samples | Excluded swing/airborne/invalid | p95 drift cm — full numeric value (decimal) | Max penetration cm — full numeric value (decimal) |
|---|---:|---:|---|---|
|spider/front_l|87594|42223|3.482359716144856e-06 (0.00000348235971614486)|3.791066319536185e-06 (0.00000379106631953618)|
|spider/front_r|85008|44809|3.511480144879897e-06 (0.00000351148014487990)|3.5264602047391236e-06 (0.00000352646020473912)|
|spider/rear_l|80844|48973|3.46209344570525e-06 (0.00000346209344570525)|3.691417077789083e-06 (0.00000369141707778908)|
|spider/rear_r|73716|56101|3.4414865694998298e-06 (0.00000344148656949983)|3.535454197844956e-06 (0.00000353545419784496)|
|leopard LOD2/L|65476|21919|4.10645516240038e-05 (0.00004106455162400380)|2.9577066015917808e-05 (0.00002957706601591781)|
|leopard LOD2/R|65693|21702|0.7175579071044922 (0.71755790710449218750)|2.9577066015917808e-05 (0.00002957706601591781)|

Spider samples are finalized tarsus transforms plus imported tip offsets. Penetration independently queries actual collision, including swing/airborne. One former interior-probe sample was rejected; all legs cover flat/ramp/steps/uneven/moving/disappearing; disclose any low auxiliary access-ramp coverage from the full report. Leopard uses finalized feet and authored sole-plane offsets, not full-mesh collision acceptance: controlled45cm/s,15degree ramp,10cm steps,5/10/15cm uneven, moving/disappearing support and explicit fixture relocation with resets/jump/WebStep. Zero invalid transforms/segment-length error in both. Native query/solve/frame timing and frame traces are retained; no detailed CPU/GPU/mobile inference.

| Family/leg | Flat | Ramp | Steps | Uneven | Moving | Disappearing | Reach failures | Support loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|spider/front_l|48355|5659|8025|4342|4080|1059|34|14513|
|spider/front_r|47952|5654|7777|7030|2210|1099|34|17676|
|spider/rear_l|49383|5973|4438|4939|3826|475|96|24006|
|spider/rear_r|48300|5861|1822|6818|1684|399|77|30057|
|leopard LOD2/L|38740|5802|3845|4940|10699|1450|not separately recorded|42|
|leopard LOD2/R|39160|5571|3842|4971|10699|1450|not separately recorded|26|

Auxiliary spider access-ramp samples: front_l=8207, front_r=4189, rear_l=3907, rear_r=0. Zero/low auxiliary coverage is not a pass for that support.

| Family | p95 frame interval ms | p95 query µs | p95 solve µs |
|---|---:|---:|---:|
|spider|2.5448482036590576|10.616146087646484|28.009992599487305|
|leopard LOD2|2.5623700618743896|7.913913726806641|13.37099838256836|

## Publication, identity and preserved failures

Technical prototype publication `ae9920682a7442f4850ca8fe8f2b127f`; SHA256 `edd86d324f4db0e0980ab55d248c8e6dd97df69277a1051a4670aa13faa82bab`. Real browser skin/morph pixels/motion and dependency export passed through the existing studio API. Prior publications, canonical IDs and Kwaku revision2 remain unchanged. Creativefalse/rightsUNVERIFIED/mobilefalse; no new restore-through-publication cook cycle is claimed.

Source/native/config/model hashes and toolchain: `inputs-02.json`, `candidate-02.json`, `package-manifest-02.json`, `identity-audit-02.json`. Installed Unreal5.8.3 CL58210709, Blender4.5.14, project-qualified export conversion retained. Frozen audit covers59runtime/config,610native-content,117authoring,650model files;945protected original entries unchanged. GitHEAD alone does not identify this uncommitted build.

Candidate010532passed routes/restarts/spider but its new leopard fixture exited2: native verification still required the old map. Failure preserved; no override. Build16requires exact flag-selected mapANDmesh and reports that binding; the Python regression rejects missing/wrong binding and nonzero exit. Corrected candidate reran the full sequence. Earlier crumpled-arm/lid/action-retention/source/import/map-creation failures remain in fresh revision/evidence directories. Keep `-ansimalloc` and the unresolved detailed-CPU-trace shutdown defect visible. No diagnostic crash was suppressed.

## Package, captures and launch

Selected package: `/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261016T013344.354217Z`. ELF SHA256 `2c8b4dabf86a742499163add2b94d3e233680bda90cac5fb521c596901df46e9`. Evidence root: `.local/verification/character-interactions-20261016/`; packaged ledger image: `package-02/cast-1/kwaku-ledger.png`. Separate source/native and clean package archives are recorded in `source-archive.json` and `package-archive-02.json` after hash verification. They are local additive backups, not a new starter, final-art kit or clean-checkout hydration solution.

```bash
cd /home/favl/Downloads/ANANSE_Production_Starter
env -u PYTHONPATH -u LD_LIBRARY_PATH ./Builds/Linux/20261016T013344.354217Z/Ananse.sh /Game/Ananse/Maps/Interactions_v003/L_Market_InteractionsLab -ansimalloc -windowed -ResX=1280 -ResY=720 -AnanseArtRefinement -AnanseInteractionRefinement
```

Home/End select spider/leopard;PageDown cycles others;1–9clips,0automatic,mouseto orbit,WASDmove,Ppause,F6/F8dedicated lab save/restore. Kwaku9shows ledger. Episode: substitute `L_Market_EpisodeInteractions`, add `-AnanseEpisode -AnanseCheckpointSlot=AnanseInteractionsManual20261016`. Use a dedicated slot.

## Changed scope and next decision

Runtime changes are in `Unreal/Source/Ananse/`: authored animation/import helpers, cast/player/animation/selection, catalogue/mission/world cosmetic hooks, story-cast/terrain verification and refinement tests; `Ananse.Build.cs`/`Unreal/Config/DefaultGame.ini` add explicit editor mesh APIs/cook paths. Authoring/import/validation helpers are `scripts/refine_character_interactions.py`, `author_ledger_interaction.py`, `refine_leopard_surfaces.py`, `verify_interaction_sources.py`, `import_character_interactions.py`, `build_interaction_maps.py`, `check_refined_kwaku.py`; existing cast/contact/cross/runtime/publish helpers, studio allowlists and tests were extended. Exact additive file paths/hashes are in the source archive manifest; pre-existing dirty work remains protected.

Next decision is visual review of faces/hands/sleeve and prop deformation against original references, followed by further art work. A finished uninterrupted mission interaction sequence remains open, alongside remaining cast/environment detail, approved voice/music, creative/cultural/rights approval, broader terrain/navigation, long-session memory, publication rollback cycle, campaign mapping and Android/iPhone/device qualification. Nothing is deployed. Accepted230344rollback and earlier archives/saves/profiles/publications/rejected evidence remain preserved. Narrow tracked working/index token-assignment scan found no matches; it is not a historical/generated-artifact secrets audit. Index remains empty.

Enterprise-execution/task-observer informed evidence separation and preserved-failure checks; skill-retrieval was unavailable, so project contracts/installed APIs supplied implementation evidence. No external reference upload or tool acquisition.

## Final safety and review artifacts

Final frozen-input/protected-original audit passed; all39immutable package payload files match, with32additional runtime Saved files excluded from delivery. The rollback ELF hash is unchanged. Narrow tracked working/index scan:69paths each,0nonempty token assignments,0staged paths.

- `.local/verification/character-interactions-20261016/ordinary-play-02/actual_gameplay_review.mp4`: decoded1280×720,720frames; SHA256 `aae15938a613f94a3dedbd1f6f0595d1c2d0f9e17203dcd80868c54750712cce`. Silent, timestamped owned-game-window captures.
- `.local/verification/character-interactions-20261016/interaction-controls-02/actual_gameplay_review.mp4`: decoded1280×720,720frames; SHA256 `a373946892a5e719627b318181ae224d007677bd1564091f6adede2f96173d1b`. Silent, timestamped owned-game-window captures.

Clean Linux backup: `/home/favl/Downloads/ANANSE_Production_Starter/.local/deliveries/20261016-character-interactions/ANANSE_Linux_20261016T013344.354217Z.tar.gz`; 39verified payload entries, SHA256 `ee8acc30439af30f094fedf2382b0fe7e1eb71f7d28e097c095ffa2cf4d07121`. Runtime profiles/logs/private studio state excluded.
