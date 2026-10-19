# Environment benchmark-cell revision — 17 October 2026

Branch `feature/local-milestone-verification`, base `ec7bf0bcf16634a13c12e92433e9731064890e80`. Uncommitted; no publication/deployment. The previous environment was rejected creatively. This revision does not reverse that decision: new creative acceptance remains REVIEW_REQUIRED.

## Bounded changes

Editable source: `SourceArt/Environments/MarketSanctuary/HeroCells_v001/HeroCells.blend` and `HeroDetails.blend`; sixteen original GLB modules, eleven shared 512×512 albedo textures and source manifests. Authoring: `scripts/author_hero_cells.py`, `author_hero_details.py`. Native construction: `scripts/build_hero_cells.py`, `build_hero_details.py`, `finish_hero_cells.py`.

Native family: `/Game/Ananse/Environments/HeroCells_v001/`. Modules: Frontage, ArchivePortal, MarketDressing, GroundTreatment, CanopySwag, Waterfront, Boat, RiverWater, HeroTree, Understory, SanctuaryMarker, WebLace, StreamBank, RockCluster, RoofGallery, WovenDeck. Runtime bridge mesh uses the versioned `GoldenWebCrossing/GoldenWebCrossing` binding, copied from the actual new WebLace mesh. All have three conventional LODs; Nanite disabled. Shared surface materials live in `Surface/M_*`. Added scenery does not own collision.

Only two previous native files intentionally changed: `/Game/Ananse/Maps/EnvironmentRoute_v002/L_RiverMarket_Route` and `L_StoryForest_Route`. Boundary-wall and roof-platform **visuals** were replaced; their physical blockers remain. All original actor transforms, interaction identities/actions and collision settings were compared before saving. Characters, mission logic, selection, saves, catalogue and publications were not edited.

The existing forest fixed-cubemap Skylight fallback intensity changed 1→3 for review readability. No added lights, real-time recapture, shipping lighting-strategy change or successful bake is claimed. Lightmass remains BLOCKED. Mobile, broader navigation and long-session memory remain unqualified; Aso Yaa creative approval remains pending.

## Evidence and retained failures

Evidence root `.local/verification/environment-hero-cells-20261017/`. Source geometry renders under `source-review/` use documented neutral softboxes; they are **source-model renders**, not runtime lighting. Native fixed-camera views and camera records are separate. Early captures are retained. Final review comparisons will identify their exact source captures and lighting differences.

First layout inspection used a relative project path and failed before map inspection; the absolute-path retry succeeded. Initial pytest invocation encountered an unrelated ROS auto-plugin import; isolated process-local `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` runs passed all 328 tests. JavaScript syntax and five new script syntax checks passed. The native automation report passed 34 tests.

First art candidate `Builds/Linux/20261017T025900.649760Z/` cooked successfully but failed the unchanged packaged bridge-visibility assertion: hiding the old crossing removed the established visual binding. The corrective action rebinds the new woven geometry through the established crossing cluster while retaining the tested 16 cm deck collision and capsule sweep. No assertion or threshold was changed. The failed package/report remain preserved.

## Visual limitations

This is a benchmark revision awaiting human review, not a production-art pass claim. Architecture remains repetitive; central ground/dressing is sparse; river edges and distant horizons are abrupt; water remains an opaque stylised surface without a qualified water simulation. Bark, stones and canopy retain visibly stylised forms. Forest lighting/composition and supporting-character presentation still need review. No voice, crowds, final audio, mobile or cinematic-quality approval is implied.

## Final package verification

Final candidate `Builds/Linux/20261017T030331.336716Z`: **all nine packaged stages passed**, including six routes/outcomes, cinematic lifecycle, before-choice restart and sanctuary restart. Each pursuit scenario retained ten capture/retry cycles. All reports use one frozen ELF `44f99ea2c5f23fa6444e90887b9b5bdca82ccd0c8a11ccaf70f3e1c069607436`. Cook and both orderly editor exits are recorded; no signing/deployment.

Canonical 39-file package-payload manifest SHA-256 `afcc164735fe98a25bc05f6471bd4fa55d54db5c90a9ec641e7778e213c846a0` (`payload-final.json`; Saved excluded). Native/content fingerprint `6bf365c910b75ac118feffb12bd238fa10386bc39e22994e8dafd021aa237f10`. Authored model fingerprint `a7dc43f9300edc2cce7dd795cdb7c2efc44dea7e9d4917420cd4504f95926fff`. Exact individual source-scene hashes and native paths are in the source manifests and `changed-paths.json`.

328 Python tests and 34 native tests passed; JavaScript and five authoring/build-script syntax checks passed. No overlapping suites were added to invent a total. The original 39-file rollback payload, 993 prior model files and all 1089 prior native files except the two intended environment maps are unchanged. No staged files. Previous failures and old review matrices remain intact.

The packaged review video decodes at1280×720,10fps, duration61.1seconds. It holds 202 actual source PNG requests to native timestamps; 11 requested screenshot files were missing/overwritten by competing capture requests and are explicitly listed in provenance. This is silent automated review evidence, not full-rate uninterrupted human play or performance video. Encoding used the installed Blender video sequencer; the initial attempt to invoke a standalone ffmpeg binary failed because that binary was absent. Nothing was installed.

`profiling.json` contains all native samples without exclusions. Interaction/readback spikes above100ms are retained. Encoding/decoding also ran during some package stages, so these are instrumented observations under a mixed workload, not isolated performance benchmarks. These one-second game-thread observations and previous-render-frame RHI counters do not qualify GPU timing, mobile or a shipping frame-time budget. `bound-final-camera/scene-budget.json` contains visible-flag mesh/instance/material/LOD counts. Geometry inventory includes 16 authored modules plus a native bridge alias, not17 distinct models.

Review ZIP: `/home/favl/Downloads/ANANSE_Hero_Cells_Visual_Review_20261017.zip`. Human creative approval is still required before expanding either cell. Baked lighting BLOCKED; mobile UNQUALIFIED; broad navigation/memory/audio open.

```bash
"/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261017T030331.336716Z/Ananse/Binaries/Linux/Ananse" /Game/Ananse/Maps/EnvironmentRoute_v002/L_RiverMarket_Route -AnanseEnvironmentRoute -AnanseAsoContact -AnanseAsoReview -AnanseAcceptedVisuals -AnanseStoryPresentation -AnanseArtRefinement -AnanseFormsScenery -AnanseInteractionRefinement -AnanseEpisode -ansimalloc -windowed -ResX=1280 -ResY=720 -UserDir="/home/favl/Downloads/ANANSE_Production_Starter/.local/hero-cells-player-review-v001"
```

The same executable/map/feature-flag family was exercised by the packaged supervisor. This interactive command removes automation and uses a separate review profile. Rollback remains the untouched011408package; map backups are in `maps-before/`. Do not reset Git.
