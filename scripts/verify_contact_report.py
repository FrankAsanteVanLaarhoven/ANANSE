"""Validate the existing cooked contact schema against independent cook inputs.

This audits retained evidence; it never reruns or upgrades a historical session.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

FIXTURE = '/Game/Characters/AnanseSpider/ContactLab_v006/L_AnanseContactLab'
SIDES = ('front_l', 'front_r', 'rear_l', 'rear_r')
SURFACES = ('flat', 'ramp', 'steps', 'uneven', 'moving', 'disappearing')
# Assertion identities from the native contact scenario, including multiplicity.
PREFIX = [
    'live publication hash loaded', 'separate Ananse identity possessed',
    'Published custom spider binding preserves verified +X basis; no inherited mannequin yaw',
    'Actual named proxy cloth material consumes published Ananse variant',
    'Actual parent material has cooked skeletal-mesh usage; parameter storage alone is insufficient',
    'Live skeletal cloth slot matches published linear colour at tolerance 0.0001',
    'real Vulkan rendering backend', 'imported custom skeleton retains at least 102 joints',
] + ['four hand marker bindings retained'] * 4 + [
    'four imported skeletal clips available',
] + ['actual clip-selector input reached skeletal player', 'live evaluated bones move during selected clip'] * 3 + [
    'Actual jump releases and reacquires transient contacts',
    'simulated input reached native save', 'Dedicated spider checkpoint created through F5',
    'simulated input reached native Load', 'F9 checkpoint load rebuilds transient contacts',
    'Direct native flight-transition fixture starts; no ability permission granted',
    'Flight/landing rebuilds contacts',
]
PER_LEG = ['per-leg actual fixture support coverage: ' + s for s in SURFACES] + [
    'post-solve finite transforms and segment-length preservation',
    'evaluated supporting-leg knee flex stays within declared 5..155 degree engineering limits',
    'actual post-solve stance drift and penetration gate',
]
EXPECTED_CHECKS = PREFIX + PER_LEG * 4 + [
    'declared fixture route traversed', 'possessed spider uses existing movement input',
]


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def finite_range(value, lower, upper):
    return type(value) in (int, float) and math.isfinite(value) and lower <= value <= upper


def validate(report, command, launch, cook_inputs, executable_sha256, publication_hash):
    """Fail closed on scenario, assertion, completion, identity or contact mismatch."""
    require(report.get('status') == 'assertions_passed' and report.get('acceptance') == 'passed', 'runtime acceptance')
    require(report.get('process_exit_status') == command.get('exit_status') == command.get('process_returncode') == 0,
            'normal process exit')
    require(command.get('forced_termination') is False, 'forced termination')
    require(report.get('mode') == command.get('mode') == launch.get('mode') == 'contact', 'scenario')
    require(command.get('context') == launch.get('context') == 'package', 'packaged context')
    require(report.get('world') == FIXTURE + '.' + FIXTURE.rsplit('/', 1)[-1], 'fixture world')
    require(report.get('pawn') == 'AnanseSpiderLabPlayer' and report.get('controller') == 'AnanseLabController', 'fixture pawn/controller')
    require(report.get('normal_lit_rendering') is True and report.get('rhi') == 'Vulkan', 'rendered backend')
    require(report.get('play_stopped') is True and report.get('profile_trace_closed_before_exit') is True and report.get('phase') == 10, 'incomplete execution')
    require(finite_range(report.get('active_play_seconds'), 240, 300), 'active duration')
    checks = report.get('checks')
    require(isinstance(checks, list) and all(type(c) is str for c in checks) and Counter(checks) == Counter(EXPECTED_CHECKS), 'assertion identities/count')
    argv = command.get('command', [])
    require(argv == launch.get('command') and FIXTURE in argv and '-AnanseVerifyMode=contact' in argv, 'launch command')
    require(command.get('slot') == launch.get('slot') == report.get('slot') and str(report['slot']).startswith('AnanseVerify_'), 'session slot')
    require(isinstance(publication_hash, str) and len(publication_hash) == 64 and report.get('loaded_hash') == command.get('publication_hash') == publication_hash, 'publication identity')
    require(executable_sha256 == command.get('executable_sha256') == launch.get('executable_sha256'), 'executable identity')
    for key in ('native_source_sha256', 'source_asset_sha256', 'authoring_source_sha256'):
        expected = cook_inputs.get(key)
        require(isinstance(expected, str) and len(expected) == 64, 'missing cook fingerprint: ' + key)
        require(command.get('build_inputs', {}).get(key) == launch.get('build_inputs', {}).get(key) == expected,
                'cook identity: ' + key)
    # Actual native schema contains JSON text here, not a nested dictionary.
    require(type(report.get('ground_contact_metrics')) is str, 'metrics schema')
    metrics = json.loads(report['ground_contact_metrics'])
    require(metrics.get('invalid_transforms') == 0 and metrics.get('last_solved_chains') == 4, 'invalid pose')
    require(str(metrics.get('measurement_stage', '')).startswith('OnBoneTransformsFinalized evaluated tarsus'), 'post-evaluation measurement')
    legs = metrics.get('legs', [])
    require(len(legs) == 4 and {l.get('leg') for l in legs} == set(SIDES), 'leg identities')
    for leg in legs:
        require(type(leg.get('samples')) is int and leg['samples'] > 0, 'zero samples')
        require(type(leg.get('excluded_swing_airborne_invalid')) is int and leg['excluded_swing_airborne_invalid'] >= 0, 'missing exclusions')
        for key, limit in [('p95_stance_drift_cm', 2), ('max_penetration_cm', .5), ('max_segment_length_error_cm', .1)]:
            require(finite_range(leg.get(key), 0, limit), leg['leg'] + ': ' + key)
        require(leg.get('joint_limit_violations') == 0, 'joint limits')
        for surface in SURFACES:
            n = leg.get('support_sample_coverage', {}).get('AnanseFixture:' + surface)
            require(type(n) is int and n > 0, 'missing fixture coverage: ' + surface)
    return metrics


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--cook-inputs', type=Path, required=True)
    p.add_argument('--catalogue', type=Path, default=Path(__file__).resolve().parents[1] / 'Unreal/Content/Data/catalogue.json')
    a = p.parse_args()
    load = lambda f: json.loads(f.read_text(encoding='utf-8-sig'))
    report_path = a.run / 'native-runtime.json'
    command = load(a.run / 'command.json')
    launch_path = a.run / 'launch.json'
    # launch is written before execution; command is finalized after the report.
    require(launch_path.stat().st_mtime_ns <= report_path.stat().st_mtime_ns, 'stale pre-launch report')
    exe = Path(command['command'][0])
    with exe.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    cook = load(a.cook_inputs)
    require(hashlib.sha256(a.catalogue.read_bytes()).hexdigest() == cook.get('files', {}).get('Unreal/Content/Data/catalogue.json'), 'catalogue file bytes differ from cook')
    metrics = validate(load(report_path), command, load(launch_path), cook, digest, load(a.catalogue).get('sha256'))
    print(json.dumps({'audit': 'passed', 'historical_run': str(a.run), 'checks': len(EXPECTED_CHECKS),
                      'legs': [{k: l[k] for k in ('leg', 'samples', 'excluded_swing_airborne_invalid', 'p95_stance_drift_cm', 'max_penetration_cm')} for l in metrics['legs']]}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
