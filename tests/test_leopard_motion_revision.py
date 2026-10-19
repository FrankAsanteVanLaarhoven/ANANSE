"""A historical mesh or fixture must not qualify the current leopard revision."""
from scripts.run_leopard_check import verify


def report():
    base = '/Game/Ananse/Characters/OseboLeopard/'
    return {'passed': True, 'normal_lit_rendering': True, 'seconds': 60,
        'world': '/Game/Ananse/Maps/ArtPass2_v003/L_LeopardArtContact.L_LeopardArtContact',
        'pawn_class': base + 'ArtPass2_v003/BP_OseboLeopard.BP_OseboLeopard_C',
        'mesh': base + 'ArtPass2_v003/OseboLeopard.OseboLeopard',
        'bones': 64, 'ability_grants': 0, 'movement_cm': 200, 'face_forward_alignment': 1,
        'animation_instance': base + 'Animations/ABP_OseboLeopard.ABP_OseboLeopard_C',
        'clips': [{'clip': base + ('Visual_v003/Capture_v002/OseboCapture.OseboCapture' if name=='CaptureReach' else 'Authored_v001/OseboLeopard' + name + '.OseboLeopard' + name),
                   'evaluated_bone_motion': True, 'graph_clip_observed': True}
                  for name in ['IdleGuard', 'Patrol', 'RunPursuit', 'TurnStop', 'Investigate',
                               'CaptureReach', 'StaggerRecover', 'Command', 'LimbIsolation']]}


def test_current_motion_fixture_requires_current_revision_mode():
    assert verify(report(), 0, True)
    assert not verify(report(), 0)


def test_old_mesh_cannot_qualify_current_motion_check():
    r = report();r['mesh'] = '/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopard.OseboLeopard'
    assert not verify(r, 0, True)


def test_wrong_map_cannot_qualify_current_motion_check():
    r = report();r['world'] = '/Game/Ananse/Maps/CharacterLabs/L_OseboLeopardCharacterLab.L_OseboLeopardCharacterLab'
    assert not verify(r, 0, True)


def test_current_mesh_still_requires_all_nine_evaluated_motions():
    r = report();r['clips'][-1]['graph_clip_observed'] = False
    assert not verify(r, 0, True)
    r = report();r['clips'].pop()
    assert not verify(r, 0, True)


def test_old_capture_clip_cannot_substitute_for_corrected_capture():
    r = report();r['clips'][5]['clip'] = '/Game/Ananse/Characters/OseboLeopard/Authored_v001/OseboLeopardCaptureReach.OseboLeopardCaptureReach'
    assert not verify(r, 0, True)

def test_same_motion_name_in_another_folder_is_rejected():
    r = report();r['clips'][0]['clip'] = '/Game/Wrong/OseboLeopardIdleGuard.OseboLeopardIdleGuard'
    assert not verify(r, 0, True)
