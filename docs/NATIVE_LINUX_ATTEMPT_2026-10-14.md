# Native Linux attempt — 14 October 2026

Branch: `feature/local-milestone-verification`; commit: none. Existing uncommitted work preserved. No engine/gameplay source changed this session; this handoff is the only new authored project file.

## Measured result

Engine installation and archive searches found no identified UE 5.8 installation or authorised archive. UE_ROOT is unset. Epic's Linux acquisition page redirects to an account-required page: https://www.unrealengine.com/en-US/linux. The owner must sign in, personally review licence terms and download the production Linux archive, or identify its alternate local path. No credentials, cookies, licence acceptance or unofficial binaries were used. No archive was extracted and no toolchain setup script was executed. Archive size, provenance, integrity and expanded-space qualification remain pending because there is no candidate archive.

Project family remains 5.8. Installed engine point version, changelist and matching compiler/toolchain are **not detected**. No Build.version pin was fabricated. Linux compilation does not depend on Android qualification.

Host read-only checks: Ubuntu 22.04.5, kernel 6.8.0-138-generic, Python 3.13.13, Git 2.34.1, GCC 11.4.0, glibc 2.35, OpenJDK 11.0.32.1, Node 22.23.2, Chrome 151.0.7922.173. RTX 4080 SUPER, NVIDIA driver 580.178.04; NVIDIA Vulkan ICD present, vulkaninfo unavailable. Graphical session is X11 on DISPLAY :0. This inventory is not a qualified Unreal rendering/toolchain result. Disk had 276.5 GiB free before snapshot.

## Preservation and fresh evidence

Evidence directory: `/home/favl/Downloads/ANANSE_Production_Starter/.local/verification/native-linux-20261014T003210.055419Z`.

- `source-before-native.zip`: 60 source/config/documentation files, 257924 source bytes; ZIP integrity checked. Excludes Git internals, credentials, databases, environments, prior runtime evidence and generated build directories.
- Snapshot SHA-256: `98592729e6316f582294665bb06580e92b8e9c5e4ec95ad9c91c0742b8269c56`.
- `source-manifest.json`: per-file sizes/hashes, disk check and snapshot hash.
- `protected-manifest.json`: hashes of supplied evidence, the previous verification run and the native input catalogue; verified unchanged after checks.
- `preserved-content.json`: read-only database/catalogue/publication comparison.
- `host.json`, `commands.json`, `BUILD_STATUS.json`, `source-review.json`: fresh inventory, exact commands/exits, status and bounded source findings.
- `pytest.xml`: **62 passed**, zero failed/errors/skipped; pytest exit 0.
- `http/http-smoke.json`: **11 checks passed**; script exit 0.
- `browser/browser-smoke.json`: **10 checks passed**; script exit 0. Installed Chrome with Playwright 1.58.0; no policy change/browser download.
- `browser/studio-overview.png` and `browser/story-laboratory.png`: genuinely captured web studio/laboratory screenshots, **not native game screenshots**.
- `browser/catalogue.json`: isolated browser-test publication export; not the persistent native test input.

Wrapper `--help`, JavaScript syntax, Python compileall and pip dependency checks exited 0. All Python verification subprocesses cleared inherited PYTHONPATH process-locally. Build/bootstrap/test/package commands were not repeated against the known missing engine.

## Native acceptance still open

Two test names found in source: `Ananse.Mission.Negotiation` and `Ananse.Mission.PowerBudget`. Runtime discovery is BLOCKED; **0 native tests executed, 0 passed, 0 failed**. Those source tests exercise mission rules, not catalogue consumption or process-restart save/load. No content publication was used by a native test.

Kwaku revision 2 remains unchanged and matches its immutable publication and native catalogue: colour `#48766B`, powers `web-step` and `borrowed-voice`; content hash `b2dfd93d29e7798e7aa3ab3c3f73c385259f9e5f7982d8b5874e226a849a7f88`. Trick Mirror restoration is deferred until this revision has been tested natively. No live review/publication/database mutation occurred.

Source inspection found catalogue-based GAS grants and common keyboard/controller/touch activation methods, primitive material palette application, and authored checkpoint fields. It does not prove runtime restrictions, visual changes or persistence. Supported persistence fields and unsupported/runtime-only fields are enumerated in `source-review.json`. Unknown requested appearance variants can use defaults; this needs explicit native verification/correction. Automation report validation currently counts successful entries without checking the exact authored identities; inspect actual test identities before accepting an engine-host report.

No editor build, map, cooked Linux package or native screenshot was produced. There is **no verified native launch command** to offer. The existing local studio remains available at http://127.0.0.1:8765.

Linux: BLOCKED by engine acquisition. Android: BLOCKED by SDK/NDK/adb and qualified device; does not block Linux. iOS: NOT TESTED, no Mac/Xcode host. No system Python/Java, shell startup, drivers, CUDA, ROS, Isaac Sim, other projects or remotes changed. All new runtime artifacts remain ignored and unstaged; no commit/push/merge/deployment/release.

Next required input is the authorised production UE 5.8 Linux archive or exact installed-engine path. Its identity/provenance/expanded-space checks must precede extraction under /home/favl/Unreal. Enterprise-execution and task-observer guided preservation/verification; skill-retrieval tools were unavailable.
