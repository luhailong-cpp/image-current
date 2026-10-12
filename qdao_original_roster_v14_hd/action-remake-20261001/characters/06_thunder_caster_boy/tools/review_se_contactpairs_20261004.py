"""Review and preview SE latest two-frame position segments, no runtime mutation."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]; O=R/'review'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pairs=[
('右脚',[14,15],'前端初落地','前伸鞋跟及前掌均放平；另一腿弯曲摆动'),
('右脚',[0,1],'前侧承重','鞋在前侧承重，膝微弯，足位较初接收近身体'),
('右脚',[2,3],'身体经过','髋部经过支撑脚，支撑腿向身后发展，另一膝前摆'),
('右脚',[4,5],'后侧蹬离','原蜷后腿重画成后侧支撑，前掌接触，左腿前摆明确离地'),
('左脚',[6,7],'前端初落地','06/07前伸平掌与支撑点保留；末轮局部收头匹配08/09体量，消除07头肩尺度跳变'),
('左脚',[8,9],'前侧承重','保持低身承重，踝鞋局部后收，平掌承受重量'),
('左脚',[10,11],'身体经过','足位回到髋下，11纠正原右脚支撑/左脚悬空错误'),
('左脚',[12,13],'后侧蹬离','前景左腿实际后收至身后、鞋跟渐升，另一腿保持离地')]
changed=[4,5,6,7,8,9,10,11,12,13,14,15];rows=[];imgs=[];issues=[];srcshas=[]
for n in range(16):
 p=R/'runtime/run/SE'/f'{n:02d}.png';g=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8-sig'));im=Image.open(p).convert('RGBA');imgs.append(im)
 src=R/g['derivedFrom'][0]['file'];native=Image.open(src).convert('RGBA');srcshas.append(sha(src))
 if im.size!=(1024,1024) or im.getchannel('A').getextrema()[0]!=0:issues.append(f'{n:02d}: runtime size or alpha')
 if sha(p)!=g['sha256'] or sha(src)!=g['derivedFrom'][0]['sha256']:issues.append(f'{n:02d}: SHA mismatch')
 if native.size!=(1254,1254) or native.resize((1024,1024),Image.Resampling.LANCZOS).tobytes()!=im.tobytes():issues.append(f'{n:02d}: native/full-canvas mismatch')
 leg,ns,phase,desc=next(x for x in pairs if n in x[1])
 rows.append({'frame':n,'file':p.relative_to(R).as_posix(),'sha256':sha(p),'nativeSource':g['derivedFrom'][0],'generationRecord':p.relative_to(R).as_posix()+'.generation.json','supportLeg':leg,'pairFrames':ns,'positionPhase':phase,'observation':g.get('visualReview'),'changedThisRound':n in changed,'actualModel':None,'actualQuality':None})
if len(set(srcshas))!=16:issues.append('duplicate native sources')
sources=[{'file':x['file'],'sha256':x['sha256'],'generationRecord':x['generationRecord']} for x in rows]
def record(p,op,**more):p.with_name(p.name+'.generation.json').write_text(json.dumps({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'derivedFrom':sources,'operation':op,'actualModel':None,'actualQuality':None,**more},ensure_ascii=False,indent=2),encoding='utf-8')
for ms in (75,300):
 ims=[i.resize((512,512),Image.Resampling.LANCZOS) for i in imgs];p=O/f'run_SE_contactpairs_{16*ms}.webp';ims[0].save(p,save_all=True,append_images=ims[1:],duration=ms,loop=0,lossless=True,method=4)
 record(p,'Full canvas512 preview;16 unique poses; no interpolation/translation/alignment',frameMs=ms,cycleMs=16*ms)
board=Image.new('RGB',(1024,1240),(229,232,229));draw=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
for k,(leg,ns,phase,desc) in enumerate(pairs):
 x=(k%4)*256;y=(k//4)*620;draw.text((x+5,y+5),f'SE {leg} {phase}',font=font,fill=(25,48,44))
 for j,n in enumerate(ns):
  im=imgs[n].resize((256,256),Image.Resampling.LANCZOS);board.paste(im,(x,y+30+j*290),im);draw.text((x+5,y+288+j*290),f'{n:02d} · 75ms',font=font,fill=(25,48,44))
p=O/'run_SE_contactpairs_positions.png';board.save(p);record(p,'Full canvas256 pose thumbnails grouped into two-frame relative support-position segments')
report={'scope':'run/SE only','reviewedAt':datetime.now(timezone.utc).isoformat(),'latestHumanRequirement':'直脚着地两帧，再旁边点两帧，再旁边点两帧，再旁边点俩帧，依次类推','timing':{'frameMs':75,'pairMs':150,'cycleMs':1200},'pairMap':[{'supportLeg':leg,'frames':ns,'position':phase,'observation':desc} for leg,ns,phase,desc in pairs],'changedFrames':changed,'retainedFrames':[n for n in range(16) if n not in changed],'travel':'画面右下SE；脚位沿跑向前端到髋下再到后侧，不以外撇代替位置变化','reference':'实际查看09_bamboo_archer_girl runtime/run/SE/02.png和10.png，只取同向脚轴/接地；保留06身份及持物','reviewMethod':['实际逐张查看16帧，包括全部新原生输出','完整联系图静态检查','1254原生→1024全画布Lanczos、透明、SHA、16原生来源互异检查'],'technicalIssues':issues,'staticIndividualFrameReviewCompleted':True,'wholeCycleVisualApproved':False,'clientIntegrated':False,'modelNote':'内置宿主管理入口；目标GPT Image2.5Sunburst/max；实际model/quality参数及返回未披露，null未确认','frames':rows}
report['cameraCorrectionFrames']=[6,7]
report['resolvedIndependentFindings']=[{'id':'SE07-08-scale-watch','resolution':'06/07内置AI局部收头，第二稿同画幅对照08/09已消除原膨大；腿脚支撑点保留，静态通过，整圈待主窗口复核','resolvedBy':[{'file':x['file'],'sha256':x['sha256'],'nativeSource':x['nativeSource']} for x in rows if x['frame'] in (6,7)]}]
(O/'run_SE_contactpairs_20261004.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# SE 两帧位置段修正记录','','16帧×75ms=1200ms，每位置段两张独立姿态150ms。右脚14–05、左脚06–13持续承重推进。','','|支撑脚|帧号|相对位置|实际处理|','|---|---|---|---|']
for leg,ns,phase,desc in pairs:lines.append(f'|{leg}|{ns[0]:02d}/{ns[1]:02d}|{phase}|{desc}|')
lines+=['','本轮修正12帧：04、05、06、07、08、09、10、11、12、13、14、15。保留00、01、02、03四帧。06/07末轮局部收头消除相邻头肩体量跳变，保留初接脚位。所有改动为内置AI独立局部绘图，没有复制、镜像、插值、全图位移或按最低像素贴地。','', '逐图来源和SHA检查0项问题不等于整圈美术通过。已逐图与联系图检查；1×、慢放和首尾动态验收交由root针对当前SHA继续，尚未接入客户端。','', '[逐图SHA/来源](run_SE_contactpairs_20261004.json) · [位置段图](run_SE_contactpairs_positions.png)','[正常1200ms](run_SE_contactpairs_1200.webp) · [慢放4800ms](run_SE_contactpairs_4800.webp)']
(O/'run_SE_contactpairs_20261004.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'frames':16,'uniqueNative':len(set(srcshas)),'issues':issues},ensure_ascii=False))
