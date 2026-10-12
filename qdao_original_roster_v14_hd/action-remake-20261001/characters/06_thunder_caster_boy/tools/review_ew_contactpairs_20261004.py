"""SHA-bound E/W final position segments and previews, read-only runtime."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];O=R/'review'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pairs=[('右脚',[0,1],'前端初接','脚掌前端落平，膝开始屈曲；异侧脚回收'),('右脚',[2,3],'前侧承重','脚仍在髋前，膝继续缓冲，身体向支撑脚接近'),('右脚',[4,5],'身体经过','支撑脚由髋下进入稍后方，另一腿抬起前摆'),('右脚',[6,7],'后侧蹬离','支撑脚到身后，前掌承重且鞋跟渐升；前摆脚准备落地'),('左脚',[8,9],'前端初接','换左脚前方落平，另一脚回收'),('左脚',[10,11],'前侧承重','足位仍在髋前，身体逐步接近支撑足'),('左脚',[12,13],'身体经过','支撑脚进入身下后稍后方，另腿前摆'),('左脚',[14,15],'后侧蹬离','后侧前掌接触、鞋跟抬起；另一脚前伸准备接00')]
changed=[2,3,4,5,6,7,11,12,13,14,15]
frames=[];issues=[];nativehashes=[];font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
for d in ['E','W']:
 ims=[];derived=[]
 for n in range(16):
  p=R/f'runtime/run/{d}/{n:02}.png';g=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8-sig'));im=Image.open(p).convert('RGBA');ims.append(im)
  if sha(p)!=g['sha256'] or im.size!=(1024,1024) or im.getchannel('A').getextrema()[0]!=0:issues.append(f'{d}/{n:02} runtime mismatch')
  source=g['derivedFrom'][0];nativehashes.append(source['sha256']);sp=R/source['file'];ng=json.loads((R/source['generationRecord']).read_text(encoding='utf-8-sig'))
  if not sp.exists():sp=Path(ng['evidence']['hostOutputPath'])
  native=Image.open(sp).convert('RGBA');expected=Image.new('RGBA',(1024,1024));expected.alpha_composite(native.resize((901,901),Image.Resampling.LANCZOS),(61,97))
  if native.size!=(1254,1254) or sha(sp)!=source['sha256'] or expected.tobytes()!=im.tobytes():issues.append(f'{d}/{n:02} native / uniform transform mismatch')
  leg,indices,phase,desc=next(v for v in pairs if n in v[1])
  f={'direction':d,'frame':n,'file':p.relative_to(R).as_posix(),'sha256':sha(p),'generationRecord':p.relative_to(R).as_posix()+'.generation.json','supportLeg':leg,'pairFrames':indices,'positionPhase':phase,'observation':desc,'frameMs':75,'pairMs':150,'nativeSource':source,'changedThisRound':n in changed,'actualModel':ng.get('actualModel'),'actualQuality':ng.get('actualQuality'),'staticFrameReviewCompleted':True}
  frames.append(f);derived.append({k:f[k] for k in ['file','sha256','generationRecord']})
 for ms in [75,300]:
  q=O/f'run_{d}_contactpairs_{ms*16}.webp';small=[i.resize((512,512),Image.Resampling.LANCZOS) for i in ims]
  small[0].save(q,save_all=True,append_images=small[1:],duration=ms,loop=0,lossless=True,method=4)
  q.with_name(q.name+'.generation.json').write_text(json.dumps({'file':q.relative_to(R).as_posix(),'sha256':sha(q),'derivedFrom':derived,'operation':'Full canvas uniform512 preview,16 independent current frames,uniform duration; no interpolation or per-frame anchor changes','frameMs':ms,'cycleMs':16*ms,'actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2),encoding='utf-8')
 board=Image.new('RGB',(1280,1400),(224,230,226));dr=ImageDraw.Draw(board)
 for n,im in enumerate(ims):
  x=n%4*320;y=n//4*350;small=im.resize((320,320),Image.Resampling.LANCZOS);board.paste(small,(x,y),small);leg,inds,phase,desc=next(v for v in pairs if n in v[1]);dr.text((x+6,y+320),f'{d}{n:02} {leg} {phase}',font=font,fill=(25,45,40))
 q=O/f'run_{d}_contactpairs_positions.png';board.save(q)
 q.with_name(q.name+'.generation.json').write_text(json.dumps({'file':q.relative_to(R).as_posix(),'sha256':sha(q),'derivedFrom':derived,'operation':'Fixed full canvas320 review contact table with observed support-position labels; review only','actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2),encoding='utf-8')
if len(set(nativehashes))!=32:issues.append('native duplicates')
rep={'reviewedAt':datetime.now(timezone.utc).isoformat(),'scope':'run/E and run/W','humanRequirement':'直脚着地两帧，再旁边点两帧，依次过渡','interpretation':'同一支撑脚相对身体沿跑向反方向进程，四段各2张独立姿态，另脚交替；不通过外撇、重复帧、整图移动伪造','timing':{'frameCount':16,'frameMs':75,'cycleMs':1200,'pairMs':150,'slowCycleMs':4800},'pairMap':[{'supportLeg':leg,'frames':ns,'positionPhase':phase,'observation':desc} for leg,ns,phase,desc in pairs],'directions':{'E':{'travel':'画面右侧','supportProgression':'画面右前→髋下→画面左后，脚尖始终向右','changedFrames':changed,'retainedFrames':[0,1,8,9,10]},'W':{'travel':'画面左侧','supportProgression':'画面左前→髋下→画面右后，脚尖始终向左','changedFrames':changed,'retainedFrames':[0,1,8,9,10]}},'staticIndividualFrameReviewCompleted':True,'staticReview':'已实看32张现用独立姿态与两向联系表，确认接地脚链连续、前掌后跟分离、腿脚无明显侧外翻；武器与符牌持手保留，肩肘带动物件前后摆动。','wholeCycleVisualApproved':False,'browserPlaybackVerification':'交root针对本报告SHA完成正常1倍/慢放/暂停逐帧验证；本文静态检查不冒称客户端或用户动态验收。','technicalIssues':issues,'clientIntegrated':False,'modelNote':'目标GPT Image2.5Sunburst/max；实际提交model/quality和返回未披露，null未确认','rejectedCandidates':[{'file':'work/run_E_10_progress_v1.png','reason':'镜头/头部放大，保留原正确E10v6'},{'file':'work/run_W_10_progress_v1.png','reason':'手臂借用初接参考，保留原正确W10v1'},{'file':'work/run_W_07_progress_v1.png','reason':'后脚接地不明确，采用v2'},{'file':'work/run_W_13_progress_v1.png','reason':'错误退回初接姿态，采用v2'},{'file':'work/run_W_14_progress_v1.png','reason':'错误初接而非后蹬，采用v2'},{'file':'work/run_W_15_progress_v1.png','reason':'前脚低于后侧支撑脚，采用v2'}],'frames':frames}
(O/'run_EW_contactpairs_20261004.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# E / W 两帧接地位置段修正','', '两向各16张独立姿态，每帧75ms，整圈1200ms；每个位置段两帧150ms。两向各修正11帧，正确00/01/08/09/10保留。','', '|支撑脚|帧号|相对位置|观察|','|---|---|---|---|']
for leg,ns,phase,desc in pairs:lines.append(f'|{leg}|{ns[0]:02}/{ns[1]:02}|{phase}|{desc}|')
lines+=['','E的支撑位置由画面右前经过髋下，再到左后；W由左前经过髋下到右后。变化是脚相对身体的前后位置，鞋尖仍沿跑向，未作镜像或外撇。','W07/13/14/15经过二次局部修正，明确后脚承重、前脚悬空。E10和W10的新候选分别因放大和改变手臂被拒，保留已正确正式帧。','', '已完成32张单帧与联系表静态复核，32来源互异，1254原生统一缩到901并固定放置(61,97)的逐像素核对通过。1倍与慢放浏览器功能验证交由root；尚未声称客户端接入或用户最终认可。','', '[逐帧SHA与来源](run_EW_contactpairs_20261004.json)','[E两帧位置图](run_E_contactpairs_positions.png) · [W两帧位置图](run_W_contactpairs_positions.png)','[E正常1200ms](run_E_contactpairs_1200.webp) · [W正常1200ms](run_W_contactpairs_1200.webp)','[E慢放4800ms](run_E_contactpairs_4800.webp) · [W慢放4800ms](run_W_contactpairs_4800.webp)']
(O/'run_EW_contactpairs_20261004.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'frames':len(frames),'uniqueNative':len(set(nativehashes)),'issues':issues},ensure_ascii=False))
