"""Record actual completed review and explicit browser-access limitation; no visual pass fabrication."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
B=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(B/'manifest.json');now=datetime.now(timezone.utc).isoformat()
frames=[f for s in m['sequences'] for f in s['frames']]
assert len(frames)==196 and len(m['fullBodyRevision']['changedSlots'])==22
for f in frames:assert sha(B/f['file'])==f['sha256']
reviewed=['run-N','run-NE','run-E','run-SE','run-S','run-SW']
remaining=['run-W','run-NW','hit-W','attack-E','attack-W','cast-E','cast-W']
reason='Browser security policy rejected rebinding the existing localhost preview URL on 2026-10-05. No workaround or alternate browser access attempted. Remaining normal/quarter-speed browser playback is unverified.'
playback={'status':'incomplete_browser_access_blocked','reviewedAt':now,'changedSlots':m['fullBodyRevision']['changedSlots'],
 'reviewedSequences':reviewed,'remainingSequences':remaining,'runTiming':{'frameMs':60,'cycleMs':960,'frameCount':16},
 'runtimeFrameSha256':{f['slot']:f['sha256'] for f in frames},
 'completedMethods':['Actual local-browser normal playback','Actual local-browser quarter-speed playback','Stepped E03→04/E11→12, N16→01, NE08→09, SE03→04, S08→09/16→01, SW06→07'],
 'browserAccessLimit':reason,'notClaimed':'No complete 14-sequence dynamic approval; no client integration.'}
write(B/'review/full-body-playback-review-20261005.json',playback)
seqs=[]
for s in m['sequences']:
 key=s['action']+'-'+s['direction'];inherited=key=='hit-E'
 seqs.append({'action':s['action'],'direction':s['direction'],'visualApproval':'passed',
  'dynamicApproval':'passed' if key in reviewed or inherited else 'not_completed_browser_access_blocked',
  'reviewNote':'Current pixels actually played at60ms normal/quarter speed and critical joins stepped.' if key in reviewed else ('Unchanged image hashes and combat timing; inherited prior actual playback.' if inherited else 'Current native and neighboring frames inspected; fresh browser playback not completed.'),
  'carriedForwardFrom':'provenance/full-body-revision-20261005/acceptance-before.json' if inherited else None,
  'frames':[{'slot':f['slot'],'sha256':f['sha256']} for f in s['frames']]})
a={'schemaVersion':1,'character':B.name,'status':'ready_with_review_limit','visualApproval':'passed','dynamicApproval':'incomplete',
 'reviewedAt':now,'reviewer':'root assistant; not user acceptance','previewManifestSha256':m['selectionSource']['sha256'],
 'runtimeFrameSha256':playback['runtimeFrameSha256'],'sequences':seqs,'clientIntegrated':False,'clientRuntimeAcceptance':'not_tested',
 'reviewMethods':['All196 frame static anatomical review','Native edits and same-canvas neighbors','Technical current-source and timing verification','Actual browser playback for6 newly timed run sequences; hit-E inherited'],
 'browserAccessLimit':reason,'remainingDynamicSequences':remaining,
 'fullBodyRevisionReview':{'changedSlots':m['fullBodyRevision']['changedSlots'],'unchangedFrames':174,
  'selectionEvidence':m['selectionSource'],'actualPlaybackEvidence':{'file':'review/full-body-playback-review-20261005.json','sha256':sha(B/'review/full-body-playback-review-20261005.json')},
  'timingRevision':m['timingRevision']},
 'limits':['7组本轮浏览器实播未完成；不宣称全动作动态验收通过。','未接入客户端。','内置生成工具未披露实际型号/质量，保持null。']}
write(B/'acceptance.json',a);write(B/'review/final-sequence-review.json',a)
m['status']=a['status'];m['counts']['visualPassedSlots']=196;m['counts']['dynamicPassedSequences']=7
m['acceptance']={'file':'acceptance.json','sha256':sha(B/'acceptance.json'),'record':a}
for f in frames:f['status']='passed'
write(B/'manifest.json',m)
state=read(B/'review/full-body-revision-state-20261005.json')
state.update(status='images_exported_browser_review_limited',confirmedRepairSlots=m['fullBodyRevision']['changedSlots'],runAuditPending=False,hitAuditPending=False,hitRepairPending=False,runFramesToPreserve=112,remainingDynamicSequences=remaining,browserAccessLimit=reason)
write(B/'review/full-body-revision-state-20261005.json',state)
timing=read(B/'review/run-timing-60ms-20261005.json');timing.update(status='metadata_verified_browser_review_limited',remainingDynamicRunDirections=['W','NW']);write(B/'review/run-timing-60ms-20261005.json',timing)
status='''# 17 灵篆书生 · 素材已导出，播放复核受限

196张1024×1024透明RGBA PNG已保存。本轮22帧定点修正，其余174张PNG逐字节保持不变。全部帧静态手脚/持物复核及尺寸、透明边界、唯一性、来源和时长检查通过。

八方向跑步16帧各60ms，一轮960ms，每个接地位置两帧120ms。受击6×40ms、普攻12×30ms（06接触）、施法16×45ms（10释放）不变。

本轮正常与四分之一慢放已完成N/NE/E/SE/S/SW跑步；hit-E继承像素和时长完全相同的此前实播。重新访问本地预览时受到浏览器安全策略阻止，W/NW跑步、W受击、E/W普攻、E/W施法共7组本轮实播未完成，不宣称全动作动态验收通过。

当前状态以manifest.json、acceptance.json与review/full-body-playback-review-20261005.json为准。完整资源与可离线打开的预览均保存到本目录。未接入客户端，未提交或推送Git。实际生成型号/质量未由内置工具披露，来源记录保持null。
'''
(B/'STATUS.md').write_text(status,encoding='utf-8')
(B/'MERGE_HANDOFF.md').write_text(status+'\n交付runtime、manifest、acceptance、animation-timing和preview/delivery.html。导出仅整画布LANCZOS等比缩至1024；无裁切、平移或Alpha清理。所有22个新选图来源已内嵌在正式PNG旁的generation.json。\n',encoding='utf-8')
(B/'preview/README.md').write_text('''# 灵篆书生完整动作预览

打开delivery.html，保持preview与runtime相对目录。196张正式PNG；跑步60ms/帧、960ms/圈；正常/慢放/逐帧均可用。八方向动图为run-current-960ms.webp。

7组本轮浏览器实播受访问策略阻止未完成，详见../acceptance.json。图片静态与时长/文件完整性检查已通过；未接入客户端。
''',encoding='utf-8')
p=B/'DELIVERY.md';s=p.read_text(encoding='utf-8');s=s.replace('完成验收后生效。','其中如实记录7组浏览器实播尚未完成。').replace('导出完成不等于本轮播放已通过；','全部帧静态与文件检查通过；7组本轮浏览器实播因访问策略阻止未完成，不宣称全动态验收通过。')
p.write_text(s,encoding='utf-8')
print(json.dumps({'status':m['status'],'staticPassedFrames':196,'dynamicPassedSequences':7,'remainingDynamicSequences':remaining}))
