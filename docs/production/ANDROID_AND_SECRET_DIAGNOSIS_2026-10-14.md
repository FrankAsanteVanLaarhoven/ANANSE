# Android prerequisite and tracked-token diagnosis — 14 October 2026

This checkpoint diagnoses existing failed attempts. It does not rerun the blocked package, install tools, modify configuration, rotate tokens or rewrite history.

## First failures and cause

Complete prior logs were read and filtered into fresh ignored evidence at `.local/verification/android-secret-diagnosis-20261014T065321.669451Z/`. Prior logs remain untouched.

- Turnkey's first prerequisite failure is `Android Studio is not installed correctly.` (`verify-sdk.log:15`). Its report is `Status=Invalid`, `Platform_InvalidHostPrerequisites`, empty current SDK and required NDK r27c. Turnkey's exit 0 reflects command completion, **not** successful qualification.
- UnrealBuildTool's first Android registration failure is `Unable to find valid SDK(s) for Android` (`UBA-AnanseEditor-Linux-Development.txt:20`), followed by Android `buildable: False`. The actionable fatal diagnostic is `Sdk: not found. Required version r27c.` at lines 48–51. UAT consequently exits 6. This precedes compilation of the requested Android target; it is not a gameplay/compiler/rendering failure.

The installed `AndroidPlatform.Automation.cs` checks `/home/favl/android-studio/bin/studio.sh` on Linux. That file is absent. Its `UpdateHostPrerequisites(..., bVerifyOnly=true)` reports the Studio error and returns false; no attempted download/install happened. It selects `/home/favl/Android/Sdk` when `ANDROID_HOME` is unset. That directory and the expected NDK directory are absent. The installed `AndroidPlatformSDK.cs` requires an NDK LLVM toolchain and a valid `JAVA_HOME/release`; a PATH Java executable alone does not satisfy the check.

## Required versus detected

| Component | Installed-engine requirement / checked source | Detected |
|---|---|---|
| Engine | UE 5.8.3, CL 58210709 | Installed; retained |
| Android Studio | Linux detection `/home/favl/android-studio/bin/studio.sh` | Absent |
| SDK platform | `Engine/Config/Android/Android_SDK.json`: android-36 | No configured/materialized SDK |
| Build tools | 36.0.0 | No configured/materialized SDK |
| NDK | 27.2.12479018, r27c; allowed r27c–r29 | Required version not found |
| CMake | 3.22.1 | No qualified Android SDK CMake |
| Java | UE source rejects missing JAVA_HOME/release and major versions below 17; documented UE recommendation OpenJDK 21.0.3 | JAVA_HOME unset; PATH `/usr/bin/java` resolves to `/usr/lib/jvm/java-11-openjdk-amd64/bin/java`, OpenJDK 11.0.32.1 |
| Device tools | platform-tools/adb for physical qualification | adb/sdkmanager/avdmanager absent from PATH |

`ANDROID_HOME`, `ANDROID_SDK_ROOT`, `NDKROOT` and `JAVA_HOME` are all unset in the qualification environment. The checked project DefaultEngine.ini contains no Android SDK settings section or SDK/NDK/Java path assignments. Engine defaults contain the section but no explicit path assignments. This is a bounded inspection, not a claim that no unrelated tool installation exists anywhere on disk.

The installed Linux engine **does contain Android platform support**: six installed-platform records cover arm64/x64 DebugGame, Development and Shipping, their required target receipts exist, and nine Android target/binary files exist. `UnrealGame-arm64.so` is a genuine ARM aarch64 64-bit ELF. These engine files do not constitute an ANANSE APK, proof of 16 KB compatibility across project dependencies, or a passed cook/device test. Reinstalling Unreal is not indicated by this evidence.

[Official UE requirements](https://dev.epicgames.com/documentation/en-us/unreal-engine/android-development-requirements-for-unreal-engine) currently list Koala 2024.1.2 Patch 1, Java 21.0.3, SDK35/build-tools35.0.1 and NDKr27c. The installed 5.8.3 SDK manifest explicitly requests API36/build-tools36.0.0. Record and qualify that discrepancy; do not silently downgrade the local engine's matching package inputs. Store eligibility remains separate from toolchain qualification.

## Exact prerequisite approval

Authorise a checksum-verified official user-local Android Studio Linux installation at `/home/favl/android-studio` (without overwriting an existing installation), with its matching JBR/JDK, and a dedicated SDK at `/home/favl/Android/Sdk` containing platform-tools, command-line tools, `platforms;android-36`, `build-tools;36.0.0`, `ndk;27.2.12479018` and `cmake;3.22.1`. Select the official version against the engine requirement and actual package checks; confirm archive provenance/version before extraction. The user must personally review and accept required licences. Do not ask for signing keys or account passwords.

Use process-local `ANDROID_HOME`, `NDKROOT`, `JAVA_HOME` and PATH for the build. The bundled `SetupAndroid.sh` writes `.bashrc` and invokes package installation; **do not execute it unchanged** under this project's no-startup-change boundary. The installed Studio/SDK can instead be explicitly qualified without modifying shell startup or system Java. [Official Android installation instructions](https://developer.android.com/studio/install) describe the Linux download/extraction route and licence gate.

After approval/materialization, the next dependent commands are a fresh non-installing Turnkey VerifySdk, a fresh Development Android ASTC BuildCookRun, then actual package/native-library checks and a named connected device. No package attempt or physical-device result is claimed at this diagnostic checkpoint. iOS requires its independent authorised Mac/Xcode/signing/device path.

## Editor-generated authentication setting

A value-safe scan examined **only Git-tracked working files and index bytes** for nonempty `AuthenticationToken` assignments. Both returned zero assignments; specifically, `Unreal/Config/DefaultEngine.ini` has zero AuthenticationToken keys in working copy and index. No credential value was printed, retained in the diagnostic report or copied into documentation. Existing private diagnostic copies were not scanned as repository attribution/exposure evidence.

No present tracked/index exposure was found, so no unrelated history-wide search, token rotation or history rewrite was performed. This is a narrow AndroidFileServer-token check, not a general secrets audit. Unreal may regenerate the editor setting on subsequent sessions; recheck tracked config before any future commit and preserve/remove only that generated block, without discarding unrelated configuration work. No configuration was edited while native tests were running.
