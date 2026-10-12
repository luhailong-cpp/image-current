from pathlib import Path
import json, hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parents[1]
sel=T/'refinement/selection.json'
data=json.loads(sel.read_text(encoding='utf-8-sig'))
rejected='refinement/versions/join-repair-20261012-v03/p04_03.png.generation.json'
restored='refinement/versions/join-repair-20261012-v02/p04_03.png.generation.json'
assert data['p04_03']==rejected and (T/restored).exists()
qa=T/'pipeline/qa/p04_03.join-repair-20261012-v03.joined-rejected.json'
assert not qa.exists()
now=datetime.now(timezone.utc).isoformat()
report={'savedAtUtc':now,'patch':'p04_03','status':'rejected_for_selection','formalAccepted':False,'actualModel':None,'actualQuality':None,'rejectedRecord':rejected,'restoredRecord':restored,'joinedCandidate':'pipeline/output/b904642ef620a686/r09_c01.candidate.png','evidence':'pipeline/qa/b904642ef620a686/intersection_x2048_y3072.png','visualFinding':'Native lantern geometry preserved, but joined background now contains a second large light/dark jagged color boundary in addition to the original vertical mismatch. Worse than v02; all raw images and receipts preserved.'}
qa.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
data['p04_03']=restored
sel.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
state={'schemaVersion':1,'savedAtUtc':now,'worker':'sol_left_20261012','status':'candidate_pending_material_and_external_QA','tile':'r09_c01','selectedNativeCount':16,'latestSelectedCandidate':'pipeline/output/0310020c9169112c/assembly.json','candidateSha256':'0a98b00b96ee0fc35598194bd0340e534fa5ea475fe6c58f0485dea18da13680','formalAccepted':False,'actualModel':None,'actualQuality':None,'openFindings':['x2048 grey-brown background and brown-plane material mismatch','x1024 blue board paint tonal transition','external top/right/bottom native tile neighbors pending'],'preservedRejectedJoinedAttempt':str(qa),'nextTile':'r09_c02','nextPatch':'p01_02'}
(T/'production-resume-20261012.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'restored':restored,'report':str(qa),'state':str(T/'production-resume-20261012.json')}))
