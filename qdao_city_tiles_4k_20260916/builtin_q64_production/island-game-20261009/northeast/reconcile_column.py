from native_work import *
p=ZONE/'selection-r03_c13.json'; q=read(p)
for i in range(1,4): q['cores'][i][0]=f'r03_c13_p{i+1:02}_01'
write(p,q)
p=ZONE/'progress.json'; q=read(p); recs=[read(p) for p in (ZONE/'native').glob('*.png.generation.json')]; usable=[r for r in recs if r['status'].startswith(('usable_native','usable_seed'))]; q['generatedNativeCount']=len(recs); q['usableNativeCount']=len(usable); q['usableCorePatchCount']=sum('_cross_' not in r['id'] for r in usable); q['usableRepairOverlayCount']=sum('_cross_' in r['id'] for r in usable); q['currentPatch']='r03_c13_p02_02'; q['status']='retrying_transient_network_error'; q['errors'].append({'stage':'r03_c13_p02_02 attempt1','error':'image generation failed: network error: error sending request','resolved':False,'retry':'same builtin input'}); q['updatedAtUtc']=now(); write(p,q)
