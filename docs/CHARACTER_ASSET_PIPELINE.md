# Character, appearance and asset production

## Cultural and creative boundary

The two supplied briefs are design sources, not primary ethnographic validation or proof of commercial ownership. They explicitly describe a variable oral tradition, then overstate exclusive original-IP ownership over every name. This project must distinguish traditional figures and community knowledge from newly authored plot, models, dialogue and code. WIPO's work on traditional cultural expressions is a relevant rights framework; obtain project-specific cultural and legal review rather than treating every inherited motif as unrestricted [S12].

Use a paid Ghanaian/Akan cultural lead to establish the adaptation's scope, pronunciation, named traditions, restricted material and credits. Build an original story world with a specific cultural foundation rather than mixing unrelated West African and diaspora references as interchangeable fantasy decoration. Research is a production dependency, not a final sensitivity check. Record who reviewed each portrayal, which source/community it draws from, the agreed transformations and unresolved disagreement.

Kwaku is an **original young apprentice**, not automatically the traditional Kwaku Ananse himself. Ananse is a separate mythic role. Aso Yaa's marriage in some traditional versions does not automatically make her the player character's spouse: this adaptation proposes an independent strategist. Neither the catalogue nor this document certifies these choices as culturally approved.

## Complete seeded catalogue

All 16 entries are **concept metadata**, not finished meshes. The five marked Slice are the first art/voice production priorities; others remain staged backlog. A collective record is not several fully modelled actors.

| Record | Proposed adaptation role | Slice / representation |
|---|---|---|
| Kwaku, the Story-Binder | Courier/apprentice; player; cleverness with consequences | Yes / human |
| Aso Yaa, the Ledger-Keeper | Strategist; protects the people hidden behind transactions | Yes / human |
| Kojo of the Slow Road | Patient investigator; remembers incompatible claims | Yes / human, Turtle-inspired |
| Esi of the Drum Court | Performer who makes private evidence publicly meaningful | Yes / human |
| The Mmoatia Twins | Ambiguous spirit guides; paths and memory have prices | Later / collective spirit-inspired entry |
| Old Boatman Kofi | River guide and escape-route mentor | Later / human |
| The Weaver of Silence | Antagonist who imposes one authorised history | Later / human |
| Osebo, Captain of the Golden Guard | Enforcer whose obligations conflict with reputation | Yes / animal-inspired concept; final portrayal pending |
| Onini, Keeper of the Root Archive | Boundary and knowledge guardian; not generically evil | Later / serpent-inspired |
| The Hive of Mmoboro | Collective consequences of abusing community trust | Later / swarm/collective |
| Lady Adwoa of the Seven Markets | Merchant rival with credible public and private goals | Later / human |
| The Glass Mask Court | Legitimacy-manufacturing political collective | Later / collective |
| Ananse | Separate traditional trickster inspiration/mentor role | Research / mythic |
| Nyame | Distant authority, judgement and story ownership themes | Research / mythic |
| Tiger | Diaspora-associated optional research entry; excluded from base slice | Research / animal |
| Ananse's family | Responsibility/stakes research placeholder, not a defined child model | Research / collective |

The four asset entries (Kwaku body, Kwaku movement, market kit, drum-court score) are **planned inventory records without binary files**. The seed marks licences and reviews unresolved. Adding or updating an asset entry does not download a marketplace product.

## CRUD and modifications that exist

Create and duplicate characters, read/filter records, update strict JSON, add appearance variants, change colours and bounded visual scale, enter named morph weights, reference typed asset IDs, archive, restore, review, revert into a new revision and publish a fixed snapshot. Editing a character does not silently rewrite existing releases. Referenced entities cannot be archived until active dependencies are removed or deliberately migrated.

A character variant includes ID/label, body asset reference, animation asset reference, cloth/accent colours, visual scale in [0.8,1.2] and up to 16 morph targets in [0,1]. The studio canvas is an abstract procedural silhouette for draft metadata, **not a faithful 3D preview**. Native optional morphs work only when corresponding morphs exist on a compatible imported mesh; no morph geometry is manufactured from its name. Animation asset metadata are not yet bound into an Animation Blueprint. Native visual scale is separate from collision dimensions to avoid accidental gameplay changes.

## Production asset pipeline (proposed)

1. **Brief and evidence.** Character purpose, relationships, cultural sources, silhouette, age/representation, pronunciation, rights/consent, platform tier and review owner. Commission original work or acquire specific compatible licences. Never assume generative output has cleared rights.
2. **Concept approval.** Front/side/back turnarounds, expression sheet, costume layers, accessories, material references, mobility requirements and non-negotiable cultural details. Review before expensive modelling.
3. **DCC production.** Blender or approved DCC: high/low meshes, UVs, topology for deformation, packed PBR textures, rig/skeleton, skin weights, morphs, sockets, collision and authored LODs. Maintain source files, versioned exports and creator attribution.
4. **Animation.** Locomotion, turning, stops, jumps, ledge/traversal, reactions, conversations, ability montages, facial performance and Osebo pursuit. Retarget only after skeleton verification. Record root-motion and capsule assumptions. Licence/consent every voice or motion source.
5. **Unreal import.** Import under stable `/Game/Characters/...` paths. Create materials, physics assets, AnimBlueprints, montages, sockets, metadata/DataAssets and lookup contracts. Preview one base and two variants in an actual lit turntable and moving gameplay scene. Validate morph ranges, clipping, cloth bounds and silhouette readability.
6. **Automated and human checks.** Verify real asset bytes and hashes, licensing evidence, missing references, skeleton/animation compatibility, LOD screen sizes, texture mips, material slots, collision, bounds, bone count, cookability and runtime memory. Run physical-phone frame-time checks with the actual crowd composition.
7. **Release.** Independent cultural/art/technical review; exact revision and bytes approved; platform cook; signed compatible manifest; staged deployment and rollback. Reviews are invalidated or superseded when the relevant content changes.

Suggested first-pass budgets are **design hypotheses, not validated engine limits**: hero LOD0 around 30–45k triangles and at most four material slots; ordinary near NPCs around 8–15k triangles with lower LODs; 1–2K hero textures with mips and reduced distant detail; one dominant shadowed light and authored/baked baseline lighting. Hair, cloth, transparency, draw calls and skinning can dominate even when triangle counts look acceptable. Replace each hypothesis with measured per-device budgets before production approval.

Keep render-critical mobile content independent of a desktop-only Nanite/Lumen requirement. Epic's standard mobile feature table does not provide those features as the general mobile baseline [S11]. Desktop quality may scale up separately only when the same gameplay remains legible.

## Later creator/modding application

Do not expose staff asset administration to players. A player creator portal would need separate identity/permissions, moderation/reporting, licence declarations, malware/quota checks and a restricted declarative format. PC mods and mobile store content are different deployment surfaces. Never allow arbitrary Unreal packages, scripts, native libraries or asset URLs merely because CRUD exists. Player-facing modding, marketplace revenue sharing and generated-character import are **not implemented** in this starter.
