"""Contact evidence schema, assertion identity and provenance regressions."""
import copy
import json
import subprocess
import sys

import pytest
from scripts.verify_contact_report import EXPECTED_CHECKS, FIXTURE, SIDES, SURFACES, validate


def inputs():
    fingerprints = {k: 'a' * 64 for k in ('native_source_sha256', 'source_asset_sha256', 'authoring_source_sha256')}
    legs = [dict(leg=s, samples=10, excluded_swing_airborne_invalid=5,
                 p95_stance_drift_cm=3.4911711281893076e-06, max_penetration_cm=0.000004,
                 max_segment_length_error_cm=0, joint_limit_violations=0,
                 support_sample_coverage={'AnanseFixture:' + f: 1 for f in SURFACES}) for s in SIDES]
    report = dict(status='assertions_passed', acceptance='passed', process_exit_status=0,
                  mode='contact', world=FIXTURE + '.' + FIXTURE.rsplit('/', 1)[-1],
                  pawn='AnanseSpiderLabPlayer', controller='AnanseLabController',
                  normal_lit_rendering=True, rhi='Vulkan', play_stopped=True,
                  profile_trace_closed_before_exit=True, phase=10, active_play_seconds=240.1,
                  checks=list(EXPECTED_CHECKS), slot='AnanseVerify_test', loaded_hash='c' * 64,
                  ground_contact_metrics=json.dumps(dict(invalid_transforms=0, last_solved_chains=4,
                    measurement_stage='OnBoneTransformsFinalized evaluated tarsus + imported tip offset', legs=legs)))
    command = dict(exit_status=0, process_returncode=0, forced_termination=False, mode='contact',
                   context='package', command=['/test/Ananse', FIXTURE, '-AnanseVerifyMode=contact'],
                   slot='AnanseVerify_test', publication_hash='c' * 64, executable_sha256='b' * 64,
                   build_inputs=copy.deepcopy(fingerprints))
    return report, command, copy.deepcopy(command), fingerprints, 'b' * 64, 'c' * 64


def test_native_schema_and_full_exponent():
    metrics = validate(*inputs())
    assert metrics['legs'][0]['p95_stance_drift_cm'] < 0.000004


@pytest.mark.parametrize('field,value', [('world', 'L_Market_Greybox'), ('pawn', 'AnansePlayer'),
    ('checks', []), ('checks', ['arbitrary success']), ('process_exit_status', 139),
    ('play_stopped', False), ('phase', 9), ('active_play_seconds', 239),
    ('normal_lit_rendering', False), ('ground_contact_metrics', {})])
def test_superficial_success_rejected(field, value):
    args = list(inputs()); args[0][field] = value
    with pytest.raises(ValueError): validate(*args)


@pytest.mark.parametrize('field,value', [('samples', 0), ('p95_stance_drift_cm', 3.4911711),
    ('p95_stance_drift_cm', float('nan')), ('max_penetration_cm', .50001),
    ('excluded_swing_airborne_invalid', None), ('support_sample_coverage', {})])
def test_per_leg_failure_not_averaged(field, value):
    args = list(inputs()); metrics = json.loads(args[0]['ground_contact_metrics'])
    metrics['legs'][0][field] = value; args[0]['ground_contact_metrics'] = json.dumps(metrics)
    with pytest.raises(ValueError): validate(*args)


def test_missing_repeated_assertion_rejected():
    args = list(inputs()); args[0]['checks'].remove('four hand marker bindings retained')
    with pytest.raises(ValueError, match='assertion'): validate(*args)


@pytest.mark.parametrize('mutation', ['source', 'executable', 'publication', 'launch', 'forced'])
def test_provenance_failure_rejected(mutation):
    args = list(inputs())
    if mutation == 'source': args[3]['native_source_sha256'] = 'd' * 64
    if mutation == 'executable': args[4] = 'd' * 64
    if mutation == 'publication': args[5] = 'd' * 64
    if mutation == 'launch': args[2]['command'] = ['/wrong/map']
    if mutation == 'forced': args[1]['forced_termination'] = True
    with pytest.raises(ValueError): validate(*args)


def test_trailing_probe_exit_is_distinct_from_python_report_exit():
    # Reproduce the shell-exit ambiguity without relying on another process.
    code = 'import sys; print("assertions_passed"); sys.exit(0)'
    python = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
    combined = subprocess.run(['bash', '-c', '"$1" -c "$2"; exit 1', '_', sys.executable, code], capture_output=True, text=True)
    assert python.returncode == 0 and combined.returncode == 1
    assert python.stdout == combined.stdout
