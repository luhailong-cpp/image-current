from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
R=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=json.loads((R/'review/video-axis-details/inputs.json').read_text(encoding='utf-8'))
own=[x for x in inputs if '06_thunder_caster_boy' in x['file']]
assert len(own)==48
assert all(sha(Path(x['file']))==x['sha256'] for x in inputs),'审计源已变化，不能套用旧观察'
observations={
'S':[
('右膝至踝向下，鞋面中线继续朝正南，前载没有侧翻。','左脚屈膝后收，露出的鞋面和鞋尖仍朝前下，未反转。'),
('右足较00收近，踝与金色鞋面中线连续，脚掌保持正面。','左足后抬较高，足背朝前下；屈膝透视缩短保留。'),
('右脚进入髋下，膝踝略压缩，鞋尖继续朝S。','左膝前提而靴仍低垂，脚背中线未朝外侧折断。'),
('右踝压缩较明显，但鞋尖与02同向，未见突然内外翻。','左腿前摆的鞋尖仍在膝踝前后摆动平面内。'),
('右后足前掌支撑，靴面仍朝S，后蹬不变成横踩。','左前摆足上翘露底；鞋底长轴居中，属于俯仰而非向侧面翻转。'),
('右后足继续支撑，脚尖和04同向。','左鞋底面扩大，脚跟仍在踝下、前掌在运动前端，未横向扭开。'),
('左前伸脚掌已放平，膝、踝与鞋中线连贯朝S。','右足屈膝后收，脚背正面可见，无反向鞋尖。'),
('左脚第二初接帧，鞋尖朝S且掌面平稳；保留自然轻微身倾。','右后足进一步收起，足背与06一致。'),
('左前载靴从初接位置回收，鞋尖仍正向前。','右脚屈膝抬起，短缩的鞋面未向外侧翻。'),
('左承重膝踝压缩，足背中线保持正S。','右后摆靴方向与08连续，保持屈膝产生的透视。'),
('左脚经过髋下，脚尖和前掌朝S，未突然旋转。','右腿准备前摆，鞋面在膝下，未出现鞋尖朝侧后的反转。'),
('左支撑脚仍正S，膝踝位置变化而脚面不侧翻。','右抬脚略向画面左偏，膝踝随之移动；不足以确证踝部外扭。'),
('左后足前掌支撑，仍保持正南鞋向。','右前摆靴上翘露底，脚跟与踝相接，长轴仍在正南平面。'),
('左足继续后蹬，脚掌方向与12连续。','右脚底可见面积增加但不横向翻面；保留前摆上翘。'),
('右前伸靴已放平，踝、鞋面中线和正S鞋尖连贯。','左足折回，鞋面正向下前方；无侧面反转。'),
('右脚第二初接，平掌与14连续，环接00仍同向。','左后脚保持折叠；鞋尖未朝身体外侧突然翻出。')],
'SE':[
('右承重靴的鞋跟在左后、鞋尖在右前，符合SE斜向。','左后摆足随屈膝缩短，足背未从一侧翻到另一侧。'),
('右脚较00收近，踝与鞋面相接自然，SE轴稳定。','左后脚位置略抬高，鞋尖仍沿屈膝折回的投影。'),
('右足经过身体下方，前掌朝右下，膝踝没有向相反侧拧。','左腿前摆准备，靴在踝下，未见突然反向鞋底。'),
('右支撑踝向后发展，鞋尖维持右下，保留后蹬倾角。','左膝前提，脚部仍随同一前后摆动平面变化。'),
('右后足前掌支撑，鞋向右前，踝仍接在鞋跟上方。','左前摆足明显上翘，鞋底朝右前可见；单图与09 SE05同类俯仰，未确证侧翻。'),
('右后足继续支撑，脚尖与04一致。','左脚前伸更远且上翘更大，鞋跟仍接踝后下方；关注05→06放掌过渡，不因露底判外翻。'),
('左初接靴平掌，鞋跟左后、鞋尖右前；略偏水平是斜视鞋长轴投影。','右后腿屈膝收起，鞋面向下前，保留透视短缩。'),
('左初接靴较06前掌更展开，踝与鞋体连贯，未形成向外侧折断。','右后摆足与06同一折叠方向，未突然翻底。'),
('左前载靴朝SE，鞋跟与前掌处于一致接地面。','右后摆鞋收在身后，脚背仍与小腿连接自然。'),
('左前载鞋位置回收而方向保持右前，未侧转。','右后足继续屈膝，短缩和鞋尖轻垂保持。'),
('左脚经过髋下，前掌朝右下，踝部无明显外折。','右抬脚在后方折回，鞋面朝向变化未构成反转。'),
('左支撑脚维持SE，膝踝与鞋面连续。','右后足鞋尖投影较偏左下，但与折膝后收一致，静态不足以判为外翻。'),
('左足在后侧蹬离，鞋跟抬高、前掌方向保持右前。','右腿前摆的短缩鞋位在踝下，没有独立横向扭转。'),
('左后足继续前掌支撑，脚尖与12保持同向。','右摆动靴随抬膝变化，未见鞋底突然左右互换。'),
('右前伸初接脚掌平放，鞋跟左后、鞋尖右前。','左后摆脚屈膝悬空，保持正常后收投影。'),
('右第二初接靴沿SE放平，环接00方向一致。','左后摆鞋面沿腿部折叠，未反向。')],
'SW':[
('右支撑靴朝左下，鞋跟在右后，身体经过时未横向转鞋。','左后脚向下前方短缩，仍随折膝，没有单独外翻。'),
('右支撑脚较00回收，鞋尖仍为SW方向。','左后摆足姿态与00连续，保留脚背可见。'),
('右足后蹬的前掌朝左前，踝向后倾但鞋尖未扭反。','左腿准备前摆，靴面未从外侧翻至内侧。'),
('右后侧支撑保持SW，脚跟抬起并非整鞋侧翻。','左前摆脚随膝踝移动，没有清楚可证的外旋断点。'),
('左前伸脚掌朝左下，膝踝至鞋面连续。','右脚后收，鞋尖轻垂而仍在前后摆动平面。'),
('左初接鞋向与04一致，鞋面较展开但没有外撇跳转。','右摆动靴位置变化保留屈膝透视。'),
('左前载靴朝SW，鞋跟和前掌在一致平面。','右抬脚投影较正S，但位于折膝腿下方，未确证踝部外拧。'),
('左承重脚的鞋尖继续左下，踝部没有突然内扣。','右后收足较短缩，脚背正面可见与06连续。'),
('左支撑脚进入髋下，鞋面中线与左下鞋尖相接。','右后摆靴位于膝后下方，鞋尖近S为折膝投影，未横翻。'),
('左支撑靴较08回收，左下方向稳定。','右后摆鞋面与08连续，未换边露底。'),
('左足后侧支撑保持SW，踝与鞋跟连接自然。','右靴仍收在屈膝下方，脚背朝前下；与11前伸变化幅度较大，需正常速度看节奏。'),
('左后足仍朝SW，支撑鞋未侧翻。','右前摆靴鞋尖偏画面左并上翘，露出鞋底；膝-踝-鞋跟仍相接，单图可由前伸屈踝解释，列动态关注而非硬错。'),
('右前伸靴落平朝左下，从11上翘转为平掌；单图鞋轴无外折。','左后足折回，保留足背朝前下的短缩。'),
('右第二初接鞋掌与12同向，未横向旋转。','左后摆靴方向与12连续，无鞋底突然反转。'),
('右前载足朝SW，鞋跟在右后，膝踝受力方向自然。','左后摆足缩在腿后，鞋面未向外侧翻。'),
('右前载靴与14同向，环接00鞋轴连续。','左后脚的折膝透视保留，未见独立侧翻。')]
}
phaseDocs={d:json.loads((R/f'review/run_{d}_contactpairs_20261004.json').read_text(encoding='utf-8')) for d in ['S','SE']}
phaseDocs['SW']=json.loads((R/'review/run_NE_SW_contactpairs_20261004.json').read_text(encoding='utf-8'))
frames=[]
for source in own:
 d,n=source['direction'],source['frame']; pair=next(x for x in phaseDocs[d]['pairMap'] if n in x['frames'])
 support,swing=observations[d][n]
 frames.append({'file':str(Path(source['file']).relative_to(R)).replace('\\','/'),'sha256':source['sha256'],'frame':n,'direction':d,
 'supportLeg':pair['supportLeg'],'swingLeg':'左脚' if pair['supportLeg']=='右脚' else '右脚','pairFrames':pair['frames'],'positionPhase':pair['position'],
 'supportLegObservation':support,'swingLegObservation':swing,'verdict':'dynamic-watch-not-confirmed-error' if (d=='SE' and n in [4,5]) or (d=='SW' and n==11) else 'retain-no-confirmed-axis-error',
 'retain':['当前两帧位置对','当前支撑脚及接触点','正常屈膝和透视短缩','已正确的手部、道具与上身'],'diagnosticImage':f'review/video-axis-details/06-{d}-{n//4}.jpg','actualViewedAtNativeCrop':True})
def evidence(d,ns): return [{k:x[k] for k in ['file','sha256','direction','frame']} for n in ns for x in frames if x['direction']==d and x['frame']==n]
contextFiles=[Path('C:/Users/luyua/AppData/Local/Temp/codex-clipboard-7cc4bf22-e4cf-4c35-8ac6-a37fd85f4037.png'),R.parents[1]/'reference-motion-review-20261004/video-contact.jpg',R.parents[1]/'reference-motion-review-20261004/character-detail.jpg',R/'review/video_reference_sequence_192_20261004.jpg',R/'review/video_reference_sequence_288_20261004.jpg']
doc={'schemaVersion':1,'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/finish_s','scope':'run/S, run/SE, run/SW 当前48帧腿脚方向，只读像素审计','trigger':'用户最新视频指出腿脚歪/外翻；旧轮通过不能代替本轮检查。',
 'method':['实际看用户12山岳NW截图，仅学习歪脚错误类型，不复制角色或方向。','实际看共享视频抽样和角色局部；视频中角色小且名称/蓝色地面效果遮腿，不能证明每张脚部细节。','逐张实际看当前48帧的原尺寸下肢裁切，包含膝、踝、足背、鞋底。','实际看09同向S/SE/SW各01、05、09、13作为运动平面参考；09为1起始，不能按同号直接断定相位。','单图复看SE04/05和SW10/11/12，并复看09 SE05/13与SW05/13，区分俯仰露底与侧向外翻。'],
 'criterion':'检查膝到踝的运动平面、踝与鞋跟连接、足背中线/鞋长轴是否突然向内外侧转折；正常屈膝或足尖上翘可露底，不能把屏幕鞋轴不竖直等同外翻。',
 'timingPreserved':{'frameMs':75,'pairMs':150,'cycleMs':1200},'runtimeMutated':False,'sourceSnapshotStillCurrent':True,'wholeCyclePlaybackByThisReviewer':False,'wholeCyclePlaybackOwner':'/root',
 'summary':{'reviewedFrames':48,'confirmedAxisErrors':0,'correctionTargets':[],'dynamicWatchFrames':['SE/04','SE/05','SW/11'],'conclusion':'本轮静态逐图未确证必须重绘的外翻/反向鞋轴。SE04/05与SW11露底可由前摆上翘解释，保留原图并交主窗口结合连续播放判断。此结论不是整套动画最终通过。'},
 'findings':[{'id':'SE04-05-forward-pitch-watch','status':'not-confirmed-axis-error','leg':'左摆动腿','location':'前摆踝与鞋底','observation':'04到05膝前伸、脚尖上翘增大，鞋底朝右前显露。鞋跟仍接在踝后下侧，未见独立向体侧翻转。09 SE05也有同类前摆上翘露底。','evidence':evidence('SE',[3,4,5,6]),'retain':'保持左腿前摆与右脚后蹬，不能仅为消除露底把抬脚改成平掌。','nextCheck':'正常速度确认03→04→05→06的脚掌俯仰过渡，只有出现独立侧向扭转才局部修正。'},
 {'id':'SW11-forward-extension-watch','status':'not-confirmed-axis-error','leg':'右摆动腿','location':'画面左前方抬起的鞋','observation':'10的右足仍收在膝下，11前伸并上翘、鞋尖更偏画面左，12已平掌初接；11足底长轴偏左但膝踝鞋跟连接未断开，可由前伸屈踝解释。静态不能证实外翻。','evidence':evidence('SW',[10,11,12]),'retain':'保持左后足支撑、右腿前伸、手杖符牌和原两帧位置对。','nextCheck':'关注10→11→12是否在75ms节奏下读成急转；若只读成正常前摆，保持该帧。'}],
 'contextSources':[{'file':str(p),'sha256':sha(p),'actuallyViewed':True,'limitation':'动作与错误类型参考；不作为06每帧鞋细节通过证明。'} for p in contextFiles],
 'directionReferences':[{**x,'actuallyViewed':True} for x in inputs if '09_bamboo_archer_girl' in x['file']],
 'frames':frames,'provenance':'本文件为人工视觉审计；没有生成或编辑游戏PNG，没有改模型/质量记录。诊断JPEG仅裁切拼排，源哈希已复核。'}
doc['orderedNeighbourFollowup']={
 'method':'直接从当前runtime PNG读取，view_image original按序对照SE04→05→06→07、SW10→11→12；先看1:1腿部板，再看这些完整1024帧。此方法是顺序邻帧视觉对照，不冒充实时动画播放。',
 'additionalReference':'实际查看主窗口从原视频提取的连续32帧板192（8~9.29秒S）、288（12~13.29秒SW→W）；同向膝踝前后推进和正常抬脚露底可作定性参考，遮挡限制不变。',
 'SE04to07':{'evidence':evidence('SE',[4,5,6,7]),'observation':'04→05左膝与脚向右前伸展、脚尖上翘增强；05→06掌面落平且踝回到鞋跟上方，06→07维持同方向平掌。未出现向相反侧翻鞋或踝部独立外折。','decision':'保留；正常前摆俯仰至初接变化，未确证外翻。'},
 'SW10to12':{'evidence':evidence('SW',[10,11,12]),'observation':'10右足在后折膝下方，11随膝向左前摆并上翘，12左前方落平；鞋跟随踝，11露底与12掌面切换可由俯仰解释。10→11位移明显，但不能据此单图认定脚轴外扭。','decision':'保留；若主窗口正常速度看到节奏急转，再定点修。'},
 'runtimeMutated':False,'wholeCyclePlaybackClaimed':False}
dest=R/'review/video_axis_S_SE_SW_20261004.json';dest.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md='''# 06 跑步 S / SE / SW 视频后腿脚轴线复核\n\n当前 48 张均逐张查看原尺寸下肢；同时查看用户错误截图、共享视频抽样及 09 同向参考。视频角色小、腿脚受遮挡，因此只作运动参考。\n\n- 本次静态检查未确证必须重画的外翻/反向鞋轴；不等于整圈动态最终通过。\n- SE04/05：左腿前摆上翘而露底，踝与鞋跟相接，和 09 SE05 属于同类俯仰。保留，主窗口关注 03→06 连续过渡。\n- SW11：右前摆鞋尖偏左，10→11 位移较大；单图可由前伸屈踝解释。保留，主窗口关注 10→12 是否实际读成急转。\n- S 的前摆露底仍沿正南平面；支撑鞋轴和后折腿透视保留。\n\n逐帧双腿观察、相位、SHA、参考图与限制见同名 JSON。支撑相位、每两帧位置对、75 ms/帧、1200 ms/圈及正确手部均未修改。48 张 runtime PNG 哈希与检查开始时一致。\n'''
md+='\n追加顺序邻帧复核：直接读取当前 1024 PNG，按 SE04→05→06→07 与 SW10→11→12 查看完整帧，再对照原尺寸下肢板；未播放动画冒充动态验收。SE 左足为前摆上翘后落平，SW 右足为后折腿转前摆后落平，均未确证踝部独立外折，保留。另已查看原视频连续 32 帧板 192 与 288，仍仅作定性运动平面参考。\n'
dest.with_suffix('.md').write_text(md,encoding='utf-8')
print(json.dumps({'report':str(dest),'frames':len(frames),'confirmedAxisErrors':0,'runtimeUnchanged':True},ensure_ascii=False))
