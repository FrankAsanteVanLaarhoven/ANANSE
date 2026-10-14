# ANANSE: Kingdoms of the Story Road
## Critical review and production build plan — 13 October 2026

**Verdict:** retain the premise and Unreal direction, but replace “large cinematic mobile game plus enterprise CRUD plus virality” with a sequence of independently testable products: a content-authoring system, a native mechanical slice, a culturally reviewed cinematic slice and a measured commercial release. A tools backend is not a finished game. An engine project is not a successful native build. Virality is a hypothesis, not a build property.

This plan is based on the two uploaded design briefs. Their roster, three powers, Market of Stolen Names mission and Android-first direction are retained. The additional mechanics, architecture, schedules and thresholds below are **proposals**, not facts contained in those briefs or observed player results. External technical facts are sourced in SOURCES.md; original research attribution is included where relevant.

## 1. Critique before expansion

The core differentiation is promising: a player does not simply win battles, but manipulates who believes what and must live with the consequences. The Weaver of Silence is a stronger thematic antagonist than treating every powerful animal archetype as an evil boss. The briefs already support these themes.

The implementation brief has seven weaknesses.

**Unresolved platform promise.** One brief targets flagship phones at 30 fps with optional 60 fps; another makes stable mid-range performance the initial target. Name two actual Android test devices at project inception, with an agreed resolution preset and thermal protocol. Prove 30 fps first. Optional 60 fps is an independent quality tier, not a marketing commitment.

**Scope contradiction.** The first brief says co-op later, but its budget table lists 1–4 players in the first release. Adopt offline-capable single-player for the slice; asynchronous sharing comes after gameplay works; co-op is a separately funded phase. Do not quietly inherit server-authority and network-prediction complexity.

**Schedule contradiction.** The source alternates between eight-week, ten-week and sixteen-week milestones without a scoped staffing model or existing implementation evidence. Replace dates-as-promises with gates. The illustrative programme below is not an estimate of a complete AAA game.

**Mechanics are named rather than specified.** “Borrowed Voice” needs prerequisites, duration, observation scope, contradiction handling and failure feedback. “Web Step” needs collision-safe anchors, range and cancellation. “Trick Mirror” needs explicit effects on witnesses rather than arbitrary invisibility. The source names alone do not establish working mechanics.

**Culture and ownership are under-specified.** Traditional names and contemporary adaptations do not automatically become exclusively owned original IP because they appear in a new game. Establish paid cultural leadership, source and licence ledgers, performer consent and an adaptation bible before final character art [S12].

**Tool rankings substitute for evidence.** The supplied AI-agent/model rankings are not reproducible performance benchmarks. One primary repository agent and one reviewer are sufficient initially. Use actually available tool/model configurations, bounded branches and compiler/test feedback. Installing many agents does not create art direction or production readiness.

**“Fully wired” lacks an observable contract.** The essential integration test is: edit a character -> validate references -> review a revision -> publish -> export -> cook -> see the exact version in the native game -> save/reload -> roll back safely. This starter implements the authoring/export portion and supplies native source, but has not completed the native demonstration.

### SWOT

Strength: narrative power, social deception and mythic traversal can reinforce a distinctive identity. Weakness: premium animation, cultural specificity and mobile performance all require sustained specialist work. Opportunity: replayable solutions and legible consequences can create original player stories and creator discussion. Threat: scope inflation, generic cultural blending, unlicensed assets, opaque rules and device/store-toolchain churn. The opportunities are testable commercial hypotheses, not market-size or revenue claims.

## 2. Product definition: who, what, where, when, why and how

**Who:** initial players are people interested in third-person traversal, infiltration, political storytelling and replayable choices; these are proposed audience segments, not validated demographic findings. Staff users are designers, writers, artists, technical artists, QA, cultural reviewers and release managers. Those roles need different permissions.

**What:** a compact premium-feeling social-stealth adventure with an original Story-Binder protagonist. The first proof is one 12–15-minute mission with three meaningful routes, two morally costly outcomes and one memorable pursuit sequence. The current source greybox is materially less than that polished proof.

**Where:** one dense market/archive district first, then a river route, forest settlement, royal court and coastal port as separately scoped chapters. Native Android is the first device-performance gate; desktop is useful for rapid iteration. iOS follows compatible Mac/Xcode validation. Console certification and co-op are not in the slice.

**When:** begin with environment, culture and native integration gates. Expand only after the current slice is fun, legible, stable and reproducible. The programme below assumes funded specialists and must be revised using actual throughput.

**Why:** make cunning materially change access, alliances and consequences rather than merely replace a lockpick animation with dialogue.

**How:** bounded rule-based social simulation; explicit evidence and belief; authored traversal; a restrained combat toolkit; high-fidelity stylisation; immutable versioned content; native testing; independent cultural review; player studies tied to specific hypotheses.

## 3. The game that should be built

### Core loop

Observe a situation -> identify a claim and the people who might believe it -> gather evidence or leverage -> choose a plan -> use movement, negotiation or deception -> react when someone challenges the story -> escape or repair the damage -> witness changed relationships and public consequences.

Make the loop readable without a large tutorial. Every meaningful deception should reveal its prerequisite and likely audience before use, then show who accepted it and what could expose it. Preserve uncertainty about consequences without hiding basic rules.

### Three layers of narrative state

**World fact:** the royal edict has been altered; the ledger contains witness names. **Individual belief:** one guard accepts Kwaku as a courier, while Kojo has evidence to the contrary. **Public narrative:** Esi's performance has made a specific account credible across the market. These layers must not collapse into a universal “reputation score” or omniscient NPC knowledge.

Represent a claim with subject, proposition, source, evidence links, who observed it, confidence, expiry and contradiction links. Propagate only through explicit events and bounded social neighbourhoods. Keep a small, inspectable active cast before scaling crowds. This is a proposed production design; the current laboratory contains only a deliberately reduced instance.

There is established research precedent for authored, reusable social rules: McCoy, Treanor, Samuel, Wardrip-Fruin and Mateas (2011), *Comme il Faut: A System for Authoring Playable Social Models*, DOI **10.1609/aiide.v7i1.12454** [S13]. That precedent supports an authorable social-model approach; it does not establish ANANSE's novelty, fun or superiority. No live LLM should adjudicate the authoritative mission state. AI may assist drafts and authoring behind review, not invent irreversible gameplay outcomes at runtime.

### Powers with counterplay

| Power | Proposed production contract | Current source boundary |
|---|---|---|
| Web Step | Authored anchor, range/visibility/collision checks, clear landing preview, interrupt/recovery policy | Intended swept arc and anchor logic; not played or physics-validated |
| Borrowed Voice | Learn a specific authorised call, bounded duration and audience, fails under contradictory evidence | Laboratory claim rules and native timed dispatch; no real voice synthesis/finished audio |
| Trick Mirror | Place a temporary decoy that redirects specific witnesses; does not erase evidence | Laboratory distraction state and native stand-in effect; no finished AI/FX |

Use a small resource budget to encourage combinations rather than unlimited ability spam. A failed con should create an interesting recovery route, not always an instant reset. Combat should initially be readable evasion, disruption and non-lethal escape; deep weapon loot, boss trees and hundreds of attacks would dilute the first proof.

### Market of Stolen Names: proposed cinematic mission

**Opening, roughly the first minute:** Kwaku arrives during a public performance as guards replace a market family's name on a royal notice. Aso identifies a discrepancy; the player physically inspects it rather than watching a long exposition sequence.

**Investigation:** the player can learn the captain's call, obtain a legitimate obligation-backed permit or discover an upper archive approach. Kojo notices inconsistencies. The player sees that social evidence is as actionable as a rooftop ledge.

**Infiltration:** the borrowed-call route tests a temporary identity; the negotiation route creates a promise with later cost; the rooftop route combines Web Step and Trick Mirror rather than bypassing the social system entirely. Each route supplies a distinct camera/animation moment without requiring a separate full level.

**Reversal and pursuit:** the recovered ledger reveals both a forged history and the names of vulnerable witnesses. Osebo closes the ordinary exit. The intended chase uses market canopy, a drum procession and a constrained escape route; it is **not implemented** by the current stationary watcher.

**Decision:** publishing the ledger undermines the regime but exposes witnesses; withholding it protects witnesses while delaying public proof. A negotiated promise changes the cost of betrayal. Esi and Aso respond differently. The immediate scene changes visibly, and a later chapter can respect the same recorded outcome.

The entire proposed mission needs no procedural open world to feel consequential. Animation, staging, spatial design, sound and feedback must carry the drama; a numerical reputation change alone is not enough.

### Engagement and sharing experiments

Propose an optional “Story Receipt” after the mission: your route, who believed you, the promise you kept or broke and the consequence. An optional replay/photo clip can be attached after explicit player action, with spoilers and identifying information controlled. Do not automatically upload voice, gameplay or personal data.

Replay must record enough events and spatial transforms for its advertised fidelity. A seed alone does not establish deterministic Unreal physics. Actual replay recording, rendering, editing and sharing are future features, not present in this kit.

Test whether players voluntarily replay for another outcome and whether actual shares lead to another person's interest. Do not substitute share-button impressions for completed shares, or paid impressions for organic growth. A premium demo or chapter unlock is a coherent monetisation hypothesis for testing; advertising, loot boxes, subscriptions, competitive economies and UGC marketplaces are out of the first proof. No forecast of sales or virality is asserted.

## 4. Build order and staffing assumptions

A planning example is a 20-week gated programme with roughly six overlapping specialist functions: game direction/production, Unreal gameplay engineering, backend/tools engineering, technical art/animation, environment/character art and QA/UX. A paid cultural/narrative lead and audio/performance specialists are additionally required, not free “AI replacements.” Individuals may cover more than one role, but the capacity reduction must be reflected in scope. This is not a cost quotation or a guarantee that six people can deliver a commercial AAA title in twenty weeks.

| Gate | Illustrative timing | Required evidence; do not advance without it |
|---|---|---|
| G0: foundation | Weeks 1–2 | Cultural brief, selected physical devices, exact engine pin, reproduced studio tests, native compile and baseline package |
| G1: mechanical slice | Weeks 3–6 | Three complete native routes; save/reload; shared rule fixtures; edit-to-cook appearance/power change; no progression softlocks |
| G2: readable player loop | Weeks 7–8 | First novice study; clear goals, understandable beliefs/counterplay; recorded failure analysis |
| G3: cinematic slice | Weeks 9–12 | Reviewed hero assets, AnimBlueprints, UMG, sound, localised strings, authored pursuit, two staged outcomes |
| G4: device qualification | Weeks 13–16 | Sustained physical-device performance, lifecycle tests, crash evidence, Android toolchain/store compliance verification |
| G5: commercial experiment | Weeks 17–20 | Consent-based closed test, replay/share instrumentation, sufficiently sized stability sample and release/rollback rehearsal |

Where a gate fails, reduce scene complexity or refine the design rather than reporting the date as completion. Do not add a second kingdom, co-op or player modding to hide a weak first mission.

## 5. Seven SMART success measures

All thresholds below are **proposed acceptance targets**, not current measurements, published industry benchmarks or guarantees. Define devices, test population and telemetry before collection. Report numerator, denominator and uncertainty; do not call a small pilot statistically conclusive.

| KPI | Measurement and gate |
|---|---|
| Gameplay comprehension | By G2, at least 24/30 first-time participants identify their goal and correctly explain why one deception succeeded or failed, using a predefined interview rubric |
| Sustained performance | By G4, on each of two named Android devices, a repeatable 20-minute mission run at the agreed resolution has p95 frame time no greater than 33.4 ms and at most 1% of frames above 50 ms; record thermal state and repeat three times |
| Reliability | By G5, at least 99.5% crash-free foreground sessions across at least 1,000 consented test sessions; report ANRs separately, device/OS breakdown and confidence intervals |
| Voluntary replay | By G4/G5, at least 30% of 50 or more eligible mission completers voluntarily start another route within seven days without a forced reward; log denominator and re-entry |
| Meaningful sharing | By G5, at least 10% of 200 eligible consenting completers successfully complete the optional sharing flow; track resulting visits separately and respect platform privacy limitations |
| Release traceability | At every release gate, 100% of runtime-referenced assets have verified bytes, compatible cook evidence, licence/creator records and required cultural/art/technical approval for that exact revision |
| Mutation/security integrity | Every pull request passes all defined negative role, stale-write, dependency and publication tests with zero unexpected authorisations; before any internet deployment, add independent security and restore/load tests |

The performance threshold is rounded slightly above the 33.33 ms frame interval for 30 fps; it remains a proposed acceptance definition, not proof of acceptable perceived pacing. The project has no actual device or participant results yet.

## 6. Scientific/engineering process and results

**Hypotheses.** H1: evidence-dependent social routes are comprehensible and motivate replay. H2: one dense native market can meet the selected 30 fps target. H3: revisioned authoring and immutable publication can prevent stale edits and broken content references within the local prototype boundary.

**Experimental design.** H1 requires consented novice playtests and the stated rubric. H2 requires repeatable physical-device traces with defined settings. H3 is tested through fresh temporary databases, positive and adversarial API cases, canonical content hashes and a real HTTP process restart. Browser, Unreal and player tests are separate evidence categories.

**Initial results.** The recorded local Python suite and real HTTP workflow pass; see evidence/BUILD_STATUS.json and their raw reports for final counts. They support a limited H3 result: exercised authoring and rule flows work in this runtime. H1 and H2 have not been tested. No native frame rate, finished character asset or player engagement result is claimed.

**Failures and challenges.** Browser validation could not load the UI because the environment's Chromium policy blocked navigation. The engine preflight reports no Unreal installation. The briefs contain incompatible scope/schedule targets and Epic's SDK recommendation differs from current Play submission policy. The initial test suite also did not cover every build/export precondition.

**Refinement.** Added explicit role separation and revision checks, fresh-output packaging, immutable export validation, preflight failure reports, server-restart checks and documentation separating metadata from real assets. Preserved browser/engine failures instead of relabelling them as success. No policy bypass was attempted.

**Further experiments.** Reproduce the browser workflow on an authorised local machine; compile and fix UE integration; run native automation and three route playthroughs; verify content edits after cooking; create shared laboratory/native conformance fixtures; then run the device and player experiments.

**New insight.** The primary development risk is not selecting another coding model. It is the gap between editable metadata, authored mechanics, real audiovisual assets and measured native experience. Each boundary needs its own evidence.

**Final conclusion.** This delivery establishes a useful tested local authoring/rules foundation and an explicit route to a native vertical slice. It does not establish a complete enterprise gaming release, state-of-the-art gameplay or viral demand. The immediate next milestone is one independently reproducible native edit-to-play demonstration, followed by a measured Android build.
