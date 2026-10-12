from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent;TILE=HERE.parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=read(HERE/'review/roof-intermediate-qa/manifest.json');current=read(HERE/'review/final-qa/manifest.json')
prior={x['id']:x for x in old['records']};changed=[];same=[]
for rec in current['records']:
    assert sha(rec['file'])==rec['sha256']
    (same if rec['sha256']==prior[rec['id']]['sha256'] else changed).append(rec['id'])
assert set(changed)=={'v2-r1','v2-r2','h1-c2','h1-c3','junction-r1-c2'},changed
assert all(a['sha256']==b['sha256'] for a,b in zip(old['externalNorthShared'],current['externalNorthShared']))
review=read(HERE/'records/roof-intermediate-visual-review.json');review['candidate']=current['candidate'];review['candidateSha256']=current['sha256'];review['visualEvidenceManifest']=str(HERE/'review/final-qa/manifest.json')
review['reviewMethod']='All 24 pairs and 9 intersections reviewed at original pixels on roof intermediate; 28 windows hash-identical in final, all 5 changed windows re-viewed at original pixels after complete-branch p23 integration. All four north-shared windows hash-identical to reviewed intermediate.'
review['unchangedWindowIds']=same;review['reReviewedChangedWindowIds']=changed
review['resolved'].append({'id':'p23-flower','originalPriority':'P2','worldBox':[51200,21504,51315,21619],'result':'115px square cutout replaced by one coherent complete flowering branch; four paste boundaries examined at 1:1 without severed leaves/petals.'})
review['reclassified']=[{'id':'p43-eave','previousPriority':'P2','finalDecision':'retain original, not a seam defect','basis':'Root and independent reviewer examined the full building: front porch eave has continuous red column/bracket support, beam positions, and shadows. All six generated alternatives are excluded.','reference':str(TILE/'qa/root-p43-repair/review-status.json')}]
review['pending']=[]
review['retainedP3'].append({'id':'p23-short-bud-occlusion','worldBox':[51285,21614,51326,21626],'finding':'A small bud behind a leaf has a short straight lower occlusion edge in generated source; not introduced by the paste boundary.'})
review['sourceAudit'].update({'repairLayerCount':6,'repairSourceRecordsStrictlyVerified':6,'pixelReplayIdentical':True,'candidateSize':[4096,4096],'noSourceImageResampling':True,'noImageBlur':True})
review['sharedRoofVerification']=str(HERE/'records/shared-roof-verification.json');review['status']='internal visual review passed with retained P3 cosmetic notes; not formal accepted';review['openP1']=0;review['openP2']=0;review['formalAcceptedCount']=0
current['visualStatus']='reviewed at 1:1 with P3 cosmetic notes';current['reviewRecord']=str(HERE/'records/final-visual-review.json');save(HERE/'review/final-qa/manifest.json',current)
review['visualEvidenceManifestSha256']=sha(HERE/'review/final-qa/manifest.json');save(HERE/'records/final-visual-review.json',review)
sidepath=str(current['candidate'])+'.generation.json';side=read(sidepath);side['visualReview']={'file':str(HERE/'records/final-visual-review.json'),'sha256':sha(HERE/'records/final-visual-review.json')};side['pixelReplayVerified']=True;side['openP1']=0;side['openP2']=0;side['retainedP3Count']=len(review['retainedP3']);save(sidepath,side)
print(json.dumps({'candidate':current['candidate'],'sha256':current['sha256'],'reviewedInternalPairs':24,'reviewedIntersections':9,'changedAndReViewed':changed,'unchangedReviewedCount':len(same),'northSharedWindowsUnchanged':4,'openP1':0,'openP2':0,'P3':len(review['retainedP3']),'formalAcceptedCount':0},ensure_ascii=False))
