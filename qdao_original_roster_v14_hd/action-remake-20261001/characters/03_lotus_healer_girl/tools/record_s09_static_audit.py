from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent.parent;B=R.parent/'09_bamboo_archer_girl'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def selected(name):
 p=R/name;j=json.loads(p.read_text(encoding='utf8'));out=[]
 for f in j['frames']:
  raw=f.get('source',f.get('file'));s=Path(raw);s=s if s.is_absolute() else (R/s).resolve()
  out.append({'slot':f.get('slot',f.get('frame')),'source':str(s),'sourceSha256':sha(s),'durationMs':f['durationMs'],'observedPhase':f['observedPhase']})
 assert len(out)==16 and sum(f['durationMs'] for f in out)==1200
 return {'input':name,'inputSha256':sha(p),'frames':out}
auditp=R/'review/run-NE-E-W-vs09-static-audit-20261004.json';old=json.loads(auditp.read_text(encoding='utf8'))
old['current03SelectedFrameHashes']=[selected(x) for x in ['review/run-NE-sequence-input.json','review/run-E-selection.json','review/run-W-sequence-input.json']]
old['hashSnapshotAtUtc']=datetime.now(timezone.utc).isoformat();wr(auditp,old)
m=json.loads((B/'manifest.json').read_text(encoding='utf8'));seq=next(s for s in m['sequences'] if s['action']=='run' and s['direction']=='S');refs=[]
for f in seq['frames']:
 p=B/f['file'];s=sha(p);assert s==f['sha256']
 refs.append({'slot':f['frame'],'source':str(p),'sourceSha256':s,'manifestMatch':True})
full=['generation/S/03-v1.png','generation/S/04-v2.png','generation/S/11-v1.png','generation/S/12-v2.png','generation/S/04-v1.png','generation/S/08-v1.png','generation/S/09-v1.png','generation/S/14-v1.png','generation/S/16-v1.png','generation/S/01-v2.png']
audit={'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'direction':'S','action':'run','role':'03_lotus_healer_girl','reference':'09_bamboo_archer_girl current user-recognized S runtime','scope':'read-only independent static review; sources and images unchanged','status':'no_major_yaw_or_leg_identity_error_seen_static_continuity_pending','visualAccepted':False,'browserTest':False,'clientTest':False,'current03':selected('review/run-S-sequence-input.json'),'reference09':refs,'fullImagesActuallyViewed03':[{'source':str(R/x),'sha256':sha(R/x)} for x in full],'fullImagesActuallyViewed09':[{'source':str(B/x),'sha256':sha(B/x)} for x in ['runtime/run/S/04.png','runtime/run/S/12.png']],'contactSheetsActuallyViewed':[{'source':str(p),'sha256':sha(p)} for p in [R/'preview/run-S-contact.jpg',B/'preview/qa/run-S-contact.png']],'majorDirectionError':{'found':False,'meaning':'本次可见静态证据未发现，不代表全动态或客户端通过。','feet':'03 S支撑/前摆鞋尖主要朝屏下，膝踝相连，没有看到双脚鞋尖向屏幕左右叉开的明显V形yaw。提膝时鞋底朝镜头是前伸俯仰，不能自动当作外撇。','supportIdentity':'当前03 S04-v2是右腿后支撑、左膝前提；S12-v2是左腿后支撑、右膝前提，腿序相反且能追踪。S10已选v2，未见旧v1式支撑腿交换。','hands':'人物右灯在屏左、左瓶在屏右，关键原图无换手。'},'comparisonTo09':{'phaseMatching':'以实际承重/提膝姿态比较；03与09不是相同帧号相同支撑腿，不拿09 S04去强制03 S04复制腿序。','feet':'09露膝与长靴使膝踝方向更容易看；03宽裤/圆鞋遮挡更多，但当前正面鞋尖没有明显左右外转。','contact':'两者都有近接触连续数帧，不能仅用全图最低alpha判断脚是否接地；南向深度投影需要固定动作根点和客户端验证。'},'continuityFindings':[{'severity':'needs_dynamic_review','range':'03→04','finding':'03中支撑到04前提膝集中一跳，左腿passing小段不足；尚未见错腿/外撇。'},{'severity':'needs_dynamic_review','range':'11→12→13','finding':'12抬身幅度比04更大，可能产生不对称竖向跳动；不应通过逐帧移图修饰。'},{'severity':'clear_arm_reversal_risk','range':'06→07→08','finding':'07取原04-v1，腿确实更前伸；但灯握点/灯体回落，08又向前抬起，形成局部反摆，需1200ms实际播放确认是否突兀。'},{'severity':'timing_boundary_pending','range':'08→09','finding':'两张前左鞋已经非常接近接触区，09继续承重；实际接触起点可能落在08末段，事件09仍为候选。'},{'severity':'timing_boundary_pending','range':'15→16→01','finding':'15前右鞋露底前伸，16已进入接触、01继续接触，腿序正确；16→01鞋底少量回升仍需整圈看。'}],'noEditEvidence':{'sourcePNGModified':False,'selectionInputModified':False,'previewModified':False,'reference09Modified':False,'generatedImages':0},'conclusion':'未发现需要立即重画的重大脚朝向/支撑腿错误。优先动态核查07手臂反摆与12身高跳变，保留1200ms=16×75；未给视觉通过结论。'}
wr(R/'review/run-S-vs09-static-audit-20261004.json',audit)
print(json.dumps({'03ComparedSlotsWithSha':64,'09SFramesHashVerified':16,'SAudit':'review/run-S-vs09-static-audit-20261004.json','SmajorYawOrLegSwapSeen':False,'visualAccepted':False}))

