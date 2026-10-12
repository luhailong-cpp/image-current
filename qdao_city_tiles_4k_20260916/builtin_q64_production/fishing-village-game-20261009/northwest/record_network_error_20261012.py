from pathlib import Path
from datetime import datetime,timezone
import json
B=Path(__file__).resolve().parent
e={'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','coordinate':'r05_c02_s01_s03_v01','error':'image generation failed: application network permission was revoked','outputReturned':False,'successReceiptCreated':False,'newErrorThisResume':True,'subsequentUserDirection':'继续','nextAction':'One ordinary built-in retry after renewed user direction; no bypass or alternative API.'}
p=B/'work-r05_c02/receipts/r05_c02_s01_s03_v01.error.json'
p.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['production-resume-20261012.json','progress.json']:
 p=B/name;v=json.loads(p.read_text(encoding='utf-8-sig'));v.setdefault('errors',[]).append(e);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(e))
