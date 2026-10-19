"""Review record validation; technical evidence cannot grant creative approval."""
GATES=frozenset(['reference_likeness','silhouette','face','hands_digits','prop_contact','clothing_deformation','limb_deformation','material_quality','cinematic_readability','gameplay_readability','source_scene_verified','package_verified'])
STATUSES=frozenset(['PASS','FAIL','BLOCKED','REVIEW_REQUIRED'])
def validate_review(record):
 errors=[]
 if set(record.get('gates',{}))!=GATES:errors.append('Exactly twelve separate gates required')
 for name,row in record.get('gates',{}).items():
  if not isinstance(row,dict)or row.get('status')not in STATUSES or not row.get('reason'):errors.append('Invalid status/reason: '+name)
 if record.get('human_creative_approval')is not False:errors.append('Human approval is not granted by this review pass')
 if record.get('gates',{}).get('reference_likeness',{}).get('status')!='REVIEW_REQUIRED':errors.append('Likeness requires human review')
 if not record.get('source_scene_sha256')or len(record['source_scene_sha256'])!=64:errors.append('Exact source scene identity required')
 if record.get('gates',{}).get('package_verified',{}).get('status')=='PASS'and not record.get('package_elf_sha256'):errors.append('Executed package identity required')
 if record.get('final_character_accepted')is not False:errors.append('This pass cannot mark a character final')
 return errors
