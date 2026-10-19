"""Historical revision preservation and refined-source/path isolation."""
import copy,hashlib
import pytest
from pydantic import ValidationError
from studio.models import Asset,STORY_REFINEMENTS
from studio.visuals import preview_source
from studio.store import DomainError
from studio.models import STORY_DESIGNS
import json

def record(design):
 key,source=STORY_DESIGNS[design];base=f"/Game/Ananse/Characters/{key}/Story_v001/"
 return {'data':{'name':key,'category':'skeletal-mesh','unreal_path':base+key+'.'+key,'visual_design':{'design_id':design,'skeleton_key':key+'-independent-v001','definition_path':base+'DA_'+key+'.DA_'+key,'source_revision':source,'source_glb_sha256':hashlib.sha256(b'actual-local-bytes').hexdigest()}}}

def complete_report():
 rows=[]
 for design,(key,source)in STORY_DESIGNS.items():
  base=f"/Game/Ananse/Characters/{key}/Story_v001/";row={'design':design,'mesh':base+key+'.'+key,'pawn_class':base+'BP_'+key+'.BP_'+key+'_C','animation_instance':base+'ABP_'+key+'.ABP_'+key+'_C','complete_round_trips':20,'movement_cm':100,'bones':48,'clips':[{'clip':base+str(i),'graph_and_pose_observed':True}for i in range(8)]}
  if key!='EsiMoth':row['flat_contact_metrics']=json.dumps({'invalid_transforms':0,'solved_chains':2,'legs':[{'samples':100,'p95_stance_drift_cm':1,'max_penetration_cm':.1,'max_segment_length_error_cm':0}for _ in range(2)]})
  rows.append(row)
 return {'passed':True,'seconds':60,'designs':rows}
from scripts.run_story_cast_check import validate

def refined():
 r=record('kwaku-human-v1');binding=STORY_REFINEMENTS[('kwaku-human-v1','authored-v006')];r['data']['unreal_path']=binding['mesh'];r['data']['visual_design'].update(definition_path=binding['definition'],source_revision='authored-v006');return r

def test_old_and_refined_revisions_validate_without_identity_change():
 for r in [record('kwaku-human-v1'),refined()]:assert Asset.model_validate(r['data']).visual_design.skeleton_key=='Kwaku-independent-v001'

@pytest.mark.parametrize('field,value',[('source_revision','authored-v007'),('definition_path','/Game/Ananse/Characters/Kwaku/Story_v001/DA_Kwaku.DA_Kwaku'),('skeleton_key','ananse-eight-limb-v002')])
def test_refined_binding_cannot_mix_revision_or_family(field,value):
 r=refined();r['data']['visual_design'][field]=value
 with pytest.raises(ValidationError):Asset.model_validate(r['data'])

def test_refined_mesh_cannot_use_old_preview_bytes(tmp_path):
 r=refined();p=tmp_path/'SourceArt/Characters/Kwaku/Authored_v006/Kwaku.glb';p.parent.mkdir(parents=True);p.write_bytes(b'actual-local-bytes');assert preview_source(tmp_path,r)[0]==p
 p.write_bytes(b'old-or-corrupt-source')
 with pytest.raises(DomainError):preview_source(tmp_path,r)

def refined_report():
 r=complete_report();d=r['designs'][0];base='/Game/Ananse/Characters/Kwaku/Refined_v001/';d.update(mesh=base+'Kwaku.Kwaku',pawn_class=base+'BP_Kwaku.BP_Kwaku_C',refined_face_bindings=True,applied_blink_peak=.99,definition_revision=2,published_visual_revision=2);return r

def test_refined_report_requires_explicit_revision_and_expression_evidence():
 r=refined_report();assert validate(r,0,True);assert not validate(r,0);assert not validate(complete_report(),0,True)
 for field,value in [('refined_face_bindings',False),('applied_blink_peak',0)]:
  changed=copy.deepcopy(r);changed['designs'][0][field]=value;assert not validate(changed,0,True)


def test_checker_rejects_a_stale_publication_even_with_valid_paths():
 r=refined_report();r['loaded_publication_hash']='a'*64;assert validate(r,0,True,'a'*64);assert not validate(r,0,True,'b'*64)


def test_checker_rejects_the_observed_cooked_morph_material_fallback():
 r=refined_report();r['material_fallback_warnings']=['Material /Game/Ananse/Characters/Kwaku/Refined_v001/Skin.Skin missing usage flag MorphTargets! Default Material will be used in game.'];assert not validate(r,0,True)

def repaired():
 r=refined();binding=STORY_REFINEMENTS[('kwaku-human-v1','authored-v008')];r['data']['unreal_path']=binding['mesh'];r['data']['visual_design'].update(definition_path=binding['definition'],source_revision='authored-v008');return r

def test_repaired_revision_preserves_family_and_requires_exact_source_bytes(tmp_path):
 r=repaired();assert Asset.model_validate(r['data']).visual_design.skeleton_key=='Kwaku-independent-v001'
 p=tmp_path/'SourceArt/Characters/Kwaku/Authored_v008/Kwaku.glb';p.parent.mkdir(parents=True);p.write_bytes(b'actual-local-bytes');assert preview_source(tmp_path,r)[0]==p
 p.write_bytes(b'previous-revision')
 with pytest.raises(DomainError):preview_source(tmp_path,r)

@pytest.mark.parametrize('field,value',[('source_revision','authored-v006'),('definition_path','/Game/Ananse/Characters/Kwaku/Refined_v001/DA_Kwaku.DA_Kwaku'),('skeleton_key','osebo-feline-biped-v001')])
def test_repaired_revision_rejects_mixed_source_definition_and_family(field,value):
 r=repaired();r['data']['visual_design'][field]=value
 with pytest.raises(ValidationError):Asset.model_validate(r['data'])

def test_repaired_report_rejects_previous_revision_and_missing_expression():
 r=refined_report();d=r['designs'][0];base='/Game/Ananse/Characters/Kwaku/Refined_v002/';d.update(mesh=base+'Kwaku.Kwaku',pawn_class=base+'BP_Kwaku.BP_Kwaku_C',definition_revision=3,published_visual_revision=3)
 assert validate(r,0,forms_scenery=True);assert not validate(r,0,True)
 for field,value in [('definition_revision',2),('published_visual_revision',2),('refined_face_bindings',False),('applied_blink_peak',0)]:
  bad=copy.deepcopy(r);bad['designs'][0][field]=value;assert not validate(bad,0,forms_scenery=True)

def interaction_record():
 r=record('kwaku-human-v1');b=STORY_REFINEMENTS[('kwaku-human-v1','authored-v016')];r['data']['unreal_path']=b['mesh'];r['data']['visual_design'].update(definition_path=b['definition'],source_revision='authored-v016');return r

def test_interaction_revision_preview_rejects_old_source_bytes(tmp_path):
 r=interaction_record();assert Asset.model_validate(r['data']).visual_design.skeleton_key=='Kwaku-independent-v001'
 p=tmp_path/'SourceArt/Characters/Kwaku/Authored_v016/Kwaku.glb';p.parent.mkdir(parents=True);p.write_bytes(b'actual-local-bytes');assert preview_source(tmp_path,r)[0]==p
 p.write_bytes(b'accepted-older-body')
 with pytest.raises(DomainError):preview_source(tmp_path,r)

def interaction_report():
 r=refined_report();d=r['designs'][0];base='/Game/Ananse/Characters/Kwaku/Interactions_v005/';d.update(mesh=base+'Kwaku.Kwaku',pawn_class=base+'BP_Kwaku.BP_Kwaku_C',definition_revision=5,published_visual_revision=5,separate_ledger_attached_observed=True,ledger_reset_cleared=True);d['clips'].append({'clip':'/Game/Ananse/Characters/Kwaku/Interactions_v003/KwakuInspectLedger.KwakuInspectLedger','graph_and_pose_observed':True,'separate_ledger_attached_observed':True,'ledger_reset_cleared':True});return r

def test_interaction_report_requires_observed_prop_and_its_actual_clip():
 r=interaction_report();assert validate(r,0,interaction_refinement=True);assert not validate(r,0,forms_scenery=True)
 for mutate in ['prop','clip','revision','reset']:
  d=copy.deepcopy(r)
  if mutate=='prop':d['designs'][0]['separate_ledger_attached_observed']=False
  elif mutate=='clip':d['designs'][0]['clips'][-1]['clip']='/Game/Ananse/Characters/Kwaku/Story_v001/KwakuInspectLedger.KwakuInspectLedger'
  elif mutate=='reset':d['designs'][0]['ledger_reset_cleared']=False
  else:d['designs'][0]['definition_revision']=3
  assert not validate(d,0,interaction_refinement=True)
