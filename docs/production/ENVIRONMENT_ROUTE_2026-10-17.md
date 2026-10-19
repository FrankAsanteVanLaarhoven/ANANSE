# River Market and Story Forest environment pass — 17 October2026

Engineering review candidate; **environment creative acceptance remains REVIEW_REQUIRED**. Aso Yaa remains pending. No other character family, publication, commit, push, deployment, installation or system tooling change.

Branch `feature/local-milestone-verification`, HEAD `ec7bf0bcf16634a13c12e92433e9731064890e80`. Existing uncommitted work preserved.

## Actual source and native assets

- Editable `SourceArt/Environments/MarketSanctuary/Route_v001/RouteEnvironment.blend` and eight GLBs: detailed facade, sagged stall/counter, three hollow pots, plank/rope dock, opaque river, rooted tree, boulder, fern. UVs and three conventional native LODs. Native prefix `/Game/Ananse/Environments/Route_v001/`.
- Editable `SourceArt/Environments/MarketSanctuary/Crossing_v001/SanctuaryCrossing.blend`, GoldenWebCrossing.glb and SanctuaryStream.glb. Native `/Game/Ananse/Environments/Crossing_v001/`. Static crossing always visible/collidable together, deck16cm; actual downward ray and42x88cm capsule sweep passed. Shallow stream lies above retained ground, not playable water or a new mission power.
- Original512px indigo weave `SourceArt/Environments/MarketSanctuary/Surface_v003/IndigoWeave.png`. Native `/Game/Ananse/Environments/RouteSurface_v001/M_Indigo`, `M_Leaf`; cloned legacy wood/plaster under `RouteSurface_v002`; coherent plaster/texture under `RouteSurface_v003/M_OchrePlaster`. All relevant materials explicitly qualify instance usage. Original shared materials unchanged.
- Maps `/Game/Ananse/Maps/EnvironmentRoute_v002/L_RiverMarket_Route` and `L_StoryForest_Route`, cloned from frozen Aso Market and accepted Sanctuary. Original templates untouched.30Market and70Forest instances;21Market and41Forest simple boxes. Hidden draft colliders replaced by explicit scenery boxes; unchanged original interaction/floor/roof/checkpoint roots. Debug interaction cubes/labels hidden; collision/actions, authored character components and HUD prompts retained.
- `AnanseEnvironmentCluster.h/.cpp`: tick-free scenery-only HISM container. `AnanseMission.cpp`: opt-in map routing only. `AnanseRuntimeVerification.cpp`: isolated environment save slot and read-only observations/static-crossing check. `AnanseEnvironmentTests.cpp`: two automation identities including actual saved-instance orientation validation. No rig/contact/selection/pursuit logic changed.
- Authoring/import/lighting/qualification scripts are listed with exact bytes in `.local/verification/environment-production-20261017/changed-paths.json`. Detailed native mesh/material/LOD paths in `reopen-final/reopen.json` and `material-qualification-01/materials.json`. New-module LOD0 instance totals: Market142460triangles; Forest33110triangles. These exclude retained geometry/characters.

Blender4.5.14; Unreal5.8.3 CL58210709, exact existing toolchain lock. Source metres to native centimetres; nominal6m facade has306cm half-extent including coping. A named90-degree yaw transforms `(100,0,0)` to approximately `(0,100,0)`cm;100saved instance rotations verified without pitch/roll. No guessed second scale transform.

## Actual tests and measurements

- Python **328 passed**, final `python-final-04.log`; JavaScript syntax checks passed. Five new guard tests enforce route-specific promise footage, six environment-report rejection/validation tests. Input-pack20tests were not rerun or added to this total.
- Native **34 discovered/executed/passed**, serial `native-tests-final-02/unreal-automation/index.json`; compiler build06 exit0. Includes saved maps/three LODs/100upright instances; prior test identities retained.
- Final cook03 exit0; **all 9packaged stages exited0** with fresh assertions, normal process exits, valid materials, actual accepted Kwaku mesh and common ELF: three routes × protect/expose, cinematic finish/skip/pause/cancel/retry recovery, two independent checkpoint restores. Each six-route run includes ten capture/retry cycles and actual Forest completion.
- Guard-only Python correction after cook03: negotiation exposure still requires the actual broken-promise event+PNG; social/rooftop must have neither. Canonical game code unchanged. Updated checker SHA is recorded in later commands and preservation-final.json; do not misstate it as the earlier frozen authoring-script byte.
- Frame-only traces retained per stage. Detailed CPU-tracing shutdown limitation and `-ansimalloc` workaround remain. Keyboard/controller events are simulated, not physical-device evidence.

- rooftop-protect: 62 one-second samples; game-delta p95 8.111839ms; last-frame RHI draw-call p95 70; primitive p95 4002; texture peak 273094656bytes; process physical peak 1685581824bytes.
- rooftop-expose: 62 one-second samples; game-delta p95 2.774807ms; last-frame RHI draw-call p95 67; primitive p95 3962; texture peak 273094656bytes; process physical peak 1704611840bytes.

These are warm-cache Linux engineering observations with screenshot overhead: sampled simulation delta, previous-render-frame RHI counters and process-global texture counters. Recently rendered/visible flags are component observations, not exact GPU visibility. They do not establish complete GPU frame/lighting cost, mobile FPS, a device budget pass or long-session stability. Rooftop runs occurred after editor captures exited. Complete per-map component/material/instance ranges are in profiling.json. No qualified per-device environment budget exists here; do not invent one.

## Bake failure and other preserved failures

CPU Lightmass crashed on its game-thread-tag assertion (Signal11); volumetric import expected64tasks and received0, with **zero lightmap textures**. `finish-01/finish.json` retains the misleading API-return `baked:true`; it is **not acceptance**. `bake-failure.json` reconciles this explicitly. Final review uses one bounded shadowed directional light, a fixed existing engine daylight cubemap without realtime recapture, and retained local Aso lights. Rect fills hidden. Nanite/Lumen/virtual shadows are not baseline assumptions. Shipping baked/mobile lighting remains BLOCKED.

Other retained failures: unexposed Python component API and partial mapv1; relative capture path and missing camera API; near-black scene-capture diagnostics superseded by genuine main-viewport captures; package010431missing instance material usage/default shaders; candidate011036tilted instances from positional rotation arguments; parallel-editor registry-cache error causing a failed automation run, followed by clean serial success. Old candidates/reports remain; no tolerance was increased. All 9final stages use011408candidate only.

## Rendered review and remaining art

Fixed-camera main viewport before/after images under `viewport-qualified/`; improved interior Forest coverage under `forest-qualified/` with separate camera metadata. Model-derived solid/topology views under `source-views/`, scene hash recorded; native material overrides differ from source preview. Before/after cameras match within each comparison, while intentional environment lighting/exposure changes are recorded separately.

Packaged video `qualified-negotiation-protect/actual_environment_sequence_review.mp4`:1280×720, 61.4seconds, 212actual framebuffer images held to request timestamps at10fps. Silent, no interpolation; five environment requests were overwritten by concurrent cinematic screenshots and are disclosed in provenance. Actual negotiation samples fill that sequence. Not full-rate profiling footage or a novice uninterrupted playthrough. Decoded614strip frames successfully.

Remaining: review architecture/plaster/wood, sparse hero-tree/leaf forms, boundary/roof surfaces, dock/river edge and navigation readability; some watcher/character proxies remain frozen. River access still limited by retained boundary. Static bridge does not establish quest-state bridge logic. No finished environment ambience, voice or lip-sync. Broader terrain/navigation, long memory, cultural/rights review, complete lighting GPU cost and Android/iOS physical qualification remain open. Aso likeness and other creative gates remain unchanged.

## Safety and launch

All 1049 prior native assets and 977 prior model files unchanged; original Aso package39payload entries and reviewZIP unchanged. Dedicated `EnvironmentRouteFinal3_*` test slots; no publication/database edits or campaign mapping. No staged paths/commit. All active native/source/cook hashes, changed paths and payload manifest retained locally. This incremental source/native safety archive requires the existing project; it is not a standalone fresh-checkout hydration kit.

Package `Builds/Linux/20261017T011408.632684Z`; ELF SHA256 `44f99ea2c5f23fa6444e90887b9b5bdca82ccd0c8a11ccaf70f3e1c069607436`. Payload-file hashes in `payload-final.json`.

```bash
"/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261017T011408.632684Z/Ananse/Binaries/Linux/Ananse" /Game/Ananse/Maps/EnvironmentRoute_v002/L_RiverMarket_Route -AnanseEnvironmentRoute -AnanseAsoContact -AnanseAsoReview -AnanseAcceptedVisuals -AnanseStoryPresentation -AnanseArtRefinement -AnanseFormsScenery -AnanseInteractionRefinement -AnanseEpisode -ansimalloc -windowed -ResX=1280 -ResY=720 -UserDir="/home/favl/Downloads/ANANSE_Production_Starter/.local/environment-route-player-review-v001"
```

This exact executable/map/flag family was exercised by the packaged supervisor; the interactive command removes automation and uses its own review directory. No default campaign-map swap. Next decision: human environment review and a separately scoped Lightmass/mobile-lighting follow-up; keep Aso Yaa pending and do not start Esi.
