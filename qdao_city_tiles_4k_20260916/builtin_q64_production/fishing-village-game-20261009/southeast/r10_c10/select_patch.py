from pathlib import Path
from datetime import datetime,timezone
import sys,json
T=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
pid,relative=sys.argv[1:3]
assert (T/relative).resolve().is_relative_to(T)
assert (T/relative).exists()
s=read(T/'selected-patches.json');s['patches'][pid]=relative;s.update(status='tile_generation_and_QA_in_progress',formalAccepted=False,updatedAt=datetime.now(timezone.utc).isoformat());write(T/'selected-patches.json',s)
p=read(T/'progress.json');p.update(updatedAt=s['updatedAt'],status=s['status'],currentPatch=pid,generatedNativeCount=len(list((T/'native').glob('*.png')))+len(list((T/'joint').glob('*/repair-*.png'))),selectedNativeCount=len(s['patches']),complete4kCount=0,formalAcceptedCount=0,nextStep='Generate remaining native positions and review all internal seams; external seams remain candidates');write(T/'progress.json',p)
print(json.dumps({'patch':pid,'selected':relative,'positions':len(s['patches'])}))
