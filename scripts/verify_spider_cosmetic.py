#!/usr/bin/env python3
"""Apply a bounded Ananse prototype revision through the existing loopback API.

This writes the selected local database. Review uses distinct ephemeral local
roles; it is not independently identified production art/rights approval.
"""
import argparse
import copy
import hashlib
import json
import secrets
import socket
import sqlite3
import sys
import threading
import time
from pathlib import Path

import httpx
import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from studio.app import create_app
from scripts.export_content import verify_manifest


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def restore_appearance(current_data, prior):
    if prior.get('kind') != 'characters' or prior.get('id') != 'ananse':
        raise ValueError('Restore source must identify Ananse, never Kwaku.')
    changed = copy.deepcopy(current_data)
    previous = prior['data']['variants'][0]
    matches = [variant for variant in changed['variants'] if variant['id'] == previous['id']]
    if len(matches) != 1:
        raise ValueError('Original variant binding changed; reconcile it explicitly.')
    for field in ('cloth_colour', 'body_asset_id'):
        matches[0][field] = previous.get(field)
    return changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=Path, default=ROOT / '.local/studio.sqlite3')
    parser.add_argument('--out', type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--colour')
    group.add_argument('--restore-from', type=Path)
    args = parser.parse_args()
    if not args.db.is_file():
        parser.error('Existing studio database required; this command never seeds a replacement.')
    args.out.mkdir(parents=True, exist_ok=False)
    backup = args.out / 'private-backup'
    backup.mkdir(mode=0o700)
    with sqlite3.connect(args.db) as live, sqlite3.connect(backup / 'studio.sqlite3') as saved:
        live.backup(saved)
        old_publications = dict(live.execute('SELECT id,manifest FROM publications'))
        kwaku_history = list(live.execute("SELECT version,document FROM revisions WHERE kind='characters' AND id='kwaku' ORDER BY version"))
    (backup / 'studio.sqlite3').chmod(0o600)
    tokens = {role: secrets.token_urlsafe(32) for role in ('editor', 'reviewer', 'publisher')}
    app = create_app(args.db, tokens)
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, log_level='error', access_log=False))
    thread = threading.Thread(target=lambda: server.run(sockets=[sock]), daemon=True)
    thread.start()
    checks = []
    try:
        with httpx.Client(base_url=f'http://127.0.0.1:{port}', timeout=10) as client:
            for _ in range(100):
                if server.started:
                    break
                time.sleep(.1)
            if not server.started:
                raise RuntimeError('Owned loopback server did not start.')

            def req(method, path, role='editor', body=None, version=None, status=200):
                headers = {'Authorization': 'Bearer ' + tokens[role]}
                if version is not None:
                    headers['If-Match'] = str(version)
                response = client.request(method, path, headers=headers, json=body)
                if response.status_code != status:
                    raise RuntimeError(f'{method} {path}: expected {status}, got {response.status_code}: {response.text}')
                return response.json()

            if client.get('/api/characters/ananse').status_code != 401:
                raise RuntimeError('Unauthenticated read accepted.')
            checks.append('unauthenticated read rejected')
            original = req('GET', '/api/characters/ananse')
            (args.out / 'original-character.json').write_text(json.dumps(original, indent=2) + '\n')
            changed = copy.deepcopy(original['data'])
            if args.restore_from:
                prior = json.loads(args.restore_from.read_text())
                changed = restore_appearance(original['data'], prior)
            else:
                # A real native source-asset reference, explicitly quarantined, not finished art.
                asset_id = 'ananse-spider-proxy-v002'
                asset_path = ROOT / 'Unreal/Content/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY.uasset'
                if not asset_path.is_file():
                    raise RuntimeError('Qualified native skeletal source asset is absent.')
                response = client.get('/api/assets/' + asset_id, headers={'Authorization': 'Bearer ' + tokens['editor']})
                if response.status_code == 404:
                    asset = req('POST', '/api/assets', body={'id': asset_id, 'data': {
                        'name': 'Ananse eight-appendage engineering proxy v002',
                        'category': 'skeletal-mesh',
                        'unreal_path': '/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY.AnanseSpider_PROXY',
                        'source_reference': 'Local imported engineering fixture. sha256 identifies native source .uasset bytes, not GLB, cooked bytes or rights clearance.',
                        'sha256': file_hash(asset_path), 'licence': 'UNVERIFIED',
                        'status': 'quarantine', 'material_slots': 6,
                    }}, status=201)
                    req('POST', f'/api/assets/{asset_id}/review', role='reviewer', body={
                        'version': asset['version'], 'decision': 'approved',
                        'note': 'Prototype metadata binding only. Quarantine, rights, final art and mobile gates remain unresolved.'})
                elif response.status_code != 200:
                    raise RuntimeError('Could not inspect existing proxy asset record.')
                else:
                    asset = response.json()
                    if asset['data']['unreal_path'] != '/Game/Characters/AnanseSpider/Proxy_GLTF_v002/AnanseSpider_PROXY.AnanseSpider_PROXY' or asset['data']['sha256'] != file_hash(asset_path):
                        raise ValueError('Existing proxy record differs; preserve it and reconcile explicitly.')
                changed['variants'][0]['cloth_colour'] = args.colour
                changed['variants'][0]['body_asset_id'] = asset_id
            req('PATCH', '/api/characters/ananse', role='reviewer', body={'data': changed}, version=original['version'], status=403)
            checks.append('reviewer cannot edit')
            revised = req('PATCH', '/api/characters/ananse', body={'data': changed}, version=original['version'])
            req('PATCH', '/api/characters/ananse', body={'data': changed}, version=original['version'], status=412)
            checks.append('stale edit rejected')
            req('POST', '/api/characters/ananse/review', role='reviewer', body={'version': original['version'], 'decision': 'approved', 'note': 'Stale negative test.'}, status=412)
            checks.append('stale review rejected')
            req('POST', '/api/characters/ananse/review', role='editor', body={'version': revised['version'], 'decision': 'approved', 'note': 'Wrong role negative test.'}, status=403)
            checks.append('editor cannot review')
            req('POST', '/api/characters/ananse/review', role='reviewer', body={
                'version': revised['version'], 'decision': 'approved',
                'note': 'Exact prototype cosmetic revision only; not final art, rights, cultural or mobile approval.'})
            req('POST', '/api/publish', role='editor', body={'channel': 'prototype'}, status=403)
            checks.append('editor cannot publish')
            publication = req('POST', '/api/publish', role='publisher', body={'channel': 'prototype'}, status=201)
            manifest = publication['manifest']
            verify_manifest(manifest)
            exported = ROOT / 'Unreal/Content/Data/catalogue.json'
            tmp = exported.with_suffix('.json.episode-tmp')
            tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
            tmp.replace(exported)
            (args.out / 'publication.json').write_text(json.dumps(publication, indent=2) + '\n')
            audit = req('GET', '/api/audit')
            checks.append('immutable publication exported; recook required')
        with sqlite3.connect(args.db) as live:
            for key, value in old_publications.items():
                if live.execute('SELECT manifest FROM publications WHERE id=?', (key,)).fetchone()[0] != value:
                    raise RuntimeError('Historical publication changed.')
            if list(live.execute("SELECT version,document FROM revisions WHERE kind='characters' AND id='kwaku' ORDER BY version")) != kwaku_history:
                raise RuntimeError('Kwaku history changed.')
        report = {'checks': checks, 'publication_id': publication['id'],
                  'publication_hash': manifest['sha256'], 'ananse_revision': revised['version'],
                  'cloth_colour': revised['data']['variants'][0]['cloth_colour'],
                  'source_asset_sha256': file_hash(asset_path) if not args.restore_from else None,
                  'historical_publications_preserved': len(old_publications), 'kwaku_history_unchanged': True,
                  'audit_integrity': audit['integrity'], 'review_scope': 'distinct local role tokens; prototype metadata only',
                  'cook_observation': 'pending'}
        (args.out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        if thread.is_alive():
            raise RuntimeError('Owned loopback server did not exit normally.')
        sock.close()


if __name__ == '__main__':
    main()
