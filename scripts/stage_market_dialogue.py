#!/usr/bin/env python3
"""Stage authored English draft bytes for the existing UFS Data cook rule."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_dialogue(payload):
    if payload.get('schema_version') != 1 or payload.get('locale') != 'en':
        raise ValueError('Unsupported dialogue version or locale.')
    lines = payload.get('lines')
    if not isinstance(lines, list) or not 1 <= len(lines) <= 256:
        raise ValueError('Missing or excessive dialogue lines.')
    seen = set()
    for line in lines:
        if not isinstance(line, dict):
            raise ValueError('Invalid line object.')
        key, speaker, text = (line.get(field) for field in ('id', 'speaker', 'text'))
        if (not isinstance(key, str) or not key.startswith('MSN_') or len(key) > 64
                or key.casefold() in seen or not isinstance(speaker, str)
                or not speaker.strip() or len(speaker) > 64 or not isinstance(text, str)
                or not text.strip() or len(text) > 1024):
            raise ValueError('Invalid or duplicate dialogue line.')
        seen.add(key.casefold())
    return len(lines)


def stage(source, destination):
    raw = source.read_bytes()
    count = validate_dialogue(json.loads(raw))
    if destination.exists() and destination.read_bytes() != raw:
        raise ValueError('Existing staged dialogue differs. Preserve/version it before replacement.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        with destination.open('xb') as stream:
            stream.write(raw)
    return {'lines': count, 'sha256': hashlib.sha256(raw).hexdigest(),
            'source': str(source), 'staged': str(destination),
            'status': 'authored_draft_not_recorded_or_approved'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT / 'production/market/dialogue.en.json')
    parser.add_argument('--out', type=Path, default=ROOT / 'Unreal/Content/Data/market-dialogue.en.json')
    args = parser.parse_args()
    print(json.dumps(stage(args.source, args.out), indent=2))


if __name__ == '__main__':
    main()
