# Hero Cells Pass 4 — bounded art continuation

Branch `feature/local-milestone-verification`, base `ec7bf0bcf16634a13c12e92433e9731064890e80`. No commit, publication, deployment, new character or map expansion. Human Pass-3 review remains authoritative: Market DIRECTION_ACCEPTED / CREATIVE_NOT_ACCEPTED; Forest CREATIVE_NOT_ACCEPTED. This revision seeks review, not automatic acceptance or propagation.

## Actual assets and scope

Editable scene: `SourceArt/Environments/MarketSanctuary/HeroCells_v004/HeroCellsPass4.blend`. Eleven new modules: RiverReach, StreamPools, QuayApron, DockLife, VerandaCorner, LayeredGrove0/1/2, EcologyIsland, SanctuaryReliquary and SanctuaryGarden. Prior hero trees are retained without added detail. No optimisation was applied to preserved rejected source; new shore, stream and background layouts are separate authored forms. Source units metres; Unreal centimetres through the qualified Interchange path. Blender4.5.14 LTS / UE5.8.3 CL58210709. Conventional three-LOD static meshes, Nanite disabled, added scenery NoCollision.

Native family: `/Game/Ananse/Environments/HeroCells_v004/`, shared materials in `Surface/`. Only the two existing EnvironmentRoute_v002 maps are changed among prior native files. New visual marker and garden remain at the former marker location; Ananse, interaction roots, checkpoints, collision and the established web deck are unchanged. Market dock dressing and irregular frontage remain inside the hero cell. River visual bounds remain the former[-3600,9600]cmYextent: one continuous132m source sheet replaces overlapping sheets. No new playable support or route is created.

Water has an authored512px normal map, two opposing UV flows and angle-dependent colour in an opaque conventional material. No refraction, water simulation, physical depth, advanced reflections, Lumen or Nanite requirement is established. Shore/apron cross-sections bridge the visual land/dock edge. Stream banks use explicit curved profiles rather than dense surface subdivisions. Exported water normals are asserted upward independently for each surface; source-surface-audit.json records measured values and GLB hashes.

Distant groves use broader asymmetric crown/understory silhouettes. Foreground ecology is composed in edge islands. The new story stone, root garden, thread inlay and wider marker silhouette aim to improve sanctuary hierarchy; these are visual proposals, not new narrative mechanics. Market frontage has asymmetric veranda/pottery/textile clusters and mooring/barrel dressing. Perspective materials preserve existing building detail while cooling its palette; this is not atmospheric fog or a substitute for environment depth.

## Lighting and visual evidence

Market lighting/exposure unchanged. Forest final review retunes only the existing directional fallback from intensity3.0 to4.0 with linear colour[.82,.90,1]; no new light, exposure change or shipping lighting policy change. Baked lighting stays BLOCKED by the preserved Lightmass crash. Forest before/after images therefore compare the full art/presentation revision, not geometry under identical lighting. Six camera transforms/FOVs remain identical. Source neutral/beauty views use documented diagnostic softboxes and are separate from native/package lighting.

Native inspection also exposed a reversed inscription face at the interim34degree rotation. The final214degree visual binding corrects the imported front axis; the failed frame remains.

The first native view exposed a too-narrow marker presentation, an intrusive root framing and a distant-material override that suppressed facade detail. Earlier source and captures remain. Corrective work widened only the new marker35%, corrected its new visual instance to214degrees after native facing inspection and placed its new garden180degrees behind it; original actors were not moved. Perspective materials were rebuilt around the existing facade textures. An authored water normal replaced inadequate grain; no technical/creative gate was relaxed.

Source scripts: author_hero_cells_pass4.py, refine_hero_pass4_presentation.py, build_hero_cells_pass4.py, reimport_hero_pass4_presentation.py finish_hero_cells_pass4.py and orient_hero_pass4_marker.py. Source/native safety archive requires this existing project. Previous Pass-3 source, package052600 and review archive remain protected. Evidence root `.local/verification/hero-cells-pass4-20261018/`.

## Open gates

Creative acceptance REVIEW_REQUIRED. Baked lighting BLOCKED. Mobile, broader navigation and long-session memory UNQUALIFIED. Aso Yaa unchanged/pending. No character work or propagation. Full controlled profiling and physical Android30fps qualification have NOT been run or approved by this art iteration. Existing runtime regression samples are incidental diagnostics only, with no per-mesh GPU/CPU/residency attribution or controlled performance claim.

Remaining risks: stylised opaque water and simplified bank forms; reused hero-tree joins/bark; repeated broad background silhouettes and distant horizon; material wear/variation; sanctuary composition and supporting character readability; unreplaced technical interaction-prop visuals, including the pale cylinder in the sanctuary; no new crowds, voices or final audio. No final environment/art/mobile claim follows from automated tests.

## Inventory diagnostics

- L_RiverMarket_Route: resident visible-flag instances 87→95; LOD0 instance-triangle upper bound 568576→480008.
- L_StoryForest_Route: resident visible-flag instances 68→64; LOD0 instance-triangle upper bound 684060→424016.

These are inventory sums, not selected-LOD/GPU cost or a controlled performance improvement. The retained hero trees remain unaccepted; no density propagation is authorised.

## Executed checkpoint

Python328 passed; JavaScript and new-script syntax passed. Native34 passed. All9packaged stages passed in `Builds/Linux/20261018T015736.098029Z`: six route/outcome cases, cinematic lifecycle and two separate checkpoint restarts. Existing assertions unchanged. Final source/native fingerprints match cook inputs; package payload unchanged by runtime tests. No unrelated terrain/device pass is inferred.

Source scene SHA256 `ee402ab3f318624a40fd85d5c06efb8226e5414b0c4a85daaad4defc3f64f545`. Canonical package payload identity `a725d1aad61511c2981d95090ad98522800f53b7da014e8447e1160f71e48527` (39 files, sorted compact JSON relative-path→SHA256 map, Saved excluded). ELF SHA256 `44f99ea2c5f23fa6444e90887b9b5bdca82ccd0c8a11ccaf70f3e1c069607436`. Per-file source/native changes and hashes are in the review bundle and safety archive. 1092 prior model files unchanged; 1471 prior native files checked with only the two intended maps changed. Previous39-file052600rollback preserved. No staged files.

Supported frame-only traces and the existing allocator workaround were retained; detailed CPU-tracing shutdown failure remains open. Profiling reports retain all samples and show both improvements and regressions without treating them as controlled performance wins.

Review video:1280×720,10fps,61.2seconds;201actual PNG requests held to native timestamps;13missing/overwritten requests disclosed. Silent sampled automated package evidence, not full-rate performance or uninterrupted human gameplay. Encoding/decoding occurred after runtime stages. Before/after evidence uses six identical native cameras and unchanged exposure; disclosed Forest fallback directional change. Source beauty/neutral renders remain explicitly separate from runtime.

Launch:
```bash
"/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261018T015736.098029Z/Ananse/Binaries/Linux/Ananse" /Game/Ananse/Maps/EnvironmentRoute_v002/L_RiverMarket_Route -AnanseEnvironmentRoute -AnanseAsoContact -AnanseAsoReview -AnanseAcceptedVisuals -AnanseStoryPresentation -AnanseArtRefinement -AnanseFormsScenery -AnanseInteractionRefinement -AnanseEpisode -ansimalloc -windowed -ResX=1280 -ResY=720 -UserDir="/home/favl/Downloads/ANANSE_Production_Starter/.local/hero-cells-pass4-player-review"
```
Same executable/map/flag family exercised by the supervisor; interactive command removes automation and uses a separate review profile. Stop for human review of the new ZIP. Do not propagate or start another character.
