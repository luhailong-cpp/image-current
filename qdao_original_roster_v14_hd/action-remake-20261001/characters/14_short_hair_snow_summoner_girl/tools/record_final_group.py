from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('action');p.add_argument('direction');p.add_argument('--notes',required=True);a=p.parse_args()
counts={'run':16,'hit':6,'attack':12,'cast':16}
out=R/'review.json';j=json.loads(out.read_text(encoding='utf-8')) if out.exists() else {}
for i in range(1,counts[a.action]+1):
 key=f'{a.action}/{a.direction}/{i:02d}';image=R/(key+'.png')
 j[key]={'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'visualStatus':'passed','reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'root with independent direction-agent static review','scope':'offline anatomy, full contact sheet, selected enlarged native/final frames, normal and quarter-speed browser preview; no engine test','notes':a.notes,'clientValidated':False}
out.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{a.action}/{a.direction}: {counts[a.action]} reviewed; total {len(j)}')
