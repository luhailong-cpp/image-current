from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,j:Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Z/'production-resume-20261012.json';j=read(p);f=Z/'r07_c15/native/p11-v20261012.png'
j.update({'firstNewOutput':{'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'nativeSize':[1254,1254],'generationRecord':str(f)+'.generation.json','savedAtUtc':datetime.now(timezone.utc).isoformat()},'currentCoordinate':'r07_c15/p12 + delegated p21-p31-p41','currentCandidateCount':8,'internalPassedCount':8,'connectedGroupReviewedCount':8,'newSelectedCoreCount':1,'remainingNativeCoreCount':895,'currentAdoptedIndex':str(Z/'current-adopted-index-20261012.json')});save(p,j)
t=Z/'r07_c15/tile-progress.json';v=read(t);v.update({'selectedCoreCount':1,'remainingCoreCount':15,'nextPatch':'p12','inflightGeneration':None,'lastSaved':j['firstNewOutput']});save(t,v)
i=Z/'current-adopted-index-20261012.json';v=read(i);v['nativeSelections']['r07_c15']=str(Z/'r07_c15/selected-native.json');v['newOutputCount']=1;v['lastSaved']=j['firstNewOutput'];save(i,v)

