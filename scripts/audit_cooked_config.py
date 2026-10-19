#!/usr/bin/env python3
"""Targeted audit of actual cooked config bytes; never prints config values."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.prepare_native_config import token_assignment_count


def read_config_entry(pak, listing):
    match = re.search(r'"Ananse/Config/DefaultEngine.ini" offset: (\d+), size: (\d+) bytes, sha1: ([a-fA-F0-9]{40}), compression: None', listing)
    if not match:
        raise ValueError('Expected uncompressed config entry is absent or unsupported; no passing audit inferred.')
    offset, size = int(match[1]), int(match[2])
    if size > 1048576:
        raise ValueError('Config entry exceeds the bounded audit size.')
    # Installed FPakEntry::GetSerializedSize: three int64s, uint32 method,
    # SHA1[20], uint8 flags and uint32 block size for an uncompressed v8+ entry.
    with pak.open('rb') as stream:
        stream.seek(offset)
        header = stream.read(53)
        if len(header) != 53 or header[48] & 1:
            raise ValueError('Truncated/encrypted entry is unsupported by this read-back.')
        raw = stream.read(size)
    if len(raw) != size or hashlib.sha1(raw).hexdigest() != match[3].lower():
        raise ValueError('Read-back bytes do not match the independent native entry digest.')
    return raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pak', type=Path, required=True)
    parser.add_argument('--unreal-pak', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    env.pop('LD_LIBRARY_PATH', None)
    command = [str(args.unreal_pak.resolve()), str(args.pak.resolve()), '-List']
    result = subprocess.run(command, env=env, capture_output=True, text=True)
    (args.out / 'native-list.log').write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f'Native list failed with {result.returncode}; no audit pass.')
    raw = read_config_entry(args.pak, result.stdout)
    count = token_assignment_count(raw)
    report = {'pak': str(args.pak.resolve()), 'command': command, 'native_exit': result.returncode,
              'config_sha256': hashlib.sha256(raw).hexdigest(), 'entry_sha1_verified': True,
              'nonempty_file_server_token_assignments': count,
              'status': 'passed_targeted_scan' if count == 0 else 'failed',
              'scope': 'Actual cooked DefaultEngine.ini; SecurityToken/AuthenticationToken only. No values exposed.'}
    (args.out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if count == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
