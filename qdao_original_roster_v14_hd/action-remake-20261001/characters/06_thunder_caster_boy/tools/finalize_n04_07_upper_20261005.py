"""Finalize owned N04-07 evidence and independently refresh reviewed W transitions."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
selected={4:'run_N_04_armswing_v3',5:'run_N_05_armswing_v3',6:'run_N_06_armswing_v2',7:'run_N_07_armswing_v1'}
old={4:'ac55dc03d65858e09a33e80278af162467b3a06d24e617106af6bf7c01cc5931',5:'2dcda381d9511b571dd6fe4dc6ea4a55083a4eadeb9a059408416560ea1c1286',6:'0699078f08ce4b9dbef3e5a34d03abcdc88eb42b4515ac69451d4f8ba6939191',7:'b70c247ea27c6e1b26b392d015f3d75df5b8d7649a784dc4d1007ad69c67b747'}
observations={
4:['右肩至肘收近躯干，前臂屈肘向N远摆；右拳高于左拳，保持握杖。','左肩后摆，袖口扩大呈近侧透视，低腕伸至腰旁；牌直接握下沿，上左伸出手掌，未附加柄。','04→05左腕继续后下摆，右肘稍收紧，非固定双手。'],
5:['右肩屈肘前摆较04稍收紧，杖随拳更竖，握点未漂移。','左袖与前臂向近侧后下方伸展，手仍低于肘，牌向上左、握下沿，腕无倒折。','05→06左臂到摆动端点，随后07开始回收，保持同一手持物。'],
6:['右臂朝远处前收，肘屈，杖的部分形体被头发遮住，清楚区别后摆姿态。','左肩后摆，肘略伸，握牌手位于身侧向近端伸；牌直接握下沿并上左伸，不悬在拳下。','06→07左肘回收、右拳轻降，是同向端点附近连续变化。'],
7:['右前臂前收远摆并轻降，杖仍由解剖右手握持，肩肘过渡成立。','左臂保持近侧后摆并轻回收，腕与袖口顺接，牌上伸且直接握底边。','07端点轻回收可衔接08；08属于其他代理，此报告不代签整个N循环。']}
frames=[]
for f,stem in selected.items():
 p=R/f'runtime/run/N/{f:02d}.png';n=R/f'work/{stem}.png'
 im=Image.open(p);ni=Image.open(n)
 assert im.size==(1024,1024) and ni.size==(1254,1254) and im.mode==ni.mode=='RGBA'
 exact=im.tobytes()==ni.resize((1024,1024),Image.Resampling.LANCZOS).tobytes()
 assert exact
 gen=read(p.with_name(p.name+'.generation.json'))
 assert gen['sha256']==sha(p) and gen['derivedFrom'][0]['sha256']==sha(n)
 o=observations[f]
 frames.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'currentSHA':sha(p),'previousRuntimeSha256':old[f],'frame':f,'direction':'N','native':{'file':n.relative_to(R).as_posix(),'sha256':sha(n),'width':1254,'height':1254},'generationRecord':p.relative_to(R).as_posix()+'.generation.json','status':'accepted-frozen-local-review','rightArm':o[0],'leftArm':o[1],'adjacentObservation':o[2],'invariants':'实际看原生/运行帧和左右同画布对照，头身、发型比例、相机、骨盆与原全腿鞋位置及相位保留；不是bbox裁切或程序造姿态。','comparison':f'review/{stem}_compare.jpg','technicalCheck':{'exactWholeCanvasLanczos1254To1024':exact,'rgba':True,'alphaExtrema':im.getchannel('A').getextrema()},'actualModel':None,'actualQuality':None})
assert len({x['native']['sha256'] for x in frames})==4 and len({x['sha256'] for x in frames})==4
audit={'schemaVersion':1,'reviewedAt':now,'reviewer':'/root/finish_s','scope':'独占 run/N/04–07 上肢修正；不代签整个N循环。','timing':{'frameMs':60,'framesPerCycle':16,'cycleMs':960,'source':'2026-10-05最新用户明确覆盖旧75ms规格'},'method':['实际查看每帧原生目标、runtime，身份画像、N idle和已确认风格图。','通过内置imagegen独立编辑每个姿态，再实际看完整画布旧新并列对照。','核验4张独立1254透明原生以及1024整幅统一导出，关联逐图来源。'],'holdingInvariant':'解剖右手雷杖，左手符牌直接握下沿且牌身向上或左上，无多余手柄。','modelEvidence':{'configTargetModel':'gpt-image-2.5-sunburst','configTargetQuality':'max','route':'builtin image_gen','submittedModel':None,'submittedQuality':None,'returnedModel':None,'returnedQuality':None,'status':'宿主无型号/质量选择器，返回未披露，实际未确认'},'frames':frames,'rejectedCandidates':[{'stem':'run_N_04_armswing_v2','reason':'人物放大下移，未采用'},{'stem':'run_N_05_armswing_v2','reason':'左手抬高失去低位后摆，未采用'},{'stem':'run_N_06_armswing_v1','reason':'人物放大且符牌朝下，未采用'}],'supersededCandidates':[{'stem':'run_N_04_armswing_v1','reason':'低手位成立但牌朝下，v3仅修握牌方向'},{'stem':'run_N_05_armswing_v1','reason':'低手位成立但牌朝下，v3仅修握牌方向'}],'mutations':'仅N04–07 PNG及其专属逐图记录；未改其它N槽、共享Git、主状态或全局预览。','integration':'本机无客户端，本次只素材与证据，不声明已游戏接入。'}
write(R/'review/run_N_04_07_armswing_20261005.json',audit)
for item in audit['rejectedCandidates']+audit['supersededCandidates']:
 p=R/f"work/{item['stem']}.png.generation.json"
 j=read(p);j['exported']=False;j['selectionStatus']='rejected' if item in audit['rejectedCandidates'] else 'superseded';j['selectionReason']=item['reason'];write(p,j)
# Amend only reviewed frame evidence; keep historical diagnostic snapshots explicit.
p=R/'review/upper_limb_run_S_SE_SW_W_20261005.json';d=read(p)
expected={2:'475b211cad48891c15b9ec3c2473c9d2fbf8bcc1e9da3af603e530188bea65ee',9:'0641ba712250e3597c54e15995720bc46b3f400c0a01b3fb40b039b020744370'}
for f,h in expected.items():assert sha(R/f'runtime/run/W/{f:02d}.png')==h
d['lastIndependentRefreshAt']=now
d['timingUntouched']={'frameMs':60,'cycleMs':960,'pairMs':120,'note':'最新用户覆盖75ms；根窗口负责预览/manifest，本代理未改动画文件。'}
d['method'].append('追加实际查看修后W01/02/03、08/09/10六张完整runtime；顺序比较肩肘腕与持物前后位置，按新SHA独立复核。')
d['parentWUpdatesPending']=False
d['summary']['confirmedIssues']=['SE02/03左臂跨躯干跳变已局部修正，父窗口负责全圈验收','W02/W09已由父窗口修正并经本代理按01→03与08→10完整图独立复核']
d['summary']['wholeLegWatch']=[]
d['summary']['wholeLegRetainedAfterIndependentParentReview']=['SE06/07：三分之四透视，髋→膝→踝→鞋头向右下，无确证外翻；保留']
wFinding=next(x for x in d['findings'] if x['id']=='W-two-transition-jumps')
wFinding['status']='resolved-by-parent-independent-local-review'
wFinding['detail']='旧W02→03、09→10肩肘交换集中；新02左牌由前位收至腰侧，右杖臂由后伸收至身侧，成为01与03之间的中间姿态。新09右拳由前伸回胸侧、左牌从后位回到胸腹旁，形成08与10之间反向过渡。握持不换手，腕与前臂顺接。'
wFinding['suggestion']='保留新02/09。其它端点多帧停留是节奏观察项，本次局部静态与顺序复核不等于代签整个动态循环。'
wFinding['resolvedBy']=[{'file':f'runtime/run/W/{f:02d}.png','sha256':h,'reviewedAt':now} for f,h in expected.items()]
for e in wFinding['evidence']:
 if e['frame'] in expected:e['sha256']=expected[e['frame']]
axis=next(x for x in d['findings'] if x['id']=='SE06-07-strict-whole-leg-watch')
axis['status']='retained-after-parent-independent-whole-leg-review'
axis['detail']='本代理整腿复看未确证独立外折；父窗口另实际对照06/07原生、runtime及09角色同向06/07，确认髋→膝→踝和踝→鞋头均向右下推进。鞋底边近水平与鞋正面可见属于三分之四透视，不能要求鞋底边沿屏幕45度。'
axis['suggestion']='解除watch硬阻断并保留当前帧；不为了统一2D鞋底边角强行重画。'
axis['resolvedBy']=[{'file':e['file'],'sha256':e['sha256'],'method':'父窗口独立完整图及09同向比较；本代理整腿原尺寸观察'} for e in axis['evidence'][:2]]
for x in d['frames']:
 if x['direction']=='W' and x['frame'] in expected:
  f=x['frame'];x['previousReviewSha256']=x['sha256'];x['sha256']=expected[f]
  x['rightArm']='右杖臂从后伸收至肋侧，肘屈且握杆点连续，作为向前摆的中间位。' if f==2 else '右杖臂由前伸收至胸侧，肘屈自然，为后摆准备。'
  x['leftArm']='左牌臂由前位回到腰侧，肩肘与袖口顺接，牌未换手。' if f==2 else '左牌臂从后位向腹侧回收，腕与袖口自然衔接、直接握牌。'
  x['adjacentPoseObservation']='实际顺看01→02→03，两臂经身侧中间位再交换，不再只跳两个端点。' if f==2 else '实际顺看08→09→10，前伸/后伸的两臂先回身侧，再继续反向摆动。'
  x['upperLimbStatus']='parent-corrected-independently-reviewed'
  x['suggestion']='保留当前帧；端点长停留及全圈动态由主窗口复核，不冒称此处已播放整圈。'
  x['evidence']['historicalDiagnosticsNote']='本字段旧裁切与顺序板属于auditedSnapshotSha256；当前复核直接看完整runtime。'
  x['evidence']['currentActuallyViewed']=[f'runtime/run/W/{j:02d}.png' for j in ([1,2,3] if f==2 else [8,9,10])]
  x['resolvedBy']={'file':x['file'],'sha256':x['sha256'],'independentReviewedAt':now}
 if x['direction']=='SE' and x['frame'] in [6,7]:
  x['wholeLegAxisObservation']='髋→大腿→膝→踝与踝→鞋头朝右下推进；鞋底边较水平但鞋正面可见，三分之四透视成立，未确证独立外翻。父窗口对比09同向帧独立复核同意保留。'
  x['wholeLegAxisStatus']='retain-no-confirmed-separate-twist'
  x['suggestion']='保留当前帧，解除严格轴线watch硬阻断；不能要求鞋底边沿屏幕45度。'
write(p,d)
print(json.dumps({'Nframes':[{'file':x['file'],'sha256':x['sha256']} for x in frames],'WRefresh':'resolved locally; global animation remains parent responsibility','audit':'review/run_N_04_07_armswing_20261005.json'},ensure_ascii=False))

