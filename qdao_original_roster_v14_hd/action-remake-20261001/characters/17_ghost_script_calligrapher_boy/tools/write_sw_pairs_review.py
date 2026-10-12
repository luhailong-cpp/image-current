from pathlib import Path
from PIL import Image
import json,hashlib,datetime
b=Path(__file__).resolve().parents[1]
vs=[3,2,2,2,3,9,6,3,4,2,3,2,4,4,2,3]
observations=[
('左腿前下方支撑，前掌已压平，暗底收窄；右腿后屈回收。','右笔臂前摆、左卷臂后摆，握持与肩袖连续。'),
('左前靴宽底缘承重，膝较01压低；右后靴持续抬离。','右笔近竖、左卷收近，两个持物手可追踪。'),
('左靴从前伸收至腰下，膝踝自然弯，宽底支撑；右腿回收。','右笔与左卷开始收拢，未见换手或断腕。'),
('左支持腿从后位拉回身下；前方右膝抬起，右靴离地。','笔手向身侧下收，卷手仍在身侧，双臂独立。'),
('左腿向身体后方展开，后靴下缘宽，右膝前摆收起。','右筆手在前下方、左卷在侧后；完整单笔穗和卷穗。'),
('左后靴持续宽前掌支撑，右膝更弯；该帧后靴相对髋部后伸较07明显，后位递进不完全单调。','双手收在躯干前形成中间态，右笔左卷；v9恢复卷轴下太极挂穗。'),
('左后靴承重，右前摆靴较08更屈收且明显离地；以08为基底独立修改膝踝，未复制帧。','近左卷臂跨胸前摆、远右笔臂后摆，肩袖和握持连续；两墨灵在画幅内。'),
('左后靴持续承重，右前摆靴稍下降伸展，准备09换脚；未双脚腾空。','同07手臂相位，近左卷前、远右笔后；毛笔单穗完整。'),
('右靴前落宽底支撑，左腿后屈回收；保留原v4正确落地。','近左卷臂前、远右笔臂后，手与武器未交换。'),
('右前靴前掌压平，窄暗底缘落地；左后腿保持抬离。','与09连续的卷前笔后，未见额外手。'),
('右支持靴收至身下，膝下承重；左腿回收靴悬离。','笔臂向前侧收回、卷臂由前向侧后过渡；肩连接可追踪。'),
('右支持靴宽底承重位于身下偏前；左回收腿在后上方。','右笔前摆、左卷后摆，两个手与肩袖连接完整。'),
('右腿向后伸形成宽底支撑，左膝前抬；后靴轴仍跟随SW，无外翻。','右笔前、左卷后；v4修复右侧墨灵/挂穗实体裁边。'),
('右后靴宽前掌承重，左腿前摆屈膝；新图保持真实后腿展开。','为修裁边卷臂明显收回，双手未换；两墨灵及卷下挂穗完整。'),
('右后靴宽前掌支撑，左腿前伸摆靴显底但未当支撑；鞋轴沿行进方向。','右笔前左卷后，手臂与肩连接完整。'),
('右后靴持续宽前掌接触，左前摆靴再伸展准备01换脚；摆靴显底属摆腿。','右笔前左卷后，环回01手相位相近；卷穗与墨灵完整。')
]
edges=json.loads((b/'review/contact-pairs-SW/edge-candidates.json').read_text(encoding='utf-8-sig'))
frames=[]
for i,v in enumerate(vs,1):
 key=f'run-SW-{i:02d}-v{v}';p=b/'staging'/f'{key}.png';im=Image.open(p);r=json.loads(p.with_suffix('.png.generation.json').read_text(encoding='utf-8-sig'))
 a=im.getchannel('A');sides={'top':(0,0,1254,1),'bottom':(0,1253,1254,1254),'left':(0,0,1,1254),'right':(1253,0,1254,1254)}
 edge={s:sum(x>128 for x in a.crop(box).getdata()) for s,box in sides.items()}
 assert sum(edge.values())==0,(key,edge)
 frames.append({'n':i,'frame':i,'slot':f'run-SW-{i:02d}','file':f'staging/{key}.png','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativeSize':list(im.size),'mode':im.mode,'alphaExtrema':list(a.getextrema()),'supportFootObserved':'anatomical LEFT (near)' if i<=8 else 'anatomical RIGHT (far)','positionPair':(i-1)//2+1,'positionIntent':['front loading','under body','rear1','rear2'][(i-1)//2%4],'actualObservation':observations[i-1][0],'handConnection':observations[i-1][1],'footAxisObservation':'支撑靴长轴沿SW；未见踝部向外折或两靴向左右撇开。前摆靴的可见鞋底不作为支撑证据。','edgeOpaquePixels':edge,'maxEdgeAlpha':edges[i-1]['maxEdgeAlpha'],'status':'selected_pending_playback','approval':False,'generationRecord':f'staging/{key}.png.generation.json','request':r['evidence']['request'],'prompt':r['prompt'],'actualModel':r.get('actualModel'),'actualQuality':r.get('actualQuality')})
doc={'character':'17_ghost_script_calligrapher_boy','direction':'SW','reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'selected_pending_playback','available':16,'expected':16,'missing':[],'approved':0,'sequencePassed':False,'runTiming':{'cycleMs':1200,'frameMs':75,'frameCount':16,'pairMs':150,'uniform':True},'latestRequirement':'01-08同一左脚、09-16同一右脚连续支撑；每相对位置两张独立姿态。覆盖旧腾空和中间4/两侧2分配。','referenceAuthority':'按用户认可09竹弓少女的同向实际图参考膝踝/鞋轴；时间遵照用户最新16x75ms。','method':'逐张原生图、整画布240px联系表、四边alpha实测。未整图升降贴地、未改alpha、未镜像、未复制帧。所有生成均内置imagegen，工具未披露实际模型与质量。','explicitVersionList':vs,'frames':frames,'pairs':[{'frames':[j,j+1],'supportFoot':'LEFT' if j<=7 else 'RIGHT','position':['front','under body','rear1','rear2'][(j-1)//2%4],'actual':'实际观察见逐帧actualObservation；05-08及13-16都有后方宽支撑，但后位距离不是严格等增。'} for j in range(1,17,2)],'technical':{'allNative1254RGBA':True,'allDistinctSHA256':len({f['sha256'] for f in frames})==16,'allFourEdgesOpaquePixelsGT128Zero':True,'completeProvenance':True},'visualFindings':{'fixed':['01/02/10支撑鞋掌压平，03/04/11支持移入身下。','05-08、13-16原双脚腾空/后靴卷起改为同脚后方持续支撑。','06双手改为中间姿态并恢复卷轴太极穗。','07以08为基底独立屈收前摆膝踝，保持同一后靴支撑。','13/14实体裁边修复；最终16张最外圈alpha>128像素均0。'],'noObservedHardDefects':['选图未见第三手/第三脚、明显断腕、左右持物互换、实体被画布裁断。','支撑靴未见脚掌向左右外撇；自然前摆脚掌显底单独记录。'],'remainingPlaybackObservations':['06到07的笔手前后位移仍较大；06已插入中间臂态，但最终平顺程度由1200ms实播决定。','13到14卷臂为修边较明显向内收，需检查75ms下收回感。','05-08后靴始终支撑，但06的后伸量大于07，四个位置段的空间递进不严格等距。','部分新图头身较源图略大，240px静态无断肢/裂接，动态规模起伏由主预览复核。'],'notClaimed':'未声称用户已验收17；本代理未执行主预览实播。'},'rejectedThisPass':{'run-SW-06-v5':'工具网络发送失败，无图片；保存原始error并换新键单次重试。','run-SW-06-v6':'额外同角色参考干扰，双臂退回05姿态。','run-SW-06-v7':'多出第三只手，明确拒选。','run-SW-06-v8':'中间双臂可用但卷下挂穗丢失，v9已局部恢复。','run-SW-07-v3':'额外同角色参考干扰，手臂相位退回05。','run-SW-07-v4':'右边有11个alpha>128像素。','run-SW-07-v5':'虽实体边缘测试通过，但整体放大且墨灵向下跳位，选择与08更连续的07v6。','run-SW-13-v3':'右边26个alpha>128像素。','run-SW-14-v3':'右边33个alpha>128像素。'},'evidence':{'contactSheet240':'review/contact-pairs-SW/current-240.jpg','edgeMeasurements':'review/contact-pairs-SW/edge-candidates.json','requests':'provenance/run-SW-*.request.json','networkError':'provenance/run-SW-06-v5.error.txt'}}
for p in [b/'review-run-SW.json',b/'review/review-run-SW.json']:
 p.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
planp=b/'review/contact-pairs-S-SW-20261004.json';plan=json.loads(planp.read_text(encoding='utf-8-sig'));plan['stage']='S and SW explicit16 selections written; parent runtime playback/export next';plan['selectedReports']={'S':'review-run-S.json','SW':'review-run-SW.json'};plan['SWLatestVersions']=vs;plan['notes']='S交audit_current完成选片；SW本轮实图接地与持物修复已收敛。remaining具体动态观察见各report，不把提示词位置当验收。';planp.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selected':len(frames),'versions':vs,'allEdgesGT128Zero':True,'review':'review-run-SW.json'}))

