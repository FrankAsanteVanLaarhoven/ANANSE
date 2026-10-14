# Verification ledger and release checklist

## Executed evidence

Use `evidence/BUILD_STATUS.json` for final counts and `evidence/pytest.xml`, `evidence/http-smoke.json`, `evidence/browser-smoke.json` and `evidence/unreal-doctor.json` for raw outcomes. These files relate to the packaged prototype, not an external repository or production deployment.

The Python suite exercises authenticated/unauthenticated reads, CRUD, strict payloads, role checks, stale revision rejection, dependencies, archive/restore/history/revert, exact-revision review, immutable prototype publication, blocked production publication, audit integrity, rule prerequisites/route completion, bounded resources and export/build helper checks. Live HTTP adds actual sockets, fresh-process persistence and static-resource responses. It does not execute browser DOM interactions or GPU code.

JavaScript syntax and Python compilation checks verify syntax, not UI correctness, rendering or business completeness. The browser test was blocked before a completed UI check. No screenshot exists from a successful browser run. The Unreal doctor correctly fails because UE_ROOT/engine are absent. Two C++ automation cases are supplied but have not been executed. There are no APK/AAB/IPA, frame-time traces, crash-free player samples or retention/share measurements.

## Reproduce

```bash
python -m pytest -q --junitxml=.local/verification/manual/pytest.xml
python scripts/http_smoke.py
node --check studio/static/app.js
python -m compileall -q studio scripts tests
python scripts/unreal.py doctor
```

The last command exits 2 with a clear blocker until an engine is installed. It is not expected to pass in the supplied container. The engine Python bootstrap can be syntax-compiled without Unreal; that does not verify its reflected editor APIs. Optional Playwright and native tests are explained in SETUP.md.

## Native acceptance matrix (pending)

Record engine Build.version, source hash, content hash, platform SDK, commands, package hash, device ID/OS, logs and any manual deviations for each run.

1. Editor target compiles without unresolved UHT/module/API errors; generate and open the intended map, not an unrelated default level.
2. Both authored native automation cases produce fresh success reports; add tests for insufficient resources, invalid claims, save incompatibility, interrupted traversal, blocked anchors and pause/resume.
3. Execute each social, negotiation and rooftop route to both supported outcomes without unintended bypasses, softlocks or permanent state corruption. Verify physical access rather than relying only on a boolean route flag.
4. Change Kwaku's palette/variant and allowed powers, review/publish/export, restart or recook, and observe the exact version in native gameplay. Verify missing asset references are rejected before a release cook, not merely logged.
5. Import one real licensed hero mesh with required morphs and AnimBlueprint. Demonstrate idle, movement, interaction and all ability animations on the target skeleton; prove collider dimensions stay correct under visual modifications.
6. Test touch multitouch/camera, controller, keyboard/mouse, safe areas, text scaling, subtitles, remapping, reduced motion, colour-independent signals and no softlock when focus changes. Current debug HUD is not accessible production UI.
7. Qualify physical phones: cold start, offline use, memory pressure, thermal soak, background/foreground, interruptions, storage full, app update, language changes and save migration/rejection. Inspect frame-time tails, not editor average FPS.
8. Resolve current target SDK, ABI, asset compression, 16 KB library/page-size support, release AAB/IPA signing and store declarations. A development APK is not a compliant release.

## Production authoring/backend gate (pending)

Do not deploy loopback development tokens as internet authentication. Add OIDC/MFA and per-user least privilege; require independently identified reviewers; enforce tenant/object access; limit upload sizes/quotas; quarantine and scan assets; use verified byte hashes; sign releases; establish revocation and rollback; externally anchor audit records; test backups/restores; load-test concurrency and queues; adopt dependency/action digest pinning and vulnerability review; monitor service health and incident response.

A “production approved” text field is insufficient. The actual production publish endpoint remains blocked until this validator and evidence flow are implemented. No tests in this starter prove compliance with a security standard, GDPR, accessibility standard, age rating or store contract.

## CI workflow status

`python-checks.yml` and `unreal-manual.yml` contain runnable command sequences but have not been installed or run on GitHub here. Self-hosted native CI is manual and intended for a protected main branch/environment only. Provisioning, credentials, runner labels and approvals are owner responsibilities. SHA-pin reviewed actions and produce platform-specific dependency artefact locks before production approval.

## Risks deliberately left open

Native C++/UHT and editor Python APIs may need correction against the exact installed engine. The laboratory and native mission rules are not shared or proven equivalent. Source includes simplified access conditions and perception; spatial exploits require playtesting. Runtime optional mesh loading is synchronous and not a scalable Asset Manager implementation. Animation references, full NPC appearance swapping, combat, chase AI, UMG, Sequencer, localization, audio, device-adaptive quality, cloud services and creator modding are not complete.

The correct response to a failed gate is a recorded issue and a narrowed claim, not a green status inferred from an adjacent test.
