"""Synthetic tests of the evidence checker. These are NOT game/device results."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("production_finish_gate", ROOT / "scripts/production_finish_gate.py")
G = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(G)
COMMIT = "a" * 40
CONTENT = "b" * 64

@pytest.fixture
def sample(tmp_path):
    def file(name, data):
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data, encoding="utf-8")
        return {"path":name,"sha256":G.digest(p)}
    raw = file("proofs/raw.log", "SYNTHETIC FIXTURE; NOT AN ENGINE RUN\n")
    proof = {"gate_id":"mission","source_commit":COMMIT,"content_sha256":CONTENT,
             "release_id":"test","run_id":"synthetic-1","status":"pass","exit_code":0,
             "timed_out":False,"forced_termination":False,"assertions":{"restart":True},
             "raw_files":[raw]}
    pf = file("proofs/run.json",json.dumps(proof))
    asset={"quality":"production","runtime":file("assets/test.uasset","synthetic asset"),
           "rights":file("assets/rights.txt","synthetic rights"),
           "review":file("assets/review.txt","synthetic review")}
    c={"schema_version":1,"release_id":"test","gates":[{"id":"mission","required_checks":["restart"],"min_tests_executed":1}],"required_asset_ids":["HERO"]}
    e={"schema_version":1,"release_id":"test","source_commit":COMMIT,"content_sha256":CONTENT,
       "dirty_tree":False,"gates":{"mission":{"status":"pass","tests_executed":1,
       "checks":{"restart":True},"proofs":[pf]}},"assets":{"HERO":asset}}
    def rewrite_proof(**changes):
        proof.update(changes)
        e["gates"]["mission"]["proofs"]=[file("proofs/run.json",json.dumps(proof))]
    return tmp_path,c,e,rewrite_proof

def result(s):
    r,c,e,_=s
    return G.validate(c,e,r,COMMIT)

def test_consistent_synthetic_fixture(sample):
    assert result(sample)["status"]=="evidence_consistent"

@pytest.mark.parametrize("status",["fail","blocked","not_run","skip","passed",None])
def test_nonpass_is_not_ready(sample,status):
    sample[2]["gates"]["mission"]["status"]=status
    assert result(sample)["status"]=="blocked"

@pytest.mark.parametrize("count",[0,-1,True,"1",1.1,None])
def test_executed_count_must_be_positive_integer(sample,count):
    sample[2]["gates"]["mission"]["tests_executed"]=count
    assert result(sample)["status"]=="blocked"

@pytest.mark.parametrize("field,value",[("source_commit","c"*40),("content_sha256","c"*64),("gate_id","art"),("release_id","other"),("status","fail"),("exit_code",124),("exit_code",False),("timed_out",True),("forced_termination",True),("run_id",""),("assertions",{}),("raw_files",[])])
def test_bad_proof_rejected(sample,field,value):
    sample[3](**{field:value})
    assert result(sample)["status"]=="blocked"

def test_missing_gate(sample):
    sample[2]["gates"]={}
    assert result(sample)["status"]=="blocked"

def test_unknown_gate(sample):
    sample[2]["gates"]["shortcut"]={"status":"pass"}
    assert result(sample)["status"]=="blocked"

def test_missing_proofs(sample):
    sample[2]["gates"]["mission"]["proofs"]=[]
    assert result(sample)["status"]=="blocked"

def test_integer_truth_is_not_boolean(sample):
    sample[2]["gates"]["mission"]["checks"]["restart"]=1
    assert result(sample)["status"]=="blocked"

def test_changed_raw_log(sample):
    (sample[0]/"proofs/raw.log").write_text("modified after hashing")
    assert result(sample)["status"]=="blocked"

def test_changed_asset(sample):
    (sample[0]/"assets/test.uasset").write_text("modified after hashing")
    assert result(sample)["status"]=="blocked"

def test_proxy_cannot_pass_asset_gate(sample):
    sample[2]["assets"]["HERO"]["quality"]="engineering_proxy"
    assert result(sample)["status"]=="blocked"

@pytest.mark.parametrize("path",["../outside", "/etc/passwd", "assets/../../outside", "https://example.com/x", "C:\\x"])
def test_asset_reference_must_stay_local(sample,path):
    sample[2]["assets"]["HERO"]["runtime"]["path"]=path
    assert result(sample)["status"]=="blocked"

def test_symlink_rejected(sample):
    r=sample[0]; p=r/"assets/test.uasset"; p.unlink()
    p.symlink_to(r/"assets/rights.txt")
    sample[2]["assets"]["HERO"]["runtime"]["sha256"]=G.digest(p)
    assert result(sample)["status"]=="blocked"

def test_lfs_pointer_rejected_even_with_matching_hash(sample):
    p=sample[0]/"assets/test.uasset";p.write_bytes(G.LFS_PREFIX+b"\noid sha256:test\nsize 5\n")
    sample[2]["assets"]["HERO"]["runtime"]["sha256"]=G.digest(p)
    assert result(sample)["status"]=="blocked"

def test_empty_file_rejected(sample):
    p=sample[0]/"assets/test.uasset";p.write_text("")
    sample[2]["assets"]["HERO"]["runtime"]["sha256"]=G.digest(p)
    assert result(sample)["status"]=="blocked"

def test_bad_root_commit(sample):
    sample[2]["source_commit"]="0"*40
    assert result(sample)["status"]=="blocked"

def test_dirty_tree_rejected(sample):
    sample[2]["dirty_tree"]=True
    assert result(sample)["status"]=="blocked"

def test_contract_cannot_remove_all_gates(sample):
    sample[1]["gates"]=[]
    with pytest.raises(ValueError): result(sample)

def test_duplicate_gate_rejected(sample):
    sample[1]["gates"]*=2
    with pytest.raises(ValueError): result(sample)

def test_missing_asset(sample):
    sample[2]["assets"]={}
    assert result(sample)["status"]=="blocked"

@pytest.mark.parametrize("text",['{"a":1,"a":2}', '{"value": NaN}', '[]'])
def test_json_structure_errors(tmp_path,text):
    p=tmp_path/"x.json";p.write_text(text)
    with pytest.raises(ValueError):G.load_json(p)

def test_bom_supported(tmp_path):
    p=tmp_path/"x.json";p.write_text('\ufeff{"a":1}')
    assert G.load_json(p)=={"a":1}

def test_report_not_overwritten(sample):
    r,c,e,_=sample
    (r/"c.json").write_text(json.dumps(c));(r/"e.json").write_text(json.dumps(e))
    out=r/"report.json";out.write_text("protected")
    p=subprocess.run([sys.executable,str(ROOT/"scripts/production_finish_gate.py"),"--contract",str(r/"c.json"),"--evidence",str(r/"e.json"),"--root",str(r),"--candidate-commit",COMMIT,"--out",str(out)],capture_output=True,text=True)
    assert p.returncode==2
    assert out.read_text()=="protected"

def test_delivered_template_blocks():
    c=G.load_json(ROOT/"production/release_contract.json")
    e=G.load_json(ROOT/"production/release_evidence.example.json")
    report=G.validate(c,e,ROOT,COMMIT)
    assert report["status"]=="blocked"
    assert report["gate_count"]==10
    assert report["required_asset_count"]==36

def test_dialogue_ids_unique_and_shots_resolve():
    d=G.load_json(ROOT/"production/market/dialogue.en.json")
    s=G.load_json(ROOT/"production/market/shots.json")
    ids=[i["id"] for i in d["lines"]]
    assert len(ids)==len(set(ids))
    for shot in s["shots"]:
        assert shot["out_seconds"]>shot["in_seconds"]>=0
        assert set(shot["dialogue_ids"])<=set(ids)

def test_shots_have_no_overlaps_in_sequence():
    s=G.load_json(ROOT/"production/market/shots.json")
    groups={}
    for shot in s["shots"]:groups.setdefault(shot["sequence"],[]).append(shot)
    for shots in groups.values():
        ordered=sorted(shots,key=lambda s:s["in_seconds"])
        assert ordered[0]["in_seconds"]==0
        for left,right in zip(ordered,ordered[1:]):
            assert left["out_seconds"]==right["in_seconds"]

def test_mission_and_audio_structure():
    m=G.load_json(ROOT/"production/market/mission_spec.json")
    ids={i["id"] for i in m["beats"]}
    assert len(ids)==len(m["beats"])
    assert all(i["next"] in ids for i in m["beats"])
    assert len(m["routes"])==3 and len(m["outcomes"])==2
    a=G.load_json(ROOT/"production/market/audio_cues.json")
    assert len({i["id"] for i in a["cues"]})==len(a["cues"])
    assert all(i["asset_status"]=="missing" for i in a["cues"])
