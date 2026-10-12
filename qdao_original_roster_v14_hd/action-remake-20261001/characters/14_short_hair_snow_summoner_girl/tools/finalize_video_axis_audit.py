"""Finalize the additional video-based repair; preserve the preceding audit history."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=read(R/'audit/video-axis-baseline.json');m=read(R/'manifest.json');accept=read(R/'audit/bamboo-root-acceptance.json')
assert m['exported']==m['visualPassed']==196
changes=[]
for file,old in base['frames'].items():
 h=sha(R/file)
 if h!=old:
  meta=read(R/(file+'.generation.json'));assert meta['videoAxisRepair']['status']=='passed_offline_after_fresh_sequence_review'
  changes.append({'file':file,'beforeSha256':old,'sha256':h,'reason':meta['videoAxisRepair']['observation'],'generationRecord':file+'.generation.json','nativeGenerationRecord':meta['derivedFrom']['generationRecord']})
assert {x['file'] for x in changes}=={'run/E/11.png','run/NE/04.png','run/NW/11.png','run/SE/07.png','run/SE/14.png','run/SW/05.png'}
now=datetime.now(timezone.utc).isoformat()
out={'status':'passed_offline_video_axis_followup','reviewedAt':now,'runFramesRechecked':128,'localAIRepairs':len(changes),'unchangedRunFrames':128-len(changes),'changes':changes,'directionObservations':{d:read(R/f'audit/root-{d}-preview-observations.json') for d in accept['directions']},'framesByDirection':{d:v['frames'] for d,v in accept['directions'].items()},'referenceVideo':{'path':base['video'],'sha256':base['videoSha256'],'decodedConsecutiveSegments':base['segments'],'visibilityLimit':'Reference actor is small and nameplate sometimes obscures soles; no claim of every sole detail from the video.'},'referenceRole':'Video motion and09 bamboo girl directional mechanics only; retained project painted style and14 identity. Screenshot mountain guard was only a diagnostic example, not edited.','modelPolicy':'audit/video-axis-model-policy.json','actualGenerationModel':None,'actualGenerationQuality':None,'route':'builtin image_gen; model/quality not disclosed','timing':{'frames':16,'frameMs':75,'cycleMs':1200,'positionsPerSupportFoot':4,'distinctPosesPerPosition':2},'handReview':'Each current direction and all6 edits examined: two connected arms, one fox on left, one crystal in right; no new hand edit needed in this followup.','technicalAudit':'audit/technical-qa.json','previewFiles':42,'clientValidated':False,'remainingKnownArtworkFixes':[],'limitations':['Offline asset and browser review; actual game-client world velocity, root and event integration not tested.','Raised sole exposure and diagonal projections preserved where anatomically coherent.']}
save(R/'audit/video-axis-final-review.json',out)
f=read(R/'audit/final-visual-review.json');f['latestFollowup']='audit/video-axis-final-review.json';f['status']='passed_offline_after_video_axis_followup';f['videoAxisAdditionalRepairs']=6;f['scope'].append('Fresh128-frame knee/ankle/shoe axis review with6 local repairs after user video feedback');save(R/'audit/final-visual-review.json',f)
intro='''## 视频反馈追加修正（2026-10-04）

重新对照用户视频连续画面及09竹弓少女，八方向128张跑步帧已复核。本次额外局部修复6张：E11、NE04、NW11的鞋掌透视/方向跳变，SE07、SE14及SW05的摆腿回跳。其余122张保留；手臂连接、左抱白狐和右持晶体重新核对。

内置生图逐张局部修正，保持1024×1024透明画布；实际型号/质量工具未披露，不以配置目标冒充返回结果。16帧×75ms=1200ms、每只支撑脚4个位置×每位置2个不同姿态保持。已复查正常/¼慢速及480px的16→01循环衔接。

[本轮完整审计](audit/video-axis-final-review.json)列出6张成品、前后SHA、逐图来源/提示词记录及各方向观察。196张正式动作与42份预览均通过当前文件校验。本轮仍是素材离线验收，未接入游戏客户端。

'''
for name in ['STATUS.md','MERGE_HANDOFF.md']:
 p=R/name;s=p.read_text(encoding='utf-8');lines=s.splitlines(True);p.write_text(lines[0]+'\n'+intro+''.join(lines[1:]),encoding='utf-8')
print(json.dumps({'status':out['status'],'rechecked':128,'changed':6,'preserved':122,'formal':196}))
