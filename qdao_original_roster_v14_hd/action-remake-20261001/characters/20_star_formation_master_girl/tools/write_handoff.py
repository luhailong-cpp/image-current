from pathlib import Path
import json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from timing import RUN_TIMING
ROOT=Path(__file__).resolve().parents[1]
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selection=rd(ROOT/'selection.json');state=rd(ROOT/'STATUS.json')
if selection.get('status')=='offline_delivery':
 import subprocess,sys
 sys.exit(subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/build_delivery.py'),'--rebuild']).returncode)
files=[]
for f in selection['frames']:
 source=ROOT/f['source'];candidate=ROOT/f"candidate/{f['action']}/{f['direction']}/{f['frame']:02}.png"
 files.append(dict(action=f['action'],direction=f['direction'],frame=f['frame'],source=f['source'],sourceSha256=sha(source),generationRecord=f['generationRecord'],candidate=candidate.relative_to(ROOT).as_posix(),candidateSha256=sha(candidate) if candidate.exists() else None,visualReview=f.get('visualReview',f.get('review',{})),dynamicAccepted=False))
data={'character':ROOT.name,'updatedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'status':'work_in_progress','expected':196,'selectedCandidates':len(files),'finalVisualPassed':0,'runtimeExported':0,'canvas':[1024,1024],'sourceNativeMinimum':[1024,1024],'transform':selection['exportTransform'],'anchorStatus':'fixed_export_transform_actual_grounding_under_review','runTiming':RUN_TIMING,'otherTimingsMs':{'hit':40,'attack':30,'cast':45},'actionMarkers':{'attackContact':{'E':6,'W':6,'status':'candidate_not_client_validated'},'castRelease':{'E':10,'W':10,'status':'candidate_not_client_validated'}},'clientIntegrated':False,'clientValidation':'not_run','actualModel':None,'actualQuality':None,'modelEvidence':'Built-in route; requested target in per-frame configSnapshot; no model/quality selector or returned field.','files':files}
(ROOT/'merge-manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 星阵少女 · 本机合并交接','',f"更新时间：{data['updatedAt']}。当前选中候选 {len(files)}/196，最终视觉通过0，正式runtime导出0。",'','工作只在本角色目录内，未切分支、暂存、提交、推送或覆盖客户端。当前全部按在制稿交接。','','## 文件与来源','','- 当前唯一选帧：[selection.json](selection.json)。动作分选表由各制作分工维护。','- 可核验路径、原生与候选SHA：[merge-manifest.json](merge-manifest.json)。','- 逐槽缺口：[STATUS.json](STATUS.json)。每张generation PNG有同名generation.json记录与真实提示词。','- 原生来源按固定整画布922×922缩放并放在1024×1024的(51,40)，导出根点(512,922)。未做逐帧bbox缩放、最低脚贴地、镜像或补帧。','- 当前candidate是可预览技术导出，不表示已正式验收。','','## 播放与验收','','[交互预览](preview/index.html)提供逐帧、慢放和缺槽。跑步正常1×统一1200ms/圈，16帧均匀75ms，无额外尾帧停留；保留4倍慢放和逐帧控制。该参数已写入离线交付，客户端未接入。','', '受击40ms/帧，普攻30ms/帧，施法45ms/帧保持原约定。普攻第6帧/施法第10帧作为待审事件参考，尚未客户端验证。','','跑步E有16张候选，正在针对支撑脚高度、膝踝承重、摆臂与接环检查，其他方向缺口按STATUS。不得把逐帧实看或文件齐全说成正常尺寸动态通过。根点虚线只用于诊断，真实鞋底相位另看provenance里的逐帧复核。','','## 合并边界','','用户另一台电脑的未提交文件未获取；合并时按完整角色ID与逐图SHA比对，勿用当前候选覆盖另一机已验收成品。旧idle/walk仅作只读身份参考，本批可用性审计见[PRIOR_REVIEW.md](PRIOR_REVIEW.md)。','','模型配置目标为GPT Image 2.5 Sunburst/max；内置入口没有型号/质量选择器且回执未披露，实际值为null/未确认。配置值不能回填成实际值。','','客户端未接入、未运行；离线技术检查和试播文件不能替代游戏内速度/滑步验收。']
(ROOT/'MERGE_HANDOFF.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'manifestFrames':len(files),'finalVisualPassed':0,'clientIntegrated':False}))

