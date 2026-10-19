#!/usr/bin/env python3
"""Keep local development file-server credentials out of source/cook inputs."""
import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SECTION = '[/Script/AndroidFileServerEditor.AndroidFileServerRuntimeSettings]'
SAFE = {'bEnablePlugin': 'False', 'bAllowNetworkConnection': 'False',
        'SecurityToken': '""', 'AuthenticationToken': '""',
        'bIncludeInShipping': 'False', 'bAllowExternalStartInShipping': 'False'}


def token_assignment_count(raw):
    pattern = rb'(?mi)^\s*(?:AuthenticationToken|SecurityToken)\s*=\s*(.*)$'
    return sum(bool(match.group(1).strip().strip(b'"\'')) for match in re.finditer(pattern, raw))


def prepare(root=ROOT):
    path = root / 'Unreal/Config/DefaultEngine.ini'
    raw = path.read_bytes()
    output, block, inside, found = [], [], False, False
    def flush():
        seen = set()
        for line in block:
            key = line.split('=', 1)[0].strip() if '=' in line else ''
            if key in SAFE:
                if key not in seen:
                    output.append(key + '=' + SAFE[key] + '\n')
                    seen.add(key)
            else:
                output.append(line)
        for key, value in SAFE.items():
            if key not in seen:
                output.append(key + '=' + value + '\n')
        block.clear()
    for line in raw.decode().splitlines(keepends=True):
        if line.strip().startswith('['):
            if inside:
                flush()
            inside = line.strip().casefold() == SECTION.casefold()
            if inside:
                found = True
            output.append(line)
        elif inside:
            block.append(line)
        else:
            output.append(line)
    if inside:
        flush()
    if not found:
        output.append('\n' + SECTION + '\n')
        output.extend(key + '=' + value + '\n' for key, value in SAFE.items())
    clean = (''.join(output).rstrip() + '\n').encode()
    backup = None
    if clean != raw:
        private = root / '.local/private/native-config'
        private.mkdir(parents=True, mode=0o700, exist_ok=True)
        backup = private / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ') + '.ini')
        fd = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
        path.write_bytes(clean)
    if token_assignment_count(path.read_bytes()):
        raise ValueError('A file-server token assignment remains; native launch blocked.')
    return {'changed': clean != raw, 'before_sha256': hashlib.sha256(raw).hexdigest(),
            'after_sha256': hashlib.sha256(clean).hexdigest(),
            'private_backup': str(backup) if backup else None,
            'token_assignments_before': token_assignment_count(raw), 'token_assignments_after': 0,
            'scope': 'Project-local Android file-server settings only. No tokens printed or rotated.'}


if __name__ == '__main__':
    import json
    parser = argparse.ArgumentParser()
    parser.parse_args()
    print(json.dumps(prepare(), indent=2))
