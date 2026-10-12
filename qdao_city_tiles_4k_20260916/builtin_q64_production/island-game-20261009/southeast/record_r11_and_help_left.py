from workflow import *
from PIL import Image
src=ROOT/'tiles/r11_c12.candidate-v01.png'
review={'tile':'r11_c12','candidate':str(src),'candidateSha256':sha(src),'reviewedAt':now(),'reviewer':'root','internalMajorGeometryPass':True,'sourceReplay':'qa/r11_c12-v01/prior-reviewed-pixel-replay.json','reusedPreviouslyReviewedIdenticalCrops':17,'newlyReviewedSeams':['h32','h33','h41','h42','h43','v23','v24','v31','v32','v33','v34'],'newlyReviewedJunctions':['22','23','31','32','33'],'totalInternalSeamsReviewed':24,'totalJunctionsReviewed':9,'northEdge':{'neighbor':'tiles/r10_c12.candidate-v02.png','review':'qa/r11_c12-v01/north-edge.json','coveragePixels':4096,'majorGeometryPass':True},'observations':['Lantern jambs, oblique crossrails, dock railing and deck board contours are continuous in inspected actual-candidate native crops.','Minor hand-painted material variation remains, no obvious hard rectangular tonal border found in new crops.','Six new cores are original builtin imagegen pixels, assembled without resampling, feathering or painting.'],'formalAccepted':False,'unreviewedExternalEdges':['west','east','south']}
write(ROOT/'qa/r11_c12.root-review-v01.json',review)
s=read(ROOT/'selection-r11_c12.json');s['status']='internal_and_north_major_geometry_pass';s['candidate']=str(src);s.pop('partialAssembly',None);write(ROOT/'selection-r11_c12.json',s)
d=read(ROOT/'production-state.json');d['rootActiveTile']={'id':'r11_c12','selectedVersions':s['patchVersions'],'candidate':str(src),'sha256':sha(src),'remaining':[],'inFlight':None,'internalPass':True,'northEdgePass':True,'review':'qa/r11_c12.root-review-v01.json','formalAccepted':False};d['complete4kCandidates']=6;d['internalPassed4kCount']=4;d['actualProgress']='active_production';d['updatedAt']=now();d['nextRootWork']='Help r10c11 left column p11,p21,p31,p41 in current contiguous queue'
for w in d['parallelWorkers']:w['notes']=w['notes'].replace('; held.','; resumed.').replace(', held.',', resumed.')
write(ROOT/'production-state.json',d)
p=read(ROOT/'progress.json');p.update({'status':'r11c12_complete_internal_and_north_pass','currentTile':'r11_c12','generatedNativeCount':len(list((ROOT/'native').glob('*.png'))),'complete4kCount':6,'internalPassed4kCount':4,'formalAcceptedCount':0,'nextStep':'Assist assigned r10c11 left column; close current 2x2 neighborhood','updatedAt':now()});write(ROOT/'progress.json',p)
helper=dict(p);helper.update({'currentTile':'r10_c11','assignedPatches':['11','21','31','41'],'generatedNativeCount':0,'status':'helper_preparing','complete4kCount':0});write(ROOT/'progress-helper-r10_c11.json',helper)
context('r10_c11_p11',['r09_c11_p41_v01.png'])
print('r11c12 review and state saved; r10c11 p11 context ready')

