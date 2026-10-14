# ANANSE: Kingdoms of the Story Road
## Production starter v0.1.0 — evidence-led prototype, not a released game

Cinematic social-stealth action adventure in an original mythic West African world. As a young Story-Binder, the player changes who is believed, who is remembered and who holds power.

**Delivery status, 13 October 2026:** the local content service and deterministic mission-rule laboratory have executed tests. The Unreal 5.8 C++ greybox integration is authored but **has not been compiled or played**. Production meshes, animation, audio, mobile packages, cloud services and a finished cinematic mission are **not included**. Browser UI code is supplied, but browser validation was blocked by the execution environment. No claim of enterprise release readiness or virality is made.

### Start here

| File | Purpose |
|---|---|
| `docs/CRITIQUE_AND_BUILD_PLAN.md` | Decisions, scope, design, research process, staffing assumptions and SMART gates |
| `docs/SETUP.md` | Python, Windows/Linux/macOS Unreal installation, publishing/export, native builds and troubleshooting |
| `docs/ARCHITECTURE.md` | Working APIs, trust boundaries, contracts and production migration |
| `docs/CHARACTER_ASSET_PIPELINE.md` | All seeded characters, appearance modifications, asset production and approval |
| `docs/TEST_AND_RELEASE_GATES.md` | Test evidence, engine/device checks and release criteria |
| `docs/SOURCES.md` | Primary technical sources and research references checked for this delivery |
| `evidence/BUILD_STATUS.json` | Machine-readable implementation/verification status |
| `AGENTS.md` | Safe, bounded coding-agent execution instructions |

### Local quick start

Use a Python 3.13 virtual environment. The requirements file pins the versions used in this runtime; it is **not a hash-locked, independently security-audited supply chain**. Windows/macOS dependency installation has not been tested here.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
python -m pytest -q --junitxml=.local/verification/manual/pytest.xml
python scripts/http_smoke.py
python scripts/studio.py
```

Windows PowerShell: replace the first two commands with `py -3.13 -m venv .venv` and `.\.venv\Scripts\Activate.ps1`. Follow your organisation's execution policy; do not disable it globally. Alternatively call `.\.venv\Scripts\python.exe` directly.

Open `http://127.0.0.1:8765`. The launcher generates three different role tokens in `.local/credentials.json`. Read the file privately, paste only the **editor** value into the UI, and connect. Never share credentials or commit `.local`. The browser keeps the entered token in memory, not local storage.

Select Kwaku, edit a colour or appearance variant, and save. Revisions and references are enforced server-side. Connect with the reviewer token for reviews and publisher token to publish an immutable **prototype** snapshot. These are development roles, not independently verified human identities. Production publishing is intentionally refused.

Try **Story laboratory → New run → Inspect altered edict → Negotiate → Enter archive → Recover ledger → Protect witnesses**. The laboratory is a deterministic rules prototype, **not a 3D game or proof of player enjoyment**.

### Bridge to Unreal

After publishing, copy the publication ID displayed in the studio:

```bash
python scripts/export_content.py --publication PUBLICATION_ID
# Install UE 5.8 using Epic's official process first; set UE_ROOT to its actual directory.
python scripts/unreal.py doctor
python scripts/unreal.py lock-engine
python scripts/unreal.py build
python scripts/unreal.py bootstrap
python scripts/unreal.py test
python scripts/unreal.py open
```

`PUBLICATION_ID` is a placeholder to replace. The export is a build-time snapshot, not a live database connection. The generated map and prototype material do not exist until the **unverified** editor bootstrap succeeds. Build errors must be corrected against the installed engine and recorded before calling this playable.

Controls authored in source: WASD/gamepad movement, mouse/right-stick camera, Space jump, E interaction, 1 Web Step, 2 Borrowed Voice, 3 Trick Mirror, F5/F9 local save/load, R restart. Touch joysticks and debug buttons require device validation. `python scripts/unreal.py open --variant festival` selects Kwaku's other seeded concept variant.

### Repository

```text
studio/             FastAPI, transactional SQLite, schemas, static content UI, rule laboratory
content/seed.json   16 character/archetype records; 7 factions; 1 mission; 4 planned asset entries
Unreal/             C++ project, native configurations, two authored automation tests
scripts/            studio launcher, exports, backups, build helpers and smoke tests
tests/              positive and adversarial API, rule and build-helper tests
docs/               production design and setup contracts
evidence/           executed-test reports and explicit blockers
.github/workflows/  authored CI configurations, not remotely executed in this delivery
```

### Scope and limits

The studio performs CRUD on **metadata**, not mesh sculpting, rigging or waveform editing. Its stand-in canvas is deliberately labelled as non-production art. Unreal source consumes names, selected appearance fields, permitted power IDs and compatible soft mesh references. A catalogue field is not automatically a complete gameplay feature: mission authoring, animation bindings, dialogue, faction simulation, UGC and assets still need dedicated implementation.

Do not expose this server to the internet. Do not treat audit hashes as externally anchored tamper-proof storage. Do not use local saves as authority for purchases, shared economies or achievements. No Unreal binaries, commercial asset packs, signing keys, external deployment or store submission are supplied.

To back up the studio while it is running:

```bash
python scripts/backup_studio.py --out BACKUP_PATH.sqlite3
```

Keep release snapshots immutable. Restore historical content through a **new revision**. Before engine upgrades, archive evidence, review compatibility, and explicitly update the engine pin; never silently replace an installed toolchain.

### Local verification — 14 October 2026

Fresh results and the bounded native blockers are documented in `docs/LOCAL_VERIFICATION_2026-10-14.md`. The supplied `evidence/` remains historical and unchanged. Smoke/build helpers now default to timestamped directories under `.local/verification/`; `--out` (smoke scripts) and `--evidence-dir` (native helper) select an explicit fresh directory.

Verification artifacts in `evidence/` and `.local/verification/` remain local and are excluded from Git. The authored handoffs record their results and paths; a fresh checkout must reproduce the checks.
