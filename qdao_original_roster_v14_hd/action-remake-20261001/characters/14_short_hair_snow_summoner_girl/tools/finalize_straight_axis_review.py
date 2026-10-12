"""Finalize the 196-frame follow-up only after visual acceptance and technical QA."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
at=datetime.now(timezone.utc).isoformat()
base=read(R/'audit/straight-axis-baseline.json');reviews=read(R/'review.json')
reports=['straight-axis-N-NE-review.json','straight-axis-W-NW-review.json','straight-axis-S-SE-SW-review.json','straight-axis-E-review.json','all-actions-hit-followup.json','all-actions-cast-followup.json','all-actions-attack-followup.json']
current={f:sha(R/f) for f in base['frames']}
changes={f:{'beforeSha256':old,'sha256':current[f],'generationRecord':f+'.generation.json'} for f,old in base['frames'].items() if current[f]!=old}
assert set(changes)=={'run/SW/06.png','attack/E/05.png','attack/E/06.png'}
seen=set()
for name in reports:
    p=R/'audit'/name;d=read(p)
    for row in d['frames']:
        f=row['file'];assert f not in seen;seen.add(f)
        assert row['sha256']==current[f] or (f in changes and row['sha256']==changes[f]['beforeSha256'])
    d['rootResolution']={'reviewedAt':at,'status':'passed_offline_current_frames','finalReview':'audit/straight-axis-final-review.json','remainingKnownRepairs':[],'currentFrameSha256':{row['file']:current[row['file']] for row in d['frames']},'note':'Initial diagnosis and before-repair SHA retained above as history. Root resolution binds current accepted files.'}
    save(p,d)
assert seen==set(current) and len(seen)==196
for f,h in current.items():assert reviews[f[:-4]]['sha256']==h and reviews[f[:-4]]['visualStatus']=='passed'
tech=read(R/'audit/technical-qa.json');assert tech['technicalPass']==196 and not tech['duplicateExports'] and not tech['duplicateNativeSources']
for f,change in changes.items():
    m=read(R/(f+'.generation.json'));assert m['straightAxisRepair']['status']=='passed_offline_after_static_and_browser_review'
    native=Path(m['derivedFrom']['generationRecord']);native=native if native.is_absolute() else R/native;n=read(native)
    change.update({'observation':m['straightAxisRepair']['observation'],'nativeGenerationRecord':str(native),'request':n['request'],'receipt':n['evidence']['receipt'],'actualModel':n['actualModel'],'actualQuality':n['actualQuality'],'route':n['route']})
playback={'method':'Actual CUA browser controls and representative screenshots; not a video recording or measured hardware FPS.','allRunDirections':{'normalCycleMs':1200,'quarterCycleMs':4800,'frames':16,'frameMs':75,'paused480pxFrames':[16,1,6],'loopObserved':'16→01'},'combat':{'groups':['hit/E','hit/W','attack/E','attack/W','cast/E','cast/W'],'normalAndQuarterSpeed':True,'displayPx':512,'focusedFrames':['hit/E/03','attack/E/05','attack/E/06','attack/W/05','cast/E/09','cast/W/07'],'attackEReplayedAfterRepair':True},'observations':'SW06 retains rear contact/knee flexion with SW toe; attack E05/06 retain stance and wrist/fox/crystal with rear toe E. N16 native15/16/01, slow playback and paused16→01 showed coordinated shank/foot tilt, no isolated yaw. SE02/03/04 additionally examined full size and SE replayed at240px normal/quarter with paused03; shortened shin-to-shoe projection remains SE, no confirmed lateral reversal.'}
audit={'status':'passed_offline_after_all_actions_and_straight_axis_followup','reviewedAt':at,'scope':'14 snow summoner only','counts':{'run':128,'hit':12,'attack':24,'cast':32,'total':196,'newAIRepaired':3,'preserved':193},'changes':changes,'currentFrameSha256':current,'staticAudits':['audit/'+n for n in reports],'independentRepairReviews':['audit/straight-axis-attack-repair-peer.json','audit/straight-axis-SW06-repair-peer.json'],'rootPlayback':playback,'timing':{'run':{'frames':16,'frameMs':75,'cycleMs':1200,'supportPositionsPerLeg':4,'distinctPosesPerPosition':2},'hit':{'framesPerDirection':6,'frameMs':40},'attack':{'framesPerDirection':12,'frameMs':30},'cast':{'framesPerDirection':16,'frameMs':45}},'modelPolicy':'audit/straight-axis-model-policy.json','remainingKnownArtworkFixes':[],'unpassedGroups':[],'clientValidated':False,'limitations':['Offline image and local browser review only; client movement/root/shadow/events not integrated.','Hidden anatomy is assessed by visible limb/sleeve connections, not claimed measurable ground truth.']}
save(R/'audit/straight-axis-final-review.json',audit)
p=R/'audit/final-visual-review.json';old=read(p);history=R/'provenance/straight-axis-prior-final-visual-review.json'
if not history.exists():save(history,old)
old.update(status=audit['status'],reviewedAt=at,latestFollowup='audit/straight-axis-final-review.json',straightAxisAdditionalRepairs=3,remainingKnownArtFixes=[]);save(p,old)
p=R/'audit/video-axis-final-review.json';d=read(p);d['supersededByLatestFollowup']={'path':'audit/straight-axis-final-review.json','at':at,'note':'Historical six-frame video-axis follow-up retained. Current196 SHA and three later repairs are in the latest follow-up.'};save(p,d)
heading='## 全动作手脚与腿脚同轴追加验收（2026-10-05）'
section=heading+'\n\n已重新实际检查全部196帧：跑步八方向128帧、受击12帧、普攻24帧、施法32帧。按最新髋—膝—踝—鞋头保持同一运动平面的要求，追加局部修正 **普攻E05/E06的后撑靴、西南跑步SW06的后撑靴**，其余193张保留。手腕、袖口、抱狐与持晶连接一并复查。\n\n内置生图逐张修正，未靠复制、镜像或插值补帧。正常及¼慢速、关键帧放大与16→01跑步循环已在本地预览检查；跑步仍16×75ms＝1200ms。当前未通过组与明确待修帧均为空，196/196离线通过；客户端未接入。\n\n[本轮逐帧与修图记录](audit/straight-axis-final-review.json)索引3张成品的前后SHA、实际提示词、参考图和内置工具回执。实际模型/质量工具未披露，明确标为未确认。下方视频反馈记录保留为前一轮历史。\n\n'
for name in ['STATUS.md','MERGE_HANDOFF.md']:
    p=R/name;t=p.read_text(encoding='utf-8');assert heading not in t
    first,rest=t.split('\n',1);p.write_text(first+'\n\n'+section+rest.lstrip(),encoding='utf-8')
print('Final follow-up audit:196 accepted;3 local AI fixes;193 retained.')
