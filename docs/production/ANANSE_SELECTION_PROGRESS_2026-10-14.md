# Existing Ananse selection integration — 14 October 2026

In progress. Branch `feature/local-milestone-verification`, base `ec7bf0b`. No commit/push/install. The user switched the single-character scope from OseboLeopard to AnanseSpider after input verification.

Existing mesh, skeleton, PhysicsAsset, four clips, native contact solver and original lab map are reused. New compiled Blueprint and typed PrimaryDataAsset live in `/Game/Production/Characters/SpiderSelection_v001/`. No reimport, proxy generation or campaign identity/species change.

New lab-only controller performs allowlisted asynchronous loads and compatibility checks before collision-aware spawn/possession. Cancellation generations reject stale callbacks; failures retain the current pawn. Swaps remove old input mappings and reset transient movement/contacts. Lab replacements receive no narrative powers. Kwaku remains the campaign default.

Home selects Ananse; End selects the existing primitive Kwaku development fixture. F1–F4 retain existing clip selection; V toggles actual mesh wireframe; P pauses/resumes. F6/F8 and lab F5/F9 use `AnanseLabSelection_v1`, separate from campaign progress. Unsupported profiles are retained and saving is refused pending explicit recovery. There is no automatic cross-publication migration.

The Kwaku fixture is NOT a qualified second skeletal family. This work does not close that acceptance gate, physical controller/touch coverage, independent 3D studio preview, publication of the native definition, full rig authoring or final art review.

## Preserved failures

An initial wrapper invocation used an unsupported engine-root flag. The first editor asset command used a relative project path and exited 1; the absolute-path retry created the assets. Build attempts caught a protected input-enumeration API, missing forward declaration and incorrect trace include; corrected builds passed. The first rendered assertion report passed but process shutdown timed out at 180 seconds and was terminated: NOT an accepted run. The harness now uses the existing delayed framebuffer/frame-trace shutdown sequence. Earlier stress runs lacked a requested-design/class assertion and are superseded by the strict final verifier. All reports remain in `.local/verification/spider-selection-20261014/`.

The initial Python invocation inherited ROS test-plugin paths and failed before collecting tests. Process-local PYTHONPATH removal and disabling unrelated plugin autoload produced the actual 146-test pass; no system packages/environment files were changed.

The ANSI allocator workaround and separate detailed CPU-trace shutdown defect remain unresolved. No full CPU trace is claimed.

## Remaining assets

Native IK Rig, Control Rig Blueprint and Animation Blueprint assets are absent. The existing animation/contact implementation is native code, not a renamed Blueprint. Original GLB/OBJ and rig manifest remain; no editable Blender scene or newly model-derived technical views were produced. Blender is absent; official release-index access returned HTTP 403, and installation remains unapproved. No download restriction was bypassed. The engineering proxy is not reference-faithful production art.

## Initial packaged result and visual correction

The first new package `Builds/Linux/20261014T215100.922322Z/` passed three rendered 60-second/40-swap sessions, including two committed process-restored profiles. Its ELF hash is `2af6f5a485f5ca8f2c780f55b13d5760ae331e88554b140c59cc0d43e801d9f8`. The keyboard run exited 0 and visibly selected both fixtures, but visual review found that V did not change the shaded mesh: the engine inspection material was unavailable. That run is not accepted for wireframe. The original screenshots/report and an explicit failed visual audit are preserved.

A new project-owned `M_LabWireframe` has actual wireframe rasterization, unlit output and skeletal usage, and is included through the existing scoped cook rule. Native automation asserts those properties. The UI harness now requires logged committed selections, material binding/restoration, committed profile recovery and a frozen world clock between pause/resume; normal exit alone cannot satisfy it. Final corrected package/results are pending below.


## Further corrections and compatibility

The next keyboard trial ran beside another owned game and received no input while unfocused. Every new UI assertion correctly failed. The harness now focuses and rechecks ownership of its own window before each key; it never targets another application's window. The focused repeat on `20261014T215857.515384Z` passed all six UI checks and its real wireframe capture was reviewed. A scripted window exit is kept separate from visual acceptance.

Routing ordinary lab F5/F9 to the new profile would have broken the existing contact verifier. `AnanseUsesDiagnosticCheckpoint()` preserves its enabled, explicit development-only `AnanseVerify_` slot for contact/spider modes; Shipping returns false. Original test identities and contact assertions remain unchanged. Normal lab F5/F9 still use the dedicated profile. The final candidate must pass the original cooked terrain/checkpoint test before this correction is accepted.

The primitive Kwaku lab HUD now explicitly states that narrative powers are disabled and it is not a qualified second skeletal family; campaign presentation remains outside this branch.

A 120-second packaged negotiation/pursuit regression on `20261014T215857.515384Z` reached technical episode completion and exited 0. This is one representative route on that source revision, not a rerun of every route/outcome or a final-art approval.

The first final contact invocation omitted its explicit fixture map and therefore loaded the campaign default; the unchanged verifier rejected the non-spider pawn immediately. That failed report is preserved. The corrected command names `/Game/Characters/AnanseSpider/ContactLab_v006/L_AnanseContactLab`; no test assertion was relaxed.


## Final candidate and executed checks

`Builds/Linux/20261014T220439.626105Z/` is the final selection-integration candidate, **not a production release candidate**. Fresh editor build 15 and native automation 06 passed: **16 discovered/executed/passed**. Full current Python suite: **159 passed**; the work-order input suite is a separate **20 passed**. JavaScript syntax and Python compilation checks passed. Tests were not weakened.

Three separate final-package lab sessions (`final-lab-01`–`03`) each exceeded 60 seconds and passed 40 requested-design/class-confirmed alternating transactions. The first two actually committed the previous process's saved lab selection. Each retained one usable controlled pawn, current input mapping, inactive prior mappings and no narrative power grants; generation cancellation was exercised. Per-leg positive evaluated samples meet p95 stance drift ≤2 cm, penetration ≤0.5 cm, segment error ≤0.1 cm, no joint violations and four solved chains. Full exclusions/coverage and scalar query/solve/frame timings are in `final-lab-contact-summary.json`; these final functional sessions overlapped the owned terrain process, so timing is observational desktop data, not a standalone benchmark or mobile evidence.

`final-keyboard` independently exercised owned-window synthetic OS keys: selection of both fixtures, the existing limb clip, true mesh wireframe, original material restoration, pause/resume with a frozen world clock, F6/F8 profile save/load, movement after reload and window-manager orderly close. All six structured checks passed and exit was 0. These are keyboard-path tests; physical keyboard/controller hardware and touch remain unverified.

Exact native source SHA-256: `449311c1f3fd46a6d9bcb5ff227dc329eafa9abb535e1d032636ca198d2b20e6`.
Required source asset aggregate: `b84ad75e9a06f679086f62b46ae02119fec598ae2e99eb18849dfb7b6925a490`.
Authoring/tool-source aggregate: `461145421f036b263a17cf03da61d70b9e3518c0e9d160c110fc523d77497c7f`.
ELF: `13155014b2e15dd56455d986b48f2b9063ace6e69b0ed36d2bc86262ef61d67d`.
UCAS: `65f83703ca6384a20ef1fb26927d51c7e10f33d82b244ab8b622a87c6dd5dee9`.
Publication remains `d35420a6279f459abd0b1cae0e417c8e`, catalogue hash `8751423ca1c06e3da01c8ddb3c69641a5521bd8aadc41963594f0aed29ce82c4`. The native selection definition is not yet a studio-managed published dependency. Do not conflate its asset revision 1 with narrative Ananse revision 3.

Verified launch from project root:

```bash
env -u PYTHONPATH -u LD_LIBRARY_PATH \
 ./Builds/Linux/20261014T220439.626105Z/Ananse/Binaries/Linux/Ananse \
 /Game/Characters/AnanseSpider/Lab_v001/L_AnanseCharacterLab \
 -ansimalloc -windowed -ResX=1280 -ResY=720
```

Engine: pinned UE 5.8.3 CL58210709; clang 20.1.8 and bundled .NET 10.0.203. DCC execution: none. No Blender installation/download/licence approval, driver change, system environment change, commit, push or deployment occurred.

The corrected original contact/checkpoint scenario (`final-terrain-02`) passed **240.0008 seconds** of cooked traversal with exit 0. Its unchanged assertions include “Dedicated spider checkpoint created through F5” and “F9 checkpoint load rebuilds transient contacts”. All four legs sampled flat, ramp, steps, uneven, moving and disappearing-support fixtures. Maximum per-leg p95 stance drift was **0.000003690 cm**; maximum penetration **0.000003804 cm**; invalid transforms and joint-limit violations were zero. These are evaluated tarsus/contact-offset measurements, not target-only checks or general production deformation approval.

| Leg | Stance samples | Excluded swing/airborne/invalid-contact samples |
|---|---:|---:|
| front L | 69,403 | 29,152 |
| front R | 65,480 | 33,075 |
| rear L | 62,511 | 36,044 |
| rear R | 55,547 | 43,008 |

Coverage counters include both actor names and fixture aliases; do not add them as independent samples. Full reach/support/transition data remain in the actual report/CSVs. P95 scalar query cost was 17.091 µs, solve cost 51.168 µs and component-tick interval 9.565 ms. These are desktop component measurements, not GPU times or mobile qualification.

Final safety checks: all three build-input aggregates match the pre-cook snapshot; all 16 original native assets and protected rollback executable/catalogue hashes are unchanged; staged paths are empty. Targeted tracked/index and actual cooked-config scans found zero nonempty assignments for the two known file-server token keys. This is not a comprehensive secret/history claim. Raw inputs, generated assets, rig maps and evidence remain local/ignored; existing publications and Kwaku history were not edited.

## Changed paths and open work

Native additions: `Unreal/Source/Ananse/AnanseLabSelection.h`, `.cpp`, `AnanseSelectionTests.cpp`. Extensions: `AnansePlayer.h/.cpp` (owned mapping cleanup, lab power suppression and profile routing), `AnanseSpiderLab.cpp` (existing lab controller binding), `AnanseWorld.cpp` (lab feedback), `AnanseRuntimeVerification.h/.cpp` (development diagnostic checkpoint query), `Unreal/Config/DefaultGame.ini` (scoped cook inclusion). Existing dirty work was preserved.

Authoring/verification additions: `scripts/build_spider_selection.py`, `build_spider_wireframe.py`, `run_lab_selection_check.py`, `native_lab_ui_smoke.py`; `tests/test_lab_selection_reports.py`; this handoff and README reconciliation. Native content additions are the actual `BP_AnanseSpider`, `DA_AnanseSpider`, `M_LabWireframe` under the versioned production folder. Local generated source records: `SourceArt/Characters/AnanseSpider/INTEGRATION_PATH_MAP.json` and `EXISTING_SOURCE_RIG_MAP.json`, including 102 actual source joints, four socket bones and original source hash. Local-only Git exclusions protect the extracted work-order inputs and generated records; nothing was staged.

**Full character gate is still open.** Missing IK Rig/Control Rig/Animation Blueprint assets are not represented by the native contact class. The new native definition is not yet published through studio dependency records, and a complete isolated 3D gallery/turntable, cosmetic publication cycle on this definition, fault-injected runtime load/spawn cases and memory soak remain work. A qualified second skeletal family is unavailable in the inspected bindings; an asynchronous clarification requests its existing project path rather than starting another character. Physical controller/touch and Android/iOS remain unqualified. Original proxy geometry/animation are reused, not final reference-faithful character production.

The next implementation remains **AnanseSpider**. Do not start another skeletal family or call this a finished character/release. Complete the missing authoring/integration gates and source-view/art dependencies without replacing the working rig.


Machine-readable final results: `.local/verification/spider-selection-20261014/FINAL_STATUS.json`; complete file hashes: `final-package-hashes.json`; final safety audit: `FINAL_SAFETY.json`. The final terrain run has 64 unchanged checks and normal lit rendering.
