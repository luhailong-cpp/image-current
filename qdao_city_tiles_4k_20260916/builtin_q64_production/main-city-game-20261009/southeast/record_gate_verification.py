from pathlib import Path
import json,datetime,hashlib
B=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
r=read(B/'capacity-gate-provenance-review.json');p=read(B/'progress.json')
p.update(updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='capacity_layout_gate_active_existing_art_review',capacityGateActive=True,inFlightImageGenCount=0,sourcePixelsReplayVerified=r['finalCoreExactReplay'],exactReplayVerified=r['finalCoreExactReplay'],historicalReferenceAvailabilityVerified=r['allHistoricalReferencesPresent'],missingHistoricalReferenceCount=len(r['missingReferenceEvidence']),missingHistoricalReferences=r['missingReferenceEvidence'],capacityGateProvenanceReport=str(B/'capacity-gate-provenance-review.json'),nextStep='Wait for root capacity/layout gate release; meanwhile review existing art only. Before new art, resolve missing approved primary style reference by an exact-hash source or root-authorized replacement; do not rewrite historical generation evidence.')
write(B/'progress.json',p)
a=read(B/'capacity-gate-ack.json');a.update(existingPixelReplayVerified=True,referenceFileAvailability='one_missing_historical_primary_style_reference',missingHistoricalReferences=r['missingReferenceEvidence'],provenanceReport=str(B/'capacity-gate-provenance-review.json'))
write(B/'capacity-gate-ack.json',a)
print(json.dumps({'generationHoldActive':True,'newImageGenCalls':0,'pixelReplay':True,'missingHistoricalReferenceFiles':len(r['missingReferenceEvidence'])}))

