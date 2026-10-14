# Local milestone verification — 14 October 2026

Branch: `feature/local-milestone-verification`. Commit: none; the delivered workspace had no Git repository. Git was initialised only in this project, with repository-local identity Frank Asante Van Laarhoven / frankleroyvan@gmail.com. All source remains uncommitted. No enclosing repository or remote was changed.

The existing studio is running at http://127.0.0.1:8765, process 1922160. Credentials remain private in `.local/credentials.json` (mode 0600); read the editor value locally and connect. The server keeps the existing metadata authoring and deterministic story laboratory. It is not a native playable game. The connected preview tool was unavailable; actual browser automation used the installed Chrome successfully.

## Changes and rationale

- `scripts/http_smoke.py`: selectable fresh evidence directory, timestamped default, refusal to overwrite existing reports.
- `scripts/browser_smoke.py`: same evidence protection; UI review of Kwaku's exact revision; palette change and removal of Trick Mirror; CLI export verification of those exact metadata values.
- `scripts/unreal.py`: fresh evidence directory propagated through doctor, logs, bootstrap and automation; refuses existing doctor/bootstrap reports. Engine family and exact-pin requirements remain unchanged.
- `scripts/build_greybox.py`: respects the native helper's evidence-directory environment. This editor-only change is syntax-checked but not engine-executed.
- `tests/test_build_tools.py`: two regression cases verify report preservation and refusal before HTTP server startup or engine execution.
- `README.md`, `docs/SETUP.md`, `docs/TEST_AND_RELEASE_GATES.md`: direct reproduction to private fresh evidence rather than overwrite historical reports; document this workstation and optional browser combination.
- This handoff records results and blockers. No native C++ or seed content was changed.

## Detected host

Ubuntu 22.04.5 LTS; Linux 6.8.0-138-generic x86_64. Python 3.13.13, Git 2.34.1, Node 22.23.2, Chrome 151.0.7922.173, OpenJDK 11.0.32.1, GCC 11.4.0. Approximately 277 GiB available when inspected; exact disk bytes, tool paths and dependency versions are in `.local/verification/20261014T0027/host.json`.

The venv is project-local and excludes system site packages. Inherited PYTHONPATH was removed only in project subprocesses, so unrelated ROS paths do not participate. Core requirements installed successfully; `pip check` exited 0. Optional Playwright 1.58.0, greenlet 3.5.6 and pyee 13.0.1 were installed only in this venv. No system Python, GPU, ROS, engine or Android installation was modified.

UE_ROOT is unset. No `Engine/Build/Build.version` was found in the bounded depth-six search under /home/favl, /opt, /usr/local and /mnt. No version is inferred. Project EngineAssociation remains 5.8. adb, sdkmanager, ndk-build, clang, clang++, dotnet and xcodebuild were unavailable on PATH. Android environment variables and usual SDK locations were absent. USB inventory identified no Android device; device availability cannot be qualified without adb.

## Commands and results

All Python checks used `env -u PYTHONPATH .venv/bin/python`. Exact argument arrays and per-command exit statuses, including intermediate failures, are preserved in `.local/verification/20261014T0027/commands.json`.

| Executed check | Final exit | Result |
|---|---:|---|
| `-m pytest -q --junitxml=.local/verification/20261014T0027/pytest-verified.xml` | 0 | 62 passed; 0 failures, errors or skipped |
| `scripts/http_smoke.py --out .local/verification/20261014T0027/http-verified` | 0 | 11 live HTTP checks, including fresh-process persistence |
| `scripts/browser_smoke.py --out .local/verification/20261014T0027/browser-verified` with ANANSE_CHROMIUM_PATH=/usr/bin/google-chrome | 0 | 10 browser workflow checks; no JavaScript exceptions |
| `node --check studio/static/app.js` | 0 | JavaScript syntax |
| `-m compileall -q studio scripts tests` | 0 | Python syntax, including editor bootstrap; no reflected-API validation |
| `scripts/unreal.py doctor --evidence-dir .../native-final` | 2 | BLOCKED: engine absent |
| `scripts/unreal.py build`, `package`, `test`, each with a separate evidence directory | 2 each | BLOCKED before any engine invocation; 0 native tests executed |
| `scripts/export_content.py --publication <recorded ID>` to live evidence and default native path | 0 each | Exact reviewed revision verified in both identical catalogues |

The original 60-test suite passed before adding regression coverage. An intermediate editing mistake introduced an unterminated inline Python string in the smoke scripts; syntax and smoke checks caught it. It was corrected and all affected checks rerun successfully. Failed command logs remain preserved, not relabelled as success.

Browser workflow exercised read, Kwaku modification, reload persistence, character creation/variant addition, archive/restore, reviewer approval, publisher publication, exported metadata, production blockers and the negotiated laboratory route. HTTP/API evidence is kept separate from browser evidence. Local role tokens do not establish independently identified human review.

## Acceptance and artifacts

The persistent studio has Kwaku revision 2 with base cloth colour `#48766B` and `trick-mirror` removed from permitted powers. Review and prototype publication succeeded. Content hash: `b2dfd93d29e7798e7aa3ab3c3f73c385259f9e5f7982d8b5874e226a849a7f88`.

Artifact paths relative to `/home/favl/Downloads/ANANSE_Production_Starter`:

- `.local/verification/20261014T0027/`: fresh command ledger, host inventory, historical hashes and all intermediate/final logs.
- `pytest-verified.xml`, `http-verified/http-smoke.json`, `browser-verified/browser-smoke.json` under that directory: final reports.
- `browser-verified/studio-overview.png` and `browser-verified/story-laboratory.png`: successful UI captures; abstract stand-ins, not finished art.
- `browser-verified/catalogue.json`: isolated browser-test export, distinct from persistent studio publication.
- `live/authoring-acceptance.json` and `live/catalogue.json`: persistent studio publication, export commands, hash and lab-session identifier.
- `Unreal/Content/Data/catalogue.json`: identical persistent publication ready as a native build input; no prior catalogue existed.
- `.local/studio.sqlite3` and `.local/credentials.json`: private live state and tokens, ignored by Git.

No engine map, native binary, cooked package, APK, AAB or IPA was generated. The laboratory route completed to `witnesses-protected` and its persisted session was read back; actual native mission/save/reload remains BLOCKED. Browser and HTTP checks cannot pass that native acceptance step.

All historical `evidence/` files retain their recorded SHA-256 values and file inventory. New runtime evidence, credentials, database, venv and catalogue are ignored and unstaged. No remote push, merge, deployment, external release, licence acceptance or asset purchase occurred.

## Next action and rollback

Owner must provide an authorised compatible UE 5.8 installation (or explicitly approve a version port), accept its licence personally, and set UE_ROOT to the actual root. On that host, record and review Build.version with `lock-engine`, compile AnanseEditor, generate the greybox without overwriting art, run native automation, cook and verify the recorded Kwaku palette/power change in gameplay, complete a native route and demonstrate F5/F9 persistence. Source inspection found no reason to claim compilation before this gate.

Android additionally needs an owner-qualified SDK/NDK/JDK for the actual engine, Turnkey verification, and an owned connected/authorised device. Existing OpenJDK 11 is not the project's documented Android JDK 21 requirement. Do not modify existing SDKs or accept licences automatically. Android acceptance stays BLOCKED.

To reverse the local Kwaku experiment, use revision history to revert revision 1 into a NEW revision, review/publish it, and re-export. Preserve prior publications and evidence. Stop only this studio process before restoring a database backup. No seed or prior evidence requires restoration.

Skill-retrieval search capabilities were unavailable. Repository contracts and direct source/test evidence guided implementation; task-observer informed evidence isolation. No research study, art completion or production claim is made.
