from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
from export_review_runtime import edge_counts
B=Path(__file__).resolve().parents[1]
vs={'W':[2,1,3,8,3,7,6,5,5,4,8,5,4,6,6,5],'SE':[3,2,2,8,3,6,3,4,4,3,1,5,5,4,4,5]}
phases=['前侧落地','前侧缓冲承重','身下支撑、对侧提膝','身下支撑过渡','后侧第一位置承重','后侧第一位置继续承重','后侧第二位置前掌支撑','后侧第二位置支撑至换脚']
for d,versions in vs.items():
 rows=[]
 for i,v in enumerate(versions,1):
  key=f'run-{d}-{i:02}-v{v}';p=B/'staging'/f'{key}.png';im=Image.open(p);edges=edge_counts(im);assert not any(edges.values()),(key,edges)
  side=('远右脚' if i<=8 else '近左脚') if d=='W' else ('近右脚' if i<=8 else '远左脚')
  rows.append({'slot':f'run-{d}-{i:02}','file':f'staging/{key}.png','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':'pending_playback','notes':side+'：'+phases[(i-1)%8]+'；鞋长轴与膝踝同向，手持物侧别保持，原生画布未平移。','edgeHighAlphaPixels':edges})
 data={'character':B.name,'reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'selected_pending_playback','contactRequirement':'review/contact-pairs-current-20261004.json','runTiming':{'cycleMs':1200,'frameMs':75,'uniform':True},'selectedForSequenceReview':rows,'actualSupportFrames':{'firstFoot':list(range(1,9)),'oppositeFoot':list(range(9,17))},'notes':'逐张原图、完整画布联系表和09当前同方向帧已核对。两帧位置分组，每帧姿态独立；接地高度受绘制透视影响，接续仍需实播确认。'}
 (B/f'review-run-{d}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('W/SE explicit latest selections written; 32 outer-edge checks passed.')
