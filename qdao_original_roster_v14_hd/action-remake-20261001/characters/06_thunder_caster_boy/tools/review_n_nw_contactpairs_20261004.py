"""Build immutable SHA-bound N/NW contact-position review and previews; runtime is read-only."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
O=R/'review'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pairs=[('右脚',[14,15],'前端初接'),('右脚',[0,1],'前侧承重'),('右脚',[2,3],'身体经过'),('右脚',[4,5],'后侧蹬离'),('左脚',[6,7],'前端初接'),('左脚',[8,9],'前侧承重'),('左脚',[10,11],'身体经过'),('左脚',[12,13],'后侧蹬离')]
observations={
'N':['右靴向北前方适度收进，小腿保留自然短比例；左脚后折悬空，14到15落膝有差别。','右鞋跟落平，支撑膝缓冲；左腿从后折向前摆，头身和肩肘连续。','右脚仍承重，身体抬起经过；03已改掉过早抬跟的大块鞋底，左腿推进。','右腿延伸到身体后方，前掌接触、跟渐抬；左腿折起准备落地。','左靴向北前方适度收进，膝微屈；右脚折起，06/07为独立落地姿态。','左鞋跟平足承重，右腿回收前摆；重心从压低转向经过。','左足持续承重，11已改掉提前蹬离；右脚抬起未提前接管支撑。','左腿后伸渐抬跟、前掌蹬离，右腿向前准备下一次14/15初接。'],
'NW':['右靴在画面右侧向左上收进，近端鞋跟/远端鞋尖明确，左脚折起；不是换成左脚支撑。','右靴由前端逐步回到身体下方，膝弯承重，左脚仍抬起。','右脚位置向右下后侧推进，02/03鞋跟仍承重；左腿前摆，不再03提前腾空。','右腿向画面右下延伸、前掌蹬离跟渐升；左腿向左上前摆。','左脚位于左前侧，膝自然弯曲，右脚抬起；足位随透视推进而不增加脚掌外撇。','左足落平、髋部经过前侧承重位置；08/09旧ground4修正保留，右脚不抢支撑。','保持画面左腿承重，10/11修正了旧图换成右腿支撑的错误；右腿始终折起悬空。','左腿维持到后侧蹬离，12/13已重画为左前掌接触、逐渐抬跟；右腿在右侧前摆，准备14初接。']}
changed={'N':[0,3,4,5,6,7,11,12,13,14,15],'NW':[2,3,4,5,8,9,10,11,12,13,14,15]}
issues=[];frames=[];natives=[]
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
for d in ['N','NW']:
 imgs=[];sources=[]
 for n in range(16):
  p=R/'runtime/run'/d/f'{n:02d}.png';g=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8-sig'));im=Image.open(p).convert('RGBA');imgs.append(im)
  if im.size!=(1024,1024) or im.getchannel('A').getextrema()[0]!=0:issues.append(f'{d}/{n}:runtime format')
  if sha(p)!=g['sha256']:issues.append(f'{d}/{n}:runtime SHA')
  native=R/g['derivedFrom'][0]['file'];natives.append(g['derivedFrom'][0]['sha256'])
  if not native.exists():issues.append(f'{d}/{n}:native missing')
  else:
   ni=Image.open(native).convert('RGBA')
   if ni.size!=(1254,1254) or sha(native)!=natives[-1]:issues.append(f'{d}/{n}:native mismatch')
   if ni.resize((1024,1024),Image.Resampling.LANCZOS).tobytes()!=im.tobytes():issues.append(f'{d}/{n}:transform mismatch')
  pairindex=next(i for i,(_,ns,_) in enumerate(pairs) if n in ns);leg,ns,phase=pairs[pairindex]
  row={'direction':d,'frame':n,'file':p.relative_to(R).as_posix(),'sha256':sha(p),'generationRecord':p.relative_to(R).as_posix()+'.generation.json','nativeSource':g['derivedFrom'][0],'supportLeg':leg,'screenSupportSide':'右' if leg=='右脚' else '左','pairFrames':ns,'positionPhase':phase,'frameMs':75,'pairMs':150,'staticObservation':observations[d][pairindex],'changedInContactRound':n in changed[d],'actualModel':g.get('actualModel'),'actualQuality':g.get('actualQuality')}
  frames.append(row);sources.append({k:row[k] for k in ['file','sha256','generationRecord']})
 for ms in [75,300]:
  q=O/f'run_{d}_contactpairs_{16*ms}.webp';a=[im.resize((512,512),Image.Resampling.LANCZOS) for im in imgs];a[0].save(q,save_all=True,append_images=a[1:],duration=ms,loop=0,lossless=True,method=4)
  q.with_name(q.name+'.generation.json').write_text(json.dumps({'file':q.relative_to(R).as_posix(),'sha256':sha(q),'derivedFrom':sources,'operation':'16 separate source frames, complete-canvas uniform512 preview; uniform timing, no interpolation/mirror/warp','frameMs':ms,'cycleMs':16*ms,'actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2),encoding='utf-8')
 board=Image.new('RGB',(1024,1232),(230,233,230));dr=ImageDraw.Draw(board)
 for i,(leg,ns,phase) in enumerate(pairs):
  x=i%4*256;y=i//4*616;dr.text((x+4,y+4),f'{d} {leg} {phase}',font=font,fill=(25,50,45))
  for j,n in enumerate(ns):
   tile=imgs[n].resize((256,256),Image.Resampling.LANCZOS);board.paste(tile,(x,y+29+j*286),tile);dr.text((x+4,y+286+j*286),f'{n:02d} · 75ms',font=font,fill=(25,50,45))
 q=O/f'run_{d}_contactpairs_positions.png';board.save(q);q.with_name(q.name+'.generation.json').write_text(json.dumps({'file':q.relative_to(R).as_posix(),'sha256':sha(q),'derivedFrom':sources,'operation':'Full-canvas256 thumbnails in 8 actual two-frame support positions; review only','actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2),encoding='utf-8')
if len(set(natives))!=32:issues.append('duplicate native')
refs=[]
for d in ['N','NW']:
 p=R.parent/'09_bamboo_archer_girl/runtime/run'/d/('01.png' if d=='N' else '09.png')
 refs.append({'file':str(p),'sha256':sha(p),'usage':'实际查看、用于同方向鞋轴和支撑/摆动对照；不复制角色身份或姿态'})
report={'schemaVersion':1,'reviewedAt':datetime.now(timezone.utc).isoformat(),'character':'06_thunder_caster_boy','scope':'run/N and run/NW only','latestHumanRequirement':'直脚着地两帧，再旁边点两帧，再旁边点两帧，再旁边点俩帧，依次类推','interpretation':'每只支撑脚连续完成4个相对位置，每位置2张真实独立姿态；初接、前侧承重、身体经过、后侧蹬离后换另一脚。鞋轴随N/NW方向，位置推进不靠外撇。','timing':{'frameMs':75,'pairMs':150,'cycleMs':1200,'slowFrameMs':300},'pairMap':[{'supportLeg':l,'frames':ns,'positionPhase':p} for l,ns,p in pairs],'actualContactFrames':{'N':{'right':[14,15,0,1,2,3,4,5],'left':[6,7,8,9,10,11,12,13]},'NW':{'right':[14,15,0,1,2,3,4,5],'left':[6,7,8,9,10,11,12,13]}},'flatLoadedSubsets':{'N':{'right':[14,15,0,1,2,3],'left':[6,7,8,9,10,11]},'NW':{'right':[14,15,0,1,2,3],'left':[6,7,8,9,10,11]}},'directions':{d:{'travel':'正背向上' if d=='N' else '背斜向左上','observations':observations[d],'changedContactRound':changed[d],'retained':[n for n in range(16) if n not in changed[d]]} for d in ['N','NW']},'reviewMethod':['逐张实际查看32张当前原尺寸图；所有新增候选图均在采用前实际查看','实际查看09同方向联系图及正式单帧，保留本角色造型与持物','逐槽核实1024RGBA、原生1254、原生与导出SHA、一对一全画布Lanczos像素一致性','实际检查32帧支撑腿连续、膝踝脚轴、摆腿和肩肘双持；此项为单帧和联系图静态检查'],'technicalIssues':issues,'uniqueNativeCount':len(set(natives)),'staticIndividualFrameReviewCompleted':True,'staticKnownUnresolved':[],'frozenForParentPlaybackReview':True,'wholeCycleVisualApproved':False,'remainingVerification':['root对当前SHA执行正常1倍/慢放及首尾组合动态复核','客户端未接入，用户最终观感未确认'],'clientIntegrated':False,'modelNote':'配置目标GPT Image 2.5 Sunburst / max；宿主管理内置入口无型号/质量选择器，实际model/quality未披露，null未确认','referenceImages':refs,'frames':frames}
(O/'run_N_NW_contactpairs_20261004.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# N / NW 接地位置两帧组修正','', '两向各16张独立姿态，75ms/帧，1200ms整圈。当前32帧已完成静态修图并冻结，供根代理检查整圈动态。','', '| 支撑脚 | 实际帧号 | 相对位置 |','|---|---|---|']
for leg,ns,phase in pairs:lines.append(f'|{leg}|{ns[0]:02d}/{ns[1]:02d}|{phase}|')
lines+=['','两向右脚连续接触：14、15、00、01、02、03、04、05；左脚：06–13。每次前6帧包含脚跟承重，末2帧以前掌蹬离。接触由实际鞋掌/小腿姿态判断，未用重复图、延长停留、镜像或整图位移凑数。','', 'N修复早接位置过低/短腿失败稿、03/11过早抬跟，保持鞋尖直向北；NW修复02/03承重、10–13提前换支撑腿，14/15右脚向前收进。NW08/09已有左脚接地修正保留。','']
for d in ['N','NW']:
 lines+=[f'{d} 实图观察：']+[f'- {ns[0]:02d}/{ns[1]:02d}：{observations[d][i]}' for i,(_,ns,_) in enumerate(pairs)]+['']
lines+=['原生1254×1254，正式1024×1024 RGBA，全画布等比导出；32张来源互异，逐图SHA及模型未确认说明见JSON。','', '静态尚无已知未处理项。整圈动态最终验收由root针对当前SHA进行；不冒称已接入客户端或已由用户确认。','', '[逐图来源与验收](run_N_NW_contactpairs_20261004.json)','[N 正常1200ms](run_N_contactpairs_1200.webp) · [NW 正常1200ms](run_NW_contactpairs_1200.webp)','[N 慢放4800ms](run_N_contactpairs_4800.webp) · [NW 慢放4800ms](run_NW_contactpairs_4800.webp)','[N位置分组](run_N_contactpairs_positions.png) · [NW位置分组](run_NW_contactpairs_positions.png)']
(O/'run_N_NW_contactpairs_20261004.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'frames':len(frames),'uniqueNative':len(set(natives)),'issues':issues},ensure_ascii=False))

