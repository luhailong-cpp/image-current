"""Census actual receipt-backed generations; independent of candidate acceptance."""
import datetime as dt
import hashlib
import json
import re
import uuid
from pathlib import Path

Z=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o):
    p=Path(p);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(p)
def resolve(v):
    if isinstance(v,dict):v=v.get('path')
    p=Path(v);return p if p.is_absolute() else Z/p
now=dt.datetime.now(dt.timezone.utc).isoformat()
good={}; errors=[]; coverage={}
for sidecar in sorted((Z/'native').glob('*.png.generation.json')):
    try:
        r=read(sidecar); p=Path(str(sidecar).removesuffix('.generation.json'))
        h=r.get('sha256') or r.get('image',{}).get('sha256')
        assert h and re.fullmatch('[0-9a-f]{64}',h),'missing hash'
        assert (r.get('tool') in ('image_gen.imagegen','image_gen__imagegen') and r.get('route')=='builtin') or r.get('generationRoute')=='builtin_image_gen','not builtin'
        if p.exists():assert sha(p)==h,'native hash mismatch'
        receipt=r.get('receipt') or r.get('receiptFile') or r.get('evidence',{}).get('receipt')
        rp=resolve(receipt);rr=read(rp)
        if isinstance(receipt,dict) and receipt.get('sha256'):assert sha(rp)==receipt['sha256'],'receipt hash mismatch'
        explicit_tool=rr.get('tool') in ('image_gen.imagegen','image_gen__imagegen')
        builtin_sidecar=(r.get('generationRoute')=='builtin_image_gen' or (r.get('tool') in ('image_gen.imagegen','image_gen__imagegen') and r.get('route')=='builtin'))
        actual_request=next((rr[k] for k in ('actualArguments','actualRequest','request') if isinstance(rr.get(k),dict)),None)
        linked_builtin_receipt=(builtin_sidecar and actual_request is not None and 'output_hint' in rr and 'image_url' in rr.get('returnedKeys',[]))
        assert explicit_tool or linked_builtin_receipt,'receipt lacks builtin evidence'
        hint=rr.get('output_hint') or rr.get('response',{}).get('output_hint') or rr.get('result',{}).get('output_hint') or rr.get('return',{}).get('output_hint')
        assert hint and 'exec-' in hint,'receipt lacks successful native output'
        gid=re.findall(r'exec-[a-zA-Z0-9-]+\.png',hint)[-1]
        if gid in good:assert good[gid]['sha256']==h,'same result with different pixels'
        else:good[gid]={'image':str(p),'sha256':h,'pixelsPresent':p.exists(),'generationRecord':{'path':str(sidecar),'sha256':sha(sidecar)},'receipt':{'path':str(rp),'sha256':sha(rp)},'toolEvidence':'receipt_explicit_tool' if explicit_tool else 'sidecar_builtin_route_and_hash_linked_actual_arguments_response','actualModel':r.get('actualModel'),'actualQuality':r.get('actualQuality')}
        match=re.match(r'(r\d{2}_c\d{2})_p([1-4][1-4])',p.name)
        if match:coverage.setdefault(match[1],set()).add(match[2])
    except Exception as e:errors.append({'record':str(sidecar),'error':str(e)})
assignment=Z.parent.parent/'acceleration-20261010/assignments.json'
a=next(x for x in read(assignment)['assignments'] if x['id']=='village_jewelry_approach')
excluded=a['coordinates']
owned_target=49-len(excluded)
census={'schemaVersion':3,'updatedAtUtc':now,'generatedNativeCount':len(good),'successfulGenerations':good,'errors':errors,'coverageByTile':{k:sorted(v) for k,v in coverage.items()},'definition':'Unique successful builtin image_gen output IDs with matching image hashes when pixels are retained and verifiable receipts. Coverage counts generated coordinates only, not usable/accepted art. Mechanical copies excluded.','originalZoneTarget':49,'ownedTarget':owned_target,'handoffTiles':excluded,'assignment':{'path':str(assignment),'sha256':sha(assignment)}}
cp=Z/'records/production-census-20261010.json';save(cp,census)
p=read(Z/'progress.json')
p.update({'updatedAtUtc':now,'status':'parallel_native_extension_and_versioned_candidate_QA','generatedNativeCount':len(good),'originalZoneTarget4kCount':49,'target4kCount':owned_target,'handedOff4kCount':len(excluded),'handedOffTiles':excluded,'assignmentRecord':str(assignment),'mechanicalIngestCounter':{'schemaVersion':3,'generatedCount':len(good),'record':str(cp),'censusErrors':len(errors)},'generatedCoordinateCoverageByTile':{k:len(v) for k,v in coverage.items()},'completeNativeCoreCoverageCount':sum(len(v) for v in coverage.values()),'fullyCovered4kCount':sum(len(v)==16 for v in coverage.values()),'missing4kCount':owned_target-sum(len(v)==16 for v in coverage.values()),'remainingUnstarted4kCount':owned_target-len(coverage),'currentTile':'r06_c12,r06_c13,r07_c12,r07_c13','currentPatch':'Native adjacent expansion plus r06_c12 repaired candidate QA','nextStep':'Close the first 2x2 block with original-scale internal and external edge review, then continue owned coordinates excluding all handed off tiles.','assembled4kCandidateCount':len({x.name.split('.candidate')[0] for x in (Z/'tiles').glob('*.candidate*.png')}),'candidateVersionCount':len(list((Z/'tiles').glob('*.candidate*.png'))),'allRequiredNativeQAExecuted':False,'allRequiredNativeQAPassed':False,'activeBlockers':['r06_c12 p43/p44 material transition exposed by corrected quay wood; native northrepair44 underway','First 2x2 external boundaries await completed neighbor natives'],'taskComplete':False,'newArtworkGenerationAllowed':True})
active_path=Z/'records/active-candidates.json'
active=read(active_path) if active_path.exists() else {'tiles':{},'activeBlockers':['Candidate QA pending'],'reviewPaths':[]}
for tile,item in active['tiles'].items():
    assert sha(resolve(item['path']))==item['sha256'],f'Active candidate hash mismatch: {tile}'
p['activeCandidates']=active['tiles']
p['activeBlockers']=active['activeBlockers']
p['activeCandidateRecord']={'path':str(active_path),'sha256':sha(active_path)}
if 'r06_c12' in active['tiles']:
    p.update({'candidatePath':active['tiles']['r06_c12']['path'],'candidateSha256':active['tiles']['r06_c12']['sha256']})
p['QAReviewPaths']=list(dict.fromkeys(p.get('QAReviewPaths',[])+active['reviewPaths']))
passed=[]
for tile,v in active['tiles'].items():
    review=Z/'qa'/(Path(v['path']).stem.replace('.candidate',''))/'internal-review-summary.json'
    if review.is_file():
        rr=read(review)
        if rr.get('internalNativeQAPassed') is True and rr.get('candidate',{}).get('sha256')==v['sha256']:passed.append(tile)
p['internalPassed4kCount']=len(passed)
p['internallyPassedTiles']=passed
p['currentTile']=','.join(sorted(k for k,v in coverage.items() if len(v)<16))
p['currentPatch']='Native adjacent expansion; see local-continuation-20261011.json for assigned coordinates'
p['internallyReviewed4kCount']=p['internalPassed4kCount']
save(Z/'progress.json',p)
plan=read(Z/'records/zone-tile-plan.json')
plan.update({'originalTileCount':49,'tileCount':owned_target,'handedOffTiles':excluded,'assignmentRecord':str(assignment),'updatedAtUtc':now})
for tile in plan['tiles']:
    tile['ownedByThisZone']=tile['id'] not in excluded
    if tile['id'] in excluded:tile.update({'status':'handed_off_exclusive_acceleration','ownerOutputDirectory':a['outputDirectory']})
save(Z/'records/zone-tile-plan.json',plan)
save(Z/'resume-ack-20261010.json',{'updatedAtUtc':now,'status':'active_production','usageGateReleased':True,'runtimeWorkRequested':False,'priorUserSuppliedAGENTSInstructionsApply':False,'firstBlock':['r06_c12','r06_c13','r07_c12','r07_c13'],'ownedTarget4kCount':owned_target,'handedOffTiles':excluded,'generatedNativeCount':len(good),'censusRecord':str(cp),'formalAcceptedCount':0})
print(json.dumps({'generatedNativeCount':len(good),'coverage':census['coverageByTile'],'censusErrors':errors,'ownedTarget':owned_target,'formalAccepted':0},ensure_ascii=False))
