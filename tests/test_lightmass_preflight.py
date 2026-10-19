"""Reject the observed startup failure, false exit-zero and incomplete probes."""
import json
from pathlib import Path
import subprocess
import pytest
from scripts.lightmass_preflight import THREAD_TAG_ERROR, classify_startup, probe_worker


def test_actual_assertion_wins_over_successful_parent_exit():
    r = classify_startup(0, THREAD_TAG_ERROR)
    assert r['status'] == 'blocked_thread_tag_assertion'
    assert r['bake_qualified'] is False


@pytest.mark.parametrize('code,log,timeout,status', [
    (-11, THREAD_TAG_ERROR, False, 'blocked_thread_tag_assertion'),
    (None, '', True, 'blocked_probe_timeout'),
    (1, 'Invalid job', False, 'blocked_worker_exit'),
    (0, 'Fatal error: worker failed', False, 'blocked_worker_diagnostic'),
    (0, 'Signal 11 caught.', False, 'blocked_worker_diagnostic'),
    (0, 'Startup completed', False, 'startup_probe_completed'),
])
def test_startup_classification_never_qualifies_bake(code, log, timeout, status):
    result = classify_startup(code, log, timeout)
    assert result['status'] == status
    assert result['bake_qualified'] is False


def test_crashed_worker_exit_and_evidence_are_retained(tmp_path, monkeypatch):
    worker = tmp_path / 'UnrealLightmass'
    worker.write_bytes(b'fixture executable identity')
    worker.with_suffix('.version').write_text(json.dumps({'MajorVersion': 5, 'MinorVersion': 8}))
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: subprocess.CompletedProcess(a[0], -11, THREAD_TAG_ERROR.encode()))
    out = tmp_path / 'probe'
    result = probe_worker(worker, out)
    assert result['status'] == 'blocked_thread_tag_assertion'
    assert result['process_exit_status'] == -11
    assert len(result['worker_sha256']) == 64
    assert (out / 'startup.log').read_text() == THREAD_TAG_ERROR
    assert json.loads((out / 'preflight.json').read_text()) == result
    with pytest.raises(FileExistsError):
        probe_worker(worker, out)


def test_timeout_remains_incomplete_and_preserves_partial_output(tmp_path, monkeypatch):
    worker = tmp_path / 'UnrealLightmass'
    worker.write_bytes(b'fixture')
    def expire(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 1, output=b'partial startup')
    monkeypatch.setattr(subprocess, 'run', expire)
    result = probe_worker(worker, tmp_path / 'probe', 1)
    assert result['status'] == 'blocked_probe_timeout'
    assert result['process_exit_status'] is None
    assert result['bake_qualified'] is False


def test_missing_worker_never_creates_success_evidence(tmp_path):
    with pytest.raises(FileNotFoundError):
        probe_worker(tmp_path / 'missing', tmp_path / 'out')
    assert not (tmp_path / 'out').exists()


def test_environment_finish_rejects_worker_before_asset_access(tmp_path, monkeypatch):
    import runpy
    import sys
    import types
    import scripts.lightmass_preflight as preflight
    accessed = []
    unreal = types.ModuleType('unreal')
    for name in ('LevelEditorSubsystem', 'EditorActorSubsystem', 'StaticMeshEditorSubsystem'):
        setattr(unreal, name, type(name, (), {}))
    unreal.get_editor_subsystem = lambda cls: object()
    def forbidden(*args, **kwargs):
        accessed.append(args)
        raise AssertionError('No asset may load during blocked startup')
    unreal.load_asset = forbidden
    monkeypatch.setitem(sys.modules, 'unreal', unreal)
    monkeypatch.setenv('ANANSE_EVIDENCE_DIR', str(tmp_path / 'integration'))
    monkeypatch.setattr(preflight, 'probe_worker', lambda *a, **k: {'status': 'blocked_thread_tag_assertion'})
    with pytest.raises(RuntimeError, match='project assets untouched'):
        runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/finish_route_environment.py'))
    assert accessed == []
