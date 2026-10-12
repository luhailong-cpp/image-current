from native_work import *
import re, shutil, numpy as np
recorded=now()
rp=ZONE/'qa/color-repairs-20261011-merge.json'
r=read(rp)
for t in r['tiles']:
 assert sha(t['file'])==t['sha256']
 t['independentRootReview']='passed native bottle whole object and4perimeters; gourd6outer strips+2internal boundaries+2horizontal band strips; updated full4096shared border4segments'
 t['independentRootReviewedAtUtc']=recorded
r['status']='passed_internal_color_repairs_and_root_independent_review'
r['rootIndependentReviewedAtUtc']=recorded
write(rp,r)
# Preserve the successful first native of this new round as exact evidence.
native=ZONE/'native/r05_c12_p02_04.png'
meta=read(native.with_suffix('.png.generation.json'))
assert sha(native)==meta['sha256']=='c80e506c3edffb93853a5291aa132ccfd3a50e9cd87202c0491e93b0f41ca33a'
write(ZONE/'qa/builtin-resumed-round2-20261011.json',{'id':meta['id'],'file':native.as_posix(),'sha256':meta['sha256'],'generatedAtUtc':meta['generatedAt'],'actualModel':None,'actualQuality':None,'receipt':meta['evidence']['receipt'],'previousBlockResolved':True,'status':'real_builtin_output_saved_and_upper_join_passed','recordedAtUtc':recorded})
source=(ZONE/'export_local_candidate_group.py').read_text(encoding='utf-8-sig')
source=source.replace('20261011-local-v1','20261011-local-v2')
source=source.replace("'continuous_native_candidate_with_two_internal_color_repairs_pending'","'continuous_native_candidate_all_six_internal_passed'")
source=source.replace("'currentlyInternalPassedTiles':4","'currentlyInternalPassedTiles':6").replace("'internalPassedTiles':4","'internalPassedTiles':6")
source=source.replace("'internalColorRepairTiles':['r03_c12','r03_c13']","'internalColorRepairTiles':[]")
source=source.replace("'knownDefects':[{'tileIds':['r03_c12','r03_c13'],'issue':'gold gourd horizontal color band around tile-localy2048'},{'tileIds':['r03_c12'],'issue':'slender clay bottle horizontal color band around tile-localy3072'}]","'knownDefects':[]")
source=source.replace("'outerAdjacentTileEdgesNotFullyAcceptedCount':8","'outerAdjacentTileEdgesNotFullyAcceptedCount':6")
exec(compile(source,'export-local-v2','exec'))
indexpath=ZONE/'exports/20261011-local-v2/delivery-index.json'
index=read(indexpath)
index['repairVerification']=rp.as_posix()
index['externalNorthReview']=str(ZONE/'qa/cross-zone-20261011/review.json')
index['externalNorthPixelsUnchangedAfterRepairs']=True
index['supersedes']=str(ZONE/'exports/20261011-local-v1/delivery-index.json')
write(indexpath,index)
print('Root repair QA and v2 export saved')

