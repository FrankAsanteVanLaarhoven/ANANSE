import copy
import json
from pathlib import Path

import pytest

from scripts.stage_market_dialogue import stage, validate_dialogue
from scripts.verify_spider_cosmetic import restore_appearance

SOURCE = Path(__file__).resolve().parents[1] / 'production/market/dialogue.en.json'


def test_actual_authored_dialogue_stages_exact_bytes(tmp_path):
    out = tmp_path / 'Data/market-dialogue.en.json'
    report = stage(SOURCE, out)
    assert report['lines'] == 44
    assert out.read_bytes() == SOURCE.read_bytes()
    assert stage(SOURCE, out) == report


def test_existing_modified_stage_is_preserved(tmp_path):
    out = tmp_path / 'dialogue.json'
    out.write_bytes(b'private existing draft')
    with pytest.raises(ValueError, match='differs'):
        stage(SOURCE, out)
    assert out.read_bytes() == b'private existing draft'


def test_cosmetic_restore_preserves_unrelated_current_edits():
    prior = {'kind': 'characters', 'id': 'ananse', 'data': {'variants': [
        {'id': 'base', 'cloth_colour': '#AD6E36', 'body_asset_id': None}]}}
    current = {'description': 'New user edit', 'powers': [], 'variants': [
        {'id': 'base', 'cloth_colour': '#48766B', 'body_asset_id': 'ananse-spider-proxy-v002', 'label': 'New label'},
        {'id': 'night', 'cloth_colour': '#123456', 'body_asset_id': None}]}
    restored = restore_appearance(current, prior)
    assert restored['description'] == 'New user edit'
    assert restored['variants'][0]['label'] == 'New label'
    assert restored['variants'][1] == current['variants'][1]
    assert restored['variants'][0]['cloth_colour'] == '#AD6E36'
    assert restored['variants'][0]['body_asset_id'] is None
    assert current['variants'][0]['cloth_colour'] == '#48766B'


def test_cosmetic_restore_rejects_other_identity():
    with pytest.raises(ValueError, match='never Kwaku'):
        restore_appearance({}, {'kind': 'characters', 'id': 'kwaku'})


@pytest.mark.parametrize('change', ['duplicate', 'case_duplicate', 'blank_text', 'blank_speaker', 'oversize', 'locale', 'version'])
def test_bad_dialogue_rejected(change):
    doc = copy.deepcopy(json.loads(SOURCE.read_text()))
    if change in ('duplicate', 'case_duplicate'):
        doc['lines'][1]['id'] = doc['lines'][0]['id'] if change == 'duplicate' else doc['lines'][0]['id'].lower().replace('msn_', 'MSN_')
    elif change == 'blank_text':
        doc['lines'][0]['text'] = ' '
    elif change == 'blank_speaker':
        doc['lines'][0]['speaker'] = ' '
    elif change == 'oversize':
        doc['lines'][0]['text'] = 'a' * 1025
    elif change == 'locale':
        doc['locale'] = 'unknown'
    else:
        doc['schema_version'] = 2
    with pytest.raises(ValueError):
        validate_dialogue(doc)
