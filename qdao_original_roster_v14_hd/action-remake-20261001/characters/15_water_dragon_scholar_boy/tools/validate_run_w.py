from pathlib import Path
from PIL import Image,ImageSequence
import json,hashlib
from datetime import datetime,timezone
b=Path(__file__).resolve().parents[1]
s=json.loads((b/'audit/run-W-selection.json').read_text(encoding='utf-8'))['frames']
checks=[]
for r in s:
 p=b/r['source']; im=Image.open(p)
 rec=json.loads((b/r['generationRecord']).read_text(encoding='utf-8-sig'))
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']==rec['sha256']
 assert im.size==(1254,1254) and im.mode=='RGBA'
 checks.append({'frame':r['frame'],'source':r['source'],'sha256':r['sha256'],'native':[im.width,im.height],'alphaExtrema':im.getchannel('A').getextrema(),'nonzeroBBox':im.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox(),'note':r['review']['notes']})
gifChecks=[]
for name,expected in [('legacy480',480),('trial640',640),('trial720',720),('trial800',800),('slow2880',2880)]:
 p=b/'audit'/f'run-W-{name}.gif'; im=Image.open(p); ds=[f.info['duration'] for f in ImageSequence.Iterator(im)]
 assert len(ds)==16 and sum(ds)==expected
 gifChecks.append({'file':p.relative_to(b).as_posix(),'frames':len(ds),'durationsMs':ds,'cycleMs':sum(ds)})
report={'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'finish_w','staticSelected':16,'dynamicAcceptance':'pending_root_visual_review','clientIntegration':'not_integrated_no_local_client','transform':{'sourceCanvas':[1254,1254],'fixedResize':[940,940],'fixedInset':[42,49],'target':[1024,1024],'perFrameTransform':False},'groundingObserved':{'nearLeftPlantedSourceY':[1200,1204],'nearLeftOutputApproxY':[949,952],'farRightPlantedSourceY':1191,'farRightOutputApproxY':942,'note':'实际近远脚透视层诊断，不强制单条最低脚线。04前掌略低近脚参考仍需主审。'},'reselectedSources':{'05':'run-W-04-v1.png','08':'run-W-05-v1.png'},'newEditsSelected':['run-W-03-v5','run-W-04-v3','run-W-10-v3','run-W-11-v3','run-W-15-v2','run-W-16-v3'],'rejectedThisTurn':[{'source':'run-W-03-v3.png','reason':'近肩错误连接持扇手，换手深度错误'},{'source':'run-W-03-v4.png','reason':'相同错误未修复'},{'source':'run-W-16-v2.png','reason':'前靴高度与15过近，预触地伸腿不足'}],'browserVerification':{'url':'http://127.0.0.1:8716/audit/run-W-review.html','loaded':True,'trialOptionsObservedMs':[640,720,800,2880],'frame16Inspected':True,'limits':'只证明浏览器真实帧可播放/可切时长与逐图，整段审美动态仍待主审；未核验客户端位移。'},'gifChecks':gifChecks,'frames':checks,'remaining':['主审全段摆臂/衣摆/首尾衔接','最终选择640/720/800ms节奏及是否给予承重更多时长','与客户端位移结合检查滑步']}
(b/'audit/run-W-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'png':16,'uniqueHashes':len(set(r['sha256']for r in s)),'gifCycleChecks':[(r['file'],r['cycleMs'])for r in gifChecks]},ensure_ascii=False))

