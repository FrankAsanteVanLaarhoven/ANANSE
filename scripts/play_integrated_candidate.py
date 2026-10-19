"""Launch an existing integrated Linux review candidate with its required bindings."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
import re
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MAPS = {
    'chapter': '/Game/Ananse/Maps/EnvironmentRoute_v002/L_RiverMarket_Route',
    'cast-lab': '/Game/Ananse/Maps/Contact_v002/L_AsoYaaCharacterLab',
}
FLAGS = ['-AnanseAsoContact', '-AnanseAsoReview', '-AnanseAcceptedVisuals',
         '-AnanseStoryPresentation', '-AnanseArtRefinement', '-AnanseFormsScenery',
         '-AnanseInteractionRefinement',
         '-ansimalloc', '-windowed', '-ResX=1280', '-ResY=720']


def launch_command(package: Path, scene: str, profile: Path) -> list[str]:
    package = package.resolve()
    if not package.is_relative_to((ROOT / 'Builds/Linux').resolve()):
        raise ValueError('Use an existing project-local Linux candidate.')
    executable = package / 'Ananse/Binaries/Linux/Ananse'
    if not executable.is_file():
        raise FileNotFoundError(executable)
    return [str(executable), MAPS[scene], *FLAGS,
            *(['-AnanseEnvironmentRoute', '-AnanseEpisode', '-AnanseProductionPursuit'] if scene == 'chapter' else ['-AnanseArtPass2', '-AnanseVisualReview', '-AnanseNeutralLabLighting']),
            '-UserDir=' + str(profile.resolve())]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True, type=Path)
    parser.add_argument('--scene', choices=MAPS, default='chapter')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--profile', help='Reusable isolated review-profile name; omitted creates a fresh profile.')
    args = parser.parse_args()
    if args.profile and not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', args.profile):
        parser.error('Profile must be a simple name of 1..64 letters, numbers, underscores or hyphens.')
    profile = ROOT / '.local/player-reviews' / (args.profile or (args.scene + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')))
    try:
        command = launch_command(args.package, args.scene, profile)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.dry_run:
        print(json.dumps({'command': command, 'creative': 'REVIEW_REQUIRED', 'mobile': 'UNQUALIFIED'}, indent=2))
        return 0
    profile.mkdir(parents=True, exist_ok=bool(args.profile))
    env = os.environ.copy()
    for key in ('PYTHONPATH', 'LD_LIBRARY_PATH'):
        env.pop(key, None)
    print('Review candidate: creative acceptance pending; mobile unqualified.', flush=True)
    return subprocess.call(command, cwd=ROOT, env=env)


if __name__ == '__main__':
    raise SystemExit(main())
