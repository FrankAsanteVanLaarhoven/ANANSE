#!/usr/bin/env python3
"""Validate a reviewed manual native-build candidate without executing candidate code."""
from __future__ import annotations
import argparse
import re
import subprocess
from pathlib import Path

TRUSTED_REF = 'refs/heads/feature/local-milestone-verification'
TRUSTED_REMOTE = 'refs/remotes/origin/feature/local-milestone-verification'


def validate_request(event_name: str, workflow_ref: str, candidate_sha: str) -> None:
    if event_name != 'workflow_dispatch':
        raise ValueError('Native builds require manual workflow_dispatch.')
    if workflow_ref != TRUSTED_REF:
        raise ValueError('Dispatch must use the reviewed development workflow ref.')
    if not re.fullmatch(r'[0-9a-f]{40}', candidate_sha):
        raise ValueError('Candidate must be an exact lowercase 40-character commit SHA.')


def validate_candidate(repo: Path, candidate_sha: str) -> None:
    # Run Git only; never import or execute source from the candidate tree.
    actual = subprocess.check_output(
        ['git', 'rev-parse', f'{candidate_sha}^{{commit}}'], cwd=repo, text=True
    ).strip()
    if actual != candidate_sha:
        raise ValueError('Candidate is not the requested commit object.')
    result = subprocess.run(
        ['git', 'merge-base', '--is-ancestor', candidate_sha, TRUSTED_REMOTE], cwd=repo
    )
    if result.returncode != 0:
        raise ValueError('Candidate is not reachable from the reviewed development ref.')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--event', required=True)
    parser.add_argument('--workflow-ref', required=True)
    parser.add_argument('--candidate-sha', required=True)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    args = parser.parse_args()
    validate_request(args.event, args.workflow_ref, args.candidate_sha)
    validate_candidate(args.repo, args.candidate_sha)
    print(f'Validated reviewed native candidate {args.candidate_sha}')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(f'BLOCKED: {error}')
