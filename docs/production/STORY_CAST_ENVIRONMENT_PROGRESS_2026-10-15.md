# Story cast and environment implementation — 15 October 2026

Branch `feature/local-milestone-verification`, base `ec7bf0bcf16634a13c12e92433e9731064890e80`. No new commit/push. Existing dirty work and all prior rollback packages preserved. This is a new engineering/content integration checkpoint, not final character, environment, episode or mobile acceptance.

## Implemented

Seven additional designs now have actual editable scenes, skinned GLBs, own skeletons, distinct keyed action drafts, front/left/right/back/beauty images, actual topology/bone/joint-pose sheets and model-derived turntables:

- `SourceArt/Characters/Kwaku/Authored_v002/` (v001 retained as an earlier rejected clothing/sash draft).
- `SourceArt/Characters/AsoYaa/Authored_v001/`.
- `SourceArt/Characters/EsiHuman/Authored_v001/`.
- `SourceArt/Characters/OseboHuman/Authored_v001/`.
- `SourceArt/Characters/KojoTortoise/Authored_v001/`.
- `SourceArt/Characters/KofiHornbill/Authored_v001/`.
- `SourceArt/Characters/EsiMoth/Authored_v001/`.

These are original editable WIP meshes, not final reference-faithful commissioned art. Human anatomy and hidden views are proposals. The hornbill uses its two wing-arms, not an additional arm pair. Moth lower wings/concealed legs retain proposed status. Existing spider/quad-leg anatomy and imported assets remain intact. No species or narrative identity migration was approved.

Native paths for each key: `/Game/Ananse/Characters/<Key>/Story_v001/`. Actual imported mesh `<Key>`, imported Skeleton/PhysicsAsset, `IK_<Key>`, executable authoring `CR_<Key>`, compiled `ABP_<Key>`, `BP_<Key>` and typed `DA_<Key>` are recorded per design in `.local/verification/story-cast-20261015/native-<Key>/<Key>-native.json`. Existing correct imported names are preserved through path maps rather than renamed. Labs: `/Game/Ananse/Maps/StoryCast_v001/L_<Key>CharacterLab`.

One shared input interface consumes each independent skeleton's own compiled graph and clips. No cross-species retargeting/skeleton compatibility declaration. Six grounded designs reuse the existing two-chain contact solver with actual rest geometry and one final deformation path. Moth has no claimed ground-contact pass. Gameplay capsules own collision; supporting feet never move the collision body. Runtime capsule resizing uses `SetCapsuleSize`, followed by a fresh floor check, rather than the initialization-only API.

Three saved native LODs per design, four configured influence ceiling, actual source maximum positive influences two. All normal-play physics bodies kinematic; no ragdoll or artist joint-limit/deformation acceptance. Maps, generated binaries, models and evidence remain local/unstaged and scoped through `.git/info/exclude`.

## Environments and episode staging

`SourceArt/Environments/MarketSanctuary/Authored_v001/MarketAndSanctuary.blend` contains editable facade/roof/stall/textile/wares/dock and tree/root/foliage/stone modules. Seven actual GLBs imported under `/Game/Ananse/Environments/Story_v001/`. Decorative foliage remains nonblocking; architecture, stalls, dock, tree and stone modules use static complex collision. Floor owns continuous ground support. These are authored environment drafts with dynamic lighting; baked/mobile rendering and detailed creative/material/environment acceptance remain open.

New free-play maps:
- `/Game/Ananse/Maps/Story_v001/L_Market_Authored`
- `/Game/Ananse/Maps/Story_v001/L_Sanctuary_Authored`

New episode staging maps preserve the original greybox and technical sanctuary:
- `/Game/Ananse/Maps/Story_v001/L_Market_EpisodeStaging`
- `/Game/Ananse/Maps/Story_v001/L_Sanctuary_EpisodeStaging`

Explicit `-AnanseStoryPresentation` selects staging episode map identities. Default campaign map identities are unchanged without that flag. Staging Kwaku retains canonical identity and powers, using a separate staged Blueprint; the lab definition remains powers-disabled. Staging Aso/Esi are visual performance actors, not duplicate mission owners. Canonical Osebo's existing pursuit optionally uses the human design; leopard species mapping stays unapproved. Older saves remain intact under the existing strict content-hash/map policy; no silent migration is claimed.

## Studio and publication

Extended the existing allowlisted visual schema and local hash-checked GLB resolver. Seven actual skinned browser previews verified joint/action counts, evaluated clip identity and changing skin poses, actual triangle wireframes and cleanup. No external script/model fetch or reference upload.

Technical prototype publication `89439f2b4de14ccab3245771a130d6cf`, payload SHA256 `24358a8cbf3871ad011df7c59250bd2be7527100bed8a0c82eaa68790aebcf1c`, was exported through the existing API after exact-revision technical checks. Temporary local technical roles do not supply independent human creative, cultural, rights or mobile approval. Asset records remain review/UNVERIFIED/mobile-false. All canonical character records, Kwaku history and earlier immutable publications compared unchanged. Private database/catalogue backups protected under the local evidence root; no tokens printed.

## Executed so far

- Python suite: 264 passed, including 23 new cross-family binding/source/report regressions; JS syntax checks passed. The initial test invocation picked up an unrelated inherited ROS plugin path; failed log retained, process-local PYTHONPATH isolation and disabled external pytest plugin autoload fixed the invocation without installing/changing unrelated tools.
- Native automation: 21 discovered/executed/passed, including new independent native family/LOD/kinematic binding checks. No authored-test-only counts.
- Seven source integrity checks passed: actual materialised scene/GLB hashes, skin joint counts, finite/nonnegative normalised weights, no unweighted vertices, distinct actions and matching model-derived technical view provenance. DCC's existing built-in codec encoded turntables; no installation.
- `editor-cast-06`: rendered 60.00029754638672 active seconds, normal exit0; all seven designs exercised through actual pose graphs/movement, each with 20 complete Ananse round trips (140 full round trips/280 commits). Six grounded families met per-leg flat-floor p95 drift <=2cm and maximum penetration <=0.5cm; full measured values/sample counts/exclusions in report. This does not establish multi-fixture terrain or physical-input acceptance.
- Earlier failed reports are preserved. Capsule initialization/floor-state errors caused Kwaku contact drift and taller-body spawn rejection; these were corrected without increasing thresholds. A wait for actual finalized spider pose replaces premature same-frame inspection, retaining four solved-chain assertion.
- Initial episode map duplication via the generic asset-copy API crashed with a standalone-world reference error before either staging map was materialized. The supported installed `NewLevelFromTemplate` API in one editor per map produced the new maps; failure logs retained and original maps unchanged. The first package preflight correctly rejected missing staging maps and was not a successful cook.

## Remaining verification and acceptance

The final correction candidate completed the twelve executed runtime/check stages described in the final checkpoint below. Their passing status covers this engineering milestone only; the work-order art, full per-character coverage, publication-variation and platform gates remain open.

All creative resemblance and deformation approvals remain open. The models are still simplified WIP, with visible silhouette/facial/clothing/paw/feather/shell detail and clearance work. Recorded gestures are animation drafts, not final acting or lip-sync. Final recordings, environment art/lighting/bake, species mapping decisions, full terrain fixtures for new families, physical controller/touch, long-session memory plateau, services and Android/iOS qualification remain open. Existing allocator workaround and detailed CPU-trace shutdown limitation remain; only supported frame/native timings may be reported.


## Materialised native family inventory

| Design | Bones | Actual distinct draft actions | Native LOD0/1/2 triangles | Kinematic bodies | Actual sockets |
|---|---:|---:|---|---:|---:|
| Kwaku | 46 | 11 | 107914/53956/26978 | 9 | 5 |
| AsoYaa | 48 | 8 | 72180/36088/18044 | 15 | 3 |
| EsiHuman | 49 | 8 | 70084/35040/17520 | 16 | 4 |
| OseboHuman | 49 | 8 | 77832/38914/19456 | 16 | 4 |
| KojoTortoise | 50 | 8 | 47964/23980/11990 | 13 | 5 |
| KofiHornbill | 49 | 8 | 61768/30882/15440 | 16 | 4 |
| EsiMoth | 54 | 8 | 49488/24742/12370 | 14 | 4 |

Native socket transforms are at the named actual bone origins. Prop-specific grip offsets, contact/deformation and joint limits still need work and review; socket existence does not prove a hand meets its prop. The first socket checker described only Skeleton sockets, despite saving valid mesh-local sockets; that failure is retained. The read-back now uses the installed engine's active socket list, covering mesh and Skeleton objects. All 29 new socket objects are saved and reopened through the native checks. Original spider/leopard sockets were not edited.

New dependency publication `000f3a0426ce4b11a44e4ce37110039d`, payload SHA256 `3c1f4c0939a5dfe4bfb028facb935c8b8587f122adf5e3b8e0aa20f79cfe0bff`, advances seven visual asset records to revision2 and registers seven actual environment static meshes. Native definition revisions remain1; source visual-record and definition revisions are separate. Canonical characters, Kwaku history and all earlier publications remain unchanged. Temporary technical review is not independent human art/rights approval.

Dynamic staging sky/real-time ambient capture and warm daylight now exist on the four new environment maps. This is desktop dynamic lighting, not baked/mobile acceptance. Kojo's36cm gameplay capsule radius covers the declared rest shell envelope; full posed doorway/cloth/staff clearance remains unqualified. Moth hover is a9–15cm visual offset over collision-aware horizontal walking, not flight or a campaign power.

The first staged episode failed the final escape because it inherited the lab45cm/s speed. Staging Kwaku now retains the existing420cm/s campaign movement and original rotation/input policy; clip inspection keys are lab-only. Contacts are qualified only for controlled low-speed walking; fast campaign movement and Web Step release the contact solve and use source animation. This does not qualify fast locomotion contacts.

The next staged episode passed capture/retry/escape but exposed a geometry-dependent test approach: the old gate approach was occluded by the new dock. The staging verifier now walks the real open dock lane and asserts unobstructed interaction rather than bypassing the gameplay visibility check. `editor-episode-approach-02` passed121.40698110638186active seconds through actual sanctuary travel and epilogue completion, approach `(1782.433,572.570,97.499)` to gate `(1800,700,60)`, actual trace obstruction `None`. The new final package also checks the pursuer's actual human SkeletalMesh/independent Animation Blueprint with primitive representation hidden.

## Asset backup/review delivery

`.local/deliveries/20261015-story-cast/ANANSE_Authored_Cast_Environments_20261015_v001.zip` contains366 verified asset entries, seven editable character scenes and one editable environment scene, skinned interchange files, actual technical views/inspection geometry/turntables and new native assets/maps. Size93137905bytes; SHA256 `085dc171ded59192d8bb71bfc2560b65a079db463910a8686c628a8a5145b539`. The archive was reopened and every manifest entry rehashed. It excludes original kits/private references/saves/databases/credentials/logs and is not a replacement project. It requires this project's current native classes; do not blindly extract over edits. Creative/production status remains WIP.

## Current selected package identity — tests in progress

`Builds/Linux/20261015T042839.571111Z/`; ELF SHA256 `688be041691d2ea8128bbfdad5a96382a4d57508a8d8ec8ac1704ccb81bb1986`. Exact native/config, content, authoring and model fingerprints are recorded in `cook-inputs-06.json` and compared equal after cook.39 immutable payload files are hashed separately from mutable Saved output. Current selected package regression stages remain in progress under `verified-candidate/`; earlier failed/intermediate results do not establish acceptance for this package.

Native automation21passed again after final socket/verification code. Python: 264 passed in the closeout run; input-workorder verifier checked52declared files, validated9contracts/81targets, and its separate20input tests passed. Neither source/input checks nor native automation alone prove final rendered gameplay or art quality. Targeted worktree/index assignment scan: zero SecurityToken/AuthenticationToken assignments, zero staged files. Actual cooked DefaultEngine.ini read back and independently digested: zero matching token assignments. This is not a comprehensive secret/history audit. The first scan invocation used a string for a byte-regex helper and was corrected; no secret values were displayed.

The previous selected024635package's39payload files and35original spider-content files match their preserved snapshots. Prior mutable-log discrepancy from the earlier task remains historical and was not rewritten.


## Art inspection and unfinished implementation — do not conflate with approval

The new cast is currently **rigged editable art blockouts**, not final reference-faithful characters. Visual inspection confirms substantial modelling work remains; this is not merely waiting for someone to approve finished art. Specific incomplete work is recorded in `remaining-work.json`: Kofi eyes are obscured by the current beak; Kojo still has an overly human face; human clothing/neck/shoulder joins and motion intersections need repair; Esi hair/instrument contacts are unfinished; moth facial/wing detail remains simplified. Detailed hand IK, facial morph/lip-sync targets, cloth/prop contacts and full per-limb clearance have not been completed.

The six new grounded families have passed flat-floor contact checks only. Three shared roster sessions are not three independent sixty-second runs for each individual character. New dependency publications prove native byte/path retrieval and reviewed revision handling, not a per-design cosmetic change/new-publication visual rollback cycle. Those work-order gates remain pending. Source file existence, correct native classes, counts and passing automation do not make the cast final or fully ready for the storyline.


## Sanctuary no-movement checkpoint correction

The selected042839 package passed the staged episode, full59clip shared cast session, market/forest cast sessions and pre-consequence restart, but sanctuary restart failed. Preserved diagnostics show the pawn was already exactly at its saved position `(-400,-350,77.650)`; its75.5cm half-height/30cm radius capsule was clear, with no overlap/encroachment. The zero-distance actor movement returned failure and the loader incorrectly called the location blocked. `LoadLocal` now accepts an exact-position/rotation no-op only after the engine's collision validation; all other placements still use checked teleport. The original save and failed reports remain intact. Build30 compiled; editor restart08 restored exact state and is checking the remaining idle duration. This change requires a fresh packaged regression; current source bytes differ from042839 cook inputs.


## Fresh correction candidate — final checks underway

`Builds/Linux/20261015T050301.033364Z/`, ELF SHA256 `9f25d1628a316e42dffe1053367a3cfaa077d568e51061e3a7d96f436f7ca824`. Exact frozen inputs: `.local/verification/story-cast-20261015/cook-inputs-07.json`; native source `a9898c3d722e8660182f6d202597bfb1c282eb9b0a67c4fa2c8d4433e82b9fdc`, content `35a58fda2417f8f8a93733e86e35a09ebbc3a0fe8ba7dc3f946052598d5d3c29`, authoring source `25bd9cecbe83934aa24ed05068c8df772c9aee0477e5b2f3f99d92866f8ea592`, authored models `e6b2dbd09aa3fd0c599c0db3f9a61fce084802e12a69aac4d4e942f4f0e9a21e`. All four categories compare unchanged after cook.39 immutable payload files recorded in `selected-package-07-payload-hashes.json`.

Post-fix Python: 264 passed and native21 discovered/executed/passed. Editor sanctuary restart08 completed60seconds with exact state restored and normal exit. The fresh package passed the staged played episode, full 59-clip, 196.3300018310547-active-second cast session and market/forest 60-second cast sessions. Each shared cast session performs20Ananse round trips per new design; this is not three 60-second individual-character sessions. Final execution ledger is `verified-candidate-02/execution.json`; restart, original terrain and keyboard/profile checks continue.

Twelve actual post-evaluation feet across six new grounded designs passed flat-floor drift/penetration targets; all individual values, sample counts and exclusions are in `new-family-flat-contact-07.json`. Largest p95 drift `2.1996664145262912e-05cm`, largest penetration `1.118694490287453e-05cm`. Moth is N/A; full new-family terrain qualification remains pending.

Native UnrealPak extraction failed on its Linux backslash-joined filename; the failed log remains. A read-only native list plus SHA1-verified uncompressed entry read checked the actual cooked DefaultEngine.ini: zero nonempty named file-server token assignments, SHA256 `6a02738f3f3a4d0d5ece1f6a80d263dceae5d0bb540c84983c9b87e78d175a37`. Tracked/index targeted scan also found zero nonempty assignments; an earlier broad-whitespace regex matched an empty line and was corrected. Neither check is an all-history/all-secret claim. No staged files, credential rotation or history rewriting. Rollback 39 payload files still match;41spider native paths unchanged since previously verified cook06.


Interactive launch from this candidate (uses existing lab controls; no physical input qualification implied):

```bash
cd /home/favl/Downloads/ANANSE_Production_Starter
env -u PYTHONPATH -u LD_LIBRARY_PATH \
  ./Builds/Linux/20261015T050301.033364Z/Ananse/Binaries/Linux/Ananse \
  /Game/Characters/AnanseSpider/Lab_v001/L_AnanseCharacterLab \
  -ansimalloc -windowed -ResX=1280 -ResY=720
```

Home: Ananse; End: leopard; PageDown: cycle seven new designs; WASD/mouse; Space: jump;1–9: draft clips,0:auto;V:wireframe;P:pause;F6/F8:dedicated lab selection profile. Creature campaign roles/powers remain restricted. To inspect staged episode presentation, use map `/Game/Ananse/Maps/Story_v001/L_Market_EpisodeStaging` with `-AnanseEpisode -AnanseStoryPresentation`; the final packaged verifier command is retained in `verified-candidate-02/staging-episode/command.json`.


The fresh package now passed both sixty-second process restarts. Original spider terrain regression passed240.00079711619765active seconds, with actual finalized tarsus/tip contacts, zero invalid transforms and unchanged thresholds. Full scientific/decimal per-leg values, sample counts/exclusions and native frame/query/solve percentiles: `spider-terrain-metrics-07.json`. The first leopard supervisor failed before engine launch (`ModuleNotFoundError: scripts`); invocation corrected to `python -m scripts.run_leopard_contact_check`, no source/package/threshold change. Remaining executions use `verified-candidate-02-remaining/`; original failed command/log preserved.


## Final executed engineering checkpoint

All twelve final stages passed on050301: staged episode; full59clip shared cast session; market60s; sanctuary60s; before-consequence restart60s; sanctuary-arrival restart60s; original spider terrain240s; leopard terrain160s atLOD2; original spider/leopard20round trips plus seven negative cases; keyboard selection; fresh-process Kwaku profile restoration; fresh-process moth profile restoration. Every selected final process exited normally. Execution is split across `verified-candidate-02/execution.json` and `verified-candidate-02-remaining/execution.json`; the original import-only supervisor failure remains explicitly recorded, not erased.

`FINAL_ENGINEERING_STATUS.json` combines successful stages and exact source/package identity while retaining `full_cast_storyline_ready:false`. Python264and native21passed after the save fix. The separately executed20input-work-order tests are not added to these totals. Source integrity, model-derived views and studio browser checks remain separate evidence categories. Keyboard events are synthetic owned-window input, not physical keyboard/controller/touch certification.

Leopard actual contact metrics atLOD2: left p95 drift `4.1062427044380456e-05cm`, right `0.6907605528831482cm`; maximum penetration both `2.9576965971500613e-05cm`. Samples65189left/65371right, with exclusions/fixture coverage and timings in `leopard-terrain-metrics-07.json`. Original spider full per-leg numbers remain in `spider-terrain-metrics-07.json`; new-family flat results remain in `new-family-flat-contact-07.json`. No threshold was increased. Native frame/query/solve measurements and frame traces are retained; complete CPU/GPU tracing and memory-plateau qualification are not supplied by these results.

Current source/content/authoring/model identities still match frozen07inputs. The93,137,905byte/366entry source/native archive was rehashed unchanged: `085dc171ded59192d8bb71bfc2560b65a079db463910a8686c628a8a5145b539`. Original rollback payload39files remain unchanged, and all41spider-related native paths compare unchanged since the previously protected cook06. No commits, staged files, pushes, installs, purchases, deployments, signing changes or private-reference uploads.

Genuine packaged captures are under `verified-candidate-02/{cast-full-clips,market-cast,sanctuary-cast}/` and `verified-candidate-02-remaining/keyboard-{create,restore-kwaku,restore-moth}/`. Visual inspection confirms sparse/dark environment drafts and simplified character blockouts. This is unfinished implementation, not only an approval dependency. Next work is actual face/clothing/feather/shell/wing/prop/deformation refinement, environment composition/material/lighting and performance/audio integration, plus the remaining individual gates. The fresh staging run covers negotiation/protect-witnesses; social/rooftop and expose-ledger need fresh-map verification. No claim that the whole cast or storyline is production-ready.
