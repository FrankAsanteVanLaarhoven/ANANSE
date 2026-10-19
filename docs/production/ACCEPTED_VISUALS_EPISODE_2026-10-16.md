# Approved visuals — playable episode integration, 16 October 2026

The accepted Kwaku appearance now plays the existing episode from the market through pursuit, consequence and sanctuary completion. The six route/outcome cases and two separate restart cases passed in one new Linux package. Osebo remains the original human campaign pursuer; the leopard stays a separate selectable design. This is a development checkpoint, not a final release candidate.

Branch `feature/local-milestone-verification`; HEAD `ec7bf0bcf16634a13c12e92433e9731064890e80`. Newer work remains uncommitted. No commit, push, merge, publication, deployment, tool installation or unrelated system changes.

## Approval and scope

[User approval record](VISUAL_APPROVAL_2026-10-16.json) records the exact statement “visuals are fine carry on with game developmemt”, scoped to continued development with Kwaku035/Osebo021. It does not claim uploaded-image inspection or approve commercial release, species remapping, dynamic cape deformation, memory stability or physical devices. Historical Pass-2 matrices and failures remain intact.

Four new assets, without modifying the previous meshes, skeletons, rigs, clips, physics or map files:

- `/Game/Ananse/Characters/Kwaku/EpisodeAccepted_v001/BP_KwakuAcceptedEpisode.BP_KwakuAcceptedEpisode_C`
- `/Game/Ananse/Characters/Kwaku/EpisodeAccepted_v001/BP_KwakuAcceptedEpisodeMode.BP_KwakuAcceptedEpisodeMode_C`
- `/Game/Ananse/Maps/EpisodeAccepted_v001/L_Market_AcceptedVisuals`
- `/Game/Ananse/Maps/EpisodeAccepted_v001/L_Sanctuary_AcceptedVisuals`

The pawn reuses `/Game/Ananse/Characters/Kwaku/ArtPass2_v003/Kwaku.Kwaku`, the existing46-bone skeleton,11 clips/Animation Blueprint, contact controller and ledger component. It retains Kwaku identity, normal campaign powers, collision and movement authority. Existing route/mission/pursuit/cinematic/save systems remain authoritative. `-AnanseAcceptedVisuals` selects the new map/travel binding and prevents the older published mesh from replacing this approved appearance. Exact mesh/class and non-lab campaign ownership are asserted during gameplay.

The isolated default save slot is `AnanseAcceptedEpisode_v1`. Legacy `AnansePrototype`, other character slots and the existing save schema remain unchanged. Explicit test slots are separate. Older saves are not silently migrated or overwritten. No catalogue publication changed.

## Changed source and verification

Native changes: `AnanseCastLab.cpp` (appearance guard), `AnanseMission.cpp` (map selection), `AnanseRuntimeVerification.cpp` (isolated default slot), `AnansePursuitVerification.cpp` (actual mesh/identity assertions), `AnanseAcceptedEpisodeTests.cpp` (two new tests). Authoring/supervision: `scripts/build_accepted_episode.py`, `scripts/unreal.py`, `scripts/native_runtime_smoke.py`; two Python map-preflight tests in `tests/test_accepted_episode.py`.

[Exact path/hash delta](../../.local/verification/accepted-episode-20261016/changed-paths.json) · [frozen cook inputs](../../.local/verification/accepted-episode-20261016/inputs-01.json) · [native market binding](../../.local/verification/accepted-episode-20261016/native-0-retry/native.json) · [native sanctuary binding](../../.local/verification/accepted-episode-20261016/native-1/native.json).

296Python tests passed;30native tests passed (28with the existing SDL initialization warning), with fresh nonzero reports and no assertion/identity/threshold removal. JavaScript syntax check passed. Tests ran after implementation and before cooking. [Python result](../../.local/verification/accepted-episode-20261016/python-final.log) · [native report](../../.local/verification/accepted-episode-20261016/native-tests-01/unreal-automation/index.json) · [native command and exit](../../.local/verification/accepted-episode-20261016/native-tests-01-supervisor.log).

The rendered pre-cook preview passed the negotiation route, ten capture/retry cycles, consequence, actual sanctuary travel and completion. Fresh packaged results:

| Scenario | Result | Active seconds |
|---|---|---:|
| negotiation-protect | PASS | 61.521 |
| negotiation-expose | PASS | 61.518 |
| social-protect | PASS | 61.541 |
| social-expose | PASS | 61.517 |
| rooftop-protect | PASS | 61.507 |
| rooftop-expose | PASS | 61.511 |
| restart-before-choice | PASS | 61.506 |
| restart-sanctuary | PASS | 61.486 |

Each of the six complete routes includes ten real capture/retry cycles, played escape, visible consequence/dialogue, actual map travel and epilogue completion. Reload processes verify saved state, position, controls, absence of stale pursuer and non-repetition of durable events. Before-choice restart restores the pending choice with outcome unset; it is not misreported as a completed protected-witness outcome. Sanctuary restart restores the saved arrival beat. Cross-family regression separately passed20round trips/40committed transitions and7negative cases in this same package.

[Executed package stages](../../.local/verification/accepted-episode-20261016/package-01/stages.json) · [delivery record](../../.local/verification/accepted-episode-20261016/delivery.json) · [cross-family report](../../.local/verification/accepted-episode-20261016/package-01/cross-family/result.json). Native simulated input is not physical keyboard/controller/touch coverage. No new terrain qualification is claimed; original art/contact assets remain unchanged.

## Fresh package, identity and launch

Package `/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261016T183031.018405Z`. ELF SHA-256 `bf1c670eaf940873be7b1ce3cfa5239ae69baa87e802705be6ea82476e2109f4`. Prelaunch payload manifest SHA-256 `9e3e05535cee08d95e2bf8f6945378fe92c46e817214409ece16e0b4ee057043`; full file hashes are in [payload-before.json](../../.local/verification/accepted-episode-20261016/payload-before.json).

Native source/config `1fef8073598b4d74aa3d51e6be8c4f5821e76d4fce38816a715cb243eade318c`; native content `97896678a3c39c9d4cce633aafa59fce52af7c398f45215c291c6e52ac3e4780`; authoring scripts `f18f82ee20565ef05c9f543e864f8c96c8454c07b0a68580df36b9e2208d43bf`; models `6e60ed7639a0018187225881f43eb7503156365009062b5f97aae102d07db888`. These identify the uncommitted build inputs, not the entire repository solely through its old commit. UE5.8.3/changelist58210709; existing qualified Blender4.5.14 sources unchanged. [Cook command/log](../../.local/verification/accepted-episode-20261016/cook-01-supervisor.log).

```bash
"/home/favl/Downloads/ANANSE_Production_Starter/Builds/Linux/20261016T183031.018405Z/Ananse/Binaries/Linux/Ananse" /Game/Ananse/Maps/EpisodeAccepted_v001/L_Market_AcceptedVisuals -AnanseAcceptedVisuals -AnanseEpisode -AnanseStoryPresentation -AnanseArtRefinement -AnanseFormsScenery -AnanseInteractionRefinement -ansimalloc -windowed -ResX=1280 -ResY=720 -UserDir="/home/favl/Downloads/ANANSE_Production_Starter/.local/accepted-episode-player-profile"
```

This uses the same executable/map/presentation flags as the executed package tests, with verification automation omitted and a separate player profile. N starts New Game, C continues, E interacts,1/2/3 invoke permitted powers, F5 saves, F9 loads, Escape pauses/skips the active presentation. The inherited menu behaviour has not been newly qualified by physical input in this milestone.

[Genuine sanctuary completion capture](../../.local/verification/accepted-episode-20261016/package-01/negotiation-protect/native-game.png). Further route/restart screenshots are stored beside their native reports. These are actual game captures; environment/UI labels still identify development content.

## Preservation and remaining work

[Preservation audit](../../.local/verification/accepted-episode-20261016/preservation.json): all880previous native assets and878model files unchanged; frozen source/content/model/script bytes match the cook; original171420rollback39payload files and new39payload files unchanged; catalogue publication, commit and empty index preserved. Original reference manifests, matrices, review ZIP and saved scenes remain intact.

Failures retained: build01 rejected an unparenthesized logical expression; native authoring0 stopped at an incorrect reflected property name before producing a complete map. The compiler grouping/property spelling were corrected; the partial pawn bytes and failure logs remain in evidence. Neither failure is counted as a successful qualification.

The allocator workaround remains `-ansimalloc`; detailed CPU-trace shutdown failure remains unresolved. Frame traces do not imply full CPU/GPU profiling or phone performance. Final audio/voice/music, environment/cinematic polish, Aso Yaa/remaining character review, dynamic cape motion, wider navigation/terrain, long-session memory and Android/iOS device qualification remain open. No online service is deployed.

Next bounded development: negotiation-character/presentation integration using the existing Aso Yaa draft and authored dialogue; keep canonical identities and current mechanics intact.
