# Native Linux recovery — 2026-10-14

Branch `feature/local-milestone-verification`; unchanged commit `4f0c817161bacf1b63935a1443f30629aaa9b52e`. Source changes remain uncommitted. Original archive, source snapshot, supplied evidence, publications, and pre-existing saves are preserved. New runtime evidence and artifacts are ignored local files.

## Result and qualification

A fresh Development Linux package was built and exercised outside the editor. Native input-driven verification activated Web Step, Borrowed Voice and Trick Mirror, completed the negotiation route to `witnesses-protected`, saved with F5 to a dedicated slot, exited, and loaded with F9 in a new packaged process. Both package processes rendered for at least 60 seconds and exited 0. Tests injected native controller input events through implemented bindings; physical keyboard/controller/touch hardware was not exercised. The character is a cube/sphere greybox placeholder, with unfinished lighting/environment and no production animation.

UE root `/home/favl/Unreal/UE_5.8.3-58210709`; production UE 5.8.3, changelist 58210709, compatible changelist 55116800. Bundled clang 20.1.8 and .NET SDK 10.0.203. Host Ubuntu 22.04.5, glibc 2.35, NVIDIA RTX 4080 SUPER / driver 580.178.04. Actual runtime backend Vulkan. No system, driver, ROS, CUDA, Python, SDK, or startup-file changes.

## Recovered exception and independent failures

The interrupted Python attempt failed with this complete recorded traceback:

```
Traceback (most recent call last):
  File "/home/favl/Downloads/ANANSE_Production_Starter/.local/verification/native-install-20261014T014419.097770Z/native_play.py", line 52, in tick
    catalogue=unreal.SubsystemBlueprintLibrary.get_game_instance_subsystem(world,unreal.AnanseCatalogue)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: module 'unreal' has no attribute 'SubsystemBlueprintLibrary'
```

`SubsystemBlueprintLibrary` is Blueprint-internal in the installed engine and not exposed as that Python class. Native catalogue/readiness accessors were added; gameplay assertions now execute in Development C++, with Python restricted to process/editor orchestration.

The command-line Python executor additionally auto-queues `QUIT_EDITOR` after script return unless `unreal.EditorPythonScripting.set_keep_python_script_alive(True)` is set. Installed source confirms this lifecycle; the launch script now uses the actual `ScriptName` API.

A separate genuine gameplay fault was found: `AAnansePlayer::Restart()` unintentionally overrode virtual `APawn::Restart()`, repeatedly opening the map during possession and leaving zero usable mappings. Renaming the R-key handler `RestartRun()` restores normal pawn lifecycle and input.

The original bootstrap saved assets but crashed; that attempt remains failed. A minimal direct Python `quit_editor()` also reproduced a main-thread SIGSEGV under gdb: `_int_free → __libc_free → ubidi_close_64 → TextBiDi::Internal::FICUTextBiDi::~FICUTextBiDi → FTextLayout::~FTextLayout → FSlateTextLayout`. The gdb command's exit 0 is not an application pass. Default editor allocator logs report Mimalloc; rendered PIE assertions can pass but editor shutdown still exits -11. A delayed teardown did not resolve it. Process-local `-ansimalloc` logs ANSI and produced three consecutive successful PIE play/stop/close cycles. This is a verified workaround, not proof of the ultimate engine allocator/ICU corruption cause. Game/package runs pass with their default allocator. Normal non-PIE queued editor exits and asset-validation edits also exited 0.

The external three-second agent-hook timeout has no project-local diagnostic evidence establishing its cause or a relationship to either engine failure. It remains an independent external event.

## Content and persistence

Kwaku revision 2 publication hash `b2dfd93d29e7798e7aa3ab3c3f73c385259f9e5f7982d8b5874e226a849a7f88` remains immutable. Native `native-r2-game-05` loaded that exact hash, compared the body material against sRGB `#48766B` converted to linear `(0.064803,0.181164,0.147027,1)` with tolerance 0.0001, and proved absent Mirror through simulated keyboard, gamepad, and touch handler paths; 60 seconds of movement and exit 0. The screenshot was captured from the real rendered framebuffer.

A NEW revision 3 restored only the three intended powers, retaining revision 2's appearance. It was reviewed and published through the existing authenticated local studio API: publication `eea37c87d2134aadab8823524aeb360d`, hash `4e37e276855d51bcd73d95ab9ac25db4d43b0822a039e23e27a4278dd7a2019f`. Export used `scripts/export_content.py --publication eea37c87d2134aadab8823524aeb360d`. Native runs checked the live subsystem hash and ability grants. Local role tokens are not independently identified reviewers. Hair/outfit/accessory metadata is not demonstrated native asset rendering; no finished character, rig or animations are supplied.

Native baseline `native-baseline-game-05` completed spatial interactions and saved slot `AnanseVerify_20261014T034649`. Fresh process `native-reload-game-01` compared every `FAnanseMissionState` field, position (0.05 cm), rotation (0.01 degree), relative voice/mirror timers and all saved cooldowns (0.03 seconds). Timers were already zero at these completed-route checkpoints; this does not establish non-zero timer restoration or persistence of unrecorded runtime objects/ability activation. Packaged baseline/reload used dedicated slot `AnanseVerify_20261014T035036`. No existing default save was overwritten.

## Consecutive rendered PIE cycles

| Attempt | Active play seconds | Process exit | Assertions/stop |
|---|---:|---:|---|
| native-reload-pie-ansi-01 | 60.006 | 0 | passed |
| native-baseline-pie-ansi-02 | 60.003 | 0 | passed |
| native-reload-pie-ansi-03 | 60.004 | 0 | passed |

Each uses a new editor process, actual PIE world, `AnanseGameMode`, possessed `AnansePlayer`, Vulkan and the RTX 4080 SUPER. None uses NullRHI or offscreen rendering. The preceding standalone baseline, standalone restart, package baseline and package restart also passed independently. Screenshots/command records are in each named attempt directory.

## Source changes

- `Unreal/Source/Ananse.Target.cs` and `AnanseEditor.Target.cs`: V7 target settings matching this engine; no shared-environment warning bypass.
- `Ananse.Build.cs`: RHI/ApplicationCore runtime dependencies and editor-only UnrealEd dependency.
- `AnansePlayer.h/.cpp`: correct restart-handler name, read-only catalogue/world/readiness accessors, input diagnostics, Development verifier hooks and dedicated test save-slot routing. Normal F5/F9 slot remains `AnansePrototype`.
- `AnanseMission.h/.cpp`: bounded validated optional checkpoint slot and read-only timer accessors; normal mission/persistence rules retained.
- `AnanseRuntimeVerification.h/.cpp`: opt-in native frame-based Development acceptance scenarios, real binding delivery checks, collision-aware movement/interaction, catalogue/material/ability checks, checkpoint comparison, framebuffer capture and orderly lifecycle supervision. Shipping hooks are inert.
- `scripts/start_native_pie.py`, `native_runtime_smoke.py`: editor orchestration and bounded owned-PID supervisor with fresh logs, exact engine pin, native assertions and minimum play duration. `native_play_editor.py`/`native_play_smoke.py` forward legacy entry points; superseded implementations are preserved locally.
- `scripts/build_greybox.py`: deferred executor shutdown and persisted `NoCollision` profile only for the decorative anchor marker. Existing generated map was edited in place after a backup; roof/obstacle collision and sweeps remain active. Native trace proved the marker blocked sample 16 at Z=285. The original runtime collision-enable edit did not persist through profile reload; its failed attempt is retained.
- `scripts/unreal.py`: absolute evidence paths; corrected SoftQuit syntax, UTF-8 BOM decoding, required test identities, rejection of empty/stale/malformed/incomplete/inconsistent reports.
- `tests/test_build_tools.py`: meaningful negative report-validation coverage.
- `toolchain.lock.json`: exact Build.version pin. `.gitignore`: generated map/material and cook file-open-order logs excluded.

## Commands and results

All native scenario argv, working directories, PIDs, environment removals, actual process returns, forced-termination status and duration are in each `launch.json`/`command.json`. All earlier failed attempts remain present; report existence never converts a failed process to a pass. The old interrupted attempt returned 124 after termination; fresh failed PIE processes return -11. Headless automation is recorded separately from rendered scenarios.

- Editor builds: initial V5 settings failure was corrected to V7; subsequent builds succeeded. Recovery build 04 failed linking `IPlatformInputDeviceMapper::Get`; adding its owning ApplicationCore dependency fixed build 05. Final native-verifier build 14 exited 0. Logs are retained per build directory.
- `env -u PYTHONPATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q --junitxml=.../pytest-final.xml`: exit 0, 66 passed. Initial unsanitized plugin auto-discovery failed on inherited ROS modules; no ROS/system packages were changed.
- Python compileall and `node --check studio/static/app.js`: exit 0.
- `scripts/unreal.py test --evidence-dir .../native-tests-final`: exit 0; 2 discovered, 2 executed, 2 passed: `Ananse.Mission.Negotiation`, `Ananse.Mission.PowerBudget`. NullRHI provides no visual evidence. Relative evidence paths caused an earlier wrapper failure despite engine execution; normalization and a fresh rerun fixed it.
- `scripts/unreal.py package --platform Linux --evidence-dir .../package-linux-01`: wrapper/UAT exit 0; fresh build/cook/stage/pak/IoStore/archive completed. Disk check before packaging showed 144 GiB available.
- Packaged baseline and reload launchers: exit 0; native processes exit 0, assertions passed, 60 seconds each.
- `UnrealPak -List`: exit 0, expected catalogue listed. `UnrealPak -Extract`: exit 1 due the installed Linux implementation constructing a literal backslash filename; no engine code was changed. Inspection confirmed uncompressed packaged project INI contains no AuthenticationToken key, no credential/database paths are staged, and known studio token bytes are absent. This limited inspection is not an independent security audit.

Unchanged historical 11 HTTP / 10 browser checks were not rerun as filler; the required new edit/review/publication/export was performed through the live studio API and native integration was tested. No browser-runner or physical input evidence is newly claimed.

## Artifacts and launch

Package: `/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261014T034836.346853Z`. Executable: `/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261014T034836.346853Z/Ananse/Binaries/Linux/Ananse` (SHA-256 `43aad4677e6d6a74e6e0e4484a531857eec790b62486e6fa6cb0fac1decef00d`). All build-file hashes, excluding runtime Saved files, are in `/home/favl/Downloads/ANANSE_Production_Starter/.local/verification/native-recovery-20261014T023300.503733Z/package-artifacts.json`. Native screenshots and hashes are listed in each run report. Generated map/material, evidence, DB/credentials, environments and Build outputs remain local ignored artifacts. Editor-generated Android authentication settings are privately preserved and removed from tracked config; packaging strips editor settings, and its INI inspection found no AuthenticationToken.

Play the verified package:

```bash
env -u PYTHONPATH -u LD_LIBRARY_PATH /home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261014T034836.346853Z/Ananse.sh -windowed -ResX=1280 -ResY=720
```

Controls: WASD/stick movement, mouse/right stick look, E interaction, 1/2/3 powers, F5/F9 local save/load, R restart. Physical hardware operation and manual window-close interaction were not independently exercised.

Editor workaround qualified by the native PIE cycles:

```bash
env -u PYTHONPATH -u LD_LIBRARY_PATH /home/favl/Unreal/UE_5.8.3-58210709/Engine/Binaries/Linux/UnrealEditor /home/favl/Downloads/ANANSE_Production_Starter/Unreal/Ananse.uproject -ansimalloc
```

Repeat the exact verified native editor scenario with `scripts/native_runtime_smoke.py --engine-root ... --mode baseline --context pie --allocator ansi --out <NEW_DIRECTORY>`. It runs real gameplay and closes the editor; do not point it at evidence already present.

## Remaining boundaries

Linux: native greybox milestone passed with documented ANSI editor workaround; default Mimalloc PIE/editor shutdown still requires engine-level investigation. Manual/hardware input, sustained performance/device frame times, other routes/endings, finished assets, faithful character editing, production GAS/UI/backend and commercial approval are not established. No broad production-ready claim.

Android: BLOCKED until a separately qualified SDK/NDK and identified connected physical device exist. iOS: NOT TESTED; a Mac/Xcode/signing qualification is required. Neither platform blocks this verified Linux build. No commit, push, merge, public release, deployment, licence acceptance or driver/system changes were performed.
