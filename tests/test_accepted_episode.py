from pathlib import Path
import pytest
from scripts.unreal import required_accepted_episode_maps,ACCEPTED_EPISODE_MAPS

def test_accepted_episode_rejects_missing_and_partial_maps(tmp_path):
 with pytest.raises(RuntimeError,match='Accepted episode map missing'):required_accepted_episode_maps(tmp_path)
 p=tmp_path/(ACCEPTED_EPISODE_MAPS[0].removeprefix('/Game/')+'.umap');p.parent.mkdir(parents=True);p.write_bytes(b'fixture')
 with pytest.raises(RuntimeError,match='Sanctuary'):required_accepted_episode_maps(tmp_path)

def test_accepted_episode_requires_market_and_sanctuary(tmp_path):
 for path in ACCEPTED_EPISODE_MAPS:
  p=tmp_path/(path.removeprefix('/Game/')+'.umap');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'fixture')
 assert required_accepted_episode_maps(tmp_path)==list(ACCEPTED_EPISODE_MAPS)
