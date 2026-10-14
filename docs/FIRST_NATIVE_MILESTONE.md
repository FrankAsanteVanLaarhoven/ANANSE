# First mergeable native milestone

**Owner:** native gameplay engineer, reviewed by technical art/QA and project owner.
**Deliverable:** one recording and evidence bundle proving a real native edit-to-play cycle; not a screenshot of source code.

Start from this repository. Read AGENTS.md and the verification ledger. Use a feature branch. Install UE through an authorised official process, record Build.version, compile AnanseEditor and correct integration errors against that engine. Do not substitute a new blank Third Person template and report it as this implementation.

Publish a prototype catalogue in the existing studio; export it. Generate the greybox map without overwriting artist changes. Run both native tests with fresh reports, then manually complete the social, negotiation and rooftop routes and both endings. Record collision/line-of-sight/access exploits and fix them before calling the route complete.

Change Kwaku's base palette and remove one permitted power, publish a new revision, export and recook. Show the changed appearance and blocked power in the new build, with the package and manifest hashes. Demonstrate F5/F9 persistence on the same content hash and intentional rejection of an incompatible save. Restore prior content as a new revision and prove it can be rebuilt.

On one named owned Android device, install the fresh Development APK and record startup, touch controls, an entire mission and a thermal/frame-time trace. Resolve API 36/toolchain incompatibility rather than merely editing an INI value. Do not submit to a store or create paid services.

Required report: source commit/diff, exact engine/SDK/NDK, commands, new test reports, generated map/asset inventory, package SHA-256, device/OS/settings, successful and failed route observations, remaining bugs, measured frame times and rollback steps. No acceptance based only on a successful compilation, editor frame rate or Python tests.
