from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now,progress
audit={'reviewer':'root','reviewedAt':now(),'tile':'r10_c12','candidate':'tiles/r10_c12.candidate-v02.png','sha256':sha(ROOT/'tiles/r10_c12.candidate-v02.png'),'formalAccepted':False,'internalSeams':{'count':24,'status':'root_visual_pass_after_h12_native_repair','evidence':'qa/r10_c12-v01/seams.json plus qa/r10_c12-v02/h12.png and repair insertion QA','notes':'All24 actual candidate seam crops viewed at native resolution. h12 v01 rejected for vertical color cut/short truncated joint; v02 repairs it with a native512x1024 insert. Other23 seam areas not changed.'},'junctions':{'count':9,'status':'root_visual_pass','evidence':'qa/r10_c12.junction_11-v01.png through33, updated12-v02 rechecked'},'repairEdges':{'status':'root_visual_pass','evidence':'qa/r10_c12_h12-repair_v01.hard-insert.png','notes':'All four hard-insert edges checked in original1254 target context; no obvious color/geometry step observed.'},'northSharedEdge':{'status':'root_visual_pass','neighbor':'tiles/r09_c12.candidate-v02.png','evidence':'qa/r09_c12-v02-r10_c12-v02.south-border-1..4.png','notes':'Native1024x512 strips cover full4096 seam. Border1/4 unchanged fromv01;2/3 rechecked afterrepair.'},'remaining':['independent review','other three neighboring4k edges'],'pixelProvenance':'17 rectangles, coverage exactly once, source pixel-exact assertions passed'}
write(ROOT/'qa/r10_c12.root-review-v02.json',audit)
for rc,v in read(ROOT/'selection-r10_c12.json')['patchVersions'].items():
 p=ROOT/'native'/f'r10_c12_p{rc}_{v}.png.generation.json';d=read(p);d.update(status='selected_current_native_with_final_rectangle_ownership',formalAccepted=False,selectionRecord='selected-native-r10_c12.json');write(p,d)
for name,reason in [('r10_c12_p43_v01','Artificial straight strip on pillar and wall-cap step; replaced byv02'),('r10_c12_p11_v01','Invented carved posts; replaced byv02')]:
 p=ROOT/'native'/f'{name}.png.generation.json';d=read(p);d.update(status='rejected_superseded_native',rejectionReason=reason,formalAccepted=False);write(p,d)
p=ROOT/'native/r10_c12_h12-repair_v01.png.generation.json';d=read(p);d.update(status='selected_current_seam_repair',formalAccepted=False);write(p,d)
p=ROOT/'tiles/r10_c12.candidate-v01.png.generation.json';d=read(p);d.update(status='superseded_assembly_keep_text_record',replacedBy='tiles/r10_c12.candidate-v02.png');write(p,d)
s=read(ROOT/'production-state.json');s['updatedAt']=now();s['complete4kCandidates']=5;s['formalAcceptedCount']=0
s['rootActiveTile']={'id':'r10_c12','selectedVersions':read(ROOT/'selection-r10_c12.json')['patchVersions'],'inFlight':None,'latestCandidate':'tiles/r10_c12.candidate-v02.png','sha256':audit['sha256'],'nativeSeamRepair':'native/r10_c12_h12-repair_v01.png','review':'qa/r10_c12.root-review-v02.json','remaining':audit['remaining']}
s['parallelWorkers'][0]['notes']='4K complete; native local seam repairs ongoing, then r10_c11 assigned.'
s['parallelWorkers'][1]['notes']='4K complete; two local column seam repairs ongoing, then independent root tile review.'
s['parallelWorkers'][2]['notes']='r08_c12 complete candidate-v1; internal and shared southern edge review ongoing, then r08_c11 assigned.'
write(ROOT/'production-state.json',s)
progress(status='review_and_frontier_preparation',complete4kCount=5,formalAcceptedCount=0,generatedNativeCount=len(list((ROOT/'native').glob('*.png'))),usableNativeCount=32,latestCandidate='tiles/r10_c12.candidate-v02.png',rootVisualReviewed4kCount=2,currentTile='r11_c12',currentPatch=None,nextStep='Independently review root revisions while expanding native art south to r11_c12')
tid='r11_c12';tile=next(t for t in read(ROOT/'coordinate-plan.json')['tiles'] if t['id']==tid);refs=read(ROOT/'references.json')
box=[v*1254/57344 for v in tile['coreGlobalBox']]
out=ROOT/'qa'/f'{tid}.layout-preview.png';Image.open(refs[0]['file']).transform((1024,1024),Image.Transform.EXTENT,box,Image.Resampling.NEAREST).save(out)
write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'operation':'enlarged coordinate-only reference, never final art','source':refs[0],'sourceCrop':box})
print('Root checkpoint and r11c12 layout review saved')
