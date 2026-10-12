from pathlib import Path
from datetime import datetime,timezone
import json
from contact_validation import validate_contact
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
d='N';now=datetime.now(timezone.utc).isoformat();c=validate_contact(R,d,require_preview=False);root=read(R/'audit/bamboo-root-acceptance.json')
preview={'reviewedAt':now,'page':'bamboo-reference.html','method':'Actual CUA controls and representative screenshots; current16 full-body contact sheet. No continuous video or hardware FPS measurement.','normal':{'cycleMs':1200,'displayPx':240,'played':True,'visibleSampleFrames':[7]},'quarterSpeed':{'cycleMs':4800,'displayPx':240,'played':True,'visibleSampleFrames':[14]},'paused480pxFrames':[1,2,3,6,8,9,10,16,1],'loopStep':'16 to01 via actual next button','observations':'北向前落地脚以纵深短透视过渡到髋下，再向身后踩压；01-08左腿支撑、09-16右腿支撑。08与16后脚前掌向地、摆动脚回收悬空，换脚连续。06与10托晶右掌可见并保留头部尺度，抱狐左臂遮挡关系一致。','clientValidated':False}
c.update(status='passed_offline_four_spatial_pairs',rootPreview=preview,reviewedAt=now);save(R/'audit/contact-N-review.json',c)
root['directions'][d]={'status':'accepted_offline_after_user_feedback','reviewedAt':now,'frames':c['frames'],'method':preview['method'],'notes':[preview['observations']],'contactReview':'audit/contact-N-review.json','rootPreview':preview,'clientValidated':False};save(R/'audit/bamboo-root-acceptance.json',root);validate_contact(R,d)
print('N preview recorded.')

