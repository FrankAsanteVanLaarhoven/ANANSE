# Production content and release guard

An additive change set for the existing ANANSE repository. Files here are authoring specifications and an evidence consistency checker, not meshes, recordings, Unreal assets or deployed services. It does not replace the existing mission-rule implementation or studio.

Read `docs/production/PRODUCTION_FINISH.md` and `docs/production/CODEX_EXECUTE.md`.

## Delivered

- 44 original English draft dialogue lines with stable IDs and performance notes.
- 18 cinematic shot definitions across six sequences.
- Nine mission beats, three routes and two existing outcome IDs.
- 24 audio cue briefs and 24 production animation task categories.
- Ten release domains and 36 required asset obligations, initially incomplete.
- A standard-library release-evidence checker with 54 synthetic/content-structure tests executed in the preparation environment.

The checker tests are not the repository's 66 historical tests and do not add native or mobile coverage. No combined total is claimed. Existing tests need rerunning after integration. No source/dependency files in the existing repository are replaced by this patch.

## Apply

Inspect the patch in the existing project and preserve user changes first:

```bash
git apply --check /actual/path/ANANSE_Production_Finish.patch
git apply /actual/path/ANANSE_Production_Finish.patch
```

Run the added tests using the project's isolated environment:

```bash
.venv/bin/python -m pytest -q tests/test_production_finish_gate.py
```

Do not run these example paths literally; use the downloaded patch's actual local path. These commands do not commit, push or deploy anything.

## Checker

A release evidence document uses the shape in `release_evidence.example.json`. Required file references have a repository-relative POSIX path and a lowercase SHA-256. References must resolve to nonempty regular files, not symlinks, escaped paths or unmaterialized LFS pointers. Gate proof JSON must bind release ID, source commit, content digest and gate ID, with a nonempty run ID, exit 0, no timeout/forced termination, required true assertions and hashed raw evidence.

Assets require a declared production quality, runtime file, rights file and art-review file. The checker does not parse a UAsset, verify legal ownership, identify the reviewer, attest the engine build or evaluate the art. Real runner/device and human review remain mandatory. Fabricated evidence remains a trust problem; passing this tool is only `evidence_consistent`, not a release certificate.

Example (expected exit 1 because the template contains no executed evidence):

```bash
.venv/bin/python scripts/production_finish_gate.py \
  --root . \
  --contract production/release_contract.json \
  --evidence production/release_evidence.example.json \
  --candidate-commit "$(git rev-parse HEAD)" \
  --out .local/verification/production-template-check.json
```

Choose a new `--out` path each time. Existing reports are never overwritten. Exit 0 means evidence is internally consistent; exit 1 means incomplete/invalid declarations; exit 2 means input or output errors. No network requests, installation, source mutation, signing, engine launch or publishing is performed.

Production evidence must be created from the actual candidate, not by modifying the example's booleans. Synthetic fixtures in the tests are deliberately fake evidence used to check the checker; do not use them in a release report.

## Integration

`market/*.json` is staging content. It has no automatic gameplay effect. Map it through an explicitly implemented, reviewed adapter into the existing mission/cinematic/localization/audio systems. Resolve speaker aliases against the catalogue. Preserve historical saves, published revisions and identity distinctions. Record imported assets and engine-side results separately.
