from pathlib import Path
import json,datetime
T=Path(__file__).resolve().parent;q=T/'qa/native-repairs-20261013-v03';m=json.loads((q/'manifest.json').read_text())
for c in m['crops']:
 if c['status']=='pending_changed':c.update(status='pass',actuallyViewed=True,viewDetail='original',notes='Gold eave and red fascia now connect smoothly through x3072. Actual native final crop inspected. Available repair perimeter reviewed separately.')
r=dict(candidate=m['candidate'],crops=m['crops'],passed=sum(c['status']=='pass' for c in m['crops']),needsRepair=sum(c['status']=='needs_repair' for c in m['crops']),total=47,actuallyViewedChangedCount=1,reusedUnchangedCount=46,formalAccepted=False)
(q/'review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
cp=json.loads((T/'current-fullqa-checkpoint-20261013.json').read_text());backup=T/'checkpoint-v02-before-south-ridge-20261013.json';assert not backup.exists();backup.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
cp.update(updatedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate=m['candidate'],assembly=str(T/'candidate/native-repairs-20261013-v03/assembly.json'),nativeSourceCount=21,nativeRepairVersionCount=len(list((T/'repair-batches').glob('*/generation.json'))),selectedRepairSourceCount=5,fullQA=str(q/'review.json'),qaPassed=r['passed'],qaNeedsRepair=r['needsRepair'])
cp['localCompleted'].append('s04_03 eastern lower gold ridge geometry and fascia step repaired');cp['unpassed']=[s for s in cp['unpassed'] if not s.startswith('s04_03 eastern ridge step')]
(T/'current-fullqa-checkpoint-20261013.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(cp))
