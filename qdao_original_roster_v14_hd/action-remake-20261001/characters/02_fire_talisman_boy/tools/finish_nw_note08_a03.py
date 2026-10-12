import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[1]
for f in range(1,17):
    a=Image.open(R/f'frames/run/NW/{f:02d}.png').convert('RGBA')
    b=Image.open(R/f'work/finish-NW-final/{f:02d}.png').convert('RGBA')
    assert ImageChops.difference(a,b).getbbox() is None
rp=R/'reviews/run-NW-eight-support-final-review-20261004.json'
r=json.loads(rp.read_text(encoding='utf-8'))
note='08 a03已改为中间收臂：近侧解剖左肘下收、左手铜铃在腰侧；远侧解剖右肘收至右肋、右手符扇部分靠躯干；两腿及右足后端支撑关系保持。实际查看新原生图及更新16帧联系图，通过单帧解剖/持物检查，08→09动态仍待root统一复核。'
r['latestRevision']={'frame':8,'candidate':'finish-nw-NW08-a03','sourceRecord':'records/finish-nw-NW08-a03.json','sha256':hashlib.sha256((R/'frames/run/NW/08.png').read_bytes()).hexdigest(),'reviewedAt':datetime.now(timezone.utc).isoformat(),'visualNotes':note,'allPreviewFramesMatchFormalPixels':True}
r['visualNotes'] += ' '+note
next(x for x in r['frames'] if x['frame']==8)['visualNotes'] += '；'+note
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cp=R/'work/grounding-v2/north/NW/finish-nw-NW08-a03.png.generation.json'
c=json.loads(cp.read_text(encoding='utf-8'));c['visualQA']={'status':'single_frame_pass_pending_root_dynamic','notes':note}
cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('NW08 a03 reviewed; 16 preview images equal formal; report synchronized')
