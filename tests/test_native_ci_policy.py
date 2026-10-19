from pathlib import Path
import subprocess
import pytest
from scripts.native_ci_policy import TRUSTED_REF, TRUSTED_REMOTE, validate_candidate, validate_request


def test_manual_exact_commit_on_trusted_ref():
    validate_request('workflow_dispatch', TRUSTED_REF, 'a' * 40)


@pytest.mark.parametrize('event,ref,sha', [
    ('pull_request', TRUSTED_REF, 'a' * 40),
    ('push', TRUSTED_REF, 'a' * 40),
    ('workflow_dispatch', 'refs/heads/main', 'a' * 40),
    ('workflow_dispatch', TRUSTED_REF, 'main'),
    ('workflow_dispatch', TRUSTED_REF, 'a' * 39),
    ('workflow_dispatch', TRUSTED_REF, 'A' * 40),
    ('workflow_dispatch', TRUSTED_REF, 'a' * 40 + '\n'),
    ('workflow_dispatch', TRUSTED_REF, '$(echo secret)'),
])
def test_reject_unsafe_dispatch(event, ref, sha):
    with pytest.raises(ValueError):
        validate_request(event, ref, sha)


def git(repo: Path, *args):
    return subprocess.check_output(['git', *args], cwd=repo, text=True).strip()


def test_candidate_must_be_reachable_from_reviewed_ref(tmp_path):
    git(tmp_path, 'init', '-q')
    git(tmp_path, '-c', 'user.name=Frank Asante Van Laarhoven', '-c', 'user.email=frankleroyvan@gmail.com', 'commit', '--allow-empty', '-qm', 'reviewed')
    approved = git(tmp_path, 'rev-parse', 'HEAD')
    git(tmp_path, 'update-ref', TRUSTED_REMOTE, approved)
    validate_candidate(tmp_path, approved)
    git(tmp_path, '-c', 'user.name=Frank Asante Van Laarhoven', '-c', 'user.email=frankleroyvan@gmail.com', 'commit', '--allow-empty', '-qm', 'unreviewed')
    with pytest.raises(ValueError):
        validate_candidate(tmp_path, git(tmp_path, 'rev-parse', 'HEAD'))
