from pathlib import Path
import json,hashlib,runpy,sys
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,j:Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
t=Z/'r07_c15';selection=read(t/'selected-native.json')
existing=[p for p,f in selection.items() if (t/'native'/f).is_file() and Path(str(t/'native'/f)+'.generation.json').is_file()]
v=read(t/'tile-progress.json');v.update({'selectedCoreCount':len(existing),'remainingCoreCount':16-len(existing),'updatedAt':now})
if len(sys.argv)>1:v['nextPatch']=sys.argv[1] if sys.argv[1]!='none' else None
save(t/'tile-progress.json',v)
runpy.run_path(str(Z/'refresh_progress.py'),run_name='__main__')
p=read(Z/'progress.json');r=read(Z/'production-resume-20261012.json')
r.update({'updatedAtUtc':now,'currentCandidateCount':p['complete4kCandidateCount'],'internalPassedCount':p['internalPassed4kCount'],'connectedGroupReviewedCount':p['connectedGroupReviewed4kCount'],'newSelectedCoreCount':p['usableSelectedCoreCount']-128,'remainingNativeCoreCount':p['missingNativeCoreCount']})
save(Z/'production-resume-20261012.json',r)
i=read(Z/'current-adopted-index-20261012.json');i.update({'updatedAt':now,'newOutputCount':p['generatedNativeCount']-176,'newSelectedCoreCount':p['usableSelectedCoreCount']-128})
for tid in ['r07_c15','r07_c16','r08_c15','r08_c16']:
    f=Z/tid/'selected-native.json'
    if f.is_file():i.setdefault('nativeSelections',{})[tid]=str(f)
save(Z/'current-adopted-index-20261012.json',i)
