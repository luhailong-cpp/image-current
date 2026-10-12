import json,hashlib,datetime
from pathlib import Path
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
before={(x['direction'],x['frame']):x['sha256'] for x in load(R/'reviews/full-limb-N-W-before-20261005.json')}
changed={1,2,3,4,9,10}
n_hands={
1:'左肩—屈肘—袖口至左腕藏于铃/头侧的遮挡关系合理；右肩袖口至持扇右腕单链可追，无多腕。',
2:'延续01左铃前摆靠头侧、右扇后摆，袖口与持握位置对应，无断手或道具换手。',
3:'左腕与铃柄连接可见，右袖口至右扇单腕连接；双肘自然屈曲，摆臂过渡可读。',
4:'左铃柄被左手握住，右手从右袖口持扇；肩肘腕连接和03相邻可读。',
5:'左手握铃后摆、右手持扇前摆，两侧肩袖方向与手腕对应；铃柄局部被握手遮挡合理。',
6:'两条肩—袖—腕链与05连续，右扇左铃保持，无游离手或附加腕。',
7:'左铃和右扇延续摆臂末段，两手各接一个袖口，遮挡未造成断链。',
8:'与07相邻，左铃柄由左手持握、右袖口接右扇手，前后遮挡关系可读。',
9:'左肩袖口至后伸左腕和铃环连续；远侧右袖口接扇手，躯干遮挡合理。',
10:'与09同摆臂段，左腕绕握铃环、右手持扇，无断腕、双腕或道具换手。',
11:'左手随铃回收、右扇手向侧后变化，肩肘腕层次合理。',
12:'延续11的肩—肘—腕线，左铃单握和右扇单握清楚。',
13:'左腕至铃环、右腕至扇柄均可追溯到对应肩部，肘部自然弯曲。',
14:'与13相邻，手腕遮挡和袖口方向连贯，右扇左铃身份未变。',
15:'左铃向后摆与右扇前后变化可读，左右手各一条连接链。',
16:'与15相邻，双腕单链、道具持手保持；循环回01为正常摆臂回收。'
}
w_hands={
1:'近侧左臂前摆持铃，远侧右臂后摆持扇；两条肩肘腕连接可追，无多腕。',
2:'与01相邻，左腕握铃柄、远侧右腕接扇柄，无断手。',
3:'左铃臂回到腰侧中位，远侧右扇臂向前；与02为跨中位摆动，未互换持手。',
4:'与03同位置段，双肘弯曲、两袖口各接一腕，右扇左铃正确。',
5:'近侧左铃臂后摆，远侧右扇臂前摆，肩袖、肘和腕在同一链条上。',
6:'延续05的对侧摆臂，腕与铃柄/扇柄连接清楚。',
7:'左铃臂后摆末段仍接近侧肩，右扇从远侧肩前摆，无双腕。',
8:'与07相邻，左肩至持铃腕单链，右袖口至持扇腕单链连续。',
9:'左铃臂回收至髋侧，右扇臂维持前摆，两手连接合理。',
10:'与09连续，近侧左袖口到铃腕和远侧右袖口到扇腕可追。',
11:'左铃臂向前、右扇臂向后，10至11为经过中位换向，右扇左铃未换手。',
12:'与11同摆臂段，两侧肩肘腕连接清楚，无断手或附加腕。',
13:'左铃前摆、右扇后摆延续，两袖口到各自持物腕连续。',
14:'与13相邻，双肘保持自然弯曲，握铃和持扇结构正确。',
15:'左铃前摆末段、右扇后摆，两条手臂链可追，没有袖口脱腕。',
16:'延续15，右扇左铃单持握、肩肘腕层次合理；与01循环同一持物身份。'
}
frames=[]
for d in ['N','W']:
 for f in range(1,17):
  p=R/f'frames/run/{d}/{f:02}.png';h=sha(p);side=load(p.with_suffix('.png.generation.json'));im=Image.open(p)
  assert side['sha256']==h
  assert im.size==(1024,1024) and im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
  repl=d=='N' and f in changed
  assert (h!=before[d,f])==repl
  arm=(n_hands if d=='N' else w_hands)[f]
  support='RIGHT' if f<=8 else 'LEFT'
  segment=((f-1)%8)//2+1
  if repl:
   leg=('将'+('右' if f<=4 else '左')+'支撑鞋原来朝外侧探出的鞋头收回北向，现呈后跟正视、鞋头向远方；髋—膝—踝—鞋头保持前进平面。保留原承重点、膝弯、自然换重心与另一腿后屈，不锁膝、不横叉。')
   rec=load(R/side['generationRecord']);native=R/rec['native']['file']
   assert sha(native)==rec['native']['sha256']
   assert rec['actualModel'] is None and rec['actualQuality'] is None
   assert ImageChops.difference(Image.open(native).resize((1024,1024),Image.Resampling.LANCZOS),im).getbbox() is None
  elif d=='N':
   leg=('北向'+('右' if f<=8 else '左')+'腿支撑，髋膝踝沿前后运动平面，后跟朝镜头、鞋头向北；另一腿露鞋底是正常后屈。保留弯膝和第'+str(segment)+'个两帧承重位置段，未见横叉或鞋头横撇。')
  else:
   leg=('西向'+('右' if f<=8 else '左')+'腿支撑，髋膝踝与鞋头沿西向前后运动平面；支撑鞋侧面透视及抬脚自然屈膝合理。上轮抬脚鞋轴修正仍成立，保留第'+str(segment)+'个两帧承重位置段，无锁膝、双腿横叉或新外翻。')
  frames.append(dict(action='run',direction=d,frame=f,path=p.relative_to(R).as_posix(),sha256=h,decision='replaced' if repl else 'retained',reason='手链：'+arm+' 脚链：'+leg,handChainObservation=arm,legChainObservation=leg,previousSha256=before[d,f],generationRecord=side['generationRecord'],supportFoot=support,supportPositionSegment=segment,frameDurationMs=75))
contact=[f'reviews/full-limb-{d}-contact-20261005.jpg' for d in ['N','W']]
report={'reviewId':'full-limb-N-W-20261004','reviewedAt':now,'actualReviewDate':'2026-10-05','reviewer':'finish_north','scope':'按2026-10-05最新要求重新逐帧检查N/W全部手链与髋膝踝鞋头轴，非引用旧脚轴报告代替本次手部复核。','frames':frames,'knownUnresolvedArtFailures':[],
'summary':{'frames':32,'replaced':6,'retained':26,'replacedSlots':['run/N/'+f'{f:02}' for f in sorted(changed)],'hands':'32帧右扇左铃单链连接，未发现断手、双腕、持物换手硬错误。','legs':'6帧北向支撑鞋外探收正；正常屈膝、换重心和蹬地保留。'},
'gait':{'framesPerDirection':16,'frameDurationMs':75,'cycleDurationMs':1200,'support':'RIGHT01-08; LEFT09-16','segments':'每只支撑脚4个位置段，每段2独立姿态'},
'contactSheets':[{'path':p,'sha256':sha(R/p),'operation':'每帧完整1024画布统一等比512，4x4排列；无bbox缩放、裁切或逐帧位移。'} for p in contact],
'evidence':{'armDetails':[f'reviews/full-limb-{d}-arms-{s}-20261005.jpg' for d in ['N','W'] for s in ['01-08','09-16']],'actualViewed':'32帧手臂区域逐帧放大；32帧完整画布联系表；6新图原生返回全图和正式导入后序列复核。','identityRef':'D:/work/image/q_daoist_character_pack_4096/02_fire_talisman_boy_transparent_4096.png','styleRef':'D:/work/image/designs/jubaozhai-ui/02-characters.png','referenceUse':'实际查看且每张生成均传入身份、风格和N08正后跟参考。','limits':'静态与相邻序列审图；最终正常/慢速播放由root统一验收，未声明本机客户端已接入。'},
'checks':{'formalShaSidecar':32,'formal1024RgbaTransparent':32,'newNativeShaAndUniformResizePixels':6,'newNativeSize':[1254,1254]},
'modelEvidence':{'configuredTargetModel':'gpt-image-2.5-sunburst','configuredTargetQuality':'max','route':'builtin image_gen','submittedModel':None,'submittedQuality':None,'actualReturnedModel':None,'actualReturnedQuality':None,'confirmation':'未确认：宿主管理入口无型号/质量选择器，返回未披露；逐图request/receipt/record保存真实证据。'}}
out=R/'reviews/full-limb-N-W-20261004.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
ip=R/'inventory-run-north.json';iv=load(ip); rows={(x['direction'],x['frame']):x for x in frames}
for x in iv['frames']:
 key=(x.get('direction'),x.get('frame'))
 if key in rows:
  q=rows[key];assert x['sha256']==q['sha256']
  x['visual_status']='full_limb_static_review_pass_pending_root_dynamic_review'
  x['full_limb_review']={'report':out.relative_to(R).as_posix(),'reviewedAt':now,'decision':q['decision'],'reason':q['reason']}
ip.write_text(json.dumps(iv,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(out),'frames':32,'replaced':6,'retained':26,'shaChecks':32,'newNativeExactChecks':6,'knownUnresolvedArtFailures':[]},ensure_ascii=False))

