import json,sys,time
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
def save_json(path,data):
 for attempt in range(4):
  try:
   temp=path.with_suffix('.next.json')
   temp.write_text(json.dumps(data,indent=2),encoding='utf-8')
   temp.replace(path)
   return
  except OSError:
   if attempt==3:raise
   time.sleep(.25)
path=R/'selected-patches.json'
d=json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {'tile':R.name,'patches':{},'internalReady':False,'formalAccepted':False}
stem=sys.argv[1];d['patches'][stem.split('-')[0]]='native/'+stem+'.png'
d['status']='native_generation_in_progress';d['updatedAt']=datetime.now(timezone.utc).isoformat()
save_json(path,d)
p={'tile':R.name,'status':d['status'],'generatedNativeCount':len(list((R/'native').glob('*.png'))),'selectedPatchCount':len(d['patches']),'remainingPositions':16-len(d['patches']),'complete4kCandidateCount':0,'internalReady4kCount':0,'formalAcceptedCount':0,'updatedAt':d['updatedAt']}
save_json(R/'progress.json',p)
print(json.dumps(p))

