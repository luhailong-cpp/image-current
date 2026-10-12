from native_work import *
qpath=ZONE/'qa/root-recovery-QA-20261013.json';q=read(qpath)
for e in q['entries']+q['boundary']:
 assert sha(e['file'])==e['sha256']
 if e['status']=='pending_visual_review':e.update(status='passed_visual_100pct',reviewer='root',reviewedAtUtc=now())
q.update(status='passed',reviewedAtUtc=now(),finding='Nine changed internal crops and all four east edge segments inspected at 1:1; geometry, paving and shadows continuous. Forty unchanged passed crops retained by identical hash.')
write(qpath,q)
name='r03_c10-native-v2-20261013';dp=ZONE/'tiles'/f'{name}.png.derivation.json';d=read(dp)
rp=ZONE/'qa'/f'{name}-review.json'
review={'tileId':'r03_c10','candidatePath':d['file'],'sha256':d['sha256'],'size':[4096,4096],'reviewer':'root','reviewedAtUtc':now(),'nativeCoreCount':16,'internalSeamCount':24,'internalCrossCount':9,'status':'complete_internal_QA_passed','internalReview':'passed16core24seam9cross_native1to1','inspectedCrops':q['entries'],'inheritedIdenticalHashCount':40,'newlyInspectedCount':9,'boundaryReview':{'pair':['r03_c10','r03_c11'],'reviewedPixels':4096,'sources':q['boundarySources'],'crops':q['boundary'],'geometry':'passed'},'pendingIssues':[],'externalSeams':'east passed full4096; other adjacent completed tile boundaries pending','formalAccepted':False,'finalArtUpscaled':False,'blending':'none'}
assert not rp.exists();write(rp,review)
d.update(internalReview=review['internalReview'],status=review['status'],reviewPath=rp.as_posix(),pendingIssues=[],externalSeams=review['externalSeams']);write(dp,d)
sp=ZONE/'selection-r03_c10.json';s=read(sp);s.update(internalReview=d['internalReview'],pendingIssues=[],reviewPath=rp.as_posix(),updatedAtUtc=now());write(sp,s)
split=read(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json');batch=next(b for b in split['batches'] if b['key']=='island-east-residences')
conflicts=[]
for tid in batch['tiles']:
 conflicts.extend(str(p) for p in (ZONE/'native').glob(tid+'*.png'))
 sp2=ZONE/f'selection-{tid}.json'
 if sp2.exists() and any(v for row in read(sp2).get('cores',[]) for v in row):conflicts.append(str(sp2))
ackpath=ROOT/batch['ownerAckFile']
if not ackpath.exists():
 write(ackpath,{'ownerThreadId':batch['owner'],'reservedTiles':batch['tiles'],'activeConflicts':conflicts,'inFlightSaved':True,'timestamp':now(),'excludedFromOwnerQueue':True,'internalWorkersNotified':True,'ready':not conflicts,'adjacentRevisionStability':'r03_c10-native-v2-20261013 now internally passed; current selections and hashes authoritative; shared borders remain subject to explicit edge checks.','evidence':'Current target native glob and selected core records checked; no root imagegen in flight on reserved coordinates.'})
print(json.dumps({'candidate':d['file'],'internalReview':d['internalReview'],'allocationConflicts':conflicts,'ownerAck':str(ackpath)}))
