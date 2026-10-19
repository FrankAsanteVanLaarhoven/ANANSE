from pathlib import Path

from scripts.prepare_native_config import prepare, token_assignment_count, SECTION
from scripts.audit_cooked_config import read_config_entry
import hashlib
import pytest


def test_both_token_names_detected_without_exposing_values():
    assert token_assignment_count(b'AuthenticationToken=fixture\nSecurityToken="fixture"\n') == 2
    assert token_assignment_count(b'AuthenticationToken=""\nSecurityToken=\n') == 0


def test_private_backup_and_unrelated_settings_preserved(tmp_path):
    path = tmp_path / 'Unreal/Config/DefaultEngine.ini'
    path.parent.mkdir(parents=True)
    original = b'[Rendering]\nKeepThis=123\n' + SECTION.encode() + b'\nSecurityToken=fixture\nbUseCompression=True\n[Other]\nUntouched=Yes\n'
    path.write_bytes(original)
    result = prepare(tmp_path)
    assert result['token_assignments_before'] == 1
    assert token_assignment_count(path.read_bytes()) == 0
    assert b'bUseCompression=True' in path.read_bytes()
    assert b'[Other]\nUntouched=Yes' in path.read_bytes()
    backup = Path(result['private_backup'])
    assert backup.read_bytes() == original
    assert backup.stat().st_mode & 0o777 == 0o600
    assert backup.parent.stat().st_mode & 0o777 == 0o700


def test_prepare_is_idempotent_and_prevents_auto_generation(tmp_path):
    path = tmp_path / 'Unreal/Config/DefaultEngine.ini'
    path.parent.mkdir(parents=True)
    path.write_text('[Other]\nKeep=True\n')
    prepare(tmp_path)
    first = path.read_bytes()
    second = prepare(tmp_path)
    assert not second['changed']
    assert second['private_backup'] is None
    assert path.read_bytes() == first
    assert b'SecurityToken=""' in first
    assert b'bEnablePlugin=False' in first


def test_cooked_readback_verifies_bytes_not_expected_metadata(tmp_path):
    payload = b'[Test]\nSecurityToken=fixture\n'
    pak = tmp_path / 'fixture.pak'
    pak.write_bytes(bytes(53) + payload)
    listing = f'"Ananse/Config/DefaultEngine.ini" offset: 0, size: {len(payload)} bytes, sha1: {hashlib.sha1(payload).hexdigest()}, compression: None.'
    assert token_assignment_count(read_config_entry(pak, listing)) == 1
    pak.write_bytes(bytes(53) + b'x' * len(payload))
    with pytest.raises(ValueError, match='digest'):
        read_config_entry(pak, listing)


def test_missing_native_entry_never_counts_as_clean(tmp_path):
    with pytest.raises(ValueError, match='absent'):
        read_config_entry(tmp_path / 'absent.pak', '')
