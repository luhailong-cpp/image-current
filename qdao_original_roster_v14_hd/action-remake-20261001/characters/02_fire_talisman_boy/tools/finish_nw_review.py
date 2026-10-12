import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ip=R/'inventory-run-nw-finish.json';iv=json.loads(ip.read_text(encoding='utf-8'))
assert len(iv['frames'])==16
groups=[('RIGHT',[1,2],'central','右髋下承重，第二帧屈膝；近左腿离地'),('RIGHT',[3,4],'slight_rear','同一右足沿NW运动轴向画面右下稍后移'),('RIGHT',[5,6],'rear','同一右腿进一步向身后支撑，前掌持续压地'),('RIGHT',[7,8],'rear_push','右足后端支撑，08左小腿回收到下一落点附近'),('LEFT',[9,10],'central','近左足初触到屈膝压低，远右腿折起'),('LEFT',[11,12],'slight_rear','左足持续承重，身体经过脚上方'),('LEFT',[13,14],'rear','左支撑足相对髋部后移，右脚独立离地'),('LEFT',[15,16],'rear_push','左足后端前掌支撑；16右脚回收且左铃手臂前摆')]
lookup={f:(side,pos,note) for side,fs,pos,note in groups for f in fs}
rows=[]
for e in sorted(iv['frames'],key=lambda x:x['frame']):
    p=R/e['path'];actual=sha(p);assert actual==e['sha256'];rp=R/e['native_evidence'];rec=json.loads(rp.read_text(encoding='utf-8-sig'));native=rec['native'];np=Path(native['file']);np=np if np.is_absolute() else R/np
    assert sha(np)==native['sha256'];assert rec['export']['sha256']==actual
    im=Image.open(p);assert im.size==(1024,1024) and im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
    sc=json.loads(p.with_suffix('.png.generation.json').read_text(encoding='utf-8'));assert sc['sha256']==actual and sc['derivedFrom']['sha256']==native['sha256']
    side,pos,note=lookup[e['frame']]
    rows.append({'frame':e['frame'],'file':e['path'],'sha256':actual,'supportFoot':side,'position':pos,'visualNotes':note,'sourceRecord':e['native_evidence'],'native':native['file'],'nativeSHA256':native['sha256'],'nativeSize':[native['width'],native['height']],'size':[1024,1024],'mode':'RGBA','actualModel':rec.get('actualModel'),'actualQuality':rec.get('actualQuality'),'status':'single_frame_pass_sequence_pending_root_dynamic'})
    e['source_record']=e['native_evidence'];e['visual_status']='single_frame_pass_sequence_pending_root_dynamic';e['client_status']='not_integrated';e['sequence_review']='reviews/run-NW-eight-support-final-review-20261004.json'
assert len({r['sha256'] for r in rows})==16
anim=[]
for name,cycle in [('normal',1200),('slow',4800)]:
    p=R/f'work/finish-NW-final/{name}.apng';im=Image.open(p);dur=[]
    for f in range(im.n_frames):im.seek(f);dur.append(im.info['duration'])
    assert len(dur)==16 and sum(dur)==cycle
    anim.append({'file':p.relative_to(R).as_posix(),'frames':16,'durationMs':sum(dur),'frameDurations':dur,'sha256':sha(p)})
now=datetime.now(timezone.utc).isoformat()
report={'character':'02_fire_talisman_boy','action':'run','direction':'NW','reviewedAt':now,'status':'static_review_pass_pending_root_dynamic','formalCount':16,'frameDurationMs':75,'cycleMs':1200,'slowCycleMs':4800,'retainedSlots':[9,10,11],'revisedSlots':[1,2,3,4,5,6,7,8,12,13,14,15,16],'supportPairs':[{'foot':s,'frames':fs,'position':pos,'durationMs':150,'notes':note,'sha256':[next(r['sha256'] for r in rows if r['frame']==f) for f in fs]} for s,fs,pos,note in groups],'frames':rows,'previews':{'html':'work/finish-NW-final/index.html','contact':'work/finish-NW-final/contact.jpg','animations':anim},'method':['逐帧实际查看原生生成输出与4x4正式联系图','确认01–08同一右髋到鞋的连接；09–16同一左髋到鞋的连接；每两帧独立姿态','逐图正式SHA、原生SHA、RGBA透明、尺寸、旁注/主记录匹配核验','正常/慢速APNG均16帧，逐帧75ms/300ms，验证1200/4800ms'],'rejectedCandidates':[{'key':'finish-nw-NW08-a02','reason':'近左手改拿符扇、远右手持铃，拒绝未导入'},{'key':'finish-nw-NW14-a01','reason':'出现第三只鞋/腿，拒绝未导入'}],'dynamicStatus':'按root要求不操作浏览器；由主线程统一实际正常/慢放/逐帧最终验收。','rootReviewFocus':['08→09及16→01上肢相位转换','左右半圈原图后脑/躯干透视差异在160px播放中的感受'],'knownSingleFrameArtFailures':[],'clientStatus':'not_integrated','modelQuality':'目标GPT Image2.5 Sunburst/max；工具未提供model/quality选择且返回未披露实际值，actual均null。'}
report['knownUnresolvedArtFailures']=[]
report['visualNotes']='静态逐图核对2臂2腿、右符左铃与支撑脚链，01–08右脚/09–16左脚、每两张一位置；14a01三腿与08a02换手均已拒。08→09、16→01上肢转换及后脑透视仍交root实际动态最终确认，不以静态通过代替动态通过。'
(R/'reviews/run-NW-eight-support-final-review-20261004.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
iv['updatedAt']=now;iv['qa_summary']={'formalCount':16,'technicalStatus':'passed','staticVisualStatus':'passed','dynamicStatus':'pending_root_unified_browser_review','completeSequencePassed':False,'clientStatus':'not_integrated','review':'reviews/run-NW-eight-support-final-review-20261004.json'}
ip.write_text(json.dumps(iv,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for r in rows:print(f"{r['frame']:02d} {r['sha256']}")
