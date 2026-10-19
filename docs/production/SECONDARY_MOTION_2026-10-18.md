# Secondary motion checkpoint — 18 October 2026

Branch `feature/local-milestone-verification`, HEAD `ec7bf0bcf16634a13c12e92433e9731064890e80`. No commit, push, publication or deployment.

## Scope

Movement-responsive secondary garments plus bounded wind/water presentation inside the existing hero cells. Gameplay root/capsule, collision, mission state, selection, canonical identities and existing asset revisions remain authoritative and unchanged. This does not close creative, device, broader navigation, memory or lighting gates.

## Character deformation

`AnanseSecondaryMotion.h/.cpp` adds a critically damped, closed-form response inside the existing spider and feline/cast animation proxies. Game-thread collection reads owner velocity, acceleration, turn rate and the previous evaluated chest orientation. Worker evaluation reads the copied values only; it makes no world or collision queries. Garment deformation is applied once to an explicit imported-bone allowlist before the existing contact solve. Supporting limbs, hands, props, skin, armour and tails are excluded. Parent indices were checked: no supporting limb or grasp chain descends from a mapped garment bone.

Targets: pitch ±5°, sway ±4° before per-bone stiffness scaling. Roots are stiffer than hems. The spring frequency is9/s; no Euler integration or unbounded accumulated energy. State resets on explicit transient-motion reset, new proxy/possession, teleport over150cm, long frame over0.25s, clock discontinuity, and disabled comparison mode. Pause does not advance world-time material motion.

| Design | Dedicated garment bones receiving motion |
|---|---|
| AnanseSpider | cloth_01, cloth_02, cloth_03 |
| OseboLeopard | cape_L/R_01–03 |
| AsoYaa | Dress_L, Dress_R |
| EsiHuman | Dress_L, Dress_R |
| OseboHuman | cape |
| KojoTortoise | Apron_L, Apron_R |
| EsiMoth | Garment_L, Garment_R |
| Kwaku | No independent loose-cloth chain in the saved rig |
| KofiHornbill | No independent loose-cloth chain in the saved rig |

Kwaku/hornbill fitted surfaces retain authored body movement. Independent sash, bag/strap or loose garment deformation remains work; body joints were not repurposed to imitate cloth. Single-bone pieces remain less flexible than multi-bone capes. This is bounded bone-based secondary motion, not self-colliding cloth simulation. Existing Aso robe/leg penetration and other creative deformation defects are not repaired or approved by this pass.

## Environment variants

Editable copies: `SourceArt/Environments/MarketSanctuary/Motion_v001/`. Native variants: `/Game/Ananse/Environments/Motion_v001/`.

Twelve modules: CanopySwag, Understory, CrownGuardian, RiverFig, TwinnedElder, RiverReach, StreamPools, LayeredGrove0–2, EcologyIsland, VerandaCorner. Authored RGBA masks mean branch sway / leaf flutter / water / hanging cloth. They are explicitly exported as the primary `COLOR_0` set. Source position/UV pairs and triangle counts match all twelve originals exactly. Original source scenes, maps and native assets are preserved.

Bounded shader motion: slow branch sway up to2cm, leaf flutter0.7cm with0.22cm vertical component, hanging cloth1.2cm, water vertical waves up to0.75cm. Masks pin roots, rigid surfaces and water banks. Water retains its two opposing scrolling normal layers. World-position phase offsets avoid identical motion across instances. Mesh bounds expand6cm in each direction. Conventional three LODs; no Nanite/Lumen dependency, new transparency or actor ticks. No new geometry density is propagated beyond the existing placements.

`AAnanseEnvironmentCluster::BeginPlay` swaps only exact allowlisted original meshes when `-AnanseEnvironmentRoute` is active. Per-component material overrides receive corresponding duplicated motion graphs, preserving their original surface appearance. Original map files and instance transforms are not edited. All scenery remains non-colliding. Bridge deck/collision is untouched.

`-AnanseDisableSecondaryMotion` disables both skeletal additions and environment swaps for comparison. Existing normal-map water flow remains present in this comparison; it is not a completely static-water reference.

## Validation and evidence

Evidence root: `.local/verification/secondary-motion-20261018/`. Final qualification results are recorded separately from cook success. See the machine-readable delivery report for actual stage outcomes, package hashes and preservation audit.

Python:382 passing tests. Native:37 passing automation tests. Tests cover spring frame partition independence/settling/reset, exclusions, actual imported masks, anchored and moving vertices, LOD presence and culling padding. Fixed-camera capture validation rejects missing bindings, wrong fixture, collision/tick authority, missing camera data, abnormal exit and non-finite time.

The first mask import failed because a white default colour layer preceded the mask. The first packaged attempt also exposed legacy per-component material overrides and an unavailable capture-library dependency. Failures and the superseded package are retained. Export selection was corrected, exact override variants were authored, and capture uses the already installed ImageMagick tools. A later checker rejection used the old material namespace; the exact new override namespace now has a regression test. No runtime or terrain assertion was relaxed.

## Open gates

Creative motion/naturalness review remains required, including extreme poses, cape/body/tail clearance, robe/leg clearance and full-rate gameplay. Capture overhead and desktop traces are not performance qualification. Mobile and physical devices remain unqualified. Baked lighting remains blocked by the documented Lightmass startup failure. Broader navigation, long-session memory, final audio and campaign mapping remain open. No new family, map expansion, engine patch or driver change.

Further requested motion remains: independently authored Kwaku sash/tabard and hornbill loose accessories, water interactions, floating boats/moorings, flexible sleeve detail, and collision-aware cape/robe refinement. Existing carried props retain their verified contact sockets. This checkpoint does not claim every movable object or garment is finished.

Campaign scope: the pursuit character already uses the shared authored Animation Blueprint path. Static `AAnanseInteractable` presentations, including Aso Yaa’s negotiation NPC, use legacy single-node playback and do not receive the new skeletal spring. Their migration must preserve exact clip timing and ledger contact; it remains pending. The lab Aso Yaa does receive the new robe response.

## Delivered engineering candidate

Package: `Builds/Linux/20261018T043700.710245Z/`.

ELF SHA-256: `131d8593ede3670b45bcb845177dd03a0d14ae93667560e9df351a0115b5d2b8`.

Canonical39-file payload SHA-256: `e6d4aa4b5c86e55373f9e24cab1fee31495045c7f8eec63345ff618d359c7b4b`.

Fresh results:382 Python,37 native,10 packaged checks passed. The packaged checks are four fixed-camera enabled/comparison sessions, full67-clip cast qualification,40 spider/leopard transitions with failure recovery, nine leopard motions, leopard terrain atLOD2,240-second spider terrain/checkpoint, and one negotiation/protect episode through both environments. Six route/outcome combinations and physical devices were not rerun or newly qualified by this milestone.

Worst leopard per-foot p95 stance drift:0.5783679485321045cm; maximum penetration:0.000029577260647783987cm. Spider worst drift:0.000003493988060654374cm (`3.493988060654374e-06`); maximum penetration:0.000003778802920351154cm. Full per-foot samples, fixture coverage and exclusions are retained in `qualified/terrain-metrics.json`.

All1,586 baseline native-content files and1,123 baseline model/source entries match their original hashes. Both protected39-file rollback payloads remain unchanged. New content:100 native files, approximately12.02MiB on disk;15 editable/interchange models plus one source-status entry. LOD0 triangle counts match all12 originals. LOD1/2 reduction differences are recorded in `qualified/lod-inventory.json` and range from−4 to+1 triangles per asset/LOD. These are storage/geometry facts, not RAM, GPU or mobile performance results.

The runtime/config, native content and model fingerprints match the final cook. One post-cook supervisor-only change added acceptance of the exact preserved-override material namespace; its rejection of legacy non-motion materials remains covered by a regression test. Cook inputs and the final supervisor hashes are both retained.

Five actual packaged review videos are encoded at8fps from owned-window captures with timestamps and frame-hold mapping; start/middle/end frames were decoded at1280×720. They are diagnostic samples, not full-rate fluidity approval. The additional rear-cape session uses seven synthetic clip keys and exited normally; it is separate from the ten assertion-backed packaged checks. Decoded Aso footage visibly confirms knee/robe penetration, so garment clearance remains FAIL. Other creative motion fields remain REVIEW_REQUIRED.

Review ZIP: `/home/favl/Downloads/ANANSE_Secondary_Motion_Review_20261018.zip`.

Launch environments:

```bash
python3 scripts/play_integrated_candidate.py --package Builds/Linux/20261018T043700.710245Z --scene chapter --profile secondary-motion-review
```

Launch existing cast labs:

```bash
python3 scripts/play_integrated_candidate.py --package Builds/Linux/20261018T043700.710245Z --scene cast-lab --profile secondary-motion-cast
```

Use PageDown for the seven cast designs, Home for Ananse, End for the leopard;1–9 select clips,0 restores automatic presentation. Comparison command flag:`-AnanseDisableSecondaryMotion`.

Full delivery, input hashes, changed paths, accepted stage commands and preservation reports are in `.local/verification/secondary-motion-20261018/qualified/`. The allocator workaround remains`-ansimalloc`; evidence uses frame-only traces, preserving the separate detailed-CPU-tracing shutdown limitation. No staged files, commit, push, merge, deployment, public upload, licence acceptance or system-tooling change.
