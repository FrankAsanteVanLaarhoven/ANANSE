# Android acquisition boundary

No Android installation is authorised by the current episode task. No SDK package, IDE archive, licence acceptance or device configuration has been performed in this session.

The existing engine requests API 36, build-tools 36.0.0, NDK 27.2.12479018 (r27c) and CMake 3.22.1 in `Engine/Config/Android/Android_SDK.json`. The earlier diagnostic remains valid: Studio at the engine-selected path, a qualified SDK/NDK and JAVA_HOME are missing. Do not rerun the unchanged failed package command.

Proposed approval scope:

- Official Android Studio Koala 2024.1.2 Patch 1 Linux archive, with its bundled JBR verified against the engine's Java requirement, extracted without overwriting into `/home/favl/android-studio`. Obtain it from the [official archive](https://developer.android.com/studio/archive), not a mirror. Exact archive filename, published checksum, download size and JBR version must be checked before extraction. Do not substitute the current Studio release automatically.
- Dedicated `/home/favl/Android/Sdk`: `platforms;android-36`, `build-tools;36.0.0`, `ndk;27.2.12479018`, `cmake;3.22.1`, `cmdline-tools;19.0` and platform-tools. These six Linux packages total **989,727,090 compressed bytes** in the official repository metadata retrieved this session. Their individual URLs/sizes/checksums are retained in ignored `android-package-metadata.json`. This excludes Studio/JBR, Gradle dependencies, expanded files, build intermediates and packages. A checksum proves byte identity, not licence approval.
- Reserve **32 GiB** for tools and initial work, with a fresh space check before acquisition/build; this is a planning allowance, not a measured expanded total. The workstation currently has about 107 GiB available. No emulator/system images are proposed.
- Process-local SDK/NDK/JAVA_HOME/PATH only. Do not execute the unmodified engine SetupAndroid script, which writes shell startup settings. No global Java changes, existing SDK removals, driver/library changes or extra integrations.
- Frank must personally review/accept Google's Studio/SDK terms and any package licences. No account password, signing key or cookie should be shared. Studio sign-in/cloud integrations are not required for this local build task.
- For physical testing, a named owned ARM64 Android phone, USB debugging and device-side authorisation are needed. Installation, 16 KiB compatibility, controls and thermal measurements are separate gates after packaging.

[Epic's UE requirements](https://dev.epicgames.com/documentation/en-us/unreal-engine/android-development-requirements-for-unreal-engine) list Koala Patch 1, Java 21.0.3 and NDK r27c but recommend SDK 35/build-tools 35.0.1. The actual installed manifest requests 36/36.0.0; retain this discrepancy and qualify the generated Gradle/AGP build. Do not change project dependencies just to hide it. Google's [tool compatibility table](https://developer.android.com/studio/releases) also specifies API-dependent Studio/AGP minimums. If the pinned build proves incompatible, report that exact failure and propose a reviewed adjustment before changing versions.

The next dependent action is explicit acquisition approval and personal licence review, then archive qualification, non-installing Turnkey validation and a fresh Android package attempt. Linux development continues independently. iOS still requires an authorised Mac/Xcode/signing/device path.
