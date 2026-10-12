from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,sys
from datetime import datetime
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1]
sh=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inv=json.loads((R/'inventory-hit.json').read_text(encoding='utf-8-sig'))
for direction in sys.argv[1:] or ['S','SW']:
 fs=sorted([x for x in inv['frames'] if x['action']=='run' and x['direction']==direction],key=lambda x:x['frame'])
 assert len(fs)==16 and [x['frame'] for x in fs]==list(range(1,17))
 rows=[];audit=[]
 for f in fs:
  p=R/f['path']; h=sh(p); assert h==f['sha256']
  rec=json.loads((R/f['source_record']).read_text(encoding='utf-8-sig'))
  assert rec['export']['sha256']==h
  im=Image.open(p); assert im.size==(1024,1024) and im.mode=='RGBA'
  source=R/rec['file']; assert source.exists() and sh(source)==rec['sha256']
  check={'file':f['path'],'exportSHA':True,'recordSHA':True,'nativeSHA':True,'size':list(im.size),'mode':im.mode,'generationRecord':f['source_record']}
  if 'LANCZOS' in rec['export']['operation']:
   native=Image.open(source).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
   check['nativeDownsamplePixelsExact']=ImageChops.difference(native,im).getbbox() is None
   assert check['nativeDownsamplePixelsExact']
  for suffix in ['.png.generation.json','.generation.json']:
   side=p.with_suffix(suffix)
   if side.exists():
    s=json.loads(side.read_text(encoding='utf-8-sig')); assert s['sha256']==h and s['generationRecord']==f['source_record']
    check.setdefault('sidecars',[]).append(str(side.relative_to(R)))
  foot='RIGHT' if 7<=f['frame']<=14 else 'LEFT'
  seq=(list(range(7,15)) if foot=='RIGHT' else [15,16,1,2,3,4,5,6])
  pair=seq.index(f['frame'])//2+1
  rows.append({'file':f['path'],'path':f['path'],'frame':f['frame'],'sha256':h,'supportFoot':foot,'positionPair':pair,'durationMs':75,'source_record':f['source_record'],'staticVerdict':'passed','observedSupport': ['central_flat_contact_and_knee_load','under_hip_weight_transfer','behind_hip_contact_passing_leg','rear_forefoot_push_approaching_other_contact'][pair-1]})
  audit.append(check)
 assert len(set(x['sha256'] for x in rows))==16
 pairs=[]
 for foot,seq in [('RIGHT',list(range(7,15))),('LEFT',[15,16,1,2,3,4,5,6])]:
  for k in range(4):
   ns=seq[k*2:k*2+2]
   pairs.append({'supportFoot':foot,'position':k+1,'frames':ns,'durationMs':150,'description':['中央落地与屈膝压缩','同脚移到髋下，身体经过支点','同脚在髋后承重，对侧膝前摆','同脚后掌持续蹬地，对侧脚伸向下次落点'][k], 'frameSHA256':[next(x['sha256'] for x in rows if x['frame']==n) for n in ns],'distinctIndependentPoses':True})
 rep={'schemaVersion':1,'direction':direction,'action':'run','reviewedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'reviewer':'finish_s_sw','status':'static_passed_dynamic_pending_root_review','frameCount':16,'frameMs':75,'cycleMs':1200,'frames':rows,'supportPairs':pairs,'supportSequences':{'RIGHT':list(range(7,15)),'LEFT':[15,16,1,2,3,4,5,6]},'knownUnresolvedArtFailures':[],'staticEvidence':[f'previews/run-{direction}-position-pairs-hit-review.png',f'work/run-{direction}/run-{direction}-contact-sheet.png'],'observations': ['逐帧核对两腿连接和持物归属：解剖右手五符扇、左手铜铃，无持物换手。','同脚连续8张独立姿态，四个位置各两张；不是复制静态或延时补帧。','S按纵深看鞋掌承重；SW按左下行进轴看髋前到髋后，膝踝鞋掌一致，无明显脚掌外翻。','首尾16→01保持LEFT支撑，06→07与14→15交替；后掌持续接触已补绘，未用最低像素统一贴地。'],'limits':['本子代理完成逐图与接地对表静态视觉核对；主线程统一执行可见浏览器正常/慢放动态抽验。','声明根点512/920为框架锚点，不强制所有脚掌y920。','客户端未接入、未运行验收。'],'sourceAudit':audit,'modelEvidence':{'configuredTarget':'GPT Image 2.5 Sunburst / max','submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'route':'host-managed builtin image_gen','confirmation':'未确认：工具未开放选择器，返回未披露实际型号/质量。'}}
 out=R/f'reviews/run-{direction}-position-pairs-final-review-20261004.json'
 out.write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
 for f in inv['frames']:
  if f['action']=='run' and f['direction']==direction:f['visual_status']='two_frame_position_static_passed_dynamic_review_pending'
 print(direction,'static review and source audit written: 16 frames')
(R/'inventory-hit.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding='utf-8')

