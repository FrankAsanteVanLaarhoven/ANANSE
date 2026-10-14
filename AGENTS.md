# ANANSE engineering contract

Build on the provided repository. Do not replace it with an unrelated web game or a fresh engine project.

## Authority and scope

Work on a feature branch. Read README and evidence/BUILD_STATUS.json before claiming existing functionality. Preserve user changes. Never merge, push, publish, create paid resources, accept third-party licences, alter GPU drivers, modify signing credentials or submit to stores without the user's explicit authorisation. Do not bypass browser/OS organisational restrictions.

## Boundaries

C++ owns native mechanics, persistence and runtime validation. Blueprint/UMG/Sequencer assets will own authored missions, presentation and tuning after native integration is proven. No executable content from metadata. No hidden model calls, paid APIs, telemetry endpoints or user-data uploads. Do not embed studio tokens in the game.

Keep single-player local prototype rules distinct from server-authoritative future rewards. Native GAS currently dispatches powers; it does not yet supply production AttributeSets, GameplayEffects or network prediction. The Python rules lab is not the canonical native simulation. Add shared conformance fixtures before claiming parity.

## Assets and culture

No copied franchise characters, scraped commercial asset packs, unlicensed music or unconsented voice cloning. Traditional characters are inspiration, not an exclusive ownership claim over folklore. Keep source/community/rights review explicit. Planned assets must not be relabelled as available without real files and validation.

## Required change report

State changed files, tests actually run, test counts, failures, untested platforms, remaining blockers and rollback. Do not count authored tests as executed. Do not count HTTP service checks as browser UI checks or native frame-rate evidence. An engine exit code alone does not prove tests passed. A package must come from a fresh output directory and must be installed and exercised before device functionality is claimed.

## Gates

Run Python tests and JavaScript syntax checks for local changes. Compile Unreal and execute its automation for C++ changes on an authorised engine host. Check device frame times for rendering/input changes. Use exact engine Build.version pinning. Never auto-download unknown models or install plugins to silence errors. Add hashes, wheel locks and action commit pins before production supply-chain approval.

## First implementation order

1. Reproduce local tests and browser UI in an unrestricted, authorised local environment.
2. Install the exact supported UE family, lock Build.version, compile and fix source integration.
3. Publish/export a catalogue, generate the greybox, run two native tests and record a real play-through of each route.
4. Prove edit -> publish -> export -> cook -> visible native appearance change and power removal.
5. Prove Android package installation, controls and sustained device performance.
6. Only then add artist-produced assets, AnimBlueprints, UMG, StateTree crowd behaviour and Sequencer story beats.
