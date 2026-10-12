from pathlib import Path
from PIL import Image
import json,hashlib,datetime
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012')
reasons={
 'V1-row1-quiet-v01':'Central strip native composition creates new straight tonal boundaries at mask caps. v07 not adopted.',
 'blue-band-east-join-v01':'Blue/cream retained outer anchors shifted and crossing grout moved. Do not integrate.',
 'blue-band-east-join-v02':'Text coordinate anchors not preserved: left blue/cream edge near y1013 rather than y1080. Do not integrate.',
 'blue-band-east-join-v03':'QA overlay did not prevent blue/cream anchor drift. Do not integrate.',
 'upper-cream-step-small-v01':'Target native256x256 returned1254x1254 at a different detail scale. Resampling prohibited; do not integrate.',
 'blue-coherent-left-v04':'Common blue/cream guide missed by approximately30-48 native pixels. Notch improved but retained common anchors do not join. Do not integrate.'}
for name,reason in reasons.items():
 T=D/name;p=T/'native.png';o={}
 if (T/'disposition.json').exists():o=json.loads((T/'disposition.json').read_text())
 o.update({'native':{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':list(Image.open(p).size)},'explicitlyRejected':True,'selected':False,'reason':reason,'formalAccepted':False,'internalAccepted':False,'recordedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 (T/'disposition.json').write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
T=D/'upper-cream-step-local-v02';p=T/'native.png'
(T/'disposition.json').write_text(json.dumps({'native':{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':list(Image.open(p).size)},'explicitlyRejected':False,'reason':'Original generated native is retained. Only the reviewed upper gray/cream edge corridor is extracted through proposal-v03 mask into provisional v10; whole native is not a whole-crop replacement. proposal v01/v02 candidates v08/v09 were superseded because masks missed some existing gray edge pixels.','extractionProposal':str(T/'proposal-v03.json'),'currentCandidateAssembly':str(D/'integrated-local-v10/assembly.json'),'formalAccepted':False,'internalAccepted':False},ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved six native rejection dispositions and one partial extraction disposition.')
