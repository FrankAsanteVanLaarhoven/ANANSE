# Episode content integration — 14 October 2026

Verified episode-runtime checkpoint; this document does not designate a production release candidate.

Branch: `feature/local-milestone-verification`. Base commit: `ec7bf0bcf16634a13c12e92433e9731064890e80`. All current source changes remain uncommitted. No push, merge, deployment, installation or licence acceptance occurred.

Fresh evidence: `.local/verification/episode-content-20261014/`. Original kits, previous diagnostics, saves and publications remain separate. The contact/pursuit rollback at `Builds/Linux/20261014T104432.399054Z/` remains protected.

## Implemented runtime behaviour

- Reused `UAnanseMission`, existing pursuit/powers/input and cinematic lifecycle. Escape now has a separate physical interaction before the consequence choice. Previously the exposure marker could not meet the protection-side escape gate's position condition.
- Both consequences resolve authored, speaker-labelled draft dialogue through ordinary interactions. Broken-promise lines and trust effects remain distinct. Consumed line IDs persist without awarding outcomes or trust again.
- An opt-in `-AnanseEpisode` flow adds New Game, Continue, pause/resume, persisted subtitle sizing and a development completion screen to the existing native Canvas/input architecture. `P` pauses presentations; Escape resumes a paused menu or skips an active presentation. No second application or mission state machine was introduced.
- New Game starts the existing technical opening. Five authored opening subtitle IDs follow sequence time; finish, skip and cancellation clear presentation state and restore control. These are unrecorded English drafts, not completed voice performances.
- After the consequence responses, an actual gate travels to `/Game/Production/Sanctuary/Technical_v001/L_StorySanctuary_Technical`. Kwaku stays possessed; a separate imported eight-appendage Ananse is present. Three real speaker interactions reach the canonical episode completion state.
- The sanctuary is a **six-actor technical level**, with a floor and dynamic diagnostic lighting. It is not the supplied Story Forest environment, a finished clearing, a light bake or a production audiovisual section.
- Schema 4 binds episode ID, character, map and exact catalogue hash. The destination checkpoint is written before level travel. Relative active power timers and pursuit recovery are deliberately cleared at the transition; narrative facts, resources, route, outcome, trust and consumed events remain. Transient actor/foot contacts are rebuilt. Historical schemas 1–3 retain their narrow binding policy; mismatched content remains rejected and preserved, not silently migrated.

## Authoring and actual asset binding

`scripts/verify_spider_cosmetic.py` operates through the existing loopback API with distinct ephemeral local roles. It checks unauthenticated access, wrong-role editing/review/publication, stale editing and stale review. These roles are not independently identified production reviewers.

The script registered the actual native proxy skeletal source asset in **quarantine**, reviewed its metadata, revised Ananse and published an immutable prototype snapshot. The source `.uasset` hash is explicitly distinguished from GLB and cooked hashes. No powers, Kwaku revisions or prior publications were changed.

Ananse revision 2 uses cloth `#48766B`, publication `63688c0f9b98407d80b2c0cae4876eac`, hash `ad89e76c7d34711e447f62ce431e49af804c384858907cf62b9dc7448c9a2f97`. Revision 3 restores the original `#AD6E36` and original body binding through **new** publication `d35420a6279f459abd0b1cae0e417c8e`, hash `8751423ca1c06e3da01c8ddb3c69641a5521bd8aadc41963594f0aed29ce82c4`. Both snapshots and all Kwaku history remain unchanged. The restore helper preserves unrelated current edits.

The live imported mesh consumes the published cloth colour through its runtime `Cloth_Proxy` slot. An unqualified body replacement is blocked rather than silently rendering a biped. Facial morphs, textile detail, cloth simulation, final deformation and production mesh/texture approval remain missing.

## Observed failures and fixes

1. The first rendered choice verifier mistook the escape key release for the subsequent choice press. Its failed run is preserved; explicit input sequencing fixed it without changing gameplay assertions.
2. The diagnostic light fixture initially used a nonexistent accessor. Builds 10/11 exited 6. The installed headers supplied `GetLightComponent()` and a checked point-component cast; later builds passed.
3. The first Linux cook failed because `ImportedMaterialSlotName` is editor-only. The runtime uses `MaterialSlotName`; native read-back verifies exactly one cloth slot. The failed archive/output remains preserved.
4. The first cooked colour capture had correct MID values but displayed Unreal's grey fallback. The log proved missing skeletal usage on the old static prototype material. Its earlier report alone is insufficient for visual acceptance: `cosmetic-render-audit-01.json` marks that gate failed. The old material was preserved; a new `/Game/Production/Characters/SpiderLook_v001/M_ProxyClothVariant` explicitly enables skeletal usage and connects the published parameter to base colour. New native and launch checks reject usage/fallback failures.
5. `protected-artifact-audit.json` initially compared nested metadata with strings and falsely flagged ten files. The corrected `protected-artifact-audit-02.json` extracts the recorded hashes and verifies all 16 source assets and both older package manifests unchanged. The erroneous report is preserved with an explanation.
6. The first packaged before-choice restart restored its documented fields, position and control, then failed because a 50-second readiness timeout also applied to the required 60-second idle observation. The timeout now applies only to readiness phases; all restoration and duration assertions remain.
7. Comparing real captures exposed inherited mannequin yaw when the optional body reference was present. The shared loader applied −90° even to the already-qualified +X spider. The spider class now explicitly preserves its imported basis after the shared load; the live check asserts component/actor forward alignment. No skeleton or movement controller was rebuilt.
8. One aligned-candidate package attempt overlapped the editor build and failed on the global UBT mutex. UAT labelled exit 10 `Error_SDKNotFound`, but the complete first error was `Failed (ConflictingInstance)`. The retry runs after the editor build. This was not a new missing Linux SDK and did not justify any tool installation.

## Config credential boundary

The earlier `AuthenticationToken` scan was narrow. A later engine-generated `SecurityToken` assignment was found in tracked working config, with **zero in the index and HEAD**. Its value was never printed. The original config was retained in a private 0600 backup. No token was rotated and no history was rewritten.

Installed AndroidFileServer source explains regeneration: its default is `[AUTO]`, and `PostInitProperties` generates a GUID and writes default config. Removing the entire section allowed that to recur. `scripts/prepare_native_config.py` now retains unrelated settings, explicitly empties both token keys and disables the unused project-local file-server/network/shipping switches. Native build/open/test/cook entry points prepare it idempotently. Packaging also deny-lists both token keys.

Actual cooked `DefaultEngine.ini` read-back found **zero nonempty assignments** in the inspected fixed-material and restored candidates. This is stronger than a source-only check, but remains a targeted file-server-token audit, not a comprehensive secrets guarantee. The installed UnrealPak lists entries correctly but its extraction path acquires a backslash on this host. The audit reads the uncompressed entry using the installed `FPakEntry::GetSerializedSize` layout and verifies the exact bytes against the independent native listing's SHA1 before scanning; missing, encrypted, unsupported or mismatched entries fail closed. No decoded config values enter reports.

The pre-cook snapshots remain immutable. Engine-generated settings changed `DefaultEngine.ini` between the earlier fixed-material and restoration snapshots; `candidate-source-differences.json` records that byte difference separately from the publication change. Final prepared inputs are captured after sanitization. No byte-identity claim is made across different snapshots.

The existing allocator issue still requires process-local `-ansimalloc`. The separate detailed-CPU-tracing shutdown defect remains unresolved. Only frame traces/native instrumentation support the measurements actually recorded; no complete CPU timeline or mobile performance is claimed.

## Verification already completed

- **146 Python tests passed**; JavaScript syntax, Python compilation and whitespace checks passed.
- **14 native tests discovered/executed/passed**, including all original identities and new episode/dialogue/save assertions. These are headless results, separate from rendering.
- Rendered editor-game processes completed negotiation/protection, rooftop/exposure and social/protection checks. The social run included actual map travel, separate Ananse presence, epilogue interactions and a saved completion state; 120 seconds and exit 0.
- A 60-second rendered opening lifecycle run observed all five subtitle IDs and verified finish/skip/cancel restoration.
- Owned-window synthetic X11 tests exercised menus, New Game, pause/settings/resume, skip, F5 and Continue. Playback stayed at **9.5167 seconds** throughout pause/settings, then resumed. The owned window closed through WM_DELETE_WINDOW with exit 0 and no forced termination. This is not physical-controller/touch evidence.

## Executed packaged results

All selected runs below used real Vulkan rendering at the requested 1280×720 window size, the normal lit view, frame-only traces and `-ansimalloc`. Input-event and owned-window tests are synthetic, not physical hardware coverage. Every selected run exited 0 without forced termination.

| Candidate / evidence | Actual coverage |
|---|---|
| `Builds/Linux/20261014T203036.627899Z/`, `package-change-matrix.json` | **Six of six** route/outcome combinations: negotiation, social and rooftop × protection/exposure. Each 120-second process used actual route prerequisites, ten capture/retry cycles, separate escape/choice interactions, consequence lines, map travel, epilogue and saved completion. This candidate's cloth-rendering fallback failed separately; it is gameplay evidence, not final visual acceptance. |
| `Builds/Linux/20261014T204320.051945Z/` | Correct skeletal shader usage; actual green cloth captured, zero fallback warnings. Full negotiation/exposure episode passed. The first idle restart verifier failed as described above. |
| `Builds/Linux/20261014T205847.155447Z/`, `package-final-results.json` | Full social/exposure episode and **three separate 60-second process restarts** before the choice, at sanctuary arrival and after completion. Declared state/transform/control and consumed IDs restored; no duplicated durable events. Packaged X11 menu/pause/settings/Continue test also exited 0, with the opening clock frozen at 9.517 seconds during pause. |
| Aligned green candidate, `green-aligned-artifact-path.json` | Immutable Ananse revision 2 actually cooked with the corrected +X binding. 60-second rendered clip/movement/material checks passed; captured green cloth, correct orientation and zero fallback warnings. |
| **Latest: `Builds/Linux/20261014T210638.358735Z/`** | Immutable revision 3 cooked and observed as amber-brown after a new process start. Actual ordinary New Game level option → natural opening → negotiation/protection → played pursuit → consequence → sanctuary → completion ran for **120 seconds**, saved completion and exited 0. A further separate **60-second process restart** restored completion without repeating events. All material/basis checks passed. |

The six-case artifact and latest artifact have different full fingerprints. The production gameplay implementations (`AnanseMission.cpp`, `AnansePlayer.cpp`, `AnansePursuit.cpp`) are byte-identical across them; later custom-spider rendering, diagnostics and config changes are recorded separately. Six runs on the older candidate are **not** reported as six runs of the latest binary. The latest run's native save also retains the opening's durable completion ID. These checks establish runtime flow, not a measured 15–20-minute content length or player-comprehension study.

Latest executable SHA-256: `bc1efde8a991327110bd94d29b5bad943a2c845cbc5ca70618b3d4ea40c2cadc`.

Latest cooked `.ucas` SHA-256: `c9d5abada8bb741d86ecff0eac2f03ec5a5dbe16637d5658fde4b8c0ce419bd9`.

Latest `.pak` SHA-256: `b45d4a09eda102af0c8ef01bfcb13e7e2c641d820a6c567c391b7ac10f261200`.

Exact native/config input SHA-256: `151950bf1f08c53bd642f06577488e5a3d1475a675164be4ffeda835d6861f5d`.

Required source-asset SHA-256: `be032875ec33118b6d08fa6cd46d4cb34a6658a9291a631b47ede31b1aeb0784`.

Authoring/build-script SHA-256: `c711fb66f5cc11415b8d8eca0f89944ea0e4f97c556bd6cb9a9439a809abcdac`.

`FINAL_SOURCE_SAFETY.json` verifies the current native/config, required asset and authoring source bytes match this selected cook's inputs. `latest-package-artifacts.json` records every archived artifact hash, excluding runtime-created Saved files. `executed-command-index-final.json` contains 53 completed command entries; each attempt's launch/command records retain its own context and exits. `FINAL_STATUS.json` is the compact result index. No JSON status edit substitutes for the underlying runs.

New authored native assets:

- `/Game/Production/Sanctuary/Technical_v001/L_StorySanctuary_Technical`
- `/Game/Production/Characters/SpiderLook_v001/M_ProxyClothVariant`

The existing `/Game/Characters/AnanseSpider/Proxy_GLTF_v002/` mesh, skeleton, materials and four clips remain source-byte unchanged. There was no re-import, engine reinstall or Blender execution. The exact reused toolchain is UE **5.8.3 / CL 58210709**, clang **20.1.8**, bundled .NET **10.0.203**. The project environment reports Python **3.13.13**, Node **22.23.2** and Git **2.34.1**.

Genuine captures are in the ignored evidence folders: `package-green-aligned-render-01/native-game.png`, `latest-cloth-restored-01/native-game.png`, `latest-full-episode-01/native-game.png`, and `package-final-ui-01/*.png`. The appearance comparison deliberately uses a declared transient diagnostic fill and inspection camera. It is not production lighting or faithful-art approval.

From the project directory, launch the verified Development episode:

```bash
env -u PYTHONPATH -u LD_LIBRARY_PATH \
  ./Builds/Linux/20261014T210638.358735Z/Ananse.sh \
  -ansimalloc -windowed -ResX=1280 -ResY=720 \
  -AnanseEpisode -AnanseCheckpointSlot=AnanseEpisode_20261014_Local
```

Press **N** for New Game, **C** for Continue, **P** to pause, **Escape** to resume/skip, **- / =** for subtitle size in the menu, **WASD/mouse** to move/look, **E** to interact, **1/2/3** for permitted powers, and **F5/F9** for the selected local checkpoint. After escaping, choose a consequence, interact again for its authored responses, then use the Story Road gate and speak with Ananse three times. Keep the dedicated slot to Continue after restart. A content-hash mismatch preserves the old save and reports incompatibility; it does not silently migrate it into another publication.

The contact/pursuit rollback remains at `Builds/Linux/20261014T104432.399054Z/`. Its ELF and cooked `.ucas` were rehashed unchanged. The supplied source-asset and older-package manifests also match; all failed attempts and original crash evidence remain separate and intact.

## Changed files and purpose

| Files | Purpose |
|---|---|
| `AnanseMission.h/.cpp`, new `AnanseDialogue.h/.cpp` | Existing canonical mission continuation, guarded authored dialogue, separate escape, versioned cross-map saves and epilogue completion |
| `AnansePlayer.h/.cpp`, `AnanseWorld.cpp`, `AnanseCinematic.h/.cpp` | Existing native menus/input/HUD, subtitle sizing/timeline and presentation cleanup |
| `AnanseSpiderLab.h/.cpp`, `DefaultGame.ini`, `build_spider_cloth_material.py`, `build_sanctuary_epilogue.py` | Qualified custom-basis/cloth binding, real skeletal shader and new versioned technical level/cook dependencies |
| `AnanseEpisodeTests.cpp`, runtime/pursuit verification files, `native_runtime_smoke.py`, `native_episode_ui_smoke.py` | Actual route, lifecycle, material/basis, packaged/OS-input and process-restart evidence with bounded checks |
| `stage_market_dialogue.py`, `verify_spider_cosmetic.py`, `test_market_dialogue.py` | Exact-byte dialogue staging and reviewed loopback cosmetic publication/restoration without overwriting unrelated edits |
| `prepare_native_config.py`, `audit_cooked_config.py`, `test_native_config_safety.py`, `unreal.py`, native config | Prevent file-server token regeneration, preserve private backups, audit real cooked config, include epilogue in fresh packages |
| `.gitignore`, README and this/Android approval documents | Keep generated/private material outside Git and reconcile actual local progress with earlier historical reports |

All earlier dirty files were preserved; this table describes the current session's extensions, not authorship reassignment of previous work. Generated native assets, packages, SQL backups, raw reports, screenshots and trace files remain ignored. No source kit or protected publication was overwritten.

## Remaining production gates

There are **zero source audio recordings/effect files** in the current project inventory. All 44 dialogue recording obligations and 24 cue briefs remain production work; no silence/test tone satisfies them. Independent audio buses, available original effects and a listening-reviewed mix are not completed by this checkpoint.

The 60–90-second production-target audiovisual section is **NOT PASSED**. The mesh is still a segmented engineering proxy; final silhouette/face/eyes/cloth/surface/deformation/animation and approved environment art, lighting and recordings are absent. The environment kit remains unavailable locally. There is no cultural/art approval, Blender round-trip, production Control Rig/Animation Blueprint asset, finished forest, baked-lighting acceptance, mobile/device performance or clean-checkout production asset hydration.

The studio's existing metadata/publication path is exercised; a real studio 3D preview and environment authoring remain open. Player cloud services remain separate and unimplemented; no staging/deployment result is claimed.

Android remains acquisition-blocked. See [the consolidated approval scope](ANDROID_APPROVAL_2026-10-14.md): pinned user-local tools, official sources, 989,727,090 bytes of SDK downloads plus Studio/JBR, a 32 GiB planning reserve and personal licence review. No unchanged failed Android package was rerun. iOS still lacks a qualified authorised Mac/Xcode/signing/device path.

The content-integration review target is 16 October 2026, a progress review rather than a promised final-release date. Frank Asante Van Laarhoven owns the unresolved art/audio staffing, creative/cultural approvals and platform-access decisions; no external reviewer or performer is invented here.
