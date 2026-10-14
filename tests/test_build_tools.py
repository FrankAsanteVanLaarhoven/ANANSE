import json,os,subprocess,sys
from pathlib import Path
from scripts.unreal import environment,paths
ROOT=Path(__file__).resolve().parents[1]
def test_preflight_fails_honestly_without_engine(monkeypatch):
    monkeypatch.delenv('UE_ROOT',raising=False);report=environment();assert report['engine_installed'] is False and report['blockers']
def test_preflight_rejects_other_engine_family(tmp_path,monkeypatch):
    path=tmp_path/'Engine/Build';path.mkdir(parents=True);(path/'Build.version').write_text(json.dumps({'MajorVersion':5,'MinorVersion':7}))
    monkeypatch.setenv('UE_ROOT',str(tmp_path));report=environment();assert report['engine_installed'] and report['blockers']
def test_host_paths():
    root=Path('/engine');assert str(paths(root,'Win64')[0]).endswith('Build.bat');assert str(paths(root,'Mac')[2]).endswith('MacOS/UnrealEditor');assert str(paths(root,'Linux')[0]).endswith('Linux/Build.sh')
def test_mobile_configuration_is_explicit():
    text=(ROOT/'Unreal/Config/DefaultEngine.ini').read_text();assert 'TargetSDKVersion=36' in text and 'r.DynamicGlobalIlluminationMethod=0' in text

def test_generated_map_not_silently_overwritten():assert "ANANSE_REGENERATE_GREYBOX" in (ROOT/'scripts/build_greybox.py').read_text()


def test_http_report_is_never_overwritten(tmp_path):
    report=tmp_path/'http-smoke.json';report.write_text('preserved evidence')
    result=subprocess.run([sys.executable,str(ROOT/'scripts/http_smoke.py'),'--out',str(tmp_path)],capture_output=True,text=True,timeout=10)
    assert result.returncode==1
    assert 'Evidence directory already contains smoke reports' in result.stderr
    assert report.read_text()=='preserved evidence'
    assert not (tmp_path/'http-server.log').exists()

def test_engine_report_is_never_overwritten(tmp_path):
    report=tmp_path/'unreal-doctor.json';report.write_text('preserved evidence')
    result=subprocess.run([sys.executable,str(ROOT/'scripts/unreal.py'),'doctor','--evidence-dir',str(tmp_path)],capture_output=True,text=True,timeout=10)
    assert result.returncode==2
    assert report.read_text()=='preserved evidence'
