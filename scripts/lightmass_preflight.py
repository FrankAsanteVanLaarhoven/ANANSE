"""Detect a worker startup crash before a lighting attempt can modify project assets.

A clean startup probe is never evidence of a completed or accepted lighting bake.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

THREAD_TAG_ERROR = 'The Gamethread can only be tagged on the inital thread of the application'


def classify_startup(returncode: int | None, output: str, timed_out: bool = False) -> dict:
    if THREAD_TAG_ERROR in output or 'Assertion failed: Tag == ETaskTag::EGameThread' in output:
        status = 'blocked_thread_tag_assertion'
    elif timed_out:
        status = 'blocked_probe_timeout'
    elif returncode != 0:
        status = 'blocked_worker_exit'
    elif 'Assertion failed:' in output or 'Fatal error:' in output or 'Signal 11 caught' in output:
        status = 'blocked_worker_diagnostic'
    else:
        status = 'startup_probe_completed'
    return {'status': status, 'process_exit_status': returncode,
            'timed_out': timed_out, 'bake_qualified': False,
            'scope': 'Worker startup only. Does not prove job processing, imported lightmaps, map compatibility or mobile lighting.'}


def probe_worker(worker: Path, out: Path, timeout_seconds: float = 20) -> dict:
    worker = worker.resolve()
    out = out.resolve()
    if not worker.is_file():
        raise FileNotFoundError(worker)
    if timeout_seconds <= 0:
        raise ValueError('Probe timeout must be positive')
    out.mkdir(parents=True, exist_ok=False)
    command = [str(worker), '-help', '-ansimalloc', '-unattended',
               '-UserDir=' + str(out / 'worker-profile'), '-abslog=' + str(out / 'worker.log')]
    timed_out = False
    try:
        result = subprocess.run(command, cwd=out, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=timeout_seconds, check=False)
        output = result.stdout
        returncode = result.returncode
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or b''
        returncode = None
        timed_out = True
    (out / 'startup.log').write_bytes(output)
    report = classify_startup(returncode, output.decode('utf-8', errors='replace'), timed_out)
    report.update(command=command, worker_sha256=hashlib.sha256(worker.read_bytes()).hexdigest(),
                  log_sha256=hashlib.sha256(output).hexdigest())
    version = worker.with_suffix('.version')
    if version.is_file():
        report['worker_version'] = json.loads(version.read_text())
    core = worker.parent / 'libUnrealLightmass-Core.so'
    if core.is_file():
        report['worker_core_sha256'] = hashlib.sha256(core.read_bytes()).hexdigest()
    (out / 'preflight.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--timeout', type=float, default=20)
    args = parser.parse_args()
    report = probe_worker(args.worker, args.out, args.timeout)
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'startup_probe_completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
