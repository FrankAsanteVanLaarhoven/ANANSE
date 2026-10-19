"""Allowlisted local visual source retrieval; no metadata-selected filesystem paths."""
import hashlib
from pathlib import Path
from .store import DomainError
from .models import STORY_DESIGNS, STORY_REFINEMENTS

def preview_source(root: Path, record: dict) -> tuple[Path,str]:
    visual=record['data'].get('visual_design')
    if not visual:
        raise DomainError(409,'No qualified local preview source for this visual revision.')
    if visual['design_id']=='osebo-leopard-v1' and visual['source_revision']=='authored-v002':
        relative='SourceArt/Characters/OseboLeopard/Authored_v002/OseboLeopard.glb'
    elif visual['design_id'] in STORY_DESIGNS:
        key, revision = STORY_DESIGNS[visual['design_id']]
        refined=STORY_REFINEMENTS.get((visual['design_id'],visual['source_revision']))
        if not refined and visual['source_revision'] != revision:
            raise DomainError(409,'Unsupported local source revision.')
        folder=refined['folder'] if refined else revision.replace('authored','Authored').replace('-','_')
        relative=f'SourceArt/Characters/{key}/{folder}/{key}.glb'
    else:
        raise DomainError(409,'No qualified local preview source for this visual revision.')
    path=(root/relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file() or path.stat().st_size>32*1024*1024:
        raise DomainError(409,'The allowlisted model source must be materialised locally.')
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest!=visual['source_glb_sha256']:
        raise DomainError(409,'Preview source hash differs from this exact asset revision.')
    return path,digest
