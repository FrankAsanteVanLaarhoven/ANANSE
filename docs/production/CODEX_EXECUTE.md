# Execute ANANSE production finish

This is an implementation task inside the existing project, not a request for a new blueprint, fresh starter, web game or additional proxy kit.

Repository: FrankAsanteVanLaarhoven/ANANSE
Local project: /home/favl/Downloads/ANANSE_Production_Starter
Existing engine: /home/favl/Unreal/UE_5.8.3-58210709
Last inspected remote SHA: ec7bf0bcf16634a13c12e92433e9731064890e80

Inspect actual state first; do not reset to that SHA. Preserve uncommitted README changes, native fixes, original kits, snapshots, databases and published content. Read applicable AGENTS.md and the latest handoff. Update the obsolete first-milestone execution order to allow this production phase in parallel, while retaining safety, licensing and evidence rules.

## 1. Apply additive production content when available

The optional ANANSE_Production_Finish.patch adds only new files under production/, docs/production/, scripts/ and tests/. Inspect it and run git apply --check before applying. It does not modify existing source or import assets. Never force apply over a conflicting local file.

Read docs/production/PRODUCTION_FINISH.md, production/market/* and the release checker. Run its tests. The supplied example evidence intentionally fails the release gate. Do not fill it with invented passing results.

If the optional patch has not been downloaded, continue production from this task and existing sources. Do not stop the entire project to request another attachment. Reconcile any locally implemented equivalents when the patch becomes available.

## 2. Define the production deliverable

One finished 15–20 minute Market of Stolen Names mission, three infiltration routes, active Osebo pursuit, two consequences and a short forest sanctuary epilogue. Linux is the reference build; Android and iOS require independent candidates and physical-device qualification. Offline campaign operation and optional player services are required. No open world, co-op, economy, UGC, voice chat or new agent framework.

Keep Kwaku and Ananse distinct. The spider must retain four grasping arms plus four supporting legs. Default preserves current campaign identity and adds the spider as an actual production character/controllable Character Lab and epilogue presence. Record any approved protagonist change before final casting; do not silently overwrite Kwaku or old publications.

## 3. Execute independent workstreams, not serial prerequisite deadlocks

A missing Blender archive, phone, cloud account or artist approval blocks only tasks depending on it. Record the exact blocker once. Continue an independent implementation task with a real output. Do not repeatedly scan the workstation or rerun unchanged tests to fill a session.

Start with the available character kit and the current mission systems. Request normal approval for an official, checksum-verified user-local Blender installation if needed; do not bypass a download restriction or third-party licence. Qualify skeletal import, four clips and custom skeleton; then implement Control Rig/Animation Blueprint, leg contacts, arm/finger independence, controller and camera. Identify final mesh/texture/facial/cloth/LOD work separately from the proxy.

Implement the mission's real runtime beat coordination and Sequencer bindings now, in parallel with art acquisition. Extend UAnanseMission instead of creating a competing state machine. Add active patrol/pursuit, route-specific social checks, reliable captures/retries and both outcomes. Use gameplay-owned idempotent events for cutscene finish/skip/cancel; restore input/camera/possession/audio on every exit path. Extend versioned saves with tested migration/preservation.

Use the supplied authored dialogue and shot list as drafts for review and recording. Create stable localization/voice IDs and subtitle bindings, native audio buses, cue routing, concurrency and accessible settings. Do not label empty SoundWave paths, synthetic test tones, unapproved voice cloning or timing placeholders as finished audio.

Integrate environment production sources when present. Finish one market corner and one forest clearing first using the approved mobile-forward/baked-lighting baseline. Implement collision, navigation and bridge state separately from visuals. Extend the existing studio's environment/asset review and publication workflows; no second admin app. Keep final files retrievable via approved LFS/private immutable storage.

Qualify Android immediately in parallel: current engine-compatible toolchain, ARM64, current target API, 16 KB native-library checks, fresh APK and AAB-derived install tests. Use named physical devices for touch/thermal performance. Prepare the iOS path on an authorised Mac; do not claim a Linux cook produces a qualified iOS release.

Build a narrow player-service adapter with offline fallback, optional auth, cloud-save concurrency and signed configuration. Qualify a mobile-supported provider path; PlayFab v2 Unified's currently documented platform list omits Android/iOS, so do not blindly add it. Keep staff authoring auth/database/storage separate from player services. Local mocks are not real staging. Prepare infrastructure without paid deployment until approved account, region and cost limits are known.

## 4. Fix reproducibility and CI without exposing the workstation

The audited native workflow runs only when github.ref is refs/heads/main, but the inspected repository's default/only branch was feature/local-milestone-verification. Inspect current refs and fix the release-build policy deliberately. Do not blindly remove the guard, create/merge main or execute untrusted public PRs on a privileged research machine.

.gitattributes already includes LFS patterns. Preserve ignored original kits and raw evidence, but establish a production asset path/artifact manifest that a clean checkout can hydrate and cook. Verify actual bytes instead of LFS pointer text. Preserve licences for commercial assets; never place restricted sources in the public repository.

Separate CI categories: contract tests, native compile/test, real rendered run, mobile/device tests, staging service tests and protected candidate signing. Bind evidence to source SHA, content hash, toolchain version and artifact hash. Use fresh output directories and retain unsuccessful attempts.

## 5. Production acceptance

No required shipping placeholder, missing material, missing critical audio, test HUD or development completion shortcut. All three routes/two outcomes and each cutscene skip/cancel path must work. Checkpoints survive process restart without duplicate consequences. Ananse's eight appendages articulate correctly and navigate the actual map.

Test named mobile devices in three 20-minute runs each; target p95 frame time <=33.4 ms and <=1% of frames above 50 ms. Retain thermal/memory traces. Real staging must pass authorization, stale-save conflict, offline/retry and rollback tests. Test actual packaged builds, not only PIE. Keep the allocator workaround explicit; a clean exit under -ansimalloc is not proof of root-cause repair.

The next two-working-day target is actual imported/possessed spider, real Android package attempt with diagnostics, and the first mission sequence with a tested skip/control-return path. Report partial completion honestly and continue independent executable work.

## 6. Authority and reporting

Normal local source development is in scope. Do not change drivers, CUDA, ROS, Isaac Sim, system Python, shell startup files or unrelated projects. Do not buy assets, upload private references, accept licences, create billable cloud resources, change signing credentials, publish, submit to stores, merge or push without explicit approval. Preserve authorship and legal notices; do not falsify attribution.

Batch genuinely required human decisions once: character identity, installation approval, final-art/audio budget, devices/Mac, cloud account/region/cost cap and signing access. Do not ask for credentials in chat or let unresolved decisions stop unrelated local code.

At handoff show: actual changes; latest playable build/launch command; source/content/toolchain/artifact hashes; exact tests run; screenshots/videos only if genuinely captured; missing final assets with owner; Android/iOS/cloud outcomes separately; remaining blocker and next executable task. Never report the current mandate or a JSON status edit as completed production.

Begin implementation in this session. Do not stop at a plan.
