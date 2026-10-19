# Hero Cells Pass 3 — bounded visual revision

Branch `feature/local-milestone-verification`, base `ec7bf0bcf16634a13c12e92433e9731064890e80`. No commit, publication or deployment. Human Pass-2 decision: both cells REVISE. Market architecture and woven-web directions are approved as foundations only. This revision does not expand playable maps or approve creative quality.

## Actual changes

Editable source: `SourceArt/Environments/MarketSanctuary/HeroCells_v003/HeroCellsPass3.blend`. Fifteen new authored modules: CrownGuardian, RiverFig, TwinnedElder, three DepthGroves, RiverMargin, LivingStream, three SkylineQuarters, DyersCourt, ArchiveCrown, FernEcology and RootTheatre. Shared small textures and conventional LOD meshes; no purchased/downloaded assets, external reference upload or new character family.

Tree branches use sampled cubic curves with transported cross-sections, taper and basal fluting. Rounded roots replace wedge buttresses. Upper crowns were corrected after inspecting actual source renders; original revision renders/source remain. Stream and river bank cross-sections were rounded after source inspection exposed jagged edges. Three different settlement plans vary mass height, offset wings and hip/flat roof shapes. Dye-work clusters and archive canopy/insets add intentional activity and hierarchy. Fern rosettes, leaf litter, soft root framing and staggered depth groves preserve the existing sanctuary actors and approach.

Native family: `/Game/Ananse/Environments/HeroCells_v003/`. Only existing RiverMarket/StoryForest Route maps are edited; old art is hidden, not deleted. New scenery is NoCollision. Existing actor root transforms, collision settings and interaction identities are checked before save. No character, gameplay, publication, save, checkpoint or input code changes. Prior source and native revisions remain intact.

A native-camera review exposed an actual export defect: the river skin had downward normals (area-weighted source Z=-0.99995079), so Unreal culled it. Source faces were reversed and re-exported, yielding Z=+0.99995079; stream and bank orientation were checked independently. Failed captures and the earlier scene remain. `water-normal-fix.json` records all six source surfaces. Native reimport and reopened-camera evidence follow the correction. This was not hidden by enabling two-sided water.

Water uses an opaque, quiet macro-colour material in the established fallback. This is not simulation, physical depth, full reflection or a newly approved shipping shader. Source-model beauty renders use their documented diagnostic softboxes/materials, not runtime illumination. Native shared surfaces deliberately reuse the prior qualified texture inputs; new source-scene texture variations are not evidence of matching native shader appearance. The new native water graph is separately documented and inspected. Native comparisons retain identical fixed cameras, fallback lights and exposure. No Lightmass workaround, Nanite or Lumen shipping dependency.

## Review and unresolved gates

Creative acceptance REVIEW_REQUIRED. Baked lighting BLOCKED by the previously retained Lightmass crash. Mobile, broader navigation and long-session memory UNQUALIFIED. Aso Yaa unchanged/pending. No propagation to other cells and no new family.

Remaining visual risks: tubular/overlapping branch joins and stylised bark, sparse canopy at some angles, opaque water realism, distant building/grove repetition, sanctuary hierarchy, material wear, gameplay HUD and supporting-character presentation. No new crowd, voice, animated water/silk or atmospheric fog system. Art quality must be judged in actual images, separately from tests.

Pass-2 package `Builds/Linux/20261017T043646.598325Z/` and its review ZIP are preserved. Evidence root `.local/verification/hero-cells-pass3-20261017/`. Before images are copied unmodified from Pass-2 qualified camera evidence; provenance is explicit, no temporary map swaps. Six matching new images are native editor diagnostics; packaged screenshots/video are separately labelled. Profiling deltas are descriptive, not controlled performance, FPS, GPU timing, phone or memory-stability qualification.

Static visible-flag inventory: Market88→87instances and504544→568576LOD0instance triangles; Forest71→68instances and194184→684060LOD0instance triangles. These are upper bounds, not actual selected-LOD raster costs; the Forest increase requires particular device/performance scrutiny.

## Executed checkpoint

Python328 passed; JavaScript and new-script syntax passed. Native34 passed. All9packaged stages passed in `Builds/Linux/20261017T052600.027500Z`: six route/outcome cases, cinematic lifecycle and two separate checkpoint restarts. Existing assertions unchanged. Final source/native fingerprints match cook inputs; package payload unchanged by runtime tests. No unrelated terrain/device pass is inferred.

Source scene SHA256 `a525f950ef00b78b70f7ceb4d0333bf99505163114d843ad80a188028200ab6c`. Canonical package payload identity `cd2d715c3f69c97e62faf833b9b67d1f03a36e3573ea7ea24c16289bae71cdff` (39 files, sorted compact JSON relative-path→SHA256 map, Saved excluded). ELF SHA256 `44f99ea2c5f23fa6444e90887b9b5bdca82ccd0c8a11ccaf70f3e1c069607436`. Per-file source/native changes and hashes are in the review bundle and safety archive. 1064 prior model files unchanged; 1349 prior native files checked with only the two intended maps changed. Previous39-file043646rollback preserved. No staged files.

Supported frame-only traces and the existing allocator workaround were retained; detailed CPU-tracing shutdown failure remains open. Profiling reports retain all samples and show both improvements and regressions without treating them as controlled performance wins.

Review video:1280×720,10fps,60.9seconds;205actual PNG requests held to native timestamps;12missing/overwritten requests disclosed. Silent sampled automated package evidence, not full-rate performance or uninterrupted human gameplay. Encoding/decoding occurred after runtime stages. Before/after evidence uses six identical native cameras and unchanged fallback lights/exposure. Source beauty/neutral renders remain explicitly separate from runtime.

Launch:
```bash
"/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261017T052600.027500Z/Ananse/Binaries/Linux/Ananse" /Game/Ananse/Maps/EnvironmentRoute_v002/L_RiverMarket_Route -AnanseEnvironmentRoute -AnanseAsoContact -AnanseAsoReview -AnanseAcceptedVisuals -AnanseStoryPresentation -AnanseArtRefinement -AnanseFormsScenery -AnanseInteractionRefinement -AnanseEpisode -ansimalloc -windowed -ResX=1280 -ResY=720 -UserDir="/home/favl/Downloads/ANANSE_Production_Starter/.local/hero-cells-pass3-player-review"
```
Same executable/map/flag family exercised by the supervisor; interactive command removes automation and uses a separate review profile. Stop for human review of the new ZIP. Do not propagate or start another character.
