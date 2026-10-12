from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
B=R.parent/'09_bamboo_archer_girl'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
changed=[6,8,9,12,14,15,16]
notes={
6:'近右前腿向前下方伸展、远左后腿屈膝回收；替换原来团腿收膝导致的跳跃感。',
8:'近右前鞋首次落脚，鞋底转为平缓；远左后腿仍屈膝，不把两只脚逐帧吸到同一地平。',
9:'接08，近右前脚维持平底承重，不重复翘鞋尖；为10回到身体下方承重留出过渡。',
12:'近右后腿向后蹬离，远左膝前抬，双腿前后关系连续；保留左臂抱狐、右掌持晶。',
14:'远左前腿前伸、近右后膝屈曲回收，延续13并导向15落脚。',
15:'远左前鞋落脚转平，近右腿后收；去掉第一次已经落地后又抬脚的错误节奏。',
16:'延续15的远左前鞋平缓承重，再接01；不重复翘脚尖或在循环边界突然换支撑腿。'}
phase=read(R/'run/E/grounding-review.json')
frames=[]
for n in range(1,17):
 p=R/'run/E'/f'{n:02d}.png';m=read(Path(str(p)+'.generation.json'))
 old=phase['frames'][n-1]
 frames.append({'file':f'run/E/{n:02d}.png','sha256':sha(p),'reference':str(B/'runtime/run/E'/f'{n:02d}.png'),'referenceSha256':sha(B/'runtime/run/E'/f'{n:02d}.png'),'changed':n in changed,'previousReviewSha256':old.get('sha256'),'observation':notes.get(n,old.get('observation')),'registration':m['registrationTransform'],'nativeGenerationRecord':m['derivedFrom']['generationRecord']})
audit={'schemaVersion':1,'updatedAt':datetime.now(timezone.utc).isoformat(),'scope':'E 16 final PNGs against actual user-approved09 runtime; original phase numbers do not imply a matching support leg','status':'root_static_and_browser_samples_checked_awaiting_independent_closeout','formalChangedCount':7,'formalRetainedCount':9,'changedFrames':changed,'hands':'LEFT arm continually hugs one white fox; RIGHT shoulder/sleeve/elbow/wrist/palm remains one connected arm carrying one crystal. E03 and11 observed as pass-through poses, not extra limbs.','loop':'08→09 flat near-foot contact;15→16→01 far-foot contact; near/far projected depths intentionally differ.','visualEvidence':['preview/run-E-sheet.jpg: all16 inspected by root','bamboo-reference.html: E16 enlarged, E01 enlarged, E normal240 sample03 and quarter-speed240 sample08; actual32images loaded','audit/bamboo-east-independent-review.json: independent notes including09/16 reinspection'],'playback':{'normalCycleMs':1200,'normalFrameMs':75,'slowCycleMs':4800,'slowFrameMs':300,'method':'browser launch + representative screenshots and full contact-sheet sequence inspection; no claim of video capture or precise screen refresh measurement'},'actualModel':None,'actualQuality':None,'generationEvidence':'provenance/run-E-*-bamboo-v1.request.json and corresponding response/native generation records; host does not expose model or quality','frames':frames,'clientValidated':False}
save(R/'audit/bamboo-east-review.json',audit)
print(json.dumps({'frames':len(frames),'changed':len(changed),'status':audit['status']}))

