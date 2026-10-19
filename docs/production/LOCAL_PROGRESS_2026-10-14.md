# Local production checkpoint — 14 October 2026

Branch: `feature/local-milestone-verification`. Base/current commit: `ec7bf0bcf16634a13c12e92433e9731064890e80`; this checkpoint is **uncommitted work**, not that commit's build. No commit, push, merge, deployment, signing, purchase or licence acceptance occurred.

The bounded production episode is **not finished**. Concrete progress is a controllable imported spider proxy, a real technical Level Sequence with native lifecycle handling, safer versioned checkpoints, an exercised Development Linux package, an actual failed Android package attempt, and guarded native-build policy source. Final art, production animation/IK, mission pursuit, final audio, mobile and services remain open.

## Installation and protected inputs

- Existing engine reused: `/home/favl/Unreal/UE_5.8.3-58210709`, UE 5.8.3 / CL 58210709; clang 20.1.8, bundled .NET 10.0.203. Exact Build.version pin retained.
- Original kits, source snapshot, Kwaku revision 2, subsequent revision 3, publications, saves and failed graphics reports retained. Kwaku stays campaign default; Ananse stays separate with no permitted powers. No cosmetic publication was rewritten or invented.
- Optional production patch SHA-256: `496e1c55dc65065bbb44448e640a703d721af35b3e0b77abd5173cebf5933e50`. Twelve additive files passed `git apply --check` and applied without replacing local work. Dialogue/shot/audio/animation data are authored drafts, not recordings or finished assets.
- Character archive SHA-256: `b1660c65bfffcfb58b57f8c0bbdbcbcfcf41ef2d611a8217b652d876da4f275b`; original GLB `1e94f6493d1c974c69722c9d5ca839bc3fcf87bd62e03225e1e6be8fa55e249e` retained unchanged. The source gate's 29 manifest matches, 22 unit tests and 200 custom predicates remain separate from native evidence.
- All runs use exported catalogue hash `4e37e276855d51bcd73d95ab9ac25db4d43b0822a039e23e27a4278dd7a2019f`, including reviewed Kwaku revision 3. No asset metadata grants powers.

## Changes and executed results

| Files/group | Change and verification |
|---|---|
| `AGENTS.md`, `README.md` | Parallel production execution order and corrected actual progress; safety retained |
| `production/*`, production work-order/checker/test files | Additive drafts and release-consistency checker; 54 focused tests, intentionally incomplete example BLOCKED (exit 1) |
| `AnanseCinematic.*`, mission/header, native cinematic tests, Build.cs | Real Sequencer playback; balanced input locks, camera/possession/movement restoration, idempotent durable events; finish/skip/cancel exercised |
| Mission schema-2 save code | Character/map/content binding and completed presentation events; narrow schema-1 compatibility; incompatible/unreadable saves retained, active-presentation save/load refused. Content-version migration beyond identical hashes remains required |
| `AnansePlayer.*` | Validated active character catalogue lookup; missing binding grants no default powers; ESC/controller skip; separate non-Kwaku save slots |
| `AnanseSpiderLab.*`, import tests, world HUD | Custom SkeletalMesh player in isolated lab; original movement/camera reused; F1–F4 baked clips; explicit proxy/no-power HUD; no live IK or cloth claim |
| Import, lab and sequence scripts; project plugin config | Installed Interchange GLB import and real map/LevelSequence creation; SequencerScripting enabled locally, no external plugin |
| Runtime verifier, launcher, build wrapper, packaging config | Actual evaluated clip motion, cinematic lifecycle/restart checks; optional ANSI allocator and explicit lab cook; fresh evidence/output guards retained |
| Native workflow/policy/tests | Trusted manual candidate/ref validation before self-hosted scheduling, protected environment and opt-in runner approval, pinned actions; 10 tests. Remote protections/runner/hydration are not configured or executed |
| `.gitignore` | Newly generated proxy, lab and technical sequence remain local, alongside original protected evidence/kits |

Fresh full Python regression: **130 passed**, zero failed/skipped, exit 0 (`pytest-final-clean.xml`). The first final invocation failed before collection because inherited ROS Python/plugin paths tried to load an unavailable `yaml`; the rerun cleared `PYTHONPATH` and disabled external plugin autoload only for that process. ROS/system Python were not changed. JavaScript and authoring-script syntax checks passed. Unchanged studio HTTP/browser checks were not rerun or added to these counts.

Final native automation: **8 discovered, 8 executed, 8 passed**, engine/wrapper exit 0, headless NullRHI:

- `Ananse.Mission.Negotiation`, `Ananse.Mission.PowerBudget`
- `Ananse.Cinematic.DurableEvents`, `Ananse.Cinematic.InvalidBinding`
- `Ananse.Save.BindingAndLegacyPolicy`
- `Ananse.Character.ImportedProxy.Anatomy`, `.Weights`, `.AnimationIsolation`

Editor builds 06–10 exited 0. Earlier failed builds, imports and test attempts remain recorded. Headless tests are not rendering evidence.

## Real imported assets and rendering

Current root: `/Game/Characters/AnanseSpider/Proxy_GLTF_v002`. Import output is one `AnanseSpider_PROXY` SkeletalMesh, custom Skeleton, automatic PhysicsAsset, four `AnanseSpider_PROXYA_*_Proxy` AnimSequences and seven material assets. Six sections are used by source geometry. The automatic PhysicsAsset is not a qualified production physics rig; lab mesh collision is disabled and the existing controller capsule owns movement.

The default GLTF conversion maps source +Z forward to Unreal +Y. A task-local generic pipeline applies −90° yaw with scale 1; no global importer toggle or source mutation. Native measured rest bounds are **X 132.388 / Y 158.395 / Z 207.916 cm**. Tests check all 102 names/parents, skin normalization, clip durations (3/8/3/4 seconds), eight-chain isolation and +X orientation. Blender is absent; no FBX/.blend or Blender round-trip is claimed.

`/Game/Characters/AnanseSpider/Lab_v001/L_AnanseCharacterLab` has a floor, unqualified 15-degree ramp, player start and diagnostic dynamic lights. It is not a bake or terrain-contact gate. Three consecutive final PIE runs (`rendered-spider-02/03/04`) each exceeded 60 seconds with exit 0 and orderly play/close. Each clip produced measured live component-space bone motion. Packaged `package-spider-02` also passed 60 seconds. Screenshots are real Vulkan framebuffer captures; input was simulated through native bindings, not physical keyboard/controller/touch qualification. No frame-time, stance-drift or penetration acceptance is claimed.

`/Game/Production/Market/Technical_v001/LS_MarketOpening_Technical` is a 35-second, five-camera-shot technical sequence over the existing greybox. It is entered through the native smoke harness; automatic campaign staging, final dialogue/performance/subtitles/audio remain unfinished. Rendered and packaged runs tested camera ownership, input locks, ESC skip, cancellation without award, natural finish with award, duplicate-event refusal and subsequent movement. The cinematic checkpoint survived a separate game-process restart, including mission fields and transform.

## Failures retained and fixed

1. Skin-weight test initially linked an unexported engine method. The fix uses actual public buffer/vertex data; assertions were retained.
2. Initial import failed anatomy orientation/width. A new versioned import corrects the installed importer's basis. A subsequent test caught changed output paths; paths were corrected from actual imported objects. No failed report was relabelled.
3. First rendered natural finish failed: UE broadcasts `OnStop` before `OnFinished`. Deferring external-stop cancellation one game tick lets the finish event win; explicit cancellation/EndPlay remain immediate and timers are cleared. The retry passed.
4. First packaged lab launch failed to load the map because command-line cook selection overrode MapsToCook. `--include-character-lab` explicitly includes both maps and refuses a missing lab. A new package and outside-editor retry passed.
5. The original Mimalloc ICU/Slate shutdown fault remains unresolved. Final editor/package scenarios used **`-ansimalloc`**; orderly exits under this workaround are not root-cause repair.

## Fresh package and launch

Package: `/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261014T063208.061158Z/`.

Executable: `Ananse/Binaries/Linux/Ananse`, SHA-256 `8f34b3ac9c5a495936cf8e028e3bc5d846fd2f086393ea8addd1aa996e820e2f`.

Cooked `Ananse-Linux.ucas` SHA-256 `76e1678376fd9673bfbf115c7e5ff7489bdc75d35eedf69500dc20d1f1cfe171`. Source GLB hashes are not cooked-artifact hashes. All selected container/launcher hashes are in the ignored `package-hashes.json`.

```bash
cd /home/favl/Downloads/ANANSE_Production_Starter
env -u PYTHONPATH -u LD_LIBRARY_PATH ./Builds/Linux/20261014T063208.061158Z/Ananse.sh \
  /Game/Characters/AnanseSpider/Lab_v001/L_AnanseCharacterLab -ansimalloc -windowed
```

The current package also passed the original negotiation route through spatial interactions and three-power checks (`package-route-02`), followed by F5 save, normal process exit and F9 restore in a new package process (`package-route-restart-02`). All persisted mission fields, transform and relative power/cooldown timers matched. This is the existing greybox route, not the new finished pursuit/epilogue.

Omit the map argument for the existing Kwaku market greybox. WASD/mouse/Space use the existing controller; lab F1–F4 select clips. This is a Development candidate with diagnostic HUD and proxy art, not a production release.

## Evidence and dependent blockers

Fresh evidence root: `.local/verification/production-20261014T055636.697392Z/`. Every runtime subdirectory contains exact `command.json`, `launch.json`, full logs, native assertions, screenshots and actual process status. `native-tests-final`, `linux-package-02`, `spider-import-03.json`, `package-hashes.json`, `changed-source-hashes.json`, `native-source-asset-hashes.json` and final pytest XML preserve the corresponding commands/results. Android evidence is separately under `.local/verification/android-production-20261014T055622.823763Z/`.

- **Linux:** imported/possessed proxy and technical opening work. Still required: live contact IK/custom control assets, final deformation/face/cloth/LODs, actual patrol/pursuit/route/epilogue production gameplay, finished audio/accessibility, studio 3D/variant round-trip and clean asset hydration. Environment ZIP remains absent. Original graphics diagnostics remain separate.
- **Android BLOCKED:** Turnkey exited 0 but reported SDK Invalid; actual UAT package attempt exited **6**, `Platform Android is not a valid platform to build. SDK validation failed`. Installed engine requests API36, build-tools36.0.0, NDK27.2.12479018. Java11.0.32.1 detected; no adb/qualified SDK. Empty `Builds/Android/20261014T055711.298497Z`, no APK/AAB. Requires approved official user-local matching tools, personally handled licences and named device qualification.
- **iOS NOT TESTED:** authorised Mac/Xcode/signing/device path absent.
- **Cloud NOT IMPLEMENTED/DEPLOYED:** no accounts, region/cost approval or staging. Offline save improvements are not a cloud-service adapter.
- **Art/audio:** engineering proxy is visibly unlike the final reference. Four arms/four legs are preserved, but final mesh, organic proportions, surface detail, soft deformation, expressive facial controls, clothing and approved recordings still require production/review ownership and budget. No external uploads or purchases occurred.

Next executable native task: live four-leg contact controls on the qualified rig, followed by played pursuit/capture/retry and production presentation entry points. Asset/audio/device/cloud decisions block their dependent gates only. Release evidence remains BLOCKED; never substitute this document for those gates.
