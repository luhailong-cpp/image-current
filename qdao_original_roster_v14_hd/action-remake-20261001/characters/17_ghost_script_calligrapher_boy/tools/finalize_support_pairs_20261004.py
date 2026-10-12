"""Finalize explicit N/NW candidates, provenance checks and visual QA. Does not edit PNG pixels."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
b=Path(__file__).resolve().parents[1]
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
versions={'N':[3,1,2,4,5,4,3,5,3,2,1,3,4,2,3,5],'NW':[3,4,1,2,7,3,5,5,5,1,1,2,3,2,3,2]}
notes={
'N':[
'右腿长且后跟/窄底缘低，左膝屈曲、鞋底高；替代v2大片支撑露底。',
'右腿继续较低，缓冲姿态；支撑鞋有少量底面。左卷/右笔仍分别连接正确手臂。',
'右膝屈曲承重，左脚折起；脚轴保持N。手臂前后幅度弱于腿部变化。',
'右支撑延续03，支撑鞋改为较宽平底缘；左脚仍高，没有提前换侧。',
'右腿继续后延、鞋底窄；左膝高屈。v5实图已去除v4远右孤立黑点，保持右支撑；原生重绘有细节差异，不是像素级原位清理。',
'右脚继续低位支撑；替代旧06双脚离地/提前换侧。左脚折起。',
'右脚维持支撑、左摆动鞋底缩短，鞋跟较可读；不是旧提前左脚支撑稿。',
'v5右脚仍支撑，左小腿实际向下伸、整块鞋底缩成窄缘；人工读左跟低边约1080，相比v4约1040下降约40；提示词1115没有全达到。改善预接触但到09约1170仍有余差，须实播。',
'左腿长且低、右鞋底高，实际异侧；窄鞋底缘改善接触可读性。',
'左脚继续低位承重，右腿高折；左卷手较低/近、右笔较高/远。',
'左腿承重、右脚高；双臂又较外展，10→11肩肘深度需正常速度复核。',
'左支撑延续11，鞋底改成较窄平底缘；右脚不提前落地。',
'左腿后延且低位宽底缘，右腿高折；替代旧13大片支撑露底。',
'左腿继续支撑，右腿摆动；替代旧14提前换侧，头身自然起伏只作连续性观察。',
'左支撑鞋俯仰稍增，右脚仍高；15→16→01换脚动态待合审，不能仅凭左低右高判已通过。',
'v5左脚支撑保留，右小腿实际伸下、整块鞋底缩成窄缘；右跟低边约1085，相比v4约1045下降约40，提示词1135未全达到。改善预接触但到01約1190仍有余差，须实播。'],
'NW':[
'近侧左腿前伸承重，远右腿弯曲，鞋底朝后；轴向NW。',
'近左继续承重、膝稍压；同侧平底边清楚，远右仍悬空。',
'近左腿从髋前景延至身体后侧下方，远右收于袍后；近左鞋底宽。',
'近左延续03、宽平底边，远右仍袍后；替代旧04大片底面。',
'近左后延支撑、远右向前收，宽底边；v7较v6缩回过大的支撑后伸。',
'近左继续后延支撑，远右小靴较高；替代旧06腾空稿。',
'近左前掌仍有宽支点，远右小靴向前回收；鞋跟轻抬而非垂直踮尖。',
'近左支撑保留07的宽底边，远右靴向前展开；v5替代v4过高抬跟。到09有余下下降，须实播。',
'远右腿后景支撑、近左大腿在前景弯折、鞋底显露，和01确实交换解剖侧。',
'远右继续支撑，近左膝向前屈；前后髋遮挡可以追踪。',
'远右在身下承重，近左靴仍高；支撑鞋轴仍NW。',
'远右延续11、宽平底边，近左屈膝；替代旧12大片露底。',
'远右向后支撑，近左大腿在前景前摆；非重复05近左支撑。',
'远右继续后延支撑，近左前摆；替代旧14腾空稿。',
'远右仍低位宽底支撑，近左靴前移且底面减少；保持笔卷手身份。',
'远右支撑延续15，近左靴下降但仍露底；16→01剩余落差须实播，不按目标y坐标算完成。']}
pairNames=['直轴落地/初承重','身体经过支撑脚','同脚后延承重','同脚最后推送/另一腿接近']
known={
'N':['08→09、16→01：摆动脚预落地下降与支撑交换须1200ms正常播放确认。','02→03、10→11及07→08：卷轴/毛笔手臂前后摆幅和肩肘深度有变化，持物身份正确但摆臂流畅性未正式通过。','N后视的四空间位置差异小于NW；同侧持续低位不等于四位置已正式验收。','15/16左支撑鞋存在抬跟/露底解释空间，须结合240px动态承重；没有单凭底面可见就判外翻。'],
'NW':['08→09、16→01：两次换脚仍需要正常播放核对摆动脚下降与髋部位移的连贯性。','02→03与10→11：上肢转动、躯干轻转及长短腿投影变化需动态合审。','15/16摆动近左鞋仍露底，和支撑远右鞋分属不同腿；不能把摆腿露底误判支撑外翻。']}
result={}
for dr,vs in versions.items():
 rp=b/f'review-run-{dr}.json'
 old=read(rp)
 hist=b/'review'/f'pre-support-pairs-{dr}-review-history.json'
 if not hist.exists():write(hist,{'status':'historical_superseded_phase_assumptions','supersededBy':'same support foot per8; 2frames per position;1200ms', 'previousReview':old})
 frames=[]
 for i,v in enumerate(vs,1):
  key=f'run-{dr}-{i:02}-v{v}';p=b/'staging'/f'{key}.png';im=Image.open(p);im.load();recp=p.with_suffix('.png.generation.json');rec=read(recp)
  support=('RIGHT' if i<=8 else 'LEFT') if dr=='N' else ('near anatomical LEFT' if i<=8 else 'far anatomical RIGHT')
  digest=sha(p);assert digest==rec['sha256'];assert im.width>=1024 and im.width==im.height;assert im.mode=='RGBA'
  frame={'n':i,'slot':f'run-{dr}-{i:02}','key':key,'file':f'staging/{key}.png','sha256':digest,'native_size':list(im.size),'alpha_extrema':list(im.getchannel('A').getextrema()),'generationRecord':str(recp.relative_to(b)).replace('\\','/'),'request_exists':(b/rec['evidence']['request']).exists(),'prompt_exists':(b/rec['prompt']).exists(),'supportFootObserved':support,'requestedPositionPair':(i-1)//2+1,'positionIntent':pairNames[((i-1)%8)//2],'actualObservation':notes[dr][i-1],'status':'candidate_pending_normal_speed_sequence_review','contactAccepted':False,'anatomyAccepted':False,'notes':notes[dr][i-1]}
  frames.append(frame)
  receipt=b/'provenance'/f'{key}.tool-result.json'
  if receipt.exists():rec['evidence']['toolResultFile']=str(receipt.relative_to(b)).replace('\\','/')
  rec['review']={'status':frame['status'],'selectedForSequenceReview':True,'actualObservation':frame['actualObservation'],'reviewedAt':now,'formalAcceptance':False}
  write(recp,rec)
 assert len(set(f['sha256'] for f in frames))==16
 rv={'character':b.name,'direction':dr,'status':'complete_16_candidates_pending_normal_speed_review','reviewedAt':now,'visualPassed':0,'formalVisualPassedSlots':0,'formalExportedSlots':0,'sequencePassed':False,'timing':{'frames':16,'frameMs':75,'cycleMs':1200,'framesPerPosition':2,'positionMs':150,'halfCycleSupportMs':600},'adoptedLoopMs':1200,'method':'实际原生图和240px完整16帧、鞋部裁片逐张查看；按髋-膝-踝-靴链追踪支撑侧。未用程序修改原图/alpha/整图升降，没有复制帧或改变时长。当前是完整可合并候选，主窗口负责正常速度实播。','latestAuthority':'同脚连续01-08支撑、另一脚09-16支撑；每空间位置两张独立姿态。覆盖旧4接地+腾空相位。','frames':frames,'selectedForSequenceReview':[{'slot':f['slot'],'file':f['file'],'status':f['status'],'notes':f['notes']} for f in frames],'reviewed':[{'file':f['file'],'status':f['status'],'notes':f['notes']} for f in frames],'supportFootHalves':{'01-08':frames[0]['supportFootObserved'],'09-16':frames[8]['supportFootObserved']},'knownRemainingReview':known[dr],'identity':'每张保持右手毛笔、左手卷轴、两个墨灵；没有通过仅交换道具伪造换手。','footAxis':'N靴长轴沿N；NW靴沿NW。允许背视摆腿露底，不等同外撇；支撑腿抬跟不能仅按最低像素证明真实接地。','ground':{'acceptedGroundPlane':None,'acceptedRootAnchor':None,'status':'visual_stance_candidates_dynamic_review_pending','explanation':'背视/后斜视存在纵深，未把各鞋最低像素强压同一水平线。宽底边和膝踝链是本轮承重证据；真实跑动仍需主窗口动态审查。'},'headMotionAcceptance':'允许与身体及承重相符的自然起伏；不将头顶几像素变化单独判失败，不程序冻结头部。','qa':['review/support-pairs-'+dr+'-current-240.png','review/support-pairs-'+dr+'-current-feet.png'],'knownEdgeIssue':'部分原生透明边缘仍有红青/黄色细边；未使用alpha算法。','modelDisclosure':'配置目标gpt-image-2.5-sunburst/max；内置工具无model/quality参数，实际返回未披露，两者null。','previousReviewHistory':str(hist.relative_to(b)).replace('\\','/'),'client':'not_integrated_not_tested'}
 write(rp,rv)
 for mode in ['240','feet']:
  w,h=(240,265) if mode=='240' else (330,290)
  sheet=Image.new('RGB',(4*w,4*h),(218,221,222));draw=ImageDraw.Draw(sheet)
  for j,f in enumerate(frames):
   im=Image.open(b/f['file']).convert('RGBA')
   if mode=='feet':im=im.crop((300,740,1000,1254))
   im.thumbnail((w,h-25));x=(j%4)*w+(w-im.width)//2;y=(j//4)*h+25;sheet.paste(im,(x,y),im);draw.text(((j%4)*w+5,(j//4)*h+5),f['key'],fill='black')
  sheet.save(b/'review'/f'support-pairs-{dr}-current-{mode}.png')
 result[dr]={'selected':[f['file'] for f in frames],'uniqueNativeFrames':16,'supportHalves':rv['supportFootHalves'],'remainingReview':known[dr]}
 ref=b/'review'/('reference09-N-20261003.json' if dr=='N' else 'reference09-NW-20261004.json')
 if ref.exists():
  rr=read(ref);rr['currentSupportPairsReview']={'reviewedAt':now,'supersedesPriorPhaseClaims':True,'reason':'最新用户同脚8帧支撑/每位置2帧覆盖旧接地和腾空分配。09仍为用户认可动作参照；没有照搬其旧相位编号和时长。','currentSelectionReport':f'review-run-{dr}.json','selectedFiles':[f['file'] for f in frames],'status':rv['status']};write(ref,rr)
pairpath=b/'review'/'support-pairs-N-NW-20261004.json';pairs=read(pairpath);pairs['status']='complete_native_candidates_pending_root_normal_speed_review';pairs['reviewedAt']=now;pairs['currentResults']=result;pairs['limitations']='已按实图保住同侧连续8帧候选，未把16齐或低脚标签等同正式验收。正常1200ms实播由主窗口执行。';pairs['notAccepted']=['没有正式验收：换脚衔接、四位置可读性、摆臂顺畅仍需实播。'];write(pairpath,pairs)
print(json.dumps({'directions':result,'native32Unique':len(set(sha(b/f) for v in result.values() for f in v['selected']))},ensure_ascii=False))
