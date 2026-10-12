from native_work import *
for tid in ['r03_c12','r04_c12']:
 p=ZONE/'tiles'/f'{tid}.png.derivation.json';d=read(p);d.update(internalReview='passed',status='internal_candidate_passed',reviewRecord=(ZONE/'qa'/f'{tid}-v4-bridge-final-review.json').as_posix(),externalSeams='shared r03_c12/r04_c12 full4096 passed; other adjacent boundaries tracked separately',formalAccepted=False);write(p,d)
 p=ZONE/'qa'/f'{tid}-v4-bridge-final-review.json';q=read(p);q.update(status='passed_internal_visual_and_native_provenance',changedCropReview='root viewed four affected1024 core crops, affected vertical join, full4096 shared edge in four1:1 segments and combined preview',reviewedAtUtc=now());write(p,q)
p=ZONE/'qa/connected-area/r03-r04_c12-c12.json';q=read(p);q.update(status='passed_full_shared_edge_and_preview',reviewer='root',reviewedAtUtc=now())
for seg in q['seamEvidence']:seg['status']='passed_visual_100pct';seg['sha256']=sha(seg['file'])
write(p,q)
for tids,name,size in [(['r03_c12','r03_c13'],'r03_c12-r03_c13-adjacent-preview.png',(2048,1024)),(['r03_c12','r03_c13','r03_c14'],'r03_c12-c14-contiguous-preview.png',(3072,1024))]:
 im=Image.new('RGB',(4096*len(tids),4096))
 for i,t in enumerate(tids):im.paste(Image.open(ZONE/'tiles'/f'{t}.png'),(i*4096,0))
 im.resize(size,Image.Resampling.LANCZOS).save(ZONE/'qa'/name)
 if len(tids)==2:im.save(ZONE/'qa/r03_c12-r03_c13-adjacent-context.png')
print('r03_c12 + r04_c12 internal review passed, full shared4096 passed')

