from pathlib import Path
import json,hashlib,datetime
T=Path(__file__).resolve().parent;q=T/'qa/native-repairs-20261013-v01';m=json.loads((q/'manifest.json').read_text());needs={'internal-x1024-segment02.png':'Wood fascia local hanging end repaired, but adjacent blue roof termination at tile x895 still retains a straight cut; after two local attempts this residual stays deferred/unpassed.','internal-x2048-segment02.png':'Tile termination geometry repaired; existing vertical material strip at tile x2048 unchanged and remains unpassed.','internal-y1024-segment02.png':'Roof termination repaired; subtle horizontal glaze/lightness boundary along y1024 remains unpassed.','junction-x2048-y1024.png':'Curved roof termination is restored; existing x2048 vertical material boundary remains unpassed.'}
records=[]
for c in m['crops']:
 n=Path(c['file']).name;r=dict(c)
 if c['status']=='pending_changed':r.update(status='needs_repair' if n in needs else 'pass',actuallyViewed=True,viewDetail='original',reviewer='/root/resume_r06_c03_fullqa',notes=needs.get(n,'Native changed crop actually inspected. Circular gold frame, foliage and painted surfaces remain continuous; no new geometry or perimeter break.'))
 else:r.update(actuallyViewed=False,reviewReusedByExactPixelIdentity=True)
 records.append(r)
out=dict(candidate=m['candidate'],crops=records,passed=sum(x['status']=='pass' for x in records),needsRepair=sum(x['status']=='needs_repair' for x in records),total=47,actuallyViewedChangedCount=10,reusedUnchangedCount=37,fullNativePixelProof=m['proof'],formalAccepted=False)
(q/'review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
checkpoint=dict(updatedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),tile='r06_c03',uniqueSelectedCores=16,requiredCores=16,candidate=m['candidate'],assembly=str(T/'candidate/native-repairs-20261013-v01/assembly.json'),nativeSourceCount=19,coreVersionCount=19,nativeRepairVersionCount=5,selectedRepairSourceCount=3,fullQA=str(q/'review.json'),fullQACrops=47,qaPassed=out['passed'],qaNeedsRepair=out['needsRepair'],localCompleted=['circular sign geometry and material','roof x1933 termination geometry','fascia small timber joint geometry'],unpassed=['roof x895 remaining cut deferred after two attempts','x2048/y1024 local material transitions','s03_01 beam face step near x909/y2048','east gold beam material seam','east row4 tile contour offsets','s04_03 eastern ridge step and curl','north glaze transition'],formalAccepted=False,productionComplete=False,noGitOperations=True)
(T/'current-fullqa-checkpoint-20261013.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checkpoint))
