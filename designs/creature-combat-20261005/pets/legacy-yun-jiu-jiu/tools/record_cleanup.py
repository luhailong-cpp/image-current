"""Record already completed, explicitly scoped PNG removals. Does not delete."""
import json
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
stamp=datetime.now(timezone.utc).isoformat()
plan=read(ROOT/'cleanup-plan.json')
for entry in plan['files']:
    p=(ROOT/entry['file']).resolve()
    assert p.is_relative_to(ROOT) and not p.exists(), p
    if entry.get('generationRecord'):
        rp=ROOT/entry['generationRecord']; d=read(rp)
        d['sourceRetention']={'status':'deleted-after-export','deletedAt':stamp,'reason':entry['reason'],'cleanupRecord':'cleanup.json'}
        write(rp,d)
for rp in (ROOT/'records').glob('*.json'):
    d=read(rp)
    if isinstance(d,dict) and 'referenceRetentionAudit' in d:
        for r in d['referenceRetentionAudit']:
            r['retentionStatus']='historical-input-removed-see-cleanup' if r.get('plannedRemoval') else 'current-reference-retained'
        write(rp,d)
plan.update(status='completed',completedAt=stamp,removedImages=len(plan['files']),method='SHA-verified, explicit absolute file paths, nonrecursive PowerShell Remove-Item in bounded batches',initialBatchAttempt='Automatic approval review rejected compound computed cleanup; no deletion occurred in that rejected call. Explicit named-file cleanup subsequently succeeded.')
write(ROOT/'cleanup.json',plan)
audit=read(ROOT/'qa/provenance-audit.json')
audit['postCleanupNote']='This audit captured 95 actual PNGs before cleanup. 93 native frame/candidate PNGs and 7 intermediate QA PNGs were subsequently deleted after verified export; sourceRetention/referenceRetentionAudit/cleanup.json preserve the historical chain. Current 68 runtime PNGs are checked by validation.json.'
audit['postCleanupRecordedAt']=stamp
write(ROOT/'qa/provenance-audit.json',audit)
for p in (ROOT/'qa').glob('*.md'):
    text=p.read_text(encoding='utf-8-sig')
    text=text.replace('(cast-W-contact.png)','(../preview/cast-W-contact.png)').replace('(cast-E-late-contact.png)','(../preview/cast-E-contact.png)')
    text=text.replace('[34帧总览](W-all-contact.png)','[W受击总览](../preview/hit-W-contact.png) / [W普攻总览](../preview/attack-W-contact.png) / [W施法总览](../preview/cast-W-contact.png)')
    text=text.replace('[施法09–14细看](W-cast-09-14-detail.png)','施法09–14过程细看图（已按最终保留规则清理）')
    text=text.replace('[固定坐标支撑对比](W-support-diagnostic.png)','固定坐标支撑过程对比图（已清理，文字测量保留）')
    text+='\n\n最终收尾：本文件保留制作阶段的原生静态检查历史；原生动作/拒稿/过程图片已按cleanup.json清理，最终runtime及播放检查以../README.md、../manifest.json和final-review.json为准。上文“待主窗口检查”属于当时状态。\n'
    p.write_text(text,encoding='utf-8')
print(json.dumps({'recordedRemovals':len(plan['files']),'remainingSourcePng':[p.name for p in (ROOT/'source').glob('*.png')]},ensure_ascii=False))
