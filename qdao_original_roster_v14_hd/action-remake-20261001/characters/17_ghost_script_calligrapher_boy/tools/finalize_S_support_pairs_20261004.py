from pathlib import Path
from PIL import Image
import json,hashlib,datetime
b=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
vs=[3,2,1,4,3,5,7,5,3,2,3,2,3,3,6,5]
obs=[
'右/imageLEFT脚在前下方，以金前掌下窄暗底缘支撑；v3比旧v1整底前翘减少。左腿屈于后方，轴向S。',
'右脚继续平底缓冲，鞋带-鞋尖居中，左脚尚在后方；支撑形态保留。',
'右脚在身体下方平底承重，左膝通过；右笔臂向前、左卷臂向后开始换摆，握持侧别不变。',
'右脚仍承重，左膝抬起前摆、摆靴底缘显露；旧文档未形成蹬离不再是本帧目标。',
'右脚仍低位后侧支撑，右靴较窄是抬跟/纵深，左靴抬前；保持最新要求的持续支撑。',
'v5右脚已真实画成长腿下接宽前掌，替代旧v3两脚悬空；左膝抬起。没有靠全图平移。',
'v7右脚在后侧仍有平底前掌支点，左摆靴前伸露底；相对06透视/身形略变，需连播。',
'v5右脚持续后侧支撑，左靴临接触、可见底面属于摆腿；07→08右脚投影高度变化需要连播而非强贴水平线。',
'v3左/imageRIGHT脚前伸，金前掌下为窄暗底缘，未见14/16摆脚那种大片棕色整底；右脚后屈。按实图选为接触候选。',
'左脚继续缓冲承重，鞋尖朝S；右脚仍后收。09/10人物轮廓差别需动态看，不单凭头顶偏移否决。',
'左脚身下平底承重，右膝通过、靴朝S；右笔后摆、左卷前摆，持物连接可见。',
'左脚继续身下支撑，右腿前摆；靴轴未见确定横向外撇，保留v2。',
'左脚后侧低位支撑，右摆靴前伸；鞋尖鞋带朝S。旧前掌蹬离不通过文字已不作为本帧早离地目标。',
'v3左腿伸下并以宽前掌支撑，右摆靴露底；替代旧v2后靴离地。卷轴较13更展开是透视变化，待连播。',
'v6左脚仍后侧宽前掌支撑，右靴前伸下落；笔卷手没有互换。',
'v5左脚持续后侧支撑，右靴前伸待接触；整底显露的是右摆脚；到01换侧，需正常播放确认。']
oldp=b/'review'/'review-run-S.json';hist=b/'review'/'pre-support-pairs-S-review-history.json'
if not hist.exists():write(hist,{'status':'historical_superseded','reason':'same support foot per8 and2 independent poses per position replaces older flight distribution','previousReview':read(oldp)})
frames=[]
for i,v in enumerate(vs,1):
 key=f'run-S-{i:02}-v{v}';p=b/'staging'/(key+'.png');im=Image.open(p);im.load();recp=p.with_suffix('.png.generation.json');rec=read(recp)
 assert im.size==(1254,1254) and im.mode=='RGBA';assert sha(p)==rec['sha256'];assert (b/rec['evidence']['request']).exists();assert (b/rec['prompt']).exists()
 f={'n':i,'frame':i,'slot':f'run-S-{i:02}','file':f'staging/{key}.png','sha256':sha(p),'nativeSize':list(im.size),'alphaExtrema':list(im.getchannel('A').getextrema()),'supportFootObserved':'anatomical RIGHT / image LEFT' if i<=8 else 'anatomical LEFT / image RIGHT','positionPair':(i-1)//2+1,'positionIntent':['front loading','under-body support','first rear support','second rear support'][((i-1)%8)//2],'actualObservation':obs[i-1],'notes':obs[i-1],'status':'selected_pending_playback','approval':False,'generationRecord':str(recp.relative_to(b)).replace('\\','/'),'requestExists':True,'promptExists':True}
 frames.append(f);rec['review']={'status':'selected_pending_playback','selectedForSequenceReview':True,'actualObservation':obs[i-1],'reviewedAt':now,'formalAcceptance':False};receipt=b/'provenance'/(key+'.tool-result.json')
 if receipt.exists():rec['evidence']['toolResultFile']=str(receipt.relative_to(b)).replace('\\','/')
 write(recp,rec)
assert len({f['sha256'] for f in frames})==16
out={'character':b.name,'direction':'S','reviewedAt':now,'status':'selected_pending_playback','available':16,'expected':16,'missing':[],'approved':0,'visualPassed':0,'formalVisualPassedSlots':0,'sequencePassed':False,'runTiming':{'cycleMs':1200,'frameMs':75,'uniform':True,'pairMs':150},'latestRequirement':'01-08同一右脚连续支撑，每相对位置两张独立姿态；09-16同一左脚连续支撑。覆盖旧腾空06/14与提前换脚07/15等分配。','method':'逐张原生图、完整16张240px联系图、鞋部裁片实审，保留正确脚轴与身份。本接手轮未新增生图、未平移/配准/改alpha。','frames':frames,'selectedForSequenceReview':[{'slot':f['slot'],'file':f['file'],'sha256':f['sha256'],'status':f['status'],'notes':f['notes']} for f in frames],'actualSupportFrames':{'anatomicalRight':list(range(1,9)),'anatomicalLeft':list(range(9,17))},'supportClassificationLimit':'人工从髋膝踝和宽前掌形态判断当前候选；透明前视透视没有绝对全局地面，不能根据最低像素统一贴地。','remainingReview':['08→09、16→01换脚接触衔接须主窗口正常1200ms实播。','07→08支撑靴投影高度、09→10头身体积与14→15卷轴透视变化须动态复核；自然起伏不单独判失败。','02→03笔臂前摆有变化，但未见W那种两手一帧跨到另端的整幅换极，暂不为坐标改动追加重绘。'],'axisFinding':'支撑和摆动靴中心鞋带、前掌长轴总体朝S；未发现当前候选必须立即外旋纠正的明确靴轴硬错。摆腿显底不等同支撑脚外翻。','identity':'右笔、左卷、两个墨灵，肩袖-握持连接可追踪。','qa':['review/support-pairs-S-current-240.png','review/support-pairs-S-current-feet.png'],'standaloneLivePreview':'review/support-pairs-S-live.html','playbackVerification':{'status':'not_performed_on_this_subagent','attemptedUrl':'http://127.0.0.1:8767/review/support-pairs-S-live.html','tool':'mcp__cua_repl','rawError':'Browser is not available: iab','followupInventory':{'apps':[],'browsers':[]},'ownerForReview':'root current active browser','notClaimed':'未把静态联系图或HTML代码正确等同真实动态通过。'},'supersededReview':str(hist.relative_to(b)).replace('\\','/'),'newlyAdoptedExistingNativeFrames':[1,6,7,8,9,14,15,16],'sourceAuthority':'09竹弓少女保持用户认可；最新同脚连续8帧和1200ms覆盖旧相位/时长。','headMotionAcceptance':'跑步自然起伏允许；不按单独头顶位移判失败，不改整体像素配准。','knownEdgeIssue':'原生细彩边仍有，未算法改alpha。','modelDisclosure':'既有逐图生成记录不改写；实际内置模型/质量未披露，目标配置与actual null保持区分。'}
write(b/'review-run-S.json',out);write(oldp,out)
write(b/'review'/'support-pairs-S-live-attempt.json',out['playbackVerification'])
for dr in ['N','NW','S']:
 rv=read(b/f'review-run-{dr}.json');selected={Path(f['file']).name for f in rv['selectedForSequenceReview']}
 for rp in (b/'staging').glob(f'run-{dr}-*.png.generation.json'):
  rec=read(rp);name=rp.name.replace('.generation.json','');r=rec.get('review',{})
  if name not in selected and r.get('selectedForSequenceReview') is True:
   r['selectedForSequenceReview']=False;r['status']='superseded_by_current_support_pairs_selection';r['currentSelectionReport']=f'review-run-{dr}.json';rec['review']=r;write(rp,rec)
print(json.dumps({'S': [f['file'] for f in frames],'unique':16,'size':'1254x1254','mode':'RGBA','recordHashesMatch':True,'newGenerationThisReview':0,'dynamicAccepted':False},ensure_ascii=False))

