# Installation, build and execution runbook

**Verification date: 13 October 2026.** Source IDs below resolve in SOURCES.md. Commands are supplied for execution on your own authorised machine. The Unreal commands have **not** run successfully in this delivery because no engine is installed. Existing robotics, ROS, CUDA and Android environments must not be modified blindly.

## 1. Choose a native host

Use the existing capable workstation before buying equipment. Native Linux can run Epic's Linux editor; a Windows editor in a browser/WSL container is not the chosen pipeline. Use Windows for a well-supported launcher/editor workflow when available. A compatible Mac with Xcode is required for the iOS route described here. The starter does not configure Windows-to-Mac remote signing.

For planning, reserve 150 GiB or more of working space for an installed-engine prototype and materially more for source builds, caches and art. This is a **planning reserve**, not an Epic guaranteed installation size. Check free disk, actual RAM/GPU and driver compatibility locally. Avoid changing the GPU driver used by robotics work simply to follow a generic installer.

## 2. Install the local studio

Install Python 3.13 through an official or organisation-approved method. In this repository:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
python -m pytest -q --junitxml=.local/verification/manual/pytest.xml
python scripts/http_smoke.py
python scripts/studio.py
```

On Windows use `py -3.13 -m venv .venv`, then `.\.venv\Scripts\python.exe -m pip install -r requirements.lock` and the same interpreter for the remaining commands. No system-wide execution-policy changes are necessary.

The studio binds to 127.0.0.1, port 8765 by default. `--port` changes the port. On first startup `.local/credentials.json` and `.local/studio.sqlite3` are created. Read credentials locally using a text editor, `cat .local/credentials.json` on Linux/macOS or `Get-Content .local\credentials.json` on Windows. Keep these values private. One token each exists for editor, reviewer and publisher; this is local development access control, not production SSO or independent person verification.

The launcher uses restrictive POSIX file permissions where available; on Windows put the repo in a private user directory with appropriate ACLs. Stop with Ctrl+C. Persistent data remains in `.local`. To recover a failed UI action, inspect the response/notice rather than reinitialising the database.

### Optional browser check

```bash
python -m pip install playwright
python -m playwright install chromium
python scripts/browser_smoke.py
```

This optional dependency is not part of the recorded core requirements lock. Pin its version and browser build in CI before relying on it. Do not bypass managed browser policies. The provided execution environment blocked navigation; no browser success report or screenshot was produced here.

## 3. Install Unreal Engine 5.8

UE 5.8 is the verified release family used in this starter [S1]. Do not infer an exact hotfix/changelist from the family number. After installation, `lock-engine` records Epic's actual `Engine/Build/Build.version`, and subsequent script commands reject a mismatch.

### Windows

Install Epic Games Launcher from Epic, sign in, review and accept the applicable licence yourself, then select Unreal Engine 5.8 and the Android platform components. Install the Visual Studio release supported by Epic's **current compatibility table**, the Game development with C++ workload, supported MSVC toolchain, Windows SDK and Unreal debugging/testing integration [S6]. Do not assume that any installed compiler or the newest preview compiler is compatible.

PowerShell example, adjusted to your actual installation:

```powershell
$env:UE_ROOT = 'C:\Program Files\Epic Games\UE_5.8'
.\.venv\Scripts\python.exe scripts\unreal.py doctor
.\.venv\Scripts\python.exe scripts\unreal.py lock-engine
```

### Linux

Use Epic's official Linux installed-engine archive, subject to account access and its licence [S5]. Unpack into a dedicated directory. Install the engine's bundled native toolchain rather than changing the workstation's global compiler. Epic's quickstart and requirements pages do not always present identical compiler-version text; the engine's supported bundled toolchain is the reference for this project.

```bash
export UE_ROOT="$HOME/Unreal/UE_5.8"
# Run only after unpacking the official engine into the actual directory above.
bash "$UE_ROOT/Engine/Build/BatchFiles/Linux/SetupToolchain.sh"
python scripts/unreal.py doctor
python scripts/unreal.py lock-engine
```

The downloaded engine must contain `Engine/Build/Build.version`. No Epic login, engine archive, GPU driver or Android dependency has been downloaded by this starter. Linux hosting of an editor is not proof that every mobile SDK/platform component is installed. Verify the chosen Android host path before adopting it for release builds; use the documented native Windows/macOS packaging route if the installed Linux distribution lacks the required platform tools.

### macOS and iOS

Install the engine through Epic's Mac-supported distribution. Use a Mac/OS combination meeting both Epic and Apple requirements. The checked Epic iOS matrix recommends **Xcode 26.1.1**; Apple lists **macOS 15.6 or later** for that Xcode version [S4, S7]. These are compatibility pins, not a claim that Xcode 26.1.1 is the newest Xcode. Apple has required Xcode 26+ and SDK 26+ for uploads since **28 April 2026** [S8]. The build SDK version and minimum supported iOS version are different decisions.

Set UE_ROOT to the actual engine directory. Review Xcode licences and select the correct Xcode in its normal supported setup. Verify `xcodebuild -version` and `xcode-select -p`. Do not embed Apple certificates/provisioning profiles in the repository. Bundle IDs, team selection, device provisioning, privacy declarations and App Store Connect roles must be configured by the authorised owner. The current package has no tested iOS minimum-deployment setting or signing configuration.

## 4. Author and publish content before native play

In the studio, connect as editor, select Kwaku and change a base/festival colour or permitted power set. Save. Connect as reviewer for an independent revision review. Connect as publisher and choose Publish prototype. Copy its publication ID.

```bash
python scripts/export_content.py --publication PUBLICATION_ID
```

This writes `Unreal/Content/Data/catalogue.json`. The exporter verifies the canonical payload hash, schema, identities and references. It does **not** fabricate meshes or bake animation. The runtime catalogue is loaded at startup and packaged as content; it does not connect to the studio. Re-export/restart the editor or rebuild/cook for a packaged game. An old package continues to use its old immutable catalogue.

## 5. Compile, bootstrap and test

```bash
python scripts/unreal.py build
python scripts/unreal.py bootstrap
python scripts/unreal.py test
python scripts/unreal.py open
```

The first command compiles AnanseEditor against the locked engine. The bootstrap runs Unreal's Python editor script and generates `/Game/Maps/L_Market_Greybox` and a simple material using engine primitives. It refuses to overwrite an existing generated map. To deliberately replace that generated map after preserving edits, use `python scripts/unreal.py bootstrap --replace-generated`.

The test command requires a **new** Unreal automation report and two successful ANANSE test cases. If `evidence/unreal-automation` already exists, archive it before rerunning. A missing report or failing case blocks verification even if the process returned zero.

The native integration is uncompiled in this delivery. Fix compiler/UHT/editor API errors on the pinned engine, record the exact changes, then rerun. Do not describe source generation as a successful build.

### Manual greybox walkthrough after a successful build

WASD/gamepad moves, mouse/right stick looks, Space jumps, E interacts, 1/2/3 invoke Web Step/Borrowed Voice/Trick Mirror. F5 saves, F9 loads, R restarts. Source includes default touch joysticks and debug touch buttons, but layout, multitouch, focus and orientation need physical-device testing.

Negotiate: inspect the altered edict -> talk to Aso's marker -> request archive access -> recover ledger -> protect or expose. Social route: inspect, learn the captain's call, use Borrowed Voice before expiry, request entry, recover ledger. Roof route: move within range and face the visible Web Anchor, use Web Step, use Trick Mirror and interact at the upper archive marker. These are **intended** walkthroughs, not observed successful native playthroughs.

The level uses labelled cubes, walls and stalls, not finished West African architecture or characters. The watcher is a simple local visibility check, not a complete crowd simulation or Osebo boss. Debug text is not finished dialogue/subtitle UI.

## 6. Android SDK and development packaging

Epic's checked UE 5.8 Android page lists Android Studio Koala 2024.1.2 Patch 1, NDK r27c, build-tools 35.0.1, OpenJDK 21.0.3 and recommends SDK 35 [S2]. **Google Play separately requires new mobile apps and updates to target API 36 from 31 August 2026** [S3]. Therefore an engine-default SDK check does not establish store compliance. This project's target SDK is 36, and compiler/Gradle/NDK/plugin compatibility must be proved, not assumed.

On a clean supported Windows host, Epic documents Turnkey installation through Platforms -> SDK Management -> Android -> Install SDK [S9]. CLI equivalent:

```powershell
& "$env:UE_ROOT\Engine\Build\BatchFiles\RunUAT.bat" Turnkey -Command=InstallSDK -platform=Android -SdkType=Full -BestAvailable -Unattended -nocompile -nocompileuat
```

This step can install significant dependencies and requires user-controlled licence acceptance. Do **not** delete existing Android/robotics SDKs or reset global environment variables on an established workstation. Use an isolated development account/directory and Epic's manual configuration route where existing installations conflict. Install API 36 through the official SDK manager, verify it is selected, and prove the actual generated build uses it. Turnkey's recommended default alone is insufficient.

```bash
python scripts/unreal.py verify-android
python scripts/unreal.py package --platform Android
```

The package helper creates a fresh, timestamped Development output directory and refuses missing map/catalogue inputs. Android is configured for ARM64, Vulkan and ASTC. The prototype uses a **development APK path**, not an asserted signed release AAB. Inspect actual outputs and generated target SDK with Android tools. Explicitly confirm compatible texture/device support, ABI libraries and 16 KB memory-page compatibility [S10].

Enable developer options/USB debugging only on your owned test phone; authorise its USB connection. Use the exact APK path produced by packaging:

```bash
adb devices
adb install -r /actual/path/to/Ananse-development.apk
adb logcat
```

No APK is provided with this delivery. A successful install is only the beginning: cold start, all three routes, touch input, pause/resume, audio interruption, local save/reload and a 20-minute thermal/frame-time test remain mandatory. The minimum Android SDK of 29 in the project is a proposed support floor, not a claim that every API 29 device can run it.

For store release, replace the placeholder package ID with a registered identifier, enable and test AAB output, protect release signing externally, recheck current policy/SDK/16 KB requirements, complete ratings/privacy, and use staged internal testing. These are owner-approved future gates, not automated submissions.

## 7. Desktop/iOS builds and CI

`python scripts/unreal.py package --platform Win64`, `--platform Linux`, or `--platform Mac` builds for a suitable installed native toolchain. Cross-compilation is not configured. On a provisioned Mac only, `--platform IOS` invokes the development packaging path; signing and successful device install are unverified.

The Python CI workflow runs only public source tests on a hosted runner. The native workflow is manual, main-branch-only and uses a labelled self-hosted engine runner behind an approval environment. Configure that runner, UE_ROOT, exact engine lock, content snapshot, Python environment and platform SDKs before running. Neither workflow has been executed remotely in this delivery. Pin third-party actions to reviewed commit SHAs and dependencies to verified artefacts before a production release.

## 8. Backups and rollback

Use `scripts/backup_studio.py`, which uses SQLite's backup API instead of copying a live WAL database incorrectly. Stop the studio before restoring a backup into `.local/studio.sqlite3`, preserve the previous DB/WAL files in a separate recovery directory and run integrity tests after restart. Never overwrite the only copy. Restoring content through the UI creates a new revision; published snapshots remain unchanged. Local game saves carry a schema and content hash and reject incompatible revisions. A migration policy, cloud conflict handling and trusted rewards are not implemented.

## Fresh evidence and this workstation

Keep supplied `evidence/` reports intact. HTTP/browser smoke scripts default to a new timestamped `.local/verification/` directory; select a separate empty directory for each script with `--out`. Native commands use a timestamped directory by default, or `--evidence-dir` for each fresh invocation, including bootstrap and automation reports. Existing reports cause a refusal rather than an overwrite. Pytest's XML path must likewise identify a fresh output.

On this Linux workstation, inherited `PYTHONPATH` includes unrelated ROS packages. Run project commands as `env -u PYTHONPATH .venv/bin/python ...` to preserve interpreter isolation without changing the workstation. Python 3.13.13 and the core lock were installed into the project venv. The optional browser check used Playwright 1.58.0 and existing `/usr/bin/google-chrome` (151.0.7922.173):

```bash
ANANSE_CHROMIUM_PATH=/usr/bin/google-chrome env -u PYTHONPATH .venv/bin/python scripts/browser_smoke.py
```

No browser download or policy change is needed for that verified combination. The optional package is separate from the core requirements. See `LOCAL_VERIFICATION_2026-10-14.md` for exact evidence, unchanged engine target and remaining native/device gates.
