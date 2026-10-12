from pathlib import Path
import json,hashlib,copy
from datetime import datetime,timezone
b=Path(__file__).resolve().parents[1];p=b/'audit/run-NS-selection.json';d=json.loads(p.read_text(encoding='utf-8'))
template=copy.deepcopy(next(f for f in d['frames'] if f['direction']=='S' and f['frame']==13))
for frame,key in [(13,'run-S-12-v1'),(15,'run-S-13-v1'),(16,'run-S-14-v1')]:
 f=copy.deepcopy(template);f['frame']=frame;f['source']=f'sources/new/{key}.png';f['generationRecord']=f'provenance/generation/{key}.json';f['sha256']=hashlib.sha256((b/f['source']).read_bytes()).hexdigest();f['event']=None
 f['review']={'reviewer':'continue_cast','reviewedAt':datetime.now(timezone.utc).isoformat(),'notes':['再次实际查看原始PNG，按实际相位选择；保留原文件名和来源。','S12v1本为离地已发生的帧，改用于13初腾空；S13v1用于15下降；S14v1本为近触地，改用于16，不按提示词编号认定相位。','右扇前摆，左空手后摆；屏右解剖左腿前伸、屏左右腿折回，两只靴子的轴线顺膝踝方向，无明显外八。']}
 d['frames']=[old for old in d['frames'] if not(old['direction']=='S' and old['frame']==frame)];d['frames'].append(f)
d['frames'].sort(key=lambda f:(f['direction'],f['frame']));d['status']='static_candidates_complete_dynamic_pending';d['updatedAt']=datetime.now(timezone.utc).isoformat()
assert len(d['frames'])==32
assert len(set(f['sha256'] for f in d['frames']))==32
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('NS 32/32, 32 unique SHA')

