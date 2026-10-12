import json
from pathlib import Path
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/02_fire_talisman_boy')
for key,reason in [('finish-nw-NW08-a02','换持物：近左臂拿符、远右臂持铃；拒绝，不导入，保留a01。'),('finish-nw-NW14-a01','多出第三只鞋/腿，且符扇突换位置；拒绝，不导入。')]:
 p=R/'work/grounding-v2/north/NW'/f'{key}.png.generation.json';d=json.loads(p.read_text(encoding='utf-8'));d['visualQA']={'status':'rejected','reason':reason};p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
W=R/'work/finish-NW';(W/'selection-overrides.json').write_text(json.dumps({'8':'work/grounding-v2/north/NW/finish-nw-NW08-a01.png','14':'frames/run/NW/14.png'},indent=2),encoding='utf-8')

