# Second skeletal family checkpoint — 15 October 2026

Branch `feature/local-milestone-verification`; HEAD `ec7bf0bcf16634a13c12e92433e9731064890e80`. No commit or push. Existing dirty work is retained. The initial blocked status below is historical; the later user-approved Blender acquisition and executed continuation supersede it.

## Sequencing correction

The user now authorizes OseboLeopard as the second skeletal family. Preserve the verified Ananse selection checkpoint, qualify Osebo independently, then execute the shared cross-family gate. The earlier requirement to close the first character before creating a second family is superseded only for this dependency. No acceptance threshold is waived. No existing non-spider asset path is requested. Kwaku's primitive fixture cannot satisfy the gate.

The original work-order package and manifest remain unchanged at `SourceArt/CharacterWorkorders_v1/ANANSE_Individual_Character_Workorders_v1/`. The original four-creature image was inspected locally and its SHA-256 matches `c0ad47020d133b747c6dc1db6402dde70e4aa0f617650a725316ff64a0d3b946`. Osebo remains an isolated lab design; campaign species and narrative binding are unapproved.

## Reconciled retained terrain evidence

This is an audit of the existing `final-terrain-02` session, not a new rendered traversal. Fixture `/Game/Characters/AnanseSpider/ContactLab_v006/L_AnanseContactLab`; evaluated tarsus plus original tip offset at `OnBoneTransformsFinalized`. Each leg has positive flat/ramp/steps/uneven/moving/disappearing-support coverage. Actor and fixture aliases overlap; do not sum them as independent samples.

| Leg | Samples | Excluded swing/airborne/invalid | p95 stance drift cm | Decimal cm | Maximum penetration cm | Decimal cm |
|---|---:|---:|---:|---:|---:|---:|
| front_l | 69403 | 29152 | 3.4911711281893076e-06 | 0.0000034911711281893076 | 3.8037817375879968e-06 | 0.0000038037817375879968 |
| front_r | 65480 | 33075 | 3.6899357382935705e-06 | 0.0000036899357382935705 | 3.5726457099372055e-06 | 0.0000035726457099372055 |
| rear_l | 62511 | 36044 | 3.4348959161434323e-06 | 0.0000034348959161434323 | 3.774411652557319e-06 | 0.000003774411652557319 |
| rear_r | 55547 | 43008 | 3.4453553325874964e-06 | 0.0000034453553325874964 | 3.531951051627402e-06 | 0.000003531951051627402 |

All four meet the existing per-leg limits: p95 drift ≤2 cm and maximum penetration ≤0.5 cm. Excluded samples are disclosed, not discarded from the original report. This is engineering contact evidence, not general mesh deformation or art approval.

The earlier command record printed Python's report summary and then ran `ps -C Ananse -o pid,etime,stat --no-headers`. The compound shell's exit 1 followed the trailing process probe finding no running game after normal shutdown. It was not a failed native assertion or evidence that Python's printed status overrides a checker failure. The retained native supervisor records `exit_status: 0`, `process_returncode: 0`, `forced_termination: false`; the report records normal exit and 64 assertion strings. The original wrong-map invocation remains a preflight rejection, never a terrain pass. A regression reproduces the distinction between a successful Python command and a failing trailing shell probe.

`scripts/verify_contact_report.py` independently requires the exact 64 assertion identities with multiplicity, contact scenario, explicit fixture/pawn/controller, rendered backend, completed phase/duration/trace closure, normal supervisor and game exit, matching launch/slot, executable bytes, publication identity and three preserved cook fingerprints. It understands the real encoded-metrics schema, checks every leg and fixture, and rejects absent, nonfinite, excessive or zero-sample measurements. The CLI rejects pre-launch report timestamps. Catalogue file SHA and publication payload SHA remain distinct. It does not relabel the original working-tree fingerprint record as independent package provenance.

Executed command: `python3 scripts/verify_contact_report.py --run .local/verification/spider-selection-20261014/final-terrain-02 --cook-inputs .local/verification/spider-selection-20261014/final-package-inputs.json` — exit 0. Initial checker-development failures (object-path form and file SHA versus publication SHA) were corrected against actual schema; no runtime evidence was edited.

## Native authoring work

New materialized `/Game/Production/Characters/SpiderRig_v001/IK_AnanseSpider.IK_AnanseSpider` is an actual `IKRigDefinition`, 89512 bytes, SHA-256 `54c8cda8990c645eda908e410d182190eff9bf3a3eaaaebf5c609768ca113ea6`. Its four goals and four enabled limb solvers map femur/tarsus chains; eight retarget chains preserve four arms and four supporting legs. It references the existing qualified mesh. `scripts/build_spider_ik_authoring.py` refuses to overwrite previous assets/evidence.

This asset is **authoring-only**, not a runtime solver replacement. Defaults still need pose/tuning acceptance. The native contact proxy remains the single runtime deformation path. No source mesh, skeleton, clips, physics or controller were replaced. CR and ABP integration, graph execution and packaged rig evidence remain open. A second-process reopen checker uses installed-engine controller APIs. Its first attempt failed on a nonexposed struct property; failed evidence is retained under `ik-reopen`. The corrected repeat under `ik-reopen-02` passed with exit 0, confirming the actual mesh, four enabled solvers/goals and eight saved chains.

## Modelling dependency and proposed acquisition

No qualified Blender executable was found in PATH or the previously bounded local tool locations. No nonexistent character kit was sought. No Osebo mesh, animation or native family is claimed created. No primitive substitute was introduced.

Proposed tool: **Blender 4.5.14 LTS Linux x64 portable**, official archive `https://download.blender.org/release/Blender4.5/blender-4.5.14-linux-x64.tar.xz`, expected download **378045212 bytes** from the official release index. Verify against official `blender-4.5.14.sha256` before extraction; inspect archive entries first. The expected digest has not yet been fetched. If official access remains denied, stop acquisition and report it; do not bypass the restriction.

Proposed new destination: `/home/favl/.local/opt/blender-4.5.14-linux-x64/`; archive/checksum in a new project-local ignored acquisition directory. Reserve **4 GiB** as a conservative working allowance, not a measured extracted size; additional model/render outputs need separate space. Invoke by absolute path, leaving system Python, PATH, shell startup, drivers and other applications unchanged. No account, paid add-on, reference upload or sign-in is proposed. Review bundled licence terms before use; no interactive licence acceptance is authorized here. Then qualify version, headless scene save/reopen and GLB/export dimension probe before modelling.

Approval is required by repository `AGENTS.md`, Production execution order 6: “Require explicit approval for software acquisition when needed”. Pending approval blocks DCC-dependent Osebo authoring, not the independent report/native authoring work above. This request does not ask the user to supply an existing character asset.

## Verification and remaining acceptance

Current full Python suite: **183 passed**, including 24 new checker regressions; command `env -u PYTHONPATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q`. Separate input-package checks passed: 20 tests, 52 declared file hashes and 9 contracts. JavaScript syntax, Python compilation and `git diff --check` passed. All 16 protected original native assets are unchanged. Engine authoring execution is not counted as native automation. The former 16 native tests and packaged runs remain historical; no new package or cross-family session was run.

Protected rollback: `Builds/Linux/20261014T220439.626105Z/`. Existing saves, publications, Kwaku revision history, original assets, manifests and failed reports remain intact. Generated native content/evidence stay local; nothing staged. ANSI workaround and detailed CPU-tracing failure remain unresolved.

Next dependency decision: approve the precise local DCC acquisition above. Then author the actual reference-based Osebo model/rig/actions, qualify its native assets independently, and execute three rendered sessions with at least 20 complete Ananse→Osebo→Ananse round trips each. CR/ABP graph integration, studio publication cycle, model-derived views, creative approval, physical controller and mobile gates remain explicitly open.

## Approved acquisition and executed authoring continuation

The user approved the proposed acquisition. Official checksum `9ba871ff2ecd36526b77432745980b7e6664ecd0c7ca11c48849073dcfe06da3` matched the complete 378045212-byte archive. The extraction inspected 6512 entries, rejected escaping links/paths and expanded 1167187759 file bytes into the approved user-local destination. Bundled licence files are retained. No system environment, driver or Python installation changed.

Blender 4.5.14 LTS saved/reopened a dimension-probe scene and exported/reimported its GLB at 0.5 × 0.75 × 2 metres. The same qualified import conversion in Unreal measured 75 × 50 × 200 cm after axis mapping. This closes the acquisition/units dependency; no further installation approval is needed for this approved tool.

An original editable leopard now exists under `SourceArt/Characters/OseboLeopard/Authored_v002/`, including scene, skinned GLB, static inspection OBJ, original rosette texture, rig map, nine distinct actions and model-derived views/turntable. The earlier crude v001 is retained. The v002 scene SHA-256 is `8d34d1b0a92c92763ec7b006e1962351f88fd0cb68f077700c534389238ad6f1`; GLB `4e738347d9583af8b0177ae187fb0c3c441e495fdeafd338f5c726b144aaa076`. Structural checks found 110 parts, 33326 vertices, 66106 triangles, 64 bones, at most two positive influences per vertex, no unweighted vertices and finite evaluated geometry at 45 sampled action poses. Only LOD0 exists; this is not an optimisation or visual deformation approval.

Unreal imported a genuine separate SkeletalMesh, Skeleton, PhysicsAsset and nine AnimSequences under `/Game/Ananse/Characters/OseboLeopard/Authored_v001/`. Native revision and editable-scene revision are separate identifiers. An actual compiled `BP_OseboLeopard`, typed `DA_OseboLeopard`, authoring IK Rig and isolated lab map were created. The saved Blueprint defaults reopened correctly in a separate process. The importer-generated physics constraints still need deliberate review.

The independent editor-game run exercised 60 seconds, about 359 cm of simulated movement, possession, zero ability grants and evaluated motion in all nine distinct clips, with normal process exit. A subsequent alignment check measured face-to-actor-forward dot product 1.0; the side-on capture was camera framing, not a reason to apply a second rotation.

Actual `ABP_AnanseSpider` and `ABP_OseboLeopard` assets now contain compiled Clip-variable → Sequence Player → Output Pose graphs, with different skeletons and native parents. The spider's existing proxy evaluates its source graph and then applies the existing contact solve once. Separate graph-evaluation counters and active-player clip identities are measured. The new leopard graph independently ran all nine clips with matching active-player identities and normal exit. This supersedes the earlier single-node playback evidence for graph acceptance; it is still not a feline contact test.

Actual `CR_AnanseSpider` and `CR_OseboLeopard` are executable FK authoring rigs with 102 and 64 mapped controls. Separate-process checks executed the saved graphs, changed 10 spider and 9 leopard control poses and found maximum local-translation errors of approximately 1.53e-14 and 6.18e-14 cm respectively. These are authoring FK checks, not runtime contact, collision clearance or approved joint-limit claims. First attempts exposed Python return-value/struct-constructor conventions; failed logs remain retained. No empty rig is counted as functional.

The selector now allows the leopard while preserving primitive-profile compatibility and the Kwaku campaign default. First cross-family run: 40 valid movement/gesture-confirmed transitions, but the deliberate blocked-spawn case failed. It is not accepted. The production transaction was tightened to reject capsule obstruction and adjustments beyond 100 cm. Second run: blocked-spawn rejection passed, but normal selection was correctly refused near the original lab ramp after 19 transitions. It is not accepted. The normal stress walk is now explicitly bounded on clear flat floor; the independent deliberately blocked-spawn case remains. This changes the fixture path, not contact thresholds or failed evidence.

The current work remains in progress: fresh final rendered/package runs, original affected terrain/pursuit regressions and complete build hashes are pending below. Earlier 18-native-test results are retained; an additional real Animation Blueprint graph test has been authored and compiled but its new full suite has not yet executed. Source/native rig maps and sockets are being completed. Feline live contact, physics/joint-limit review, reduced LODs, studio publication/gallery, AI presentation binding and creative approval remain open. No campaign species mapping, publication, commit or push occurred.


## Fresh native/package checkpoint

Full Python regression passed **207 tests**. Full native automation passed **19 discovered/executed/passed** with the real Animation Blueprint graph test; these are separate suites. Build 20 only adds the second isolated lab fill light after build 19. The accepted editor-game cross-family run `cross-editor-03` passed 40 committed transitions (20 complete round trips), seven named negative cases, real movement/graph/pose checks, four rebuilt spider contacts and normal exit. Earlier failed runs remain retained.

Both saved FK rigs reopened in a new process and executed **15 controls each**, including fingers/eyes and cloth/cape additions. Reopened native path maps under `SourceArt/Characters/{AnanseSpider,OseboLeopard}/INTEGRATION_PATH_MAP_20261015.json` resolve all nine requested roles to their actual classes and byte hashes. Existing correctly named import equivalents are reused. IK/Control Rigs are authoring assets; Animation Blueprints execute the runtime clip graphs. Spider runtime applies the original contact solve once.

Fresh Linux package: `Builds/Linux/20261015T011422.299570Z/`; UAT exited 0. ELF SHA-256 `d5b0fd633fd602ab93fd8d8f3eeeab604b18096fdb0e8b15bcdfdc7a6495098b`. Recorded pre-cook and post-cook bytes match across native source, native assets, authoring source and models. The four aggregate fingerprints are in local `cook-inputs-01.json`; 42 packaged file hashes and exact engine/DCC binary identities are retained locally. Source/native asset maps stay outside Git; no assets, evidence or publications were staged.

The first independent packaged Osebo run passed at 60.00259017944336 seconds, all nine distinct graph clips, 359.23626708984375 cm measured movement, +X face alignment 1 and normal exit. It saved only the dedicated lab profile. Packaged cross-family/restoration/terrain/pursuit checks are pending their results below; this paragraph does not claim their completion.

The raw original spider GLB imports into Blender with evaluated bounds that differ from the authoritative native rest geometry; both failed parity attempts remain retained. A **read-only native FBX export** instead matched native geometry bounds exactly after Blender import. Its editable inspection scene is `SourceArt/Characters/AnanseSpider/NativeReference_v001/EditableScene_v002/AnanseSpider_Existing.blend`. Native 102 bones are represented by 101 Blender bones plus the armature object representing native root. This is a documented inspection conversion, **not a qualified reimport**. No original skeleton or kit was changed. Its solid/topology/skeleton/turntable views come from that saved scene; authored native joint-limit/deformation approval remains open.

The portable acquisition used existing project instructions and installed-engine APIs. Skill-retrieval keyword/search tools were unavailable when rechecked for native/package verification; no external retrieved skill dictated implementation. No new service, account, purchase, Android installation or campaign species approval was inferred from the Blender approval.


## Executed packaged selector results

All three final rendered packaged sessions passed with normal process exits and no forced termination:

| Session | Active seconds | Committed family transitions | Complete round trips | Fresh-process restored design |
|---|---:|---:|---:|---|
| cross-package-01 | 60.00159454345703 | 40 | 20 | osebo-leopard-v1 |
| cross-package-02 | 60.00177764892578 | 40 | 20 | ananse-spider-existing |
| cross-package-03 | 60.0000114440918 | 40 | 20 | No restore requested |

Each session exercised seven distinct negative cases: unknown design, missing asset, incompatible rig, blocked spawn, cancellation, latest-request wins and late-completion rejection. The late-completion event is an adversarial timed callback to the production completion path, not a claim of observed network packet reordering. Every committed transition checked actual requested/selected ID, possessed class, mesh, skeleton, animation instance, physics binding, camera/input, movement, evaluated gesture, finite pose and graph clip. Spider returns rebuilt four solved contact chains. Exactly one controlled pawn, zero lab AI owners and zero narrative ability grants were required. These are 120 committed transitions, not UI-request counts or same-family cosmetic swaps.

Keyboard run passed all six named checks, including leopard/spider selection, actual mesh wireframe, material restoration, profile restore and pause clock. Input was **synthetic focused X11 keyboard**, not physical keyboard/controller/touch qualification. Separate captures show movement and the command pose. Physical controller remains untested.

The actual packaged leopard capture is `.local/verification/osebo-family-20261015/leopard-package-01/result.png`. Shared-lab side captures still have poor illumination; silhouette, face, armour and deformation remain visibly rough and unapproved. No automated rig/pose count supplies creative or cultural approval. The existing spider remains its labelled engineering proxy. Feline live terrain contacts are **not implemented or accepted**, and no feline drift/penetration pass is claimed.

The corrected native-spider topology sheets are under `NativeReference_v001/EditableScene_v002/technical_v003/`. Earlier nearly invisible edge renders are retained as failed inspection outputs, not accepted topology evidence. The correction converts edge width from world metres to each object's local scale. It occurred **after the cook**: `scripts/render_osebo_technical.py` and seven new inspection files differ from the cook fingerprint. Their exact separate identities are in `post-cook-inspection-output-changes.json`. Native source, native content and the saved source scenes still match the cook. The different aggregate byte sequences are not labelled identical.

Verified lab launch (from the existing project; ANSI workaround retained):

```bash
/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261015T011422.299570Z/Ananse/Binaries/Linux/Ananse /Game/Characters/AnanseSpider/Lab_v001/L_AnanseCharacterLab -ansimalloc -windowed -ResX=1280 -ResY=720
```

Home selects Ananse; End selects OseboLeopard. WASD moves, mouse looks, P pauses, F6/F8 save/restore the dedicated lab profile, V toggles actual mesh wireframe. Leopard 1–9 select the nine authored motion categories; 0 resumes automatic idle/walk. The independent leopard map is `/Game/Ananse/Maps/CharacterLabs/L_OseboLeopardCharacterLab`. Campaign default remains Kwaku.

Changed implementation paths for this milestone include `AnanseLeopardLab.{h,cpp}`, `AnanseLeopardTests.cpp`, `AnanseAuthoredAnimation.{h,cpp}`, `AnanseAnimationTests.cpp`, `AnanseCrossFamilyVerification.cpp`, `AnanseLabSelection.{h,cpp}`, and affected `AnanseGroundContact.{h,cpp}`, `AnanseSpiderLab.cpp`, `AnanseWorld.cpp`, module/config cook bindings. Project scripts cover approved DCC qualification, editable authoring, native import/rig/graph/path-map creation and strict rendered-report supervision. Exact materialised asset paths/classes are in the two versioned source-art path maps, not guessed `SK_` names. Original source parts, both imported families and all failed reports remain preserved.


## Fresh cooked terrain regression

`terrain-package-01`: **64 assertions passed**, 240.00086687225848 active seconds, normal process exit 0, strict independent report checker passed. Explicit map `/Game/Characters/AnanseSpider/ContactLab_v006/L_AnanseContactLab`; original post-evaluation tarsus plus 10.679 cm tip offset retained. Limits remain per-leg p95 stance drift ≤2 cm and maximum penetration ≤0.5 cm.

| Leg | Stance samples | Excluded swing/airborne/invalid | Full p95 drift (cm) | Full maximum penetration (cm) |
|---|---:|---:|---|---|
| front_l | 87280 | 41424 | `3.496673571135034e-06` (0.000003496673571135) | `3.7918480302323587e-06` (0.000003791848030232) |
| front_r | 83346 | 45358 | `3.481113026282401e-06` (0.000003481113026282) | `3.5268501505925087e-06` (0.000003526850150593) |
| rear_l | 80608 | 48096 | `3.475366611382924e-06` (0.000003475366611383) | `3.728328692886862e-06` (0.000003728328692887) |
| rear_r | 73100 | 55604 | `3.4267072805960197e-06` (0.000003426707280596) | `3.5407695122557925e-06` (0.000003540769512256) |

Scientific values are complete report numbers; parenthesised decimals are rounded readable equivalents. Drift excludes non-stance samples explicitly counted above; penetration independently probes the actual evaluated feet during stance/swing/airborne. Every leg has positive coverage on flat/ramp/steps/uneven/moving/disappearing fixtures. Support aliases and actor names overlap and must not be summed. These are the declared 35 cm/s walking fixtures, not arbitrary terrain or high-speed locomotion acceptance.

Zero invalid transforms, segment-length errors and knee-limit violations. Desktop p95 frame interval **2.6409718990325928 ms**, native contact query **11.204276084899902 µs**, pose/contact solve **29.65424156188965 µs**. Frame trace and native contact CSV are retained. Inline recording overhead is included; these do not establish GPU/function-thread costs or mobile performance. Full CPU tracing shutdown failure and ANSI allocator workaround remain unresolved.


## Fresh canonical pursuit/episode regression

`pursuit-package-01` passed after **121.52544633299112 active seconds**, normal exit 0: five bootstrap assertions and 47 pursuit/episode assertion entries, ten capture/retry cycles, obstructed-capture rejection, successful played escape, negotiated consequence dialogue, sanctuary map travel, three epilogue interactions and saved completion. The obstruction fixture blocked the actual sight ray; centre range remained within capture reach while blocked. Separate saved checkpoints were created before choice and on sanctuary arrival. This is the **existing Kwaku/canonical Osebo mission**, not a claim that the leopard AI presentation is integrated or its campaign species approved. Social/rooftop were not rerun in this milestone; previous episode reports remain historical.


## Exact cook identity and artifact safety

- native_source_sha256: `3f48ae88258d6a29b8babba64b16445dd50df0909d61f2dc150ce8eea81ad9e9`
- source_asset_sha256: `abf97c096f436f1360ebda8b285104defb1e9ca7b73274f0f05013b538c7e936`
- authoring_source_sha256: `4e7ca778de7c766b621d61f49479b0423ec21284ec020ea40b0ebbcfa1b3ecac`
- authored_model_sha256: `6fb76dd7d15a6c5d7f9d034a506ad41ba9ecd4d85240440108ec3333c8f43c20`

These identify 50 native/config/toolchain input files, 80 native content files, 70 authoring files and 56 model/output files **at cook time**. Post-cook topology correction is recorded separately, as above. Toolchain is pinned UE 5.8.3 CL58210709, bundled clang20.1.8/.NET10.0.203 and approved portable Blender4.5.14; exact binary hashes are retained in `candidate-toolchain.json`.

Final protection audit matched all 39 rollback files and 16 original native assets; catalogue file SHA-256 remains `306bcc37c7d0adfa00ea0fcd1024762e1a601e38e3a1d0fb56aced02cb815705`. Its payload hash remains `8751423ca1c06e3da01c8ddb3c69641a5521bd8aadc41963594f0aed29ce82c4`; these are different identities. Original work-order manifest revalidated all 52 entries and nine contracts. No publication/database migration or canonical species change occurred. The earlier separate 20 input tests are not added into the 207 root result.

Zero staged paths. Targeted SecurityToken/AuthenticationToken assignments found zero in tracked working files and index; actual cooked DefaultEngine.ini also passed its entry-hash-verified targeted scan. This is **not a comprehensive historical/artifact secret audit**. Private backup, saves, failed runs and traces remain local. No credential rotation, history rewrite, commit, push, signing or deployment.


## Open qualification gates and next bounded work

The **packaged second-family selector checkpoint passes; full character acceptance stays open**. Continue with leopard live evaluated foot contacts and declared terrain measurements, art refinement against the original feline reference, reviewed skin/cloth/physics and joint-range/clearance inspection, reduced LODs, studio 3D gallery and reviewed cosmetic publication → cook → new-publication rollback, and isolated AI presentation binding to the existing pursuit. Canonical campaign species mapping requires its separate decision. Do not start another skeletal family or substitute Kwaku's primitive fixture.

The tests checked one live controlled pawn and mapping/ability/controller cleanup; they did not measure a long-run resident-memory plateau. Independent/final cross-family scenarios did not establish every camera obstruction condition, physical controller/touch, mobile performance, final recordings, production service deployment or rights/creative acceptance. The native-spider FBX inspection scene is not a qualified round-trip replacement. Source-art and generated native output remain local through scoped `.git/info/exclude` rules; clean-checkout retrieval still needs the approved artifact-storage/publication workstream. No shipping readiness is implied.


## Final separate-process checkpoint results

- **before-choice**: 61.53374981274828 active seconds; restored `decision`, outcome `None`; 5 bootstrap and 4 scenario assertion entries; normal exit 0.
- **sanctuary**: 61.54895034991205 active seconds; restored `sanctuary`, outcome `witnesses-protected`; 5 bootstrap and 4 scenario assertion entries; normal exit 0.

Saved fields, position/control, absence of transient chase actors and unchanged durable event IDs were compared. Both 60-second processes passed without repeating dialogue/consequences. Final executed summary is local `DELIVERY_STATUS.json`; raw reports, captures, frame traces and native timing CSV remain under `.local/verification/osebo-family-20261015/`. No final character/art/publication acceptance was fabricated.
