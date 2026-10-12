from pathlib import Path
import json,sys,re
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;p=T/'tile-progress.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
n=list((T/'native').glob('*.png'));count=sum(bool(re.fullmatch('p[1-4][1-4]\\.png',x.name)) for x in n)
d.update(updatedAt=datetime.now(timezone.utc).isoformat(),nativeCount=len(n),selectedCoreCount=count,remainingCoreCount=16-count,status='native_generation_in_progress',waitFor=None,nextPatch=sys.argv[1],inflightGeneration=sys.argv[1] if sys.argv[2]=='generating' else None)
p.write_text(json.dumps(d,indent=2),encoding='utf-8')
