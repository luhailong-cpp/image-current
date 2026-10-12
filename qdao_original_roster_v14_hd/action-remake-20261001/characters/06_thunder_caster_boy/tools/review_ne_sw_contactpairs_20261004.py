"""Build SHA-bound NE/SW two-pose contact-position review; never mutate runtime."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib
from datetime import datetime, timezone

R=Path(__file__).resolve().parents[1]
OUT=R/'review'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pairs=[
 ('右脚',[12,13],'前端初落地','脚向跑向前端伸出，鞋掌落平，膝开始缓冲'),
 ('右脚',[14,15],'前侧承重','足位向髋下回收，膝踝承受重量'),
 ('右脚',[0,1],'身体经过','足位进入身体下方，保持真实承重'),
 ('右脚',[2,3],'后侧蹬离','足位到身体后侧，前掌接触、鞋跟渐升'),
 ('左脚',[4,5],'前端初落地','换左脚向跑向前端落地，右脚抬起'),
 ('左脚',[6,7],'前侧承重','膝自然屈曲，左鞋掌放平承重'),
 ('左脚',[8,9],'身体经过','身体经过左足，右腿仍在摆动'),
 ('左脚',[10,11],'后侧蹬离','左足后移并渐抬跟，右腿准备前摆')]
changed={'NE':[1,2,3,4,5,6,10,12,13,15], 'SW':[0,1,2,3,4,5,6,7,10,12,13,14,15]}
issue=[]; frames=[]; native_shas=[]; font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
for d in ['NE','SW']:
 imgs=[]; derived=[]
 for n in range(16):
  p=R/'runtime'/'run'/d/f'{n:02d}.png'; g=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8-sig'))
  im=Image.open(p).convert('RGBA'); imgs.append(im)
  if im.size!=(1024,1024) or im.getchannel('A').getextrema()[0]!=0:issue.append(f'{d}/{n:02d} runtime dimensions/alpha')
  if g['sha256']!=sha(p):issue.append(f'{d}/{n:02d} SHA mismatch')
  src=R/g['derivedFrom'][0]['file']; native_shas.append(g['derivedFrom'][0]['sha256'])
  if src.exists():
   ni=Image.open(src).convert('RGBA')
   if ni.size!=(1254,1254) or sha(src)!=g['derivedFrom'][0]['sha256']:issue.append(f'{d}/{n:02d} native mismatch')
   if ni.resize((1024,1024),Image.Resampling.LANCZOS).tobytes()!=im.tobytes():issue.append(f'{d}/{n:02d} full canvas transform mismatch')
  else:issue.append(f'{d}/{n:02d} native absent during active round')
  leg,indices,phase,desc=next(x for x in pairs if n in x[1])
  frame={'direction':d,'frame':n,'file':p.relative_to(R).as_posix(),'sha256':sha(p),'generationRecord':p.relative_to(R).as_posix()+'.generation.json','nativeSource':g['derivedFrom'][0],'supportLeg':leg,'pairFrames':indices,'positionPhase':phase,'screenSupportSide':('右下' if leg=='右脚' else '左下') if d=='NE' else ('左下' if leg=='右脚' else '右下'),'frameMs':75,'actualModel':g.get('actualModel'),'actualQuality':g.get('actualQuality'),'changedThisRound':n in changed[d],'staticObservation':g.get('visualReview',''),'wholeCycleVisualApproved':False}
  frames.append(frame);derived.append({'file':frame['file'],'sha256':frame['sha256'],'generationRecord':frame['generationRecord']})
 for ms in [75,300]:
  q=OUT/f'run_{d}_contactpairs_{16*ms}.webp'
  ims=[im.resize((512,512),Image.Resampling.LANCZOS) for im in imgs]
  ims[0].save(q,save_all=True,append_images=ims[1:],duration=ms,loop=0,lossless=True,method=4)
  q.with_name(q.name+'.generation.json').write_text(json.dumps({'file':q.relative_to(R).as_posix(),'sha256':sha(q),'derivedFrom':derived,'operation':'Complete canvas uniform512 preview,16 distinct source frames, uniform timing; no frame interpolation or anchoring','frameMs':ms,'cycleMs':ms*16,'actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2),encoding='utf-8')
 board=Image.new('RGB',(1024,1220),(229,232,229));draw=ImageDraw.Draw(board)
 for i,(leg,indices,phase,desc) in enumerate(pairs):
  x=(i%4)*256;y=(i//4)*610
  draw.text((x+5,y+5),f'{d} {leg} {phase}',font=font,fill=(25,48,44))
  for j,n in enumerate(indices):
   im=imgs[n].resize((256,256),Image.Resampling.LANCZOS);board.paste(im,(x,y+30+j*285),im)
   draw.text((x+5,y+284+j*285),f'{n:02d} · 75ms',font=font,fill=(25,48,44))
 q=OUT/f'run_{d}_contactpairs_positions.png';board.save(q)
 q.with_name(q.name+'.generation.json').write_text(json.dumps({'file':q.relative_to(R).as_posix(),'sha256':sha(q),'derivedFrom':derived,'operation':'Full canvas256 thumbnails grouped by actual two-frame support-position segments; review only','actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2),encoding='utf-8')
if len(set(native_shas))!=32:issue.append('duplicate native source')
report={'schemaVersion':1,'reviewedAt':datetime.now(timezone.utc).isoformat(),'character':'06_thunder_caster_boy','scope':'run/NE and run/SW only','latestHumanRequirement':'直脚着地两帧，再旁边点两帧，再旁边点两帧，再旁边点俩帧，依次类推','interpretation':'同一支撑脚持续接触，四个相对位置段每段两张独立姿态；随后另一脚交替。位置按跑向与透视推进，不是增加脚掌外撇。','timing':{'frameMs':75,'cycleMs':1200,'pairMs':150,'slowFrameMs':300},'pairMap':[{'supportLeg':leg,'frames':indices,'position':phase,'observation':desc} for leg,indices,phase,desc in pairs],'directions':{'NE':{'travel':'画面右上，背斜视；近端可见鞋跟，鞋尖向远端右上','stanceProgression':'足位由跑向前端逐步回到髋下、再到身体左后侧；画面左右取决于解剖腿，不把鞋尖外撇当位置变化','changedFrames':changed['NE'],'retainedFrames':[n for n in range(16) if n not in changed['NE']]},'SW':{'travel':'画面左下，前斜视；鞋尖始终沿左下','stanceProgression':'脚位由画面左前端逐步回到髋下、再到身体右后侧；06/07已经降低翘尖、04重新建立左前脚接地','changedFrames':changed['SW'],'retainedFrames':[n for n in range(16) if n not in changed['SW']]}},'reviewMethod':['实际查看全部32张当前正式帧与新输出原生单帧','实际查看09竹弓少女NE/SW同向完整联系图和正式单帧','实际查看已重建的NE与SW完整联系图','检查原生1254尺寸、runtime1024透明、SHA与全画布Lanczos变换、32张原生来源互异'],'technicalIssues':issue,'staticIndividualFrameReviewCompleted':True,'wholeCycleVisualApproved':False,'browserPlaybackVerification':'交由root针对当前SHA执行；静态修图不能冒称1倍动态观看通过','clientIntegrated':False,'modelNote':'配置目标GPT Image2.5Sunburst/max；内置实际model/quality参数及返回均未披露，null未确认','frames':frames}
(OUT/'run_NE_SW_contactpairs_20261004.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# NE / SW 两帧位置段修正记录','', '两向各16帧，每帧75ms，整圈1200ms。保持原帧序，未镜像、重复图片、插值或移动整图。','', '| 支撑脚 | 帧号 | 相对位置 | 实图观察 |','|---|---|---|---|']
for leg,indices,phase,desc in pairs:lines.append(f'|{leg}|{indices[0]:02d}/{indices[1]:02d}|{phase}|{desc}|')
lines+=['','NE：背斜视，鞋尖向画面右上，近端为鞋跟。右支撑脚在画面右下、左支撑脚在画面左下；承重到蹬离的脚位沿跑向反方向变化。','SW：前斜视，鞋尖向画面左下。右支撑脚在画面左下、左支撑脚在画面右下；承重到蹬离的脚位逐渐回到画面右后方。','', 'NE已针对性修正10帧，保留6帧；SW修正13帧，保留3帧。全部新图逐图提示词、参考用途、SHA及宿主回执保留，实际型号/质量未确认。','', '当前完成单帧与联系图静态检查；整圈1×、慢放和首尾动态审查由root针对当前SHA继续，未声称客户端接入或用户验收。','', '[逐图SHA与来源](run_NE_SW_contactpairs_20261004.json)','[NE位置段图](run_NE_contactpairs_positions.png) · [SW位置段图](run_SW_contactpairs_positions.png)','[NE正常1200ms](run_NE_contactpairs_1200.webp) · [SW正常1200ms](run_SW_contactpairs_1200.webp)','[NE慢放4800ms](run_NE_contactpairs_4800.webp) · [SW慢放4800ms](run_SW_contactpairs_4800.webp)']
(OUT/'run_NE_SW_contactpairs_20261004.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'frames':len(frames),'uniqueNative':len(set(native_shas)),'issues':issue},ensure_ascii=False))
