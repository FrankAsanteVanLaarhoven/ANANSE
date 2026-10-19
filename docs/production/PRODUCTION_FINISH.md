# ANANSE — production finish work order

**Prepared 14 October 2026.** Basis: remote commit `ec7bf0bcf16634a13c12e92433e9731064890e80`, inspected through the connected GitHub service, plus the supplied 14 October workstation handoff. This is an additive production work order and authored content change set. It is not a completed game, imported art pack, audio recording or cloud deployment.

## Release decision

Finish **one 15–20 minute production-quality Market of Stolen Names mission**, with a short Story Forest sanctuary epilogue, before expanding into further kingdoms. Keep Linux as the engineering/reference build and qualify Android and iOS as separate shipping targets. A Linux-only result does not close mobile release gates. This scope is a recommended first shippable episode/candidate, not a relabelling of the complete multi-kingdom game.

Keep the current Kwaku campaign identity and Ananse character distinct. The supplied spider design becomes an actual production character with FOUR grasping arms and FOUR walking legs. Default narrative staging uses Ananse in the epilogue and a controllable Character Lab; changing the mission protagonist needs a recorded product decision before final casting and animation. Do not stall work on unrelated systems while that decision is recorded.

Freeze new infrastructure experiments and additional starter kits. Reuse the existing studio, UAnanseMission, native player, powers, input, catalogue export, save logic and Unreal project. Extend rather than duplicate them.

## Audited baseline and gaps

The linked repository's head was `ec7bf0b`, with default branch `feature/local-milestone-verification`. Its Local-studio-contracts Actions run 38516234662 completed successfully. Its checked-in README still claims the engine has not compiled; the attached handoff reports a newer local README that remains uncommitted. Resolve this documentation lag without claiming local results were rerun remotely.

The supplied handoff reports 66 Python tests, two native tests, three 60-second rendered PIE sessions, a Linux package, one route, and save/load over process restart. It also reports that the character proxy is structurally validated but not imported, the environment source ZIP is absent locally, Blender qualification is pending, Android is blocked, iOS is untested, and `-ansimalloc` remains a process-local workaround rather than a diagnosed fix.

Two repository-level findings need correction:

1. `.github/workflows/unreal-manual.yml` has `if: github.ref == 'refs/heads/main'`, while the inspected repository currently has only the feature branch. A present workflow file is not an executed native pipeline. Choose a protected, reviewed build-ref policy; do not simply remove the condition and expose a workstation to arbitrary public-PR code.
2. `.gitignore` deliberately excludes the character kit, generated prototype assets and raw evidence. `.gitattributes` already contains Unreal/media LFS patterns. Preserve historical exclusions, but create an approved production asset location or access-controlled artifact store with immutable hashes. A fresh checkout must hydrate actual assets, not just LFS pointers or text paths on one developer's disk.

Remote source findings:
- `README.md`, `.gitignore`, `.gitattributes`, `.github/workflows/unreal-manual.yml` at the inspected SHA.
- `Unreal/Source/Ananse/AnanseMission.cpp`: current route/outcome rules and schema-1 saves; saves require identical content hashes. Production content updates therefore require an explicit save migration/preservation policy, not silent overwrite.
- `Unreal/Source/Ananse/AnanseRuntimeVerification.cpp`: development-only simulated input checks, candidate hash and render checks. Keep their scope separate from physical controller/touch coverage and human playtests.

## Six concurrent workstreams

### A. Character and environment art

The engineering proxy is an import/rig fixture, not final visual acceptance. Required production work: approved front/side/rear anatomy, sculpt, deformable topology, UVs, materials, texture baking, four-arm/four-leg rig, facial/eye setup, clothing, LODs, sockets and collision. Preserve eight-appendage identity across all views. Agree hand digit count explicitly rather than trusting inconsistent generated views.

Build the final spider's face, abdomen, markings, cloth and silhouette against the supplied reference. Compare fixed-camera native screenshots at the same scale/lighting intent. The art director and cultural reviewer must assess them; numerical topology checks cannot approve resemblance or representation.

Start with one finished market corner and one sanctuary clearing. Use approved modular architecture, restrained mobile foliage, baked lighting, clean lightmap UVs, ordinary mesh LODs, material sharing and simple collision. Do not classify decorative water as playable navigation or luminous thread as collision.

Track native source assets via reviewed Git LFS or private, hashed artifact storage. Keep `.blend`, exported geometry, textures, material instances, rigs and animation sources reproducible. Validate third-party redistribution rights before putting commercial source assets into the public repository. Hashes prove byte identity, not ownership or authenticity.

**Completion:** the cooked asset registry references approved production files for every required hero-space asset, and a second clean build can materialize and cook them. Placeholders may remain in excluded test maps, never hidden inside the shipping mission.

### B. Animation and controller

Qualify the supplied Blender 4.5+ adapter against an official compatible user-local Blender installation. A blocked download is an acquisition issue, not a reason to abandon all production work. Do not substitute an unverified binary or silently upgrade the engine. A direct Interchange GLB route is an alternative only after proving skeletal import, skin weights, rest pose and every clip with the installed engine.

Use a custom spider Control Rig. Upper and lower arms need independent controls and layered gestures; supporting legs need stable joint bends, ground targets and stance locks. Define when locks release for Web Step, jumps, capture and interruption. Root movement/collision belongs to the gameplay controller; the IK graph must not teleport the authoritative pawn to repair a visual foot error. Avoid simultaneous ragdoll/IK authority fights.

The task file lists 24 production animation categories. Replace the four proxy clips with finished locomotion, transitions, web traversal, investigation, dialogue, distraction and reactions. Validate animation notifies, cancel windows, material/cloth response, facial motion and camera collision. Keep wall/ceiling locomotion outside this first release unless it is explicitly approved as core scope.

**Completion:** playable Character Lab plus mission integration, full limb-isolation test, no unsupported biped retargeting, correct floor/ramp contacts and qualified animation LODs. Proposed contact budgets are p95 stance drift ≤2 cm and p95 penetration ≤0.5 cm on named test surfaces; these are targets, not measured outcomes.

### C. Cinematic mission and gameplay

Use `production/market/mission_spec.json` as an authored work specification, not executable metadata. Extend the existing native state machine, using Blueprint/Sequencer for presentation. Create route-specific interactions, local guard beliefs, suspicion warnings, purposeful patrols, an Osebo pursuit, failure/retry and both consequences.

The mission is arrival → inspection → social/negotiated/rooftop entry → ledger → ACTIVE pursuit → decision → visible consequence → sanctuary epilogue. The chase must be played, not replaced by a movie or completion flag.

`dialogue.en.json` supplies 44 original draft lines and performance notes. `shots.json` supplies 18 shots across the opening, discovery, pursuit introduction, two endings and epilogue. They need narrative, cultural, casting, pronunciation and accessibility review before final recording. They are not claims about historical or traditional wording. Do not manufacture unverified Twi translations.

Sequencer owns presentation, not the canonical outcome. Finish, skip, cancellation, level unload and app interruption must all restore camera, input, possession, movement, UI and audio ducking. Apply durable gameplay events once. Test skip at every semantic boundary; do not award the same consequence twice. Preserve scene state independently of audio length and localization duration.

Add explicit save migration: schema/content/mission version, map, character identity, current beat, route/outcome, evidence, witness states, bridge state, relative timers and completed event IDs. Retain old saves on incompatibility and show a recovery choice. Never reward cloud-synced client saves as trusted multiplayer achievements.

**Completion:** all three routes and both endings complete through real gameplay, with capture/retry, cutscene skip, app interruption and restart checkpoints. No debug buttons, prototype HUD text or dev command dependencies in the shipping path.

### D. Sound, music and accessible presentation

Commission or use rights-cleared final recordings. `audio_cues.json` supplies 24 non-voice cue briefs; dialogue has stable recording/localization IDs. The mix needs original/adapted-with-permission music, market/river/forest ambience, earthen/wood/stone foot contacts, cloth, ledger handling, magic, UI and appropriately cast voices.

Use Unreal's audio engine, MetaSounds where useful, submixes, spatial attenuation and explicit concurrency limits; do not introduce another middleware dependency by default. Source recording target: 48 kHz/24-bit, with platform-specific compression chosen after listening/profile tests. This target is not a claim that recordings exist.

Expose master, dialogue, music and effects controls. Provide speaker-labelled subtitles, scalable text and captions for navigation-critical sounds. Test phone speakers, headphones, mono/downmix where applicable, muted music, audio interruption and Bluetooth reconnection. Consent and rights records must cover the actual performers, recordings and compositions; do not clone a person's voice without permission.

**Completion:** every critical cue resolves to a reviewed waveform/MetaSound in the cooked build; no silence where dialogue is required, no clipped mixes, no progression dependency on waveform duration, and no unlicensed source recordings.

### E. Mobile and build/release engineering

Move physical Android packaging earlier in parallel with art. Qualify the SDK/NDK/JDK against the installed engine, then inspect the built result rather than only configuration files. As checked on 14 October 2026, Google Play requires target API 36 for new phone apps/updates. Epic's UE 5.8 requirements still recommend SDK 35; the mismatch is a qualification task, not permission to ship below Play policy. Check ARM64 libraries and 16 KB compatibility across every native dependency.

Produce a development APK first, then a signed candidate AAB with authorised signing. Test installation and gameplay using APKs actually derived from that AAB; do not confuse the bundle with an directly installable APK. Keep signing secrets outside the repository and ordinary test jobs.

Qualify an authorised Mac/Xcode path for iOS. Apple currently requires Xcode 26+ and SDK 26+ for upload. Test the signed result on a named iPhone, not only an editor/simulator. Account access and store submission remain separate decisions.

For both mobile targets test touch reachability, controller mapping, safe areas, captions, suspend/resume, offline start, storage pressure and thermal behaviour. Start at 30 fps with the approved mobile-forward/baked-lighting baseline. Desktop screenshots and Mobile Preview are not device performance evidence.

Native builds need clean asset hydration, isolated reviewed runners, exact source/content/toolchain hashes and fresh output paths. Do not attach public-PR execution to the robotics workstation. Use protected manual build inputs or an isolated private build-control pipeline, with candidate SHA recorded; never assume deleting the `main` check is a security design.

**Completion:** signed testable mobile candidates, representative physical-device reports, and a clean-checkout reproduction. Store approval is a further external gate and is not implied by signing or packaging.

### F. Player services and authoring operations

Keep the campaign offline-capable. Player services provide opt-in identity, recoverable cloud saves, controlled configuration/content delivery and consent-aware operational telemetry. Avoid multiplayer, chat, UGC and a shared economy in this release.

Preferred candidate: PlayFab behind an internal provider adapter, but do not blindly choose the newest SDK. Microsoft's currently published v2 Unified Unreal platform list does not list Android/iOS and directs unsupported platforms to v1; v1 and v2 cannot coexist. Qualify a mobile-supported client path or a narrow authenticated REST adapter on all selected targets before adoption. Do not add multiplayer OSS merely to store single-player saves.

Use versioned JSON/checkpoint envelopes and explicit optimistic-concurrency/conflict handling. Offline progress is valid locally but never authoritative for purchases. A hash is not an authenticity signature; preserve conflicting saves and provide user resolution. Test token expiry, account linking, cross-account authorization, malformed/oversized input, duplicate retries, network loss and deletion.

Authoring remains separate from player APIs: extend the existing studio, then migrate approved production services to per-person identity/MFA, PostgreSQL, private object storage, scanning/validation jobs, revision-specific approvals, immutable signed manifests and externally retained audit evidence. Never expose the current loopback token/SQLite service as the production studio. Prepare infrastructure changes locally; creating paid resources, selecting data residency, changing DNS or uploading user data needs explicit approval.

**Completion:** actual staging API calls and isolation/conflict/restore tests, observed Unreal-client integration and an approved deployment/rollback runbook. Mock tests are useful but do not establish a cloud deployment.

## Delivery cadence and responsibilities

Use one accountable integrator. Gameplay, technical-art/animation, environment-art, audio/narrative and build/services work need named ownership; one person can hold multiple roles, but that increases time. No fixed commercial delivery date is warranted until asset staffing, devices and service access are confirmed.

Within the next two working days, aim to have the existing spider genuinely imported/possessed, one candidate Android package attempt with full diagnostics, and the opening sequence bound to the real mission with a tested skip path. Missing Blender, art approvals or device access block only their dependent work. After any blocked prerequisite, record it once and continue an independent executable task.

At the first weekly production review, demonstrate one finished market corner, the spider's approved anatomy/rig direction, the full mission playable with temporary presentation clearly marked, and measured Android baseline. Subsequent weekly reviews replace temporary content, not add kingdoms. A candidate date is set after this throughput is observed.

Human decisions to consolidate in one request: protagonist identity, official Blender acquisition approval if still pending, final-art/audio commissioning budget and rights, two Android devices and one iPhone/Mac path, cloud provider/region/cost ceiling and signing-account access. Do not stop executable local tasks waiting for all decisions.

## Six release KPIs (proposed targets, not present results)

1. **Mission correctness:** all 3 routes × 2 outcomes, every cutscene skip boundary and restart checkpoint pass before RC designation.
2. **Asset completion:** 100% of required shipping assets have materialized bytes, production art acceptance, source/rights records and cook evidence; zero proxy substitutions in the shipping mission.
3. **Mobile performance:** three 20-minute runs on each of two named Android devices and one iPhone; p95 frame time ≤33.4 ms and ≤1% of frames above 50 ms at the agreed preset, with memory/thermal traces retained.
4. **Stability:** ≥99.5% crash-free foreground sessions across ≥1,000 closed-test sessions before public release, reported by device with uncertainty. Three 60-second sessions are only smoke tests.
5. **Persistence/services:** zero lost or cross-account save writes across at least 100 defined restart/offline/conflict/retry scenarios before RC; staging rollback and restore exercised. This test target is not a statistical guarantee of zero future failure.
6. **Comprehension:** at least 24 of 30 first-time testers explain the goal and the cost of their chosen outcome without facilitator explanation before content lock. Track voluntary replay/sharing separately as product experiments, not claims of guaranteed virality.

## Research/evidence record

**Hypothesis:** production art/performance and consequence-readable gameplay can turn the verified native mechanics into a replayable mobile mission. **Design:** separate code/contract checks, engine integration, device qualification, cultural/art review and blinded-to-route novice playtests. **Initial evidence:** source and CI inspection plus reported local native acceptance; no production gameplay study. **Failures:** missing assets, pending Blender acquisition, stale README, branch-gated CI and unresolved allocator issue. **Refinement:** parallel workstreams, explicit content retrieval, candidate-bound evidence and scope lock. **Further experiments:** foot contact, route/skip/save matrix, mobile thermal sessions and staging conflict tests. **Conclusion:** executable foundation is established; production content, mobile and services remain real work, not a documentation relabel.

**SWOT:** strength—working native/authoring baseline; weakness—no final art/audio or mobile qualification; opportunity—story manipulation and a distinctive eight-appendage character; threats—content throughput, inconsistent reference anatomy, device budgets, save migrations and asset rights. Responses: tightly bounded mission, named ownership, early devices, reviewed manifests and explicit migration tests.

## Current external references (checked 14 October 2026)

- Epic Sequencer: https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-sequencer-movie-tool-overview
- Epic sequence restoration: https://dev.epicgames.com/documentation/unreal-engine/what-happens-when-my-cinematic-ends-in-unreal-engine
- Epic audio engine: https://dev.epicgames.com/documentation/unreal-engine/audio-engine-overview-in-unreal-engine
- Epic MetaSounds: https://dev.epicgames.com/documentation/unreal-engine/metasounds-the-next-generation-sound-sources-in-unreal-engine
- Epic Android toolchain: https://dev.epicgames.com/documentation/en-us/unreal-engine/android-development-requirements-for-unreal-engine
- Google Play target API: https://developer.android.com/google/play/requirements/target-sdk
- Android native 16 KB: https://developer.android.com/guide/practices/page-sizes
- Apple submission SDKs: https://developer.apple.com/news/upcoming-requirements/?id=02032026a
- Blender 4.5 LTS: https://www.blender.org/download/releases/4-5/
- PlayFab v2 platform caveat: https://learn.microsoft.com/en-us/xbox/playfab/sdks/unified-unreal/overview
- PlayFab optimistic-concurrency data operation: https://learn.microsoft.com/en-us/rest/api/playfab/data/object/set-objects?view=playfab-rest
- GitHub self-hosted runner access/security: https://docs.github.com/actions/hosting-your-own-runners/managing-self-hosted-runners/managing-access-to-self-hosted-runners-using-groups

Official/vendor documentation supports technical capability and policy claims. The authored dialogue, proposed thresholds, scope and schedule are project design decisions, not peer-reviewed empirical findings.
