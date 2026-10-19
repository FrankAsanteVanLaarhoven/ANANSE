import copy
from scripts.visual_acceptance_contract import GATES,validate_review

def review():return {'gates':{g:{'status':'REVIEW_REQUIRED','reason':'Pending specific visual evidence'}for g in GATES},'source_scene_sha256':'a'*64,'human_creative_approval':False,'final_character_accepted':False}
def test_visual_review_keeps_human_gate_open():assert not validate_review(review())
def test_visual_review_rejects_unapproved_likeness_pass():
 r=review();r['gates']['reference_likeness']['status']='PASS';assert validate_review(r)
def test_visual_review_requires_all_separate_gates():
 r=review();del r['gates']['hands_digits'];assert validate_review(r)
def test_visual_review_rejects_automatic_final_acceptance():
 r=review();r['final_character_accepted']=True;assert validate_review(r)
def test_visual_review_requires_package_identity_for_technical_pass():
 r=review();r['gates']['package_verified']['status']='PASS';assert validate_review(r);r['package_elf_sha256']='b'*64;assert not validate_review(r)
def test_visual_review_preserves_failure_and_blocked_statuses():
 r=review();r['gates']['face']['status']='FAIL';r['gates']['prop_contact']['status']='BLOCKED';assert not validate_review(r)

def test_visual_package_requires_current_revision_maps(tmp_path):
 from scripts.unreal import required_visual_review_maps
 expected=['/Game/Ananse/Maps/Visual_v003/L_CharacterVisualReview','/Game/Ananse/Maps/Visual_v003/L_LeopardVisualContact']
 for path in expected:
  p=tmp_path/(path.removeprefix('/Game/')+'.umap');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'materialized test map')
 assert required_visual_review_maps(tmp_path)==expected

def test_visual_package_rejects_old_revision_only(tmp_path):
 import pytest
 from scripts.unreal import required_visual_review_maps
 for name in ['L_CharacterVisualReview','L_LeopardVisualContact']:
  p=tmp_path/'Ananse/Maps/Visual_v001'/(name+'.umap');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'old revision')
 with pytest.raises(RuntimeError,match='Visual_v003'):required_visual_review_maps(tmp_path)


def test_build_identity_includes_untracked_leopard_scene_and_derivative(tmp_path,monkeypatch):
 from scripts import native_runtime_smoke as smoke
 import hashlib
 monkeypatch.setattr(smoke,'ROOT',tmp_path)
 monkeypatch.setattr(smoke.subprocess,'check_output',lambda *args,**kwargs:'test\n')
 for relative in ['Unreal/Ananse.uproject','toolchain.lock.json','Unreal/Content/Data/catalogue.json','SourceArt/Characters/OseboLeopard/Authored_v013/OseboLeopard.blend','SourceArt/Characters/OseboLeopard/Authored_v013/NativeCapture/OseboCapture.glb']:
  p=tmp_path/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(relative.encode())
 result=smoke.build_input_identity()
 for relative in ['SourceArt/Characters/OseboLeopard/Authored_v013/OseboLeopard.blend','SourceArt/Characters/OseboLeopard/Authored_v013/NativeCapture/OseboCapture.glb']:
  assert result['authored_model_files'][relative]==hashlib.sha256(relative.encode()).hexdigest()


def test_art_pass2_cook_requires_all_three_actual_maps(tmp_path):
 from scripts.unreal import required_art_pass2_maps,ART_PASS2_MAPS
 import pytest
 with pytest.raises(RuntimeError,match='Art Pass2'):required_art_pass2_maps(tmp_path)
 for path in ART_PASS2_MAPS:
  p=tmp_path/(path.removeprefix('/Game/')+'.umap');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'new map')
 assert required_art_pass2_maps(tmp_path)==list(ART_PASS2_MAPS)
