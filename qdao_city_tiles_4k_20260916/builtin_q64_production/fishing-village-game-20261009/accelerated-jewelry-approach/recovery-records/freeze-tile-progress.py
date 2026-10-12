from pathlib import Path
from datetime import datetime,timezone
import json
b=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach');f=b/'migration-freeze-20261011.json';v=json.loads(f.read_text(encoding='utf-8'))
v['recoveryCacheNote']='The one unmatched generation-record scan entry has since been located in prior r03_c10 umbrella repair manifests and old raw-generation inventory. Its extra migration copy is preserved, but it is not a new unique output and is already within the116 recorded raw total.'
for s in v['selectedCandidatePaths']:
 if s['tile'].startswith('r05_'):
  p=b/s['tile']/'progress.json';t=json.loads(p.read_text(encoding='utf-8-sig'))
  t.update({'updatedAt':datetime.now(timezone.utc).isoformat(),'status':'migration_frozen_saved_candidate','generationStopped':True,'selectedNativeCoreCount':16,'requiredNativeCoreCount':16,'nextCoordinate':None,'candidate':s['file'],'candidateSha256':s['sha256'],'dimensions':[4096,4096],'formalAccepted':False,'migrationFreeze':str(f),'remainingWork':'See frozen root pendingRepairs; do not resume generation until user authorizes.'})
  p.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v['savedAtUtc']=datetime.now(timezone.utc).isoformat();f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Frozen checkpoints saved; no generation started; no Git operation.')

