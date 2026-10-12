from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parents[1];p=R/'review/run-NW-selection.json';s=json.loads(p.read_text(encoding='utf-8'))
for i,v in {1:2,2:2,7:8,8:6}.items():
 f=s['frames'][i-1];src=R/f'drafts/run/NW/{i:02}-v{v}.png'
 f.update(path=src.relative_to(R).as_posix(),sourcePath=src.relative_to(R).as_posix(),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),generationRecord=src.relative_to(R).as_posix()+'.generation.json')
notes={1:'近左靴前移到髋前全掌落地，远右足后折离地；形成明确第一位置。',2:'近左靴保持髋前位置，膝踝缓冲与摆腿轻变，为第二张独立前落地姿态。',7:'同一近左支撑靴在体后，下肢向右后斜伸，仍在远右抬靴的左侧，髋膝连接连续。',8:'同一近左靴前掌接地，后跟抬起；远右摆腿下放准备下一帧落地，未提前换腿。'}
for i,n in notes.items():s['frames'][i-1]['notes']=n;s['frames'][i-1]['actualContact']['evidence']=n
s.update(artStatus='final_left_positions_independent_review_pending',remainingIssues=['最新01/02前落地点、07/08后蹬位置待独立复查'],positionPairsVerified=False)
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

