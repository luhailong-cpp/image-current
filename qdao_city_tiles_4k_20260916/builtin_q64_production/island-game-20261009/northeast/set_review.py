from native_work import *
import sys
a,b,note=sys.argv[1:4]
p=ZONE/'qa'/f'{a}__{b}.json'; r=read(p); r.update({'status':'passed_internal_only','reviewedAtUtc':now(),'geometryChecks':{'visibleArchitecture':'pass','visibleContours':'pass'},'color':'pass_with_minor_brushwork_variation','notes':note}); write(p,r)
for ident in [a,b]:
    p=ZONE/'native'/f'{ident}.png.generation.json'; r=read(p); r['status']='usable_native_with_required_overlay' if r.get('requiredOverlay') else 'usable_native_candidate'; r['internalSeams']='reviewed joins pass; other edges pending'; write(p,r)
s=read(ZONE/'progress.json'); usable=[read(p) for p in (ZONE/'native').glob('*.png.generation.json') if read(p).get('status','').startswith(('usable_native','usable_seed'))]; s['usableNativeCount']=len(usable); s['usableCorePatchCount']=sum('_cross_' not in q['id'] for q in usable); s['usableRepairOverlayCount']=sum('_cross_' in q['id'] for q in usable); s['updatedAtUtc']=now(); write(ZONE/'progress.json',s)
if a.split('_p')[0]!=b.split('_p')[0]:
    p=ZONE/'qa'/f'{a}__{b}.json'; q=read(p); q['status']='passed_cross_tile_core_segment_only'; q['scope']='one1024 segment of shared4096tile edge; not full formal acceptance'; write(p,q)
