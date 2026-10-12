from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re
Z=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
progress=read(Z/'progress.json');covered={t['tile']:t for t in progress['tiles'] if t['fullyCovered4kCount']}
groups=read(Z/'connected-groups.json')
accepted_group=set(); reviewed_pairs=set()
for g in groups['groups']:
 if all(k in covered and covered[k]['candidateSha256']==v['sha256'] for k,v in g['sources'].items()):
  accepted_group.update(g['sources'])
  for a in g['sources']:
   for b in g['sources']:
    if abs(int(a[1:3])-int(b[1:3]))+abs(int(a[5:7])-int(b[5:7]))==1:reviewed_pairs.add(frozenset([a,b]))
index=[];open_edges=[]
for tid,t in covered.items():
 r,c=int(tid[1:3]),int(tid[5:7]);status=read(Z/tid/'tile-progress.json')
 item={'tile':tid,'file':t['candidate'],'sha256':t['candidateSha256'],'pixels':[4096,4096],'internalPassed':t['internalPassed4kCount']==1,'connectedGroupReviewed':tid in accepted_group,'formalAccepted':False,'tileProgress':str(Z/tid/'tile-progress.json')}
 index.append(item)
 for direction,dr,dc in [('north',-1,0),('south',1,0),('west',0,-1),('east',0,1)]:
  adj=f'r{r+dr:02}_c{c+dc:02}'
  if frozenset([tid,adj]) in reviewed_pairs:continue
  if {tid,adj}=={'r06_c13','r07_c13'} and (Z/'r07_c13/qa/north-final-20261011/report.json').exists():continue
  # Explicitly count each candidate-side open boundary, including zone perimeter not yet coordinated.
  open_edges.append({'tile':tid,'side':direction,'adjacentTile':adj,'reason':'no current reviewed completed pair','adjacentCandidatePresent':adj in covered})
missing=[];existing=[]
for r in range(1,9):
 for c in range(9,17):
  tid=f'r{r:02}_c{c:02}';d=Z/tid;selection=read(d/'selected-native.json') if (d/'selected-native.json').exists() else {}
  need=[]
  for pr in range(1,5):
   for pc in range(1,5):
    patch=f'p{pr}{pc}';f=d/'native'/selection.get(patch,patch+'.png')
    if not f.is_file():need.append(patch)
  if need:missing.append({'tile':tid,'missingPatchIds':need,'missingCount':len(need),'prepared':(d/'coordinates.json').exists()})
  if d.is_dir():
   for record in (d/'native').glob('*.generation.json'):
    rec=read(record);f=Path(rec['file'])
    if f.is_file():existing.append({'file':str(f),'sha256':sha(f),'sourceRecord':str(record)})
newSources=[Z/'r07_c13/native'/f'{p}.png' for p in ['p34','p42','p43','p44']]
newSources+=list((Z/'r07_c13/qa/finish-20261011/source').glob('*.png'))
out={'updatedAt':datetime.now(timezone.utc).isoformat(),'zone':'northeast','assignedTileCount':64,'currentCandidateCount':len(index),'internalPassedCount':sum(i['internalPassed'] for i in index),'connectedGroupReviewedCount':len(accepted_group),'formalAcceptedCount':0,'openCandidateSideCount':len(open_edges),'openCandidateSides':open_edges,'newlyIncorporatedTrueOutputs':[{'file':str(f),'sha256':sha(f)} for f in newSources],'candidateIndex':index,'stillNeedsGeneration':missing,'missingSelectedNativeCoreCount':sum(i['missingCount'] for i in missing),'networkPermission':'user restoration confirmed by controller; successful new r08_c13/p13 receipt exists','networkBlockActive':False,'currentDependencyBlock':None,'firstConfirmedOutputAfterRestoration':str(Z/'r08_c13/native/p13.png'),'firstConfirmedOutputReceipt':str(Z/'r08_c13/receipts/p13.receipt.json'),'preserveAllSources':True,'gitManagedBy':'01a11b5e-158a-77d0-8c02-e8e503b7abe4','runtimeWorkRequested':False,'builtinOnly':True,'nextStep':'Second group shared seams reviewed; continue next adjacent unpainted northeast group after final internal handoff.'}
save(Z/'local-continuation-20261011.json',out)
save(Z/'delivery-index-20261011.json',{'updatedAt':out['updatedAt'],'scope':'actual northeast outputs, incomplete zone','candidates':index,'formalAcceptedCount':0,'openCandidateSides':open_edges,'nativePreservationNote':'Native PNGs and repair sources inside zone are exact tool output copies; external original sourceOutputPath is retained as provenance. Keep all prior previews/evidence.'})
print(json.dumps({k:out[k] for k in ['currentCandidateCount','internalPassedCount','connectedGroupReviewedCount','openCandidateSideCount','missingSelectedNativeCoreCount','networkBlockActive']}))


