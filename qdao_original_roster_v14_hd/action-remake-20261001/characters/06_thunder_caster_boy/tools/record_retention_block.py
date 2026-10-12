"""Record actual automatic-approval rejection; do not retry or delete through another route."""
from pathlib import Path
from datetime import datetime,timezone
import json
R=Path(__file__).resolve().parents[1]
p=R/'records/final_retention_plan_20261004.json';plan=json.loads(p.read_text(encoding='utf-8-sig'))
plan.update(executed=False,executionState='blocked_by_automatic_approval',attemptedAt=datetime.now(timezone.utc).isoformat(),blockedAction='PowerShell native Remove-Item on487 explicit image files inside character06, after scope/SHA checks; no recursive cache deletion',rejectionReason='blocked by policy',rejectionEvidence='exec_command failed: CreateProcess Rejected; command was not launched',retryAttempted=False,remainingFilesPreserved=True)
p.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['STATUS.json','review/CURRENT_REVIEW.json']:
 p=R/name;data=json.loads(p.read_text(encoding='utf-8-sig'))
 data['retentionCleanup']={'completed':False,'state':'blocked_by_automatic_approval','remainingImageCount':len(plan['files']),'plan':'records/final_retention_plan_20261004.json','reason':'blocked by policy','finalAssetsAffected':False,'temporaryEdgeCacheAlsoPreservedAfterPriorRejection':True}
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'MERGE_HANDOFF.md';s=p.read_text(encoding='utf-8')
s=s.replace('最终PNG与当前预览确认后，按用户素材保留规则清理本目录已淘汰/中间图，保留完整来源文字与删除清单。临时Edge配置/缓存的清理曾被自动审批拒绝（仅返回 blocked by policy），因此保留，不绕过。','最终PNG及当前预览已验证。清理本目录487张原生重复图、拒稿和旧复核图时，自动审批拒绝启动删除命令（仅返回 blocked by policy），没有执行删除；这些图和全部来源文字仍保留。具体路径和SHA见 [清理清单](records/final_retention_plan_20261004.json)。此前临时Edge配置/缓存删除也被自动审批拒绝，仍保留，未绕过。素材制作与离线验证已完成，清理项因上述限制未完成。')
p.write_text(s,encoding='utf-8')
print(json.dumps({'cleanupExecuted':False,'blockedImages':len(plan['files']),'finalAssetsAffected':False}))
