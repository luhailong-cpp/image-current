from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
Z=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dt(v):return datetime.fromisoformat(v.replace('Z','+00:00'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
start=dt(read(Z/'production-resume-20261012.json')['resumedAtUtc']);now=datetime.now(timezone.utc)
outputs=[];unarchived=[];owned={'r12_c08','r13_c08','r14_c08'}
for T in sorted(Z.glob('r??_c??')):
 if not T.is_dir():continue
 for rec in sorted((T/'native').glob('*.png.generation.json')):
  g=read(rec);when=g.get('generatedAt')
  if not when or dt(when)<start:continue
  p=Path(g['file']);assert p.exists() and sha(p)==g['sha256']
  outputs.append(dict(tile=T.name,file=str(p),sha256=g['sha256'],generatedAt=when,generationRecord=str(rec),generationRecordSha256=sha(rec),dimensions=g.get('nativeDimensions'),actualModel=g.get('actualModel'),actualQuality=g.get('actualQuality'),route=g.get('route'),source=g.get('evidence',{}).get('sourcePath')))
 if T.name in owned:
  for rec in T.glob('*.receipt.json'):
   g=read(rec);when=g.get('receivedAt');src=g.get('sourcePath');native=T/'native'/(rec.name.removesuffix('.receipt.json')+'.png')
   if when and dt(when)>=start and src and Path(src).exists() and not native.exists():unarchived.append(dict(tile=T.name,receipt=str(rec),source=src,sourceSha256=sha(src),expectedNative=str(native)))
repairs=[]
for rec in (Z/'seam-qa').rglob('*.generation-receipt.json'):
 g=read(rec);when=g.get('endedAtUtc');p=g.get('savedOutput')
 if when and dt(when)>=start and p and Path(p).exists():
  assert sha(p)==g['savedOutputSha256'];repairs.append(dict(file=p,sha256=g['savedOutputSha256'],receipt=str(rec),receiptSha256=sha(rec),generatedAt=when,dimensions=g.get('dimensions'),actualModel=g.get('actualModel'),actualQuality=g.get('actualQuality'),selected=False,note='Repair raw output; selection requires separate adoption review.'))
inventory=[]
for p in Z.rglob('*'):
 if not p.is_file() or p.suffix in ['.pyc','.tmp'] or '__pycache__' in p.parts:continue
 st=p.stat()
 if st.st_mtime<start.timestamp():continue
 before=(st.st_size,st.st_mtime_ns);h=sha(p);after=p.stat();stable=before==(after.st_size,after.st_mtime_ns)
 inventory.append(dict(file=str(p),relativeFile=p.relative_to(Z).as_posix(),sha256=h,bytes=st.st_size,lastModifiedAtUtc=datetime.fromtimestamp(st.st_mtime,timezone.utc).isoformat(),stableDuringHash=stable,classification='mtime-based local inventory; does not prove generation time or uploader capture'))
index=read(Z/'delivery-index-20261012.json');out=Z/'incremental-delivery-20261012-v2.json';assert not out.exists()
write(out,dict(schemaVersion=2,savedAtUtc=now.isoformat(),scope='southeast original 49 coordinates',authorization=str(Z.parents[3]/'docs/MAP_PRODUCTION_RESUME_20261012.json'),historicalLedger=str(Z/'incremental-delivery-20261012.json'),resumeCutoffUtc=start.isoformat(),nativeOutputs=outputs,nativeOutputCount=len(outputs),repairRawOutputs=repairs,repairRawOutputCount=len(repairs),rootRecoveryAudit=dict(tiles=sorted(owned),returnedButUnarchived=unarchived,automaticSelection=False),deliveryIndex=dict(file=str(Z/'delivery-index-20261012.json'),sha256=sha(Z/'delivery-index-20261012.json'),reportedAt=index['updatedAt'],fullCoverageCandidates=index['fullCoverageCandidateCount'],internalPassed=index['internalPassedCount'],selectedPositions=index['selectedNativePositions'],missingPositions=index['missingSelectedPositions']),files=inventory,fileCount=len(inventory),builtinOnly=True,gitMutations=False,uploaderCaptureConfirmed=False,inventoryIsAtomicSnapshot=False,all49Complete=False,formalAccepted=0))
Q=Z/'r14_c08/qa/first-two-rows-resume-20261012-v1';m=read(Q/'manifest.json');ev=[dict(file=str(p),sha256=sha(p)) for p in Q.glob('*.png') if p.name not in ['candidate-4096.png','preview-QA-1024.png']];assert len(ev)==13
rp=Q/'root-native-review.json';assert not rp.exists();write(rp,dict(tile='r14_c08',selectedNativePositions=8,reviewedSeams=10,reviewedCrossings=3,geometryPassed=True,materialStatus='continuous caustics at all reviewed seams; full-tile color review after remaining 8 native patches',evidence=ev,sources=m['sources'],internalReady=False,formalAccepted=False,partialPreviewIsDeliverable=False))
sp=Z/'r14_c08/selected-patches.json';s=read(sp);s['partialGeometryReview']=str(rp);write(sp,s)
print(json.dumps(dict(ledger=str(out),newNativeOutputs=len(outputs),repairRawOutputs=len(repairs),inventoryFiles=len(inventory),rootUnarchivedOutputs=unarchived,partialGeometryEvidence=13),ensure_ascii=False))
