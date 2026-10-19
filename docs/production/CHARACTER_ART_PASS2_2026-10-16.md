# Character Art Acceptance Pass 2 — 16 October 2026

**Bounded art corrections and technical review delivered. Kwaku and OseboLeopard remain NOT ACCEPTED for final character art.** Reference likeness requires Frank's review; visible face, grip, clothing and cinematic defects remain FAIL. No third skeletal family started.

Branch `feature/local-milestone-verification`, HEAD `ec7bf0bcf16634a13c12e92433e9731064890e80`; all newer work remains uncommitted. This commit alone does not identify the build. No commit, stage, push, publication, deployment, purchase, installation or unrelated system change.

## Exact candidate and preservation

Fresh package: `/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261016T171420.467448Z`. Executable `/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261016T171420.467448Z/Ananse/Binaries/Linux/Ananse`.

ELF SHA-256 `3352af6b4bcb698a8f5e47891c75ec7f7cac844bcfbbb184f055f6437e2a10d3`. Prelaunch payload manifest SHA-256 `4d16764f28072caafe79f9d8b87a42a934ac75d503169a9d7629547b615dee45` (39 files; runtime logs excluded).

Frozen source/config `2a251b29a57612adbfd053bd15ddd8fb85c384d63bb2b397535cd1c970bb2fa8`; native content `ef01265f93f23129fc293daf251fa212306f7d0dd51f756a670dbc6a16973c03`; authoring scripts/studio `f87caa6164ac502680fb6cece78bf375f57cbd421f8d90f8d22636423f97a6d3`; authored models `6e60ed7639a0018187225881f43eb7503156365009062b5f97aae102d07db888`. Exact per-file maps: [inputs-02.json](../../.local/verification/art-pass2-20261016/inputs-02.json), [changed paths/hashes](../../.local/verification/art-pass2-20261016/changed-paths-final.json), [delivery evidence](../../.local/verification/art-pass2-20261016/delivery.json). These paths are project-local evidence, not proposed creation targets.

Protected145831rollback,745 pre-existing native asset files,788 pre-existing model files, original references and immutable publication are unchanged. [Preservation assertions](../../.local/verification/art-pass2-20261016/preservation-final-02.json). Publication `ae9920682a7442f4850ca8fe8f2b127f`, semantic hash `edd86d324f4db0e0980ab55d248c8e6dd97df69277a1051a4670aa13faa82bab`, remains unchanged. New design definitions are **unpublished local review revisions**, not reviewed studio publications. Kwaku campaign default and human Osebo identity remain unchanged.

Toolchain: UE5.8.3 changelist58210709 at `/home/favl/Unreal/UE_5.8.3-58210709`; Blender4.5.14 build62c1db4208e8 at `/home/favl/.local/opt/blender-4.5.14-linux-x64/blender`. Units: saved scenes metres; imported/runtime centimetres; original rest transforms retained and source/native posed probes checked. Original skeleton/controller/contact/physics/animation architecture retained. Gameplay owns root/collision; the existing game-thread contact snapshot and one animation deformation path remain authoritative. No second solver, root offset workaround or new gameplay architecture.

## Actual editable art corrections

Kwaku source `SourceArt/Characters/Kwaku/Authored_v035/Kwaku.blend`, SHA `1d7608b08e1a2246c6277b8d857f5fda204da850be5bd386cd3760c32a2a4401`; GLB `ae3abb4ddffe46ed492d21513df7b43775107f363549d6f0bc27100e6a81741d`.46 unchanged rest bones,11 original actions,12 nonzero facial targets; source154330vertices/max4 influences. Reshaped skull/cheeks/nose/philtrum/lips/ears; denser irregular coiled hair; actual connected orbital annulus; eye surface inset5.2mm. Arm/palm/digits now share an actual surface, with barycentric original weight transfer and bounded reduction (12648/12647 arm vertices, max1.486mm source-surface deviation). Wrist/sleeve weights and sash/cloth response revised. Natural thumb/grip, shoulder/sleeve construction and expression remain unfinished.

Osebo source `SourceArt/Characters/OseboLeopard/Authored_v021/OseboLeopard.blend`, SHA `ba5397109577eb786990c7d94c717365704904c3f1db73de15ae7e2fda4a557d`; GLB `a0aa72213b5e65c616ace6680cefa272874ff78b896e4a02920adebf864ae36f`.64 unchanged rest bones,9 original actions,12 nonzero facial targets; source61374vertices/max3 influences. True external orbital boundary loops61L/59R replace crossed loop ordering; secondary internal loops closed and winding repaired. Muzzle/cheek/skull/ear contours, tail-root flare, chest-pinned cape root and UVs revised. Seven armour parts thickened/bevelled. Ten ventral pad proposals attach to **four existing digit chains per paw**; the earlier five-digit description was incorrect. No new digit chain, weapon, species mapping or combat logic. Feline anatomy/neck/mouth/paw/costume quality remains unfinished.

New meshes/definitions/pawns: `/Game/Ananse/Characters/Kwaku/ArtPass2_v003/Kwaku.Kwaku`, `BP_Kwaku.BP_Kwaku_C`, `DA_Kwaku.DA_Kwaku` (revision11); analogous OseboLeopard paths (revision7). Actual generated class, skeleton, old physics and retained clip paths are in [native asset map](../../.local/verification/art-pass2-20261016/native-04/native.json), with [saved/reopened source/native skin probes](../../.local/verification/art-pass2-20261016/native-reopened-final.json). Kwaku still uses original Story_v001 skeleton/ABP and Visual_v003 physics; leopard uses original Authored_v001 skeleton, Animations ABP and Visual_v003 physics. LOD0/1/2 vertex counts: Kwaku163333/84963/45284, triangles306570/153076/76433; leopard68965/37099/20976, triangles121850/60396/29934. GLB material slots: Kwaku10, leopard11; actual material/action names are recorded in `materials-actions-final.json`. These counts do not establish mobile readiness.

Changed native source is limited to opt-in art bindings, fixture allowlists, inspection cameras/metadata and one per-design revision lookup fix exposed by the actual package test. No mission/route/terrain thresholds changed. Exact changed/additional paths and hashes are in the manifest above; trial revisions remain preserved separately.

## Visual/deformation review

[Kwaku twelve gates and region grid](art-pass2-20261016/Kwaku.md) · [Osebo twelve gates and region grid](art-pass2-20261016/OseboLeopard.md). Both keep likeness REVIEW_REQUIRED; faces/hands/clothing/material/cinematic quality FAIL. Leopard capture-target contact remains BLOCKED pending an actual approved binding/contact test.

[Review deliverables](../../.local/verification/art-pass2-20261016/review-deliverables/manifest.json): front/side/three-quarter comparisons and requested face, hand/paw, prop, clothing, gameplay-distance/cinematic source renders. Original references are unmodified; their illustration cameras are unmeasured. Before/after source cameras, lens, exposure and lights match exactly, asserted in [comparison provenance](../../.local/verification/art-pass2-20261016/comparison-provenance.json).

Actual source pose grids contain solid/wireframe,14 diagnostic poses per character plus expressions, hand/paw curls and interaction views (50Kwaku/53leopard images); fixed sets add20images/character including true skeleton overlays. [Kwaku pose sheet](../../.local/verification/art-pass2-20261016/Kwaku-poses-sheet.png) · [leopard pose sheet](../../.local/verification/art-pass2-20261016/OseboLeopard-poses-sheet.png) · [actual weight views](../../.local/verification/art-pass2-20261016/arm-weight-views-final/provenance.json). Source render matrices/lenses/light powers/pose angles are recorded.2.25rad elbow/1.13rad wrist/.85rad ankle are declared diagnostic samples, not approved full joint limits; no gameplay range was reduced to hide defects.

Blink paired-ray checks: Kwaku90/90 open-visible samples covered;144/234 rays excluded because open eye was not hit. Leopard86/86 covered;148/234 excluded for the same reason. This sparse coverage is not natural-blink/eye-motion approval. [Exact geometry check](../../.local/verification/art-pass2-20261016/blink-coverage-final.json).

Ledger: actual separate runtime component `LedgerPresentation`, attached to bone `hand_R`, NoCollision. `socket_ledger` is an authoring socket and is **not** the actual attachment used. Conservative page-core checks sample1728 hand vertices at58 visible frames23..80, zero core penetrations. Covers/clasp/2mm edges and invisible pickup/stow excluded. Natural thumb/palm contact and blending are still FAIL. [Actual geometry evidence](../../.local/verification/art-pass2-20261016/ledger-volume-final.json).

## Lighting/camera and preserved failures

Three opt-in maps under `/Game/Ananse/Maps/ArtPass2_v003/`: `L_CharacterArtReview`, `L_LeopardArtContact`, `L_LeopardCinematicReview`. Original campaign/fixture maps unchanged. Manual exposure compensation-2stops, physical camera exposure false, bloom/motion blur0, no defocus. This is not EV100=5; inactive min/max values do not define manual exposure. Point key/fill/rim1800/900/1500lumens with80/100/70cm sources plus distance-stable soft directional key30lux/fill12lux cover movement. Native cameras record actual world position/head distance/FOV; close portrait40deg (~49.45mm equivalent36mm), ledger55deg (~34.58mm), full body60deg. [Light correction and preserved map bytes](../../.local/verification/art-pass2-20261016/lighting-correction-03/maps.json).

Candidate01 `Builds/Linux/20261016T170302.395377Z/` is preserved **FAILED for presentation/integration**. Its ELF SHA-256 is `e2782ff2c487e7fa88a9a949836357925e1ad3f23eb5201de76b5dc777ec383b`; its inputs-01 source/content bytes differ from final inputs-02 and are not described as identical. Its Kwaku ledger shot moved~583cm beyond the light cluster and became silhouetted. Native assertions had passed, demonstrating why image inspection matters. Its cross-family checker correctly rejected40 old-mesh commits: the request passed Kwaku revision11 into leopard lookup, falling back to Visual_v003. Corrected one lookup to per-design revision; exact-new-mesh assertions and thresholds were retained. Earlier topology/blink/import/compile failures remain in the evidence directory. Do not count these as accepted runs.

Final package lighting improves travel visibility but Kwaku skin/ledger remain too dark/glossy for final cinematic use. Leopard HUD overlaps the head/ears in some native inspection shots. Lighting does not cure the anatomy/material defects; both cinematic gates remain FAIL.

## Executed verification

294Python tests passed;28native automation tests passed (2without warnings/26with known `LogInit: Querying IsUsingWayland before SDL is initialized` warning). Native report is fresh, complete, nonzero; no tests removed or thresholds weakened. `node --check studio/static/app.js` passed. These supersede only the relevant historical291/27counts, not a fabricated combined total. [Python result](../../.local/verification/art-pass2-20261016/python-final-02.log), [native report](../../.local/verification/art-pass2-20261016/native-tests-02/unreal-automation/index.json), [native command/exit](../../.local/verification/art-pass2-20261016/native-tests-02-supervisor.log), [cook command/exit](../../.local/verification/art-pass2-20261016/cook-02-supervisor.log). Python command: `env -u PYTHONPATH -u LD_LIBRARY_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q`; native command: `.venv/bin/python scripts/unreal.py test --allocator ansi --evidence-dir .local/verification/art-pass2-20261016/native-tests-02` with the pinned UE_ROOT.

Full applicable suites ran after final source correction and before cook02. Source/rest hierarchy/weights/action samples, nonzero morphs and saved/reopened skin probes passed. Final package stages: Kwaku full clip/ledger/selection regression; leopard9-motion/morph/movement;20Ananse→leopard→Ananse round trips/40commits with7negative cases; leopard terrainLOD2; four owned-window keyboard save/restore processes; existing human-campaign negotiation pursuit/capture/retry/episode smoke. All game processes exited normally. Existing all-cast helper exercised unchanged cast as regression only; no other family authored.

The exact new leopard mesh/class is required at every cross-family commit; stale/missing/incompatible/blocked/cancelled requests retain/recover the prior pawn. Spider contacts rebuild after return. Keyboard is synthetic X11 input, distinct from physical controller/touch. Two separate fresh processes restore Kwaku and leopard from dedicated `AnanseLabSelection_ArtPass2_v3` test profile. Campaign saves untouched.

Pursuit smoke uses the existing human campaign binding, not the leopard as canonical AI. It does not approve leopard capture-target contact/species mapping. Six route/outcome cases and older campaign restart results remain historical; they were not redundantly rerun in this bounded art pass. Long-session memory, broader navigation/terrain, final audio/rights, Android/iOS physical devices and service gates remain open.

LOD2 terrain fixture `/Game/Ananse/Maps/ArtPass2_v003/L_LeopardArtContact`; actual finalized foot/contact marker, not requested target alone. Thresholds per footp95drift≤2cm/maxpenetration≤.5cm. No averaging away failures:

| Leg | stance samples | p95 drift cm (decimal) | max penetration cm (decimal) | excluded swing/airborne/invalid |
|---|---:|---|---|---:|
| L | 75291 | 4.1042680095415562e-05 (0.000041042680) | 2.9576996894320473e-05 (0.000029576997) | 24902 |
| R | 75494 | 0.6624036431312561 (0.662403643131) | 2.9576996894320473e-05 (0.000029576997) | 24699 |

All six support roles flat/ramp/steps/uneven/moving/disappearing have declared coverage; jump/Web transition/reset exercised. Invalid transforms `0`; source/native post-solve segment checks retained. [Full metrics/coverage/exclusions](../../.local/verification/art-pass2-20261016/package-02/leopard-terrain/result.json). Native terrain p95 counters: query7.474329microseconds, solve13.690907microseconds, frame interval2.278498milliseconds. Frame traces/native query/solve timing support only their own counters; no complete CPU/function/thread/GPU trace or mobile performance claim. `-ansimalloc` workaround and detailed-CPU-tracing shutdown defect remain unresolved.

## Genuine native captures/video

[Kwaku packaged ledger](../../.local/verification/art-pass2-20261016/package-02/kwaku-clips/kwaku-ledger.png) · [leopard capture gesture](../../.local/verification/art-pass2-20261016/package-02/leopard-motion/leopard-stage-5.png) · [cross-family](../../.local/verification/art-pass2-20261016/package-02/cross-family/result.png).

[Kwaku actual package video](../../.local/verification/art-pass2-20261016/package-02/Kwaku-video/actual_gameplay_review.mp4), 32.25seconds/98actual captured frames, SHA `fc5b326e7d3143622b6c1a3295e3aac88062b36547573cfc562713292bd6a25f`.

[Osebo actual package video](../../.local/verification/art-pass2-20261016/package-02/OseboLeopard-video/actual_gameplay_review.mp4), 55.375seconds/171actual captured frames, SHA `86a7971a4ffa4995f9462e271824a3821b4db58e9c17e5d10157f9c93688e758`.

Both decode1280×720; frame timestamps/hashes and exact executable identity recorded. Only the owned game window was captured. Frames held to recorded timestamps at8fps; no synthesized/interpolated poses, no audio recording, no physical-input or capture-overhead performance qualification. Kwaku recording stops before the reused harness switches to other characters.

## Verified launch

```bash
"/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261016T171420.467448Z/Ananse/Binaries/Linux/Ananse" /Game/Ananse/Maps/ArtPass2_v003/L_CharacterArtReview -AnanseArtPass2 -AnanseVisualReview -AnanseArtRefinement -AnanseInteractionRefinement -ansimalloc -windowed -ResX=1280 -ResY=720 -UserDir="/home/favl/Downloads/ANANSE_Production_Starter/.local/art-pass2-manual-profile"
```

Home selects Ananse, End leopard; from spider PageDown selects Kwaku.1–9clips/0automatic,WASDmove,Ppause,F6/F8dedicated profile. For leopard inspection launch the same executable/flags with `/Game/Ananse/Maps/ArtPass2_v003/L_LeopardCinematicReview`. Exact scenario commands and exit statuses are preserved in each package stage; manual-profile destination is intentionally separate.

Next decision: review the two character matrices and visible defects. **Neither character is approved; no character three begins.** The next correction remains facial/hand/paw/clothing anatomy and skin/material/cinematic readability, followed by relevant regression. Retrieved skill-retrieval tools were unavailable; existing project contracts and local enterprise-execution/task-observer guidance informed bounded preservation and evidence handling.
