# Hero-cell art pass 2 — 17 October 2026

Branch `feature/local-milestone-verification`, HEAD `ec7bf0bcf16634a13c12e92433e9731064890e80`; uncommitted. Human review rejected the first cells for propagation. Market architecture and woven-web language are approved as a basis only. This revision remains REVIEW_REQUIRED, not artistically accepted.

## Scope and source

Toolchain: installed Blender4.5.14LTS and pinned Unreal5.8.3CL58210709. Source units are metres; native placement is centimetres through the existing qualified Interchange path. No tools were installed.

`SourceArt/Environments/MarketSanctuary/HeroCells_v002/HeroCellsPass2.blend`: editable collections for 18 original modules; three distinct hero-tree meshes, quay/river/cargo boat, far bank and settlement, vendor activity cluster, facade/threshold variation, distant forest, grove-floor patches, fallen wood, sanctuary framing, stream and silk hierarchy. Twenty shared512px textures include albedos, linear breakup/roughness data and subtle tangent-space normals. No downloaded/purchased art or external reference upload.

Native family `/Game/Ananse/Environments/HeroCells_v002/`, shared materials in `Surface/M_*`. Each static mesh has three conventional LODs and Nanite disabled. The maps remain `/Game/Ananse/Maps/EnvironmentRoute_v002/L_RiverMarket_Route` and `L_StoryForest_Route`; these are the only prior native files intentionally changed. New scenery is NoCollision. Prior collision, interaction/checkpoint roots, mission identities, characters, saves and publications are preserved. The existing woven crossing binding and its16cm deck collider remain; silk additions are visual only.

Authorship/source pipeline: `author_hero_cells_pass2.py` → `refine_hero_pass2_crowns.py` → `author_hero_pass2_backshore.py`. Native pipeline: `build_hero_cells_pass2.py`, `repair_hero_pass2_materials.py`, `reimport_hero_pass2_crowns.py`, `build_hero_pass2_backshore.py`, `finish_hero_cells_pass2.py`. These are creation/refinement scripts for this preserved local revision, not permission to overwrite older revisions. Source/native safety archive requires the existing project.

Market: stronger cargo-boat silhouettes, moorings/quay, continuous far-bank terrain and settlement layers, purposeful vendor/cart/basket/produce/cloth clusters, frontage-height offsets and archive flanking standards. Forest: independent leaning/forked/sentinel trees with upper crowns and buttress plates, ecological edge patches and an open approach, fallen wood, embracing root/thread frame around the existing stone/Ananse staging, layered trunks/canopy/distant ground and an irregular stream. Backdrops do not add playable support or routes.

Lighting and exposure are unchanged from the prior candidate. Atmospheric perspective uses geometry/palette, not a new fog/light system. Baked lighting remains BLOCKED by the prior Lightmass failure. No Lumen/Nanite shipping dependency, added lights, bloom concealment or alternative shipping strategy.

## Evidence and failures retained

Root `.local/verification/hero-cells-pass2-20261017/`. Six genuine before/after camera pairs: market arrival, archive, waterfront; forest bridge, sanctuary, stream/depth. Coordinates/FOV match, with the same exposure/fallback lighting. `before/` used binary backups; revised bytes were restored in a finally block, proved by `swap-audit.json`. Initial wrapper exited1 because it expected6PNGs but received7: an extra web-bridge request. The six required names/camera records and decoded pixels were validated individually; the extra is excluded. This is an evidence-count correction, not a runtime-test waiver.

Initial material imports saved but used fallback shaders: world-position output/mask-input names were wrong, then the texture importer auto-classified the breakup data as a normal map. Native API pin introspection and explicit linear/default compression/sampler bindings corrected both. Failed logs and grey fallback renders remain. The final fresh reopen has no fallback/compiler warnings. Upper trunks also had bare spikes in source review; genuine upper branches/crowns were added and the three actual meshes reimported. Earlier scenes/renders are preserved locally.

`source-review-qualified/` contains source-model beauty and neutral renders, with source-scene hashes and documented softbox cameras. They arrange source modules for inspection and are not runtime placement/lighting. `qualified-camera/` contains native editor views and actual scene/LOD budgets. Packaged frames/video remain separate. Do not treat source beauty lighting as shipping evidence.

## Open visual blockers

Water remains an opaque stylised surface with limited reflection/depth treatment; no water simulation or animated silk-flow effect was authored. Far settlement forms and repeated distant trunks remain visibly modular; horizon continuity still needs review. Hero roots/bark and vegetation are stylised and angular; sanctuary composition and clothing/character presentation are not newly accepted. Architecture/plaza/threshold material hierarchy still needs human judgement. No final recording, crowd system, mobile, broader navigation or long-session memory qualification is established.

## Verification, package, costs and launch

Python328/native34 passed; all9packaged stages passed in `Builds/Linux/20261017T043646.598325Z`: three routes×two outcomes, cinematic lifecycle, before-choice and after-outcome restarts. Each of the six route cases preserved ten capture/retry cycles. No tests/assertions/thresholds changed. JavaScript and eight new-script syntax checks passed.

ELF SHA-256 `44f99ea2c5f23fa6444e90887b9b5bdca82ccd0c8a11ccaf70f3e1c069607436`. Canonical39-file payload manifest identity `35e1e12f56401816fa5cb0a0df41d5833099c18c3fc4d051eaae38f98f1fe03f` (SHA256 of sorted compact JSON relative-path→file-hash map; Saved excluded). Source-scene SHA-256 `8087af316531f0d10ee830e468fd1d46a39bcf3c54de07c436fbcb0587a0c796`. Native/content fingerprint `d7503142cc09b57c0aa84e424db5cfa4ad339fc1b1e0bcee2b772eb5867f2155`. See `changed-paths.json` and the source manifest for exact individual asset paths/hashes.

1024 previous model files and all 1193 prior native files except the2intended maps are unchanged. Prior39-file030331rollback and source/maps/review evidence preserved. No staging/commit/publish/deploy. The allocator workaround and detailed-CPU-tracing shutdown limitation remain; this pass used supported frame-only evidence.

`profiling.json`, `profiling-deltas.json` and `scene-deltas.json` publish actual observations. Baseline had encoding overlap; this pass did not. Therefore deltas do not establish a controlled performance improvement. All samples/stalls are retained. Neither game-thread sample delta nor previous-frame RHI counters establish FPS, GPU performance or phone budgets.

Video:1280×720,10fps,61.2seconds, 202 actual PNG requests held to native timestamps; 13 missing/overwritten screenshot requests are disclosed. Silent automated review evidence, not full-rate performance or an uninterrupted human playthrough. Encoding/decoding ran only after all runtime stages finished.

Review ZIP `/home/favl/Downloads/ANANSE_Hero_Cells_Pass2_Visual_Review_20261017.zip`. Creative acceptance REVIEW_REQUIRED; baked lighting BLOCKED; mobile/broader navigation/long memory UNQUALIFIED. Do not propagate the cells or begin another family without human review.

```bash
"/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261017T043646.598325Z/Ananse/Binaries/Linux/Ananse" /Game/Ananse/Maps/EnvironmentRoute_v002/L_RiverMarket_Route -AnanseEnvironmentRoute -AnanseAsoContact -AnanseAsoReview -AnanseAcceptedVisuals -AnanseStoryPresentation -AnanseArtRefinement -AnanseFormsScenery -AnanseInteractionRefinement -AnanseEpisode -ansimalloc -windowed -ResX=1280 -ResY=720 -UserDir="/home/favl/Downloads/ANANSE_Production_Starter/.local/hero-cells-pass2-player-review"
```

The same executable/map/flag family was verified by the supervisor. This command removes automation and uses its own review profile. Launch030331for package rollback; binary map backups are in `maps-before/`. Do not reset Git.
