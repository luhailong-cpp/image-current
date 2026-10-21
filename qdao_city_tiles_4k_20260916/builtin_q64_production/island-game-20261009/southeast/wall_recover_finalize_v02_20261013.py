from workflow import *
q=ROOT/'qa'/'r08_c10-wall-recover-20261013-v02';old=ROOT/'qa'/'r08_c10-wall-recover-20261013-v01';proof=read(q/'source-proof.json');new=read(q/'seams.json');prior=read(old/'seams.json');changed=['h33','h41','v24','v31','v34'];reuse=[]
for e in new['entries']:
 e['status']='passed_internal_contours';e['reviewedAt']=now()
 if e['id'] in changed:e['reviewMethod']='new actual native seam individually viewed by wall_recover'
 else:
  p=next(x for x in prior['entries'] if x['id']==e['id']);assert p['sha256']==e['sha256'];e['reviewMethod']='reuse unchanged SHA256 exact cut already viewed';reuse.append(e['id'])
write(q/'seams.json',new)
reusej=[]
for r in range(1,4):
 for c in range(1,4):
  n=f'junction_{r}{c}.png'
  if n in ['junction_23.png','junction_31.png','junction_33.png']:continue
  assert sha(q/n)==sha(old/n);reusej.append(n)
write(q/'worker-review.json',{'candidate':proof['candidate'],'candidateSha256':proof['candidateSha256'],'reviewedAt':now(),'reviewer':'wall_recover','workerInternalAccepted':True,'coordinatorIndependentReviewPending':True,'externalAccepted':False,'formalAccepted':False,'sourceCount':16,'coveredPixels':16777216,'sourceReplayMismatch':0,'internalSeams':{'passed':24,'newlyViewed':changed,'unchangedInputReused':reuse},'junctions':{'passed':9,'newlyViewed':['junction_23.png','junction_31.png','junction_33.png'],'unchangedInputReused':reusej},'repairs':[{'core':'41','version':'v02','sha256':sha(ROOT/'native'/'r08_c10_p41_v02.png'),'result':'Upper-right rectangular guide boundary and interrupted grout removed; N/E seams and four-way junction viewed continuous.'},{'core':'34','version':'v03','sha256':sha(ROOT/'native'/'r08_c10_p34_v03.png'),'result':'Short interrupted ivory paving ribbon extended into natural T junction, native full view confirmed; N/W/S and E core seams remain continuous.'}],'materialNote':'Mild painted texture/shade variation across some paving remains; no hard geometry disconnection in internal QA. Coordinator may review this note.','unresolved':[{'id':'external_E_p24_wall_foot','status':'not_passed_after_two_attempts','version':'v03','evidence':str(ROOT/'qa'/'wall-resume-20261013'/'r08_c10_p24-v03-E.png'),'note':'Do not mark external or formal accepted. Saved best version retained without third same-point retry.'}]})
d=read(ROOT/'production-resume-wall-20261013.json')
for rc,v in [('34','v03'),('41','v02')]:
 f=ROOT/'native'/f'r08_c10_p{rc}_{v}.png';d['generated']['r08_c10_p'+rc]={'version':v,'file':str(f),'sha256':sha(f),'status':'quick_layout_and_edges_passed','note':'Local repair complete; full candidate internal worker check passed; root independent review pending.','reviewedAt':now()}
d['fullCandidate']=proof['candidate'];d['fullCandidateSha256']=proof['candidateSha256'];d['internalAccepted']=True;d['coordinatorIndependentReviewPending']=True;d['externalAccepted']=False;d['formalAccepted']=False;d['uniqueCoreCount']=16;d['generatedNativeCount']=25;d['selectedCoreCount']=15;d['inFlightRequests']=[];d['inFlight']=False;d['currentTile']='r08_c10';d['nextStep']='Continue r09_c10 independent missing cores; external r08c10 east wall foot pending grouped repair';d['updatedAt']=now();write(ROOT/'production-resume-wall-20261013.json',d)
print(json.dumps({'candidate':proof['candidate'],'sha256':proof['candidateSha256'],'workerInternalAccepted':True,'externalAccepted':False,'reusedSeams':len(reuse),'reusedJunctions':len(reusej)}))
