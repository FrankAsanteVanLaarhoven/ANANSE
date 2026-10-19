from scripts.run_secondary_review import validate

def report():
 return dict(passed=True,world='/Game/Ananse/Maps/EnvironmentRoute_v002/L_StoryForest_Route',secondary_disabled=False,seconds=12,cameras=[dict(horizontal_fov_degrees=50,location_cm='X=0 Y=0 Z=0',target_cm='X=100 Y=0 Z=0')for _ in range(3)],motion_clusters=[dict(mesh=f'/Game/Ananse/Environments/Motion_v001/{n}/{n}.{n}',actor_tick=False,collision=False,instances=1,materials=['/Game/Ananse/Environments/Motion_v001/Surface/M_Leaf.M_Leaf'])for n in ['CrownGuardian','RiverFig','TwinnedElder','StreamPools','EcologyIsland']])

def test_valid_binding_report():assert validate(report(),0,True,False)
def test_reject_missing_or_colliding_motion():
 r=report();r['motion_clusters']=[];assert not validate(r,0,True,False)
 r=report();r['motion_clusters'][0]['collision']=True;assert not validate(r,0,True,False)
def test_reject_wrong_fixture_and_nonfinite_time():
 r=report();assert not validate(r,0,False,False)
 r['seconds']=float('nan');assert not validate(r,0,True,False)
def test_reject_abnormal_exit_and_wrong_mode():
 assert not validate(report(),1,True,False)
 assert not validate(report(),0,True,True)
def test_reject_legacy_materials_bypassing_motion():
 r=report();r['motion_clusters'][0]['materials']=['/Game/Ananse/Environments/HeroCells_v004/Surface/M_Leaf.M_Leaf'];assert not validate(r,0,True,False)
def test_reject_missing_camera_settings():
 r=report();r['cameras']=[{}, {}, {}];assert not validate(r,0,True,False)

def test_accept_exact_preserved_override_namespace():
 r=report();r['motion_clusters'][0]['materials']=['/Game/Ananse/Environments/Motion_v001/Overrides/Ananse/Environments/HeroCells_v004/Surface/M_Leaf.M_Leaf'];assert validate(r,0,True,False)
