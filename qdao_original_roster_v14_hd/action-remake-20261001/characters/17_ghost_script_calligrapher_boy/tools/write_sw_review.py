from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
B=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy');R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl');versions=[1,1,1,1,2,4,2,2,4,1,2,2,2,2,1,2]
# These observations describe actual pixels, not requested phase labels.
obs={
1:('左腿前伸、右腿后收的接触候选','left','右笔臂前、左卷臂后，肩袖连接可追踪。','前靴显底且向SW，未见横向外撇；轻接触而非清楚平底承重。',['保留已有正确脚轴','01–03实际腿形接近，支撑转换需正常速度复核']),
2:('同侧前腿稍屈、后腿回收','left_candidate','右笔手仍较靠前，左卷手后侧，未换手。','前靴仍明显前伸显底；不能把原提示compression当作承重已通过。',['01–03支撑/通过差异不够清楚']),
3:('同侧前腿持续前伸，后腿抬起','left_candidate','右笔臂前、左卷臂后；握持连续。','靴轴随SW前进面，画面未明确兑现左支撑右通过，保持作为待审候选。',['03→04腿势转换较快']),
4:('右膝前屈，左脚低位支撑候选','left','右笔手退近髋，左卷手前移；物件归属保留。','画面右后的左靴低且接近平底，右前靴抬起；比旧03支撑层次更明显。',['与03的相位与体态变化需整段播放']),
5:('右前膝屈、左后腿延伸的推离候选','left_toe_candidate','右笔手后、左卷手向前，肩肘可辨。','两个靴轴沿SW；后腿延伸可辨，但不能只凭后靴最低点认定前掌蹬离。',['05→06卷臂由右侧前持转跨胸，变化较快']),
6:('右膝更屈收的短腾空候选','none','左袖跨胸持卷，右臂经后侧持笔，笔头/唯一尾端流苏完整。','v4两腿两靴；右前靴较07更收，后左靴仍离地，不再采用三靴或早伸腿旧稿。',['06–09上半身接近，持物臂短时保持需完整播放']),
7:('右膝开始伸开、双脚仍离地','none','与08正确跨胸卷臂/后摆笔臂保持一致。','前靴比06略下降，进入08临接触，长轴沿SW。',['06→07差异偏小、07→08较大，节奏需1200ms实播']),
8:('右前脚临落地、左脚后收','none_precontact','保持09同一左卷臂跨胸、右笔臂后摆，未换手。','前靴比09高且膝更屈，靴轴沿SW；弃用上半身错误回到笔手前摆的v1。',['整段接触与腾空仍待动态验收']),
9:('右腿前脚近乎平底接触','right','左卷臂从远肩跨胸，右笔臂后摆，完整笔头恢复；弃用手臂交换的v2。','v4前靴接触轮廓更平，膝踝自然屈，前进轴朝SW；原v3只是贴近边缘，边缘检测未证明裁断。',['墨灵仍在后侧，与前摆卷轴空间关系变化较大']),
10:('右腿压缩承重候选，左脚后抬','right','跨胸卷臂/后摆笔臂与09衔接，未换手。','前靴平底、膝屈可辨，后脚抬起，支撑比11明确。',['墨灵轮廓靠右边但无高alpha触边']),
11:('右腿仍前伸、左脚后收，过渡候选','right_ambiguous','右笔手开始前移，左卷手回撤；v2补回卷轴下杆阴阳流苏。','实际前靴显底且偏前伸，没有明确兑现提示中的通过支撑；脚轴仍沿SW，不是外撇。',['10→11→12承重/通过连贯性是明确待审点','两墨灵分处身体两边，空间连续性待审']),
12:('右腿低位平底支撑，左腿回收','right','右笔臂前、左卷臂后，肩袖正确，挂饰完整。','右靴平底支撑清楚，左脚抬离；v2下墨灵移近卷轴后高alpha触边已消除。',['与11实际腿势需连贯复核']),
13:('左前膝屈、右后腿延伸的推离/腾空边界候选','right_toe_ambiguous','右笔臂前、左卷臂后，物件归属保留。','有屈膝与后腿伸展；后靴无强烈承重读感，不能直接称前掌蹬地通过。',['13→14更像从推离边界进入短腾空，需动态判断']),
14:('双膝回收的短腾空候选','none','右笔臂前、左卷臂后，完整两墨灵；v2恢复闭口。','两靴均抬起，脚轴随SW，非向两侧外撇。',['14→15伸腿幅度较大']),
15:('左腿前伸下降、右脚后收','none_or_precontact','右笔臂前、左卷臂后，连接与16/01同侧。','前靴显底且沿SW前进，后靴抬起；没有按最低点贴地。',['15→16→01接触过渡需1200ms循环检查']),
16:('左脚临接触，右腿后收','none_precontact','右笔前、左卷后，与01持物侧别一致。','靴轴沿SW，v2修复下墨灵触边；靴底仍有前伸，接触类型留给整段判断。',['16→01衔接尚未动态通过'])}
frames=[];errors=[];allrows=[]
for n,v in enumerate(versions,1):
 file=f'staging/run-SW-{n:02d}-v{v}.png';p=B/file;sha=hashlib.sha256(p.read_bytes()).hexdigest();im=Image.open(p);rec=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8'))
 if im.size!=(1254,1254) or im.mode!='RGBA' or rec.get('sha256')!=sha:errors.append(file)
 a=im.getchannel('A');w,h=im.size;edges={name:sum(q>128 for q in a.crop(box).getdata()) for name,box in [('left',(0,0,1,h)),('right',(w-1,0,w,h)),('top',(0,0,w,1)),('bottom',(0,h-1,w,h))]}
 phase,support,hand,foot,issues=obs[n]
 req=B/'provenance'/f'run-SW-{n:02d}-v{v}.request.json';request=json.loads(req.read_text(encoding='utf-8'))
 refs=[{'file':x,'sha256':hashlib.sha256(Path(x).read_bytes()).hexdigest()} for x in request['referenced_image_paths'] if '09_bamboo_archer_girl/runtime/run/SW' in x]
 frames.append({'frame':n,'file':file,'sha256':sha,'nativeSize':list(im.size),'observedPhase':phase,'supportCandidate':support,'handConnection':hand,'footAxisObservation':foot,'issues':issues+['透明边缘仍有少量彩边，整体未通过'],'status':'needs_review','approval':False,'dynamicApproval':False,'edgeOpaquePixels':edges,'reference09':refs,'generationRecord':str(p.with_name(p.name+'.generation.json').relative_to(B))})
for p in sorted((B/'staging').glob('run-SW-*.png')):
 im=Image.open(p);sha=hashlib.sha256(p.read_bytes()).hexdigest();recpath=p.with_name(p.name+'.generation.json');rec=json.loads(recpath.read_text(encoding='utf-8'))
 allrows.append({'file':str(p.relative_to(B)),'sha256':sha,'nativeSize':list(im.size),'mode':im.mode,'recordMatches':rec.get('sha256')==sha})
 if im.size!=(1254,1254) or im.mode!='RGBA' or rec.get('sha256')!=sha:errors.append(str(p))
review={'reviewedAt':datetime.now(timezone.utc).isoformat(),'direction':'SW','available':16,'expected':16,'missing':[],'candidateCount':len(allrows),'approved':0,'fullLoopDynamicReview':'pending_no_available_browser','timing':{'adoptedCycleMs':1200,'frameMs':75,'frameCount':16,'phaseWeightsApplied':False},'referenceAuthority':'最新用户认可09竹弓少女当前版；读取其SW实际16图并作姿态参考，节奏按最新1200ms覆盖09旧720ms。','method':'逐张实际查看生成结果及固定整画布240px选图，不将提示相位当事实；脚轴、膝踝、持物肩连接、接地和边缘分别检查。未进行整图贴地、独立包围盒缩放、镜像、复制插帧。','candidateSupportFrames':[4,9,10,12],'remainingPriorityReview':[2,3,5,11,13,14],'frames':frames,'validation':{'selectedCount':len(frames),'uniqueSelectedSha256':len(set(x['sha256'] for x in frames)),'allRecordsMatch':not errors,'errors':errors,'selectedOpaqueEdgeClear':all(not any(f['edgeOpaquePixels'].values()) for f in frames)},'allCandidateEvidence':allrows,'notSelectedCandidates':{'run-SW-05-v1.png':'未按实际姿态形成屈膝换步，过度沿袭源图前伸腿。','run-SW-09-v1.png':'后侧毛笔误为两端流苏杆，后续局部修复。','run-SW-09-v2.png':'卷/笔臂肩连接互换，不选。','run-SW-09-v3.png':'上半身连接已修，但前靴接触轮廓较弱；v4更适合落地。','run-SW-13-v1.png':'仍为前腿直伸姿态，未体现13屈膝转换。','run-SW-06-v1.png':'出现第三只靴和笔头端流苏。','run-SW-06-v2.png':'第三靴已去除，但流苏仍接笔头端。','run-SW-06-v3.png':'流苏已纠正，但与08形成先伸后屈；v4按同一上半身建立较高屈收。','run-SW-07-v1.png':'前靴过早伸到低处，接08反向屈回；选v2。','run-SW-08-v1.png':'上半身回到笔臂前摆，破坏09相邻持物臂关系。','run-SW-11-v1.png':'卷轴下杆挂饰缺失；v2恢复。','run-SW-12-v1.png':'下墨灵有21个高alpha像素触右边；v2修复。','run-SW-14-v1.png':'闭口设定漂为张嘴；v2恢复。','run-SW-16-v1.png':'下墨灵有7个高alpha像素触右边；v2修复。'},'quotaOrGenerationErrors':[],'technicalCompletionDoesNotImplyVisualPass':True}
(B/'review/review-run-SW.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidateCount':len(allrows),'selected':16,'uniqueSelected':review['validation']['uniqueSelectedSha256'],'errors':errors,'selectedOpaqueEdgeClear':review['validation']['selectedOpaqueEdgeClear']}))

