# Cast and environment integration — 18 October 2026

Branch `feature/local-milestone-verification`, base HEAD `ec7bf0bcf16634a13c12e92433e9731064890e80`. Work remains uncommitted. No publishing or deployment.

## Scope

Verify the nine existing selectable designs and the River Market → Story Forest episode in the frozen Pass-4 Linux candidate. Repair verification and launch-access gaps without editing art, character rigs, gameplay architecture, maps or publications. This does not certify final polish or creative acceptance.

Candidate: `Builds/Linux/20261018T015736.098029Z/`.

## Integration access

From the project root:

```bash
python3 scripts/play_integrated_candidate.py --package Builds/Linux/20261018T015736.098029Z --scene chapter --profile chapter01-review
python3 scripts/play_integrated_candidate.py --package Builds/Linux/20261018T015736.098029Z --scene cast-lab --profile cast-review
```

The explicit review launcher supplies the established refined-character/environment bindings and uses a named isolated player-review profile when `--profile` is supplied; omit it for a fresh profile. Reuse the same name to resume the same review saves across processes. `--dry-run` prints the exact command without launching or creating a profile. The legacy default map is not promoted to an unapproved environment.

In the cast lab: PageDown cycles the seven cast designs; Home selects Ananse; End selects OseboLeopard. Existing clip, wireframe, pause and profile controls remain. In Chapter 01: WASD/mouse/Space move/look/jump, E interacts, 1/2/3 select established powers, Escape skips presentation, F5/F9 save/load. Physical controller and touch coverage are separate.

## Changes

- `scripts/run_story_cast_check.py`: require finite numeric duration, movement, bone/sample counts and segment-error values before accepting evidence. NaN/infinity/missing/boolean values cannot substitute for valid measurements; existing thresholds retained.
- `tests/test_story_visual_designs.py`: malformed numeric evidence regression cases.
- `scripts/audit_character_environment_wiring.py`: read-only native asset-class/generated-class, skeleton, physics, IK, Control Rig, Animation Blueprint, LOD and saved-world audit. Never compiles or saves assets. Runtime graph execution is verified separately.
- `scripts/play_integrated_candidate.py`: explicit Chapter 01/cast-lab launcher for an existing project-local package, with isolated profiles and required opt-in bindings.

## Evidence and qualification

Evidence: `.local/verification/integration-audit-20261018/`.

Historical Pass-4 results are not counted as new execution. The final results below refer only to this audit. No new cook is needed for these verification/launcher-only changes.

## Remaining production gates

Functional selection/pose checks do not approve faces, digits, clothing, props, materials, cinematography or resemblance. The five other cast designs remain authored drafts. Ananse's engineering proxy remains explicitly identified. Aso Yaa's corrected contact appearance remains a development-review override; it is not an approved immutable creative publication. Existing Kwaku/Osebo decisions are preserved.

Pass-4 environment creative acceptance remains REVIEW_REQUIRED. Baked lighting remains BLOCKED by the independently reproduced Lightmass startup crash. Mobile/physical-device performance, broader terrain/navigation, long-session memory, final audio/voice/lip-sync and unapproved campaign species mappings remain open. No new character family, map expansion or geometry propagation was performed.

## Visible limitations observed during this check

The corrected Aso stable-hold capture is genuine packaged output, but still shows simplified/flattened hand forms, angular sleeve/cuff transitions and a simplified ledger. Stable socket/contact metrics do not establish natural grasp anatomy or finished wardrobe deformation. These remain art-review items. The original all-cast lab captures also have strong side-lighting and dark silhouettes; they establish running content, not consistent cinematic presentation. The new opt-in launcher points at the existing corrected contact lab rather than that older lab map. No new likeness or polish approval follows.

Actual evidence examples:
- `.local/verification/integration-audit-20261018/aso-kwaku/ledger_stable_hold.png`
- `.local/verification/integration-audit-20261018/cast/cast_1.png`

The nine-motion leopard supervisor previously targeted only the original runtime mesh/map. It now has an explicit `--art-pass2` mode requiring the current ArtPass2_v003 mesh, generated pawn class and exact contact fixture. The historical default remains strict. Regression cases reject an old mesh, wrong fixture or missing/unevaluated motion in the current-revision check.

The first native audit retained an API-access failure after eight families; a second invocation used a relative project path and was rejected before opening the project. The corrected absolute-path run (`native-03/native-wiring.json`) reopened all nine families and both maps. These failed invocations are retained and are not counted as passes.

The first current-revision nine-motion run exited normally and observed all nine motions, but its supervisor rejected the replacement capture clip because it expected the old clip basename. The corrected checker requires the exact eight retained source paths plus `Visual_v003/Capture_v002/OseboCapture.OseboCapture`; old CaptureReach or same-named clips in other folders are rejected. The first failed result remains unchanged. A fresh supervisor execution is recorded separately under `leopard-nine-motion-02/`.

## Final executed result

- **367 Python tests passed**, full suite exit 0 (`python-tests-revision-final.log`).
- **34 native automation tests passed**, fresh report checked for expected identities and complete execution (`automation/unreal-automation/index.json`).
- **15 packaged sessions accepted**: one full seven-design cast loop; three corrected Aso Yaa loops with Kwaku/Ananse/leopard; one Ananse/leopard loop with negative selection cases; six route/outcome cases; cinematic lifecycle; two process restarts; and one fresh current-revision nine-motion leopard check. Earlier failed supervisor invocations remain excluded.
- Seven-design cast loop: 59 evaluated clip entries and 20 complete round trips per design. Corrected Aso: 16 clips and 20 round trips per base. Leopard: all nine required categories. Cross-family negative checks preserve the usable pawn and reject stale completions.
- **Nine current native asset families reopened**, each with a distinct skeleton and real generated pawn/animation classes. Both route worlds reopened. Eight characters have three saved LODs; Ananse retains one saved LOD. This is inventory, not reviewed mobile suitability.
- JavaScript syntax and changed Python-script compilation passed. Three launcher negative checks rejected profile escape, an outside-project package and a missing package. Launcher command generation was exercised for both scenes; human interactive play through the new launcher itself is not claimed.

| Design | Current definition revision | Saved LODs | New functional evidence |
|---|---:|---:|---|
| Kwaku | 11 | 3 | Full 11-clip loop, movement, switching, ledger and episode coverage |
| Aso Yaa | 5 | 3 | Corrected 16-clip contact loop with three bases, negotiation route |
| EsiHuman | 1 | 3 | Eight-clip loop, movement, 20 round trips |
| OseboHuman | 1 | 3 | Eight-clip loop, movement, 20 round trips |
| KojoTortoise | 1 | 3 | Eight-clip loop, movement, declared flat-contact metrics, 20 round trips |
| KofiHornbill | 1 | 3 | Eight-clip loop, movement, declared flat-contact metrics, 20 round trips |
| EsiMoth | 1 | 3 | Eight-clip loop, movement, 20 round trips; grounded-contact qualification not inferred |
| OseboLeopard | 7 | 3 | Nine evaluated motion categories, pursuit/route presentation, 20 cross-family round trips |
| AnanseSpider | 1 | 1 | Return/possession, movement, evaluated gesture and rebuilt four-leg contacts |

Machine-readable summary: `.local/verification/integration-audit-20261018/integration-summary.json`. Exact loaded classes, meshes, skeletons, physics, IK, Control Rig and Animation Blueprint paths: `native-03/native-wiring.json`. Per-stage commands and outcomes: `stages.json`, `cast/process.json`, `leopard-nine-motion-02/process.json`. Changed verification-source hashes: `verification-source-hashes.json`.

Final hashes confirm **1,586 native assets, 1,123 authored model files, 66 runtime/configuration files and all 39 frozen package payload files unchanged**. No art, native runtime code or cooked content changed; the existing candidate is retained rather than presenting an identical recook as new work. Original references, earlier failure evidence, rollback packages and publications remain preserved. No staged files or new commit.

**Next decision:** human review of the existing environment/character evidence and a bounded corrective art pass for outstanding defects. Functional wiring is verified within these scenarios; final refinements/polish are incomplete. Do not propagate Forest geometry or claim mobile/release acceptance from these results.
