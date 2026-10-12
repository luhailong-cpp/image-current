import json,hashlib,datetime
from pathlib import Path
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
reportPath=R/'reviews/full-limb-N-W-20261004.json';j=read(reportPath)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
newHands={
3:'右扇腕由原前摆端点移至躯干侧约(390,605)，经过屈肘中位；与W02约(655,550)、W04约(240,550)形成分段轨迹，消除一次跨身约400px的突跳。右肩—肘—腕单链、5张符可辨，原左铃臂握持和位置保持。',
11:'右扇腕由原后摆端点移至躯干侧约(515,595)，经过屈肘中位；与W10约(220,580)、W12约(725,455)形成反向分段轨迹。远侧右臂至持扇腕连接清楚、5张符可辨；原左铃臂仍前摆，未添腕或换持手。'
}
for f in j['frames']:
 p=R/f['path']; side=read(p.with_suffix('.png.generation.json')); h=sha(p);im=Image.open(p)
 if f['direction']=='W' and f['frame'] in newHands:
  f.update(sha256=h,decision='replaced',generationRecord=side['generationRecord'],handChainObservation=newHands[f['frame']])
  f['reason']='手链：'+f['handChainObservation']+' 脚链：'+f['legChainObservation']
 assert f['sha256']==h==side['sha256']
 assert im.size==(1024,1024) and im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
 if f['decision']=='replaced':
  rec=read(R/side['generationRecord']);nat=R/rec['native']['file']
  assert sha(nat)==rec['native']['sha256']
  assert rec['actualModel'] is None and rec['actualQuality'] is None
  assert ImageChops.difference(Image.open(nat).resize((1024,1024),Image.Resampling.LANCZOS),im).getbbox() is None
j['reviewedAt']=now;j['revision']=2;j['actualReviewDate']='2026-10-05'
j['summary'].update(replaced=8,retained=24,replacedSlots=[f"run/{f['direction']}/{f['frame']:02}" for f in j['frames'] if f['decision']=='replaced'],hands='32帧持物身份与肩肘腕连接复核；W03/W11补充右扇腕经躯干侧的中位过渡，保留铃臂，5符可辨。')
j['evidence']['actualViewed']='32帧手臂放大与完整画布联系表；8新图原生全图和导入后序列复核；W02-04及W10-12重点逐图比较持扇腕轨迹。'
j['evidence']['referenceUse']='每张生成实际附身份与已确认风格；N支撑鞋用已看N08正后跟参照，W03/W11用已看前后帧约束腕部轨迹，保留原腿脚。'
j['trajectoryCheck']={'method':'人工静态对照1024画布，坐标为近似腕中心，不是姿态估计器测量。','W02-W03-W04':[[655,550],[390,605],[240,550]],'W10-W11-W12':[[220,580],[515,595],[725,455]],'finding':'新增中间位置将前后端点间的单帧跨身跳段拆开，持扇手仍沿对应肩肘腕链运动；最终动画播放由root验收。'}
j['checks']['newNativeShaAndUniformResizePixels']=8
for c in j['contactSheets']:c['sha256']=sha(R/c['path'])
j['knownUnresolvedArtFailures']=[]
reportPath.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
ip=R/'inventory-run-north.json';iv=read(ip);rr={(x['direction'],x['frame']):x for x in j['frames']}
for x in iv['frames']:
 k=(x.get('direction'),x.get('frame'))
 if k in rr:
  q=rr[k];assert x['sha256']==q['sha256']
  x['visual_status']='full_limb_static_review_pass_pending_root_dynamic_review'
  x['full_limb_review']={'report':reportPath.relative_to(R).as_posix(),'reviewedAt':now,'decision':q['decision'],'reason':q['reason']}
ip.write_text(json.dumps(iv,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(reportPath),'frames':32,'replaced':8,'retained':24,'newNativeExact':8,'W03':rr['W',3]['sha256'],'W11':rr['W',11]['sha256']},ensure_ascii=False))

