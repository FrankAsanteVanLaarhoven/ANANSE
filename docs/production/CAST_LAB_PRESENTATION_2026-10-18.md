# Cast lab neutral lighting — 18 October 2026

Branch: `feature/local-milestone-verification`. Base HEAD: `ec7bf0bcf16634a13c12e92433e9731064890e80`. No commit, publication or deployment.

## Bounded change

Refinement mode intentionally disabled the controller's two preview lights, while refined cast meshes used channel 0. In the older shared lab this left dark silhouettes and strong side illumination. An explicit `-AnanseNeutralLabLighting` option now reuses those two lights with white, 3,000-lumen, shadow-free fills. Their positions follow the camera yaw, 250 cm toward the viewer and 150 cm either side, at the existing 180 cm height above the pawn origin. Existing 1,200 cm attenuation bounds remain. Aso Yaa's two legacy character-specific preview fills are skipped in this explicit neutral mode so they do not stack with the controller lighting; other launches retain them. The controller updates their channels on possession; it creates no extra light per swap.

The player-review launcher enables this option only in `cast-lab`. Chapter 01 and launches without the flag retain their earlier behavior. This is diagnostic review lighting, not a replacement shipping lighting strategy or cinematic-art acceptance. No map, character geometry, material, rig, animation, publication or source scene was edited.

## Changed source

- `Unreal/Source/Ananse/AnanseLabSelection.h` and `.cpp`: shared preview-light configuration and camera-facing placement behind the explicit lab option.
- `Unreal/Source/Ananse/AnanseCastLab.cpp`: suppress the overlapping Aso-only legacy preview fills in neutral mode.
- `Unreal/Source/Ananse/AnanseSelectionTests.cpp`: native regression for legacy behavior, physical units and possession-channel policy.
- `Unreal/Source/Ananse/AnanseStoryCastVerification.cpp`: report actual preview-light count, component intensity/units and channels after swaps, plus per-character point-light component counts.
- `scripts/play_integrated_candidate.py`: enable neutral lighting in the opt-in cast lab.
- `scripts/run_story_cast_check.py`: neutral component-evidence checks and current Aso Yaa revision-5/16-clip/contact validation. Corrected Aso mode requires `--full-clips` before launch.
- `scripts/run_cross_family_check.py`: optional neutral-lighting launch flag.
- `scripts/run_aso_yaa_check.py`: focused neutral-mode validation using the same measured-light checks.
- `tests/test_story_visual_designs.py`: reject old Aso bindings, incomplete ledger phases, missing clips, missing/wrong/accumulated preview lights and shortened corrected-Aso runs.

## Trial evidence retained

Evidence root: `.local/verification/lab-presentation-20261018/`.

Initial neutral lighting retained the old opposite-side positions and gave uneven frontal illumination. The camera-facing 12,000-lumen trial illuminated the face but was too bright on pale cloth. Both trial runtime processes were deliberately stopped after inspection; their incomplete reports are not accepted qualification. Source snapshots and actual PNG captures remain.

The 3,000-lumen shortened preview produced useful diagnostic frames, but correctly failed runtime acceptance: the full corrected Aso ledger sequence was not observed (`aso_ledger_samples=0`, phase mask 0). No thresholds were changed. The CLI now rejects that shortened corrected-Aso configuration before starting the engine. Final qualification uses full clips.

## Acceptance boundary

Improved visibility exposes existing simplified faces, hand/cuff forms, shoulder/sleeve geometry and material response. It does not repair or approve them. Character art and environment review states remain unchanged. Pass-4 environment creative acceptance is REVIEW_REQUIRED; baked lighting remains BLOCKED by the retained Lightmass startup crash. Mobile, broader navigation and long-session memory remain unqualified. No physical-device profiling, broader map expansion, Forest propagation or new skeletal family was undertaken.

The first cooked candidate (`Builds/Linux/20261018T034805.176475Z/`) is preserved as superseded/unqualified: inspection exposed Aso-specific legacy fills stacking with the shared neutral pair. Its qualification process was stopped; its metrics are not final acceptance. The final source suppresses those extra components only in neutral mode and rejects their presence in runtime evidence.

The focused corrected-Aso editor run passed all 16 clips, full ledger phases and 20 round trips, reporting zero character fill components and two controller lights. Diagnostic output still exposes simplified facial/hand forms and extreme-pose robe penetration; these remain art defects, not lighting failures.

Final execution, package identity and preservation results follow.


## Final executed checkpoint

- **375 Python tests passed**, full suite; JavaScript syntax and changed Python compilation passed.
- **35 native automation tests passed**, including the new light-channel regression; final balanced native build succeeded.
- Focused corrected-Aso editor run passed 16 full clips, complete ledger contact, declared flat contacts and 20 round trips, with zero character-specific fill components.
- **Three fresh packaged stages passed** in the revised candidate: full seven-design cast playback (67 evaluated clips, 20 round trips per design), 20 complete Ananse/leopard round trips with negative selection cases, and the declared negotiation/protect Chapter 01 episode through Market and Forest with review lighting off.
- The packaged cast used the exact contact-lab map selected by the player-review launcher. All seven selected actors reported zero extra point-light components; the controller retained exactly two 3,000-lumen lights, physical lumen units, channel0 on/channel1 off. This is a bounded diagnostic-light check, not a long-session memory or whole-scene light-budget qualification.
- No new six-route/outcome, physical-controller, touch, Android or iOS qualification is inferred. Earlier broad gameplay results remain attached to their earlier artifacts. This candidate is a lab-review checkpoint, not a production/release acceptance.

Candidate: `Builds/Linux/20261018T035320.990906Z/`.

ELF SHA-256: `baf77f170ffafdd8597258c6e3134d5e84602ee79043f60d26bce9a23a87d089`.

Canonical 39-file payload SHA-256: `4ced779659b423299c37f711d9b1dd9ea043d303150cf7a6dba32ae265007723`.

Cook inputs and post-qualification source/content/toolchain fingerprints match. All **1,586 native assets and 1,123 authored model files** are unchanged. Five native source files changed intentionally; the other frozen runtime/configuration inputs are unchanged. All 39 payload files in the frozen Pass-4 package, the superseded trial and this final candidate retain their recorded hashes. Original source scenes, rollback packages, publications and failure evidence are preserved. No staged files, commits, engine patches or system changes.

Frame-only traces and `-ansimalloc` remain in use. The detailed CPU-tracing shutdown limitation remains open. Shipping baked lighting is still BLOCKED; the neutral lab option does not replace that dependency.

### Launch

From the project root:

```bash
python3 scripts/play_integrated_candidate.py --package Builds/Linux/20261018T035320.990906Z --scene cast-lab --profile lab-neutral-20261018
```

Use `--scene chapter --profile chapter-review-20261018` for the unchanged Chapter 01 lighting path. Omit `--profile` for a fresh isolated review session; reuse the name for review-save continuity. PageDown cycles the seven cast designs; Home selects Ananse; End selects the leopard. The launcher command was dry-run checked; packaged automation exercised the same lab world and binding modes. Human-operated controller/touch play is not claimed.

### Evidence

Final evidence root: `.local/verification/lab-presentation-20261018/final/`.

- `qualified-candidate.json`: package identity, executed stages, open gates and preservation results.
- `review-images.json`: seven genuine packaged capture paths, design IDs, source world and hashes.
- `packaged-cast/result.json`: exact loaded meshes/classes/clips, contacts and measured lighting.
- `packaged-cross/result.json`: 40 committed transitions and negative-case recovery.
- `packaged-episode/`: fresh route assertions and frame trace with neutral-review lighting disabled.
- `preservation-final.json`, `inputs-cook.json`, `inputs-after-qualification.json`: retained source/content/package identity checks.

`editor-cast-final/` in the parent evidence folder is the earlier full-cast controller-light qualification before suppressing Aso's actor-specific fills; it is not substituted for the final balanced packaged result. Trial captures differ in animation timing and, for the final launcher scene, source map; they are diagnostic comparisons rather than photometrically identical A/B images.

**Next decision:** review the now-visible character defects. Aso's extreme-pose robe penetration and simplified face/hands remain unresolved; no character or environment creative gate was promoted. Environment review, baked lighting, mobile, broader navigation, final audio and long-session memory remain open.
