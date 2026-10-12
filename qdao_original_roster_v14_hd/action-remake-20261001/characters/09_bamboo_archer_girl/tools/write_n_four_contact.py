from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((ROOT/'review-parts/run-N.json').read_text(encoding='utf-8-sig'))
segments=[{'foot':'right','frames':[15,16,1,2],'count':4,'durationMs':300,'crossesLoopBoundary':True,'phases':['initial_contact','loading','early_weight_bearing','weight_bearing']},{'foot':'left','frames':[7,8,9,10],'count':4,'durationMs':300,'crossesLoopBoundary':False,'phases':['initial_contact','loading','weight_bearing','weight_bearing']}]
out={'reviewedAt':datetime.now(timezone.utc).isoformat(),'action':'run','direction':'N','minimumFourContactStaticStatus':'passed','latestSpatial242Status':'pending_spatial_allocation','latestSpatialRequirement':'中间接地4帧，旁边接地各2帧；四张低脚接触不能直接当成中间4帧已完成。','contactSegments':segments,'runtimeFilesChanged':['runtime/run/N/01.png','runtime/run/N/16.png'],'frames':[{'frame':int(r['slot'].split('/')[-1]),'slot':r['slot'],'file':'runtime/'+r['slot']+'.png','sha256':r['sha256'],'visualObservation':r['evidence'],'footOrientation':r['footOrientation']} for r in review['frames']],'dynamicVisualAcceptance':False,'clientIntegration':'not_integrated','reviewBasis':'逐张原图与当前接触表；右15/16/01/02与左07/08/09/10可追踪同脚平跟杯、薄金边和软膝承重。N16首次新稿和N01首次缩头稿均已判拒并以独立重绘替换；源图记录保留。'}
for r in out['frames']:assert r['sha256']==sha(ROOT/r['file'])
(ROOT/'audit/run-N-four-contact-20261004.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
review['fourContactReview20261004']={'source':'audit/run-N-four-contact-20261004.json','contactSegments':segments,'latestSpatial242Status':'pending_spatial_allocation','dynamicVisualAcceptance':False}
(ROOT/'review-parts/run-N.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
print('N actual four-contact frame evidence recorded; latest spatial2/4/2 remains pending.')
