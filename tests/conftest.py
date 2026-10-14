from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from studio.app import create_app
ROOT=Path(__file__).resolve().parents[1]
TOKENS={"editor":"e"*40,"reviewer":"r"*40,"publisher":"p"*40}
@pytest.fixture
def client(tmp_path):
    app=create_app(tmp_path/'test.sqlite3',TOKENS,ROOT/'content/seed.json')
    with TestClient(app) as client:yield client
@pytest.fixture
def headers():return {"Authorization":"Bearer "+TOKENS['editor']}
def auth(role):return {"Authorization":"Bearer "+TOKENS[role]}
