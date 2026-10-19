"""Strict checks of reopened native scenery and unchanged gameplay-anchor evidence."""
import math

def validate(report):
    if report.get('status')!='reopened':raise ValueError('Native reopen incomplete')
    if len(report.get('maps',[]))!=2:raise ValueError('Expected both route maps')
    for mesh in report.get('meshes',[]):
        counts=mesh.get('lod_vertices',[])
        if len(counts)!=3 or any(type(v)!=int or v<=0 for v in counts)or not(counts[0]>=counts[1]>=counts[2]):raise ValueError('Missing/invalid conventional LODs')
        if mesh.get('nanite_enabled')is not False:raise ValueError('Conventional mesh baseline required')
    if len(report.get('meshes',[]))<8:raise ValueError('Missing materialized meshes')
    for row in report['maps']:
        if row.get('anchor_differences')!=[]:raise ValueError('Gameplay anchors changed')
        if row.get('instances',0)<=0 or row.get('simple_collision_boxes',0)<=0:raise ValueError('Missing scenery/collision')
        if row.get('unexpected_visual_collision')!=[]:raise ValueError('Scenery owns blocking collision')
    return True

def summarize_samples(samples):
    if not samples:raise ValueError('No runtime samples')
    for s in samples:
        for k in ['active_seconds','game_delta_ms','last_frame_rhi_draw_calls','last_frame_rhi_primitives','process_physical_bytes']:
            v=s.get(k)
            if not isinstance(v,(float,int))or not math.isfinite(v)or v<0:raise ValueError('Invalid runtime sample: '+k)
    def p95(v):return sorted(v)[min(len(v)-1,math.ceil(len(v)*.95)-1)]
    return {'samples':len(samples),'sampled_game_delta_p95_ms':p95([s['game_delta_ms']for s in samples]),'last_frame_rhi_draw_calls_p95':p95([s['last_frame_rhi_draw_calls']for s in samples]),'last_frame_rhi_primitives_p95':p95([s['last_frame_rhi_primitives']for s in samples]),'process_physical_peak_bytes':max(s['process_physical_bytes']for s in samples),'scope':'One-second game-thread samples of previous render-frame counters; screenshot overhead included; not GPU timing, long-session memory or mobile qualification'}
