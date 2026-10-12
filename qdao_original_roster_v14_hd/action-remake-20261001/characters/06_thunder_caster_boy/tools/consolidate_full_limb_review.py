"""Consolidate current SHA-bound whole-limb audits, preserving historical timing evidence."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
read=lambda n:json.loads((R/n).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=['review/upper_limb_run_N_NE_NW_E_20261005.json','review/upper_limb_run_S_SE_SW_W_20261005.json','review/upper_limb_combat_20261005.json']
baseline=read('records/full_limb_baseline_20261005.json');old={f['path']:f['sha256'] for f in baseline['frames']}
rows={};errors=[]
for source in sources:
 g=read(source)
 if g.get('parentWUpdatesPending'):errors.append(source+': W updates pending')
 for issue in g.get('unresolvedBlockingIssues',[]):errors.append(str(issue))
 for f in g.get('frames',[]):
  rel=f.get('file',f.get('path'));p=R/rel
  if rel in rows:errors.append('duplicate '+rel)
  if sha(p)!=f['sha256']:errors.append('stale '+rel)
  if any('repair-in-progress' in str(f.get(k,'')) or str(f.get(k,'')).startswith('pending') for k in ['upperLimbStatus','wholeLegAxisStatus','status']):errors.append('unresolved '+rel)
  c={'file':rel,'sha256':sha(p),'sourceReview':source,'observations':f,'changedThisRound':sha(p)!=old[rel]}
  if rel.startswith('runtime/run/'):
   phase=baseline['runPositions'][rel]
   c.update(supportLeg=phase['supportLeg'],pairFrames=phase['pairFrames'],positionPhase=phase['positionPhase'],phaseBaselineSha256=phase['sha256'],phasePreserved='本轮局部上肢/鞋朝向修正保留原支撑脚、膝踝位置与两帧相位；对应实看审计见observations')
  rows[rel]=c
assert len(rows)==196, len(rows)
assert not errors, errors
out={'recordedAt':datetime.now(timezone.utc).isoformat(),'character':'06_thunder_caster_boy','staticReviewComplete':True,'frameCount':196,'frames':list(rows.values()),'unresolvedBlockingIssues':[],'sourceReports':[{'file':s,'sha256':sha(R/s)} for s in sources],'changedRuntimeFiles':[r for r,f in rows.items() if f['changedThisRound']],'retainedRuntimeCount':sum(not f['changedThisRound'] for f in rows.values()),'criteria':'髋-大腿-膝-小腿-踝-鞋头保持同一运动平面；自然屈膝/透视保留。肩-肘-腕连续，右杖左牌固定持物和握点。','timing':{'runFrameMs':60,'runCycleMs':960,'pairMs':120,'slowCycleMs':3840,'source':'records/run_timing_user_correction_20261005.json','hitFrameMs':40,'attackFrameMs':30,'castFrameMs':45},'dynamicPlaybackReviewed':False,'playbackOwner':'root final browser review after last PNG update','clientIntegrated':False,'userFinalApproved':False,'historicalReportsTimingNote':'被引用报告写入时的75ms/1200ms属于历史快照；本次直接用户纠正以60ms/960ms为准，不改历史证据'}
(R/'review/full_limb_final_20261005.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'staticFrames':196,'changed':len(out['changedRuntimeFiles']),'retained':out['retainedRuntimeCount'],'runCycleMs':960}))

