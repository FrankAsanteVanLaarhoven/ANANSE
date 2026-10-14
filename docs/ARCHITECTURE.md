# Architecture and integration contracts

## The implemented boundary

```text
Local authenticated browser
  -> FastAPI validation + role check + revision precondition
  -> SQLite transaction: entity + immutable revision + audit event
  -> Independent review of a specific revision
  -> Publisher creates immutable PROTOTYPE snapshot
  -> export_content.py verifies canonical SHA-256 and references
  -> Unreal Content/Data/catalogue.json
  -> native compile/cook/startup (NOT yet verified)
  -> catalogue subsystem -> player/interaction presentation and allowed power IDs
```

The browser/API/rule laboratory have an actual implementation. Native consumption is authored source, not an observed working runtime. An asset path in a catalogue is **not** proof that a UAsset exists, is licensed, is cookable or is compatible with a skeleton.

## Modules and data ownership

`studio/models.py` owns strict declarative contracts. `store.py` owns transactional persistence, revision history, dependency validation, review and publication. `app.py` owns HTTP and local role boundaries. `lab.py` owns an intentionally small deterministic mission-rule model. `Unreal/Source/Ananse` contains a single comprehensible runtime module with separate catalogue, player, mission, powers and world files. Split additional editor/runtime/plugins only when a genuine dependency boundary exists.

Stable record identity is distinct from a revision and an appearance variant. A revision contains editable metadata; an immutable publication fixes the versions used by a build. Relationships use stable IDs, never display names. Archiving preserves identity and history and is blocked while active references exist. Restoring or reverting creates a new revision, rather than rewriting old history.

The catalogue carries names, palette/visual scale, morph names, mesh references, power IDs, mission and faction metadata. Native source currently consumes **only a subset**: names, selected appearance and permitted powers, with optional compatible mesh loading. It does not interpret arbitrary mission records as executable level scripting, retarget an animation asset, update all NPC behaviour from faction descriptions or support every edited creature representation. These are explicit future work items.

## API surface

All `/api/*` endpoints require `Authorization: Bearer <local role token>`; public `/health` exposes no credentials. Static assets are public on loopback. `If-Match` is mandatory for mutations of existing entities and stale revisions return 412. CRUD data are fully validated replacement documents, even though the HTTP update verb is PATCH.

| Route | Methods/role | Meaning |
|---|---|---|
| `/api/whoami` | GET / authenticated | Current local role |
| `/api/{kind}` | GET / authenticated; POST / editor | Paginated listing; create |
| `/api/{kind}/{id}` | GET / authenticated; PATCH, DELETE / editor | Read; update; archive |
| `.../restore` | POST / editor + revision | Restore as new revision |
| `.../history` | GET / authenticated | Immutable snapshots |
| `.../revert` | POST / editor + revision | Restore historical data into a new revision |
| `.../review` | POST / reviewer | Approve/reject a specific revision |
| `/api/validation` | GET / authenticated | Current blockers |
| `/api/publish` | POST / publisher | Prototype publication; production always rejected |
| `/api/publications/{id}` | GET / authenticated | Immutable manifest |
| `/api/audit` | GET / authenticated | Local event trail and chain integrity |
| `/api/lab/actions` | GET / authenticated | Allowed laboratory actions |
| `/api/lab/sessions` | POST / editor | New rule-lab run |
| `/api/lab/sessions/{id}` | GET / authenticated | Persisted state |
| `/api/lab/sessions/{id}/actions` | POST / editor + expected_version | Validated state transition |

`kind` is characters, factions, missions or assets. Bodies are bounded to 256 KiB. Host/origin checking, constrained IDs/paths, parameterised SQL and no executable user scripts reduce the local attack surface. Tests exercise role denial, malformed inputs, stale writes, dependencies and publication integrity. This is **not** a penetration test, an internet-service security certification or a concurrent multi-tenant load test.

## Security limitations

The three role tokens are generated locally. A single operator with the credentials file can act as all three roles; distinct tokens do not establish independent human review. SQLite is single-host local persistence. The audit hash chain detects accidental/inconsistent edits but is not independently anchored; a privileged operator can rewrite or replace the entire database. Manifests are hashed, not cryptographically signed with a trusted release key. The runtime is not an authenticated remote content downloader.

No production OIDC/MFA, tenant isolation, password/account lifecycle, expiring access tokens, rate-limit infrastructure, external WORM audit storage, operational backup service, malware scanning or content delivery network exists in the starter. Production publication is hard-blocked even if metadata are manually labelled approved, because approval cannot substitute for those controls or actual asset validation.

## Proposed production topology — not implemented

Keep the authoring service a modular monolith initially. Use managed PostgreSQL for metadata and immutable revisions; object storage for quarantined source files, review renders and cooked releases; an OIDC identity provider with MFA and per-user roles; a job queue for scan/import/validation/cooking; isolated Unreal build workers; signed manifests and a CDN for compatible cooked bundles; externally anchored audit events and tested backups. Use secrets-manager identities scoped to each worker rather than shared tokens.

Select one managed player backend only after the offline slice works; **PlayFab is the proposed candidate**, not an installed dependency in this code. Keep player identity/cloud saves/telemetry separate from the staff content studio. Premium offline campaign progress may remain local; every online reward or purchase must be verified under server-owned policy. Do not promote a local save to trusted currency. Co-op requires a later authority, replication, reconnection and latency design; the local GAS ability policy is not co-op-ready.

Production content pipeline: upload -> quarantine -> file/type/size/rights scan -> DCC import -> Unreal data validation -> skeleton/material/LOD checks -> target-platform cook -> isolated gameplay validation -> reviewer approvals -> signed immutable release -> staged rollout -> rollback to a prior compatible manifest. JSON may reference approved assets, but may not become executable code or an arbitrary download URL.

## Native mechanics and parity

The authored C++ controller uses Enhanced Input. Gameplay Ability System classes dispatch three local abilities. Mission state currently owns cooldowns/resource limits; production AttributeSets, GameplayEffects, prediction, cancellation semantics and full ability testing remain work. Web Step includes an intended capsule-swept arc to authored anchors, Borrowed Voice is time-limited, and Trick Mirror produces a temporary stand-in distraction. The watcher is a local visibility/suspicion prototype rather than a StateTree-based social AI system.

The rule laboratory uses discrete beats; Unreal uses seconds, spatial interaction and collision. Their implementations are **not semantically identical or cross-runtime verified**. Before expanding, define shared transition fixtures for evidence/permit/claim/route/outcome and run them against both. Keep spatial mechanics in native tests. A Python unit-test success cannot certify Unreal collision, animation or input.

## Build evidence and operational policy

Each native release candidate should identify source commit, exact Build.version, platform SDK/toolchain, content-manifest hash, cook arguments, asset bytes, test reports and package hash. The engine lock is generated only on an installed engine host. Keep Development and Shipping outputs separate. Use fresh archive directories to avoid stale-package success. The supplied workflows are templates with real commands, not executed remote CI evidence. Never place signing secrets on an untrusted pull-request runner.
