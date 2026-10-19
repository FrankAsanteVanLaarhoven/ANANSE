# Reviewed native builds and Android qualification

## Native build policy

The local workflow candidate replaces the obsolete main-only guard with manual dispatch on `feature/local-milestone-verification`. It accepts a lowercase, exact 40-character candidate SHA. A GitHub-hosted policy job checks that the object is a commit reachable from the reviewed development ref before scheduling the native job. It does not execute candidate source during validation. The native job checks out that exact SHA, records it, and retains `native-build-approval`, read-only permissions, no PR trigger, pinned checkout/upload actions, no persisted checkout credentials and serialized builds.

This is a local workflow change, not proof of configured repository protection or an executed remote native pipeline. Scheduling is additionally disabled unless the repository variable `ANANSE_NATIVE_RUNNER_APPROVED` is exactly `true`. Set it only after provisioning the isolated runner and protections. Before enabling a runner, an administrator must protect this branch and configure the named environment with required independent reviewers and prevention of self-review. The reviewer must inspect the exact SHA and its build scripts before approving. Reachability alone is not approval. Use an isolated disposable build runner without robotics access, signing keys, studio tokens, production accounts or sensitive host mounts; do not attach the research workstation to arbitrary public-PR builds.

Dependencies install into a job-local virtual environment. `requirements.lock` pins versions but lacks wheel hashes; production supply-chain qualification remains open. No claim of complete reproducibility is made: approved production assets and reviewed catalogue bytes still need clean-checkout hydration, rights approval and immutable artifact manifests. Existing LFS patterns are retained; original ignored kits are not newly published. The workflow produces compile/headless automation evidence only, not rendered, mobile, signing or production readiness evidence.

The installed engine pin is still exact. The known editor shutdown workaround must remain process-local `-ansimalloc`; it is not a root-cause repair. Fresh evidence must retain actual native exits and test counts.

## Android attempt — 14 October 2026

Evidence: `.local/verification/android-production-20261014T055622.823763Z/` (ignored local files).

Detected installed UE 5.8.3, changelist 58210709, and OpenJDK 11.0.32.1. `adb`, `sdkmanager`, and `avdmanager` are absent from PATH. `ANDROID_HOME`, `ANDROID_SDK_ROOT`, `NDKROOT` and `JAVA_HOME` are unset. No SDK was found at the specifically checked `/home/favl/Android/Sdk`, `/home/favl/Android`, or `/opt/android-sdk`; no broad workstation scan or SDK installation occurred.

The actual installed `Engine/Config/Android/Android_SDK.json` requests `platforms=android-36`, `build-tools=36.0.0`, `cmake=3.22.1`, and NDK `27.2.12479018` (r27c, allowed r27c–r29). These installed-engine values supersede the pasted SDK35 recommendation for this machine; they do not prove store eligibility or package compatibility.

1. `RunUAT.sh Turnkey -command=VerifySdk -platform=Android -unattended -utf8output -ReportFilename=... -LogFilename=...` exited **0**, but its actual report says **Status=Invalid**, with `Platform_InvalidHostPrerequisites` and `Android Studio is not installed correctly.` The zero process exit is not an Android qualification pass. No update/install flags were used.
2. A fresh `BuildCookRun` requested Android ASTC Development build/cook/stage/pak/IoStore/package/archive of the existing market. UAT exited **6**: `Platform Android is not a valid platform to build. SDK validation failed`. Full command/log are preserved in `package-attempt/`. The fresh archive directory `Builds/Android/20261014T055711.298497Z` is empty; there is **no APK or AAB**.

Android ARM64/library alignment, 16 KB page-size compatibility, touch controls, install, sustained frame time, thermal/memory and AAB-derived install tests are **BLOCKED**, not passed. No identifiable physical-device test was possible without the toolchain/adb. iOS remains **NOT TESTED**, requiring an authorised Mac/Xcode/signing/device path. No system Java, existing SDK, shell startup, drivers or unrelated project was changed.

Next dependent action: approve/provide an official user-local Android Studio and engine-matching SDK/NDK/JDK installation, personally handle any required licence acceptance, then rerun Turnkey and the package attempt into fresh evidence. No signing or store upload is authorised by this qualification. Continue independent mission/native implementation meanwhile.

Pinned action release provenance: [checkout v4.2.2](https://github.com/actions/checkout/releases/tag/v4.2.2) and [upload-artifact v4.6.2](https://github.com/actions/upload-artifact/releases/tag/v4.6.2), checked against their official release pages.
