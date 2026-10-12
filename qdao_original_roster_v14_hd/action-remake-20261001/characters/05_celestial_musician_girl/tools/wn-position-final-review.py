from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
r=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/05_celestial_musician_girl');p=r/'provenance/ground-contact-20261004/position-selection-WN.json'
s=json.loads(p.read_text(encoding='utf-8-sig'))
for x in s:
 x['visualStatus']='offline_sequence_review_passed_candidate_for_parent_promotion'
 if x['direction']=='W' and x['targetFrame']==7:x['visualNotes']+=' 该图后掌接触带较08略低；保持固定配准，未逐帧贴线；静态仍可读前掌蹬地。'
 if x['direction']=='N' and x['targetFrame']==11:x['visualNotes']+=' 保留原N10压低缓冲及躯干高度，未把真实重心压缩当比例错误。'
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
checks=[]
for x in s:
 im=Image.open(r/x['sourceFile']);a=im.getchannel('A');checks.append({'direction':x['direction'],'frame':x['targetFrame'],'size':list(im.size),'mode':im.mode,'edgeMaxAlpha':max(a.crop(box).getextrema()[1] for box in [(0,0,1024,1),(0,1023,1024,1024),(0,0,1,1024),(1023,0,1024,1024)]),'sha256Verified':sha(r/x['sourceFile'])==x['sha256'],'sourceGenerationRecordSha256Verified':sha(r/x['sourceGenerationRecord'])==x['sourceGenerationRecordSha256']})
assert all(x['size']==[1024,1024] and x['mode']=='RGBA' and x['edgeMaxAlpha']==0 and x['sha256Verified'] and x['sourceGenerationRecordSha256Verified'] for x in checks)
report={'createdAt':datetime.now(timezone.utc).isoformat(),'reviewer':'finish_ew','status':'offline_WN_sequence_review_complete_pending_parent_promotion','selection':'provenance/ground-contact-20261004/position-selection-WN.json','selectionSha256':sha(p),'count':32,'uniqueSourceFiles':len({x['sourceFile'] for x in s}),'uniqueSha256':len({x['sha256'] for x in s}),'independentNewEditsSelected':sum(x['operation'].startswith('independent') for x in s),'byteExactReorderedReuse':sum(x['operation'].startswith('byte_exact') for x in s),'timing':'16x75ms=1200ms unchanged uniform','registration':{'scale':0.65,'W':[565,1202],'N':[645,1180],'target':[512,942],'perFrameAlignment':False},'visualEvidence':[{'file':'provenance/ground-contact-20261004/WN-position-'+d+'-'+kind+'.jpg','sha256':sha(r/('provenance/ground-contact-20261004/WN-position-'+d+'-'+kind+'.jpg')),'actuallyViewed':True} for d in ['W','N'] for kind in ['full','legs']],'sequenceConclusions':[{'direction':d,'rightContinuousSupportFrames':[1,2,3,4,5,6,7,8],'leftContinuousSupportFrames':[9,10,11,12,13,14,15,16],'pairs':[[1,2],[3,4],[5,6],[7,8],[9,10],[11,12],[13,14],[15,16]],'pairReview':'每对2张独立图；依次前方接受负荷、早承重、髋下/略后晚承重、后方前掌蹬地；按膝踝连线和近远腿遮挡追踪，未把画面左右当换腿。','loopReview':'08至09与16至01由后方支撑脚蹬地过渡到对侧落地，未见双腿交换、多肢或持琴拓扑断开。','handsInstrument':'W近LEFT臂跨琴上端抓握、远RIGHT手低弦保持；N背视左手琴上端握持与遮挡连续。','remainingNecessaryCorrections':[]} for d in ['W','N']],'rejectedCandidates':[{'file':'staging/run/W/01-v5.native.png','reason':'前掌改平但高度仍像预接触，改用v6'},{'file':'staging/run/W/07-v2.native.png','reason':'后蹬前掌偏高，改用v3'},{'file':'staging/run/W/08-v2.native.png','reason':'自由前脚更抬高，未朝下次落地推进，改用v3'},{'file':'staging/run/W/16-v3.native.png','reason':'后支撑LEFT脚仍腾空，改用v4'}],'limitations':'仅离线原生逐张与等比例整圈/腿部成对静态审阅。W07支撑带较08略低，未通过整图挪动或贴脚处理；未进行客户端世界移动或地面碰撞验证。N原10压低姿态保留。','finalFilesModified':False,'clientValidated':False,'checks':checks}
(r/'provenance/ground-contact-20261004/WN-position-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selectionSha256':sha(p),'reportSha256':sha(r/'provenance/ground-contact-20261004/WN-position-review.json'),'count':32,'new':14,'reused':18,'allBordersAlphaZero':True}))

