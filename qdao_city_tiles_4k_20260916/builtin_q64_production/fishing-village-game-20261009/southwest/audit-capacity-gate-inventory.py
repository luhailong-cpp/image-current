from pathlib import Path
import json,re,hashlib
from datetime import datetime,timezone
from PIL import Image
r=Path(__file__).resolve().parent
gate=r.parents[1]/'capacity-layout-gate-20261010.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
by={}
for p in sorted((r/'native').glob('*.png.generation.json')):
 j=read(p);f=Path(j['file']);m=re.fullmatch(r'(r\d{2}_c\d{2})_(p\d{2}_\d{2})_v(\d+)\.png\.generation\.json',p.name)
 row={'stem':f.stem,'file':str(f),'sha256':j['sha256'],'hashVerified':f.is_file() and sha(f)==j['sha256'],'status':j.get('status'),'coordinates':j.get('coordinates'),'actualModel':j.get('actualModel'),'actualQuality':j.get('actualQuality')}
 rows.append(row)
 if m and not any(t in j.get('status','').lower() for t in ('rejected','superseded','frozen')):
  tile,patch,v=m.groups();k=(tile,patch)
  if k not in by or int(v)>by[k]['version']:by[k]={**row,'version':int(v),'tile':tile,'patch':patch}
tiles=[]
for tid in sorted({t for t,p in by}):
 cur=[by[k] for k in sorted(by) if k[0]==tid]
 tiles.append({'tile':tid,'currentNativeSlots':len(cur),'missingPatches':[f'p{pr:02}_{pc:02}' for pr in range(1,5) for pc in range(1,5) if (tid,f'p{pr:02}_{pc:02}') not in by],'selected':cur})
pending=[]
for p in sorted((r/'native').glob('*.request.json')):
 stem=p.name.removesuffix('.request.json')
 if not (r/'native'/(stem+'.png')).exists():
  pending.append({'stem':stem,'request':str(p),'promptExists':(r/'native'/(stem+'.prompt.txt')).exists(),'receiptExists':(r/'native'/(stem+'.receipt.json')).exists(),'classification':'Prepared request or failed historical attempt; filesystem presence alone does not prove invocation.'})
ack={'schemaVersion':1,'acknowledgedAtUtc':datetime.now(timezone.utc).isoformat(),'zone':'southwest','gate':{'path':str(gate),'sha256':sha(gate),'status':read(gate)['status']},'status':'generation_held_readonly_qa_continues','inFlightStatus':{'root':'No active imagegen call. r09_c06_p04_03_v2 was prepared before interruption but never invoked; no PNG/receipt. Last successful root call r09_c06_p04_03_v1 is saved with full provenance.','agents':'All three previously errored with application network permission revoked; resumed with explicit no-imagegen read-only audit tasks. No active generation currently.'},'generatedNativeCount':len(rows),'generatedCoordinates':tiles,'allGeneratedRecords':rows,'unreturnedOrUninvokedRequests':pending,'target4kCount':49,'fullyCovered4kCount':sum(t['currentNativeSlots']==16 for t in tiles),'missingCoverage4kCount':49-sum(t['currentNativeSlots']==16 for t in tiles),'activeCoordinateTileCount':len(tiles),'currentSelectedNativeSlotCount':len(by),'requiredNativeCoreSlotCount':49*16,'missingNativeCoreSlotCount':49*16-len(by),'internalPassed4kCount':2,'internalPassedTiles':['r09_c04','r09_c05'],'exportedInternalCandidate4kCount':1,'externalPassed4kCount':0,'formalAcceptedCount':0,'capacity5000Validated':False,'worldSizeChanged':False,'newArtRequestsAfterAcknowledgement':0,'notes':['Internal c05 acceptance is supported by repair-r09_c05-v3-independent-internal-audit.json; its shared rail edge with c04 remains failed.','r10c04 fully covered but stairs structurally fail; coverage is not acceptance.','Prepared request is not an in-flight tool call or generated image.','No artwork deleted; no global/shared/client/git writes.']}
(r/'capacity-gate-ack.json').write_text(json.dumps(ack,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'progress.json';progress=read(p)
progress.update({'status':'capacity_layout_gate_readonly_qa','updatedAtUtc':ack['acknowledgedAtUtc'],'generatedNativeCount':len(rows),'fullyCovered4kCount':ack['fullyCovered4kCount'],'internalPassed4kCount':2,'internalPassedTiles':['r09_c04','r09_c05'],'externalPassed4kCount':0,'formalAcceptedCount':0,'remainingFormal4kCount':49,'remainingInternal4kCount':47,'missingCoverage4kCount':ack['missingCoverage4kCount'],'currentSelectedNativeSlotCount':len(by),'missingNativeCoreSlotCount':ack['missingNativeCoreSlotCount'],'exportedInternalCandidate4kCount':1,'nextStep':'While shared capacity/layout gate is active: read-only source replay, seam/road risks, and mechanical assembly only; resume artwork only after root releases gate.','gateAcknowledgement':str(r/'capacity-gate-ack.json'),'legacyCountNote':'complete4kCount remains the prior exported-candidate count (1). Use explicit fullyCovered4kCount/internalPassed4kCount/externalPassed4kCount/formalAcceptedCount for acceptance stages.','capacity5000Validated':False})
p.write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'generated':len(rows),'tiles':[{k:t[k] for k in ('tile','currentNativeSlots','missingPatches')} for t in tiles],'fullyCovered':ack['fullyCovered4kCount'],'selectedSlots':len(by),'missingSlots':ack['missingNativeCoreSlotCount'],'badImageHashes':sum(not x['hashVerified'] for x in rows),'pendingRequests':pending,'ack':str(r/'capacity-gate-ack.json')},ensure_ascii=False))

