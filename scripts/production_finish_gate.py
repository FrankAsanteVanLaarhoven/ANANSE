#!/usr/bin/env python3
"""Check candidate-bound ANANSE release evidence. No builds, downloads or uploads.

This is a consistency guard, not an engine test, art reviewer, identity verifier,
security audit or signature verifier. A fabricated proof can still lie; acceptance
requires review of real runner/device evidence and an authorised release decision.
Exit: 0 consistent ready declarations; 1 incomplete/invalid evidence; 2 input error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
LFS_PREFIX = b"version https://git-lfs.github.com/spec/v1"


def load_json(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    def constant(value: str) -> None:
        raise ValueError(f"non-finite JSON constant: {value}")
    value = json.loads(path.read_text(encoding="utf-8-sig"),
                       object_pairs_hook=pairs, parse_constant=constant)
    if not isinstance(value, dict):
        raise ValueError("JSON document must be an object")
    return value


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def validate(contract: dict[str, Any], evidence: dict[str, Any], root: Path,
             expected_commit: str) -> dict[str, Any]:
    errors: list[str] = []
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("root must be a directory")
    if not isinstance(expected_commit, str) or not HEX40.fullmatch(expected_commit):
        raise ValueError("candidate commit must be a full lowercase 40-character Git SHA")
    if type(contract.get("schema_version")) is not int or contract["schema_version"] != 1:
        raise ValueError("unsupported contract schema")
    release_id = contract.get("release_id")
    if not isinstance(release_id, str) or not release_id.strip():
        raise ValueError("missing release_id")
    specs = contract.get("gates")
    asset_ids = contract.get("required_asset_ids")
    if not isinstance(specs, list) or not specs or not isinstance(asset_ids, list) or not asset_ids:
        raise ValueError("non-empty gates and required_asset_ids are mandatory")
    gate_ids: set[str] = set()
    for spec in specs:
        if not isinstance(spec, dict):
            raise ValueError("gate spec must be an object")
        gid, checks, minimum = spec.get("id"), spec.get("required_checks"), spec.get("min_tests_executed")
        if not isinstance(gid, str) or not gid or gid in gate_ids:
            raise ValueError("gate IDs must be non-empty and unique")
        gate_ids.add(gid)
        if (not isinstance(checks, list) or not checks or
                any(not isinstance(c, str) or not c for c in checks) or len(set(checks)) != len(checks)):
            raise ValueError(f"{gid}: required_checks must be non-empty unique strings")
        if type(minimum) is not int or minimum < 1:
            raise ValueError(f"{gid}: positive integer min_tests_executed required")
    if any(not isinstance(i, str) or not i for i in asset_ids) or len(set(asset_ids)) != len(asset_ids):
        raise ValueError("required_asset_ids must contain unique non-empty strings")
    if type(evidence.get("schema_version")) is not int or evidence.get("schema_version") != 1:
        errors.append("unsupported evidence schema")
    if evidence.get("release_id") != release_id:
        errors.append("release_id mismatch")
    if evidence.get("source_commit") != expected_commit:
        errors.append("candidate source_commit mismatch")
    if evidence.get("dirty_tree") is not False:
        errors.append("candidate must declare a clean source tree; this guard does not query Git")
    content = evidence.get("content_sha256")
    if not isinstance(content, str) or not HEX64.fullmatch(content):
        errors.append("content_sha256 must be a full SHA-256")

    def file_ref(ref: Any, context: str) -> Path | None:
        if not isinstance(ref, dict):
            errors.append(f"{context}: missing file reference")
            return None
        name, sha = ref.get("path"), ref.get("sha256")
        if not isinstance(name, str) or not name or "\\" in name or ":" in name:
            errors.append(f"{context}: invalid relative path")
            return None
        rel = PurePosixPath(name)
        if rel.is_absolute() or ".." in rel.parts or not rel.parts:
            errors.append(f"{context}: path escapes root")
            return None
        if not isinstance(sha, str) or not HEX64.fullmatch(sha):
            errors.append(f"{context}: invalid SHA-256")
            return None
        try:
            # Reject symlinks throughout the chain, not just those resolving out.
            path = root
            for part in rel.parts:
                path = path / part
                if path.is_symlink():
                    raise ValueError("symlink file references are not accepted")
            path = path.resolve(strict=True)
            path.relative_to(root)
            if not path.is_file() or path.stat().st_size == 0:
                raise ValueError("empty or non-file evidence")
            with path.open("rb") as stream:
                if stream.read(len(LFS_PREFIX)) == LFS_PREFIX:
                    raise ValueError("unmaterialized Git LFS pointer")
            if digest(path) != sha:
                raise ValueError("SHA-256 mismatch")
            return path
        except (OSError, ValueError, RuntimeError) as exc:
            errors.append(f"{context}: {exc}")
            return None

    gates = evidence.get("gates")
    if not isinstance(gates, dict):
        errors.append("gates must be an object")
        gates = {}
    for unexpected in sorted(set(gates) - gate_ids):
        errors.append(f"unknown gate: {unexpected}")
    for spec in specs:
        gid = spec["id"]
        row = gates.get(gid)
        if not isinstance(row, dict):
            errors.append(f"{gid}: missing gate")
            continue
        if row.get("status") != "pass":
            errors.append(f"{gid}: status is not pass")
        n = row.get("tests_executed")
        if type(n) is not int or n < spec["min_tests_executed"]:
            errors.append(f"{gid}: insufficient executed checks")
        checks = row.get("checks")
        if not isinstance(checks, dict):
            checks = {}
        for check in spec["required_checks"]:
            if checks.get(check) is not True:
                errors.append(f"{gid}: missing/failed check {check}")
        refs = row.get("proofs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"{gid}: no proof files")
            continue
        proved: set[str] = set()
        for ref in refs:
            path = file_ref(ref, gid)
            if path is None:
                continue
            try:
                proof = load_json(path)
                for key, expected in (("gate_id", gid), ("source_commit", expected_commit),
                                      ("content_sha256", content), ("release_id", release_id)):
                    if proof.get(key) != expected:
                        raise ValueError(f"proof {key} mismatch")
                if not isinstance(proof.get("run_id"), str) or not proof["run_id"].strip():
                    raise ValueError("proof requires a non-empty run_id")
                if proof.get("status") != "pass":
                    raise ValueError("proof status is not pass")
                if type(proof.get("exit_code")) is not int or proof["exit_code"] != 0:
                    raise ValueError("proof exit_code is not zero")
                if proof.get("timed_out") is not False or proof.get("forced_termination") is not False:
                    raise ValueError("proof must exclude timeout and forced termination")
                actual = proof.get("assertions")
                if not isinstance(actual, dict):
                    raise ValueError("proof assertions must be an object")
                proved.update(k for k, value in actual.items() if value is True)
                raw = proof.get("raw_files")
                if not isinstance(raw, list) or not raw:
                    raise ValueError("proof requires hashed raw evidence files")
                for raw_ref in raw:
                    file_ref(raw_ref, f"{gid}/raw")
            except (OSError, ValueError) as exc:
                errors.append(f"{gid}: {exc}")
        missing = set(spec["required_checks"]) - proved
        if missing:
            errors.append(f"{gid}: required assertions not covered by proofs: {', '.join(sorted(missing))}")
    assets = evidence.get("assets")
    if not isinstance(assets, dict):
        assets = {}
        errors.append("assets must be an object")
    for asset_id in asset_ids:
        asset = assets.get(asset_id)
        if not isinstance(asset, dict):
            errors.append(f"{asset_id}: missing required asset")
            continue
        if asset.get("quality") != "production":
            errors.append(f"{asset_id}: quality is not production")
        for kind in ("runtime", "rights", "review"):
            file_ref(asset.get(kind), f"{asset_id}/{kind}")
    return {"schema_version": 1, "release_id": release_id,
            "source_commit": expected_commit,
            "status": "blocked" if errors else "evidence_consistent",
            "gate_count": len(specs), "required_asset_count": len(asset_ids),
            "errors": errors,
            "limitation": "Consistency of declarations and referenced bytes only; not independent release certification."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--candidate-commit", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        result = validate(load_json(args.contract), load_json(args.evidence),
                          args.root, args.candidate_commit)
        text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            # Never overwrite an earlier result, including one with failed checks.
            with args.out.open("x", encoding="utf-8") as stream:
                stream.write(text)
        print(text, end="")
        return 0 if result["status"] == "evidence_consistent" else 1
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"INPUT ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
