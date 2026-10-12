from pathlib import Path
import json, hashlib
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parent.parent
B=R.parent/'09_bamboo_archer_girl'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
now=datetime.now(timezone.utc).isoformat()
p=R/'generation/NE/03-v4.png'
im=Image.open(p);a=im.getchannel('A')
review={'schemaVersion':1,'file':p.relative_to(R).as_posix(),'sha256':sha(p),'reviewedAtUtc':now,'action':'run','direction':'NE','frame':3,'version':4,'status':'rejected_for_selection','visualAccepted':False,'clientAcceptance':'not_performed','dynamicAcceptance':False,'native':list(im.size),'mode':im.mode,'alphaExtrema':a.getextrema(),'alphaGt8BoundsExclusive':a.point(lambda v:255 if v>8 else 0).getbbox(),'actualModel':None,'actualQuality':None,'durationMs':75,'cycleMs':1200,'observedPhase':'原右脚仍在低位支撑，左腿仍主要后折；近右灯臂提前到高位，未得到中段passing。','selectionChanged':False,'issues':['左摆腿没有完成从后折向前通过：鞋中心仅约(555,975)→(585,975)，仍未达到目标(650,1020)的中位。','右手灯握点从旧约(990,625)上到约(1005,470)，比目标y565更高，接近/超过04-v1约(985,500)。入选会把跳变提前到02→03。','右支撑鞋保持原区域，底边略下移约10px，头顶较旧稿略高；不是严格像素局部锁定。'],'manualLandmarks':{'method':'人工观察原图估计，误差约10–20源像素；不是自动分割或真实关节测量','03-v1':{'rightGrip':[990,625],'leftSwingShoeCenter':[555,975],'rightSupportBottomY':1183},'03-v4':{'rightGrip':[1005,470],'leftSwingShoeCenter':[585,975],'rightSupportBottomY':1193},'04-v1':{'rightGrip':[985,500],'leftSwingShoeCenter':[795,966],'rightSupportBottomY':1184}},'root':{'native':[710,1180],'nativeCanvas':1254,'status':'fixed diagnostic only; no alignment performed'},'pixelOperation':'one independent local AI redraw; no programmatic sprite transform'}
write(p.with_suffix('.review.json'),review)
gp=Path(str(p)+'.generation.json');g=json.loads(gp.read_text(encoding='utf8'));g.update(status='rejected_for_selection',reviewFile=p.with_suffix('.review.json').relative_to(R).as_posix(),action='run',direction='NE',frame=3,operation='one local AI redraw; not selected after actual inspection');write(gp,g)
manifest=json.loads((B/'manifest.json').read_text(encoding='utf8'))
ref_sources=[]
for seq in manifest['sequences']:
 if seq['action']=='run' and seq['direction'] in ('NE','E','W'):
  for f in seq['frames']:
   fp=B/f['file'];actual=sha(fp);assert actual==f['sha256']
   rim=Image.open(fp);assert rim.size==(1024,1024) and rim.mode=='RGBA'
   ref_sources.append({'direction':seq['direction'],'frame':f['frame'],'path':str(fp),'sha256':actual,'manifestMatch':True,'inspection':'contact sheet whole sequence; selected full images separately listed'})
full09=['runtime/run/NE/04.png','runtime/run/NE/11.png','runtime/run/NE/12.png','runtime/run/NE/13.png','runtime/run/E/03.png','runtime/run/W/03.png']
full03=['generation/NE/01-v3.png','generation/NE/03-v1.png','generation/NE/04-v1.png','generation/NE/11-v1.png','generation/NE/13-v1.png','generation/NE/16-v1.png','generation/NE/03-v4.png','generation/E/03-v3.png','generation/E/04-v5.png','generation/E/12-v6.png','generation/W/04-v1.png','generation/W/11-v1.png']
inputs=['review/run-NE-sequence-input.json','review/run-E-selection.json','review/run-W-sequence-input.json']
current=[]
for name in inputs:
 q=R/name;j=json.loads(q.read_text(encoding='utf8'))
 current.append({'file':name,'sha256':sha(q),'frameCount':len(j['frames']),'durationsMs':[f['durationMs'] for f in j['frames']],'totalMs':sum(f['durationMs'] for f in j['frames'])})
 assert len(j['frames'])==16 and all(f['durationMs']==75 for f in j['frames'])
 if name==inputs[0]:assert j['frames'][2]['source']=='generation/NE/03-v1.png'
audit={'schemaVersion':1,'createdAtUtc':now,'scope':'03 NE/E/W static direction, hand and contact comparison against user-recognized 09 same-direction material','visualAccepted':False,'browserTest':False,'clientTest':False,'referenceAuthority':'09用户认可当前版本；本次仅以实际同方向图像作视觉对照，不把相同帧号当成相同相位，不复制像素，不扩展为客户端已验收。Moon未使用。','referenceDocuments':[{'path':str(B/x),'sha256':sha(B/x)} for x in ['MERGE_HANDOFF.md','manifest.json','animation-timing.json']],'referenceFrames':ref_sources,'fullImagesActuallyViewed09':[{'path':str(B/x),'sha256':sha(B/x)} for x in full09],'fullImagesActuallyViewed03':[{'path':str(R/x),'sha256':sha(R/x)} for x in full03],'contactSheetsActuallyViewed':[{'path':str(root/x),'sha256':sha(root/x)} for root,names in [(B,['preview/qa/run-NE-contact.png','preview/qa/run-E-contact.png','preview/qa/run-W-contact.png']),(R,['preview/run-NE-contact.jpg','preview/run-E-contact.jpg','preview/run-W-contact.jpg'])] for x in names],'current03Inputs':current,'blockingFindings':[{'id':'NE-passing','severity':'clear_continuity_defect','evidence':'03 NE01–03左鞋长期后折；03-v1左鞋约(555,975)，04-v1突然转至约(795,966)，右灯握点约y625→500。缺少膝向前通过和灯臂中位。09也有低幅段，不能靠09同帧号自动修好。','fixResult':'03-v4一次编辑未改善passing且灯臂过早抬高，未入选。'}],'directionFindings':[{'direction':'NE','feet':'03支撑脚经常以更短的鞋尖/后跟视图出现；09 NE11/12鞋的侧面长轴更容易读，03宽裤和鞋跟视角会掩盖膝踝关系。原03-v1与04-v1的右支撑到后蹬可追踪，没有足够证据把露出的鞋底本身判成外撇；需要在1200ms播放中继续看鞋尖与胫骨同平面。','hands':'关键原图能沿近右肩/袖连接到灯；玉瓶在远左。未见真实换手。','contact':'16→01右脚下降衔接在当前诊断根点附近；11→12过渡幅度偏大但支撑脚归属仍能读。前后半圈头/骨盆约60px横向差异需整圈核验，不能逐帧挪图消除。'},{'direction':'E','feet':'03 E03-v3支撑鞋长轴向屏右，与09 E03的支撑姿态有相近承重关系；03鞋面更宽、更多俯视顶面，09靴子侧面更长更清楚。E04-v5/E12-v6后支撑鞋朝右且脚跟抬起，静图不足以认定双脚V形外叉。','hands':'03近右灯、远左瓶没有换手；03 E03→E04灯臂由后髋快速跨至前方，幅度比09空右拳明显更大，仍有连续性风险。','contact':'E16已经开始跟接触，E01继续接触；两张接触不是自动错误，但1200ms下接触停留感需实播，未冒称通过。'},{'direction':'W','feet':'03 W04近左支撑与W11远右支撑鞋尖均向屏左，膝踝投影同向；与09 W03支撑相位比较，03宽裤遮掉膝关节更多，后折鞋的鞋面装饰增加外转观感。未从已看原图证实水平yaw外叉。','hands':'近左玉瓶、远右灯保持；W04→05及W10→11道具前后交接较大，和09持弓臂的有限摆幅不同，不能把这当成换手。','contact':'W16→01是前跟继续下降，主要待1200ms动态观察；禁止用每帧最低alpha归一化掩盖浮移。'}],'nonBlockingOrUnresolved':['09本身NE早期也有幅度较小段，它提供已认可的方向/鞋型观感，不是可机械照搬的相位编号模板。','圆鞋与长靴的轮廓、裙裤遮挡差异属于角色设计差异；只凭鞋面暴露/鞋底可见不能断言脚yaw错误。','当前只做静态联系图和选定全图检查，无浏览器连播、无客户端验收。'],'changes':{'Wcast12':'selected generation/cast/W/12-v2.png; local lamp body repair; hand/feet retained; slight oversize remains','NE03':'03-v4 generated and rejected; run-NE input untouched','previewFilesModified':False,'09FilesModified':False,'totalManifestModified':False,'sourcePNGProgrammaticTransforms':False}}
write(R/'review/run-NE-E-W-vs09-static-audit-20261004.json',audit)
print(json.dumps({'09FramesHashVerified':len(ref_sources),'NE03v4Selected':False,'NECurrentSource':'generation/NE/03-v1.png','runTotals':[x['totalMs'] for x in current],'reviewsWritten':[str(p.with_suffix('.review.json')),str(R/'review/run-NE-E-W-vs09-static-audit-20261004.json')]}))

