from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,uuid
Z=Path(__file__).resolve().parent;T=Z/'r14_c15'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,d):
 tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
 tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,p)
q=T/'review/assembly-c162322cbdcca7cb2291/visual-qa-v3-3f0ba6b3.json'
assert sha(q)=='26014ff56b52a96eef58ff56614275f726920adfa99815b089b01fdb85384fa4'
report=read(q);latest=read(T/'candidate/latest-assembly.json');p=read(T/'progress.json')
expected='3f0ba6b330136574a1ea9508d2a213fc9b66a5a42c95c737ee0820a6cb0798a9'
assert latest['candidate']['sha256']==expected and sha(Path(p['candidate']))==expected
assert report['candidate']['sha256']==expected
assert all(v['independentAlphaReplayExact'] and v['contextCoreExact'] for v in report['verification'].values())
assert report['internalCarriedForward']['fullSeams']==6 and report['internalCarriedForward']['junctions']==9
evidence={'path':str(q),'sha256':sha(q)}
updates={'status':'internal_visual_pass_external_repairs_in_progress','internalArtQA':'internal_visual_pass','internalSeamQA':'passed','independentVisualQA':evidence,'externalNeighborSeamQA':'north_and_west_failed_east_and_south_pending','externalCoreFindings':report['externalCoreJoins']['remainingFindings'],'formalAccepted':False}
latest.update(updates);p.update(updates,updatedAt=datetime.now(timezone.utc).isoformat(),nextStep='Repair north x230 board joint and west stone joins using actual native sources; then review current-core neighbor joins.')
atomic(T/'candidate/latest-assembly.json',latest);atomic(T/'progress.json',p)
print(json.dumps({'tile':'r14_c15','candidateSha256':expected,'independentVisualQA':evidence,'internalSeamQA':'passed','formalAccepted':False}))
