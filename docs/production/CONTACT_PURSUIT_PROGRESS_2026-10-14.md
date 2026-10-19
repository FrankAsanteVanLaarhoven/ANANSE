# Ground contact and played pursuit — 14 October 2026

Branch `feature/local-milestone-verification`, base commit `ec7bf0bcf16634a13c12e92433e9731064890e80`. All changes remain uncommitted. Existing source, snapshots, publications and rollback package remain local and protected. This is a Development checkpoint, not the finished episode.

## Implemented native work

- `AnanseGroundContact.*`: four named supporting chains, support-local stance anchors, bounded swing trajectories, controlled released-leg targets, game-thread terrain queries, and a copied animation-worker pose boundary. Native animation owns pelvis adjustment; gameplay owns root movement/collision. Engineering knee flex is constrained to 5–155 degrees. No stretching is permitted. Four arms retain imported gesture animation.
- `AnanseSpiderLab.*`: reuses the existing movement/player, imported 102-joint proxy, and four source clips. Controlled walking is 35 cm/s with 35-degree/s turning. `L` switches live contacts/source-clip preview; the treadmill clip is not terrain locomotion.
- `AnansePursuit.*`, mission/save/world changes: opt-in technical introduction, perceived line-of-sight/last-known chase, six-second bounded search, collision-swept local stuck recovery, obstructed capture checks, idempotent entry/retry, and an actual permitted Mirror distraction. Kwaku stays campaign identity. Osebo remains a primitive engineering proxy. NavMesh coverage is not qualified; the exercised greybox fallback uses CharacterMovement sweeps.
- Schema 3 checkpoints persist pursuit state, cached knowledge, relative timers and pre-chase recovery. Schemas 1/2 retain narrow same-content compatibility. Incompatible saves remain intact. Raw actors and foot-support pointers are not serialized. Jump, Web Step, teleport/load and capture release transient motion/contact state. Spider capture hookup exists; the played chase is Kwaku's.
- Player movement/jump remain available after the consequence without clearing the outcome. Development manual runs can select a separate `-AnanseCheckpointSlot=...`; validation still rejects unsafe slot names.
- Native verification and launcher now bind dirty/untracked native source, source assets, catalogue, module and toolchain identity. Requested 60–600-second duration and normal lit rendering are mandatory. The owned possessed pawn runs the session harness; a moving unpossessed spider fixture is not a second player.
- `build_contact_lab.py`: versioned `/Game/Characters/AnanseSpider/ContactLab_v006/L_AnanseContactLab`, 19 actors, flat floor, 15-degree ramps, five 20-cm steps, 10/15/20/25-cm uneven fixtures, translated support and an occupancy-triggered disappearing support with a 20-cm catch surface.
- `DefaultInput.ini` removes only the inherited F1/F2/F3/F4/F5/F9 debug-command conflicts. `scripts/unreal.py` explicitly cooks the contact lab and forwards `-ansimalloc` to the cooker using the installed engine's AdditionalCookerOptions API.

## Executed results so far

The evidence root is `.local/verification/contact-pursuit-20261014T065510.860417Z/`. Each attempt has its own commands, logs, reports, actual screenshots and traces. Failed attempts are retained.

- Fresh Python regression: 130 passed. JavaScript and Python syntax checks exited 0. Studio/API/browser source did not change; historical HTTP/browser evidence is not rerun or relabelled here.
- Native automation: 10 discovered, 10 executed, 10 passed. Original eight identities remain; new identities are `Ananse.Mission.ProductionPursuitGates` and `Ananse.Save.PursuitRecoveryEnvelope`. NullRHI tests are separate from rendered proof.
- `terrain-contact-11`, `-12`, `-13`: each completed 240 seconds and exited 0. `-13` explicitly verified normal lit view index 3. Every leg recorded all six declared support categories. Per-leg p95 stance drift and maximum independently measured penetration were below 0.00001 cm; segment-length error and invalid transforms were zero; knee-limit violations were zero. Actual evaluated tarsus transforms plus the imported tip offset define the measured contact point. This is not a requested-target-only measurement.
- Drift excludes swing/airborne/released samples and records excluded counts; penetration includes those samples and queries actual collision occupancy. Raw stance CSV and CPU/frame/animation traces remain in each run. Reported query/solve times include the instrumented native work; these are desktop observations, not mobile/GPU qualification.
- `pursuit-06`: 121.49 seconds, ten real capture/retry cycles, actual obstructed capture below 100 cm for at least 0.35 seconds, permitted Mirror activation, played escape and consequence; orderly exit, normal lit.
- `pursuit-restart-02` and `-03`: two separate process starts loading slot `AnanseVerify_20261014T092445`, comparing documented fields/timers/transform/cached knowledge and recovery state; each then played ten capture/retry cycles and escaped, with normal-lit orderly exits. `-01` restored fields but failed because its harness resumed at the wrong interaction phase; preserved as failure.
- `pursuit-07`: 121.57 seconds, ten cycles/escape, and more than 509 cm of actual post-outcome input-driven movement without clearing the consequence. Its endurance rectangle encountered the real consequence marker; the subsequent fixture uses the verified clear x=1300 lane instead.

## Diagnosed failures and limitations

Early contact runs exposed unreachable-anchor gait deadlock, released-pose crouch/sprawl, and an interior ground-ray hit. The last cause was proven in-engine: a former ray started at Z=108.95 inside the Z=100–120 moving box, returned distance zero/initial overlap, and planted a foot there. An elevated ray hit Z=120 correctly. The query now starts 200 cm above its candidate and rejects initial overlaps. Assertions and limits were retained.

The original Mimalloc/ICU/Slate/SDL shutdown investigation is not resolved. `-ansimalloc` remains process-local. A failed first PIE contact process is retained separately from subsequent orderly standalone-game exits.

A fresh first package cooked successfully at `Builds/Linux/20261014T094057.160339Z/`, but its mixed test failed at 30 seconds: the harness incorrectly required the unpossessed companion to satisfy player-possession readiness. That candidate is retained as failed acceptance. The corrected harness filters the owned pawn, initializes companion walking physics and uses collision-clear endurance paths. Fresh package verification remains in progress; no ten-minute pass is claimed yet.

## Safety and dependent gates

Before cooking, editor-generated private settings were preserved in `.local/private` with mode 0600 and their Android file-server section removed from the working config. Tracked working files and the index contained zero authentication-token assignments; no values were printed, credentials rotated or history rewritten. Final checks will be recorded after all launches.

Engine reused: `/home/favl/Unreal/UE_5.8.3-58210709`, UE 5.8.3 / CL 58210709, clang 20.1.8, bundled .NET 10.0.203. No engine reinstallation, system Python/Java, driver, CUDA, ROS, Isaac Sim or shell-startup changes occurred.

Android remains BLOCKED: absent engine-selected `/home/favl/android-studio/bin/studio.sh`, SDK/NDK, and qualified JBR; PATH Java is 11.0.32.1. Installed engine requests SDK API 36, build-tools 36.0.0 and NDK 27.2.12479018 (r27c). Android platform/ARM64 support is present in the installed engine. No known-blocked packaging command was repeated. Approval for official user-local acquisition and personally handled licences remains pending. iOS and physical devices remain untested.

Final mesh/texture/deformation/facial/cloth/LOD work, production animation/control assets, final Osebo art/audio, other-route playthroughs, epilogue, environment kit integration, studio 3D/publication round-trip, clean asset hydration and player services remain open. No production, mobile, cultural approval or commercial release claim follows from this checkpoint.

## Packaged reliability investigation

`linux-package-02` and `-03` also cooked successfully into separate preserved directories. The first mixed fixtures exposed real collision with a stall; the patrol moved into the western clear floor area, with actual capsule sweeps required before motion. No collision was disabled or geometry removed.

`package-mixed-03` completed **601.63 seconds**, ten capture/retry cycles and escape, 1795.36 m of player movement and 201.34 m of spider movement with 115 passed progress windows. All four actual feet passed the contact limits (p95 drift/max penetration below 0.00001 cm), all transforms were valid, no stretching or knee-limit violations occurred. Desktop p95 frame interval/query/solve costs were 2.10 ms / 7.54 microseconds / 26.48 microseconds. The process then exited **139**, so overall acceptance is **FAILED**, despite gameplay assertions passing.

The shutdown assertion was `GetNumUsed() == 0` in `LockFreeFixedSizeAllocator.h:209`, followed by SIGSEGV. A shorter owned GDB reproduction stopped at `TLockFreeFixedSizeAllocator<65536,64,FThreadSafeCounter>::~TLockFreeFixedSizeAllocator` during libc exit; full thread stacks are retained in `package-shutdown-gdb-01/gdb.log`. The same short scenario without tracing exited 0, a discriminating diagnostic rather than full profiling acceptance. This is separate from the older Mimalloc/ICU/Slate failure.

Source now explicitly pauses/closes the trace and shuts down its worker **after** final gameplay assertions/framebuffer capture and **before** process exit, using installed TraceLog APIs. CPU/frame/animation profiling remains enabled through gameplay. The fix still requires a fresh packaged profiled run; the allocator error is not suppressed, and the underlying engine issue is not relabelled solved.

The original assets and rollback were rehashed: sixteen native source assets and eight package files remain byte-identical (`protected-artifact-check.json`). Package config extraction attempts using the installed UnrealPak returned 1 because its read path acquired a backslash separator; those logs are preserved. Source/index token checks were zero and the inspected staged INI contained no token. Decompressed packaged-config audit is not claimed complete.

## Profiling isolation and supported alternative

The explicit trace shutdown did **not** cure the detailed-CPU failure: `package-profile-exit-04` still exited 139. A controlled CPU+frame capture also exited 139, while frame-only and no-trace runs exited 0. Full CPU-channel capture remains **BLOCKED**. Installed CPU-profiler source retains dynamic scope names in memory-stack pages; that is consistent with the recovered allocator destructor stack, but no complete engine root-cause repair is claimed.

The launcher now has an explicit `--trace-preset frame` alternative (default `full` remains available for reproducing the failure). Frame tracing stays active through play, and the native evaluated-point CSV now records `query_us`, `pose_us` and `frame_interval_ms` per stance sample. Actual native p95 timings and all-state penetration remain in the reports. This provides measured contact/animation cost without pretending that a detailed CPU timeline passed.

A fresh `linux-package-05` candidate is undergoing the required 600-second mixed run with this explicit profile. The package remains under acceptance until its exit and the separate cooked contact-map run have succeeded. No failed full-trace result is rewritten as passed.

## Final verified Development candidate

The available Linux checkpoint is now verified with the explicit **frame-only plus native timing CSV** profile. Detailed CPU-channel profiling remains blocked; the original allocator workaround remains required.

Fresh candidate: `/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261014T104432.399054Z/`. `linux-package-05` build/cook/stage/package/archive exited 0. It includes the market, original Character Lab, Contact Lab v006, proxy skeleton/four clips, technical sequences and catalogue hash `4e37e276855d51bcd73d95ab9ac25db4d43b0822a039e23e27a4278dd7a2019f`.

- `package-mixed-05`: **601.70 seconds**, ten real capture/retry cycles and escape; 201.34 m spider traversal, 114 passed progress windows; native assertions, normal lit rendering, trace closure and process exit **0**. Per-leg p95 drift/max penetration remain below 0.00001 cm, with zero invalid transforms/stretch/knee-limit violations. Desktop p95 frame interval **2.09 ms**, contact query **7.07 microseconds**, pose evaluation **27.24 microseconds**. Inline instrumentation/CSV overhead is included; GPU cost/mobile performance is not established.
- `package-contact-05`: **240.00 seconds**, every leg on flat/ramp/steps/uneven/moving/disappearing support, jump, Web Step-motion reset and dedicated F5/F9 contact rebuild; normal lit, all native gates and process exit **0**. The spider has no gameplay powers: the Web Step transition check invokes the existing motion service as a named Development fixture, not permission coverage.
- Independent Euclidean CSV read-back passes drift limits and reads actual timestamped query/pose/frame timing columns. Stance rows exclude swing/airborne/released drift samples; native penetration metrics include those states. Full CPU timeline is explicitly unavailable.
- Current source regression: **130 Python passed**, **10 native discovered/executed/passed**, Python/JavaScript syntax and final whitespace check exited 0. Studio source is unchanged; no new HTTP/browser pass is claimed.
- Three normal-lit standalone rendered sessions were recorded before the package (contact and played pursuit/recovery); two separate restart recoveries then each played ten additional capture/retry cycles. Simulated native input is distinct from physical keyboard/gamepad/touch coverage.

Build identity (`cook-input-fingerprint-05.json`, covering dirty/untracked native source/config and required source-asset bytes):

| Identity | SHA-256 |
|---|---|
| Native source/config inputs at cook | `8cba8338b5821e82f211ef1ebcc035dc90878ce6f5f662522202804da41448fb` |
| Source asset inputs | `8a9c46328f79f1ab4122088134598efd8eac9af057f5ff283429e154fde9760d` |
| Packaged ELF | `dfef43d163997931901d1f028e63866e09cd8f85b97b828554efa1bd23d4bc63` |
| Cooked Ananse-Linux.ucas | `e99407c7b80cc2ebc4d7d80d6a9006fd5a15ae15d4ac47f81c22e6781cd1bb98` |

Container/launcher/debug-file hashes are in `package05-hashes.json`; source hashes are not cooked hashes or signatures. After verification a trailing blank line alone was removed from DefaultEngine.ini for `git diff --check`; `post-cook-formatting.json` retains before/after hashes. No configuration entries or compiled gameplay source changed.

Launch the played development pursuit with a separate manual checkpoint slot:

```bash
cd /home/favl/Downloads/ANANSE_Production_Starter
env -u PYTHONPATH -u LD_LIBRARY_PATH ./Builds/Linux/20261014T104432.399054Z/Ananse.sh \
  -ansimalloc -windowed -AnanseProductionPursuit -AnanseCheckpointSlot=AnansePursuitManual20261014
```

WASD/mouse/Space move/look/jump; E performs spatial interactions/retry; ESC skips the technical introduction; 1/2/3 are Kwaku's existing permitted powers; F5/F9 save/load the selected slot. The verified route is negotiation → archive → ledger → pursuit → Mirror-assisted escape → protected witnesses. Other route entry points reuse the mission but are not promoted to played acceptance here.

Launch the cooked controllable spider contact lab:

```bash
env -u PYTHONPATH -u LD_LIBRARY_PATH ./Builds/Linux/20261014T104432.399054Z/Ananse.sh \
  /Game/Characters/AnanseSpider/ContactLab_v006/L_AnanseContactLab \
  -ansimalloc -windowed -AnanseCheckpointSlot=AnanseContactManual20261014
```

F1/F2/F3/F4 select the four imported source clips; L toggles live contact/source-clip preview. Live contact overrides supporting-leg source poses and preserves arm gestures. This is a labelled engineering proxy at controlled walking speed, not final art, a complete artist Control Rig, wall/ceiling locomotion or network prediction.

Fresh evidence paths: `native-tests-33`, `pytest-final-profile.xml`, `package-mixed-05`, `package-contact-05`, `independent-package05-csv-audit.json`, `package05-contact-performance-audit.json`, `package05-hashes.json` and the final secret/source checks. Each runtime folder retains exact command, PID/exit, real screenshots, frame trace and contact CSV. Failed candidates and diagnostics remain separate and intact.

Remaining gates: detailed CPU-channel shutdown repair, final character/Osebo/environment art and animation/audio, all route/outcome coverage, epilogue, studio preview/publication integration, clean asset retrieval, Android acquisition/device qualification, authorised iOS path and real player services. No commit, push, merge, deployment, signing or licence acceptance occurred. The source branch remains dirty for review.

### Exact-package checkpoint restarts and command exits

`package-restart-05-01` and `package-restart-05-02` each started a **new packaged OS process** with slot `AnanseVerify_20261014T104642`, restored the documented schema-3 fields/recovery/knowledge/relative timers, then played ten capture/retry cycles, escaped and continued moving. Active durations were **121.58 seconds each**, normal lit, assertions passed, exit **0**. These are additional to the standalone-editor-game restart checks.

| Executed command category | Actual exit/result |
|---|---|
| Latest `scripts/unreal.py build` / `test` | 0 / 0; ten discovered/executed/succeeded |
| `pytest -q` with isolated environment | 0; 130 passed |
| Python compileall / Node syntax / final diff check | 0 / 0 / 0 |
| Development Linux build/cook/package/archive attempts 01–05 | Each 0; only candidate 05 passed all final runtime checks |
| Full-CPU packaged endurance/short diagnostics | 139 despite completed gameplay assertions; preserved FAILED |
| Owned GDB shutdown reproduction | GDB supervisor 0, stopped at real allocator assertion; not a game pass |
| No-trace / frame-only short diagnostic | 0 / 0; channel isolation, not substitute endurance |
| Candidate 05 mixed / cooked contact / two checkpoint restart runs | 0 / 0 / 0 / 0; 601.70 / 240.00 / 121.58 / 121.58 seconds |
| UnrealPak help / two config extraction attempts | 1 / 1 / 1; usage/path-separator diagnostics, no decompressed-config pass claimed |

Exact runtime argv/PID/exit records are indexed in the ignored `executed-runtime-command-index.json`; build/test/package arguments and exits are retained in separate supervisor/UAT logs. Historical supplied reports remain unchanged. Final tracked/index credential scan is zero; before/after configuration-format hashes and unchanged source-asset identity are retained in `final-source-and-secret-check-02.json`.
