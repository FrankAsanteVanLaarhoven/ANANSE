# CPU Lightmass startup diagnostic — 18 October 2026

Branch: `feature/local-milestone-verification`. Base HEAD: `ec7bf0bcf16634a13c12e92433e9731064890e80`. No commit or publication.

## Result

Baked lighting remains **BLOCKED**. The installed Unreal 5.8.3 CL58210709 worker crashes before an ANANSE map or lighting job loads. Standalone startup returned -11 with the game-thread task-tag assertion. This isolates the immediate failure from environment geometry. It does not establish that later job processing would work.

The debugger stopped at the assertion in `FTaskTagScope`, `ThreadingBase.cpp:100`, called by `FEngineLoop::PreInitPreStartupScreen`, `LaunchEngineLoop.cpp:2035`, then `LightmassMain`. Installed Launch source wraps the relevant static-initialisation scope with a Mac-only main-thread guard. No engine code, assertion or binary was changed. The installed distribution does not contain the worker entrypoint source needed for a normal local program rebuild. A supported replacement/rebuild must be qualified separately; bypassing the assertion is not a project fix.

## Project change

- `scripts/lightmass_preflight.py`: standalone bounded startup probe; saves command, worker/version/core hashes, raw output and process status in a fresh directory. Output paths are absolute. Existing evidence cannot be overwritten.
- `scripts/finish_route_environment.py`: rejects a failed probe before the first mesh/collision/map mutation.
- `tests/test_lightmass_preflight.py`: 11 checks covering the recorded assertion, nonzero exit, misleading exit-zero diagnostics, timeout, missing worker, evidence retention and blocked environment-script execution with a minimal editor test double.

A completed startup probe never qualifies a bake. Actual lightmap import, job completion and map verification remain required. The editor API's earlier true return is not accepted as lighting success.

## Validation

`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q`: **339 passed**, exit 0. No native/runtime code changed; no editor bake or cook was rerun.

Actual revised CLI probe: exit 1 as intended, report `blocked_thread_tag_assertion`, child status -11, `bake_qualified: false`. A debugger assertion stop is diagnostic evidence, not a successful worker run.

Evidence directory: `.local/verification/lightmass-diagnostic-20261018/`. Key records: `absolute-preflight/preflight.json`, `absolute-preflight/startup.log`, `worker-gdb.log`, `full-tests-final.log`, `preservation.json`. Earlier relative-path probe retained; the revised probe resolves its output directory before launch.

Worker SHA-256: `3b7d5ae9bb3b61f67a83db5abc1488248ad5dd31394341852e26fd17f56d250e`.

## Safety and remaining gates

Compared against frozen Pass-4 inputs: **1,586 native assets, 1,123 authored model files and 66 runtime/configuration files unchanged**. Review ZIP SHA-256 remains `c9d3ed34aeaff2bd7078f4a5e4431806b6444d539717c773dfd9a3fe873c37f2`.

No character, map, geometry, material, collision, navigation, lighting strategy, save, publication, package, engine or system configuration was deliberately modified. Existing rollback and failed evidence retained. New diagnostic outputs stay local, unstaged. No new Linux package was needed or produced.

Creative acceptance remains REVIEW_REQUIRED; mobile, broader navigation and long-session memory remain unqualified. No propagation, map expansion or new character work. Next decision remains visual review of the frozen candidate; an engine-worker repair is a separate technical dependency.
